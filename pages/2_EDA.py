"""Página de análisis exploratorio de datos agrícolas."""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

from src.datos import cargar_csv, tarjeta_estudiante
from src.eda import resumen_numerico, tabla_frecuencias, vallas_tukey
from src.exportar import figura_pdf, figura_png, reporte_markdown, tabla_excel
from src.validacion import archivo_vacio, columnas_seleccionadas, suficientes_datos, datos_faltantes


UNIDADES = {
    "dosis_N": "kg/ha",
    "lamina_riego": "mm",
    "materia_organica": "%",
    "ph": "adimensional",
    "rendimiento": "t/ha",
}

NOMBRES = {
    "dosis_N": "Dosis de N",
    "lamina_riego": "Lámina de riego",
    "materia_organica": "Materia orgánica",
    "ph": "pH",
    "rendimiento": "Rendimiento",
}


def mostrar_grafico(figura: plt.Figure) -> None:
    """Muestra una figura de Matplotlib y libera la memoria utilizada."""
    st.pyplot(figura, use_container_width=True)
    plt.close(figura)


st.set_page_config(page_title="EDA", layout="wide")
tarjeta_estudiante()
st.title("EDA: Análisis Exploratorio de Datos")

df = cargar_csv("parcelas.csv")
if not archivo_vacio(df, "parcelas.csv"):
    st.stop()
if not columnas_seleccionadas(
    df, ["parcela", "suelo", "riego", "rendimiento"], "el análisis EDA"
):
    st.stop()
datos_faltantes(df, ["parcela", "suelo", "riego", "rendimiento"], "parcelas.csv")
if not suficientes_datos(len(df), 10, "el EDA de parcelas"):
    st.stop()

# Los filtros se aplican primero para que todas las secciones trabajen igual.
st.sidebar.header("Filtros del EDA")
suelo_opciones = ["Todos"] + sorted(df["suelo"].dropna().unique().tolist())
suelo_elegido = st.sidebar.selectbox("Suelo", suelo_opciones)
riego_opciones = ["Todos"] + sorted(df["riego"].dropna().unique().tolist())
riego_elegido = st.sidebar.selectbox("Riego", riego_opciones)

df_filtrado = df.copy()
if suelo_elegido != "Todos":
    df_filtrado = df_filtrado[df_filtrado["suelo"] == suelo_elegido]
if riego_elegido != "Todos":
    df_filtrado = df_filtrado[df_filtrado["riego"] == riego_elegido]

st.caption(f"Datos mostrados: {len(df_filtrado)} de {len(df)} parcelas.")

# a) Análisis univariado
st.header("a) Univariado")
numericas = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
variable = st.selectbox(
    "Variable numérica",
    numericas,
    format_func=lambda c: f"{NOMBRES.get(c, c)} ({UNIDADES.get(c, '')})",
)

resumen = resumen_numerico(df_filtrado[variable])
tabla_resumen = pd.DataFrame([resumen]).T
tabla_resumen.columns = ["valor"]
tabla_resumen.index.name = "medida"
st.dataframe(tabla_resumen.style.format("{:.4f}", na_rep="—"), use_container_width=True)

col_hist, col_caja = st.columns(2)
serie = df_filtrado[variable].dropna()
unidad = UNIDADES.get(variable, "")
nombre = NOMBRES.get(variable, variable)

with col_hist:
    fig, ax = plt.subplots()
    sns.histplot(serie, kde=True, ax=ax, color="#2a9d8f")
    ax.set_title(f"Histograma y densidad de {nombre.lower()}")
    ax.set_xlabel(f"{nombre} ({unidad})" if unidad else nombre)
    ax.set_ylabel("Frecuencia")
    mostrar_grafico(fig)

with col_caja:
    fig, ax = plt.subplots()
    sns.boxplot(x=serie, ax=ax, color="#f4a261")
    ax.set_title(f"Diagrama de caja de {nombre.lower()}")
    ax.set_xlabel(f"{nombre} ({unidad})" if unidad else nombre)
    mostrar_grafico(fig)

lim_inf, lim_sup, atipicos = vallas_tukey(serie)
st.subheader("Parcelas atípicas según Tukey")
if serie.empty:
    st.info("No hay datos disponibles con los filtros seleccionados.")
