"""Ejecuta AutoTS y guarda los resultados reproducibles del pronóstico agrícola."""

import json
from pathlib import Path

import pandas as pd

from src.series import cargar_serie, ejecutar_autots


# Define la raíz del proyecto para que los archivos se guarden sin depender de
# la carpeta desde la cual se invoque el script.
RAIZ_PROYECTO = Path(__file__).resolve().parent

# Lee los metadatos porque el código identifica al estudiante y permite
# generar una semilla reproducible sin usar valores aleatorios ocultos.
ruta_metadatos = RAIZ_PROYECTO / "datos" / "metadatos.json"
with ruta_metadatos.open("r", encoding="utf-8") as archivo:
    metadatos = json.load(archivo)

# Convierte el código de texto a entero y conserva los últimos cuatro dígitos.
# Esta reducción mantiene la semilla dentro de un rango manejable por AutoTS.
semilla = int(metadatos["codigo"]) % 10000

# Carga la precipitación mensual desde 2015 hasta 2025 con índice y frecuencia MS.
serie_precipitacion = cargar_serie("precipitacion_mm")

# Ejecuta AutoTS como un ensayo de variedades con selección genética:
# prueba modelos y transformaciones, evalúa cada variante históricamente, conserva
# las mejores y usa validaciones hacia atrás para detectar pronósticos consistentes.
resultado = ejecutar_autots(
    serie=serie_precipitacion,
    horizonte=12,
    model_list="superfast",
    generaciones=5,
    validaciones=2,
    intervalo=0.9,
    semilla=semilla,
)

# Crea la carpeta de resultados sólo si todavía no existe.
ruta_resultados = RAIZ_PROYECTO / "resultados"
ruta_resultados.mkdir(parents=True, exist_ok=True)

# Guarda el pronóstico con punto, banda inferior y banda superior en milímetros.
resultado["pronostico"].to_csv(
    ruta_resultados / "autots_pronostico.csv",
    index=False,
)

# Guarda las diez mejores variantes evaluadas por AutoTS.
resultado["top10"].to_csv(
    ruta_resultados / "autots_top10_modelos.csv",
    index=False,
)

# Guarda el nombre, los parámetros y las transformaciones del modelo ganador.
with (ruta_resultados / "autots_mejor_modelo.json").open(
    "w",
    encoding="utf-8",
) as archivo:
    json.dump(resultado["mejor_modelo"], archivo, ensure_ascii=False, indent=2, default=str)

# Identifica la posición de SeasonalNaive si aparece en la tabla final.
top10 = resultado["top10"]
posicion_seasonal_naive = None
for indice, fila in top10.iterrows():
    nombre_modelo = str(fila["Model"]).lower()
    if "seasonalnaive" in nombre_modelo or "seasonal naive" in nombre_modelo:
        posicion_seasonal_naive = indice + 1
        break

# Presenta el modelo ganador y la posición de SeasonalNaive para revisión rápida.
print(
    "Modelo ganador:",
    resultado["mejor_modelo"]["nombre"],
)
if posicion_seasonal_naive is None:
    print("SeasonalNaive: no aparece en el top 10")
else:
    print(f"SeasonalNaive: puesto {posicion_seasonal_naive} en el top 10")
