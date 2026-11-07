"""Página de inicio de la aplicación de Estadística Aplicada."""

import streamlit as st

from src.datos import tarjeta_estudiante


st.set_page_config(
    page_title="Estadística Aplicada con Python y R",
    layout="wide",
)


def main() -> None:
    """Construye el contenido de la página de inicio."""
    tarjeta_estudiante()

    st.title("App de Estadística Aplicada — Ingeniería Agrícola, Unisucre")

    st.markdown(
        "Esta aplicación acompaña el aprendizaje de estadística aplicada mediante "
        "datos agrícolas simulados y herramientas interactivas en Streamlit."
    )

    st.header("Propósito de la app")
    st.write(
        "Permite explorar datos de parcelas, precipitación, clima y secado; "
        "reconocer patrones; ajustar modelos estadísticos; evaluar supuestos; "
        "interpretar resultados y validar cálculos mediante procedimientos "
        "reproducibles."
    )

    st.header("Páginas disponibles")
    st.markdown("""
    - **Datos:** carga, visualización y preparación de los conjuntos disponibles.
    - **EDA:** análisis exploratorio con resúmenes, histogramas, diagramas de caja y correlaciones.
    - **Distribuciones:** ajuste y comparación de modelos probabilísticos para extremos y secado.
    - **Regresión:** correlación, regresión por mínimos cuadrados ordinarios y diagnóstico de residuos.
    - **Series de tiempo:** componentes, descomposición, referencia, validación y pronóstico.
    """)

    st.header("Lápiz y Algoritmo")
    st.info(
        "Primero se calcula a mano o en papel para comprender fórmulas, unidades y "
        "supuestos. Después se verifica el resultado con la app, Python y R, "
        "comparando valores, gráficos y decisiones estadísticas."
    )

    st.warning(
        "La app apoya el aprendizaje, pero la interpretación de resultados y la "
        "responsabilidad académica son exclusivas del estudiante."
    )


if __name__ == "__main__":
    main()