else:
    mascara_atipicos = df_filtrado[variable].isin(atipicos)
    tabla_atipicos = df_filtrado.loc[mascara_atipicos, ["parcela", "suelo", "riego", variable]]
    st.write(
        f"Valla inferior: {lim_inf:.4f} {unidad}; "
        f"valla superior: {lim_sup:.4f} {unidad}"
    )
    if tabla_atipicos.empty:
        st.info("No se identificaron parcelas atípicas.")
    else:
        st.dataframe(tabla_atipicos, use_container_width=True, hide_index=True)

# b) Análisis cualitativo
st.header("b) Cualitativo")
for variable_cualitativa in ["suelo", "riego"]:
    st.subheader(f"Distribución de {variable_cualitativa}")
    frecuencias = tabla_frecuencias(df_filtrado[variable_cualitativa])
    col_tabla, col_grafico = st.columns(2)
    with col_tabla:
        st.dataframe(
            frecuencias.style.format({"frecuencia_relativa": "{:.4f}"}),
            use_container_width=True,
            hide_index=True,
        )
    with col_grafico:
        fig, ax = plt.subplots()
        sns.barplot(
            data=frecuencias,
            x="categoria",
            y="frecuencia_absoluta",
            ax=ax,
            color="#457b9d",
        )
        ax.set_title(f"Frecuencia absoluta de {variable_cualitativa}")
        ax.set_xlabel(f"{variable_cualitativa.capitalize()}")
        ax.set_ylabel("Número de parcelas")
        mostrar_grafico(fig)

# c) Análisis bivariado
st.header("c) Bivariado")
col_suelo, col_riego = st.columns(2)
with col_suelo:
    fig, ax = plt.subplots()
    sns.boxplot(data=df_filtrado, x="suelo", y="rendimiento", ax=ax, color="#8ecae6")
    ax.set_xlabel("Suelo")
    ax.set_ylabel("Rendimiento (t/ha)")
    ax.set_title("Rendimiento según el suelo")
    mostrar_grafico(fig)
with col_riego:
    fig, ax = plt.subplots()
    sns.boxplot(data=df_filtrado, x="riego", y="rendimiento", ax=ax, color="#90be6d")
    ax.set_xlabel("Riego")
    ax.set_ylabel("Rendimiento (t/ha)")
    ax.set_title("Rendimiento según el riego")
    mostrar_grafico(fig)

opciones_x = [c for c in numericas if c != "rendimiento"]
x_elegida = st.selectbox(
    "Variable X para el diagrama de dispersión",
    opciones_x,
    format_func=lambda c: f"{NOMBRES.get(c, c)} ({UNIDADES.get(c, '')})",
)
fig, ax = plt.subplots()
sns.scatterplot(
    data=df_filtrado,
    x=x_elegida,
    y="rendimiento",
    hue="riego",
    palette="deep",
    ax=ax,
)
ax.set_xlabel(f"{NOMBRES.get(x_elegida, x_elegida)} ({UNIDADES.get(x_elegida, '')})")
ax.set_ylabel("Rendimiento (t/ha)")
ax.set_title("Dispersión coloreada por riego")
mostrar_grafico(fig)

st.subheader("Matriz de correlación de Pearson")
correlaciones = df_filtrado[numericas].corr(method="pearson")
fig, ax = plt.subplots(figsize=(8, 6))
sns.heatmap(
    correlaciones,
    annot=True,
    fmt=".2f",
    cmap="vlag",
    center=0,
    ax=ax,
)
ax.set_title("Correlación de Pearson entre variables numéricas")
mostrar_grafico(fig)

# d) Datos faltantes y atípicos
st.header("d) Datos faltantes y atípicos")
faltantes = df.isna().sum()
tabla_faltantes = pd.DataFrame({
    "variable": faltantes[faltantes > 0].index,
    "cantidad": faltantes[faltantes > 0].values,
})
if tabla_faltantes.empty:
    st.success("No se encontraron valores faltantes en parcelas.csv.")
