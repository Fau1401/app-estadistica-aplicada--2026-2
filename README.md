# App de Estadística Aplicada — Ingeniería Agrícola

## Datos del estudiante

- **Nombre:** Faisury Pérez Amaya
- **Código:** 1102829578
- **Grupo:** No registrado en `datos/metadatos.json`
- **Cultivo:** Ñame
- **Municipio:** San Marcos
- **Huella:** `CEB93C9A`

Los datos personales anteriores se obtienen de `datos/metadatos.json`.

## Descripción general

Esta aplicación multipágina desarrollada con Streamlit acompaña el aprendizaje de estadística aplicada en Ingeniería Agrícola. Permite explorar datos agrícolas simulados, caracterizar variables, ajustar distribuciones de probabilidad, estimar relaciones mediante regresión y analizar pronósticos de series de tiempo. Los resultados se presentan en tablas, gráficos y reportes descargables.

La aplicación separa la interfaz de usuario, las operaciones estadísticas y la carga de datos para favorecer la comprensión, la reproducibilidad y el mantenimiento del código.

## Objetivo académico

Aplicar métodos de estadística descriptiva, exploratoria, probabilística, inferencial, regresión y series de tiempo sobre información agrícola, utilizando primero razonamientos y cálculos manuales y luego verificando los resultados con herramientas computacionales. También busca desarrollar criterios para interpretar unidades, supuestos, incertidumbre y limitaciones estadísticas.

## Páginas de la aplicación

La aplicación dispone de seis páginas:

1. **Inicio**
   - Presenta el propósito general, el flujo de trabajo y las páginas disponibles.
   - Explica la metodología del Lápiz y el Algoritmo.
   - Muestra los datos del estudiante registrados en los metadatos.

2. **Datos**
   - Permite visualizar los cuatro conjuntos disponibles: parcelas, precipitación máxima anual, clima mensual y secado.
   - Carga archivos CSV o Excel proporcionados por el usuario.
   - Informa dimensiones, tipos de variables, valores faltantes, descripciones y unidades.
   - Permite descargar el conjunto seleccionado en formato CSV.

3. **EDA**
   - Estudia variables numéricas y categóricas.
   - Calcula medidas de tendencia central, dispersión y posición.
   - Presenta histogramas, densidades, diagramas de caja, frecuencias y tablas de correlación.
   - Incluye filtros por tipo de suelo y régimen de riego, detección de valores atípicos y gráficos de comparación por grupos.

4. **Distribuciones**
   - Ajusta distribuciones a la precipitación máxima anual.
   - Compara modelos mediante AIC, BIC, AICc y pruebas o medidas de bondad de ajuste.
   - Calcula cuantiles, períodos de retorno, riesgo y intervalos bootstrap.
   - Ajusta y compara modelos de secado en capa delgada mediante curvas observadas y ajustadas.

5. **Regresión**
   - Calcula correlaciones de Pearson y Spearman.
   - Ajusta regresión lineal simple y regresión múltiple por mínimos cuadrados ordinarios.
   - Presenta coeficientes, intervalos, estadísticos de ajuste y diagnóstico de residuos.
   - Permite calcular predicciones y verificar relaciones entre variables explicativas y el rendimiento.

6. **Series de tiempo**
   - Analiza precipitación mensual y temperatura mensual.
   - Presenta promedios móviles, descomposición, índices estacionales y competencia entre métodos de referencia.
   - Realiza validación temporal y pronóstico con AutoTS mediante modelos rápidos.
   - Muestra intervalos o bandas de incertidumbre y métricas MAE, RMSE y SMAPE.

## Hallazgos del EDA

(escrito por el estudiante, con cifras y unidades)

## Hallazgos de distribuciones

(escrito por el estudiante, con cifras y unidades)

## Hallazgos de la regresión

(escrito por el estudiante, con cifras y unidades)

## Hallazgos de series de tiempo

(escrito por el estudiante, con cifras y unidades)

## Tecnologías

- Python
- Streamlit
- pandas y NumPy
- SciPy y statsmodels
- scikit-learn
- Matplotlib y seaborn
- AutoTS
- openpyxl
- pytest

## Estructura del proyecto

