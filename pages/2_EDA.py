"""Página de análisis exploratorio de datos."""

import streamlit as st

from src.datos import tarjeta_estudiante


st.set_page_config(page_title="EDA", layout="wide")
tarjeta_estudiante()
st.title("EDA: Análisis Exploratorio de Datos")
st.info("En construcción")
st.markdown("""
- Resúmenes por variable y por grupo.
- Histogramas, densidades y diagramas de caja.
- Dispersión, correlación y matriz de gráficos.
- Identificación de valores atípicos.
- Series temporales y frecuencias categóricas.
""")
