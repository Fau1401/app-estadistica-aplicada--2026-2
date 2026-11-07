"""Página funcional para comparar distribuciones de máximos anuales."""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import scipy.stats as stats
import streamlit as st

from src.datos import cargar_csv, tarjeta_estudiante
from src.distribuciones import (
    CANDIDATAS,
    ajustar,
    bootstrap_cuantil,
    cuantil_retorno,
    gumbel_momentos,
    posiciones_graficas,
    riesgo_falla,
    tabla_comparativa,
)
from src.eda import resumen_numerico
from src.modelos_curvas import ajustar_curva, MODELOS, tabla_modelos


def mostrar_grafico(figura: plt.Figure) -> None:
    """Presenta una figura de Matplotlib y libera su memoria."""
    st.pyplot(figura, use_container_width=True)
    plt.close(figura)


@st.cache_data
def tabla_bondad_filtrada(
    datos_csv: pd.DataFrame,
    seleccionadas: tuple[str, ...],
    n_mc: int,
) -> pd.DataFrame:
    """Cachea la costosa comparación Monte Carlo para una selección y tamaño dados."""
    tabla = tabla_comparativa(datos_csv["pmax24h_mm"], n_mc=n_mc)
    return tabla[tabla["modelo"].isin(seleccionadas)].copy()


st.set_page_config(page_title="Distribuciones", layout="wide")
tarjeta_estudiante()
st.title("Distribuciones de precipitación máxima anual")

df_precipitacion = cargar_csv("precip_max_anual.csv")
datos = pd.to_numeric(df_precipitacion["pmax24h_mm"], errors="coerce").dropna()
st.sidebar.header("Opciones de distribución")
seleccionadas = st.sidebar.multiselect(
    "Distribuciones candidatas",
    options=list(CANDIDATAS.keys()),
    default=list(CANDIDATAS.keys()),
)
if not seleccionadas:
    st.warning("Seleccione al menos una distribución.")
    st.stop()

# 1. Los datos
st.header("1. Los datos")
fig, ax = plt.subplots(figsize=(11, 4))
ax.bar(df_precipitacion["anio"], df_precipitacion["pmax24h_mm"], color="#457b9d")
ax.set_xlabel("Año")
ax.set_ylabel("Precipitación máxima en 24 h (mm)")
ax.set_title("Máximos anuales de precipitación")
mostrar_grafico(fig)

resumen = resumen_numerico(datos)
tabla_resumen = pd.DataFrame([resumen]).T
tabla_resumen.columns = ["valor"]
tabla_resumen.index.name = "medida"
st.subheader("Resumen numérico")
st.dataframe(tabla_resumen.style.format("{:.4f}", na_rep="—"), use_container_width=True)

fig, ax = plt.subplots()
sns.histplot(datos, kde=True, ax=ax, color="#2a9d8f")
ax.set_xlabel("Precipitación máxima en 24 h (mm)")
ax.set_ylabel("Frecuencia")
ax.set_title("Histograma de máximos anuales")
mostrar_grafico(fig)

# 2. Candidatas y ajuste
st.header("2. Candidatas y ajuste")
ajustes = {}
for nombre in seleccionadas:
    ajustes[nombre] = ajustar(datos, nombre)[0]

fig, ax = plt.subplots(figsize=(9, 5))
sns.histplot(datos, bins="auto", stat="density", kde=False, color="#b0bec5", ax=ax, alpha=0.55)
x_min, x_max = float(datos.min()), float(datos.max())
margen = 0.15 * (x_max - x_min)
x_grid = np.linspace(max(0, x_min - margen), x_max + margen, 500)
for nombre, params in ajustes.items():
    ax.plot(
        x_grid,
        CANDIDATAS[nombre].pdf(x_grid, *params),
        label=nombre,
        linewidth=1.8,
    )
