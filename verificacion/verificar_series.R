# Verificación independiente de PM3, índices estacionales y métodos de referencia.

datos <- read.csv("datos/muestra_series24.csv", encoding = "UTF-8")
x <- datos$precipitacion_mm
meses <- datos$mes

cat("VERIFICACIÓN SERIES - muestra_series24.csv\n")
cat("PM3 de 2025 (ventana que termina en el mes actual):\n")
for (indice in which(datos$anio == 2025)) {
  ventana <- x[max(1, indice - 2):indice]
  pm3 <- if (length(ventana) == 3) mean(ventana) else NA
  cat(sprintf("%s: PM3 = %.4f\n", datos$fecha[indice], pm3))
}

media_general <- mean(x)
indices <- numeric(12)
for (mes in 1:12) indices[mes] <- mean(x[meses == mes]) - media_general
cat("Índices estacionales aditivos:\n")
for (mes in 1:12) cat(sprintf("Mes %2d = %.4f\n", mes, indices[mes]))
cat(sprintf("Suma de índices = %.4f\n", sum(indices)))

entrenamiento <- x[datos$conjunto == "entrenamiento"]
validacion <- x[datos$conjunto == "validacion"]
h <- length(validacion)
naive <- rep(tail(entrenamiento, 1), h)
# Mismos meses de junio a diciembre de 2024: posiciones 7:12 de la muestra.
estacional <- x[7:12]
promedio <- rep(mean(entrenamiento), h)

cat("Pronósticos julio-diciembre 2025:\n")
for (j in seq_len(h)) {
  cat(sprintf("%s: Real = %.4f; Ingenuo = %.4f; Estacional = %.4f; Promedio = %.4f\n",
              datos$fecha[18+j], validacion[j], naive[j], estacional[j], promedio[j]))
}

metodos <- list(Ingenuo = naive, "Estacional ingenuo" = estacional, Promedio = promedio)
resultados <- data.frame(Metodo = character(), MAE = numeric(), RMSE = numeric(), SMAPE = numeric())
for (nombre in names(metodos)) {
  pronostico <- metodos[[nombre]]
  errores <- abs(validacion - pronostico)
  mae <- mean(errores)
  rmse <- sqrt(mean((validacion - pronostico)^2))
  smape <- 200 * mean(errores / (abs(validacion) + abs(pronostico)))
  resultados <- rbind(resultados, data.frame(Metodo = nombre, MAE = mae, RMSE = rmse, SMAPE = smape))
}
cat("Métricas ordenadas por SMAPE:\n")
resultados <- resultados[order(resultados$SMAPE), ]
print(resultados, row.names = FALSE, digits = 4)
