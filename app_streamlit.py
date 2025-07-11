import streamlit as st
import requests

API_URL = "https://api-cliente-jbzl.onrender.com"

st.set_page_config(page_title="Registro de Campaña", page_icon="📲")

st.title("📲 Registro a la Campaña de Préstamos")

numero = st.text_input("Ingresá tu número con código país (ej: 5491123456789):")

if st.button("✅ Quiero participar"):
    if numero:
        try:
            response = requests.post(f"{API_URL}/registro", json={"num_telefono": numero})
            if response.status_code == 200:
                st.success("¡Registro exitoso! En breve recibirás un mensaje.")
            else:
                st.error(f"Ocurrió un error. Código: {response.status_code}")
        except Exception as e:
            st.error(f"Error de conexión: {e}")
    else:
        st.warning("Ingresá un número válido antes de continuar.")

# OPCIONAL: ver todos los registros
with st.expander("📋 Ver registros actuales"):
    try:
        registros = requests.get(f"{API_URL}/registros").json()
        if registros:
            st.write(registros)
        else:
            st.info("No hay registros aún.")
    except Exception as e:
        st.error(f"No se pudieron cargar los registros: {e}")
