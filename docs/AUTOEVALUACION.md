# Autoevaluación técnica del proyecto final

## Alcance de la revisión

Se revisaron la estructura del repositorio, los módulos de `src/`, las seis páginas de Streamlit, las pruebas unitarias, los scripts independientes de `verificacion/`, las muestras de `datos/` y el comportamiento de arranque. No se modificó código, datos ni archivos de configuración.

Las pruebas ejecutadas fueron:

- `.venv/bin/python -m pytest -q`: **4 pruebas aprobadas**.
- Los cuatro scripts de `verificacion/`: ejecutados y sin errores.
- Compilación de `app.py`, `pages/`, `src/` y `verificacion/`: sin errores de sintaxis.
- Arranque de Streamlit con `.venv/bin/streamlit run app.py`: servidor disponible y rutas principales con respuesta HTTP 200.
- `AppTest` para la página principal y las cinco páginas interiores: **sin excepciones de renderizado inicial**.

La verificación HTTP y `AppTest` no sustituyen una interacción manual completa con todos los controles, cargas de archivos y ejecuciones costosas de AutoTS.

## 1. Organización del proyecto y modularidad

**Evaluación: buena, con estructura clara.**

La separación entre interfaz y cálculo es adecuada:

- `app.py` contiene la página principal.
- `pages/` contiene la interfaz de las seis vistas, incluida la página de inicio.
- `src/datos.py`, `src/eda.py`, `src/distribuciones.py`, `src/regresion.py`, `src/series.py`, `src/modelos_curvas.py`, `src/validacion.py` y `src/exportar.py` separan responsabilidades reutilizables.
- `tests/` contiene pruebas de coincidencia entre cálculos independientes.
- `verificacion/` contiene cálculos manuales o independientes.
- `datos/` contiene las fuentes simuladas y las muestras pequeñas.

La organización permite localizar y reutilizar funciones. Los módulos estadísticos tienen nombres coherentes con su función y las páginas llaman funciones de `src/`, en vez de concentrar toda la lógica en la interfaz.

Existen aspectos susceptibles de mejora:

- Varias páginas tienen archivos extensos, con una mezcla de validación, presentación, cálculos auxiliares y exportación.
- La validación del estado de los datos se repite parcialmente entre páginas, aunque el módulo `src/validacion.py` ya ofrece ayudas comunes.
- La configuración visual de unidades aparece de forma distribuida entre `src/` y las páginas.
- Hay utilidades de salida, tablas y gráficos en la interfaz que podrían seguir separándose más claramente de la lógica estadística.

## 2. Claridad de comentarios y docstrings

**Evaluación: buena.**

Los módulos principales incluyen docstrings en español que explican propósito, fórmulas y unidades. Los comentarios también suelen aportar información relevante, por ejemplo:

- El método tipo 7 para cuartiles.
- La diferencia entre desviación estándar poblacional y muestral.
- La parametrización de la GEV en SciPy.
- La definición de AIC, BIC y AICc.
- La interpretación de residuales y pruebas de supuestos.
- El rezago estacional de doce meses.

Las funciones tienen nombres descriptivos y el código separa operaciones de cálculo, presentación y validación. Los resultados se acompañan frecuentemente por unidades.

No obstante, persisten dos detalles:

- Algunas rutas usan comentarios breves o nombres variables únicamente, sin explicar decisiones estadísticas complejas.
- La interfaz contiene texto explicativo amplio dentro de los scripts; eso favorece la comprensión, pero también hace que los archivos sean más extensos y difíciles de mantener.

## 3. Correctitud estadística por página

### Inicio

La página principal presenta metadatos del estudiante, navegación, propósito, metodología y advertencias. No realiza cálculos estadísticos propios. Su funcionamiento general es correcto en el arranque observado.

### Datos

La carga de archivos CSV y Excel es razonable. Se clasifican tipos y se muestran filas, columnas y valores faltantes. Los archivos `datos/*.csv` se leen sin alterar su fuente.

Se deben supervisar estos riesgos:

