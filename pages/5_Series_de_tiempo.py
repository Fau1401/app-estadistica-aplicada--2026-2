"""Página funcional de exploración, descomposición y pronóstico temporal."""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from src.datos import cargar_csv, cargar_metadatos, tarjeta_estudiante
from src.series import (
    cargar_serie,
    concurso_referencia,
    descomponer,
    ejecutar_autots,
    indices_estacionales,
    metodos_referencia,
    metricas,
    promedio_movil,
)


MESES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]


def mostrar_grafico(figura: plt.Figure) -> None:
    """Muestra una figura y libera la memoria de Matplotlib."""
    st.pyplot(figura, width="stretch")
    plt.close(figura)


@st.cache_resource
def ejecutar_autots_cache(
    serie: pd.Series,
    horizonte: int,
    model_list: str,
    generaciones: int,
    validaciones: int,
    intervalo: float,
    semilla: int,
) -> dict:
    """Cachea una ejecución de AutoTS para evitar repetir el mismo cálculo."""
    return ejecutar_autots(
        serie,
        horizonte,
        model_list,
        generaciones,
        validaciones,
        intervalo,
        semilla,
    )


st.set_page_config(page_title="Series de tiempo", layout="wide")
tarjeta_estudiante()
st.title("Series de tiempo")

# 1. Exploración
st.header("1. Exploración")
variable = st.selectbox(
    "Variable",
    options=["precipitacion_mm", "temperatura_c"],
    format_func=lambda valor: (
        "Precipitación (mm)" if valor == "precipitacion_mm" else "Temperatura (°C)"
    ),
)
serie = cargar_serie(variable)
unidad = "mm" if variable == "precipitacion_mm" else "°C"
nombre_variable = (
    "Precipitación" if variable == "precipitacion_mm" else "Temperatura"
)

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(serie.index, serie.values, color="#457b9d", alpha=0.45, label="Observado")
ax.plot(
    promedio_movil(serie, 3).index,
    promedio_movil(serie, 3).values,
    color="#e09f3e",
    label="PM3",
)
ax.plot(
    promedio_movil(serie, 12).index,
    promedio_movil(serie, 12).values,
    color="#9d0208",
    linewidth=2,
    label="PM12",
)
ax.set_xlabel("Fecha")
ax.set_ylabel(f"{nombre_variable} ({unidad})")
ax.set_title(f"Serie mensual de {nombre_variable.lower()} y promedios móviles")
ax.legend()
ax.grid(True, alpha=0.25)
mostrar_grafico(fig)

datos_mes = serie.dropna().to_frame(name="valor").copy()
datos_mes["mes"] = datos_mes.index.month
fig, ax = plt.subplots(figsize=(10, 4))
meses_presentes = sorted(datos_mes["mes"].unique())
datos_mes["nombre_mes"] = datos_mes["mes"].map(
    lambda numero: MESES[numero - 1]
)
orden_meses = [MESES[numero - 1] for numero in meses_presentes]
datos_mes["nombre_mes"] = pd.Categorical(
    datos_mes["nombre_mes"],
    categories=orden_meses,
    ordered=True,
)
import seaborn as sns
sns.boxplot(
    data=datos_mes,
    x="nombre_mes",
    y="valor",
    ax=ax,
    color="#90be6d",
)
ax.set_xlabel("Mes")
ax.set_ylabel(f"{nombre_variable} ({unidad})")
ax.set_title(f"Distribución mensual de {nombre_variable.lower()}")
plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
mostrar_grafico(fig)

st.info(
    "Tendencia: cambio de largo plazo; estacionalidad: patrón que se repite cada 12 "
    "meses; irregularidad: variaciones no explicadas por esos dos componentes. En el "
    "Caribe colombiano las lluvias suelen mostrar un régimen bimodal, con máximos hacia "
    "abril-mayo y septiembre-noviembre y menor lluvia entre periodos secos."
)