```text
.
├── app.py                  # Página de inicio y configuración de Streamlit
├── pages/
│   ├── 1_Datos.py          # Carga y exploración de datos
│   ├── 2_EDA.py            # Análisis exploratorio
│   ├── 3_Distribuciones.py # Probabilidad extrema y secado
│   ├── 4_Regresion.py      # Correlación y regresión
│   └── 5_Series_de_tiempo.py
├── src/
│   ├── datos.py            # Lectura, metadatos y ayudas de datos
│   ├── eda.py              # Resúmenes, frecuencias y detección de atípicos
│   ├── distribuciones.py   # Ajustes, bondad, retornos y riesgo
│   ├── regresion.py        # MCO, correlación y diagnóstico
│   ├── series.py           # Componentes, referencia y pronóstico
│   ├── modelos_curvas.py   # Modelos de secado
│   ├── validacion.py       # Validación de archivos y columnas
│   └── exportar.py         # Exportación de tablas, PNG, PDF y Markdown
├── datos/
│   ├── metadatos.json
│   ├── parcelas.csv
│   ├── precip_max_anual.csv
│   ├── clima_mensual.csv
│   ├── secado.csv
│   └── archivos de muestra utilizados por las verificaciones
├── tests/                  # Pruebas unitarias
├── verificacion/           # Scripts de comprobación de resultados
├── docs/                   # Documentación de diseño
├── resultados/             # Resultados generados
├── generar_datos.py        # Generación reproducible de datos simulados
├── pronostico_autots.py    # Ejecución auxiliar de AutoTS
├── requirements.txt
└── LICENSE
```

## Ejecución en GitHub Codespaces

1. Abra el repositorio en GitHub y cree un Codespace desde el botón **Code → Codespaces → Create codespace on main**.
2. Espere a que el entorno instale las herramientas del proyecto.
3. En la terminal integrada, cambie a la raíz del repositorio si fuera necesario:

   ```bash
   cd /workspaces/app-estadistica-aplicada--2026-2
   ```

4. Cree el entorno virtual, si aún no existe, y úselo para instalar las dependencias:

   ```bash
   python -m venv .venv
   .venv/bin/pip install -r requirements.txt
   ```

5. Inicie la aplicación con el intérprete, Streamlit y las herramientas del entorno virtual:

   ```bash
   .venv/bin/streamlit run app.py
   ```

6. Abra la URL local indicada por Streamlit o el enlace publicado por Codespaces en el panel de puertos.
7. Para ejecutar las pruebas:

   ```bash
   .venv/bin/python -m pytest -q
   ```

No es necesario modificar los archivos dentro de `datos/` ni `generar_datos.py`.

## Metodología: Lápiz y Algoritmo

El proceso se desarrolla en dos etapas complementarias:

1. **Lápiz:** primero se identifica el problema, se registra la variable, las unidades, el tamaño de muestra y los supuestos; luego se sustituyen los datos en las fórmulas y se obtiene una estimación manual o escrita.
2. **Algoritmo:** posteriormente se realiza el cálculo con Python mediante la aplicación. El estudiante compara cifras, gráficas y decisiones estadísticas, verifica diferencias por redondeo o codificación y corrige sus procedimientos si encuentra inconsistencias.

El enfoque exige que el estudiante supervise las respuestas, entienda las fórmulas y pueda explicar el significado agrícola de cada resultado.

## Limitaciones

- Los datos son simulados y no representan mediciones reales ni permiten concluir que una relación sea causal en campo.
- Las simulaciones están condicionadas por reglas, rangos y dependencias definidas en el generador de datos.
- AutoTS usa configuraciones de evaluación reducidas para mantener tiempos razonables; por ello no realiza una búsqueda exhaustiva ni garantiza el mejor modelo posible.
- Los intervalos, pronósticos y pruebas dependen de supuestos como independencia, estacionariedad, normalidad, homocedasticidad, linealidad, dominio de la variable o longitud suficiente de la serie.
- Los criterios de bondad de ajuste no eliminan por sí solos la incertidumbre ni sirven como única regla para elegir un modelo.
- La regresión lineal no controla todas las variables externas ni demuestra causalidad.
- Los resultados de archivos cargados por el usuario dependen de su calidad, unidades y consistencia.
- Los modelos de series pueden responder mal ante cambios estructurales, datos faltantes, estacionalidad irregular o horizontes largos.

## Posibles mejoras

- Incorporar datos agrícolas reales con autorización y trazabilidad.
- Añadir validación automática de unidades, rangos y metadatos de archivos propios.
- Ampliar el catálogo y la búsqueda de modelos, manteniendo controles visibles sobre tiempo y recursos.
- Incluir intervalos de confianza por perfil de verosimilitud y validación cruzada temporal más robusta.
- Mejorar diagnóstico de influencia, colinealidad y residuos en regresión.
- Añadir pruebas estadísticas de estacionariedad, independencia y homogeneidad temporal.
- Integrar comparación reproducible entre modelos, semillas y particiones.
- Crear almacenamiento persistente de resultados individuales y reportes exportables.

## Referencias básicas

- Montgomery, D. C., Peck, E. A., & Vining, G. G. *Introduction to Linear Regression Analysis*. Wiley.
- Hyndman, R. J., & Athanasopoulos, G. *Forecasting: Principles and Practice*. OTexts.
- Collet, D. *Modelling Survival Data in Medical Research*. Chapman & Hall/CRC.
- Documentación oficial de Python, Streamlit, pandas, NumPy, SciPy, statsmodels, scikit-learn, Matplotlib, seaborn, AutoTS y pytest.