- Las variables de fecha solo se identifican por contener la palabra “fecha”; formatos temporales con otros nombres podrían quedar como texto.
- El usuario puede cargar archivos con unidades o rangos no descritos; la aplicación advierte sobre la necesidad de verificar el origen, lo cual es apropiado.
- Los formatos de lectura pueden depender de la codificación o del separador de archivos CSV externos.

### EDA

**Estado general: correcto para los cálculos revisados.**

En `src/eda.py`:

- La varianza usa `ddof=1`, por lo que corresponde a la varianza muestral.
- La desviación estándar usa igualmente `ddof=1`.
- Los cuartiles utilizan el método predeterminado de pandas, equivalente al tipo 7 o `method="linear"`.
- Las vallas de Tukey se calculan con `Q1 - 1.5RIC` y `Q3 + 1.5RIC`.
- La frecuencia relativa divide cada conteo entre el total válido.
- Las correlaciones y gráficos usan los filtros aplicados a la misma muestra.

El script independiente confirma:

- Varianza muestral: `15.0212`.
- Desviación estándar muestral: `3.8757`.
- Q1 tipo 7: `25.3875`.
- Q3 tipo 7: `29.2715`.
- Sin valores atípicos en la muestra de diez registros.

Coinciden los cálculos independientes y la prueba automatizada.

Puntos por supervisar:

- Si `n=1`, la desviación y varianza se fijan en cero, decisión conservadora por falta de muestra para estimar dispersión.
- El EDA utiliza media y desviación con valores completos pero no informa una prueba formal de normalidad en todas las variables.
- La matriz de correlación de Pearson podría interpretarse como causalidad si el estudiante no supervisa su lectura.

### Distribuciones

**Estado general estadísticamente correcto para los cálculos principales revisados, con una mejora importante sobre consistencia y reproducibilidad.**

El conteo de parámetros es correcto:

- Normal: 2 parámetros libres.
- Gumbel: 2 parámetros libres.
- Lognormal, Gamma y Weibull con ubicación fijada en cero: 2 parámetros libres.
- GEV: 3 parámetros libres.

La implementación usa:

\[
AIC=2k-2\ell,\qquad BIC=k\ln(n)-2\ell,\qquad
AICc=AIC+\frac{2k(k+1)}{n-k-1}
\]

La corrección está presente y el denominador se protege cuando `n-k-1 <= 0`. Para modelos positivos, el ajuste fija `loc=0`, y el usuario debería distinguir ese supuesto de distribuciones con ubicación libre.

La posición empírica Weibull usa `i/(n+1)`; Gringorten usa `(i-0.44)/(n+0.12)`. El período de retorno usa `T=1/(1-p)`. El cuantíl usa correctamente la probabilidad acumulada `F(x_T)=1-1/T`.

El riesgo usa correctamente:

\[
R=1-(1-1/T)^N
\]

En la muestra, el resultado es aproximadamente `0.3965` para `T=50` y `N=25`.

#### Parámetro de forma de la GEV

La librería SciPy usa `c=-xi`, donde `xi` es el índice clásico de forma de la teoría de valores extremos. El comentario de `src/distribuciones.py` y el uso directo de `stats.genextreme.ppf()` son coherentes: el cálculo no aplica manualmente un signo contrario. No obstante, la interfaz debería informar explícitamente que el número mostrado corresponde a `c` de SciPy y mostrar la equivalencia `xi=-c`. Sin esa conversión visible existe riesgo de interpretación incorrecta, aunque no se encontró un error numérico en el cálculo directo.

#### Valores p Monte Carlo

`bondad_ajuste()` usa `stats.goodness_of_fit` para KS y Anderson-Darling, simulando muestras bajo el modelo ajustado. También informa un KS ingenuo como referencia. Para Lognormal, Gamma y Weibull, `loc=0` se registra como parámetro conocido; los demás parámetros se reestiman.

Los valores p Monte Carlo son simulados; pueden cambiar entre ejecuciones si no se fija una semilla. La página tampoco fija una semilla propia para la bondad de ajuste. Esto afecta la reproducibilidad y podría generar decisiones algo distintas al cambiar la muestra simulada.

