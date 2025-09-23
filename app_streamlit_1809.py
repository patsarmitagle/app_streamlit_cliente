import streamlit as st
import requests
import pandas as pd
import re
import random
from datetime import date, timedelta, datetime
from typing import Dict, Any, List, Optional, Union

# ---------------------------
# Config de página
# ---------------------------
st.set_page_config(page_title="Registro Préstamos", layout="centered", page_icon="📲")

# ---------------------------
# Sidebar (endpoints y opciones)
# ---------------------------
st.sidebar.header("⚙️ Configuración")
API_APPEND = st.sidebar.text_input(
    "Endpoint alta (append)",
    value="https://mvp-api.1yzxcwh7kd3n.us-south.codeengine.appdomain.cloud/append",
)
API_FILTER_BASE = st.sidebar.text_input(
    "Endpoint filtro por cédula (filter/{id})",
    value="https://mvp-api.1yzxcwh7kd3n.us-south.codeengine.appdomain.cloud/filter",
)
API_NOTIF = st.sidebar.text_input(
    "Endpoint notificación WhatsApp",
    value="https://api-notificacion-haqu.onrender.com/enviar-notificacion",
)
ENVIAR_NOTIF = st.sidebar.checkbox("Enviar notificación por WhatsApp", value=True)
TIMEOUT = st.sidebar.number_input("Timeout (seg)", min_value=5, max_value=60, value=20, step=1)

# ---------------------------
# Encabezado
# ---------------------------
st.image("Logo_BeClever_VersionPrincipal_Color.png", width=250)
st.title("📲 Registro a la Campaña de Préstamos")
st.markdown("Ingresá tu número con código país (ej: **5491123456789**).")

# ---------------------------
# Utilidades
# ---------------------------
PHONE_RE = re.compile(r"^\d{11,15}$")
def es_telefono_valido(tel: str) -> bool:
    return bool(PHONE_RE.match((tel or "").strip()))

NOMBRES = ["Selena", "Carlos", "María", "Juan", "Lucía"]
APELLIDOS1 = ["Gibert", "Pérez", "González", "Ramírez"]
APELLIDOS2 = ["Vicente", "López", "Díaz", "Rodríguez"]
GENEROS = ["FEMENINO", "MASCULINO"]

def random_fecha_nacimiento(min_year=1980, max_year=2002) -> str:
    start = date(min_year, 1, 1)
    end = date(max_year, 12, 31)
    d = start + timedelta(days=random.randint(0, (end - start).days))
    return d.strftime("%Y-%m-%d")

def calcular_edad(fecha_iso: str) -> str:
    try:
        f = datetime.strptime(fecha_iso, "%Y-%m-%d").date()
        today = date.today()
        edad = today.year - f.year - ((today.month, today.day) < (f.month, f.day))
        return str(max(0, edad))
    except Exception:
        return "35"

def generar_id_cliente() -> str:
    # Si preferís UUID: return uuid.uuid4().hex
    return str(random.randint(10_000_000, 99_999_999))

def payload_alta_desde_telefono(telefono: str) -> Dict[str, Any]:
    telefono = (telefono or "").strip()
    nombre = random.choice(NOMBRES)
    apellido1 = random.choice(APELLIDOS1)
    apellido2 = random.choice(APELLIDOS2)
    fecha_nac = random_fecha_nacimiento(1980, 2002)
    genero = random.choice(GENEROS)
    id_cliente = generar_id_cliente()
    num_ident = str(random.randint(1_000_000_000, 1_999_999_999))

    return {
        "num_telefono": telefono,
        "tipo_id": "C",
        "num_identificacion": num_ident,
        "nombre_completo": f"{nombre} {apellido1} {apellido2}",
        "nombres": nombre,
        "primer_apellido": apellido1,
        "segundo_apellido": apellido2,
        "fecha_nacimiento": fecha_nac,
        "genero_cliente": genero,
        "edad": calcular_edad(fecha_nac),
        "grupo_pad": "0",
        "cod_ciudad": "0",
        "ciudad": "BOGOTA D.C.",
        "cod_depto": "11",
        "departamento": "BOGOTA D.C.",
        "productos_aprob": "PP/VEH_NUE/VEH_USA/VIV/ROTA/TC/LBZ60/LBZ72/LBZ84/LBZ96",
        "disponible": "1942461.13",
        "gastos_fliar": "1442461.13",
        "disponible_pp": "1692461.13",
        "plazo_pp": "60",
        "tasa_pp": "1.6",
        "monto_pp": "81091707.58",
        "cuota_pp": "1692461.13",
        "Monto_Lbz_60": "74617281.56",
        "Monto_Lbz_72": "80767861.54",
        "Monto_Lbz_84": "73908821.55",
        "Monto_Lbz_96": "77691769.76",
        "Cuota_Lbz_60": "1243621.36",
        "Cuota_Lbz_72": "1121775.85",
        "Cuota_Lbz_84": "879866.92",
        "Cuota_Lbz_96": "809289.27",
        "id_cliente": id_cliente,
    }

def _to_dict_first(record: Union[Dict[str, Any], List[Dict[str, Any]], None]) -> Optional[Dict[str, Any]]:
    """Normaliza respuesta del backend: si viene lista, toma el primero; si dict, lo devuelve; si no, None."""
    if record is None:
        return None
    if isinstance(record, list):
        return record[0] if record else None
    if isinstance(record, dict):
        return record
    return None

