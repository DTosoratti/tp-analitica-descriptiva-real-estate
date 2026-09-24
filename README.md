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
a partir de propiedades comparables y, dentro de ese conjunto, identificar
casos con potencial para una estrategia de refacción y reventa (flipping).

Para ello se busca construir valores de referencia considerando variables
como ubicación, superficie, cantidad de ambientes, antigüedad, estado y
otras características relevantes de cada propiedad.



## Fuente principal de datos

La fuente principal utilizada es **RE/MAX Argentina**.

Los datos se obtienen mediante un extractor desarrollado por el equipo
sobre la API utilizada por el sitio de RE/MAX.

La extracción se realiza en dos etapas:

1. Consulta del listado paginado de propiedades en venta en CABA.
2. Consulta del detalle de cada propiedad para incorporar información
   adicional no disponible en el listado general.

La información obtenida se almacena inicialmente sin modificaciones para
conservar una versión reproducible de los datos originales.

Posteriormente se realiza la limpieza, transformación y selección del
universo de departamentos usados utilizado en el análisis.



## Flujo general del proyecto

RE/MAX
→ extracción de listados
→ extracción de detalles
→ datos raw
→ limpieza y validación
→ datos procesados
→ análisis descriptivo
→ construcción de comparables
→ identificación de oportunidades


## Estructura del repositorio

### `data/raw/`
Contiene los datos originales obtenidos durante la extracción.

Los archivos de esta carpeta no deben modificarse manualmente, ya que
representan la información obtenida directamente de la fuente.

### `data/processed/`
Contiene los datasets resultantes de los procesos de limpieza,
transformación y selección del universo de análisis.

### `notebooks/`
Contiene los notebooks utilizados para ejecutar y documentar las
distintas etapas del proyecto.

- `01_extraccion_remax.ipynb`: configuración y ejecución de la extracción.
- `02_Limpieza.ipynb`: limpieza, controles de calidad y generación de
  variables derivadas.

### `src/`
Contiene las funciones y módulos reutilizables del proyecto.

La lógica completa del scraper y las funciones repetitivas de limpieza
se almacenan en esta carpeta para evitar concentrar todo el código en
los notebooks.

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
ejecución y controles. La lógica reutilizable del scraper se encuentra
en `src/`.



## Criterio de conservación de datos

Se mantiene una separación entre los datos originales y los datos
procesados.

La base `raw` conserva la respuesta obtenida de la fuente para permitir
reproducir y auditar el proceso.

Las exclusiones, correcciones y transformaciones se realizan posteriormente
y deben quedar documentadas mediante reglas reproducibles.

Las excepciones particulares detectadas durante la limpieza no se corrigen
directamente mediante valores hardcodeados dentro del notebook. Se registran
como reglas o excepciones documentadas para mantener la trazabilidad del
proceso.



## Fuentes externas

En las siguientes etapas, la base principal será enriquecida con fuentes
externas para incorporar información espacial y económica relevante.

Entre ellas se consideran:

- límites oficiales de barrios de CABA;
- estaciones de subte y ferrocarril;
- espacios verdes;
- establecimientos educativos;
- información necesaria para estimar y actualizar costos de refacción;
- tipo de cambio.

Cada fuente será documentada indicando su nivel de agregación y la variable
que aporta al análisis.
