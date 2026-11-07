"""Herramientas de análisis y pronóstico para series mensuales agrícolas."""

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose


RAIZ_PROYECTO = Path(__file__).resolve().parent.parent


def cargar_serie(variable: str) -> pd.Series:
    """
    Carga una variable mensual y devuelve una serie con índice de fechas.

    La función lee ``clima_mensual.csv``, convierte la columna fecha a
    ``DatetimeIndex`` y reindexa cada observación a frecuencia mensual MS
    (primer día del mes). Los meses faltantes se mantienen como NaN y deben
    tratarse antes de modelos que los rechacen.
    """
    if variable not in {"precipitacion_mm", "temperatura_c"}:
        raise ValueError(
            "variable debe ser 'precipitacion_mm' o 'temperatura_c'."
        )

    ruta = RAIZ_PROYECTO / "datos" / "clima_mensual.csv"
    datos = pd.read_csv(ruta, parse_dates=["fecha"])
    serie = datos.set_index("fecha")[variable].sort_index()
    serie = serie.asfreq("MS")
    serie.name = variable
    return serie


def promedio_movil(serie: pd.Series, orden: int) -> pd.Series:
    """
    Calcula un promedio móvil con ventana que termina en el mes actual.

    Se usa ``rolling(window=orden, min_periods=orden)``, por lo que una salida
    empieza después de completar la ventana completa de ``orden`` meses.
    """
    if orden < 1:
        raise ValueError("El orden del promedio móvil debe ser al menos 1.")
    serie_numerica = pd.to_numeric(serie, errors="coerce")
    return serie_numerica.rolling(window=orden, min_periods=orden).mean()


def indices_estacionales(serie: pd.Series) -> pd.Series:
    """
    Calcula índices estacionales aditivos por mes.

    Para cada mes se promedia el valor observado y se resta el promedio
    general de la serie: índice_mes = media_mes - media_general. Si existen
    los 12 meses, la suma teórica de los índices aditivos es cero. Se aplica
    una pequeña corrección central para eliminar el residuo numérico y lograr
    aproximadamente la suma cero exigida.
    """
    serie_numerica = pd.to_numeric(serie, errors="coerce").dropna()
    if serie_numerica.empty:
        return pd.Series(dtype=float, name="indice_estacional")

    promedio_general = float(serie_numerica.mean())
    indices = (
        serie_numerica.groupby(serie_numerica.index.month).mean()
        - promedio_general
    )
    indices.index = pd.Index(indices.index, name="mes")
    indices.name = "indice_estacional"

    # Centros numéricos y promedio móvil pueden dejar una suma pequeña distinta
    # de cero; se centra para que el ajuste aditivo represente exactamente 12 meses.
    if len(indices) == 12:
        indices = indices - indices.mean()
    return indices.sort_index()


def descomponer(serie: pd.Series):
    """
    Descompone una serie mensual con el modelo aditivo y periodo de 12 meses.

    Devuelve el objeto de ``statsmodels.tsa.seasonal.seasonal_decompose`` con
    observada, tendencia, estacionalidad y residuo. La serie se reindexa a
    frecuencia mensual e interpola faltantes únicamente para este cálculo.
    """
    serie_numerica = pd.to_numeric(serie, errors="coerce")
    serie_numerica = serie_numerica.asfreq("MS").interpolate(method="time")
    serie_numerica = serie_numerica.ffill().bfill().dropna()
    if len(serie_numerica) < 24:
        raise ValueError(
            "Se necesitan al menos 24 meses para una descomposición estacional."
        )
    return seasonal_decompose(
        serie_numerica,
        model="additive",
        period=12,
        extrapolate_trend="period",
    )


def metodos_referencia(
    entrenamiento: pd.Series,
    h: int,
) -> dict[str, pd.Series]:
    """
    Construye pronósticos de referencia para los próximos h meses.

    - Ingenuo: repite el último valor observado.
    - Estacional ingenuo: usa el mismo mes de 12 meses atrás.
    - Promedio: repite la media histórica del entrenamiento.

    Las fechas resultantes comienzan después del último índice de entrenamiento.
    """
    if h < 1:
        raise ValueError("El horizonte h debe ser al menos 1 mes.")

    serie = pd.to_numeric(entrenamiento, errors="coerce").dropna().sort_index()
    if serie.empty:
        raise ValueError("El entrenamiento no contiene datos válidos.")
    if not isinstance(serie.index, pd.DatetimeIndex):
        raise TypeError("El índice de entrenamiento debe ser de fechas.")

    ultimo = serie.index.max()
    horizonte = pd.date_range(start=ultimo + pd.offsets.MonthBegin(1), periods=h, freq="MS")

    ing = pd.Series(np.repeat(float(serie.iloc[-1]), h), index=horizonte, name="Ingenuo")
    promedio = pd.Series(np.repeat(float(serie.mean()), h), index=horizonte, name="Promedio")

    estacional = []
    for fecha in horizonte:
        fecha_anterior = fecha - pd.DateOffset(years=1)
        if fecha_anterior in serie.index and pd.notna(serie.loc[fecha_anterior]):
            estacional.append(float(serie.loc[fecha_anterior]))
        else:
            # Mes anterior disponible como alternativa transparente si falta una
            # observación del año previo.
            estacional.append(float(serie.iloc[-1]))
    estacional_serie = pd.Series(
        estacional,
        index=horizonte,
        name="Estacional ingenuo",
    )

    return {
        "Ingenuo": ing,
        "Estacional ingenuo": estacional_serie,
        "Promedio": promedio,
    }