También se muestra el valor p KS ingenuo, que no corrige completamente por haber estimado parámetros con los mismos datos. La interfaz lo distingue con claridad del valor p Monte Carlo, lo cual es apropiado.

#### Modelos de secado

Los modelos Lewis, Henderson-Pabis, Page, Logarítmico y Dos términos están definidos correctamente en sus ecuaciones. Las curvas se ajustan con mínimos cuadrados no lineales mediante `curve_fit`. El código estima `k` como el número de parámetros ajustados y calcula AICc de acuerdo con la fórmula por tamaño de muestra.

La métrica χ² reducida divide la suma ponderada por `n-k`, y `RMSE` se calcula con `SCE/n`. Estas convenciones son plausibles y deben explicarse en el reporte por estar asociadas al método empleado.

### Regresión

**Estado general: correcto para regresión simple y concordante con los cálculos independientes.**

En `calculo_manual()`:

- `b1=Sxy/Sxx`.
- `b0=ȳ-b1·x̄`.
- `RSE=sqrt(SCE/(n-2))`.
- `SE(b1)=RSE/sqrt(Sxx)`.
- La prueba bilateral usa `df=n-2`.
- Los intervalos de pendiente usan el cuantil t bilateral al 95 %.

La muestra independiente produce `RSE=2.2737`, con `n=8`, `n-2=6`, y el valor coincide con statsmodels. Los gráficos de residuos están alineados con las variables calculadas por el modelo.

El diagnóstico incluye Shapiro-Wilk y Breusch-Pagan. Es importante leer los p-valores con cautela:

- En Shapiro-Wilk, un p-valor bajo aporta evidencia contra normalidad.
- En Breusch-Pagan, un p-valor bajo aporta evidencia contra homocedasticidad.

La página explica ambas decisiones, pero en la lógica no se muestran algunas salidas estadísticas más completas para todos los supuestos, por ejemplo influencia, distancia de Cook, colinealidad o pruebas adicionales.

Para regresión múltiple:

- Se eliminan faltantes por lista de variables usada.
- statsmodels construye la fórmula y calcula intervalos.
- No se verifica explícitamente en la página colinealidad, tamaño de muestra relativo al número de predictores ni rango adecuado de predicciones.
- La selección manual de variables permite modelos redundantes o sobreajustados.

### Series de tiempo

**Estado general: correcto para los cálculos de referencia revisados.**

El promedio móvil usa una ventana terminal de tres observaciones. En diciembre de 2025 muestra `172.5967` para la muestra de 24 meses; coincide con el script independiente.

Los índices estacionales aditivos se calculan como media mensual menos media general. Para un ciclo completo de doce meses, se centra la suma para que sea exactamente cero dentro del redondeo. Esto es apropiado para descomposición aditiva y evita desbalance numérico.

La descomposición usa periodo de doce meses.

El estacional ingenuo usa el mismo mes doce meses atrás, mediante `fecha - DateOffset(years=1)`. Si falta esa fecha, la implementación usa el último dato como alternativa transparente. Para la muestra completa, el rezago es efectivamente doce meses.

Las métricas implementan:

\[
MAE=\frac1h\sum|e_i|,\qquad
RMSE=\sqrt{\frac1h\sum e_i^2},\qquad
SMAPE=200\frac1h\sum\frac{|e_i|}{|y_i|+|\hat y_i|}
\]

La implementación coincide con las fórmulas solicitadas. Para pares reales y pronosticados ambos iguales a cero, asigna cero al término para evitar `0/0`; es una extensión razonable.

La validación de la aplicación usa los últimos doce meses como conjunto de prueba y los registros previos como entrenamiento. La verificación independiente emplea una partición marcada de 18/6 meses y obtiene:

- Estacional ingenuo: MAE `27.6833`, RMSE `30.2731`, SMAPE `27.7792`.
- Ingenuo: SMAPE `54.6281`.
- Promedio: SMAPE `55.1958`.
- Método ganador independiente: Estacional ingenuo.

