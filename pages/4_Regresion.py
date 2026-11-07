"""Página de correlación y regresión lineal."""

import streamlit as st

from src.datos import tarjeta_estudiante


st.set_page_config(page_title="Regresión", layout="wide")
tarjeta_estudiante()
st.title("Regresión")
st.info("En construcción")
st.markdown("""
- Correlaciones de Pearson y Spearman.
- Regresión lineal simple mediante mínimos cuadrados ordinarios.
- Bondad de ajuste e inferencia sobre la pendiente.
- Intervalos de confianza y de predicción.
- Diagnóstico de residuos, supuestos y observaciones influyentes.
""")
