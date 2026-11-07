"""Página de datos de la aplicación multipágina."""

import streamlit as st

from src.datos import tarjeta_estudiante


st.set_page_config(page_title="Datos", layout="wide")
tarjeta_estudiante()
st.title("Datos")
st.info("En construcción")
st.markdown("""
- Carga de archivos CSV y XLSX.
- Vista previa y selección de variables.
- Tipos de datos, faltantes y duplicados.
- Estadísticos descriptivos y filtros.
- Preparación y registro de transformaciones.
""")
