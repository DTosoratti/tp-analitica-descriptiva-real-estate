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

Contiene la base consolidada generada durante la extracción
(`remax_caba_propiedades.csv`, 17.023 avisos y 29 variables).

Por su tamaño, el archivo no se versiona en el repositorio: se aloja en
Google Drive y el notebook de limpieza lo descarga automáticamente en
esta carpeta mediante `gdown`.

Los archivos de esta carpeta no se modifican manualmente una vez generados,
de manera de conservar un punto de partida reproducible para las etapas
posteriores del proyecto.

### `data/processed/`

Contiene los datasets resultantes de los procesos de limpieza,
transformación, validación y selección del universo de análisis.

- `remax_deptos_limpio.csv`: base analítica de departamentos usados en
  venta en CABA (9.500 avisos y 41 variables). Es el insumo de las etapas
  de ingeniería de variables y análisis.
- `registro_limpieza.csv`: registro de cada exclusión y modificación
  aplicada durante la limpieza, con su criterio y la cantidad de registros
  afectados.

### `data/excepciones_manuales.csv`

Tabla de correcciones puntuales por aviso que no pueden resolverse con una
regla general (por ejemplo, ventas en bloque o alquileres publicados como
venta). Cada fila indica el ID afectado, la etapa, la acción (excluir o
reemplazar), la columna, el valor nuevo y el motivo de la corrección.

### `notebooks/`

Contiene los notebooks utilizados para ejecutar y documentar las distintas
etapas del proyecto.

- `01_extraccion_remax.ipynb`: configuración, ejecución y controles de la
  extracción.
- `02_limpieza_remax.ipynb`: limpieza y auditoría de calidad. Define el
  universo de análisis, trata valores imposibles, duplicados, monedas,
  valores faltantes y outliers, y exporta la base analítica a
  `data/processed/`.

### `src/`

Contiene las funciones y módulos reutilizables del proyecto, para evitar
concentrar la lógica en los notebooks.

- `scraper_remax.py`: lógica completa del extractor (requests, reintentos,
  paralelismo y normalización).
- `limpieza.py`: funciones de auditoría (calidad, variables categóricas y
  numéricas, reglas de consistencia), registro de pasos de limpieza y
  aplicación de excepciones manuales.
- `patrones.py`: expresiones regulares utilizadas en la limpieza y en la
  ingeniería de variables, definidas en un único lugar.
- `diagnostico.py`: funciones de diagnóstico (validación de ambientes contra
  el título, diagnóstico de valores faltantes y detección de outliers).

### `reports/`

Contiene informes, gráficos y entregables del proyecto.


## Ejecución

Los notebooks están preparados para ejecutarse en Google Colab. Al iniciar,
clonan el repositorio (o lo actualizan si ya está clonado) y trabajan desde
su raíz, de modo que los módulos de `src/` y las rutas de `data/` funcionan
sin configuración adicional.

El flujo debe ejecutarse respetando el siguiente orden:

1. Ejecutar `01_extraccion_remax.ipynb` (solo si se quiere generar una
   nueva corrida de la extracción).
2. Verificar los controles de la extracción.
3. Ejecutar `02_limpieza_remax.ipynb`. El notebook descarga la base raw,
   aplica la limpieza y exporta los resultados a `data/processed/`.
4. Verificar el registro de limpieza y los controles finales de calidad.
5. Utilizar `data/processed/remax_deptos_limpio.csv` para las etapas
   siguientes.

El notebook de extracción contiene principalmente la configuración,
ejecución y controles del proceso. La lógica reutilizable del scraper se
encuentra separada en `src/scraper_remax.py`.


## Limpieza y auditoría de calidad

A partir de los 17.023 avisos de la base raw se construyó una base analítica
de **9.500 departamentos usados en venta** (55,8 % de la extracción).

| Paso | Avisos excluidos | Avisos restantes |
| --- | ---: | ---: |
| Base raw | — | 17.023 |
| Tipologías distintas de departamento | 5.358 | 11.665 |
| PH clasificados como departamento | 53 | 11.612 |
| Propiedades nuevas (pozo, preventa, a estrenar) | 1.963 | 9.649 |
| Duplicados | 132 | 9.517 |
| Excepciones manuales (ventas en bloque y alquiler) | 12 | 9.505 |
| Precio publicado en pesos | 2 | 9.503 |
| Superficies imposibles | 3 | 9.500 |

La mayor parte de la reducción responde a la definición del alcance
(43,3 % de la base raw) y no a problemas de calidad (0,9 %).

Criterios principales:

- **Valores imposibles o de relleno** (expensas o antigüedad iguales a 0,
  superficie cubierta nula) se reemplazan por faltantes en lugar de
  excluir el aviso.
- **Valores faltantes**: se diagnostica su mecanismo (tests t de Welch,
  chi-cuadrado y regresión logística). Como ninguno resulta completamente
  aleatorio, no se imputan en la base limpia y se agregan indicadores de
  dato informado.
- **Outliers**: se detectan con Box-Cox y regla de Tukey, y con la distancia
  de Mahalanobis. Solo se excluyen los errores comprobados; los valores
  atípicos genuinos (segmento de lujo, unidades a reciclar) se conservan y
  se marcan, porque los precios por m² inusualmente bajos pueden
  corresponder a las oportunidades que se busca identificar.
- **Casos dudosos** se conservan con indicadores de calidad
  (`Flag_Ambientes_Dudoso`, `Flag_Dormitorios_Inconsistente`,
  `Flag_Posible_Republicacion`, `Flag_Atipico_Bajo`, `Flag_Atipico_Alto`,
  `Flag_Extremo`, `Flag_Outlier_Multivariado`).


## Criterio de conservación de datos

Se mantiene una separación entre la base generada durante la extracción y
los datos procesados posteriormente.

La base `raw` constituye el resultado consolidado de la extracción y no se
modifica manualmente una vez generada. A partir de esta base se construyen
los datasets procesados, manteniendo separadas las etapas de extracción y
limpieza.

Las exclusiones, correcciones y transformaciones analíticas se aplican
mediante reglas reproducibles, y cada una queda anotada en
`data/processed/registro_limpieza.csv`.

Las excepciones particulares detectadas durante la limpieza se registran
explícitamente en `data/excepciones_manuales.csv`, indicando el motivo de
cada corrección, para mantener la trazabilidad del proceso y evitar
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
