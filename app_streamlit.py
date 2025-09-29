import streamlit as st
import requests
import pandas as pd
import re
import random
import time
from datetime import date, timedelta, datetime
from typing import Dict, Any, List, Optional, Union

# =======================
# Config y Sidebar
# =======================
st.set_page_config(page_title="Registro Préstamos", layout="centered", page_icon="📲")

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

st.sidebar.markdown("---")
VALIDAR_PERSISTENCIA = st.sidebar.checkbox("Validar escritura (GET inmediato)", value=True)
REINTENTOS = st.sidebar.number_input("Reintentos GET /filter", min_value=0, max_value=10, value=3, step=1)
ESPERA = st.sidebar.number_input("Espera entre reintentos (seg)", min_value=0, max_value=30, value=2, step=1)

st.sidebar.markdown("---")
IGNORAR_MISMATCH = set(st.sidebar.multiselect(
    "Ignorar diferencias en campos",
    options=["id_cliente", "num_telefono", "nombres", "primer_apellido"],
    default=["id_cliente", "num_telefono"],
))

# =======================
# Utilidades
# =======================
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
    if record is None:
        return None
    if isinstance(record, list):
        return record[0] if record else None
    if isinstance(record, dict):
        return record
    return None

def consultar_por_cedula(api_filter_base: str, cedula: str, timeout: int = 20) -> Optional[Dict[str, Any]]:
    url = api_filter_base.rstrip("/") + "/" + str(cedula).strip()
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return _to_dict_first(data)

def mostrar_http(label: str, resp: requests.Response):
    st.markdown(f"**{label}** — HTTP `{resp.status_code}`")
    with st.expander(f"Ver respuesta cruda de {label}"):
        try:
            st.json(resp.json())
        except Exception:
            st.code(resp.text)

def render_info_grid(datos: Dict[str, Any], titulo_izq: str = "🆔 Número de Identificación:", titulo_der: str = "👤 Nombre completo:"):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"**{titulo_izq}**")
        st.code(str(datos.get("num_identificacion","")))
    with c2:
        st.markdown(f"**{titulo_der}**")
        st.code(str(datos.get("nombre_completo","")))
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("**🎂 Fecha de Nacimiento:**")
        st.code(str(datos.get("fecha_nacimiento","")))
    with c4:
        st.markdown("**📞 Teléfono:**")
        st.code(str(datos.get("num_telefono","")))
    c5, _ = st.columns([1,1])
    with c5:
        st.markdown("**🆔 ID Cliente:**")
        st.code(str(datos.get("id_cliente","")))

# =======================
# Estado
# =======================
if "ultimo_registro_enviado" not in st.session_state:
    st.session_state["ultimo_registro_enviado"] = None
if "ultima_cedula" not in st.session_state:
    st.session_state["ultima_cedula"] = ""
if "ultimo_registro_remoto" not in st.session_state:
    st.session_state["ultimo_registro_remoto"] = None
if "ultima_respuesta_append" not in st.session_state:
    st.session_state["ultima_respuesta_append"] = None
if "ultima_respuesta_notif" not in st.session_state:
    st.session_state["ultima_respuesta_notif"] = None

# =======================
# BLOQUE 1 — Registro (PRIMERO)
# =======================
st.image("Logo_BeClever_VersionPrincipal_Color.png", width=250)
st.title("Valida si fuiste asignado a la Campaña de Préstamos")
st.markdown("Ingresá tu número con código país (ej: **5491123456789**).")

with st.form("form_registro", clear_on_submit=False):
    telefono = st.text_input("", placeholder="5491123456789")
    enviar = st.form_submit_button("✅ Validar mi télefono", use_container_width=True)

