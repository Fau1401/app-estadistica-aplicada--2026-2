"""Funciones estadísticas reutilizables para el análisis exploratorio de datos."""

from typing import Any

import pandas as pd


def resumen_numerico(serie: pd.Series) -> dict[str, Any]:
    """
    Calcula medidas descriptivas de una variable numérica.

    Los cuartiles se calculan con el método tipo 7, que equivale al argumento
    ``method="linear"`` de pandas y a la interpolación usada de forma predeterminada
    por R. La desviación estándar y la varianza son muestrales (denominador n - 1).
    """
    valores = pd.to_numeric(serie, errors="coerce").dropna()

    # Si no hay observaciones válidas, se conserva una estructura uniforme.
    if valores.empty:
        return {
            "n": 0,
            "media": float("nan"),
            "mediana": float("nan"),
            "desviacion_estandar": float("nan"),
            "varianza": float("nan"),
            "cv_pct": float("nan"),
            "minimo": float("nan"),
            "q1": float("nan"),
            "q3": float("nan"),
            "maximo": float("nan"),
            "ric": float("nan"),
            "asimetria": float("nan"),
        }

    media = float(valores.mean())
    mediana = float(valores.median())
    desviacion_estandar = float(valores.std(ddof=1)) if len(valores) > 1 else 0.0
    varianza = float(valores.var(ddof=1)) if len(valores) > 1 else 0.0
    minimo = float(valores.min())
    q1 = float(valores.quantile(0.25))
    q3 = float(valores.quantile(0.75))
    maximo = float(valores.max())
    ric = q3 - q1
    cv_pct = (desviacion_estandar / abs(media) * 100.0) if media != 0 else float("nan")
    asimetria = float(valores.skew()) if len(valores) >= 3 else 0.0

    return {
        "n": int(valores.count()),
        "media": media,
        "mediana": mediana,
        "desviacion_estandar": desviacion_estandar,
        "varianza": varianza,
        "cv_pct": cv_pct,
        "minimo": minimo,
        "q1": q1,
        "q3": q3,
        "maximo": maximo,
        "ric": ric,
        "asimetria": asimetria,
    }


def vallas_tukey(serie: pd.Series) -> tuple[float, float, list[Any]]:
    """
    Calcula las vallas de Tukey y devuelve los valores ubicados fuera de ellas.

    La valla inferior es Q1 - 1.5·RIC y la superior es Q3 + 1.5·RIC.
    """
    valores = pd.to_numeric(serie, errors="coerce").dropna()
    if valores.empty:
        return float("nan"), float("nan"), []

    q1 = float(valores.quantile(0.25))
    q3 = float(valores.quantile(0.75))
    ric = q3 - q1
    limite_inferior = q1 - 1.5 * ric
    limite_superior = q3 + 1.5 * ric
    atipicos = valores[(valores < limite_inferior) | (valores > limite_superior)].tolist()
    return limite_inferior, limite_superior, atipicos


def tabla_frecuencias(serie: pd.Series) -> pd.DataFrame:
    """Construye frecuencias absolutas y relativas para una variable cualitativa."""
    datos = serie.dropna()
    conteos = datos.value_counts(dropna=False)
    total = int(conteos.sum())
    relativas = conteos / total if total else conteos * 0.0
    return pd.DataFrame({
        "categoria": conteos.index.astype(str),
        "frecuencia_absoluta": conteos.values,
        "frecuencia_relativa": relativas.values,
    })
