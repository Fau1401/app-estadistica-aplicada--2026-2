"""Página de análisis de distribuciones probabilísticas."""

import streamlit as st

from src.datos import tarjeta_estudiante


st.set_page_config(page_title="Distribuciones", layout="wide")
tarjeta_estudiante()
st.title("Distribuciones")
st.info("En construcción")
st.markdown("""
- Distribuciones Normal, Lognormal, Gamma, Weibull, Gumbel y GEV.
- Ajuste de precipitación máxima anual.
- Pruebas Kolmogorov-Smirnov y Anderson-Darling.
- Criterios AIC, BIC y AICc.
- Período de retorno, riesgo e incertidumbre.
- Comparación de modelos de secado en capa delgada.
""")
