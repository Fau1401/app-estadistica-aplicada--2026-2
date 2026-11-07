"""Funciones de carga y presentación de los datos del proyecto."""

import json
from pathlib import Path

import pandas as pd
import streamlit as st


RAIZ_PROYECTO = Path(__file__).resolve().parent.parent
CARPETA_DATOS = RAIZ_PROYECTO / "datos"


@st.cache_data
def cargar_csv(nombre: str) -> pd.DataFrame:
    """
    Carga un archivo CSV ubicado en la carpeta datos del proyecto.

    Las columnas cuyo nombre contiene "fecha" se interpretan como fechas para
    facilitar los análisis temporales posteriores.
    """
    ruta = CARPETA_DATOS / nombre
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encontró el archivo de datos: {ruta}")

    # Identifica todas las columnas de fecha antes de leer el archivo.
    columnas = pd.read_csv(ruta, nrows=0).columns
    columnas_fecha = [columna for columna in columnas if "fecha" in columna.lower()]

    return pd.read_csv(ruta, parse_dates=columnas_fecha if columnas_fecha else None)


def cargar_metadatos() -> dict:
    """Lee y devuelve los metadatos personalizados del estudiante."""
    ruta = CARPETA_DATOS / "metadatos.json"
    if not ruta.is_file():
        raise FileNotFoundError(f"No se encontró el archivo de metadatos: {ruta}")

    with ruta.open("r", encoding="utf-8") as archivo:
        return json.load(archivo)


def tarjeta_estudiante() -> None:
    """Muestra los datos personalizados del estudiante en la barra lateral."""
    metadatos = cargar_metadatos()

    st.sidebar.markdown("### Estudiante")
    st.sidebar.write(f"**Nombre:** {metadatos['nombre']}")
    st.sidebar.write(f"**Código:** {metadatos['codigo']}")
    st.sidebar.write(f"**Cultivo:** {metadatos['cultivo']}")
    st.sidebar.write(f"**Municipio:** {metadatos['municipio']}")
    st.sidebar.write(f"**Huella:** `{metadatos['huella']}`")


def tipos_de_variables(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clasifica las variables de un DataFrame como nominales, ordinales,
    cuantitativas discretas o cuantitativas continuas.

    Para variables ordinales se reconocen nombres que contienen "nivel",
    "clase", "categoria", "categoría", "orden" o "grupo". Las variables
    numéricas enteras se consideran discretas y las de punto flotante,
    continuas.
    """
    nombres_ordinales = ("nivel", "clase", "categoria", "categoría", "orden", "grupo")
    filas = []

    for variable in df.columns:
        tipo_dato = str(df[variable].dtype)
        nombre = variable.lower()

        if pd.api.types.is_datetime64_any_dtype(df[variable]):
            clasificacion = "cuantitativa continua"
        elif pd.api.types.is_bool_dtype(df[variable]) or pd.api.types.is_object_dtype(df[variable]) or pd.api.types.is_string_dtype(df[variable]):
            clasificacion = "cualitativa ordinal" if any(palabra in nombre for palabra in nombres_ordinales) else "cualitativa nominal"
        elif pd.api.types.is_integer_dtype(df[variable]):
            clasificacion = "cuantitativa discreta"
        elif pd.api.types.is_float_dtype(df[variable]):
            clasificacion = "cuantitativa continua"
        else:
            clasificacion = "cualitativa nominal"

        filas.append({
            "variable": variable,
            "tipo de dato": tipo_dato,
            "clasificación estadística": clasificacion,
        })

    return pd.DataFrame(filas)


def valores_faltantes(df: pd.DataFrame) -> pd.DataFrame:
    """Calcula la cantidad y el porcentaje de valores faltantes por variable."""
    cantidades = df.isna().sum()
    porcentajes = cantidades / len(df) * 100 if len(df) else cantidades * 0.0

    return pd.DataFrame({
        "variable": cantidades.index,
        "cantidad faltante": cantidades.values,
        "porcentaje faltante": porcentajes.round(2).values,
    })
