"""Página funcional de correlación y regresión lineal."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
import seaborn as sns
import streamlit as st

from src.datos import cargar_csv, tarjeta_estudiante
from src.regresion import (
    ajustar_multiple,
    ajustar_rls,
    calculo_manual,
    diagnostico_residuos,
    matriz_correlacion,
    predecir,
)


UNIDADES_X = {
    "dosis_N": "kg/ha",
    "lamina_riego": "mm",
    "materia_organica": "%",
    "ph": "adimensional",
}

NOMBRES_X = {
    "dosis_N": "Dosis de N",
    "lamina_riego": "Lámina de riego",
    "materia_organica": "Materia orgánica",
    "ph": "pH",
}


def mostrar_grafico(figura: plt.Figure) -> None:
    """Muestra una figura de Matplotlib y libera su memoria."""
    st.pyplot(figura, use_container_width=True)
    plt.close(figura)


st.set_page_config(page_title="Regresión", layout="wide")
tarjeta_estudiante()
st.title("Correlación y regresión lineal")

parcelas = cargar_csv("parcelas.csv")
variables_numericas = [
    columna
    for columna in parcelas.columns
    if pd.api.types.is_numeric_dtype(parcelas[columna])
]
variables_x = [columna for columna in variables_numericas if columna != "rendimiento"]

# 1. Correlación
st.header("1. Correlación")
metodo = st.radio(
    "Método de correlación",
    options=["pearson", "spearman"],
    format_func=lambda valor: "Pearson" if valor == "pearson" else "Spearman",
    horizontal=True,
)
matriz = matriz_correlacion(parcelas, metodo)

fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(
    matriz,
    annot=True,
    fmt=".2f",
    cmap="vlag",
    center=0,
    vmin=-1,
    vmax=1,
    ax=ax,
)
ax.set_title(f"Matriz de correlación de {metodo.capitalize()}")
mostrar_grafico(fig)

st.subheader("Correlación con rendimiento")
if "rendimiento" in matriz.columns:
    tabla_correlacion = (
        matriz["rendimiento"]
        .drop(labels=["rendimiento"])
        .rename("correlación")
        .reset_index()
        .rename(columns={"index": "variable"})
    )
    tabla_correlacion["|correlación|"] = tabla_correlacion["correlación"].abs()
    tabla_correlacion = tabla_correlacion.sort_values(
        "|correlación|",
        ascending=False,
    ).reset_index(drop=True)
    st.dataframe(
        tabla_correlacion.style.format({
            "correlación": "{:.4f}",
            "|correlación|": "{:.4f}",
        }),
        use_container_width=True,
        hide_index=True,
    )
st.warning(
    "Correlación no implica causalidad: una asociación puede surgir por azar, "
    "por variables confusoras o por relaciones indirectas."
)

# 2. Regresión lineal simple
st.header("2. Regresión lineal simple")
x_seleccionada = st.selectbox(
    "Variable independiente X",
    variables_x,
    index=variables_x.index("lamina_riego") if "lamina_riego" in variables_x else 0,
    format_func=lambda columna: (
        f"{NOMBRES_X.get(columna, columna)} ({UNIDADES_X.get(columna, '')})"
    ),
)
datos_rls = parcelas[[x_seleccionada, "rendimiento"]].dropna()
modelo_rls = ajustar_rls(datos_rls, x_seleccionada, "rendimiento")
b0 = float(modelo_rls.params["Intercept"])
b1 = float(modelo_rls.params[x_seleccionada])
r = float(datos_rls[x_seleccionada].corr(datos_rls["rendimiento"], method="pearson"))

nombre_x = NOMBRES_X.get(x_seleccionada, x_seleccionada)
unidad_x = UNIDADES_X.get(x_seleccionada, "")

fig, ax = plt.subplots(figsize=(8, 5))
sns.scatterplot(
    data=datos_rls,
    x=x_seleccionada,
    y="rendimiento",
    ax=ax,
    color="#457b9d",
    s=45,
)
grid_x = np.linspace(datos_rls[x_seleccionada].min(), datos_rls[x_seleccionada].max(), 300)
ax.plot(grid_x, b0 + b1 * grid_x, color="#d62828", linewidth=2, label="Recta ajustada")
ax.set_xlabel(f"{nombre_x} ({unidad_x})" if unidad_x else nombre_x)
ax.set_ylabel("Rendimiento (t/ha)")
ax.set_title(f"Rendimiento en función de {nombre_x.lower()}")
ax.legend()
mostrar_grafico(fig)

st.subheader("Ecuación ajustada")
st.latex(
    rf"\hat{{rendimiento}} = {b0:.4f} + {b1:.6f}"
    rf"\,({nombre_x}) \quad [t/ha]"
)
st.caption(
    f"Pendiente expresada por cada unidad de {nombre_x.lower()} "
    f"({unidad_x if unidad_x else 'unidad original'})."
)

metricas_col1, metricas_col2, metricas_col3 = st.columns(3)
rse = float(np.sqrt(modelo_rls.ssr / modelo_rls.df_resid))
with metricas_col1:
    st.metric("r de Pearson", f"{r:.4f}")
with metricas_col2:
    st.metric("R²", f"{modelo_rls.rsquared:.4f}")
with metricas_col3:
    st.metric("RSE (t/ha)", f"{rse:.4f}")

tabla_coeficientes = pd.DataFrame({
    "coeficiente": modelo_rls.params.index,
    "estimación": modelo_rls.params.values,
    "error_estandar": modelo_rls.bse.values,
    "t": modelo_rls.tvalues.values,
    "p_valor": modelo_rls.pvalues.values,
    "IC95_inferior": modelo_rls.conf_int().iloc[:, 0].values,
    "IC95_superior": modelo_rls.conf_int().iloc[:, 1].values,
})
st.dataframe(
    tabla_coeficientes.style.format({
        "estimación": "{:.6f}",
        "error_estandar": "{:.6f}",
        "t": "{:.4f}",
        "p_valor": "{:.4f}",
        "IC95_inferior": "{:.6f}",
        "IC95_superior": "{:.6f}",
    }),
    use_container_width=True,
    hide_index=True,
)

p_pendiente = float(modelo_rls.pvalues[x_seleccionada])
if p_pendiente < 0.05:
    decision = (
        "Se rechaza H0: β1 = 0 al 5 %. Existe evidencia estadística de una asociación "
        "lineal entre X y el rendimiento."
    )
else:
    decision = (
        "No se rechaza H0: β1 = 0 al 5 %. No hay evidencia estadística suficiente "
        "de una asociación lineal entre X y el rendimiento."
    )
st.info(decision)
st.info(
    (
        f"Interpretación de b1: por cada 100 mm de lámina de riego, "
        f"el rendimiento cambia en promedio {100 * b1:.4f} t/ha."
        if x_seleccionada == "lamina_riego"
        else (
            f"Interpretación de b1: por cada 100 unidades de {nombre_x.lower()}, "
            f"el rendimiento cambia en promedio {100 * b1:.4f} t/ha."
        )
    ) + " Se mantiene constante la interpretación dentro de este modelo simple."
)

# 3. Diagnóstico de residuos
st.header("3. Diagnóstico de residuos")
diagnostico = diagnostico_residuos(modelo_rls)
residuos = diagnostico["residuos"]
ajustados = diagnostico["ajustados"]

col_residuos, col_histograma = st.columns(2)
with col_residuos:
    fig, ax = plt.subplots()
    ax.scatter(ajustados, residuos, color="#457b9d")
    ax.axhline(0, color="#d62828", linestyle="--")
    ax.set_xlabel("Valores ajustados (t/ha)")
    ax.set_ylabel("Residuo (t/ha)")
    ax.set_title("Residuos vs. ajustados")
    mostrar_grafico(fig)
with col_histograma:
    fig, ax = plt.subplots()
    sns.histplot(residuos, kde=True, ax=ax, color="#2a9d8f")
    ax.set_xlabel("Residuo (t/ha)")
    ax.set_ylabel("Frecuencia")
    ax.set_title("Histograma de residuos")
    mostrar_grafico(fig)

fig, ax = plt.subplots()
stats.probplot(residuos, dist="norm", plot=ax)
ax.set_xlabel("Cuantil teórico normal")
ax.set_ylabel("Cuantil de residuos")
ax.set_title("Gráfico Q-Q de residuos")
mostrar_grafico(fig)

p_shapiro = diagnostico["shapiro_p_valor"]
p_bp = diagnostico["breusch_pagan_p_valor"]
col_test1, col_test2 = st.columns(2)
with col_test1:
    st.metric("Shapiro-Wilk estadístico", f"{diagnostico['shapiro_estadistico']:.4f}")
    st.write(f"valor p = {p_shapiro:.4f}")
    st.info(
        "Los residuos parecen aproximadamente normales."
        if p_shapiro >= 0.05
        else "Existe evidencia de desviación de la normalidad de los residuos."
    )
with col_test2:
    st.metric("Breusch-Pagan estadístico", f"{diagnostico['breusch_pagan_estadistico']:.4f}")
    st.write(f"valor p = {p_bp:.4f}")
    st.info(
        "No hay evidencia de heterocedasticidad."
        if p_bp >= 0.05
        else "Existe evidencia de heterocedasticidad."
    )

# 4. Predicción
st.header("4. Predicción")
rango_min = float(datos_rls[x_seleccionada].min())
rango_max = float(datos_rls[x_seleccionada].max())
valor_slider = st.slider(
    f"Valor de {nombre_x}",
    min_value=float(rango_min),
    max_value=float(rango_max),
    value=float((rango_min + rango_max) / 2),
)
resultado_slider = predecir(modelo_rls, valor_slider)
col_pred1, col_pred2, col_pred3 = st.columns(3)
with col_pred1:
    st.metric("Predicción (t/ha)", f"{resultado_slider['prediccion']:.4f}")
with col_pred2:
    st.metric(
        "IC 95 % media",
        f"{resultado_slider['IC95_inferior']:.4f} a {resultado_slider['IC95_superior']:.4f}",
    )
with col_pred3:
    st.metric(
        "IP 95 % nueva parcela",
        f"{resultado_slider['IP95_inferior']:.4f} a {resultado_slider['IP95_superior']:.4f}",
    )

valor_libre = st.number_input(
    f"Valor libre de {nombre_x}",
    value=float((rango_min + rango_max) / 2),
)
resultado_libre = predecir(modelo_rls, float(valor_libre))
if valor_libre < rango_min or valor_libre > rango_max:
    st.warning(
        f"EXTRAPOLACIÓN: {valor_libre:.4f} {unidad_x} está fuera del rango observado "
        f"[{rango_min:.4f}, {rango_max:.4f}] {unidad_x}."
    )
else:
    st.success("El valor está dentro del rango observado.")
st.write(
    f"Predicción: {resultado_libre['prediccion']:.4f} t/ha; "
    f"IC 95 %: {resultado_libre['IC95_inferior']:.4f} a {resultado_libre['IC95_superior']:.4f} t/ha; "
    f"IP 95 %: {resultado_libre['IP95_inferior']:.4f} a {resultado_libre['IP95_superior']:.4f} t/ha."
)

# 5. Regresión múltiple
st.header("5. Regresión múltiple (vista previa)")
variables_multiples = [
    "dosis_N",
    "lamina_riego",
    "materia_organica",
    "ph",
]
modelo_multiple = ajustar_multiple(parcelas, "rendimiento", variables_multiples)

tabla_multiple = pd.DataFrame({
    "coeficiente": modelo_multiple.params.index,
    "estimación": modelo_multiple.params.values,
    "error_estándar": modelo_multiple.bse.values,
    "p_valor": modelo_multiple.pvalues.values,
})
st.dataframe(
    tabla_multiple.style.format({
        "estimación": "{:.6f}",
        "error_estándar": "{:.6f}",
        "p_valor": "{:.4f}",
    }),
    use_container_width=True,
    hide_index=True,
)
metrica_m1, metrica_m2 = st.columns(2)
with metrica_m1:
    st.metric("R²", f"{modelo_multiple.rsquared:.4f}")
with metrica_m2:
    st.metric("R² ajustado", f"{modelo_multiple.rsquared_adj:.4f}")

# 6. Verificación con 8 parcelas
st.header("6. Verificación del cálculo a mano (8 parcelas)")
muestra = cargar_csv("muestra_reg8.csv")
x_muestra = muestra["lamina_riego"].to_numpy(dtype=float)
y_muestra = muestra["rendimiento"].to_numpy(dtype=float)
manual = calculo_manual(x_muestra, y_muestra)

st.subheader("Tabla de desviaciones, productos cruzados y rangos")
media_x_muestra = manual["media_x"]
media_y_muestra = manual["media_y"]
tabla_mano = pd.DataFrame({
    "parcela": muestra["parcela"],
    "lamina_riego_mm": x_muestra,
    "rendimiento_t_ha": y_muestra,
    "x_x_media": x_muestra - media_x_muestra,
    "y_y_media": y_muestra - media_y_muestra,
    "producto_cruzado": (x_muestra - media_x_muestra) * (y_muestra - media_y_muestra),
    "cuadrado_x": (x_muestra - media_x_muestra) ** 2,
    "cuadrado_y": (y_muestra - media_y_muestra) ** 2,
    "rango_x": pd.Series(x_muestra).rank(method="average"),
    "rango_y": pd.Series(y_muestra).rank(method="average"),
    "ajustado_t_ha": manual["ajustados"],
    "residuo_t_ha": manual["residuos"],
})
st.dataframe(
    tabla_mano.style.format({
        columna: "{:.4f}"
        for columna in tabla_mano.columns
        if columna != "parcela"
    }),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Resultados de cálculo_manual")
orden_resultados = [
    "n", "media_x", "media_y", "Sxx", "Syy", "Sxy", "r", "rho_spearman",
    "b1", "b0", "SCE", "SCR", "SCT", "R2", "RSE", "SE_b1", "t",
    "t_critico", "p_valor", "IC95_b1_inferior", "IC95_b1_superior",
]
filas_resultados = []
for clave in orden_resultados:
    filas_resultados.append({
        "resultado": clave,
        "valor": manual[clave],
    })
tabla_resultados = pd.DataFrame(filas_resultados)
tabla_resultados["valor"] = tabla_resultados["valor"].map(
    lambda valor: np.nan if isinstance(valor, (list, np.ndarray)) else valor
)
tabla_resultados["valor_mostrado"] = tabla_resultados.apply(
    lambda fila: (
        f"{fila['valor']:.6f}" if fila["resultado"] == "b1"
        else (f"{fila['valor']:.4f}" if pd.notna(fila["valor"]) else "—")
    ),
    axis=1,
)
st.dataframe(
    tabla_resultados[["resultado", "valor_mostrado"]].rename(
        columns={"valor_mostrado": "valor"}
    ),
    use_container_width=True,
    hide_index=True,
)

fig, ax = plt.subplots(figsize=(8, 5))
ax.scatter(x_muestra, y_muestra, color="#457b9d", s=45, label="8 parcelas")
grid_x_muestra = np.linspace(x_muestra.min(), x_muestra.max(), 300)
ax.plot(
    grid_x_muestra,
    manual["b0"] + manual["b1"] * grid_x_muestra,
    color="#d62828",
    linewidth=2,
    label="Recta ajustada",
)
ax.set_xlabel("Lámina de riego (mm)")
ax.set_ylabel("Rendimiento (t/ha)")
ax.set_title("Recta ajustada con las 8 parcelas de muestra")
ax.legend()
mostrar_grafico(fig)

st.subheader("Comparación: 8 parcelas frente a todas las parcelas")
manual_todas = calculo_manual(
    parcelas["lamina_riego"],
    parcelas["rendimiento"],
)
tabla_comparacion = pd.DataFrame({
    "medida": ["b1", "r", "R²", "t", "p_valor"],
    "8_parcelas": [
        manual["b1"],
        manual["r"],
        manual["R2"],
        manual["t"],
        manual["p_valor"],
    ],
    "todas_las_parcelas": [
        manual_todas["b1"],
        manual_todas["r"],
        manual_todas["R2"],
        manual_todas["t"],
        manual_todas["p_valor"],
    ],
})
tabla_comparacion["8_parcelas"] = tabla_comparacion.apply(
    lambda fila: (
        f"{fila['8_parcelas']:.6f}" if fila["medida"] == "b1"
        else f"{fila['8_parcelas']:.4f}"
    ),
    axis=1,
)
tabla_comparacion["todas_las_parcelas"] = tabla_comparacion.apply(
    lambda fila: (
        f"{fila['todas_las_parcelas']:.6f}" if fila["medida"] == "b1"
        else f"{fila['todas_las_parcelas']:.4f}"
    ),
    axis=1,
)
st.dataframe(
    tabla_comparacion,
    use_container_width=True,
    hide_index=True,
)