El pronóstico AutoTS admite semilla derivada del código estudiantil, horizonte configurable, lista rápida o rápida automática y banda de intervalo. La semilla mejora reproducibilidad, pero el rendimiento real depende de la combinación AutoTS disponible, del tamaño de la búsqueda y de los datos históricos.

Puntos por supervisar:

- La división temporal fija para referencia evita mezclar validación con entrenamiento, pero no constituye validación cruzada temporal completa.
- AutoTS puede requerir una ejecución prolongada y no garantiza el óptimo global.
- Las bandas pueden estar basadas en el mecanismo propio de AutoTS; no deben interpretarse como intervalos de confianza clásicos sin revisar su documentación o cobertura.

## 4. Funcionamiento de cada página

### Página Inicio

- Renderiza sin excepciones en `AppTest`.
- Responde HTTP 200 mediante Streamlit.
- Muestra navegación y metodología.
- No ejecuta cálculos pesados al cargar.

### Página Datos

- Renderiza sin excepciones.
- Permite seleccionar los conjuntos disponibles.
- Presenta vista previa, tipos y faltantes.
- La carga de archivo propio fue revisada en código; la interacción real con carga mediante navegador se considera parte de una prueba manual pendiente.

### Página EDA

- Renderiza sin excepciones con los datos incluidos.
- Los filtros del sidebar reconstruyen tablas y gráficos.
- Los cálculos n-1 y tipo 7 coinciden con el script independiente.
- Las exportaciones están integradas en el mismo flujo, pero no se verificó manualmente la descarga de PDF, PNG y Excel en navegador.

### Página Distribuciones

- Renderiza sin excepciones con los datos incluidos.
- Ejecuta ajustes y 199 simulaciones Monte Carlo en el estado predeterminado observado.
- Las rutas de exportación están disponibles.
- No se ejecutó manualmente un ajuste presionando controles durante la autoevaluación; `AppTest` solamente realizó la carga inicial.
- Se recomienda una prueba manual de todos los modelos seleccionados, sobre todo GEV, y una prueba con tamaños pequeños para observar el comportamiento de AICc indefinido.

### Página Regresión

- Renderiza sin excepciones.
- Correlación, regresión simple, cálculos manuales y regresiones múltiples están disponibles.
- El cálculo independiente coincide con la implementación manual.
- No se probaron manualmente todas las interacciones de selección y descarga.

### Página Series de tiempo

- Renderiza sin excepciones.
- Explora las dos variables definidas.
- Ejecuta descomposición, índices, validación y muestra de verificación.
- AutoTS no se ejecutó durante la revisión para evitar esperar una búsqueda costosa; su ejecución fue revisada como integración de código y botón.

### Resultados globales

- Las seis rutas principales responden HTTP 200.
- Las seis cargas iniciales ejecutadas con `AppTest` no presentan excepciones.
- Las cuatro pruebas unitarias pasan.
- Los cuatro scripts independientes pasan.

## 5. Coincidencia entre las secciones de verificación de la app y `verificacion/`

| Página | Muestra | Coincidencia | Observación |
|---|---|---:|---|
| EDA | `muestra_eda10.csv` | Alta | Media, mediana, varianza, desviación, cuartiles, RIC y atípicos usan las mismas fórmulas y pasan la prueba automatizada. |
| Distribuciones | `muestra_dist10.csv` | Parcial | La app y el script coinciden en media, desviación muestral, posiciones Weibull/Gringorten, Gumbel por momentos, cuantiles de retorno y riesgo. |
| Regresión | `muestra_reg8.csv` | Alta | Sxx, Sxy, pendiente, R² y RSE coinciden; la prueba automatizada valida varios resultados contra el script. |
| Series | `muestra_series24.csv` | Alta | Promedio móvil, índices, pronósticos, SMAPE y ganador coinciden con el script independiente. |

Existen diferencias de alcance, no necesariamente contradicciones:

