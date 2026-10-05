# Real Estate Analytics 🏠

## Inteligencia de mercado inmobiliario en CABA — Analítica Descriptiva (ITBA)

Trabajo Práctico Integrador de la materia **Analítica Descriptiva** de la
Licenciatura en Analítica Empresarial y Social del ITBA.

### Integrantes

- Dante Tosoratti
- Martina Risso
- María Sol Allievi
- Tomás Agustín Picciolo


## Descripción del proyecto

El proyecto analiza la oferta de departamentos usados en venta en la Ciudad
Autónoma de Buenos Aires (CABA) para detectar propiedades publicadas por
debajo del valor de propiedades comparables y, dentro de ese conjunto,
identificar oportunidades de refacción y reventa (flipping).

El problema se aborda como un problema de **valuación relativa**: primero se
estima cuánto debería valer una propiedad según comparables de características
similares, y luego se compara ese valor con el precio publicado. La diferencia
es la señal de subvaluación. Para las unidades que necesitan obra, esa señal es
el punto de partida para evaluar si el descuento compensa el costo de la
refacción y los demás costos de la operación.


## Interlocutor

El producto analítico está dirigido a un **Fondo de Inversión Inmobiliario**.
El equipo de inversión lo usa para dos decisiones concretas:

1. **Priorizar qué propiedades visitar u ofertar**, a partir de un ranking de
   subvaluación.
2. **Decidir si conviene comprar y refaccionar una unidad puntual**, a partir
   del margen potencial de flipping.

El resultado se consume mediante un ranking exportable y, en la entrega final,
un tablero interactivo en Power BI o Tableau.


## Contexto de negocio

El mercado inmobiliario de CABA presenta una fuerte dispersión de información:
a partir de un aviso individual no es sencillo determinar si el precio pedido
está alineado con propiedades comparables.

Además, tiene características que condicionan tanto la señal de descuento como
la viabilidad de una estrategia de flipping:

- **Crédito hipotecario escaso y cíclico:** una parte relevante de las
  operaciones se realiza sin financiamiento, lo que reduce la demanda potencial
  en la reventa.
- **Dolarización:** los precios se expresan en dólares, mientras que parte de
  los costos de la operación y de la obra se pagan en pesos.
- **Iliquidez:** una propiedad puede permanecer publicada durante meses. Una
  oportunidad de flipping depende no solo del margen estimado, sino también del
  tiempo necesario para realizarlo mediante la reventa.
- **Brecha entre precio publicado y precio de cierre:** el dataset contiene
  precios de publicación. El gap de subvaluación es una señal de descuento
  respecto de comparables publicados, no una estimación del descuento respecto
  del precio efectivo de transacción.


## Alcance y unidad de análisis

| Dimensión | Definición |
| --- | --- |
| Ubicación | CABA, todos los barrios |
| Operación | Venta |
| Tipología | Departamentos (todas las subcategorías de RE/MAX: estándar, monoambiente, semipiso, dúplex, tríplex, piso, loft, penthouse) |
| Condición | Stock usado. Se excluyen pozo, preventa, en construcción y a estrenar |
| Moneda de análisis | USD |
| Unidad de análisis | Aviso individual de una propiedad |
| Corte temporal | Una corrida completa del extractor (ver *Datos*). Para estudiar permanencia en el mercado se realizarán capturas sucesivas |

La base raw conserva todas las tipologías que devuelve la fuente. El filtro al
universo de análisis se aplica en la etapa de limpieza, de modo que la
extracción original permanezca completa y reproducible.


## Preguntas por nivel analítico

### Descriptivo

1. ¿Cuál es el precio mediano y la dispersión del USD/m² por barrio, y cómo
   varía según superficie, ambientes y antigüedad?
2. ¿Qué diferencia de USD/m² existe entre departamentos que necesitan obra y
   departamentos reciclados o refaccionados comparables?
3. ¿Qué proporción de la oferta usada puede clasificarse como "necesita obra",
   "buen estado", "reciclada/refaccionada" o queda sin evidencia suficiente?
4. ¿Qué características y amenities aparecen con mayor frecuencia en cada
   segmento de precio?
5. ¿Cuánto tiempo permanece observado un aviso antes de dejar de aparecer en
   las capturas sucesivas?

### Diagnóstico

