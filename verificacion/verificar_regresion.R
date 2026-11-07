# Verificación independiente con fórmulas explícitas, lm() y summary().

datos <- read.csv("datos/muestra_reg8.csv", encoding = "UTF-8")
x <- datos$lamina_riego
y <- datos$rendimiento
n <- length(x)
x_bar <- mean(x); y_bar <- mean(y)
dx <- x - x_bar; dy <- y - y_bar
sxx <- sum(dx^2); syy <- sum(dy^2); sxy <- sum(dx * dy)
r <- sxy / sqrt(sxx * syy)
rho <- cor(x, y, method = "spearman")
b1 <- sxy / sxx
b0 <- y_bar - b1 * x_bar
ajustados <- b0 + b1 * x
residuos <- y - ajustados
sce <- sum(residuos^2)
scr <- sum((ajustados - y_bar)^2)
sct <- syy
r2 <- 1 - sce / sct
rse <- sqrt(sce / (n - 2))
se_b1 <- rse / sqrt(sxx)
t <- b1 / se_b1
gl <- n - 2
tcritico <- qt(0.975, df = gl)
p_valor <- 2 * pt(-abs(t), df = gl)
ic <- b1 + c(-1, 1) * tcritico * se_b1
decision <- if (p_valor < 0.05) "Se rechaza H0" else "No se rechaza H0"

cat("VERIFICACIÓN REGRESIÓN - muestra_reg8.csv\n")
medidas <- c(n, sxx, syy, sxy, r, rho, b0, b1, sce, scr, sct, r2,
             rse, se_b1, t, tcritico, p_valor, ic[1], ic[2])
nombres <- c("n","Sxx","Syy","Sxy","r Pearson","rho Spearman","b0","b1",
             "SCE","SCR","SCT","R²","RSE","SE(b1)","t",
             "t crítico bilateral","p-valor","IC95 inferior","IC95 superior")
for (i in seq_along(medidas)) cat(sprintf("%s = %.4f\n", nombres[i], medidas[i]))
cat(sprintf("Decisión al 5 %% = %s\n", decision))

modelo <- lm(rendimiento ~ lamina_riego, data = datos)
cat("Resumen de lm():\n")
print(summary(modelo), digits = 4)
