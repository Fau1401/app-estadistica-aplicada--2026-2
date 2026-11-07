# Plan de desarrollo de la aplicación

## Objetivo

Construir una aplicación multipágina en Streamlit para que estudiantes de Ingeniería Agrícola puedan cargar o explorar datos, realizar análisis exploratorios, ajustar distribuciones y modelos de regresión, analizar series de tiempo y verificar los cálculos mediante pruebas reproducibles.

La aplicación debe separar la interfaz de usuario, la lógica estadística y las utilidades de datos para facilitar su mantenimiento, pruebas y comprensión académica.

## Criterios generales de diseño

- Usar Streamlit para la navegación multipágina y los controles interactivos.
- Presentar unidades, significado agrícola y supuestos estadísticos junto a cada resultado.
- Mostrar mensajes claros cuando los datos sean insuficientes, tengan valores faltantes, estén fuera del dominio esperado o no cumplan un supuesto mínimo.
- Mantener copias de los resultados numéricos en tablas descargables cuando sea útil.
- Mostrar siempre un tamaño de muestra, el período cubierto y los datos excluidos o transformados.
- Registrar las versiones y paquetes relevantes de forma reproducible, sin mezclar esas decisiones con el código estadístico.

## Páginas y funciones

| Página | Función principal | Entradas principales | Tablas que muestra | Gráficas que muestra |
|---|---|---|---|---|
| Inicio | Presentar el propósito, navegación y estado general de la aplicación. | Base de datos cargada, configuración global opcional. | Resumen de archivos disponibles, variables detectadas y estado de validación. | Vista previa mínima o mapa visual de la navegación, sin análisis estadístico complejo. |
| Datos | Cargar, validar, seleccionar y preparar conjuntos de datos. | Archivo CSV o XLSX; separador y codificación para CSV; hoja para XLSX; selección de variables; tratamiento de faltantes; filtros de fecha o categoría. | Vista previa, tipos inferidos, estadísticos básicos, faltantes, duplicados y registro de transformaciones. | Perfil de faltantes, histogramas o diagramas según las variables elegidas. |
| EDA | Explorar distribuciones, relaciones y patrones antes del análisis formal. | Conjunto de datos ya cargado; variables numéricas y categóricas; opciones de agrupamiento, filtros y número de clases. | Resumen numérico, frecuencias, conteos por grupo, matriz de correlación y detección de valores atípicos. | Histogramas, diagramas de caja, densidades, series simples, gráficos de dispersión y matriz de gráficos. |
| Distribuciones | Ajustar modelos de probabilidad a la precipitación máxima anual y comparar alternativas. | Serie anual; unidad; modelo: Normal, Lognormal, Gamma, Weibull, Gumbel o GEV; método de ajuste; nivel de significancia; retornos y horizonte deseado. | Parámetros estimados, intervalos o incertidumbre, estadísticas KS y Anderson-Darling, valores críticos o p-valores, AIC, BIC, AICc y tabla comparativa de modelos; también tabla de período de retorno y riesgo. | Histograma con densidades ajustadas, función de distribución empírica y ajustada, QQ-plot, PP-plot, probabilidades y bandas de incertidumbre; curva altura/precipitación versus período de retorno. |
| Distribuciones: secado | Ajustar y comparar modelos de secado en capa delgada. | Conjunto tiempo-humedad; variable dependiente, tiempo, tratamientos o condiciones; modelos disponibles y validación o partición. | Parámetros de cada modelo, número de parámetros, log-verosimilitud, SSE/RMSE, AICc y tabla de clasificación por modelo. | Razón de humedad observada y ajustada frente al tiempo; residuos frente a tiempo o ajustes; comparación superpuesta de curvas. |
| Regresión | Estimar relaciones entre variables continuas y evaluar modelos lineales simples. | Variable respuesta; variable explicativa; nivel de confianza; tratamiento de faltantes; opción para excluir o destacar observaciones. | Estadísticos descriptivos, correlaciones Pearson y Spearman, coeficientes MCO, errores estándar, estadísticos t y intervalos de confianza, R² y R² ajustado, ANOVA y diagnóstico de residuos. | Dispersión con recta ajustada, intervalo de confianza e intervalo de predicción; residuos versus ajustados; QQ-plot, histograma de residuos y escala-localización; análisis de influencia opcional. |
| Series de tiempo | Analizar tendencia, estacionalidad y pronosticar una serie temporal. | Frecuencia temporal, variable objetivo, fecha inicial o índice temporal, horizonte de pronóstico, período de validación, estacionalidad esperada y método AutoTS. | Componentes estimados, promedios móviles, índices estacionales, métricas MAE, RMSE y SMAPE, comparación de métodos de referencia, modelos candidatos y pronóstico con intervalos. | Serie original, componentes tendencia-estacional-residual, promedios móviles, perfil estacional, descomposición clásica, observados versus ajustados y pronóstico con bandas de incertidumbre. |