# 2. Descomposición clásica
st.header("2. Descomposición clásica")
try:
    descompuesta = descomponer(serie)
    componentes = [
        ("Observada", descompuesta.observed),
        ("Tendencia", descompuesta.trend),
        ("Estacionalidad", descompuesta.seasonal),
        ("Residuo", descompuesta.resid),
    ]
    fig, ejes = plt.subplots(4, 1, figsize=(11, 8), sharex=True)
    for ax, (titulo, componente) in zip(ejes, componentes):
        ax.plot(componente.index, componente.values, linewidth=1.2, color="#457b9d")
        ax.set_ylabel(f"{unidad}")
        ax.set_title(titulo)
        ax.grid(True, alpha=0.25)
    ejes[-1].set_xlabel("Fecha")
    plt.tight_layout()
    mostrar_grafico(fig)
except ValueError as error:
    st.error(str(error))

indices = indices_estacionales(serie)
tabla_indices = pd.DataFrame({
    "mes_numero": indices.index,
    "mes": [MESES[int(numero) - 1] for numero in indices.index],
    "indice": indices.values,
})
tabla_indices["interpretación"] = tabla_indices["indice"].map(
    lambda valor: (
        "Por encima del promedio general"
        if valor >= 0
        else "Por debajo del promedio general"
    )
)
st.subheader("Índices estacionales aditivos")
st.dataframe(
    tabla_indices[["mes_numero", "mes", "indice", "interpretación"]].style.format({
        "indice": "{:.4f}",
    }),
    width="stretch",
    hide_index=True,
)
st.caption(
    f"Suma de los 12 índices: {indices.sum():.4f} {unidad}. "
    "La suma cercana a cero conserva la separación aditiva entre componentes."
)

# 3. Métodos de referencia y validación
st.header("3. Métodos de referencia y validación")
validacion_ultimos = serie.dropna().copy().sort_index().iloc[-12:]
entrenamiento_ref = serie.dropna().copy().sort_index().iloc[:-12]
pronosticos_ref = metodos_referencia(
    entrenamiento_ref,
    h=len(validacion_ultimos),
)

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(
    validacion_ultimos.index,
    validacion_ultimos.values,
    color="#1d3557",
    marker="o",
    linewidth=2,
    label="Real",
)
colores = ["#e09f3e", "#9d0208", "#2a9d8f"]
for (nombre, pronostico), color in zip(pronosticos_ref.items(), colores):
    ax.plot(
        pronostico.index,
        pronostico.values,
        marker="o",
        linewidth=1.5,
        color=color,
        label=nombre,
    )
ax.set_xlabel("Mes")
ax.set_ylabel(f"{nombre_variable} ({unidad})")
ax.set_title("Validación con los últimos 12 meses")
ax.legend()
ax.grid(True, alpha=0.25)
mostrar_grafico(fig)

filas_metricas_ref = []
for nombre, pronostico in pronosticos_ref.items():
    metricas_metodo = metricas(validacion_ultimos, pronostico)
    filas_metricas_ref.append({"metodo": nombre, **metricas_metodo})
tabla_metricas_ref = pd.DataFrame(filas_metricas_ref).sort_values(
    "SMAPE"
).reset_index(drop=True)
st.dataframe(
    tabla_metricas_ref.style.format({
        "MAE": "{:.4f}",
        "RMSE": "{:.4f}",
        "SMAPE": "{:.4f}",
    }),
    width="stretch",
    hide_index=True,
)

# 4. AutoTS
st.header("4. Pronóstico automático con AutoTS")
metadatos = cargar_metadatos()
semilla = int(metadatos["codigo"]) % 10000

