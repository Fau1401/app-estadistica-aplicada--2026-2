# Plantilla de comparación de resultados

Registre los resultados obtenidos a mano, con Python, con R y en la app. Marque "Sí" solo
cuando las diferencias numéricas estén dentro de la precisión indicada.

## EDA: `muestra_eda10.csv`

| Medida | A mano | Python | R | App | ¿Coincide? |
|---|---:|---:|---:|---:|---|
| n | | | | | |
| Media | | | | | |
| Mediana | | | | | |
| Varianza muestral | | | | | |
| Desviación estándar muestral | | | | | |
| CV (%) | | | | | |
| Q1 tipo 7 | | | | | |
| Q3 tipo 7 | | | | | |
| RIC | | | | | |
| Valla inferior de Tukey | | | | | |
| Valla superior de Tukey | | | | | |
| Atípicos | | | | | |
| Media con riego No | | | | | |
| Media con riego Sí | | | | | |

## Distribuciones: `muestra_dist10.csv`

| Medida | A mano | Python | R | App | ¿Coincide? |
|---|---:|---:|---:|---:|---|
| β de Gumbel por momentos | | | | | |
| μ de Gumbel por momentos | | | | | |
| xT T = 10 años | | | | | |
| xT T = 50 años | | | | | |
| xT T = 100 años | | | | | |
| Riesgo T = 50, N = 25 | | | | | |
| Posiciones de Weibull | | | | | |
| T empírica | | | | | |

## Regresión: `muestra_reg8.csv`

| Medida | A mano | Python | R | App | ¿Coincide? |
|---|---:|---:|---:|---:|---|
| Sxx | | | | | |
| Syy | | | | | |
| Sxy | | | | | |
| r de Pearson | | | | | |
| rho de Spearman | | | | | |
| b0 | | | | | |
| b1 | | | | | |
| SCE | | | | | |
| R² | | | | | |
| RSE | | | | | |
| SE(b1) | | | | | |
| Estadístico t | | | | | |
| p-valor | | | | | |
| IC 95 % de b1 | | | | | |
| Decisión H0: β1 = 0 | | | | | |

## Series: `muestra_series24.csv`

| Medida | A mano | Python | R | App | ¿Coincide? |
|---|---:|---:|---:|---:|---|
| PM3 de julio-diciembre de 2025 | | | | | |
| Índices estacionales de los 12 meses | | | | | |
| Suma de índices estacionales | | | | | |
| Pronóstico ingenuo | | | | | |
| Pronóstico estacional ingenuo | | | | | |
| Pronóstico promedio | | | | | |
| MAE por método | | | | | |
| RMSE por método | | | | | |
| SMAPE por método | | | | | |
| Método ganador | | | | | |

## ¿Se cumplió mi predicción previa?

Escriba aquí si los valores calculados manualmente coincidieron con Python, R y la app, antes
de revisar las posibles diferencias numéricas.

## Diferencias encontradas y su causa

Registre cualquier diferencia y explique si fue por redondeo, tipo de cuantiles, número de
decimales, criterio de desviación muestral, ajuste automático o interpretación del método.