## Cálculos estadísticos por página

### Inicio

- Verificar si existen datos cargados y si las variables requeridas están disponibles.
- Contar registros, variables, fechas válidas y faltantes sin modificar la fuente original.
- Presentar el flujo recomendado de uso y enlaces de navegación.

### Datos

- Inferir tipos de datos y convertir columnas seleccionadas a numéricas, categóricas o temporales.
- Calcular conteos de registros, valores únicos, faltantes, duplicados y rangos.
- Calcular estadísticos descriptivos como media, mediana, desviación estándar, mínimo, máximo, cuartiles, sesgo y curtosis cuando sean aplicables.
- Crear filtros y agregaciones sin destruir los datos cargados originalmentes.
- Mantener un registro simple de las columnas eliminadas, convertidas o imputadas.

### EDA

- Calcular medidas de tendencia central, dispersión y posición por variable o grupo.
- Calcular frecuencias absolutas y relativas para variables categóricas.
- Calcular correlaciones de Pearson, Spearman y posibles matrices de correlación para variables continuas.
- Identificar posibles valores atípicos mediante rango intercuartílico, z-score robusto u otros criterios claramente documentados.
- Construir tablas de resumen por año, mes, estación o categoría cuando el usuario seleccione una variable temporal o categórica.

### Distribuciones

#### Precipitación máxima anual

- Verificar independencia, orden temporal, longitud mínima de la muestra y dominio de los datos según el modelo.
- Ajustar por máxima verosimilitud, como método principal, cuando corresponda a cada distribución seleccionada:
  - Normal: ubicación y escala.
  - Lognormal: parámetros de forma y escala; registro de la variable para validar el dominio positivo.
  - Gamma: forma y escala.
  - Weibull: forma y escala.
  - Gumbel: ubicación y escala.
  - GEV: ubicación, escala y forma.
- Calcular el logaritmo de la verosimilitud y los criterios AIC, BIC y AICc:
  - `AIC = 2k - 2 ln(L)`
  - `BIC = k ln(n) - 2 ln(L)`
  - `AICc = AIC + 2k(k+1)/(n-k-1)`
- Ejecutar las pruebas de bondad de ajuste Kolmogorov-Smirnov y Anderson-Darling.
- Reportar estadístico observado, valor crítico o p-valor aproximado, nivel de significancia y decisión sin confundir ausencia de rechazo con aceptación del modelo.
- Calcular cuantiles para probabilidades o períodos de retorno seleccionados.
- Para período de retorno $T$ expresar la probabilidad anual de excedencia como $p = 1/T$ y el nivel asociado como $x_T = F^{-1}(1-p)$.
- Calcular el riesgo de al menos un excedencia durante $n$ años como `1 - (1 - p)^n`.
- Presentar intervalos o bandas de incertidumbre por simulación bootstrap paramétrica, perfil de verosimilitud o método disponible, indicando explícitamente el procedimiento usado.
- Permitir comparar modelos y ordenar por AICc, manteniendo también AIC y BIC para evitar decisiones basadas en una sola métrica.

#### Modelos de secado en capa delgada

- Ajustar modelos definidos por la sesión o por el proyecto, con sus ecuaciones registradas en código y documentación.
- Estimar parámetros por mínimos cuadrados o máxima verosimilitud según el modelo.
- Calcular predicciones, residuales, SSE, RMSE, log-verosimilitud cuando aplique, número de parámetros y AICc.
- Ordenar los modelos por AICc y reportar diferencias respecto al mejor modelo y pesos relativos cuando sean útiles.
- Permitir comparar curvas observadas y ajustadas para cada condición o tratamiento.

### Regresión

- Calcular correlaciones Pearson y Spearman junto con tamaños de muestra y valores de significancia si se implementan.
- Ajustar regresión lineal simple por MCO:
  - $\hat y = \beta_0 + \beta_1 x$
- Calcular pendiente, intercepto, errores estándar, intervalos de confianza, estadísticos t y p-valores.
- Calcular R², R² ajustado, suma de cuadrados de errores, regresión y total, estadístico F, ANOVA y error estándar de la regresión.
- Calcular residuos ordinarios, estandarizados y, si se implementan, residuos studentizados externamente.
- Construir intervalos de confianza para la media y intervalos de predicción para una nueva observación.
- Verificar linealidad, homocedasticidad, independencia visual, normalidad de residuos y puntos influyentes mediante gráficos y pruebas complementarias claramente etiquetadas.
- No omitir los supuestos ni afirmar causalidad a partir de una relación observacional.

