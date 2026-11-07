"""Verificación independiente de los cálculos del EDA para la muestra de 10 parcelas."""

import csv
import math
from collections import defaultdict

import numpy as np


RUTA = "datos/muestra_eda10.csv"

with open(RUTA, "r", encoding="utf-8-sig", newline="") as archivo:
    filas = list(csv.DictReader(archivo))

x = np.array([float(fila["rendimiento"]) for fila in filas], dtype=float)
# Se conservan los acentos solo en los textos; los cálculos usan las fórmulas explícitas.
n = len(x)
media = float(np.mean(x))
mediana = float(np.median(x))
varianza = float(np.sum((x - media) ** 2) / (n - 1))
desviacion = math.sqrt(varianza)
cv = desviacion / media * 100.0
q1, q3 = np.quantile(x, [0.25, 0.75], method="linear")
ric = float(q3 - q1)
limite_inferior = float(q1 - 1.5 * ric)
limite_superior = float(q3 + 1.5 * ric)
atipicos = [(filas[i]["parcela"], float(valor)) for i, valor in enumerate(x)
            if valor < limite_inferior or valor > limite_superior]

print("VERIFICACIÓN EDA - muestra_eda10.csv")
print(f"n = {n:.4f}")
print(f"Media = {media:.4f}")
print(f"Mediana = {mediana:.4f}")
print(f"Varianza muestral = {varianza:.4f}")
print(f"Desviación estándar muestral = {desviacion:.4f}")
print(f"CV (%) = {cv:.4f}")
print(f"Q1 tipo 7 = {float(q1):.4f}")
print(f"Q3 tipo 7 = {float(q3):.4f}")
print(f"RIC = {ric:.4f}")
print(f"Valla inferior = {limite_inferior:.4f}")
print(f"Valla superior = {limite_superior:.4f}")
print(f"Atípicos = {atipicos}")

grupos = defaultdict(list)
for fila in filas:
    grupos[fila["riego"]].append(float(fila["rendimiento"]))
for riego in sorted(grupos):
    grupo = grupos[riego]
    print(f"Media rendimiento con riego {riego} = {sum(grupo) / len(grupo):.4f}")
