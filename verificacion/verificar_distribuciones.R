# Verificación independiente de posiciones empíricas y Gumbel por momentos.

datos <- read.csv("datos/muestra_dist10.csv", encoding = "UTF-8")
x <- sort(datos$pmax24h_mm)
n <- length(x)
media <- mean(x)
desviacion <- sd(x)

cat("VERIFICACIÓN DISTRIBUCIONES - muestra_dist10.csv\n")
cat(sprintf("Media = %.4f\n", media))
cat(sprintf("Desviación estándar muestral = %.4f\n", desviacion))
for (i in seq_len(n)) {
  p_weibull <- i / (n + 1)
  p_gringorten <- (i - 0.44) / (n + 0.12)
  t_empirica <- 1 / (1 - p_weibull)
  cat(sprintf("Orden %2d: x = %.4f; Weibull = %.4f; T_empírica = %.4f; Gringorten = %.4f\n",
              i, x[i], p_weibull, t_empirica, p_gringorten))
}

beta <- desviacion * sqrt(6) / pi
mu <- media - 0.5772 * beta
cat(sprintf("Beta (Gumbel, momentos) = %.4f\n", beta))
cat(sprintf("Mu (Gumbel, momentos) = %.4f\n", mu))
for (T in c(10, 50, 100)) {
  y <- -log(-log(1 - 1 / T))
  x_t <- mu + beta * y
  cat(sprintf("x_T por momentos, T = %3d años = %.4f\n", T, x_t))
}
riesgo <- 1 - (1 - 1 / 50)^25
cat(sprintf("Riesgo de falla, T = 50 y N = 25 = %.4f\n", riesgo))

# Ajuste por máxima verosimilitud opcional en Posit Cloud.
# Instalar una vez con:
# install.packages(c("fitdistrplus", "evd"))
if (requireNamespace("fitdistrplus", quietly = TRUE)) {
  cat("fitdistrplus disponible. Ajuste Gumbel pendiente si la distribución 'gum' es compatible.\n")
  ajuste <- try(fitdistrplus::fitdist(x, "gum", start = list(loc = media, scale = beta)), silent = TRUE)
  if (!inherits(ajuste, "try-error")) print(ajuste$estimate, digits = 4)
} else {
  cat("fitdistrplus no está instalado. En Posit Cloud: install.packages('fitdistrplus').\n")
}
if (requireNamespace("evd", quietly = TRUE)) {
  ajuste_evd <- try(evd::gumbel.fit(x), silent = TRUE)
  if (!inherits(ajuste_evd, "try-error")) {
    cat("Estimaciones de máxima verosimilitud con evd (loc, scale):\n")
    print(ajuste_evd$estimate, digits = 4)
  }
} else {
  cat("evd no está instalado. En Posit Cloud: install.packages('evd').\n")
}