with st.form("form_autots"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        horizonte = st.slider("Horizonte (meses)", 6, 24, 12)
    with col2:
        model_list = st.selectbox("Lista de modelos", ["superfast", "fast"])
    with col3:
        generaciones = st.slider("Generaciones", 1, 10, 5)
    with col4:
        validaciones = st.slider("Validaciones", 1, 3, 2)
    intervalo = st.select_slider(
        "Intervalo de predicción",
        options=[0.8, 0.9, 0.95],
        value=0.9,
    )
    ejecutar = st.form_submit_button("Ejecutar AutoTS")

if ejecutar:
    with st.spinner("AutoTS está evaluando modelos y transformaciones. Puede tardar varios minutos."):
        resultado_autots = ejecutar_autots_cache(
            cargar_serie("precipitacion_mm"),
            horizonte,
            model_list,
            generaciones,
            validaciones,
            intervalo,
            semilla,
        )
    st.session_state["resultado_autots"] = resultado_autots

resultado_autots = st.session_state.get("resultado_autots")
if resultado_autots is not None:
    st.subheader("Modelo ganador")
    st.write(resultado_autots["mejor_modelo"]["nombre"])
    st.json(resultado_autots["mejor_modelo"])

    pronostico_autots = resultado_autots["pronostico"]
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(
        serie.index,
        serie.values,
        color="#1d3557",
        linewidth=1.5,
        label="Serie observada",
    )
    fechas_pronostico = pd.to_datetime(pronostico_autots["fecha"])
    ax.plot(
        fechas_pronostico,
        pronostico_autots["pronostico_mm"],
        color="#d62828",
        linewidth=2,
        label="Pronóstico",
    )
    ax.fill_between(
        fechas_pronostico,
        pronostico_autots["limite_inferior_mm"],
        pronostico_autots["limite_superior_mm"],
        color="#f4a261",
        alpha=0.35,
        label=f"Banda {int(intervalo * 100)} %",
    )
    ax.set_xlabel("Fecha")
    ax.set_ylabel(f"{nombre_variable} ({unidad})")
    ax.set_title("Pronóstico automático con banda de incertidumbre")
    ax.legend()
    ax.grid(True, alpha=0.25)
    mostrar_grafico(fig)

    st.subheader("Tabla del pronóstico")
    st.dataframe(
        pronostico_autots.style.format({
            "pronostico_mm": "{:.4f}",
            "limite_inferior_mm": "{:.4f}",
            "limite_superior_mm": "{:.4f}",
        }),
        width="stretch",
        hide_index=True,
    )
    st.subheader("Top 10 modelos")
    st.dataframe(
        resultado_autots["top10"].style.format({
            columna: "{:.4f}"
            for columna in ["smape", "mae", "rmse", "Score"]
            if columna in resultado_autots["top10"].columns
        }),
        width="stretch",
        hide_index=True,
    )
    st.download_button(
        "Descargar pronóstico en CSV",
        data=pronostico_autots.to_csv(index=False).encode("utf-8-sig"),
        file_name="autots_pronostico.csv",
        mime="text/csv",
    )
    st.info(
        "AutoTS funciona como un ensayo de variedades: prueba distintos modelos y "
        "transformaciones, los evalúa en observaciones históricas y conserva las mejores "
        "variedades según su desempeño, como en una selección genética agronómica."
    )

# 5. Resultados guardados
st.header("5. Resultados guardados")
ruta_raiz = Path(__file__).resolve().parent.parent
ruta_resultados = ruta_raiz / "resultados"
archivos_guardados = ["autots_pronostico.csv", "autots_top10_modelos.csv", "autots_mejor_modelo.json"]
existen_resultados = all((ruta_resultados / nombre).exists() for nombre in archivos_guardados)
if existen_resultados:
    pronostico_guardado = pd.read_csv(ruta_resultados / "autots_pronostico.csv")
    top10_guardado = pd.read_csv(ruta_resultados / "autots_top10_modelos.csv")
    with (ruta_resultados / "autots_mejor_modelo.json").open("r", encoding="utf-8") as archivo:
        mejor_guardado = json.load(archivo)
    st.success("Se encontraron resultados guardados previamente; no se volvió a ejecutar AutoTS.")
    st.json(mejor_guardado)
    st.dataframe(pronostico_guardado, width="stretch", hide_index=True)
    st.dataframe(top10_guardado, width="stretch", hide_index=True)
else:
    st.info("Aún no existen los tres archivos de resultados en la carpeta resultados/.")

# 6. Verificación de 24 meses
st.header("6. Verificación del cálculo a mano (24 meses)")
muestra24 = cargar_csv("muestra_series24.csv")
entrenamiento_muestra = muestra24[muestra24["conjunto"] == "entrenamiento"].copy()
validacion_muestra = muestra24[muestra24["conjunto"] == "validacion"].copy()

tabla_24 = pd.concat([
    entrenamiento_muestra[["periodo", "fecha", "precipitacion_mm", "conjunto"]],
    validacion_muestra[["periodo", "fecha", "precipitacion_mm", "conjunto"]],
]).sort_values("periodo")
tabla_24["PM3"] = tabla_24["precipitacion_mm"].rolling(
    window=3,
    min_periods=3,
).mean()
st.dataframe(
    tabla_24.style.format({
        "precipitacion_mm": "{:.4f}",
        "PM3": "{:.4f}",
    }),
    width="stretch",
    hide_index=True,
)

serie_muestra_entrenamiento = (
    entrenamiento_muestra.set_index("fecha")["precipitacion_mm"].asfreq("MS")
)
indices_muestra = indices_estacionales(
    serie_muestra_entrenamiento
)
tabla_indices_muestra = pd.DataFrame({
    "mes": [MESES[int(numero) - 1] for numero in indices_muestra.index],
    "indice": indices_muestra.values,
})
st.subheader("Índices estacionales y suma")
st.dataframe(
    tabla_indices_muestra.style.format({"indice": "{:.4f}"}),
    width="stretch",
    hide_index=True,
)
st.write(f"Suma de índices: {indices_muestra.sum():.4f}")

pronosticos_muestra = metodos_referencia(
    serie_muestra_entrenamiento,
    h=6,
)
reales_muestra = validacion_muestra.set_index("fecha")["precipitacion_mm"]
tabla_pronostico_muestra = pd.DataFrame({"real": reales_muestra})
for nombre, pronostico in pronosticos_muestra.items():
    tabla_pronostico_muestra[nombre] = pronostico
tabla_pronostico_muestra = tabla_pronostico_muestra.reset_index().rename(
    columns={"fecha": "fecha"}
)
st.subheader("Pronósticos julio-diciembre 2025")
st.dataframe(
    tabla_pronostico_muestra.style.format({
        columna: "{:.4f}"
        for columna in tabla_pronostico_muestra.columns
        if columna != "fecha"
    }),
    width="stretch",
    hide_index=True,
)

filas_errores = []
metricas_metodos_muestra = []
for nombre, pronostico in pronosticos_muestra.items():
    pronostico_alineado = pronostico.reindex(reales_muestra.index)
    error = reales_muestra - pronostico_alineado
    metricas_metodo = metricas(reales_muestra, pronostico_alineado)
    metricas_metodos_muestra.append({"metodo": nombre, **metricas_metodo})
    for fecha in reales_muestra.index:
        y = float(reales_muestra.loc[fecha])
        yhat = float(pronostico_alineado.loc[fecha])
        e = y - yhat
        filas_errores.append({
            "metodo": nombre,
            "fecha": fecha,
            "|e|": abs(e),
            "e2": e ** 2,
            "termino_sMAPE": abs(e) / (abs(y) + abs(yhat)),
        })

st.subheader("Errores por mes")
st.dataframe(
    pd.DataFrame(filas_errores).style.format({
        "|e|": "{:.4f}",
        "e2": "{:.4f}",
        "termino_sMAPE": "{:.4f}",
    }),
    width="stretch",
    hide_index=True,
)

tabla_metricas_muestra = pd.DataFrame(metricas_metodos_muestra).sort_values(
    "SMAPE"
).reset_index(drop=True)
st.subheader("Métricas y método ganador")
st.dataframe(
    tabla_metricas_muestra.style.format({
        "MAE": "{:.4f}",
        "RMSE": "{:.4f}",
        "SMAPE": "{:.4f}",
    }),
    width="stretch",
    hide_index=True,
)
st.success(f"Método ganador: {tabla_metricas_muestra.iloc[0]['metodo']}")

fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(
    tabla_24["fecha"],
    tabla_24["precipitacion_mm"],
    color="#1d3557",
    marker="o",
    label="Serie de muestra",
)
fecha_corte = validacion_muestra["fecha"].min()
ax.axvline(fecha_corte, color="#d62828", linestyle="--", linewidth=2)
ax.text(
    fecha_corte,
    ax.get_ylim()[1],
    " Inicio de validación",
    va="top",
    color="#d62828",
)
ax.set_xlabel("Fecha")
ax.set_ylabel("Precipitación (mm)")
ax.set_title("Entrenamiento y validación de la muestra de 24 meses")
ax.grid(True, alpha=0.25)
mostrar_grafico(fig)
