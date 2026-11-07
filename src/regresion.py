"""Funciones de correlación y regresión lineal para datos agrícolas."""

from pathlib import Path
from typing import Any, Iterable
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.diagnostic import het_breuschpagan


def matriz_correlacion(
    df: pd.DataFrame,
    metodo: str = "pearson",
) -> pd.DataFrame:
    """
    Calcula una matriz de correlación para las variables numéricas.

    ``metodo`` puede ser ``"pearson"`` para relaciones lineales o
    ``"spearman"`` para una asociación monótona basada en rangos.
    """
    metodo_normalizado = metodo.lower()
    if metodo_normalizado not in {"pearson", "spearman"}:
        raise ValueError("El método debe ser 'pearson' o 'spearman'.")
    variables_numericas = df.select_dtypes(include=[np.number])
    return variables_numericas.corr(method=metodo_normalizado)


def calculo_manual(x: Iterable[float], y: Iterable[float]) -> dict[str, Any]:
    """
    Calcula una regresión lineal simple usando las fórmulas analíticas de clase.

    Con x̄ y ȳ como medias, se define Sxx=Σ(x-x̄)², Syy=Σ(y-ȳ)² y
    Sxy=Σ(x-x̄)(y-ȳ). Entonces b1=Sxy/Sxx y b0=ȳ-b1·x̄. Los errores
    estándar, pruebas y intervalos se basan en distribución t con n-2 gl.
    """
    x_arr = np.asarray(list(x), dtype=float)
    y_arr = np.asarray(list(y), dtype=float)
    mascara = np.isfinite(x_arr) & np.isfinite(y_arr)
    x_arr = x_arr[mascara]
    y_arr = y_arr[mascara]

    n = int(len(x_arr))
    if n < 3:
        raise ValueError("Se necesitan al menos tres observaciones válidas.")

    x_media = float(np.mean(x_arr))
    y_media = float(np.mean(y_arr))
    dx = x_arr - x_media
    dy = y_arr - y_media

    Sxx = float(np.sum(dx ** 2))
    Syy = float(np.sum(dy ** 2))
    Sxy = float(np.sum(dx * dy))
    if Sxx == 0:
        raise ValueError("Sxx debe ser mayor que cero para ajustar una pendiente.")

    b1 = float(Sxy / Sxx)
    b0 = float(y_media - b1 * x_media)
    ajustados = b0 + b1 * x_arr
    residuos = y_arr - ajustados

    SCE = float(np.sum(residuos ** 2))
    SCR = float(np.sum((ajustados - y_media) ** 2))
    SCT = float(np.sum(dy ** 2))
    R2 = float(1.0 - SCE / SCT) if SCT > 0 else float("nan")
    RSE = float(np.sqrt(SCE / (n - 2)))
    SE_b1 = float(RSE / np.sqrt(Sxx))
    t_estadistico = float(b1 / SE_b1) if SE_b1 > 0 else float("nan")
    t_critico = float(stats.t.ppf(0.975, df=n - 2))
    p_valor = (
        float(2.0 * stats.t.sf(abs(t_estadistico), df=n - 2))
        if np.isfinite(t_estadistico)
        else float("nan")
    )
    margen_ic = t_critico * SE_b1

    rho = float(stats.spearmanr(x_arr, y_arr).statistic)
    r = float(np.corrcoef(x_arr, y_arr)[0, 1])

    return {
        "n": n,
        "media_x": x_media,
        "media_y": y_media,
        "Sxx": Sxx,
        "Syy": Syy,
        "Sxy": Sxy,
        "r": r,
        "rho_spearman": rho,
        "b1": b1,
        "b0": b0,
        "ajustados": ajustados,
        "residuos": residuos,
        "SCE": SCE,
        "SCR": SCR,
        "SCT": SCT,
        "R2": R2,
        "RSE": RSE,
        "SE_b1": SE_b1,
        "t": t_estadistico,
        "t_critico": t_critico,
        "p_valor": p_valor,
        "IC95_b1_inferior": float(b1 - margen_ic),
        "IC95_b1_superior": float(b1 + margen_ic),
    }


def ajustar_rls(df: pd.DataFrame, x: str, y: str):
    """
    Ajusta y = b0 + b1·x mediante statsmodels fórmula OLS.

    Se eliminan automáticamente las observaciones que tengan faltantes en
    cualquiera de las dos columnas seleccionadas.
    """
    datos = df[[x, y]].dropna().copy()
    modelo = smf.ols(formula=f"{y} ~ {x}", data=datos).fit()
    return modelo


