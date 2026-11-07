"""Genera conjuntos simulados personalizados para la aplicación estadística."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import gumbel_r


# Datos personales utilizados para personalizar todas las simulaciones.
CODIGO = "1102829578"
NOMBRE = "Faisury Pérez Amaya"

# Semilla reproducible derivada del código estudiantil.
SEMILLA = int(CODIGO) % (2 ** 32)
RNG = np.random.default_rng(SEMILLA)

# Definiciones de cultivos, con un rendimiento base aproximado en t/ha.
CULTIVOS = {
    "Maíz": 7.0,
    "Arroz": 6.0,
    "Yuca": 25.0,
    "Ñame": 18.0,
    "Ajonjolí": 1.5,
    "Plátano": 30.0,
    "Frijol": 2.2,
    "Sorgo": 5.0,
}
MUNICIPIOS = [
    "Sincelejo", "Corozal", "Sampués", "Los Palmitos",
    "San Marcos", "Majagual", "Tolú", "Ovejas",
]


def elegir_texto(opciones: list[str]) -> str:
    """Selecciona un elemento de una lista usando la generación aleatoria definida."""
    indice = int(RNG.integers(0, len(opciones)))
    return opciones[indice]


def generar_parcelas() -> pd.DataFrame:
    """Genera el conjunto de parcelas y el rendimiento agrícola asociado."""
    n_parcelas = int(RNG.integers(80, 121))

    suelos = np.array(["Franco", "Arcilloso", "Arenoso"])
    suelo = RNG.choice(suelos, size=n_parcelas)
    riego = RNG.choice(["Sí", "No"], size=n_parcelas, p=[0.58, 0.42])

    # El nitrógeno se distribuye entre dosis bajas y altas dentro del rango solicitado.
    dosis_n = np.clip(RNG.normal(95, 42, n_parcelas), 0, 180).round(1)

    # Las parcelas con riego reciben láminas mayores que las parcelas sin riego.
    lamina_riego = np.zeros(n_parcelas)
    mascara_riego = riego == "Sí"
    lamina_riego[mascara_riego] = RNG.normal(180, 55, mascara_riego.sum())
    lamina_riego[~mascara_riego] = RNG.normal(45, 25, (~mascara_riego).sum())
    lamina_riego = np.clip(lamina_riego, 0, None).round(1)

    materia_organica = RNG.uniform(1.2, 5.8, n_parcelas).round(2)
    ph = RNG.uniform(4.8, 7.8, n_parcelas).round(2)

    # Respuesta agrícola simulada con efectos aditivos y de suelo.
    efecto_suelo = np.select(
        [suelo == "Franco", suelo == "Arcilloso", suelo == "Arenoso"],
        [0.8, 0.3, -0.35],
        default=0.0,
    )
    dosis_n_optima = 110.0
    efecto_n = 0.035 * dosis_n - 0.00022 * (dosis_n - dosis_n_optima) ** 2
    efecto_riego = 0.018 * lamina_riego
    efecto_materia = 0.72 * materia_organica
    efecto_ph = 0.62 * ph - 0.055 * (ph - 6.4) ** 2

    rendimiento = (
        RENDIMIENTO_BASE + efecto_n + efecto_riego + efecto_materia
        + efecto_ph + efecto_suelo + RNG.normal(0, 0.65, n_parcelas)
    )
    rendimiento = np.maximum(rendimiento, 0.1)

    # Introduce dos valores claramente atípicos: uno alto y uno bajo.
    indice_alto = int(RNG.integers(0, n_parcelas))
    indice_bajo = int(RNG.integers(0, n_parcelas - 1))
    if indice_bajo >= indice_alto:
        indice_bajo += 1
    rendimiento[indice_alto] = rendimiento[indice_alto] + 8.0
    rendimiento[indice_bajo] = max(0.05, rendimiento[indice_bajo] - 8.0)

    # Asigna entre 3 y 6 faltantes, sin fijar valores negativos o fuera de rango.
    cantidad_faltantes = int(RNG.integers(3, 7))
    indices_faltantes = RNG.choice(n_parcelas, size=cantidad_faltantes, replace=False)
    materia_organica = materia_organica.astype(float)
    materia_organica[indices_faltantes] = np.nan

    parcelas = pd.DataFrame({
        "parcela": [f"P{i:03d}" for i in range(1, n_parcelas + 1)],
        "suelo": suelo,
        "riego": riego,
        "dosis_N": dosis_n,
        "lamina_riego": lamina_riego,
        "materia_organica": materia_organica,
        "ph": ph,
        "rendimiento": rendimiento.round(3),
    })
    return parcelas


def generar_precipitacion_anual() -> pd.DataFrame:
    """Simula máximas de 24 horas con una distribución Gumbel anual."""
    mu = float(RNG.uniform(70, 100))
    beta = float(RNG.uniform(12, 20))
    anios = np.arange(1986, 2026)
    valores = gumbel_r.rvs(loc=mu, scale=beta, size=len(anios), random_state=RNG)
    return pd.DataFrame({
        "anio": anios,
        "pmax24h_mm": np.maximum(valores, 0).round(2),
    }), mu, beta


def generar_clima_mensual() -> pd.DataFrame:
    """Simula precipitación mensual bimodal y temperatura con ciclo anual."""
    fechas = pd.date_range("2015-01-01", "2025-12-01", freq="MS")
    meses = fechas.month

    # Régimen bimodal: dos máximos en abril-mayo y septiembre-noviembre.
    precipitacion_base = np.array([55, 48, 65, 150, 180, 100, 75, 80, 170, 210, 160, 70])
    ciclo_base = precipitacion_base[meses - 1].astype(float)

    indice_seco = np.isin(meses, [12, 1, 2, 3])
    ciclo_base[indice_seco] *= 0.78
    ruido_lognormal = RNG.lognormal(mean=0.0, sigma=0.25, size=len(fechas))
    precipitacion = np.maximum(ciclo_base * ruido_lognormal, 0).round(2)

    # Temperatura con leve tendencia creciente y ciclo anual suave.
    posicion = np.arange(len(fechas))
    tendencia = 0.012 * posicion
    ciclo_temperatura = 1.6 * np.cos(2 * np.pi * (meses - 1) / 12)
    temperatura = 27.4 + tendencia + ciclo_temperatura + RNG.normal(0, 0.45, len(fechas))

    return pd.DataFrame({
        "fecha": fechas,
        "precipitacion_mm": precipitacion,
        "temperatura_c": temperatura.round(2),
    })


def generar_secado() -> pd.DataFrame:
    """Simula la razón de humedad con el modelo de Page."""
    k = float(RNG.uniform(0.0045, 0.0120))
    n = float(RNG.uniform(0.75, 1.35))
    tiempo = np.arange(0, 301, 15)
    mr_teorico = np.exp(-k * tiempo ** n)
    ruido = RNG.normal(0, 0.008, len(tiempo))
    mr = np.clip(mr_teorico + ruido, 0, None)
    mr[0] = 1.0

    return pd.DataFrame({
        "tiempo_min": tiempo,
        "MR": mr.round(5),
    }), k, n


def seleccionar_muestra_eda(parcelas: pd.DataFrame) -> pd.DataFrame:
    """Toma 10 parcelas, incluyendo una parcela con rendimiento atípico."""
    q1, q3 = parcelas["rendimiento"].quantile([0.25, 0.75])
    rango_intercuartil = q3 - q1
    mascara_atipico = (
        (parcelas["rendimiento"] < q1 - 1.5 * rango_intercuartil)
        | (parcelas["rendimiento"] > q3 + 1.5 * rango_intercuartil)
    )
    indices_atipicos = parcelas.index[mascara_atipico].tolist()

    atipico = parcelas.loc[RNG.choice(indices_atipicos)].copy()
    normales = parcelas.loc[~mascara_atipico].sample(n=9, random_state=SEMILLA)
    muestra = pd.concat([normales, atipico.to_frame().T])
    return muestra[["parcela", "suelo", "riego", "rendimiento"]].reset_index(drop=True)


def seleccionar_muestra_dist(precipitacion: pd.DataFrame) -> pd.DataFrame:
    """Selecciona 10 años al azar entre los 40 años disponibles."""
    return precipitacion.sample(n=10, random_state=SEMILLA).sort_values("anio").reset_index(drop=True)


def seleccionar_muestra_regresion(parcelas: pd.DataFrame) -> pd.DataFrame:
    """Forma 8 grupos por lámina de riego y conserva una parcela de cada grupo."""
    q1, q3 = parcelas["rendimiento"].quantile([0.25, 0.75])
    rango_intercuartil = q3 - q1
    mascara_atipico = (
        (parcelas["rendimiento"] < q1 - 1.5 * rango_intercuartil)
        | (parcelas["rendimiento"] > q3 + 1.5 * rango_intercuartil)
    )
    candidatas = parcelas.loc[~mascara_atipico].copy()

    # pd.qcut reparte las parcelas sin atípicos según cuantiles de lámina.
    candidatas["grupo_lamina"] = pd.qcut(
        candidatas["lamina_riego"], q=8, labels=False, duplicates="drop"
    )
    muestra = (
        candidatas.dropna(subset=["grupo_lamina"])
        .groupby("grupo_lamina", group_keys=False)
        .apply(lambda grupo: grupo.iloc[[int(RNG.integers(0, len(grupo)))]], include_groups=False)
        .reset_index(drop=True)
    )
    return muestra[["parcela", "lamina_riego", "rendimiento"]].sort_values("lamina_riego").reset_index(drop=True)


def seleccionar_muestra_series(clima: pd.DataFrame) -> pd.DataFrame:
    """Extrae los 24 meses de 2024-2025 y marca entrenamiento y validación."""
    datos = clima.loc[(clima["fecha"] >= "2024-01-01") & (clima["fecha"] <= "2025-12-01")].copy()
    datos = datos.reset_index(drop=True)
    datos["periodo"] = np.arange(1, len(datos) + 1)

    muestra = pd.DataFrame({
        "periodo": datos["periodo"],
        "fecha": datos["fecha"].dt.strftime("%Y-%m-%d"),
        "anio": datos["fecha"].dt.year,
        "mes": datos["fecha"].dt.month,
        "precipitacion_mm": datos["precipitacion_mm"],
        "conjunto": np.where(datos["periodo"] <= 18, "entrenamiento", "validacion"),
    })
    return muestra


def generar_todos_los_datos() -> None:
    """Genera y guarda todos los archivos CSV y metadatos solicitados."""
    global RENDIMIENTO_BASE

    nombres_cultivos = list(CULTIVOS.keys())
    cultivo = nombres_cultivos[int(RNG.integers(0, len(nombres_cultivos)))]
    RENDIMIENTO_BASE = CULTIVOS[cultivo]
    municipio = elegir_texto(MUNICIPIOS)

    carpeta_datos = Path(__file__).resolve().parent / "datos"
    carpeta_datos.mkdir(parents=True, exist_ok=True)

    parcelas = generar_parcelas()
    precipitacion, mu_gumbel, beta_gumbel = generar_precipitacion_anual()
    clima = generar_clima_mensual()
    secado, k_page, n_page = generar_secado()

    parcelas.to_csv(carpeta_datos / "parcelas.csv", index=False)
    precipitacion.to_csv(carpeta_datos / "precip_max_anual.csv", index=False)
    clima.to_csv(carpeta_datos / "clima_mensual.csv", index=False)
    secado.to_csv(carpeta_datos / "secado.csv", index=False)

    muestra_eda = seleccionar_muestra_eda(parcelas)
    muestra_dist = seleccionar_muestra_dist(precipitacion)
    muestra_reg = seleccionar_muestra_regresion(parcelas)
    muestra_series = seleccionar_muestra_series(clima)

    muestra_eda.to_csv(carpeta_datos / "muestra_eda10.csv", index=False)
    muestra_dist.to_csv(carpeta_datos / "muestra_dist10.csv", index=False)
    muestra_reg.to_csv(carpeta_datos / "muestra_reg8.csv", index=False)
    muestra_series.to_csv(carpeta_datos / "muestra_series24.csv", index=False)

    suma_rendimiento = float(parcelas["rendimiento"].sum())
    texto_huella = f"{CODIGO}|{len(parcelas)}|{suma_rendimiento:.2f}"
    huella = hashlib.md5(texto_huella.encode("utf-8")).hexdigest()[:8].upper()

    metadatos = {
        "codigo": CODIGO,
        "nombre": NOMBRE,
        "cultivo": cultivo,
        "municipio": municipio,
        "n_parcelas": len(parcelas),
        "huella": huella,
    }
    with open(carpeta_datos / "metadatos.json", "w", encoding="utf-8") as archivo:
        json.dump(metadatos, archivo, ensure_ascii=False, indent=2)

    print(f"Nombre: {NOMBRE}")
    print(f"Código: {CODIGO}")
    print(f"Cultivo: {cultivo}")
    print(f"Municipio: {municipio}")
    print(f"Huella: {huella}")
    print("\nmuestra_eda10.csv")
    print(muestra_eda.to_string(index=False))
    print("\nmuestra_dist10.csv")
    print(muestra_dist.to_string(index=False))
    print("\nmuestra_reg8.csv")
    print(muestra_reg.to_string(index=False))
    print("\nmuestra_series24.csv")
    print(muestra_series.to_string(index=False))


if __name__ == "__main__":
    generar_todos_los_datos()
