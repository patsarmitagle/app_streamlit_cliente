import re
import requests
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Registro Préstamos",
    page_icon="📲",
    layout="centered"
)

# ===== Estilos =====
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.main {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-direction: column;
}
.card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 16px;
  padding: 1.5rem;
  text-align: center;
  max-width: 500px;
}
.badge {
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 12px;
  padding: .75rem;
  margin-bottom: .5rem;
  font-size: 0.95rem;
  text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ===== Header centrado =====
st.image("Logo_BeClever_VersionPrincipal_Color.png", width=150)
st.markdown("## 📲 Registro a la Campaña de Préstamos")
st.caption("Ingresá tu número con código país (ej: 5491123456789)")

st.markdown("---")

# ===== Formulario =====
PHONE_RE = re.compile(r"^\d{11,15}$")
def es_telefono_valido(tel: str) -> bool:
    return bool(PHONE_RE.match(tel))

with st.container():
    st.markdown('<div class="card">', unsafe_allow_html=True)
    with st.form("form_registro", clear_on_submit=False):
        telefono = st.text_input(
            "Número de WhatsApp",
            placeholder="5491123456789",
            label_visibility="collapsed"
        )
        enviar = st.form_submit_button("✅ Quiero participar", use_container_width=True)

    if enviar:
        if not es_telefono_valido(telefono.strip()):
            st.error("Revisá el formato (11–15 dígitos, con código país).")
        else:
            with st.spinner("Registrando…"):
                try:
                    r = requests.post(
                        "https://api-cliente-jbzl.onrender.com/registro",
                        json={"num_telefono": telefono.strip()},
                        timeout=20
                    )
                    if r.status_code == 200:
                        st.success("¡Registro exitoso! En breve recibirás un mensaje.")
                    else:
                        st.error("Error al registrar.")
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ===== Último registro (cards) =====
st.subheader("🔍 Último registro creado")

ultimo = None
registros_validos = []
try:
    r_all = requests.get("https://api-cliente-jbzl.onrender.com/registros", timeout=20)
    if r_all.status_code == 200:
        registros = r_all.json()
        registros_validos = [r for r in registros if r.get("num_identificacion") not in (None, "", "num_identificacion")]
        if registros_validos:
            ultimo = registros_validos[-1]
    else:
        st.warning(f"No se pudo obtener registros (HTTP {r_all.status_code}).")

except Exception as e:
    st.warning("No se pudo obtener la información del servidor.")
    st.exception(e)

if ultimo:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""<div class="badge"><strong>🆔 Número de Identificación</strong>{ultimo.get("num_identificacion","—")}</div>""",
                    unsafe_allow_html=True)
        st.markdown(f"""<div class="badge"><strong>👤 Nombre completo</strong>{ultimo.get("nombre_completo","—")}</div>""",
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="badge"><strong>🎂 Fecha de Nacimiento</strong>{ultimo.get("fecha_nacimiento","—")}</div>""",
                    unsafe_allow_html=True)
        st.markdown(f"""<div class="badge"><strong>📞 Teléfono</strong>{ultimo.get("num_telefono","—")}</div>""",
                    unsafe_allow_html=True)

    st.markdown(f"""<div class="badge"><strong>🆔 ID Cliente</strong>{ultimo.get("id_cliente","—")}</div>""",
                unsafe_allow_html=True)
else:
    st.info("No hay registros válidos aún.")

# ===== Tabla de registros =====
with st.expander("📋 Ver registros actuales"):
    if registros_validos:
        try:
            df = pd.DataFrame(registros_validos)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.write("No se pudo cargar la tabla.")
            st.exception(e)
    else:
        st.caption("Sin datos para mostrar.")