### Series de tiempo

- Validar frecuencia, orden temporal, fechas duplicadas, faltantes y regularidad de la serie.
- Agregar o muestrear la serie cuando el usuario seleccione una frecuencia compatible, documentando cada transformación.
- Calcular promedios móviles simples y ponderados o centrados según la opción elegida.
- Estimar componentes aditivos o multiplicativos según sea apropiado para la escala y variabilidad de los datos.
- Calcular índices estacionales mediante promedio por período estacional y normalización según el método aditivo o multiplicativo.
- Ejecutar descomposición clásica y conservar una tabla por fecha con observado, componente estacional, tendencia, residuo y ajustado.
- Comparar métodos de referencia: media, deriva, paseo aleatorio o estacional ingenuo, según la frecuencia disponible.
- Crear una partición temporal de entrenamiento, validación y prueba sin mezclar observaciones futuras.
- Calcular MAE, RMSE y SMAPE en la validación y en prueba cuando exista un periodo reservado:
  - `MAE = promedio(|y - y_hat|)`
  - `RMSE = raíz(promedio((y - y_hat)^2))`
  - `SMAPE = promedio(200 * |y-y_hat| / (|y|+|y_hat|))`
- Comparar modelos de AutoTS y, si está disponible, seleccionar el método según una métrica definida, evitando optimización con datos reservados para prueba.
- Generar pronósticos fuera de muestra y bandas o intervalos aproximados, indicando el horizonte y los supuestos de incertidumbre.

## Organización modular del proyecto

```text
app-estadistica-aplicada/
├── app.py                     # Punto de entrada y navegación principal
├── pages/
│   ├── 1_Inicio.py
│   ├── 2_Datos.py
│   ├── 3_EDA.py
│   ├── 4_Distribuciones.py
│   ├── 5_Regresion.py
│   └── 6_Series_de_tiempo.py
├── src/
│   ├── datos.py               # carga, validación, tipos y transformaciones
│   ├── estadistica.py         # resúmenes, correlaciones, regresión y pruebas
│   ├── distribuciones.py      # ajuste, selección, KS, AD, AIC/BIC/AICc y retornos
│   ├── secado.py              # modelos de secado en capa delgada y AICc
│   ├── series_tiempo.py       # componentes, validación y pronóstico
│   ├── graficos.py            # funciones reutilizables de visualización
│   └── formatos.py            # formato de tablas, unidades y mensajes educativos
├── datos/
│   ├── README.md              # descripción, origen, licencia y diccionario
│   └── ejemplos/              # conjuntos de datos pequeños usados como casos demostrativos
├── verificacion/
│   ├── test_datos.py
│   ├── test_estadistica.py
│   ├── test_distribuciones.py
│   └── test_series_tiempo.py
├── docs/
│   └── PLAN_DESARROLLO.md
└── archivos de configuración del entorno del proyecto
```

### Responsabilidades

- `app.py` debe cargar la configuración general y construir la navegación hacia las páginas.
- `pages/` debe contener la interfaz, validación del contexto de Streamlit y llamadas a funciones de `src/`; debe evitar implementaciones estadísticas extensas.
- `src/datos.py` debe ser la única superficie central para entrada, limpieza y validación básica.
- `src/estadistica.py` debe agrupar cálculos compartidos de resúmenes, correlaciones y regresión.
- `src/distribuciones.py` debe concentrar ajustes probabilísticos, criterios de información, pruebas y retornos.
- `src/secado.py` debe separar las ecuaciones de los modelos de secado y sus métricas de comparación.
- `src/series_tiempo.py` debe contener descomposición, métodos de referencia, métricas, partición temporal y pronósticos.
- `src/graficos.py` debe reutilizar estilos y generar tablas o figuras consistentes con la interfaz.
- `verificacion/` debe contener pruebas pequeñas sobre casos conocidos, casos límite y reproducción de cálculos esperados.
- `datos/ejemplos/` debe conservar datos reales o sintéticos documentados, con una explicación breve de sus unidades.

### Estado compartido

Usar el estado de sesión de Streamlit para conservar el archivo cargado, las columnas seleccionadas, filtros y resultados recientes. Evitar un estado global fuera de Streamlit y no modificar los datos originales al aplicar transformaciones.

## Orden recomendado de construcción

