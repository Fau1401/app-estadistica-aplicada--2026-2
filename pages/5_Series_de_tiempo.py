"""Página de análisis y pronóstico de series de tiempo."""

import streamlit as st

from src.datos import tarjeta_estudiante


st.set_page_config(page_title="Series de tiempo", layout="wide")
tarjeta_estudiante()
st.title("Series de tiempo")
st.info("En construcción")
st.markdown("""
- Componentes y promedios móviles.
- Índices estacionales y descomposición clásica.
- Métodos de referencia e históricos.
- Validación con MAE, RMSE y SMAPE.
- Pronóstico con AutoTS y medidas de incertidumbre.
""")
