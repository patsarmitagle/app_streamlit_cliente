import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Registro a Préstamos", page_icon="📲")

st.title("📲 Registro a la Campaña de Préstamos")
st.write("Ingresá tu número con código país (ej: 5491123456789):")

num_telefono = st.text_input("", placeholder="5491123456789")

if st.button("✅ Quiero participar"):
    if num_telefono.strip() != "":
        payload = {"num_telefono": num_telefono}
        response = requests.post("https://api-cliente-jbzl.onrender.com/registro", json=payload)

        if response.status_code == 200:
            st.success("¡Registro exitoso! En breve recibirás un mensaje.")
            data = response.json()
            nuevo_id = data["id_cliente"]
        else:
            st.error("Error al registrar el número.")
            nuevo_id = None
    else:
        st.warning("Ingresá un número válido.")
        nuevo_id = None
else:
    nuevo_id = None

# Obtener registros
registros_response = requests.get("https://api-cliente-jbzl.onrender.com/registros")
if registros_response.status_code == 200:
    registros = registros_response.json()

    if nuevo_id:
        # Mostrar último registro con botones de copiar
        ultimo = next((r for r in registros if r.get("id_cliente") == nuevo_id), None)
        if ultimo:
            st.markdown("### 🔍 Último registro creado")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**🆔 Número de Identificación**")
                st.text_input("", value=ultimo.get("num_identificacion"), key="id_copy", disabled=True)

            with col2:
                st.markdown("**📅 Fecha de Nacimiento**")
                st.text_input("", value=ultimo.get("fecha_nacimiento"), key="fecha_copy", disabled=True)

            st.markdown("**👤 Nombre completo:**")
            st.code(ultimo.get("nombre_completo"), language="text")

            st.markdown("**📱 Teléfono:**")
            st.code(ultimo.get("num_telefono"), language="text")

    # Mostrar todos los registros
    with st.expander("📋 Ver todos los registros actuales"):
        st.json(registros)
else:
    st.error("No se pudieron obtener los registros.")