1. **Preparar la estructura mínima del proyecto.**
   Crear primero los directorios y archivos base necesarios para que exista una ejecución reproducible. Este paso permite validar el entorno antes de añadir contenido estadístico.

2. **Construir `src/datos.py` y la página Datos.**
   Es el punto de entrada de toda la aplicación. Primero deben resolverse carga, inferencia de tipos, faltantes y filtros, porque las demás páginas dependen de una representación confiable de los datos.

3. **Implementar resúmenes básicos y la página EDA.**
   Permite comprobar visualmente las transformaciones hechas por Datos y familiariza al estudiante con las variables antes de ajustar modelos. Las tablas y gráficas deben reutilizar funciones comunes.

4. **Agregar funciones numéricas compartidas en `src/estadistica.py`.**
   Centralizar correlaciones, MCO y métricas evita duplicar cálculos. Incluir pruebas básicas para coeficientes, predicciones o casos conocidos.

5. **Construir la página Regresión.**
   Su lógica es local y fácil de separar en resultados, inferencia y diagnóstico. Es adecuada después de consolidar DataFrames y funciones descriptivas, pero antes de módulos probabilísticos más amplios.

6. **Construir `src/distribuciones.py` y la sección de precipitación.**
   Empieza con un único modelo, por ejemplo Gumbel o Normal, y luego añade los demás. Esto permite validar la verosimilitud, las pruebas KS y AD y los criterios antes de introducir comparación, retornos, riesgo e incertidumbre.

7. **Agregar los modelos de secado y su comparación AICc.**
   Reutiliza las tablas comparativas y algunas visualizaciones ya probadas, pero exige ecuaciones y conjuntos de datos específicos que deben documentarse por separado.

8. **Construir `src/series_tiempo.py` y la página Series de tiempo.**
   Conviene dejarla al final de la lógica estadística porque combina validación temporal, descomposición, partición temporal y pronóstico. Añadir primero componentes y referencias, después métricas, y finalmente AutoTS.

9. **Completar Inicio y mejorar navegación.**
   No conviene construirla como contenido aislado al principio; debe reflejar el estado real de Datos, EDA y los módulos ya disponibles.

10. **Añadir pruebas de regresión y casos documentados.**
    Crear verificaciones independientes con datos conocidos para impedir cambios silenciosos en cálculos, escalas, unidades y criterios de selección.

11. **Ejecutar una validación integral.**
    Probar carga, navegación, casos sin datos, datos inválidos, categorías constantes, series cortas, modelos fallidos y períodos de pronóstico insuficientes. Comprobar que no aparecen resultados ambiguos ni divisiones por cero.

12. **Pulir documentación y experiencia de usuario.**
    Explicar supuestos, lectura de tablas, interpretación de gráficos, unidades y limitaciones. Mantener el diccionario de datos y las fuentes de los ejemplos actualizados.

## Estrategia de verificación y casos límite

- Comprobar cada fórmula con valores calculados manualmente o con tablas conocidas antes de usar datos reales.
- Separar pruebas de cálculo en `verificacion/` de pruebas de interfaz en Streamlit.
- Verificar que una serie constante, una muestra muy pequeña, una variable categórica usada como numérica y una fecha inválida producen errores comprensibles.
- En distribuciones, comprobar el dominio positivo para Lognormal y Gamma, el comportamiento de Weibull y la estabilidad numérica de la cola de GEV.
- En secado, comprobar que ningún modelo reciba valores negativos o ceros cuando su ecuación no los admita.
- En regresión, comprobar pendientes, interceptos y residuos sobre una recta perfecta y sobre datos con ruido.
- En series de tiempo, comprobar que la partición temporal nunca utilice registros futuros y que los índices estacionales estén alineados con la frecuencia real.

## Entregables por fase

| Fase | Entregable verificable |
|---|---|
| Fundación | Proyecto con punto de entrada ejecutable y módulos vacíos o funcionalmente mínimos. |
| Datos y EDA | Carga de archivos, validación, filtros, resúmenes y gráficos exploratorios. |
| Regresión | Correlación, MCO, inferencia, bondad de ajuste y diagnóstico visual reproducible. |
| Distribuciones | Ajuste, pruebas, criterios, retornos, riesgo y comparación de al menos los seis modelos solicitados. |
| Secado | Comparación de modelos mediante métricas y AICc con datos documentados. |
| Series de tiempo | Componentes, descomposición, métodos de referencia, validación y pronóstico con AutoTS. |
| Cierre | Pruebas ejecutadas, documentación de datos y guía de interpretación para estudiantes. |