1. ¿Qué variables disponibles explican mejor las diferencias de precio entre
   propiedades comparables de una misma zona?
2. ¿El descuento asociado a "necesita obra" es similar en todos los barrios o
   cambia según la zona?
3. ¿Qué relación tienen amenities como cochera, seguridad, pileta o terraza con
   el USD/m² dentro de segmentos comparables?
4. ¿La dispersión del USD/m² dentro de estratos homogéneos permite identificar
   micromercados u oportunidades que un promedio general oculta?

### Predictivo

¿Cuál es el **Precio Esperado Reciclado (PER)** de una propiedad que necesita
obra, es decir, el valor que tendría después de la refacción, estimado a partir
de propiedades comparables en buen estado o recicladas?

### Prescriptivo

Dados el PER, el precio publicado, el costo de refacción y los costos de la
operación, ¿qué propiedades conviene comprar, respetando un margen mínimo, un
presupuesto y un soporte estadístico mínimo del benchmark?


## Arquitectura analítica

### Variable a estimar

El **Precio Esperado Reciclado (PER)** es la mediana condicional del USD/m²
homogeneizado dentro del estrato de la propiedad, calculada solo con
propiedades en buen estado o recicladas, multiplicada por la superficie
homogeneizada de la propiedad.

El PER no es observable para las propiedades que necesitan obra: se infiere
por transferencia desde las comparables en buen estado, bajo el supuesto de
**ignorabilidad condicional** (dos propiedades del mismo estrato difieren en
valor esperado solo por su estado de conservación). Este supuesto es una
limitación explícita del análisis.

### Validación

- Holdout 80/20 sobre las propiedades con estado conocido (buen estado o
  reciclada), estratificado por barrio, sin filtración entre entrenamiento y
  prueba.
- Métricas: error absoluto medio (MAE), error porcentual absoluto medio (MAPE)
  y cobertura (proporción de casos cuyo precio real cae dentro del rango
  intercuartílico del estrato de entrenamiento).
- Al menos cinco semillas distintas; se informan la media y el desvío del MAPE.
- Criterio de aceptación inicial: MAPE menor al 15 %. Los estratos que no lo
  cumplen se tratan con cautela o se excluyen de la regla de decisión.

### Regla de decisión

Se recomienda comprar una propiedad si y solo si se cumplen simultáneamente:

1. margen potencial de flipping ≥ umbral de margen;
2. gap de subvaluación inicial ≥ umbral de gap;
3. inversión total ≤ presupuesto disponible;
4. cantidad de comparables del estrato ≥ mínimo definido;
5. margen no negativo en el escenario conservador del valor post-obra.

Los umbrales son hiperparámetros: se eligen mediante un análisis de
sensibilidad que balancea la cantidad de oportunidades detectadas contra la
confiabilidad del margen.


## KPIs

| KPI | Definición | Interpretación comercial |
| --- | --- | --- |
| Superficie homogeneizada (m²) | Superficie cubierta + 0,5 × (Superficie total − Superficie cubierta) | Pondera la superficie descubierta, que vale menos que la cubierta |
| USD/m² homogeneizado | Precio publicado / Superficie homogeneizada | Compara propiedades de distinto tamaño en una misma unidad de valor |
| Benchmark USD/m² | Mediana del USD/m² homogeneizado del grupo de comparables | Referencia robusta de mercado para el segmento |
| Precio esperado (USD) | Benchmark USD/m² × Superficie homogeneizada | Valor de referencia de una propiedad comparable |
| Gap de subvaluación (%) | (Precio esperado − Precio publicado) / Precio esperado × 100 | Cuánto más barata está publicada respecto de su benchmark |
| Gap de estado (%) | (Mediana USD/m² Reciclada − Mediana USD/m² Necesita obra) / Mediana USD/m² Reciclada × 100 | Descuento asociado a la necesidad de refacción dentro de un segmento |
| Precio Esperado Reciclado — PER (USD) | Mediana del USD/m² homogeneizado de comparables en buen estado o recicladas × Superficie homogeneizada. Escenarios: P25 (conservador), mediana (base) y P75 (optimista) | Valor post-obra estimado |
| Costo de obra (USD) | Superficie cubierta intervenida × Costo USD/m² según nivel de obra × (1 + contingencia) | Inversión necesaria para llevar la unidad a un estado comparable |
| Costo de tenencia (USD) | Expensas mensuales en USD × (meses de obra + meses de venta) + costo de oportunidad del capital | Costo de mantener la unidad durante la operación |
| Inversión total (USD) | Precio de compra + Costos de compra + Costo de obra + Costo de tenencia | Capital total comprometido |
| Margen potencial de flipping (%) | (PER × (1 − Costos de venta) − Inversión total) / Inversión total | Ganancia potencial relativa, antes de impuestos no modelados |


