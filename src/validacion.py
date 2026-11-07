"""Validaciones pedagógicas para evitar que la aplicación muestre errores técnicos."""

from collections.abc import Callable, Iterable
from typing import Any

import pandas as pd
import streamlit as st


def archivo_vacio(df: pd.DataFrame | None, nombre_archivo: str) -> bool:
    """Detecta un archivo inexistente o sin filas y explica cómo corregirlo."""
    if df is None or df.empty:
        st.error(
            f"El archivo {nombre_archivo} está vacío o no contiene filas. "
            "Qué pasó: no hay observaciones para realizar el análisis. "
            "Corrija el archivo CSV y revise que tenga al menos una fila de datos, además de encabezados."
        )
        return False
    return True


def columnas_seleccionadas(
    df: pd.DataFrame,
    columnas_requeridas: Iterable[str],
    nombre_contexto: str,
) -> bool:
    """Comprueba columnas necesarias antes de elegir o calcular una variable."""
    faltantes = sorted(set(columnas_requeridas) - set(df.columns))
    if faltantes:
        st.error(
            f"No se puede realizar {nombre_contexto} porque faltan las columnas "
            f"{', '.join(faltantes)}. Qué pasó: el archivo CSV no coincide con el formato esperado. "
            "Corrija los nombres de los encabezados o cargue la muestra original."
        )
        return False
    return True


def variable_respuesta_numerica(
    df: pd.DataFrame,
    columna: str,
    nombre_pagina: str = "el análisis",
) -> pd.Series | None:
    """Convierte una respuesta a numérico e informa si contiene texto inválido."""
    if columna not in df.columns:
        st.error(
            f"No existe la variable {columna} para realizar {nombre_pagina}. "
            "Seleccione otra columna o revise los encabezados del archivo."
        )
        return None
    serie = pd.to_numeric(df[columna], errors="coerce")
    no_numericos = int(serie.isna().sum() - df[columna].isna().sum())
    if no_numericos > 0 or serie.dropna().empty:
        st.error(
            f"La variable {columna} no es totalmente numérica. Qué pasó: "
            f"hay {no_numericos} valor(es) que no pudieron convertirse a número "
            f"y {int(serie.dropna().shape[0])} dato(s) numérico(s) válido(s). "
            "Corrija texto, símbolos o comas decimales en el archivo."
        )
        return None
    return serie


def datos_faltantes(
    df: pd.DataFrame,
    columnas: Iterable[str],
    nombre_contexto: str,
) -> bool:
    """Informa sobre faltantes y recuerda que no deben borrarse sin justificación."""
    existentes = [columna for columna in columnas if columna in df.columns]
    cantidad = int(df[existentes].isna().sum().sum())
    if cantidad > 0:
        st.warning(
            f"Se encontraron {cantidad} dato(s) faltante(s) en {nombre_contexto}. "
            "Qué pasó: el cálculo usará las filas disponibles, pero las faltantes pueden "
            "sesgar o reducir el análisis. No las borre sin justificar; revise el origen, "
            "documente el mecanismo y decida imputación o análisis por separado."
        )
        return False
    return True


def suficientes_datos(
    cantidad: int,
    minimo: int,
    nombre_contexto: str,
) -> bool:
    """Valida un mínimo de observaciones usando umbrales pedagógicos."""
    if cantidad < minimo:
        st.error(
            f"Hay {cantidad} observaciones para {nombre_contexto}; se necesitan al menos "
            f"{minimo}. Qué pasó: el cálculo sería poco estable o no cumpliría el diseño mínimo. "
            "Agregue datos válidos o revise los filtros antes de repetir el análisis."
        )
        return False
    return True


def error_ajuste(
    funcion: Callable[..., Any],
    *argumentos: Any,
    nombre_modelo: str,
    **kwargs: Any,
) -> Any | None:
    """Ejecuta un ajuste y convierte excepciones técnicas en mensajes pedagógicos."""
    try:
        return funcion(*argumentos, **kwargs)
    except (ValueError, TypeError, RuntimeError, FloatingPointError, ZeroDivisionError) as error:
        st.error(
            f"No fue posible ajustar {nombre_modelo}. Qué pasó: los datos o los valores "
            f"iniciales impidieron converger al modelo ({type(error).__name__}). "
            "Revise valores faltantes, rangos, ceros o constantes; luego pruebe otra "
            "selección o valide la calidad de la muestra."
        )
        return None