def metricas(real: Iterable[float], pronostico: Iterable[float]) -> dict[str, float]:
    """
    Calcula MAE, RMSE y SMAPE para valores reales y pronosticados.

    Con e = real-pronóstico, MAE=media(|e|), RMSE=sqrt(media(e²)) y
    SMAPE=200·media(|e|/(|real|+|pronóstico|)). Los pares no finitos se excluyen.
    """
    reales = np.asarray(list(real), dtype=float)
    pronosticados = np.asarray(list(pronostico), dtype=float)
    if reales.shape != pronosticados.shape:
        raise ValueError("Real y pronóstico deben tener la misma longitud.")

    mascara = np.isfinite(reales) & np.isfinite(pronosticados)
    reales = reales[mascara]
    pronosticados = pronosticados[mascara]
    if len(reales) == 0:
        return {"MAE": float("nan"), "RMSE": float("nan"), "SMAPE": float("nan")}

    errores = reales - pronosticados
    mae = float(np.mean(np.abs(errores)))
    rmse = float(np.sqrt(np.mean(errores ** 2)))
    denominador = np.abs(reales) + np.abs(pronosticados)
    if np.any(denominador == 0):
        # Si ambos son cero, el término se define como cero en vez de 0/0.
        terminos = np.zeros_like(denominador)
        positivos = denominador > 0
        terminos[positivos] = np.abs(errores[positivos]) / denominador[positivos]
    else:
        terminos = np.abs(errores) / denominador
    smape = float(200.0 * np.mean(terminos))
    return {"MAE": mae, "RMSE": rmse, "SMAPE": smape}


def concurso_referencia(muestra24: pd.DataFrame) -> pd.DataFrame:
    """
    Compara tres pronósticos de referencia en seis meses de validación.

    Se usa el conjunto marcado como ``entrenamiento`` para ajustarlos y los
    últimos 24 registros deben estar ordenados por fecha. La tabla resultante
    se ordena por SMAPE, por lo que el primer método es el mejor de referencia.
    """
    requeridas = {"fecha", "precipitacion_mm", "conjunto"}
    if not requeridas.issubset(muestra24.columns):
        faltantes = requeridas.difference(muestra24.columns)
        raise ValueError(f"Faltan columnas: {', '.join(sorted(faltantes))}")

    datos = muestra24.copy()
    datos["fecha"] = pd.to_datetime(datos["fecha"])
    datos = datos.sort_values("fecha")
    datos["precipitacion_mm"] = pd.to_numeric(
        datos["precipitacion_mm"],
        errors="coerce",
    )

    entrenamiento_df = datos.loc[datos["conjunto"] == "entrenamiento"]
    validacion_df = datos.loc[datos["conjunto"] == "validacion"]
    if len(entrenamiento_df) != 18:
        raise ValueError("El conjunto de entrenamiento debe tener 18 meses.")
    if len(validacion_df) != 6:
        raise ValueError("El conjunto de validación debe tener 6 meses.")

    entrenamiento = (
        entrenamiento_df.set_index("fecha")["precipitacion_mm"]
        .sort_index()
        .asfreq("MS")
    )
    validacion = (
        validacion_df.set_index("fecha")["precipitacion_mm"]
        .sort_index()
        .asfreq("MS")
    )

    pronosticos = metodos_referencia(entrenamiento, h=len(validacion))
    filas = []
    for nombre_metodo, pronostico in pronosticos.items():
        reales_alineados = validacion.reindex(pronostico.index)
        metricas_metodo = metricas(reales_alineados, pronostico)
        filas.append({
            "metodo": nombre_metodo,
            **metricas_metodo,
        })
    return pd.DataFrame(filas).sort_values("SMAPE").reset_index(drop=True)


if __name__ == "__main__":
    ruta_muestra = RAIZ_PROYECTO / "datos" / "muestra_series24.csv"
    muestra24 = pd.read_csv(ruta_muestra, parse_dates=["fecha"])
    print(concurso_referencia(muestra24).to_string(index=False))
