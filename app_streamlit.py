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
            placeholder="5491123456789"
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

# ===== Último registro =====
st.subheader("🔍 Último registro creado")
