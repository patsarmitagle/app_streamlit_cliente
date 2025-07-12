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
        response = requests.post("https://api-cliente-jbz1.onrender.com/registro", json=payload)
        if response.status_code == 200:
            st.success("¡Registro exitoso! En breve recibirás un mensaje.")
        else:
            st.error("Ocurrió un error al registrar.")
    except Exception as e:
        st.error(f"Error al conectar: {e}")

# Mostrar datos del último registro
try:
    response = requests.get("https://api-cliente-jbz1.onrender.com/registros")

    if response.status_code == 200 and response.content:
        registros = response.json()

        if registros:
            ultimo = registros[-1]

            st.markdown("### 🔍 Último registro creado")

            # Función para mostrar input con botón copiar
            def copy_button(label, text, id_html):
                html(f"""
                    <div style="margin-bottom:10px">
                        <span style="font-weight:bold; margin-right:10px">{label}</span>
                        <input type="text" value="{text}" id="{id_html}" readonly style="margin-right:10px; padding:5px; border-radius:5px; width:200px"/>
                        <button onclick="navigator.clipboard.writeText(document.getElementById('{id_html}').value)">📋 Copiar</button>
                    </div>
                """, height=40)

            # Mostrar número de identificación y fecha con botón copiar
            copy_button("🆔 Número de Identificación", ultimo.get("num_identificacion"), "identificacion")
            copy_button("📅 Fecha de Nacimiento", ultimo.get("fecha_nacimiento"), "fecha")

            st.markdown(f"👤 **Nombre completo:**")
            st.code(ultimo.get("nombre_completo"))

            st.markdown(f"📱 **Teléfono:**")
            st.code(ultimo.get("num_telefono"))

            st.markdown(f"🆔 **ID Cliente:**")
            st.code(ultimo.get("id_cliente"))

        else:
            st.warning("No hay registros aún.")
    else:
        st.warning("No se pudo obtener la información del servidor.")
except Exception as e:
    st.error(f"Error: {e}")

# Mostrar todos los registros como tabla
with st.expander("📋 Ver registros actuales"):
    try:
        if 'registros' in locals():
            df = pd.DataFrame(registros)
            st.dataframe(df)
        else:
            st.write("No se pudo cargar la tabla.")
    except:
        st.write("No se pudo cargar la tabla.")