else:
    st.dataframe(tabla_faltantes, use_container_width=True, hide_index=True)
    parcelas_faltantes = df[df.isna().any(axis=1)][["parcela"] + tabla_faltantes["variable"].tolist()].drop_duplicates()
    st.dataframe(parcelas_faltantes, use_container_width=True, hide_index=True)
st.info(
    "No borre las faltantes sin justificar: primero revise si son errores de captura, "
    "identifique el mecanismo (MCAR, MAR o MNAR) e informe el impacto. Según el objetivo, "
    "puede imputarlas con un método razonable, analizar por separado o usar un modelo que "
    "acepte faltantes. Los valores elegidos deben quedar documentados."
)

# e) Verificación con 10 parcelas
st.header('e) Verificación del cálculo a mano (10 parcelas)')
muestra = cargar_csv("muestra_eda10.csv")
st.subheader("Tabla de la muestra")
st.dataframe(muestra, use_container_width=True, hide_index=True)

resumen_muestra = resumen_numerico(muestra["rendimiento"])
tabla_verificacion = pd.DataFrame([resumen_muestra]).T
tabla_verificacion.columns = ["valor"]
tabla_verificacion.index.name = "medida"
st.subheader("Resumen numérico")
st.dataframe(tabla_verificacion.style.format("{:.4f}", na_rep="—"), use_container_width=True)

media_muestra = muestra["rendimiento"].mean()
tabla_desviaciones = pd.DataFrame({
    "parcela": muestra["parcela"],
    "rendimiento": muestra["rendimiento"],
    "x - media": muestra["rendimiento"] - media_muestra,
    "cuadrado": (muestra["rendimiento"] - media_muestra) ** 2,
})
st.subheader("Tabla de desviaciones")
st.dataframe(
    tabla_desviaciones.style.format({
        "rendimiento": "{:.4f}",
        "x - media": "{:.4f}",
        "cuadrado": "{:.4f}",
    }),
    use_container_width=True,
    hide_index=True,
)

lim_inf_muestra, lim_sup_muestra, atipicos_muestra = vallas_tukey(muestra["rendimiento"])
st.subheader("Vallas y atípicos de Tukey")
st.write(
    f"Límite inferior = {lim_inf_muestra:.4f} t/ha; "
    f"límite superior = {lim_sup_muestra:.4f} t/ha."
)
if atipicos_muestra:
    st.write("Atípicos: " + ", ".join(f"{valor:.4f}" for valor in atipicos_muestra) + " t/ha")
else:
    st.write("Atípicos: ninguno")

media_por_riego = muestra.groupby("riego", dropna=False)["rendimiento"].mean().reset_index()
media_por_riego.columns = ["riego", "media_rendimiento_t_ha"]
st.subheader("Media de rendimiento por riego")
st.dataframe(
    media_por_riego.style.format({"media_rendimiento_t_ha": "{:.4f}"}),
    use_container_width=True,
    hide_index=True,
)

with st.expander("Descargar resultados"):
    tabla_excel(
        {
            "Resumen": tabla_resumen,
            "Frecuencia suelo": tabla_frecuencias(df_filtrado["suelo"]),
            "Frecuencia riego": tabla_frecuencias(df_filtrado["riego"]),
            "Muestra EDA10": muestra,
        },
        "eda_resultados.xlsx",
    )
    fig_exportar, ax_exportar = plt.subplots(figsize=(8, 5))
    sns.histplot(df_filtrado[variable].dropna(), kde=True, ax=ax_exportar, color="#2a9d8f")
    ax_exportar.set_xlabel(f"{nombre} ({unidad})" if unidad else nombre)
    ax_exportar.set_ylabel("Frecuencia")
    ax_exportar.set_title(f"Histograma de {nombre.lower()}")
    figura_png(fig_exportar, "eda_histograma.png")
    figura_pdf(fig_exportar, "eda_histograma.pdf")
    reporte_markdown(
        "Reporte EDA",
        {
            "Variable analizada": variable,
            "Resumen numérico": "El resumen seleccionado está disponible en la tabla Excel.",
            "Datos faltantes": (
                "Se conservaron los faltantes y se documentó su tratamiento esperado; "
                "no se eliminaron sin justificación."
            ),
        },
        "reporte_eda.md",
    )
    plt.close(fig_exportar)