## Definición operativa de propiedad "barata"

Una propiedad se considera **barata** cuando su precio publicado por m² es
significativamente inferior al de propiedades comparables, en una magnitud que
no puede atribuirse a la dispersión normal de su segmento ni a su estado de
conservación.

### Grupo de propiedades comparables

Cada propiedad se compara con departamentos usados que comparten:

- **Barrio oficial**, asignado a partir de las coordenadas y los límites de BA Data;
- **Ambientes**: 1, 2, 3, 4, y 5 o más;
- **Banda de superficie**: terciles de superficie homogeneizada dentro de cada
  cantidad de ambientes (chica, media y grande);
- **Banda de antigüedad**: hasta 10 años, 11 a 30, 31 a 50, más de 50, y sin dato.

Cada grupo debe tener al menos **10 propiedades**. Si no se alcanza ese mínimo,
se amplía en forma jerárquica hasta el primer nivel que lo cumpla:

| Nivel | Criterio del grupo |
| --- | --- |
| 1 | Barrio × ambientes × banda de superficie × banda de antigüedad |
| 2 | Barrio × ambientes × banda de superficie |
| 3 | Comuna × ambientes × banda de superficie |
| 4 | Comuna × ambientes |

Para cada propiedad se registra el nivel utilizado. Si ningún nivel alcanza el
mínimo, la propiedad queda **sin benchmark** y no se clasifica.

Del cálculo del benchmark se excluyen la propia propiedad evaluada, los avisos
marcados como valores extremos o con cantidad de ambientes dudosa, y los
clasificados como "necesita obra".

### Criterio de clasificación

Una propiedad es barata si cumple las tres condiciones:

1. **Gap de subvaluación ≥ 15 %.**
2. **USD/m² en el cuartil inferior de su grupo** (por debajo del percentil 25).
   Esta condición controla la dispersión: en un grupo heterogéneo, un descuento
   del 15 % respecto de la mediana puede estar dentro del rango habitual.
3. **No está clasificada como "necesita obra"**, porque esos casos son más
   baratos por una razón identificable y se evalúan con el margen de flipping.

Las propiedades que cumplen el criterio, pero tienen indicadores de posible
error de carga, se revisan manualmente antes de incluirlas en el ranking.

| Categoría | Condición |
| --- | --- |
| **Barata** | Cumple el gap, el cuartil inferior y no necesita obra, sin indicadores de error |
| **Barata — requiere verificación** | Cumple el criterio, pero tiene indicadores de posible error de carga |
| **A refaccionar con descuento** | Necesita obra y su gap es positivo → se evalúa con el margen de flipping |
| **Precio de mercado** | No cumple el criterio de subvaluación |
| **Sin benchmark** | Ningún nivel de comparación alcanza 10 propiedades |

El umbral del 15 % y el coeficiente de 0,5 de la superficie descubierta son
supuestos iniciales. Se evaluará la sensibilidad con umbrales del 10 % y del
20 % y coeficientes entre 0,3 y 0,7.


## Tratamiento de la variable `Estado_Propiedad`

`Estado_Propiedad` se construye con expresiones regulares sobre el título y la
descripción. Es una **señal imperfecta**: tiene baja cobertura (la mayoría de
los avisos no menciona la condición del inmueble), sesgo de declaración (se
menciona cuando conviene destacarlo) y menciones parciales ("baño reciclado"
no describe la unidad completa).

Decisión adoptada:

- `Estado_Propiedad` mantiene cuatro categorías (Necesita_obra, Buen_estado,
  Reciclada_refaccionada, Sin_clasificar) y se usa en el diagnóstico (H1).
- `Estado_Agrupado` tiene tres niveles (Necesita_obra, Buen_o_reciclada,
  Sin_clasificar) y se usa para armar los comparables.
- **Sin_clasificar** es una categoría propia: no se imputa ni se asume buen estado.
- `Reciclado_Parcial` marca menciones de reciclado de un solo ambiente; esos
  avisos no se cuentan como reciclada integral al construir el PER.
