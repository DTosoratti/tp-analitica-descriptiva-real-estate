# Real Estate Analytics 🏠

## Analítica Descriptiva — ITBA

Trabajo Práctico Integrador de la materia **Analítica Descriptiva** de la
Licenciatura en Analítica Empresarial y Social del ITBA.

### Integrantes

- Dante Tosoratti
- Martina Risso
- María Sol Allievi
- Tomás Agustín Picciolo


## Objetivo del proyecto

El proyecto analiza el mercado de departamentos usados en venta en la
Ciudad Autónoma de Buenos Aires (CABA), desde la perspectiva de un fondo
de inversión inmobiliaria.

El objetivo principal es detectar propiedades potencialmente subvaluadas
respecto de inmuebles comparables y, dentro de ese conjunto, identificar
casos con potencial para una estrategia de refacción y reventa (flipping).

Para ello se construyen grupos de propiedades comparables considerando
principalmente ubicación, superficie y cantidad de ambientes. Otras
variables, como antigüedad, estado y características de la propiedad,
serán evaluadas según su disponibilidad, calidad y capacidad para mejorar
la comparabilidad.


## Criterio de subvaluación

En este proyecto una propiedad no se considera una oportunidad simplemente
por presentar un precio inferior al promedio general del mercado.

Se define como **potencialmente subvaluada** aquella propiedad cuyo precio
publicado se encuentra por debajo de un valor de referencia construido a
partir de propiedades comparables.

Los grupos comparables se construyen considerando principalmente:

- ubicación;
- cantidad de ambientes;
- rango de superficie;
- y otras características relevantes según la disponibilidad y calidad
  de los datos.

Para cada grupo comparable se utiliza como benchmark la mediana del precio
por metro cuadrado (USD/m²).

A partir de este benchmark se estima un precio esperado para cada propiedad:

**Precio esperado = Benchmark USD/m² × Superficie de la propiedad**

Luego se calcula el gap de subvaluación:

**Gap de subvaluación = (Precio esperado - Precio publicado) / Precio esperado**

Un gap positivo indica que la propiedad se encuentra publicada por debajo
del valor de referencia de su grupo comparable. Cuanto mayor sea este gap,
mayor será el descuento relativo respecto del benchmark utilizado.

A efectos exploratorios, se evaluará inicialmente un umbral de gap igual o
superior al 15 % para identificar candidatos de interés. Este umbral será
analizado posteriormente mediante pruebas de sensibilidad y no se interpreta
como una regla universal del mercado.

El análisis utiliza precios publicados. Por lo tanto, la identificación de
subvaluación representa una señal relativa dentro de la oferta observada y
no implica que el precio estimado corresponda al precio efectivo de cierre
de una operación.


## Fuente principal de datos

La fuente principal utilizada es **RE/MAX Argentina**.

Los datos se obtienen mediante un extractor desarrollado por el equipo
sobre la API utilizada por el sitio de RE/MAX.

La extracción se realiza en dos etapas:

1. Consulta del listado paginado de propiedades en venta en CABA.
2. Consulta del detalle de cada propiedad para incorporar información
   adicional no disponible en el listado general.

La información extraída se consolida en una base `raw` que conserva los
campos obtenidos de la fuente y las transformaciones mínimas necesarias
para estructurar la extracción.

Las etapas posteriores de limpieza, filtrado del universo de análisis,
tratamiento de valores atípicos y generación de variables analíticas se
realizan sobre una base procesada.


## Flujo general del proyecto

RE/MAX  
→ extracción de listados  
→ extracción de detalles  
→ datos raw  
→ limpieza y validación  
→ datos procesados  
→ análisis descriptivo  
→ construcción de comparables  
→ identificación de propiedades potencialmente subvaluadas  
→ evaluación de oportunidades de flipping


## Estructura del repositorio

### `data/raw/`

Contiene la base consolidada generada durante la extracción.

Los archivos de esta carpeta no se modifican manualmente una vez generados,
de manera de conservar un punto de partida reproducible para las etapas
posteriores del proyecto.

### `data/processed/`

Contiene los datasets resultantes de los procesos de limpieza,
transformación, validación y selección del universo de análisis.

### `notebooks/`

Contiene los notebooks utilizados para ejecutar y documentar las distintas
etapas del proyecto.

- `01_extraccion_remax.ipynb`: configuración, ejecución y controles de la
  extracción.
- `02_Limpieza.ipynb`: limpieza, controles de calidad y generación de
  variables derivadas.

### `src/`

Contiene las funciones y módulos reutilizables del proyecto.

La lógica completa del scraper se encuentra en `src/scraper_remax.py`.
Las funciones repetitivas utilizadas en otras etapas del proyecto también
se incorporan a esta carpeta para evitar concentrar toda la lógica en los
notebooks.

### `reports/`

Contiene informes, gráficos y entregables del proyecto.


## Ejecución

El flujo debe ejecutarse respetando el siguiente orden:

1. Ejecutar `01_extraccion_remax.ipynb`.
2. Verificar los controles de la extracción.
3. Ejecutar `02_Limpieza.ipynb`.
4. Verificar los controles de calidad y los registros excluidos.
5. Utilizar el dataset procesado resultante para el análisis.

El notebook de extracción contiene principalmente la configuración,
ejecución y controles del proceso. La lógica reutilizable del scraper se
encuentra separada en `src/scraper_remax.py`.


## Criterio de conservación de datos

Se mantiene una separación entre la base generada durante la extracción y
los datos procesados posteriormente.

La base `raw` constituye el resultado consolidado de la extracción y no se
modifica manualmente una vez generada. A partir de esta base se construyen
los datasets procesados, manteniendo separadas las etapas de extracción y
limpieza.

Las exclusiones, correcciones y transformaciones analíticas se realizan
posteriormente y deben quedar documentadas mediante reglas reproducibles.

Las excepciones particulares detectadas durante la limpieza se registran
explícitamente para mantener la trazabilidad del proceso y evitar
correcciones aisladas mediante valores hardcodeados dentro de los notebooks.


## Fuentes externas

En las siguientes etapas, la base principal será enriquecida con fuentes
externas para incorporar información espacial y económica relevante para
el análisis.

Entre ellas se consideran:

- límites oficiales de barrios de CABA;
- estaciones de subte y ferrocarril;
- espacios verdes;
- establecimientos educativos;
- información para estimar y actualizar costos de refacción;
- tipo de cambio.

Cada fuente será documentada indicando su procedencia, nivel de agregación,
variable incorporada y la comparación o análisis que permite realizar.
