"""Herramientas de exportación con botones de descarga de Streamlit."""

from io import BytesIO

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


def tabla_excel(
    tablas: dict[str, pd.DataFrame] | pd.DataFrame,
    nombre_archivo: str,
    etiqueta: str = "Descargar tablas en Excel",
) -> None:
    """Escribe una o varias tablas en un archivo Excel de bytes y crea el botón."""
    if isinstance(tablas, pd.DataFrame):
        tablas = {"Resultados": tablas}
    salida = BytesIO()
    with pd.ExcelWriter(salida, engine="openpyxl") as escritor:
        for hoja, tabla in tablas.items():
            nombre_hoja = str(hoja)[:31] if hoja else "Resultados"
            tabla.to_excel(escritor, sheet_name=nombre_hoja, index=False)
    st.download_button(
        etiqueta,
        data=salida.getvalue(),
        file_name=nombre_archivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def figura_png(
    figura: plt.Figure,
    nombre_archivo: str,
    etiqueta: str = "Descargar figura en PNG",
) -> None:
    """Codifica una figura Matplotlib como PNG y muestra su botón de descarga."""
    salida = BytesIO()
    figura.savefig(salida, format="png", dpi=150, bbox_inches="tight")
    st.download_button(etiqueta, salida.getvalue(), nombre_archivo, "image/png")


def figura_pdf(
    figura: plt.Figure,
    nombre_archivo: str,
    etiqueta: str = "Descargar figura en PDF",
) -> None:
    """Codifica una figura Matplotlib como PDF y muestra su botón de descarga."""
    salida = BytesIO()
    figura.savefig(salida, format="pdf", bbox_inches="tight")
    st.download_button(
        etiqueta,
        salida.getvalue(),
        nombre_archivo,
        "application/pdf",
    )


def reporte_markdown(
    titulo: str,
    secciones: dict[str, str],
    nombre_archivo: str = "reporte.md",
) -> None:
    """Construye un reporte breve en Markdown y crea un botón de descarga."""
    partes = [f"# {titulo}", ""]
    for encabezado, texto in secciones.items():
        partes.extend([f"## {encabezado}", "", str(texto), ""])
    contenido = "\n".join(partes).encode("utf-8-sig")
    st.download_button(
        "Descargar reporte breve en Markdown",
        contenido,
        nombre_archivo,
        "text/markdown",
    )
