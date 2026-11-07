"""Selección de modelos probabilísticos para la precipitación máxima anual."""

import math
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats


# El diccionario reúne las distribuciones candidatas con su objeto de scipy.stats.
# Para las distribuciones con soporte positivo se fija la ubicación en cero;
# así se ajustan dos parámetros libres en vez de permitir una traslación artificial.
CANDIDATAS = {
    "Normal": stats.norm,
    "Lognormal": stats.lognorm,
    "Gamma": stats.gamma,
    "Weibull": stats.weibull_min,
    "Gumbel": stats.gumbel_r,
    "GEV": stats.genextreme,
    # En scipy, el parámetro de forma c de genextreme es -xi (menos el índice ξ
    # de cola de la teoría de valores extremos generalizada).
}


def _datos_validos(datos: Any) -> np.ndarray:
    """Convierte los datos a un arreglo y elimina los valores no disponibles."""
    serie = pd.Series(datos)
    return pd.to_numeric(serie, errors="coerce").dropna().to_numpy(dtype=float)


def _parametros_conocidos(nombre: str) -> dict[str, float] | None:
    """Devuelve los parámetros fijos exigidos por el modelo seleccionado."""
    if nombre in {"Lognormal", "Gamma", "Weibull"}:
        # La primera forma de la distribución suele quedar libre; únicamente loc=0 es fijo.
        return {"loc": 0.0}
    return None


def _numero_parametros(nombre: str) -> int:
    """Calcula el número de parámetros libres sin contar una ubicación fija."""
    if nombre in {"Lognormal", "Gamma", "Weibull"}:
        return 2
    if nombre == "GEV":
        return 3
    return 2


def ajustar(datos: Any, nombre: str) -> tuple[tuple[float, ...], int]:
    """
    Ajusta una distribución por máxima verosimilitud con scipy.stats.fit.

    Los parámetros tienen la forma de scipy: (forma o formas, loc, scale).
    Para Lognormal, Gamma y Weibull se fija ``loc=0``; los demás parámetros
    se estiman libremente. El entero devuelto es k, el número de parámetros libres.
    """
    if nombre not in CANDIDATAS:
        raise ValueError(f"Distribución desconocida: {nombre}")

    valores = _datos_validos(datos)
    if valores.size == 0:
        raise ValueError("No hay datos numéricos válidos para ajustar la distribución.")

    distribucion = CANDIDATAS[nombre]
    if nombre in {"Lognormal", "Gamma", "Weibull"}:
        params = tuple(float(x) for x in distribucion.fit(valores, floc=0.0))
    else:
        params = tuple(float(x) for x in distribucion.fit(valores))
    return params, _numero_parametros(nombre)


def log_verosimilitud(datos: Any, nombre: str, params: tuple[float, ...]) -> float:
    """
    Calcula la log-verosimilitud.

    Se aplica el logaritmo de la función de densidad a cada observación y se
    suma: ℓ = Σ log f(xᵢ | parámetros). Los faltantes ya fueron eliminados.
    """
    if nombre not in CANDIDATAS:
        raise ValueError(f"Distribución desconocida: {nombre}")
    valores = _datos_validos(datos)
    log_densidades = CANDIDATAS[nombre].logpdf(valores, *params)
    return float(np.sum(log_densidades[np.isfinite(log_densidades)]))


def criterios_informacion(
    datos: Any,
    nombre: str,
    params: tuple[float, ...],
) -> dict[str, float]:
    """
    Calcula AIC, BIC y AIC corregido.

    Si k es el número de parámetros libres, n el tamaño de muestra y ℓ la
    log-verosimilitud: AIC=2k-2ℓ, BIC=k·ln(n)-2ℓ y
    AICc=AIC+2k(k+1)/(n-k-1). El denominador necesita n-k-1 mayor que cero.
    """
    valores = _datos_validos(datos)
    n = len(valores)
    k = _numero_parametros(nombre)
    ell = log_verosimilitud(valores, nombre, params)
    aic = 2.0 * k - 2.0 * ell
    bic = k * math.log(n) - 2.0 * ell if n > 0 else float("nan")
    aicc = (
        aic + (2.0 * k * (k + 1.0) / (n - k - 1.0))
        if n - k - 1.0 > 0
        else float("nan")
    )
    return {"k": float(k), "log_verosimilitud": ell, "AIC": aic, "BIC": bic, "AICc": aicc}