def predecir(modelo, x0: float | Iterable[float]) -> dict[str, Any]:
    """
    Predice nuevos valores con intervalos de confianza y de predicción al 95 %.

    El intervalo de confianza describe la incertidumbre de la media esperada.
    El intervalo de predicción es más amplio y describe una observación nueva.
    """
    variable_explicativa = modelo.model.exog_names[1]
    if np.isscalar(x0):
        nuevos = pd.DataFrame({variable_explicativa: [float(x0)]})
    else:
        nuevos = pd.DataFrame({
            variable_explicativa: np.asarray(x0, dtype=float),
        })
    predicciones = modelo.get_prediction(nuevos)
    resumen = predicciones.summary_frame(alpha=0.05)

    prediccion = resumen["mean"].to_numpy(dtype=float)
    ic_inferior = resumen["mean_ci_lower"].to_numpy(dtype=float)
    ic_superior = resumen["mean_ci_upper"].to_numpy(dtype=float)
    ip_inferior = resumen["obs_ci_lower"].to_numpy(dtype=float)
    ip_superior = resumen["obs_ci_upper"].to_numpy(dtype=float)

    if len(prediccion) == 1:
        return {
            "prediccion": float(prediccion[0]),
            "IC95_inferior": float(ic_inferior[0]),
            "IC95_superior": float(ic_superior[0]),
            "IP95_inferior": float(ip_inferior[0]),
            "IP95_superior": float(ip_superior[0]),
        }
    return {
        "prediccion": prediccion,
        "IC95_inferior": ic_inferior,
        "IC95_superior": ic_superior,
        "IP95_inferior": ip_inferior,
        "IP95_superior": ip_superior,
    }


def diagnostico_residuos(modelo) -> dict[str, Any]:
    """
    Obtiene residuos y pruebas básicas de supuestos del modelo ajustado.

    Shapiro-Wilk evalúa normalidad de los residuos. Breusch-Pagan evalúa la
    homocedasticidad; su p-valor alto indica ausencia de evidencia contra varianza constante.
    """
    residuo = np.asarray(modelo.resid, dtype=float)
    ajustado = np.asarray(modelo.fittedvalues, dtype=float)
    prueba_shapiro = stats.shapiro(residuo)
    exog = modelo.model.exog
    _, p_bp, lm_bp, _ = het_breuschpagan(residuo, exog)

    return {
        "residuos": residuo,
        "ajustados": ajustado,
        "shapiro_estadistico": float(prueba_shapiro.statistic),
        "shapiro_p_valor": float(prueba_shapiro.pvalue),
        "breusch_pagan_estadistico": float(lm_bp),
        "breusch_pagan_p_valor": float(p_bp),
        "bp_estadistico": float(lm_bp),
        "bp_p_valor": float(p_bp),
    }


def ajustar_multiple(
    df: pd.DataFrame,
    y: str,
    lista_x: list[str],
):
    """
    Ajusta una regresión lineal múltiple con todas las variables elegidas.

    Primero elimina todas las filas con faltantes en y o en las explicativas;
    luego construye una fórmula OLS usando ``statsmodels.formula.api``.
    """
    if not lista_x:
        raise ValueError("Debe proporcionar al menos una variable explicativa.")
    columnas = [y] + list(lista_x)
    datos = df[columnas].dropna().copy()
    formula = f"{y} ~ " + " + ".join(lista_x)
    return smf.ols(formula=formula, data=datos).fit()


if __name__ == "__main__":
    ruta_raiz = Path(__file__).resolve().parent.parent
    muestra = pd.read_csv(ruta_raiz / "datos" / "muestra_reg8.csv")
    manual = calculo_manual(
        muestra["lamina_riego"],
        muestra["rendimiento"],
    )
    modelo = ajustar_rls(
        muestra,
        "lamina_riego",
        "rendimiento",
    )

    nombres = {
        "b0": "Intercepto",
        "b1": "Pendiente",
        "R2": "R²",
        "RSE": "RSE",
        "t": "t",
    }
    print("Comparación de cálculo manual y statsmodels")
    print("medida                manual          statsmodels")
    for clave, etiqueta in nombres.items():
        valor_manual = manual[clave]
        if clave == "b0":
            valor_modelo = modelo.params["Intercept"]
        elif clave == "b1":
            valor_modelo = modelo.params["lamina_riego"]
        elif clave == "R2":
            valor_modelo = modelo.rsquared
        elif clave == "RSE":
            valor_modelo = np.sqrt(modelo.ssr / modelo.df_resid)
        else:
            valor_modelo = modelo.tvalues["lamina_riego"]
        print(f"{etiqueta:20s} {valor_manual:14.8f} {valor_modelo:14.8f}")
