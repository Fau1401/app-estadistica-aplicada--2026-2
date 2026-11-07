"""Verificación independiente de Gumbel y posiciones empíricas para 10 años."""

import csv
import math

RUTA = "datos/muestra_dist10.csv"

with open(RUTA, "r", encoding="utf-8-sig", newline="") as archivo:
    filas = list(csv.DictReader(archivo))

x = sorted([float(fila["pmax24h_mm"]) for fila in filas])
n = len(x)
media = sum(x) / n
# La desviación estándar es muestral: se divide por n - 1.
desviacion = math.sqrt(sum((valor - media) ** 2 for valor in x) / (n - 1))

print("VERIFICACIÓN DISTRIBUCIONES - muestra_dist10.csv")
print(f"Media = {media:.4f}")
print(f"Desviación estándar muestral = {desviacion:.4f}")

for i, valor in enumerate(x, start=1):
    p_weibull = i / (n + 1)
    p_gringorten = (i - 0.44) / (n + 0.12)
    t_weibull = 1 / (1 - p_weibull)
    print(f"Orden {i:2d}: x = {valor:.4f}; Weibull = {p_weibull:.4f}; "
          f"T_empírica = {t_weibull:.4f}; Gringorten = {p_gringorten:.4f}")

# Gumbel por momentos: beta mide la escala y mu la ubicación.
beta = desviacion * math.sqrt(6.0) / math.pi
mu = media - 0.5772 * beta
print(f"Beta (Gumbel, momentos) = {beta:.4f}")
print(f"Mu (Gumbel, momentos) = {mu:.4f}")

for T in (10, 50, 100):
    variable_reducida = -math.log(-math.log(1.0 - 1.0 / T))
    x_t = mu + beta * variable_reducida
    print(f"x_T por momentos, T = {T:3d} años = {x_t:.4f}")

riesgo = 1.0 - (1.0 - 1.0 / 50.0) ** 25
print(f"Riesgo de falla, T = 50 y N = 25 = {riesgo:.4f}")