def bondad_ajuste(
    datos: Any,
    nombre: str,
    n_mc: int,
) -> dict[str, float]:
    """
    Calcula pruebas KS y Anderson-Darling, con Monte Carlo para corregir Lilliefors.

    ``goodness_of_fit`` simula muestras bajo la distribución ajustada, vuelve a
    ajustar cada muestra y compara estadísticos. Se añaden KS y AD ingenuos para
    comparación: el valor p ingenuo no corrige por estimación de parámetros.
    """
    if nombre not in CANDIDATAS:
        raise ValueError(f"Distribución desconocida: {nombre}")
    valores = _datos_validos(datos)
    distribucion = CANDIDATAS[nombre]
    params, _ = ajustar(valores, nombre)
    conocidos = _parametros_conocidos(nombre)

    # Monte Carlo para KS: la hipótesis nula no usa un ajuste de parámetros fijados a mano.
    ks_mc = stats.goodness_of_fit(
        distribucion,
        valores,
        known_params=conocidos,
        statistic="ks",
        n_mc_samples=n_mc,
    )
    # Monte Carlo para Anderson-Darling.
    ad_mc = stats.goodness_of_fit(
        distribucion,
        valores,
        known_params=conocidos,
        statistic="ad",
        n_mc_samples=n_mc,
    )

    # La prueba ingenua usa directamente el ajuste al conjunto observado.
    ks_ingenuo = stats.kstest(valores, distribucion.cdf, args=params)

    return {
        "KS_estadistico_MC": float(ks_mc.statistic),
        "KS_p_MC": float(ks_mc.pvalue),
        "AD_estadistico_MC": float(ad_mc.statistic),
        "AD_p_MC": float(ad_mc.pvalue),
        "KS_estadistico_ingenuo": float(ks_ingenuo.statistic),
        "KS_p_ingenuo": float(ks_ingenuo.pvalue),
    }


def _interpretacion_delta_aic(delta: float) -> str:
    """Interpreta la diferencia de AIC respecto al mejor modelo."""
    if delta < 2.0:
        return "soporte sustancial"
    if delta <= 7.0:
        return "menos soporte"
    return "sin soporte"


def tabla_comparativa(datos: Any, n_mc: int = 199) -> pd.DataFrame:
    """Compara todas las candidatas y ordena conceptualmente por el AIC mínimo."""
    filas: list[dict[str, Any]] = []
    for nombre in CANDIDATAS:
        try:
            params, k = ajustar(datos, nombre)
            criterios = criterios_informacion(datos, nombre, params)
            bondad = bondad_ajuste(datos, nombre, n_mc)
            filas.append({
                "modelo": nombre,
                "parametros": ", ".join(f"{valor:.6f}" for valor in params),
                "k": k,
                **criterios,
                **bondad,
            })
        except (ValueError, RuntimeError, FloatingPointError):
            filas.append({
                "modelo": nombre,
                "parametros": "ajuste fallido",
                "k": np.nan,
                "log_verosimilitud": np.nan,
                "AIC": np.nan,
                "BIC": np.nan,
                "AICc": np.nan,
            })

    tabla = pd.DataFrame(filas)
    tabla_validas = tabla.dropna(subset=["AIC"]).copy()
    if not tabla_validas.empty:
        aic_minimo = tabla_validas["AIC"].min()
        tabla_validas["delta_AIC"] = tabla_validas["AIC"] - aic_minimo
        tabla_validas["interpretacion_delta_AIC"] = tabla_validas["delta_AIC"].map(
            _interpretacion_delta_aic
        )
        tabla_validas["rechaza_H0_5_pct"] = (
            tabla_validas["KS_p_MC"] < 0.05
        ) | (tabla_validas["AD_p_MC"] < 0.05)
        # Las filas fallidas se mantienen al final si existieran.
        fallidas = tabla[tabla["AIC"].isna()].copy()
        tabla = pd.concat([tabla_validas, fallidas], ignore_index=True)

    return tabla.sort_values("AIC", na_position="last").reset_index(drop=True)