- Se validará manualmente una muestra estratificada de 50 avisos por categoría
  (precisión mínima inicial: 80 % en Necesita_obra y Reciclada_refaccionada).

La columna `Estado` de la base raw corresponde al estado de la publicación y no
a la condición física del inmueble; se renombra como `Estado_Publicacion`.


## Hipótesis

**H1. Descuento por condición.** Los departamentos que necesitan obra presentan
un USD/m² menor que los reciclados o refaccionados, aun dentro de un mismo
estrato de barrio, ambientes y superficie.

**H2. Dispersión condicional.** Una mayor dispersión del USD/m² dentro de un
estrato homogéneo (barrio, ambientes y superficie, con baja variabilidad
interna de superficie) es indicativa de oportunidades. La dispersión sobre
agregados menos granulares, como el barrio completo, se interpreta como baja
confiabilidad del benchmark y no como oportunidad. Antes de atribuir la
dispersión a una oportunidad se descartan errores de carga como causa
alternativa.

**H3. Existencia de oportunidades de flipping.** En una parte de los casos que
necesitan obra, el descuento de entrada supera el costo de refacción, los
costos de transacción, el costo de tenencia y las contingencias, generando un
margen positivo aun en el escenario conservador del valor post-obra.


## Datos

### Fuente principal: RE/MAX Argentina

Extractor propio sobre la API interna del sitio de RE/MAX, restringido a
Capital Federal y operación de venta. La extracción se realiza en dos etapas:
listado paginado de propiedades y consulta del detalle de cada una (que aporta
descripción, antigüedad y apto crédito).

| Característica | Valor |
| --- | --- |
| Fecha de corte | **[completar: fecha de la corrida del extractor]** |
| Cobertura geográfica | CABA |
| Registros raw | 17.023 avisos, 29 variables |
| Registros en la base analítica | 9.500 departamentos usados, 41 variables |
| Granularidad | Aviso individual |
| Moneda | Precio en USD; expensas en ARS |

La variable `Fecha_Publicacion` llega vacía desde la fuente (100 % de
faltantes), por lo que la permanencia en el mercado se medirá con capturas
sucesivas, registrando la primera y la última fecha en que se observa cada aviso.

**Normalización monetaria.** No se aplicaron conversiones de moneda. Los
precios se analizan en USD, tal como se publican (se excluyeron dos avisos con
precio en pesos). Las expensas se conservan en pesos. Su conversión a USD,
necesaria para el costo de tenencia, se hará con el tipo de cambio definido en
la sección de fuentes externas, indicando la fuente y la fecha de referencia.

### Limpieza

| Paso | Avisos excluidos | Avisos restantes |
| --- | ---: | ---: |
| Base raw | — | 17.023 |
| Tipologías distintas de departamento | 5.358 | 11.665 |
| PH clasificados como departamento | 53 | 11.612 |
| Propiedades nuevas (pozo, preventa, a estrenar) | 1.963 | 9.649 |
| Duplicados | 132 | 9.517 |
| Excepciones manuales (ventas en bloque y un alquiler) | 12 | 9.505 |
| Precio publicado en pesos | 2 | 9.503 |
| Superficies imposibles | 3 | 9.500 |

La mayor parte de la reducción responde a la definición del alcance (43,3 % de
la base raw) y no a problemas de calidad (0,9 %).

- **Valores imposibles o de relleno** (expensas o antigüedad iguales a 0,
  superficie cubierta nula) se reemplazan por faltantes en lugar de excluir el aviso.
- **Valores faltantes:** se diagnosticó su mecanismo con tests t de Welch,
  chi-cuadrado y regresión logística. Ninguno resulta completamente aleatorio,
  por lo que no se imputan en la base limpia y se agregan indicadores de dato
  informado. Las expensas se imputarán con KNN en la etapa de ingeniería de
  variables, solo para el costo de tenencia.
- **Outliers:** se detectan con Box-Cox y regla de Tukey, y con la distancia de
  Mahalanobis. Solo se excluyen errores comprobados. Los valores atípicos
  genuinos (segmento de lujo, unidades a reciclar) se conservan y se marcan,
  porque los precios por m² inusualmente bajos pueden ser las oportunidades
  que se busca identificar.
