# Verificación independiente del EDA; los cálculos usan funciones básicas de R.

datos <- read.csv("datos/muestra_eda10.csv", encoding = "UTF-8")
x <- datos$rendimiento
n <- length(x)
media <- mean(x)
mediana <- median(x)
varianza <- sum((x - media)^2) / (n - 1)
desviacion <- sqrt(varianza)
cv <- desviacion / media * 100
q <- quantile(x, probs = c(0.25, 0.75), type = 7, names = FALSE)
q1 <- q[1]; q3 <- q[2]; ric <- q3 - q1
inferior <- q1 - 1.5 * ric
superior <- q3 + 1.5 * ric
atipicos <- data.frame(parcela = datos$parcela[x < inferior | x > superior],
                       rendimiento = x[x < inferior | x > superior])

cat("VERIFICACIÓN EDA - muestra_eda10.csv\n")
cat(sprintf("n = %.4f\n", n))
cat(sprintf("Media = %.4f\n", media))
cat(sprintf("Mediana = %.4f\n", mediana))
cat(sprintf("Varianza muestral = %.4f\n", varianza))
cat(sprintf("Desviación estándar muestral = %.4f\n", desviacion))
cat(sprintf("CV (%%) = %.4f\n", cv))
cat(sprintf("Q1 tipo 7 = %.4f\n", q1))
cat(sprintf("Q3 tipo 7 = %.4f\n", q3))
cat(sprintf("RIC = %.4f\n", ric))
cat(sprintf("Valla inferior = %.4f\n", inferior))
cat(sprintf("Valla superior = %.4f\n", superior))
print(atipicos, row.names = FALSE)
cat("Media por riego:\n")
print(tapply(datos$rendimiento, datos$riego, mean), digits = 4)
