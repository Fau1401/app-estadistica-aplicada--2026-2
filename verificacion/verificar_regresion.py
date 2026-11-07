"""Verificación independiente de regresión simple para las 8 parcelas."""

import csv
import math
from scipy import stats

RUTA = "datos/muestra_reg8.csv"
with open(RUTA, "r", encoding="utf-8-sig", newline="") as archivo:
    filas = list(csv.DictReader(archivo))
x = [float(fila["lamina_riego"]) for fila in filas]
y = [float(fila["rendimiento"]) for fila in filas]
n = len(x)
x_bar = sum(x) / n
y_bar = sum(y) / n
dx = [valor - x_bar for valor in x]
dy = [valor - y_bar for valor in y]
sxx = sum(valor * valor for valor in dx)
syy = sum(valor * valor for valor in dy)
sxy = sum(a * b for a, b in zip(dx, dy))

r = sxy / math.sqrt(sxx * syy)
rank_x = stats.rankdata(x, method="average").tolist()
rank_y = stats.rankdata(y, method="average").tolist()
rank_x_bar = sum(rank_x) / n
rank_y_bar = sum(rank_y) / n
rho = sum((a-rank_x_bar)*(b-rank_y_bar) for a, b in zip(rank_x, rank_y)) / math.sqrt(
    sum((a-rank_x_bar)**2 for a in rank_x) * sum((b-rank_y_bar)**2 for b in rank_y))
b1 = sxy / sxx
b0 = y_bar - b1 * x_bar
ajustados = [b0 + b1 * valor for valor in x]
residuos = [valor_real - valor_ajustado for valor_real, valor_ajustado in zip(y, ajustados)]
sce = sum(valor * valor for valor in residuos)
scr = sum((valor_ajustado-y_bar)**2 for valor_ajustado in ajustados)
sct = syy
r2 = 1 - sce / sct
rse = math.sqrt(sce / (n - 2))
se_b1 = rse / math.sqrt(sxx)
t = b1 / se_b1
gl = n - 2
tcritico = stats.t.ppf(0.975, gl)
p_valor = 2 * stats.t.sf(abs(t), gl)
limite_inferior = b1 - tcritico * se_b1
limite_superior = b1 + tcritico * se_b1
decision = "Se rechaza H0" if p_valor < 0.05 else "No se rechaza H0"

print("VERIFICACIÓN REGRESIÓN - muestra_reg8.csv")
for nombre, valor in [
    ("n", n), ("Sxx", sxx), ("Syy", syy), ("Sxy", sxy), ("r Pearson", r),
    ("rho Spearman", rho), ("b0", b0), ("b1", b1), ("SCE", sce),
    ("SCR", scr), ("SCT", sct), ("R²", r2), ("RSE", rse),
    ("SE(b1)", se_b1), ("t", t), ("t crítico bilateral", tcritico),
    ("p-valor", p_valor), ("IC95 inferior", limite_inferior),
    ("IC95 superior", limite_superior),
]:
    if nombre == "n":
        print(f"{nombre} = {valor:.4f}")
    else:
        print(f"{nombre} = {valor:.4f}")
print(f"Decisión al 5 % = {decision}")