- `verificacion/verificar_distribuciones.py` no incluye todas las fórmulas de AIC/BIC/AICc, bondad Monte Carlo, bootstrap ni comparación de todas las distribuciones.
- No contiene una comprobación independiente explícita del parámetro de forma `c=-xi` de GEV.
- `verificacion/verificar_regresion.py` verifica regresión simple, pero no verifica regresión múltiple, intervalos del modelo statsmodels ni los p-valores Shapiro/Breusch-Pagan.
- La verificación independiente de series usa `x[6:12]` para el estacional ingenuo, mientras la app utiliza la identificación explícita por fecha restando doce meses. Ambos producen el mismo resultado en la muestra con fechas completas.
- Las pruebas unitarias ya detectan coincidencia EDA, Gumbel, regresión simple y el ganador estacional; no cubren todas las funciones de distribución o el módulo AutoTS.

## 6. Lista priorizada de correcciones

### Crítica

- No se identificó una corrección estadística crítica en las fórmulas verificadas: varianza n-1, cuartiles tipo 7, AIC/BIC/AICc, RSE con n-2, SMAPE, estacional de doce meses y rezago estacional son consistentes.

### Importante

1. **Fijar una semilla reproducible para las simulaciones KS y Anderson-Darling Monte Carlo.**
   Los p-valores pueden variar entre ejecuciones. La página debe permitir una semilla y usarla en los dos procedimientos.

2. **Distinguir claramente en la interfaz el parámetro `c` de SciPy y el índice clásico `xi=-c` de la GEV.**
   La implementación es numéricamente coherente, pero una etiqueta ambigua puede producir interpretaciones incorrectas.

3. **Ampliar el alcance independiente de las verificaciones de distribuciones.**
   Falta una verificación independiente de `k`, AIC, BIC, AICc, el p-valor Monte Carlo, el bootstrap y la parametrización GEV.

4. **Ampliar las verificaciones automatizadas de regresión y series.**
   Agregar pruebas para regresión múltiple, residuos, intervalos, criterios de secado, descomposición y particiones temporales distintas.

5. **Revisar la consistencia entre el selector del modelo recomendado y AICc.**
   Para máximos anuales, la selección mostrada prioriza respaldo físico, p-valor, delta AIC y simplicidad. Cuando dos modelos tienen delta AIC pequeño pero distinto AICc, conviene declarar explícitamente qué criterio decide el empate.

6. **Documentar expresamente el supuesto de estacionariedad, independencia y tamaño mínimo.**
   Las páginas tienen controles y validaciones parciales, pero una interpretación responsable debe insistir en que el pronóstico y el ajuste de extremos no eliminan supuestos por sí solos.

### Deseable

1. Reemplazar gradualmente los usos obsoletos de `use_container_width=True` por el parámetro moderno recomendado por Streamlit.

2. Añadir un indicador de tiempo transcurrido, estado y cancelación durante AutoTS.

3. Agregar pruebas manuales o automatizadas para carga de CSV/Excel y descargas PNG/PDF/XLSX.

4. Añadir advertencias ante regresiones con pocas observaciones, muchos predictores, predicciones fuera del rango observado y datos con colinealidad.

5. Incorporar pruebas adicionales de independencia temporal, estacionariedad, heterocedasticidad avanzada y validación cruzada temporal.

6. Hacer explícito qué resultados de Monte Carlo usan semillas locales y cuáles son aleatorios.

7. Mejorar la separación entre presentación y cálculos de las páginas más largas, especialmente distribuciones y series.

8. Unificar el formato de nombres, unidades y mensajes entre todas las páginas.

9. Registrar las versiones exactas usadas para ejecutar el proyecto y las limitaciones de AutoTS.

10. Crear una prueba de extremo a extremo que abra las páginas y active los controles principales sin ejecutar búsquedas AutoTS innecesariamente largas.

## Conclusión

El proyecto presenta una organización modular clara y una separación adecuada entre datos, lógica estadística, interfaz y verificaciones. Los cálculos revisados son compatibles con las fórmulas solicitadas y las pruebas existentes pasan.

La autoevaluación no encuentra un defecto crítico de fórmula en las áreas solicitadas. Las mejoras prioritarias son reproducibilidad Monte Carlo, claridad de la parametrización GEV, ampliación de verificaciones independientes y mayor cobertura de regresión múltiple, validación temporal y controles estadísticos adicionales.
