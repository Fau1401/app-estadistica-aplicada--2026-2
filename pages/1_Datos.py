"""Página funcional para explorar los datos disponibles y cargar archivos propios."""

from pathlib import Path

import pandas as pd
import streamlit as st

from src.datos import cargar_csv, tarjeta_estudiante, tipos_de_variables, valores_faltantes


st.set_page_config(page_title="Datos", layout="wide")
tarjeta_estudiante()
st.title("Datos")

archivos_disponibles = {
    "parcelas.csv": "parcelas",
    "precip_max_anual.csv": "precipitación máxima anual",
    "clima_mensual.csv": "clima mensual",
    "secado.csv": "secado",
}

descripciones = {
    "parcelas.csv": (
        "Parcelas agrícolas simuladas con variables de suelo, riego, fertilización, "
        "materia orgánica, pH y rendimiento. Unidad de rendimiento: toneladas por hectárea (t/ha); "
        "nitrógeno: kg/ha; lámina: mm; materia orgánica: %; pH: adimensional. "
        "Se utiliza en EDA y Regresión.",
    ),
    "precip_max_anual.csv": (
        "Máxima precipitación registrada en 24 horas para cada año. "
        "pmax24h_mm está en milímetros (mm) y anio es un año calendario. "
        "Se utiliza en Distribuciones.",
    ),
    "clima_mensual.csv": (
        "Clima mensual simulado desde 2015 hasta 2025. La precipitación se expresa "
        "en milímetros (mm) y la temperatura en grados Celsius (°C). "
        "Se utiliza en Series de tiempo.",
    ),
    "secado.csv": (
        "Razón de humedad MR durante un proceso de secado en capa delgada. "
        "El tiempo está en minutos (min) y MR es adimensional. "
        "Se utiliza en Distribuciones para comparar modelos de secado.",
    ),
}

archivo_nombre = st.selectbox(
    "Seleccione uno de los datos disponibles",
    options=list(archivos_disponibles.keys()),
    format_func=lambda nombre: archivos_disponibles[nombre].capitalize(),
)

archivo_cargado = st.file_uploader(
    "También puede cargar un archivo CSV o Excel propio",
    type=["csv", "xlsx", "xls"],
)

if archivo_cargado is not None:
    try:
        if archivo_cargado.name.lower().endswith(".csv"):
            df = pd.read_csv(archivo_cargado)
            nombre_descarga = archivo_cargado.name
        else:
            df = pd.read_excel(archivo_cargado)
            nombre_descarga = Path(archivo_cargado.name).stem + ".csv"

        columnas_fecha = [columna for columna in df.columns if "fecha" in columna.lower()]
        for columna in columnas_fecha:
            df[columna] = pd.to_datetime(df[columna], errors="coerce")

        st.success(f"Archivo propio cargado: {archivo_cargado.name}")
        descripcion_archivo = "Archivo cargado por el usuario. Las unidades deben verificarse en el origen del archivo. Se aplica esta página para explorar su estructura."
    except Exception as error:
        st.error(f"No fue posible leer el archivo: {error}")
        st.stop()
else:
    df = cargar_csv(archivo_nombre)
    nombre_descarga = archivo_nombre
    descripcion_archivo = descripciones[archivo_nombre]

st.subheader("Vista general")
columna_filas, columna_columnas = st.columns(2)
with columna_filas:
    st.metric("Filas", f"{len(df):,}".replace(",", "."))
with columna_columnas:
    st.metric("Columnas", df.shape[1])

st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("Tipo y clasificación de las variables")
st.dataframe(tipos_de_variables(df), use_container_width=True, hide_index=True)

st.subheader("Valores faltantes por variable")
st.dataframe(valores_faltantes(df), use_container_width=True, hide_index=True)

st.subheader("Descripción del archivo")
st.write(descripcion_archivo)

contenido_csv = df.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "Descargar tabla en CSV",
    data=contenido_csv,
    file_name=nombre_descarga,
    mime="text/csv",
)
