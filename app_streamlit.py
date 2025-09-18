import streamlit as st
import requests
import pandas as pd
import re
from streamlit.components.v1 import html

st.set_page_config(page_title="Registro Préstamos", layout="centered")

# --- Constantes ---
API_REGISTRO = "https://api-cliente-jbzl.onrender.com/registro"
API_REGISTROS = "https://api-cliente-jbzl.onrender.com/registros"
API_NOTIF = "https://api-notificacion-haqu.onrender.com/enviar-notificacion"
TIMEOUT = 20
PHONE_RE = re.compile(r"^\d{11,15}$")

def es_telefono_valido(tel: str) -> bool:
    return bool(PHONE_RE.match((tel or "").strip()))

st.image("Logo_BeClever_VersionPrincipal_Color.png", width=250)
st.title("📲 Registro a la Campaña de Préstamos")
st.markdown("Ingresá tu número con código país (ej: **5491123456789**):")

# --- Formulario de registro ---
with st.form("form_registro", clear_on_submit=False):
    telefono = st.text_input("", placeholder="5491123456789")
    enviar = st.form_submit_button("✅ Quiero participar", use_container_width=True)

if enviar:
    tel = (telefono or "").strip()
    if not es_telefono_valido(tel):
        st.error("Revisá el formato (11–15 dígitos, con código país).")
    else:
        payload = {"num_telefono": tel}
        with st.spinner("Registrando…"):
            try:
                response = requests.post(API_REGISTRO, json=payload, timeout=TIMEOUT)
                if response.status_code == 200:
                    # Parseo seguro de JSON
                    try:
                        cliente = response.json()
                    except ValueError:
                        st.error("La API de registro no devolvió JSON válido.")
                        cliente = None

                    if cliente:
                        st.success("¡Registro exitoso! En breve recibirás un mensaje.")

                        # Enviar notificación (con claves seguras)
                        payload_notificacion = {
                            "nombres": cliente.get("nombres", ""),
                            "primer_apellido": cliente.get("primer_apellido", ""),
                            "num_telefono": cliente.get("num_telefono", tel),
                        }
                        try:
                            notif_response = requests.post(API_NOTIF, json=payload_notificacion, timeout=TIMEOUT)
                            if notif_response.status_code == 200:
                                st.success("📩 Notificación enviada por WhatsApp.")
                            else:
                                st.warning(f"No se pudo enviar la notificación: {notif_response.text}")
                        except Exception as e:
                            st.warning(f"No se pudo enviar la notificación: {e}")
                else:
                    st.error(f"Ocurrió un error al registrar (HTTP {response.status_code}).")
            except Exception as e:
                st.error(f"Error al conectar: {e}")

# --- Utilidad botón copiar (opcional) ---
def copy_button(label, text, input_id):
    html(f"""
        <div style="margin-bottom:10px">
            <span style="font-weight:bold; margin-right:10px">{label}:</span>
            <input type="text" value="{text}" id="{input_id}" readonly
                   style="margin-right:10px; padding:5px; border-radius:5px; width:200px"/>
            <button onclick="navigator.clipboard.writeText(document.getElementById('{input_id}').value)">📋 Copiar</button>
        </div>
    """, height=40)

# --- Mostrar datos del último registro ---
if "ultimo_registro" not in st.session_state:
    st.session_state["ultimo_registro"] = None

registros_validos = []  # siempre definimos la variable
ultimo = None

try:
    with st.spinner("Cargando registros…"):
        response = requests.get(API_REGISTROS, timeout=TIMEOUT)
        response.raise_for_status()
        try:
            registros = response.json()
        except ValueError:
            st.warning("La API de registros no devolvió JSON válido.")
            registros = []

        if isinstance(registros, list):
            # Filtrar registros válidos
            registros_validos = [r for r in registros if r.get("num_identificacion") and r["num_identificacion"] != "num_identificacion"]
            if registros_validos:
                ultimo = registros_validos[-1]
        else:
            st.warning("La API de registros no devolvió una lista.")
except Exception as e:
    st.warning("No se pudo obtener la información del servidor.")
    st.error(f"{e}")

st.markdown("### 🔍 Último registro creado")
if ultimo:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🆔 Número de Identificación:**")
        st.code(str(ultimo.get("num_identificacion", "")))
        st.markdown("**🎂 Fecha de Nacimiento:**")
        st.code(str(ultimo.get("fecha_nacimiento", "")))
        st.markdown("**🆔 ID Cliente:**")
        st.code(str(ultimo.get("id_cliente", "")))
    with col2:
        st.markdown("**👤 Nombre completo:**")
        st.code(str(ultimo.get("nombre_completo", "")))
        st.markdown("**📞 Teléfono:**")
        st.code(str(ultimo.get("num_telefono", "")))
else:
    st.info("No hay registros válidos aún.")

# --- Tabla de registros (expander) ---
with st.expander("📋 Ver registros actuales"):
    if registros_validos:
        df = pd.DataFrame(registros_validos)
        # Orden amigable si existen estas columnas
        cols_order = [c for c in ["id_cliente", "num_identificacion", "nombre_completo", "num_telefono", "fecha_nacimiento"] if c in df.columns]
        if cols_order:
            df = df[cols_order]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.write("No hay registros para mostrar todavía.")
