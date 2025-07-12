import streamlit as st
import requests
import pandas as pd
from streamlit.components.v1 import html

st.set_page_config(page_title="Registro Préstamos", layout="centered")

st.title("📲 Registro a la Campaña de Préstamos")
st.markdown("Ingresá tu número con código país (ej: 5491123456789):")

telefono = st.text_input("")

if st.button("✅ Quiero participar") and telefono:
    payload = {"num_telefono": telefono}
    try:
        response = requests.post("https://api-cliente-jbzl.onrender.com/registro", json=payload)
        if response.status_code == 200:
            st.success("¡Registro exitoso! En breve recibirás un mensaje.")
        else:
            st.error("Ocurrió un error al registrar.")
    except Exception as e:
        st.error(f"Error al conectar: {e}")

# Función para mostrar input con botón copiar
def copy_button(label, text, input_id):
    html(f"""
        <div style="margin-bottom:10px">
            <span style="font-weight:bold; margin-right:10px">{label}:</span>
            <input type="text" value="{text}" id="{input_id}" readonly style="margin-right:10px; padding:5px; border-radius:5px; width:200px"/>
            <button onclick="navigator.clipboard.writeText(document.getElementById('{input_id}').value)">📋 Copiar</button>
        </div>
    """, height=40)

# Mostrar datos del último registro

if "ultimo_registro" not in st.session_state:
    st.session_state["ultimo_registro"] = {}
    
try:
    response = requests.get("https://api-cliente-jbzl.onrender.com/registros")
    registros = response.json()

    # Filtrar registros válidos
    registros_validos = [r for r in registros if r["num_identificacion"] != "num_identificacion"]

    if registros_validos:
        ultimo = registros_validos[-1]
    if ultimo:
        st.markdown("### 🔍 Último registro creado")

        st.markdown("**🆔 Número de Identificación:**")
        st.code(ultimo.get("num_identificacion", ""),"")

        st.markdown("**🎂 Fecha de Nacimiento:**")
        st.code(ultimo.get("fecha_nacimiento", ""), language="")
            
        st.markdown("**👤 Nombre completo:**")
        st.code(ultimo.get("nombre_completo", ""))

        st.markdown("**📞 Teléfono:**")
        st.code(ultimo.get("num_telefono", ""))
        
        st.markdown(f"🆔 **ID Cliente:**")
        st.code(ultimo.get("id_cliente", ""))
    else:
        st.warning("No hay registros válidos aún.")

except Exception as e:
    st.warning("No se pudo obtener la información del servidor.")
    st.error(f"{e}")

# Mostrar todos los registros como tabla
with st.expander("📋 Ver registros actuales"):
    try:
        df = pd.DataFrame(registros_validos)
        st.dataframe(df)
    except Exception as e:
        st.write("No se pudo cargar la tabla.")
        st.error(f"{e}")