- **Casos dudosos** se conservan con indicadores de calidad
  (`Flag_Ambientes_Dudoso`, `Flag_Dormitorios_Inconsistente`,
  `Flag_Posible_Republicacion`, `Flag_Atipico_Bajo`, `Flag_Atipico_Alto`,
  `Flag_Extremo`, `Flag_Outlier_Multivariado`).

El detalle de cada paso está en `data/processed/registro_limpieza.csv`, y el
significado de cada variable, en `data/diccionario_datos.md`.


## Fuentes externas

Una fuente es **indispensable** si sin ella no puede calcularse algún paso de
la regla de decisión. Las **complementarias** se incorporan en la Pre-Entrega 3
para explicar diferencias de precio dentro de un mismo estrato.

### Indispensables

| Fuente | Cobertura y período | Granularidad y mecanismo de unión | Variable derivada | Aporta a | Limitaciones |
| --- | --- | --- | --- | --- | --- |
| [BA Data — Barrios](https://data.buenosaires.gob.ar/dataset/barrios) | CABA; límites vigentes | Polígonos de barrio. Unión espacial punto en polígono con la latitud y longitud de cada aviso | `Barrio_Oficial`, `Comuna` | Estratos del benchmark y del PER (niveles 1 a 4) | Avisos con coordenadas faltantes o fuera de CABA no pueden asignarse |
| [INDEC — Índice del Costo de la Construcción](https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-33) | Gran Buenos Aires; serie mensual | Serie temporal; se une por fecha (cotización y fecha de análisis) | Factor de actualización del costo de obra | Costo de refacción | Es un índice, no un costo por m²; está en pesos |
| Tipo de cambio histórico (BCRA; MEP como alternativa) | Argentina; serie diaria | Serie temporal; se une por fecha de referencia | Costos de obra y expensas en USD | Inversión total y margen | El margen cambia según el tipo de cambio elegido; se informa la sensibilidad |
| Estadísticas de escrituras o precios de cierre (por ejemplo, Colegio de Escribanos de CABA) | CABA; mensual | Agregado por zona o ciudad (desagregación a confirmar) | Brecha estimada entre precio publicado y de cierre | Ajuste del gap y del valor post-obra | Disponibilidad y nivel de desagregación por confirmar |

### Complementarias (Pre-Entrega 3)

| Fuente | Granularidad y mecanismo de unión | Variable derivada | Comparación que permite |
| --- | --- | --- | --- |
| [BA Data — Estaciones de subte](https://data.buenosaires.gob.ar/dataset/subte-estaciones) y [ferrocarril](https://data.buenosaires.gob.ar/dataset/estaciones-ferrocarril) | Puntos; distancia a la estación más cercana | Distancia en metros | Diferencias de USD/m² dentro de un mismo estrato |
| [BA Data — Espacios verdes](https://data.buenosaires.gob.ar/dataset/espacios-verdes) | Polígonos o puntos; distancia al más cercano, según tamaño o tipo | Distancia en metros | Ídem |
| [BA Data — Establecimientos educativos](https://data.buenosaires.gob.ar/dataset/establecimientos-educativos) | Puntos; distancia por tipo de institución (gestión y nivel) | Distancia en metros | Ídem |


## Estructura del repositorio

```
├── README.md
├── data/
│   ├── raw/
│   │   ├── remax_caba_propiedades_muestra.csv   # muestra de la base raw
│   │   └── (base completa: se descarga desde Drive, ver Reproducción)
│   ├── processed/
│   │   ├── remax_deptos_limpio.csv              # base analítica (9.500 × 41)
│   │   └── registro_limpieza.csv                # registro de cada paso de limpieza
│   ├── excepciones_manuales.csv                 # correcciones puntuales documentadas
│   └── diccionario_datos.md                     # diccionario de variables
├── notebooks/
│   ├── 01_extraccion_remax.ipynb
│   └── 02_limpieza_remax.ipynb
├── src/
│   ├── scraper_remax.py                         # extractor (requests, reintentos, paralelismo)
│   ├── limpieza.py                              # auditorías, registro de pasos, excepciones
│   ├── patrones.py                              # expresiones regulares
│   └── diagnostico.py                           # validación de ambientes, faltantes y outliers
└── reports/
```

La base raw completa (36 MB) no se versiona por su tamaño. En `data/raw/` se
incluye una muestra representativa, y el esquema completo figura en el
diccionario de datos.


## Reproducción

Los notebooks se ejecutan en Google Colab. Al iniciar, clonan el repositorio
(o lo actualizan si ya está clonado) y trabajan desde su raíz, de modo que los
módulos de `src/` y las rutas de `data/` funcionan sin configuración adicional.
No se usan rutas personales.

1. **Extracción (opcional).** `01_extraccion_remax.ipynb` genera una nueva
   corrida del extractor. Para reproducir el análisis no es necesario: se usa
   la corrida publicada.
2. **Limpieza.** `02_limpieza_remax.ipynb` descarga la base raw desde Google
   Drive con `gdown` (ID definido al inicio del notebook), aplica la limpieza y
   exporta los resultados a `data/processed/`.
3. **Controles.** Verificar el registro de limpieza y los controles finales del
   notebook (9.500 avisos, sin identificadores duplicados).
4. **Análisis.** Las etapas siguientes parten de
   `data/processed/remax_deptos_limpio.csv`.


## Cambios a partir de la devolución de la PreEntrega 1

| Observación | Cambio realizado |
| --- | --- |
| El contexto requería mayor profundidad | Se incorporaron el crédito hipotecario, la dolarización, la iliquidez y la brecha entre precio publicado y de cierre, y su efecto sobre la señal de descuento y la salida del flipping |
| Lo predictivo y prescriptivo quedó como intención futura | Se definió la variable a estimar (PER), su validación (holdout, MAE, MAPE, cobertura) y una regla de decisión con umbrales, presupuesto y mínimo de comparables |
| Mayor dispersión no implica más oportunidades | H2 se reformuló en términos condicionales a estratos homogéneos, descartando errores de carga como causa alternativa |
| El valor post-obra y el costo de flipping no diferenciaban sus componentes | El costo se descompone en calidad, alcance, tiempo, transacción y contingencias; el valor post-obra se estima con tres escenarios |
| La variable "estado" es ruidosa | Se decidió usarla como señal imperfecta con categorías agrupadas, sin imputar, con validación manual |
| Definir operativamente qué es una propiedad "barata" | Benchmark de comparables con mínimo de casos, ampliación jerárquica, control de dispersión y separación de las unidades que necesitan obra |
| Fuentes externas sin nivel ni comparación | Se separaron indispensables y complementarias, indicando nivel, mecanismo de unión y aporte a la regla |
| El scraper ocupaba una celda muy extensa | La lógica se trasladó a `src/scraper_remax.py`; el notebook contiene configuración, ejecución y controles |
| Chequeos repetidos, patrones redefinidos y correcciones hardcodeadas en la limpieza | Auditorías encapsuladas en `src/limpieza.py`, patrones únicos en `src/patrones.py`, excepciones en `data/excepciones_manuales.csv` y registro de cada paso |
| El README mencionaba Argenprop | Se corrigió la fuente (RE/MAX) y se documentaron la ejecución, las salidas de cada notebook y la ubicación de los datos |


## Observaciones pendientes y plan

| Pendiente | Plan |
| --- | --- |
| Barrio oficial y comuna | Unión espacial con los polígonos de BA Data, antes de construir los comparables |
| Variables derivadas del texto | Booleanas con expresiones regulares (reciclado a nuevo, a refaccionar, luminoso, vista, etc.), amenities binarias, cochera, `Estado_Propiedad`, `Estado_Agrupado` y `Reciclado_Parcial` |
| Cálculo de KPIs | Superficie homogeneizada, benchmark, gap de subvaluación, PER y categorías de la definición de propiedad barata |
| Imputación de expensas | KNN después del tratamiento de outliers, solo para el costo de tenencia |
| Validación del clasificador de estado | Lectura manual de 50 avisos por categoría |
| Costo de refacción | Cotizaciones por nivel de obra (liviana, media, integral), actualizadas con el ICC y convertidas a USD |
| Tipo de cambio y brecha de cierre | Definir la fuente del tipo de cambio y confirmar la disponibilidad de estadísticas de escrituras |
| Permanencia en el mercado | Nuevas capturas del extractor para medir la primera y la última aparición de cada aviso |
| EDA y validación preliminar de hipótesis | Estadísticos robustos, distribuciones por barrio y estado, análisis espacial y tests de H1 y H2 |
