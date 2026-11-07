"""Ajuste y comparación de modelos semiempíricos de secado."""

from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy.optimize import curve_fit


def _lewis(t: np.ndarray, k: float) -> np.ndarray:
    """Calcula el Lewis: MR = exp(-k·t)."""
    return np.exp(-k * t)


def _henderson_pabis(t: np.ndarray, a: float, k: float) -> np.ndarray:
    """Calcula Henderson-Pabis: MR = a·exp(-k·t)."""
    return a * np.exp(-k * t)


def _page(t: np.ndarray, k: float, n: float) -> np.ndarray:
    """Calcula Page: MR = exp(-k·t^n)."""
    return np.exp(-k * np.power(t, n))


def _logaritmico(t: np.ndarray, a: float, k: float, c: float) -> np.ndarray:
    """Calcula el modelo Logarítmico: MR = a·exp(-k·t) + c."""
    return a * np.exp(-k * t) + c


def _dos_terminos(t: np.ndarray, a: float, k0: float, b: float, k1: float) -> np.ndarray:
    """Calcula Dos términos: a·exp(-k0·t) + b·exp(-k1·t)."""
    return a * np.exp(-k0 * t) + b * np.exp(-k1 * t)


# Cada entrada contiene la ecuación, el valor inicial y los límites razonables.
# Los nombres ayudan a interpretar el reporte y los p0 aceleran la convergencia.
MODELOS: dict[str, dict[str, Any]] = {
    "Lewis": {
        "funcion": _lewis,
        "p0": [0.005],
        "limites": ([0.0], [np.inf]),
        "nombres_parametros": ["k"],
    },
    "Henderson-Pabis": {
        "funcion": _henderson_pabis,
        "p0": [1.0, 0.005],
        "limites": ([0.0, 0.0], [np.inf, np.inf]),
        "nombres_parametros": ["a", "k"],
    },
    "Page": {
        "funcion": _page,
        "p0": [0.005, 1.0],
        "limites": ([0.0, 0.0], [np.inf, np.inf]),
        "nombres_parametros": ["k", "n"],
    },
    "Logarítmico": {
        "funcion": _logaritmico,
        "p0": [1.0, 0.005, 0.0],
        "limites": ([0.0, 0.0, -1.0], [np.inf, np.inf, 1.0]),
        "nombres_parametros": ["a", "k", "c"],
    },
    "Dos términos": {
        "funcion": _dos_terminos,
        "p0": [0.5, 0.002, 0.5, 0.02],
        "limites": ([0.0, 0.0, 0.0, 0.0], [np.inf, np.inf, np.inf, np.inf]),
        "nombres_parametros": ["a", "k0", "b", "k1"],
    },
}


def _datos_curva(t: Any, MR: Any) -> tuple[np.ndarray, np.ndarray]:
    """Convierte tiempo y humedad en arreglos finitos y elimina faltantes."""
    tiempo = pd.to_numeric(pd.Series(t), errors="coerce").to_numpy(dtype=float)
    humedad = pd.to_numeric(pd.Series(MR), errors="coerce").to_numpy(dtype=float)
    mascara = np.isfinite(tiempo) & np.isfinite(humedad)
    return tiempo[mascara], humedad[mascara]