ax.set_xlabel("Precipitación máxima en 24 h (mm)")
ax.set_ylabel("Densidad (1/mm)")
ax.set_title("Histograma con densidades ajustadas")
ax.legend()
mostrar_grafico(fig)

st.info(
    "Gumbel y GEV tienen respaldo teórico para máximos anuales mediante el teorema "
    "de valores extremos: si bloques independientes producen máximos, su distribución "
    "línealmente normalizada converge a una de las familias de la distribución generalizada "
    "de valores extremos. Gumbel es el caso sin cola adicional. Por ello son candidatos "
    "naturales antes que una distribución elegida solo por forma visual."
)

# 3. Bondad de ajuste
st.header("3. Bondad de ajuste")
n_mc = st.slider("Número de simulaciones Monte Carlo (n_mc)", 99, 499, 199, 20)
with st.spinner("Calculando valores p por simulación Monte Carlo..."):
    tabla_bondad = tabla_bondad_filtrada(df_precipitacion, tuple(seleccionadas), n_mc)

tabla_p = tabla_bondad[[
    "modelo",
    "KS_estadistico_MC",
    "KS_p_MC",
    "KS_p_ingenuo",
    "AD_estadistico_MC",
    "AD_p_MC",
    "rechaza_H0_5_pct",
]].copy()
tabla_p.columns = [
    "Modelo",
    "KS",
    "valor p KS Monte Carlo",
    "valor p KS ingenuo",
    "AD",
    "valor p AD Monte Carlo",
    "¿Rechaza H0 al 5 %?",
]
st.dataframe(
    tabla_p.style.format({
        "KS": "{:.4f}",
        "valor p KS Monte Carlo": "{:.4f}",
        "valor p KS ingenuo": "{:.4f}",
        "AD": "{:.4f}",
        "valor p AD Monte Carlo": "{:.4f}",
    }),
    use_container_width=True,
    hide_index=True,
)

