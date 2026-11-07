"""Verificación independiente de promedios móviles, índices y pronósticos de referencia."""

import csv
import math

RUTA = "datos/muestra_series24.csv"
with open(RUTA, "r", encoding="utf-8-sig", newline="") as archivo:
    filas = list(csv.DictReader(archivo))

x = [float(fila["precipitacion_mm"]) for fila in filas]
meses = [int(fila["mes"]) for fila in filas]

print("VERIFICACIÓN SERIES - muestra_series24.csv")
print("PM3 de 2025 (ventana que termina en el mes actual):")
for fila, valor in zip(filas, x):
    if int(fila["anio"]) == 2025:
        indice = filas.index(fila)
        ventana = x[max(0, indice - 2):indice + 1]
        pm3 = sum(ventana) / len(ventana) if len(ventana) == 3 else float("nan")
        print(f"{fila['fecha']}: PM3 = {pm3:.4f}")

media_general = sum(x) / len(x)
indices = {}
for mes in range(1, 13):
    valores_mes = [valor for valor, mes_actual in zip(x, meses) if mes_actual == mes]
    indices[mes] = sum(valores_mes) / len(valores_mes) - media_general

print("Índices estacionales aditivos:")
for mes in range(1, 13):
    print(f"Mes {mes:2d} = {indices[mes]:.4f}")
print(f"Suma de índices = {sum(indices.values()):.4f}")

entrenamiento = [valor for fila, valor in zip(filas, x) if fila["conjunto"] == "entrenamiento"]
validacion = [valor for fila, valor in zip(filas, x) if fila["conjunto"] == "validacion"]
h = len(validacion)
naive = [entrenamiento[-1] for _ in range(h)]
estacional = x[6:12]
promedio = [sum(entrenamiento) / len(entrenamiento) for _ in range(h)]
metodos = {
    "Ingenuo": naive,
    "Estacional ingenuo": estacional,
    "Promedio": promedio,
}

print("Pronósticos julio-diciembre 2025:")
for fila, real in zip(filas[18:24], validacion):
    print(f"{fila['fecha']}: Real = {real:.4f}; "
          f"Ingenuo = {naive[int(fila['periodo'])-19]:.4f}; "
          f"Estacional = {estacional[int(fila['periodo'])-19]:.4f}; "
          f"Promedio = {promedio[int(fila['periodo'])-19]:.4f}")

resultados = []
for nombre, pronostico in metodos.items():
    errores = [abs(real - pred) for real, pred in zip(validacion, pronostico)]
    cuadrados = [error * error for error in errores]
    mae = sum(errores) / h
    rmse = math.sqrt(sum(cuadrados) / h)
    smape = 200 * sum(
        abs(real - pred) / (abs(real) + abs(pred))
        for real, pred in zip(validacion, pronostico)
    ) / h
    resultados.append((nombre, mae, rmse, smape))

print("Métricas ordenadas por SMAPE:")
for nombre, mae, rmse, smape in sorted(resultados, key=lambda fila: fila[3]):
    print(f"{nombre}: MAE = {mae:.4f}; RMSE = {rmse:.4f}; SMAPE = {smape:.4f}")