if enviar:
    tel = (telefono or "").strip()
    if not es_telefono_valido(tel):
        st.error("Revisá el formato (11–15 dígitos, con código país).")
    else:
        alta = payload_alta_desde_telefono(tel)
        with st.spinner("Registrando…"):
            try:
                resp = requests.post(API_APPEND, json=alta, timeout=TIMEOUT)
                st.session_state["ultima_respuesta_append"] = resp
                if 200 <= resp.status_code < 300:
                    st.success("Tus datos forman parte de nuestra campaña!")
                    st.session_state["ultimo_registro_enviado"] = alta
                    st.session_state["ultima_cedula"] = alta.get("num_identificacion", "")

                    # Validación inmediata de persistencia
                    if VALIDAR_PERSISTENCIA and st.session_state["ultima_cedula"]:
                        ced = st.session_state["ultima_cedula"]
                        encontrado = None
                        for i in range(int(REINTENTOS) + 1):
                            try:
                                encontrado = consultar_por_cedula(API_FILTER_BASE, ced, TIMEOUT)
                                if encontrado:
                                    break
                            except Exception:
                                pass
                            if i < REINTENTOS:
                                time.sleep(ESPERA)

                        if encontrado:
                            st.success("Tu número de celular fue validado correctamente!")
                            st.session_state["ultimo_registro_remoto"] = encontrado

                            # Validación con ignorados
                            campos_a_chequear = ["num_identificacion", "num_telefono", "id_cliente", "nombres", "primer_apellido"]
                            mismatches, cambios_ignorados = [], []
                            for k in campos_a_chequear:
                                enviado_v = str(alta.get(k, ""))
                                recibido_v = str(encontrado.get(k, ""))
                                if enviado_v != recibido_v:
                                    if k in IGNORAR_MISMATCH:
                                        cambios_ignorados.append(k)
                                    else:
                                        mismatches.append(k)
                            if cambios_ignorados:
                                st.info(f"🔄 El backend modificó (ignorado por config): {', '.join(cambios_ignorados)}")
                            if mismatches:
                                st.warning(f"⚠️ Campos que no coinciden: {', '.join(mismatches)}")
                        else:
                            st.error("✗ No se encontró el registro en /filter/{id} tras los reintentos.")

                    # Notificación opcional
                    if ENVIAR_NOTIF:
                        payload_notif = {
                            "nombres": alta.get("nombres", ""),
                            "primer_apellido": alta.get("primer_apellido", ""),
                            "num_telefono": alta.get("num_telefono", tel),
                        }
                        try:
                            n = requests.post(API_NOTIF, json=payload_notif, timeout=TIMEOUT)
                            st.session_state["ultima_respuesta_notif"] = n
                            if 200 <= n.status_code < 300:
                                st.success("📩 Muy pronto un ejecutivo te contactará por WhatsApp.")
                            else:
                                st.warning(f"No se pudo enviar la notificación (HTTP {n.status_code}).")
                        except Exception as e:
                            st.warning(f"No se pudo enviar la notificación: {e}")

                else:
                    st.error(f"Error en alta (HTTP {resp.status_code}).")
            except Exception as e:
                st.error(f"Error al conectar: {e}")

st.markdown("---")

# =======================
# BLOQUE 2 — Consulta en backend (PRIMERO DESPUÉS DEL FORM)
# =======================
st.subheader("🔎 Consultar en backend (por cédula)")
cedula_default = st.session_state.get("ultima_cedula", "")
col_inp, col_btn = st.columns([3,1])
with col_inp:
    cedula_input = st.text_input("Cédula (num_identificacion)", value=cedula_default or "", placeholder="1999999999")
with col_btn:
    refrescar = st.button("🔄 Refrescar en backend", use_container_width=True)

registro_remoto = None
if (cedula_input or "").strip() and refrescar:
    with st.spinner("Consultando /filter/{id}…"):
        try:
            registro_remoto = consultar_por_cedula(API_FILTER_BASE, cedula_input, TIMEOUT)
            if registro_remoto:
                st.success("Datos recuperados desde el backend.")
                st.session_state["ultimo_registro_remoto"] = registro_remoto
            else:
                st.info("No se encontró registro para esa cédula.")
        except Exception as e:
            st.error(f"No se pudo consultar el backend: {e}")

# Tabs de visualización (se muestran acá, antes del resto)
tab1, tab2 = st.tabs(["📤 Enviado (esta sesión)", "📥 Recuperado (backend)"])
with tab1:
    enviado = st.session_state.get("ultimo_registro_enviado")
    if enviado:
        render_info_grid(enviado)
    else:
        st.info("Aún no enviaste un registro en esta sesión.")
with tab2:
    recuperado = st.session_state.get("ultimo_registro_remoto")
    if recuperado:
        render_info_grid(recuperado)
        with st.expander("📋 Ver payload completo"):
            df = pd.DataFrame([recuperado]).T
            st.dataframe(df, use_container_width=True)
    else:
        st.info("Aún no hay datos recuperados. Usá el alta o la consulta manual.")

# =======================
# BLOQUE 3 — Avanzado / Debug (DESPUÉS)
# =======================
st.markdown("---")
with st.expander("🛠️ Avanzado / Debug"):
    resp_append = st.session_state.get("ultima_respuesta_append")
    if resp_append is not None:
        mostrar_http("Respuesta /append", resp_append)

    resp_notif = st.session_state.get("ultima_respuesta_notif")
    if resp_notif is not None:
        mostrar_http("Respuesta notificación", resp_notif)