def consultar_por_cedula(api_filter_base: str, cedula: str, timeout: int = 20) -> Optional[Dict[str, Any]]:
    """Hace GET a {base}/{cedula} y devuelve un dict con el registro (o None)."""
    url = api_filter_base.rstrip("/") + "/" + str(cedula).strip()
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    try:
        data = r.json()
    except ValueError:
        raise RuntimeError("La API de filtro no devolvió JSON válido.")
    reg = _to_dict_first(data)
    return reg

# ---------------------------
# Estado
# ---------------------------
if "ultimo_registro_enviado" not in st.session_state:
    st.session_state["ultimo_registro_enviado"] = None  # payload enviado al append
if "ultima_cedula" not in st.session_state:
    st.session_state["ultima_cedula"] = ""              # se guardará num_identificacion

# ---------------------------
# Formulario de alta
# ---------------------------
with st.form("form_registro", clear_on_submit=False):
    telefono = st.text_input("Número de WhatsApp", placeholder="5491123456789", label_visibility="hidden")
    enviar = st.form_submit_button("✅ Quiero participar", use_container_width=True)

if enviar:
    tel = (telefono or "").strip()
    if not es_telefono_valido(tel):
        st.error("Revisá el formato (11–15 dígitos, con código país).")
    else:
        alta = payload_alta_desde_telefono(tel)
        with st.spinner("Registrando…"):
            try:
                resp = requests.post(API_APPEND, json=alta, timeout=TIMEOUT)
                if 200 <= resp.status_code < 300:
                    st.success("¡Registro exitoso! Tu alta fue enviada al motor.")
                    st.session_state["ultimo_registro_enviado"] = alta
                    st.session_state["ultima_cedula"] = alta.get("num_identificacion", "")
                    # Notificación opcional
                    if ENVIAR_NOTIF:
                        payload_notif = {
                            "nombres": alta.get("nombres", ""),
                            "primer_apellido": alta.get("primer_apellido", ""),
                            "num_telefono": alta.get("num_telefono", tel),
                        }
                        try:
                            n = requests.post(API_NOTIF, json=payload_notif, timeout=TIMEOUT)
                            if 200 <= n.status_code < 300:
                                st.success("📩 Notificación enviada por WhatsApp.")
                            else:
                                st.warning(f"No se pudo enviar la notificación (HTTP {n.status_code}): {n.text}")
                        except Exception as e:
                            st.warning(f"No se pudo enviar la notificación: {e}")
                else:
                    st.error(f"Error en alta (HTTP {resp.status_code}). Respuesta: {resp.text}")
            except Exception as e:
                st.error(f"Error al conectar: {e}")

st.markdown("---")

# ---------------------------
# Consulta del último registro vía /filter/{id}
# ---------------------------
st.subheader("🔍 Consultar último registro en backend (por cédula)")
cedula_default = st.session_state.get("ultima_cedula", "")
col_inp, col_btn = st.columns([3,1])
with col_inp:
    cedula_input = st.text_input("Cédula (num_identificacion)", value=cedula_default or "", placeholder="1999999999")
with col_btn:
    refrescar = st.button("🔄 Refrescar datos del backend", use_container_width=True)

registro_remoto: Optional[Dict[str, Any]] = None
if (cedula_input or "").strip():
    if refrescar or cedula_input != cedula_default:
        with st.spinner("Consultando en backend…"):
            try:
                registro_remoto = consultar_por_cedula(API_FILTER_BASE, cedula_input, TIMEOUT)
                if registro_remoto is None:
                    st.info("No se encontró registro para esa cédula.")
                else:
                    st.success("Datos recuperados desde el backend.")
                    # actualizamos la cédula por si la cambió manualmente
                    st.session_state["ultima_cedula"] = cedula_input.strip()
            except Exception as e:
                st.error(f"No se pudo consultar el backend: {e}")

# Mostrar panel comparativo (enviado vs recuperado) o sólo recuperado si existe
tab1, tab2 = st.tabs(["📤 Enviado (esta sesión)", "📥 Recuperado (backend)"])

with tab1:
    enviado = st.session_state.get("ultimo_registro_enviado")
    if enviado:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🆔 Número de Identificación:**")
            st.code(str(enviado.get("num_identificacion", "")))
            st.markdown("**🎂 Fecha de Nacimiento:**")
            st.code(str(enviado.get("fecha_nacimiento", "")))
            st.markdown("**🆔 ID Cliente:**")
            st.code(str(enviado.get("id_cliente", "")))
        with col2:
            st.markdown("**👤 Nombre completo:**")
            st.code(str(enviado.get("nombre_completo", "")))
            st.markdown("**📞 Teléfono:**")
            st.code(str(enviado.get("num_telefono", "")))
    else:
        st.info("Aún no enviaste un registro en esta sesión.")

with tab2:
    if registro_remoto:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**🆔 Número de Identificación:**")
            st.code(str(registro_remoto.get("num_identificacion", "")))
            st.markdown("**🎂 Fecha de Nacimiento:**")
            st.code(str(registro_remoto.get("fecha_nacimiento", "")))
            st.markdown("**🆔 ID Cliente:**")
            st.code(str(registro_remoto.get("id_cliente", "")))
        with col2:
            st.markdown("**👤 Nombre completo:**")
            st.code(str(registro_remoto.get("nombre_completo", "")))
            st.markdown("**📞 Teléfono:**")
            st.code(str(registro_remoto.get("num_telefono", "")))
        # Extra: tabla completa del dict
        with st.expander("📋 Ver payload completo recuperado"):
            df = pd.DataFrame([registro_remoto]).T
            st.dataframe(df, use_container_width=True)
    else:
        st.info("Usá el campo de cédula y el botón de refrescar para traer datos del backend.")