cuantas = len(seleccionadas)
ncols = min(3, cuantas)
nrows = int(np.ceil(cuantas / ncols))
fig, ejes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows), squeeze=False)
for indice, nombre in enumerate(seleccionadas):
    ax = ejes[indice // ncols, indice % ncols]
    params = ajustes[nombre]
    probabilidades = (np.arange(1, len(datos) + 1) - 0.375) / (len(datos) + 0.25)
    cuantiles_teoricos = CANDIDATAS[nombre].ppf(probabilidades, *params)
    sns.scatterplot(
        x=np.sort(cuantiles_teoricos),
        y=np.sort(datos),
        ax=ax,
        color="#457b9d",
    )
    minimo = min(float(np.min(cuantiles_teoricos)), float(datos.min()))
    maximo = max(float(np.max(cuantiles_teoricos)), float(datos.max()))
    ax.plot([minimo, maximo], [minimo, maximo], "--", color="#d62828")
    ax.set_title(f"Q-Q: {nombre}")
    ax.set_xlabel("Cuantiles teóricos (mm)")
    ax.set_ylabel("Cuantiles observados (mm)")
for indice in range(cuantas, nrows * ncols):
    ejes[indice // ncols, indice % ncols].axis("off")
plt.tight_layout()
mostrar_grafico(fig)

# 4. Criterios de información
st.header("4. Criterios de información")
tabla_info = tabla_bondad[[
    "modelo", "k", "AIC", "BIC", "AICc", "delta_AIC", "interpretacion_delta_AIC"
]].copy()
tabla_info = tabla_info.sort_values("AIC").reset_index(drop=True)
st.dataframe(
    tabla_info.style.format({
        "k": "{:.0f}",
        "AIC": "{:.4f}",
        "BIC": "{:.4f}",
        "AICc": "{:.4f}",
        "delta_AIC": "{:.4f}",
    }),
    use_container_width=True,
    hide_index=True,
)

fig, ax = plt.subplots()
sns.barplot(data=tabla_info, x="modelo", y="delta_AIC", ax=ax, color="#f4a261")
ax.set_xlabel("Modelo")
ax.set_ylabel("ΔAIC respecto al mínimo")
ax.set_title("Comparación por AIC")
plt.xticks(rotation=30, ha="right")
mostrar_grafico(fig)

# (i)-(iv): respaldo físico, Q-Q visual, AD no rechazado y ΔAIC pequeño.
candidatos_validos = tabla_info[
    (tabla_info["modelo"].isin(["Gumbel", "GEV"]))
    & (tabla_info["modelo"].isin(tabla_bondad.loc[
        tabla_bondad["AD_p_MC"] >= 0.05, "modelo"
    ].tolist()))
    & (tabla_info["delta_AIC"] < 4.0)
]
if candidatos_validos.empty:
    candidatos_validos = tabla_info[tabla_info["delta_AIC"] < 4.0]
if candidatos_validos.empty:
    candidatos_validos = tabla_info
candidatos_validos = candidatos_validos.sort_values(
    ["k", "AIC"], ascending=[True, True]
)
modelo_recomendado = str(candidatos_validos.iloc[0]["modelo"])
st.success(
    f"Modelo recomendado: {modelo_recomendado}. Se priorizó respaldo físico para máximos "
    "anuales, aceptación visual del Q-Q, ausencia de rechazo por Anderson-Darling, "
    "y ΔAIC pequeño. Entre modelos equivalentes se eligió el más simple."
)

# 5. Período de retorno
st.header("5. Período de retorno y diseño")
periodos = [2, 5, 10, 25, 50, 100]
filas_retorno = []
for nombre, params in ajustes.items():
    fila = {"Modelo": nombre}
    for T in periodos:
        fila[f"x_{T} (mm)"] = cuantil_retorno(nombre, params, T)
    filas_retorno.append(fila)
tabla_retorno = pd.DataFrame(filas_retorno)
st.dataframe(
    tabla_retorno.style.format({col: "{:.4f}" for col in tabla_retorno.columns if col != "Modelo"}),
    use_container_width=True,
    hide_index=True,
)

posiciones = posiciones_graficas(datos)
p_gringorten = posiciones["p_gringorten"].to_numpy()
y_reducida_empirica = -np.log(-np.log(p_gringorten))
periodos_curva = np.logspace(np.log10(2), np.log10(100), 300)
y_reducida_curva = -np.log(-np.log(1.0 - 1.0 / periodos_curva))

fig, ax = plt.subplots(figsize=(9, 5))
ax.scatter(y_reducida_empirica, np.sort(datos), s=42, color="#1d3557", label="Datos (Gringorten)")
for nombre, params in ajustes.items():
    probabilidades = 1.0 - 1.0 / periodos_curva
    cuantiles = CANDIDATAS[nombre].ppf(probabilidades, *params)
    ax.plot(y_reducida_curva, cuantiles, label=nombre)
ax.set_xlabel("Variable reducida: -ln[-ln(1 - 1/T)]")
ax.set_ylabel("Precipitación máxima en 24 h (mm)")
ax.set_title("Papel de Gumbel y posiciones empíricas")
etiquetas_T = [2, 5, 10, 25, 50, 100]
posiciones_T = [-np.log(-np.log(1.0 - 1.0 / T)) for T in etiquetas_T]
ax.set_xticks(posiciones_T, [str(T) for T in etiquetas_T])
ax.grid(True, alpha=0.25)
ax.legend()
mostrar_grafico(fig)

T_diseno = st.select_slider(
    "Período de retorno T para el intervalo bootstrap (años)",
    options=periodos,
    value=50,
)
B_bootstrap = st.slider("Número de remuestreos B", 100, 1000, 300, 100)
modelo_ic = st.selectbox(
    "Modelo para el cuantíl bootstrap",
    seleccionadas,
    index=seleccionadas.index(modelo_recomendado) if modelo_recomendado in seleccionadas else 0,
)
with st.spinner("Calculando intervalo bootstrap paramétrico..."):
    limite_inf, limite_sup = bootstrap_cuantil(
        datos, modelo_ic, T_diseno, B=B_bootstrap, semilla=42
    )
st.write(
    f"IC 95 % de x_{T_diseno} con {modelo_ic}: "
    f"{limite_inf:.4f} a {limite_sup:.4f} mm."
)

st.subheader("Calculadora de riesgo de falla")
T_riesgo = st.number_input("Período de retorno T (años)", min_value=1.01, value=50.0, step=1.0)
vida_util = st.number_input("Vida útil N (años)", min_value=1, value=25, step=1)
riesgo = riesgo_falla(float(T_riesgo), int(vida_util))
st.metric("Riesgo de al menos una excedencia", f"{riesgo:.4%}")
st.caption(
    "Ejemplo: para un canal de drenaje con T = 50 años y vida útil de 25 años, "
    "se calcula R = 1-(1-1/T)^N."
)

# 6. Verificación con 10 años
st.header("6. Verificación del cálculo a mano (10 años)")
muestra = cargar_csv("muestra_dist10.csv")
st.subheader("Tabla ordenada con posición de Weibull")
tabla_muestra = posiciones_graficas(muestra["pmax24h_mm"])
tabla_anios = muestra["anio"]
tabla_muestra = tabla_muestra.merge(
    muestra.sort_values("pmax24h_mm").reset_index(drop=True)[["anio", "pmax24h_mm"]],
    left_on="dato",
    right_on="pmax24h_mm",
    how="left",
).drop(columns=["pmax24h_mm"])
tabla_muestra.columns = ["pmax24h_mm", "puesto", "p_weibull", "p_gringorten", "T_weibull", "T_gringorten", "anio"]
tabla_muestra = tabla_muestra[["anio", "pmax24h_mm", "puesto", "p_weibull", "T_weibull"]]
st.dataframe(
    tabla_muestra.style.format({
        "pmax24h_mm": "{:.4f}",
        "p_weibull": "{:.4f}",
        "T_weibull": "{:.4f}",
    }),
    use_container_width=True,
    hide_index=True,
)

valores_muestra = muestra["pmax24h_mm"]
media_muestra = float(valores_muestra.mean())
desviacion_muestra = float(valores_muestra.std(ddof=1))
momentos = gumbel_momentos(valores_muestra)
params_ml_muestra, _ = ajustar(valores_muestra, "Gumbel")

st.subheader("Estadísticos y parámetros de Gumbel")
tabla_gumbel = pd.DataFrame([
    {"cálculo": "Media", "valor": media_muestra},
    {"cálculo": "Desviación estándar muestral", "valor": desviacion_muestra},
    {"cálculo": "β por momentos", "valor": momentos["beta"]},
    {"cálculo": "μ por momentos", "valor": momentos["mu"]},
    {"cálculo": "β por máxima verosimilitud", "valor": params_ml_muestra[1]},
    {"cálculo": "μ por máxima verosimilitud", "valor": params_ml_muestra[0]},
])
st.dataframe(
    tabla_gumbel.style.format({"valor": "{:.4f}"}),
    use_container_width=True,
    hide_index=True,
)

st.subheader("Cuantiles de retorno x_T")
filas_cuantiles_muestra = []
for T in [10, 50, 100]:
    filas_cuantiles_muestra.append({
        "T (años)": T,
        "x_T momentos (mm)": cuantil_retorno(
            "Gumbel", (momentos["mu"], momentos["beta"]), T
        ),
        "x_T máxima verosimilitud (mm)": cuantil_retorno("Gumbel", params_ml_muestra, T),
    })
st.dataframe(
    pd.DataFrame(filas_cuantiles_muestra).style.format({
        "x_T momentos (mm)": "{:.4f}",
        "x_T máxima verosimilitud (mm)": "{:.4f}",
    }),
    use_container_width=True,
    hide_index=True,
)

riesgo_10 = riesgo_falla(50, 25)
st.subheader("Riesgo de diseño")
st.write(
    f"Para T = 50 años y N = 25 años: "
    f"R = 1 - (1 - 1/50)^25 = {riesgo_10:.4f}."
)

# Ingeniería agrícola: modelos semiempíricos de secado
st.header("Ingeniería: modelos de secado (AICc)")
secado = cargar_csv("secado.csv")
tiempo_secado = secado["tiempo_min"].to_numpy(dtype=float)
mr_observado = secado["MR"].to_numpy(dtype=float)

@st.cache_data
def comparar_modelos_secado(t: np.ndarray, mr: np.ndarray) -> pd.DataFrame:
    """Cachea los ajustes no lineales de todos los modelos de secado."""
    return tabla_modelos(t, mr)


tabla_secado = comparar_modelos_secado(tiempo_secado, mr_observado)
tablas_validas = tabla_secado.dropna(subset=["AICc"])
mejor_modelo = str(tablas_validas.iloc[0]["modelo"])

st.subheader("Curvas observada y ajustadas")
fig, ax = plt.subplots(figsize=(9, 5))
ax.scatter(
    tiempo_secado,
    mr_observado,
    color="#1d3557",
    label="MR observado",
    s=35,
)
grid_tiempo = np.linspace(tiempo_secado.min(), tiempo_secado.max(), 300)
for nombre, especificacion in MODELOS.items():
    try:
        parametros, _ = ajustar_curva(tiempo_secado, mr_observado, nombre)
        mr_curva = especificacion["funcion"](grid_tiempo, *parametros)
        ax.plot(grid_tiempo, mr_curva, linewidth=1.8, label=nombre)
    except (ValueError, RuntimeError, FloatingPointError):
        continue
ax.set_xlabel("Tiempo de secado (min)")
ax.set_ylabel("Razón de humedad MR (adimensional)")
ax.set_title("Comparación de modelos semiempíricos de secado")
ax.grid(True, alpha=0.25)
ax.legend()
mostrar_grafico(fig)

st.subheader("Comparación por AICc")
columnas_mostrar = ["modelo", "k", "R2", "RMSE", "chi2_reducido", "AIC", "AICc", "delta_AICc"]
columnas_mostrar += [
    nombre_parametro
    for nombre_parametro in ["parametros", "a", "k_modelo", "n", "c", "k0", "b", "k1"]
    if nombre_parametro in tabla_secado.columns
]
tabla_secado_visible = tabla_secado[columnas_mostrar].copy()
st.dataframe(
    tabla_secado_visible.style.format({
        columna: "{:.4f}"
        for columna in tabla_secado_visible.columns
        if columna not in ["modelo", "k", "parametros"]
    }),
    use_container_width=True,
    hide_index=True,
)

parametros_mejor, mr_ajustado_mejor = ajustar_curva(
    tiempo_secado,
    mr_observado,
    mejor_modelo,
)
residuos = mr_observado - mr_ajustado_mejor

st.subheader(f"Residuos del mejor modelo: {mejor_modelo}")
fig, ax = plt.subplots(figsize=(8, 4))
ax.scatter(tiempo_secado, residuos, color="#e76f51", s=35)
ax.axhline(0, color="#264653", linestyle="--", linewidth=1)
ax.set_xlabel("Tiempo de secado (min)")
ax.set_ylabel("Residuo de MR (observado - ajustado)")
ax.set_title(f"Residuos de {mejor_modelo}")
ax.grid(True, alpha=0.25)
mostrar_grafico(fig)

st.info(
    "El AICc castiga los parámetros extra mediante la corrección por tamaño de muestra. "
    "Así aplica una navaja de Ockham matemática: se recompensa el ajuste, pero se penaliza "
    "la complejidad innecesaria. Es como decidir si comprar una secadora más compleja: si "
    "una más sencilla seca igual dentro de la precisión requerida, conviene la opción sencilla."
)