def ajustar_curva(
    t: Any,
    MR: Any,
    nombre: str,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Ajusta un modelo semiempírico con mínimos cuadrados no lineales.

    ``curve_fit`` minimiza la suma de cuadrados entre los MR observados y los
    predichos. La función devuelve el vector de parámetros ajustados y los MR
    calculados sobre el mismo tiempo observado.
    """
    if nombre not in MODELOS:
        raise ValueError(f"Modelo desconocido: {nombre}")
    tiempo, humedad = _datos_curva(t, MR)
    if len(tiempo) < len(MODELOS[nombre]["p0"]):
        raise ValueError("No hay suficientes observaciones para ajustar el modelo.")

    modelo = MODELOS[nombre]
    parametros, _ = curve_fit(
        modelo["funcion"],
        tiempo,
        humedad,
        p0=modelo["p0"],
        bounds=modelo["limites"],
        maxfev=100000,
    )
    ajustados = modelo["funcion"](tiempo, *parametros)
    return parametros, ajustados


def metricas_curva(MR: Any, MR_ajustado: Any, k: int) -> dict[str, float]:
    """
    Calcula métricas de calidad del ajuste y criterios de información.

    - R² = 1 - SCE/SCT mide la fracción explicada.
    - RMSE = sqrt(SCE/n) es el error cuadrático medio.
    - χ² reducido aproxima la suma (MR-ŷ)²/ŷ dividida entre los grados de
      libertad n-k. El denominador evita usar cero mediante un límite pequeño.
    - AIC = n·ln(SCE/n) + 2k.
    - AICc agrega la corrección por muestra pequeña:
      AICc = AIC + 2k(k+1)/(n-k-1).
    """
    observado = np.asarray(MR, dtype=float)
    predicho = np.asarray(MR_ajustado, dtype=float)
    mascara = np.isfinite(observado) & np.isfinite(predicho)
    observado = observado[mascara]
    predicho = predicho[mascara]
    n = len(observado)
    if n == 0:
        raise ValueError("No hay observaciones válidas para calcular métricas.")

    residuos = observado - predicho
    sce = float(np.sum(residuos ** 2))
    sct = float(np.sum((observado - observado.mean()) ** 2))
    r2 = 1.0 - sce / sct if sct > 0 else float("nan")
    rmse = float(np.sqrt(sce / n))
    predicho_seguro = np.maximum(np.abs(predicho), np.finfo(float).eps)
    chi2 = float(np.sum(residuos ** 2 / predicho_seguro))
    grados_libertad = n - k
    chi2_reducido = chi2 / grados_libertad if grados_libertad > 0 else float("nan")

    if sce > 0:
        aic = n * np.log(sce / n) + 2.0 * k
    else:
        aic = float("-inf")
    aicc = (
        aic + 2.0 * k * (k + 1.0) / (n - k - 1.0)
        if n - k - 1.0 > 0
        else float("nan")
    )
    return {
        "R2": r2,
        "RMSE": rmse,
        "chi2_reducido": chi2_reducido,
        "AIC": float(aic),
        "AICc": float(aicc),
    }


def tabla_modelos(t: Any, MR: Any) -> pd.DataFrame:
    """
    Ajusta todos los modelos y devuelve sus parámetros y métricas por AICc.

    Los parámetros se presentan como texto legible para la tabla. La columna
    ``k`` identifica el número de parámetros estimados y el mismo valor se usa
    en los criterios de información.
    """
    filas: list[dict[str, Any]] = []
    for nombre, especificacion in MODELOS.items():
        try:
            parametros, ajustados = ajustar_curva(t, MR, nombre)
            tiempo, observado = _datos_curva(t, MR)
            k = len(parametros)
            metricas = metricas_curva(observado, ajustados, k)
            fila = {"modelo": nombre, "k": k}
            fila["parametros"] = ", ".join(
                f"{nombre_parametro}={valor:.6f}"
                for nombre_parametro, valor in zip(
                    especificacion["nombres_parametros"],
                    parametros,
                )
            )
            for nombre_parametro, valor in zip(
                especificacion["nombres_parametros"],
                parametros,
            ):
                clave = "k_modelo" if nombre_parametro == "k" else nombre_parametro
                fila[clave] = float(valor)
            fila.update(metricas)
            filas.append(fila)
        except (ValueError, RuntimeError, FloatingPointError):
            filas.append({
                "modelo": nombre,
                "k": np.nan,
                "R2": np.nan,
                "RMSE": np.nan,
                "chi2_reducido": np.nan,
                "AIC": np.nan,
                "AICc": np.nan,
            })

    tabla = pd.DataFrame(filas)
    if tabla.empty or tabla["AICc"].dropna().empty:
        return tabla
    tabla["delta_AICc"] = tabla["AICc"] - tabla["AICc"].min()
    return tabla.sort_values("AICc", na_position="last").reset_index(drop=True)