def posiciones_graficas(datos: Any) -> pd.DataFrame:
    """
    Construye posiciones empíricas para comparar datos con una distribución.

    Con datos crecientes x_(i), p_W=i/(n+1) usa Weibull y
    p_G=(i-0.44)/(n+0.12) usa Gringorten. El período empírico es T=1/(1-p).
    """
    valores = np.sort(_datos_validos(datos))
    n = len(valores)
    if n == 0:
        return pd.DataFrame(
            {"dato": [], "puesto": [], "p_weibull": [], "p_gringorten": [], "T_weibull": [], "T_gringorten": []}
        )

    i = np.arange(1, n + 1, dtype=float)
    p_weibull = i / (n + 1.0)
    p_gringorten = (i - 0.44) / (n + 0.12)
    return pd.DataFrame({
        "dato": valores,
        "puesto": i.astype(int),
        "p_weibull": p_weibull,
        "p_gringorten": p_gringorten,
        "T_weibull": 1.0 / (1.0 - p_weibull),
        "T_gringorten": 1.0 / (1.0 - p_gringorten),
    })


def cuantil_retorno(nombre: str, params: tuple[float, ...], T: float) -> float:
    """
    Calcula el cuantíl x_T correspondiente al período de retorno T.

    Como F(x_T)=1-1/T, se usa la función inversa ppf:
    x_T=F⁻¹(1-1/T). Períodos usuales: 2, 5, 10, 25, 50 y 100 años.
    """
    if nombre not in CANDIDATAS:
        raise ValueError(f"Distribución desconocida: {nombre}")
    if T <= 1:
        raise ValueError("El período de retorno T debe ser mayor que 1 año.")
    probabilidad_no_excedencia = 1.0 - 1.0 / T
    return float(CANDIDATAS[nombre].ppf(probabilidad_no_excedencia, *params))


def riesgo_falla(T: float, N: int) -> float:
    """
    Calcula el riesgo de al menos una falla en N años.

    Para un período T se conoce la probabilidad anual 1/T. No falla en un año
    es 1-1/T; durante N años es (1-1/T)^N. Por complemento, R=1-(1-1/T)^N.
    """
    if T <= 1:
        raise ValueError("El período de retorno T debe ser mayor que 1 año.")
    if N < 0:
        raise ValueError("El número de años N no puede ser negativo.")
    return float(1.0 - (1.0 - 1.0 / T) ** N)


def bootstrap_cuantil(
    datos: Any,
    nombre: str,
    T: float,
    B: int = 500,
    semilla: int = None,
) -> tuple[float, float]:
    """
    Estima por bootstrap paramétrico el intervalo de confianza del 95 % de x_T.

    Se ajusta el modelo original, se generan B muestras de ese modelo ajustado,
    se vuelve a ajustar cada muestra y se calcula su cuantíl. Los extremos son
    los percentiles 2.5 y 97.5 % de los B cuantiles bootstrap.
    """
    if B < 1:
        raise ValueError("B debe ser al menos 1.")
    valores = _datos_validos(datos)
    params, _ = ajustar(valores, nombre)
    distribucion = CANDIDATAS[nombre]
    generador = np.random.default_rng(semilla)
    cuantiles = []

    for _ in range(B):
        muestra = distribucion.rvs(*params, size=len(valores), random_state=generador)
        try:
            params_boot, _ = ajustar(muestra, nombre)
            cuantiles.append(cuantil_retorno(nombre, params_boot, T))
        except (ValueError, RuntimeError, FloatingPointError):
            continue

    if not cuantiles:
        raise RuntimeError("El bootstrap no produjo ajustes válidos.")
    limite_inferior, limite_superior = np.percentile(cuantiles, [2.5, 97.5])
    return float(limite_inferior), float(limite_superior)


def gumbel_momentos(datos: Any) -> dict[str, float]:
    """
    Estima los parámetros Gumbel por el método de momentos usado en clase.

    Se calcula β=s·√6/π y μ=media-0.5772·β, donde s es la desviación estándar
    muestral. Estas estimaciones permiten construir scipy.stats.gumbel_r
    mediante loc=mu y scale=beta.
    """
    valores = _datos_validos(datos)
    if len(valores) < 2:
        raise ValueError("Se necesitan al menos dos datos para calcular momentos.")
    beta = float(np.std(valores, ddof=1) * math.sqrt(6.0) / math.pi)
    mu = float(np.mean(valores) - 0.5772 * beta)
    return {"mu": mu, "beta": beta}


if __name__ == "__main__":
    ruta_datos = "datos/precip_max_anual.csv"
    precip = pd.read_csv(ruta_datos)["pmax24h_mm"]
    tabla = tabla_comparativa(precip, n_mc=199)
    print(tabla.to_string(index=False))
