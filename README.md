# Real Estate Analytics 🏠
 
## Inteligencia de mercado inmobiliario en CABA — Analítica Descriptiva (ITBA)
 
Trabajo Práctico Integrador de la materia **Analítica Descriptiva** de la
Licenciatura en Analítica Empresarial y Social del ITBA.
 
### Integrantes
 
- Dante Tosoratti
- Martina Risso
- María Sol Allievi
- Tomás Agustín Picciolo
### Guía de lectura
 
| Descripcion | ir a |
| --- | --- |
| Qué se hizo y para quién | [Descripción](#descripción-del-proyecto), [Interlocutor](#interlocutor) |
| KPIs, hipótesis y su estado | [KPIs](#kpis), [Hipótesis](#hipótesis), [Estado de las hipótesis](#estado-de-las-hipótesis) |
| Cómo se trató el estado de la propiedad | [Tratamiento de `Estado_Propiedad`](#tratamiento-de-la-variable-estado_propiedad) |
| Datos, limpieza y fuentes externas | [Datos](#datos), [Fuentes externas](#fuentes-externas) |
| Hallazgos del análisis | [Principales hallazgos](#principales-hallazgos-del-análisis-exploratorio), [Modelo explicativo y benchmark ajustado](#modelo-explicativo-y-benchmark-ajustado), [Modelo económico de flipping](#modelo-económico-de-flipping) |
| Recomendaciones y dashboard | [Recomendaciones](#recomendaciones-para-el-fondo), [Dashboard](#dashboard) |
| Qué cambió en la PreEntrega 3 | [Cambios en la PreEntrega 3](#cambios-en-la-preentrega-3) |
| Qué cambió desde la PreEntrega 1 | [Cambios a partir de la devolución](#cambios-a-partir-de-la-devolución-de-la-preentrega-1) |
| Cómo reproducir el análisis | [Reproducción](#reproducción), [Estructura del repositorio](#estructura-del-repositorio) |
| Limitaciones y pendientes | [Limitaciones](#limitaciones), [Observaciones pendientes](#observaciones-pendientes-y-plan) |
 
 
## Descripción del proyecto
 
El proyecto analiza la oferta de departamentos usados en venta en la Ciudad
Autónoma de Buenos Aires (CABA) para detectar propiedades publicadas por
debajo del valor de propiedades comparables y, dentro de ese conjunto,
identificar oportunidades de refacción y reventa (flipping).
 
Se aborda como un problema de **valuación relativa**: primero se estima cuánto
debería valer una propiedad según comparables similares y luego se compara ese
valor con el precio publicado. La diferencia es la señal de subvaluación. Para
las unidades que necesitan obra, esa señal es el punto de partida para evaluar
si el descuento compensa el costo de la refacción y los demás costos de la
operación.
 
**Alcance.** Departamentos usados en venta en todos los barrios de CABA
(se excluyen pozo, preventa, en construcción y a estrenar), con precios en USD
y el aviso individual como unidad de análisis. Los datos son una única corrida
del extractor; para medir permanencia en el mercado harían falta capturas
sucesivas. El filtro al universo de análisis se aplica en la limpieza, de modo
que la base raw permanece completa y reproducible.
 
 
## Interlocutor
 
El producto está dirigido a un **Fondo de Inversión Inmobiliario**, que lo usa
para dos decisiones:
 
1. **Priorizar qué propiedades visitar u ofertar**, a partir de un ranking de
   subvaluación.
2. **Decidir si conviene comprar y refaccionar una unidad puntual**, a partir
   del margen potencial de flipping.
El resultado se consume mediante dos rankings exportables
(`data/processed/ranking_visitas.csv` y `data/processed/flipping_ranking_priorizado.csv`)
y un tablero interactivo (ver [Dashboard](#dashboard)).
 
**Contexto de negocio.** Cuatro características del mercado condicionan la señal
de descuento y la viabilidad del flipping: el crédito hipotecario es escaso y
cíclico (menos demanda en la reventa); los precios están dolarizados pero parte
de los costos se paga en pesos; la iliquidez hace que una propiedad pueda
permanecer publicada meses; y los datos son precios de publicación, no de
cierre, por lo que el gap es una señal de descuento frente a comparables
publicados y no frente al precio efectivo de transacción.
 
 
## Preguntas por nivel analítico
 
- **Descriptivo.** ¿Cuál es el USD/m² mediano y su dispersión por barrio? ¿Qué diferencia hay entre departamentos que necesitan obra y reciclados comparables?
- **Diagnóstico.** ¿Qué variables explican las diferencias de precio entre comparables? ¿El descuento por obra es similar en todos los barrios? ¿La dispersión dentro de estratos homogéneos revela oportunidades?
- **Predictivo.** ¿Cuál es el **Precio Esperado Reciclado (PER)** de una propiedad que necesita obra, es decir, el valor que tendría después de la refacción?
- **Prescriptivo.** Dados el PER, el precio publicado y los costos de la operación, ¿qué propiedades conviene comprar, respetando un margen mínimo, un presupuesto y un soporte estadístico mínimo?
## Arquitectura analítica
 
**Variable a estimar.** El **PER** es la mediana del USD/m² homogeneizado de las
propiedades comparables en buen estado o recicladas, multiplicada por la
superficie homogeneizada de la propiedad. No es observable para las unidades
que necesitan obra: se infiere por transferencia desde las comparables, bajo el
supuesto de **ignorabilidad condicional** (dos propiedades del mismo estrato
difieren en valor esperado solo por su estado de conservación). Es una
limitación explícita.
 
**Validación.** Holdout 80/20 sobre propiedades con estado conocido,
estratificado por barrio y con cinco semillas; métricas MAE, MAPE y cobertura
(proporción de casos cuyo precio real cae dentro del rango intercuartílico).
Resultado (notebook 03, sección 11): el benchmark tiene un error porcentual
mediano (MdAPE) de 14,7 % y un MAPE de 19,5 %; el PER, de 14,0 % y 17,6 %. El
MAPE supera el criterio inicial (15 %) porque lo influyen propiedades muy
alejadas de sus comparables; el error típico se ubica cerca del 15 %. El umbral
de gap del 25 % supera ambas medidas de error.
 
**Regla de decisión.** Se recomienda comprar una propiedad si y solo si se
cumplen a la vez: margen potencial ≥ umbral de margen; gap de subvaluación
inicial ≥ umbral de gap; inversión total ≤ presupuesto; comparables del estrato
≥ mínimo; y margen no negativo en el escenario conservador. Está implementada en
`src/flipping.py` (`aplicar_regla`) con los umbrales de `src/config.py`
(`MARGEN_MINIMO_PCT` = 15 %, `PRESUPUESTO_MAX_USD` = USD 300.000,
`DESCUENTO_NEGOCIABLE_PCT` = 10 %, `MIN_COMPARABLES` = 10). Además calcula el
**precio máximo de oferta** de cada unidad: el que deja el margen mínimo en el
escenario base.
 
 
## KPIs
 
Todos los KPIs están calculados. Los que dependen solo de los avisos están en
`data/processed/remax_deptos_features.csv`; los del modelo económico, en
`data/processed/flipping_modelo_economico.csv`.
 
| KPI | Definición | Dónde |
| --- | --- | --- |
| Superficie homogeneizada (m²) | Cubierta + 0,5 × (total − cubierta) | Notebook 03 |
| USD/m² homogeneizado | Precio publicado / superficie homogeneizada | Notebook 03 |
| Benchmark USD/m² | Mediana del USD/m² homogeneizado del grupo de comparables | Notebook 03 |
| Precio esperado (USD) | Benchmark × superficie homogeneizada | Notebook 03 |
| Gap de subvaluación (%) | (Precio esperado − precio publicado) / precio esperado × 100 | Notebook 03 |
| Gap de estado (%) | (Mediana USD/m² reciclada − mediana USD/m² necesita obra) / mediana reciclada × 100 | Notebook 04 |
| PER (USD) | Mediana del USD/m² de comparables en buen estado o reciclados × superficie. Escenarios: P25 (conservador), mediana (base) y P75 (optimista) | Notebook 03 |
| Potencial bruto (%) | PER frente al precio publicado, como paso previo al margen | Notebook 03 |
| Costo de obra (USD) | Superficie cubierta × costo USD/m² según nivel de obra × (1 + contingencia) | Notebook 07 |
| Costo de tenencia (USD) | Expensas en USD × (meses de obra + meses de venta) + costo de oportunidad del capital | Notebook 07 |
| Inversión total (USD) | Compra + costos de compra + obra + tenencia | Notebook 07 |
| Margen potencial de flipping (ROI, %) | (PER × (1 − costos de venta) − inversión total) / inversión total | Notebook 07 |
 
### Costo de la operación de flipping
 
El costo no es un único valor por m²: se descompone en **calidad** (tres niveles
de obra con costo propio), **alcance** (superficie intervenida), **tiempo**
(meses de obra y comercialización, con expensas y capital inmovilizado),
**transacción** (compra y venta) y **contingencias**.
 
El índice de costo de la construcción del INDEC no es un costo por m², así que el
costo de refacción se triangula con tres fuentes: (1) un costo base por nivel de
obra (liviana, media, integral) verificado contra informes de cámaras del
sector, (2) su actualización con el ICC del INDEC y conversión a USD, y (3) la
**cota implícita del mercado**: la diferencia de USD/m² entre unidades
recicladas y las que necesitan obra, que indica cuánto paga el mercado por la
obra. Los valores por escenario y su fuente están en
`data/supuestos_flipping.csv` (por ejemplo, obra media de 400 a 650 USD/m² e
integral de 1.000 a 1.300 USD/m²). El nivel de obra se asigna según el aviso
("a reciclar" → integral; "a actualizar" → media) y, sin evidencia, se usa el
integral como caso conservador.
 
| Parámetro | Valor inicial |
| --- | --- |
| Costos de compra | 6 % a 8 % del precio |
| Costos de venta | 4 % a 6 % del precio de reventa |
| Contingencia de obra | 10 % a 20 % del costo de obra |
| Plazo de obra | 2 a 6 meses según nivel |
| Plazo de comercialización | 3 a 9 meses |
 
 
## Definición operativa de propiedad "barata"
 
Una propiedad es **barata** cuando su precio por m² es significativamente
inferior al de sus comparables, en una magnitud que no se explica por la
dispersión normal del segmento ni por su estado de conservación.
 
**Comparables.** Departamentos usados que comparten barrio oficial (asignado
con coordenadas y límites de BA Data), ambientes (1, 2, 3, 4 y 5 o más), banda
de superficie (terciles dentro de cada cantidad de ambientes) y banda de
antigüedad (hasta 10, 11 a 30, 31 a 50, más de 50 y sin dato). Cada grupo debe
tener al menos **10 propiedades**; si no, se amplía hasta el primer nivel que
lo cumpla:
 
| Nivel | Criterio del grupo |
| --- | --- |
| 1 | Barrio × ambientes × banda de superficie × banda de antigüedad |
| 2 | Barrio × ambientes × banda de superficie |
| 3 | Comuna × ambientes × banda de superficie |
| 4 | Comuna × ambientes |
 
Si ningún nivel alcanza el mínimo, la propiedad queda **sin benchmark**. Del
cálculo se excluyen la propia propiedad, los avisos con valores extremos o
ambientes dudosos y los clasificados como "necesita obra".
 
**Criterio.** Es barata si cumple las tres condiciones: (1) gap de subvaluación
≥ 25 %; (2) USD/m² por debajo del percentil 25 de su grupo, que controla la
dispersión; y (3) no está clasificada como "necesita obra", porque esos casos
son más baratos por una razón identificable y se evalúan con el margen de
flipping. Las que cumplen pero tienen indicadores de posible error de carga se
revisan manualmente.
 
| Categoría | Condición |
| --- | --- |
| **Barata** | Cumple el criterio, sin indicadores de error |
| **Barata — requiere verificación** | Cumple el criterio, con indicadores de posible error de carga |
| **A refaccionar con descuento** | Necesita obra y su gap es positivo → se evalúa con el margen de flipping |
| **Precio de mercado** | No cumple el criterio |
| **Sin benchmark** | Ningún nivel alcanza 10 propiedades |
 
**Umbral.** El 15 % inicial se recalibró a **25 %** (notebook 03, sección 7.3):
con 15 %, el 18,6 % de los avisos resultaba barato (el percentil 75 del gap es
13,8 %), lo que refleja dispersión normal más que subvaluación; el 25 % se
aproxima al percentil 90 e identifica al 8,8 % de los avisos. El coeficiente
0,5 de la superficie descubierta es un supuesto: con 0,3 y 0,7 la clasificación
coincide en el 97,3 % y el 97,7 % de los avisos (sección 7.4).
 
**Cifras de propiedades baratas.** Corresponden a definiciones distintas:
 
| Cifra | Qué cuenta | Dónde |
| --- | --- | --- |
| 716 | `Barata` (sin indicadores de error), base completa | Notebook 03 |
| 836 | `Barata` + `Barata_requiere_verificacion` (716 + 120) | Notebook 03 |
| 822 | Baratas del benchmark jerárquico entre los 9.194 avisos con benchmark ajustado (sin las que necesitan obra) | Notebook 11 |
| 326 | De esas 822, las que también son baratas con el benchmark ajustado | Notebook 11 |
| 249 | De esas 326, las que no tienen indicadores de error: **candidatas de mayor confianza** | Notebook 09 |
 
 
## Tratamiento de la variable `Estado_Propiedad`
 
`Estado_Propiedad` se construye con expresiones regulares sobre el título y la
descripción. Es una **señal imperfecta**: baja cobertura (la mayoría de los
avisos no menciona la condición), sesgo de declaración y menciones parciales
("baño reciclado" no describe toda la unidad). Decisión adoptada:
 
- `Estado_Propiedad` tiene cuatro categorías (`Necesita_obra`, `Buen_estado`,
  `Reciclada_refaccionada`, `Sin_clasificar`) y se usa en el diagnóstico (H1).
  `Estado_Agrupado` tiene tres (`Necesita_obra`, `Buen_o_reciclada`,
  `Sin_clasificar`) y arma los comparables.
- `Sin_clasificar` es una categoría propia: no se imputa ni se asume buen estado.
- `Reciclado_Parcial` marca menciones de reciclado de un solo ambiente (343
  avisos); no cuentan como reciclada integral al construir el PER.
Resultado: 63,5 % sin clasificar, 21,6 % buen estado, 10,3 % reciclada o
refaccionada y 4,6 % necesita obra (439 avisos).
 
**Criterio de revisión manual.** Los cuatro integrantes comparan la
clasificación automática con la lectura del título y la descripción:
`Necesita_obra` si el aviso ofrece la unidad para reciclar, refaccionar o hacer
flipping de forma explícita; `Buen_o_reciclada` si dice que está en buen estado
o ya fue reciclada; `Sin_clasificar` para el resto y las señales mezcladas. Si
hay señales opuestas, prevalece el estado descripto de forma específica y
repetida, salvo que se describa obra concreta. Las diferencias con la
clasificación automática, que da prioridad a las señales de obra, son lo que la
validación mide.
 
### Qué se midió sobre la calidad de la señal
 
| Aspecto | Resultado |
| --- | --- |
| Señales contradictorias (notebook 03, sec. 5.4) | 66 de los 439 `Necesita_obra` (15 %) también mencionan buen estado o reciclado integral; con otros 20 casos suman 78 avisos marcados con `Flag_Senal_Contradictoria` |
| Sesgo de declaración (sec. 6.4) | Casi no informan el estado los edificios de hasta 10 años (87 % sin clasificar) ni los avisos sin antigüedad (99 %), frente a 51–55 % en los de más de 30 años; los avisos más caros lo informan menos (75 % contra 57 %) |
| Cruce con señales no textuales (sec. 6.5 y 6.6) | Los `Necesita_obra` son los más antiguos (mediana de 56 años contra 47 y 36) y tienen las expensas por m² más bajas: respaldo indirecto, no reemplaza la validación manual |
| Sensibilidad a la definición de "reciclada" (sec. 8.3) | El potencial bruto mediano se mantiene entre 21 % y 31 %; con solo comparables de estado informado, las `Barata` pasan de 716 a 663 |
| Revisión de los 78 avisos contradictorios (sec. 10.3) | Coincidencia de 79,5 % (62 de 78): 59 de 68 `Necesita_obra` (86,8 %) y 3 de 10 `Reciclada_refaccionada`, porque 7 eran unidades a renovar con frases como "gran potencial de reciclado" |
| Doble lectura independiente de 50 avisos estratificados (notebook 06) | Acuerdo entre evaluadores de 66 % (kappa = 0,54). Contra la referencia, el clasificador tiene un accuracy de 78 % (kappa = 0,70), con precisión de 82 % en `Necesita_obra` y 75 % en `Reciclada_refaccionada`, y recall de 100 % en ambas. Los 17 desacuerdos los adjudicó uno de los evaluadores |
| Muestra aleatoria de 50 `Reciclada_refaccionada` (sec. 10.4) | 47 de 50 confirmados (94 %; intervalo de Wilson 95 %: 84 %–98 %). Supera el 80 % fijado como criterio, por lo que no se modificó el patrón |
 
 
## Hipótesis
 
- **H1. Descuento por condición.** Los departamentos que necesitan obra tienen
  un USD/m² menor que los reciclados, aun dentro de un mismo estrato de barrio,
  ambientes y superficie.
- **H2. Dispersión condicional.** Una mayor dispersión del USD/m² dentro de un
  estrato homogéneo es indicativa de oportunidades; la dispersión sobre
  agregados menos granulares se interpreta como baja confiabilidad del
  benchmark. Antes se descartan errores de carga como causa alternativa.
- **H3. Oportunidades de flipping.** En una parte de los casos que necesitan
  obra, el descuento de entrada supera el costo de refacción, la transacción,
  la tenencia y las contingencias, con margen positivo aun en el escenario
  conservador del valor post-obra.
## Datos
 
**Fuente principal: RE/MAX Argentina.** Extractor propio sobre la API interna
del sitio, restringido a CABA y venta, en dos etapas: listado paginado y
detalle de cada propiedad.
 
| Característica | Valor |
| --- | --- |
| Fecha de corte | 26 de septiembre de 2026 (aproximada, según la fecha de creación del archivo) |
| Registros raw | 17.023 avisos, 29 variables |
| Base analítica | 9.500 departamentos usados, 41 variables |
| Moneda | Precio en USD; expensas en ARS (se convierten con el tipo de cambio de `src/config.py`) |
 
`Fecha_Publicacion` llega vacía (100 % de faltantes), por lo que la permanencia
en el mercado requeriría capturas sucesivas.
 
**Limpieza.** La mayor parte de la reducción responde al alcance (43,3 % de la
raw) y no a problemas de calidad (0,9 %).
 
| Paso | Excluidos | Restantes |
| --- | ---: | ---: |
| Base raw | — | 17.023 |
| Tipologías distintas de departamento | 5.358 | 11.665 |
| PH clasificados como departamento | 53 | 11.612 |
| Propiedades nuevas (pozo, preventa, a estrenar) | 1.963 | 9.649 |
| Duplicados | 132 | 9.517 |
| Excepciones manuales (ventas en bloque y un alquiler) | 12 | 9.505 |
| Precio publicado en pesos | 2 | 9.503 |
| Superficies imposibles | 3 | 9.500 |
 
- Los valores imposibles o de relleno se reemplazan por faltantes. Ningún mecanismo de faltantes es completamente aleatorio (Welch, chi-cuadrado, regresión logística), por lo que no se imputan en la base limpia; las expensas se imputan con KNN solo para el costo de tenencia.
- Los outliers se detectan con Box-Cox y Tukey y con la distancia de Mahalanobis. Solo se excluyen errores comprobados; los atípicos genuinos se conservan y marcan (`Flag_*`), porque los precios por m² muy bajos pueden ser las oportunidades buscadas.
El detalle de cada paso está en `data/processed/registro_limpieza.csv` y el
significado de cada variable, en `data/diccionario_datos.md`.
 
 
## Fuentes externas
 
Una fuente es **indispensable** si sin ella no puede calcularse algún paso de
la regla de decisión; las **complementarias** explican diferencias de precio
dentro de un mismo estrato.
 
| Fuente | Nivel y unión | Variable y aporte | Limitaciones |
| --- | --- | --- | --- |
| [BA Data — Barrios](https://data.buenosaires.gob.ar/dataset/barrios) (**integrada**; CC-BY-2.5-AR) | Polígonos; unión espacial punto en polígono con latitud y longitud | `Barrio_Oficial` y `Comuna`: estratos del benchmark y del PER | 4 avisos con coordenadas fuera de CABA (uno excluido, tres asignados por etiqueta y marcados) |
| [INDEC — Índice del Costo de la Construcción](https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-33) | Serie mensual; unión por fecha | Factor de actualización del costo de obra | Es un índice, no un costo por m²; está en pesos |
| Tipo de cambio (**integrado**: dólar MEP, DolarHub, 02/11/2026) | Valor a la fecha de análisis | Expensas en USD: tenencia, inversión y margen | ±20 % casi no cambia el resultado (solo afecta a las expensas) |
| Estadísticas de escrituras (por ejemplo, Colegio de Escribanos de CABA) | Agregado mensual por zona o ciudad | Brecha entre precio publicado y de cierre | Disponibilidad y desagregación por confirmar |
| [BA Data — Subte](https://data.buenosaires.gob.ar/dataset/subte-estaciones), [ferrocarril](https://data.buenosaires.gob.ar/dataset/estaciones-ferrocarril), [espacios verdes](https://data.buenosaires.gob.ar/dataset/espacios-verdes), [establecimientos educativos](https://data.buenosaires.gob.ar/dataset/establecimientos-educativos) y [hospitales](https://data.buenosaires.gob.ar/dataset/hospitales) (complementarias) | Puntos o polígonos; distancia de cada aviso al elemento más cercano | Distancia al subte, al tren, a plazas o parques, a escuelas y a hospitales: pregunta diagnóstica 1 | Son fotos vigentes a la fecha de descarga; no informan frecuencia, calidad ni tamaño (hospitales: solo públicos de la Ciudad) |
 
 
## Estructura del repositorio
 
```
├── README.md
├── requirements.txt                             # dependencias (pip install -r requirements.txt)
├── data/
│   ├── raw/                                     # muestra de la base raw (la completa se descarga desde Drive)
│   ├── processed/
│   │   ├── remax_deptos_limpio.csv              # base analítica (9.500 × 41)
│   │   ├── remax_deptos_features.csv            # variables derivadas y KPIs (9.499 × 100)
│   │   ├── registro_limpieza.csv / registro_features.csv  # registro de pasos
│   │   ├── oportunidades_benchmark_ajustado.csv # brechas y categoría por aviso (notebook 11)
│   │   ├── flipping_modelo_economico.csv        # costos, ROI y decisión de las 428 unidades a reciclar (notebook 07)
│   │   ├── flipping_ranking_priorizado.csv      # las 428 ordenadas por descuento requerido (notebook 07)
│   │   └── ranking_visitas.csv                  # 249 candidatas de mayor confianza (notebook 09)
│   ├── external/                                # fuentes externas (se descargan al ejecutar el notebook 03)
│   ├── validation/                              # planillas de la doble lectura manual (notebook 06)
│   ├── supuestos_flipping.csv                   # supuestos de costos por componente y escenario, con fuente
│   ├── excepciones_manuales.csv                 # correcciones puntuales documentadas
│   └── diccionario_datos.md / diccionario_variables.csv
├── notebooks/                                   # 01 a 11, ver Reproducción
├── src/
│   ├── config.py                                # parámetros, rutas y supuestos centralizados
│   ├── datos.py, scraper_remax.py, scrapers_alternativos.py  # descarga de la raw y extractores
│   ├── limpieza.py, patrones.py, diagnostico.py # limpieza, expresiones regulares y validaciones
│   ├── benchmark.py, eda.py                     # benchmark jerárquico, PER y estadísticos
│   ├── modelos.py                               # regresión hedónica y benchmark ajustado
│   ├── flipping.py                              # costos, ROI, precio máximo de oferta y regla de decisión
│   └── dashboard.py, dashboard_plantilla.html   # generan dashboard/index.html
├── dashboard/index.html                         # dashboard interactivo (se abre en el navegador)
├── tests/                                       # python -m pytest tests/
└── reports/
    ├── hallazgos_negocio.md                     # hallazgos que cambian el rumbo del negocio
    ├── informe_preentrega_1.docx / .pdf         # informe ejecutivo de la Pre-Entrega 1
    ├── validacion_*.csv                         # benchmark, muestra de estado, contradictorios y muestra de reciclada
    └── dashboard/                               # capturas de las vistas principales
```
 
 
## Reproducción
 
Los notebooks se ejecutan sobre la copia local del repositorio (Jupyter, VS Code
o Colab con el repositorio ya descargado). No clonan ni actualizan nada: la
primera celda ubica la raíz del proyecto (la carpeta que contiene `src/`), de
modo que los módulos y las rutas de `data/` funcionan sin configuración. No se
usan rutas personales. Las dependencias están en `requirements.txt` y los tests
se ejecutan con `python -m pytest tests/`.
 
**Parámetros centralizados.** Los umbrales, rutas y supuestos que afectan los
resultados (gap de 25 %, mínimo de 10 comparables, escenarios del PER, costos de
transacción) están en `src/config.py`, y los supuestos de costos de flipping, en
`data/supuestos_flipping.csv`; ningún valor se escribe a mano en un notebook.
 
**Versión de la base raw.** La raw completa (36 MB, no versionada) se descarga
desde Google Drive solo si falta en `data/raw/` y se verifica con su huella
SHA-256 (`RAW_SHA256` en `src/config.py`, `obtener_raw()` de `src/datos.py`); si
no coincide con la extracción de referencia, la ejecución se detiene.
 
| Notebook | Qué hace |
| --- | --- |
| 01 Extracción | Corrida del extractor (opcional: se usa la corrida publicada) |
| 02 Limpieza | Obtiene la raw, limpia y exporta a `data/processed/` |
| 03 Features y KPIs | Barrios oficiales, variables, estado, benchmark, PER y validación del benchmark |
| 04 EDA | Preguntas descriptivas y diagnósticas, con evidencia preliminar de las hipótesis |
| 05 Validación y robustez | Sensibilidad del PER a referencias contradictorias y a señales de estado |
| 06 Validación manual | Doble lectura independiente del clasificador de estado |
| 07 Modelo económico | Costos, ROI en tres escenarios, precio máximo de oferta, regla de decisión y sensibilidad (`src/flipping.py`) |
| 08 Evaluación de hipótesis | Evalúa H1, H2 y H3 con pruebas estadísticas y análisis de robustez. Incluye un análisis exploratorio de micromercados por barrio |
| 09 Resultados y recomendaciones | Ranking de visitas y recomendaciones (conviene correrla después de la 11) |
| 10 Modelo explicativo | Regresión hedónica validada fuera de muestra (`src/modelos.py`) |
| 11 Benchmark ajustado | Contrasta el benchmark jerárquico con el ajustado por antigüedad y características |
 
 
## Principales hallazgos del análisis exploratorio
 
El detalle está en `notebooks/04_eda.ipynb`, sección 12, y las implicancias para
el fondo, en [`reports/hallazgos_negocio.md`](reports/hallazgos_negocio.md).
 
- **La ubicación es el principal determinante del precio.** La mediana del
  USD/m² va de USD 917 en Villa Lugano a USD 5.110 en Puerto Madero. La
  antigüedad es la variable física más asociada con el precio por m²
  (Spearman ρ = −0,48).
- **El descuento por necesitar obra es real y homogéneo.** Las unidades que
  necesitan obra se publican, en la mediana, 17,4 % por debajo del benchmark
  (Mann-Whitney, p < 0,001) y el descuento no difiere significativamente entre
  comunas (Kruskal-Wallis, p = 0,26).
- **La categoría del edificio explica diferencias que el benchmark no captura.**
  Los avisos con gimnasio, pileta, SUM o seguridad se publican entre 15 y 27
  puntos por encima de sus comparables (lo que motivó el benchmark ajustado).
- **El mercado toma las oportunidades.** Los avisos reservados o en negociación
  están 8,4 puntos más baratos respecto de su benchmark que los activos, y las
  baratas tienen más operaciones en curso (34 % contra 23 %). Las que requieren
  verificación se comportan como las de precio de mercado, lo que sugiere que
  una parte son errores de carga.
- **El flipping no cierra a precio publicado.** 290 unidades que necesitan obra
  tienen un potencial bruto (antes de la obra) superior a los costos de
  transacción, pero al descontar la obra, la tenencia y el costo de
  oportunidad, ninguna es rentable en el escenario conservador (ver
  [Modelo económico de flipping](#modelo-económico-de-flipping)).
- **Micromercados y dispersión.** En 43 barrios (9.433 avisos),
  se encontró una asociación positiva moderada entre la dispersión
  relativa de precios y la proporción de propiedades clasificadas
  como baratas (Spearman ρ = 0,48; p = 0,0011).
  Es una señal exploratoria para priorizar barrios, no una
  confirmación de rentabilidad.

### Estado de las hipótesis
 
| Hipótesis | Resultado (notebook 08) |
| --- | --- |
| **H1.** Descuento por condición | **Se sostiene.** Las unidades que necesitan obra se publican 17,5 puntos por debajo de sus comparables (IC 95 % bootstrap: −19,9 a −15,3; Mann-Whitney, p < 0,001; probabilidad de superioridad 0,75). Se mantiene sin señales contradictorias (−16,4) y en los estratos más finos (−17,3), y no difiere entre comunas (Kruskal-Wallis, p = 0,26). El modelo hedónico lo confirma (−14 % frente a buen estado) |
| **H2.** Dispersión condicional | **Se sostiene parcialmente.** En 289 estratos, la dispersión se asocia con la proporción de baratas sin indicadores de error (Spearman 0,43; IC 95 %: 0,33 a 0,53), también al controlar por el tamaño del estrato (0,45). Pero los estratos más dispersos concentran más casos que requieren verificación (0,2 % en el quintil menos disperso contra 1,5 % en el más disperso): la dispersión sirve para priorizar la revisión, no como prueba de oportunidad |
| **H3.** Oportunidades de flipping | **No se sostiene (reformulada).** Con los supuestos con fuente, 0 de 428 unidades son rentables en el escenario conservador (IC 95 % Wilson: 0 a 0,9 %) y 2 en el base. El descuento de entrada cubre la transacción y la tenencia, pero no la obra |
 
Los tests se recalculan en `notebooks/08_evaluacion_hipotesis.ipynb` desde
`data/processed/`.
 
 
## Modelo explicativo y benchmark ajustado
 
El detalle está en `notebooks/10_modelo_explicativo.ipynb` y
`notebooks/11_benchmark_ajustado.ipynb`; el código, en `src/modelos.py`.
 
**Modelo explicativo (notebook 10).** Regresión por mínimos cuadrados del
logaritmo del USD/m² homogeneizado (9.232 avisos, R² = 0,71) con efectos fijos
de barrio, ambientes, superficie, antigüedad, 19 características y estado, y
errores estándar robustos (HC3). Cada coeficiente es la diferencia porcentual
del USD/m² controlando por las demás variables; es una asociación, no una
relación causal.
 
- Con lo demás constante, una unidad que necesita obra se publica
  aproximadamente 14 % por debajo de una en buen estado y 22 % por debajo de
  una reciclada. Es menos que la comparación directa (25 %), porque parte de esa
  brecha se explica por ubicación y características.
- En un holdout repetido con cinco semillas, el modelo tiene un MAPE de 15,3 %,
  frente a 19,7 % del benchmark jerárquico.
**Benchmark ajustado (notebook 11).** Usa el modelo con predicciones fuera de
muestra (validación cruzada de cinco pliegues) como benchmark que considera
antigüedad y características del edificio.
 
- El MAPE baja de 19,6 % a 15,3 % (y el error mediano de 14,8 % a 11,6 %), tanto
  en avisos en buen estado como en reciclados.
- De las 822 propiedades que el benchmark jerárquico marca como baratas (sin las
  que necesitan obra), 326 (40 %) lo siguen siendo con el ajuste; las otras
  tienen menos amenities, en particular cochera. Las 326 confirmadas por ambos
  métodos son las candidatas de mayor confianza.
- El PER del modelo económico es consistente con el del modelo (razón mediana
  1,04; Spearman 0,97), por lo que el supuesto de reventa no está sesgado al alza.
- Un híbrido que corrige la regresión con la mediana local de los residuos no
  mejoró la precisión y se descartó.
Ambos modelos usan precios de publicación y no observan el estado del edificio,
el piso ni las terminaciones: sirven para priorizar y contrastar, no para tasar.
 
 
## Modelo económico de flipping
 
El detalle está en `notebooks/07_modelo_economico_flipping.ipynb`; la lógica, en
`src/flipping.py`; los supuestos, con su fuente, en `data/supuestos_flipping.csv`.
 
- **Nivel de obra por aviso.** Integral si el aviso dice "a reciclar" o "a
  refaccionar", o si no hay evidencia (caso conservador): 311 unidades. Media si
  solo hay señales débiles ("a actualizar"): 117 unidades. En los 12 barrios del
  cuartil superior de USD/m² se aplica un factor de terminación premium.
- **Resultado.** El ROI mediano es de −53 % (conservador), −39 % (base) y −19 %
  (optimista). Ninguna unidad es rentable en el escenario conservador, 2 lo son
  en el base y 62 en el optimista.
- **¿Cuánta obra paga el mercado?** El PER es, en la mediana, 1,23 veces el
  precio publicado. Con ese descuento, la obra máxima pagable con ROI 0 es de
  unos 24 USD/m² en la mediana: 132 unidades pagarían una obra liviana
  (220 USD/m²), 36 una media (500) y 1 una integral (1.150).
- **Sensibilidad.** El supuesto que más pesa es el nivel de obra: si todas
  fueran livianas, 137 serían rentables en el escenario base. Un descuento de
  negociación del 10 % lleva las rentables en el base de 2 a 6. El tipo de
  cambio (±20 %) casi no influye, porque solo afecta a las expensas.
La versión anterior de este notebook usaba supuestos ilustrativos (obra de 150 a
500 USD/m², gastos de compra de 4 % y de venta de 3 %, sin contingencia ni costo
de oportunidad) que no coincidían con los supuestos con fuente del proyecto; con
ellos resultaban 46 operaciones rentables en los tres escenarios.
 
 
## Recomendaciones para el fondo
 
El detalle está en `notebooks/09_resultados_recomendaciones.ipynb`.
 
1. **Qué visitar.** Priorizar las 249 candidatas de mayor confianza
   (`data/processed/ranking_visitas.csv`): son baratas con dos métodos
   independientes y no tienen indicadores de error. El 41 % ya está reservado o
   en negociación, contra el 23 % de las no baratas (chi-cuadrado, p < 0,001),
   lo que respalda que la señal no es solo error de carga. El orden exacto
   depende del método (20 del top 50 coinciden), por lo que el ranking se usa
   por tramos y no por puesto.
2. **Flipping.** No adoptarlo como estrategia general a precio publicado. Usar el
   precio máximo de oferta de cada unidad (`flipping_ranking_priorizado.csv`)
   como techo de negociación. Solo 7 unidades alcanzarían el margen mínimo con un
   descuento de hasta 30 %.
3. **Antes de ofertar,** verificar el aviso y cotizar la obra con una visita
   técnica: el alcance de la obra es el supuesto que más mueve el resultado.
## Dashboard
 
El tablero es un único archivo HTML autocontenido, **`dashboard/index.html`**, que
se abre con doble clic en cualquier navegador, sin instalar nada ni conectarse a
internet. Se regenera, después de volver a correr los notebooks 07 y 11, con
`python -m src.dashboard` desde la raíz (`src/dashboard.py` une los datos y los
inserta en `src/dashboard_plantilla.html`).
 
| Decisión del fondo | Vista |
| --- | --- |
| Qué propiedades visitar | Indicadores (baratas, confirmadas por ambos métodos y candidatas de mayor confianza), mapa, oportunidades por barrio y tabla ordenada por brecha, con link al aviso y marca de "requiere verificación" |
| Si conviene refaccionar una unidad | Sección de flipping: unidades rentables por escenario y, para cada unidad, precio máximo de oferta, descuento requerido, ROI y decisión |
| Contexto | Precio relativo al benchmark según estado y distribución de los avisos según el cruce de métodos |
 
Los filtros de barrio, ambientes, estado y oportunidad actualizan todas las
vistas (la sección de flipping usa solo barrio y ambientes). Las fuentes son
`remax_deptos_features.csv` (notebook 03), `oportunidades_benchmark_ajustado.csv`
(notebook 11) y `flipping_modelo_economico.csv` (notebook 07); sus cifras
coinciden con las de las notebooks 07 y 09 (por ejemplo, 249 candidatas y 0
rentables en el escenario conservador), y `tests/test_dashboard.py` lo
verifica. Capturas en `reports/dashboard/`.
 
 
## Cambios en la PreEntrega 3
 
| Observación | Cambio realizado |
| --- | --- |
| El modelo económico no usaba los supuestos con fuente del proyecto | La notebook 07 lee `data/supuestos_flipping.csv` y `src/config.py`, asigna el nivel de obra por aviso e incluye contingencia, costo de oportunidad y factor premium; la lógica pasó a `src/flipping.py`. H3 pasó de "a favor" a "no se sostiene" |
| La evaluación de hipótesis copiaba resultados a mano | La notebook 08 recalcula H1, H2 y H3 con tamaños de efecto, intervalos bootstrap o de Wilson y pruebas de robustez |
| Recomendaciones basadas en supuestos ilustrativos | La notebook 09 recomienda a partir del ranking de baratas confirmado por dos métodos y del precio máximo de oferta |
| Notebooks sin outputs, fuera de orden o con nombres de copia | Se ejecutaron de punta a punta y se quitaron los sufijos "(1)", "(2)" y "(4)" |
| Dependencias de Colab y variables no definidas | Se quitó `google.colab` de la notebook 06; la 05 importaba `PATRONES` de una sesión anterior; la 04 corre sin geopandas |
| Umbrales repetidos en las notebooks | La 05 toma `UMBRAL_GAP` de `src/config.py`; el modelo económico, todos sus parámetros |
| Faltaban modelos explicativos y un benchmark con características | Notebooks 10 y 11 (`src/modelos.py`) |
| Tests y dashboard | Se agregaron `tests/` y un tablero HTML interactivo (`dashboard/index.html`) |
 
 
## Cambios a partir de la devolución de la PreEntrega 1
 
| Observación | Cambio realizado |
| --- | --- |
| El contexto requería mayor profundidad | Se incorporaron crédito hipotecario, dolarización, iliquidez y brecha entre precio publicado y de cierre |
| Lo predictivo y prescriptivo quedó como intención futura | Se definieron el PER, su validación (holdout, MAE, MAPE, cobertura) y una regla de decisión con umbrales |
| Mayor dispersión no implica más oportunidades | H2 se reformuló en términos condicionales a estratos homogéneos |
| El valor post-obra y el costo de flipping no diferenciaban sus componentes | Costo descompuesto en cinco dimensiones y triangulado con tres fuentes; valor post-obra en tres escenarios |
| La variable "estado" es ruidosa | Señal imperfecta con categorías agrupadas, sin imputar, y validación manual |
| Definir qué es una propiedad "barata" | Benchmark con mínimo de casos, ampliación jerárquica y control de dispersión; umbral recalibrado de 15 % a 25 % |
| Fuentes externas sin nivel ni comparación | Se separaron indispensables y complementarias, con nivel, unión y aporte |
| Scraper en una celda extensa; correcciones hardcodeadas; README con Argenprop | Lógica en `src/`, excepciones en `data/excepciones_manuales.csv`; se corrigió la fuente (RE/MAX) |
 
 
## Limitaciones
 
- **Una sola fuente y una única captura.** Los avisos provienen de RE/MAX y son una foto a la fecha de corte: no representan a todo el mercado y no se observa la permanencia ni la evolución del precio.
- **Precio de publicación.** Se analizan precios pedidos, no de cierre; la brecha entre ambos no está medida.
- **Estado inferido del texto.** El 63,5 % de los avisos no informa el estado. El clasificador se validó con doble lectura (accuracy de 78 %, kappa de 0,70), con los 78 avisos contradictorios y con una muestra aleatoria de `Reciclada_refaccionada` (94 %), siempre sobre el texto y no sobre el estado físico real.
- **Costos de obra.** Son supuestos con fuente secundaria, no cotizaciones propias, y el nivel de obra se infiere del texto; es el supuesto que más mueve el resultado del flipping.
- **Valor post-obra.** El PER usa comparables en buen estado o reciclados; una unidad recién reciclada de forma integral puede valer más (lo aproxima el escenario optimista). No se modelan impuestos ni financiamiento.
- **Umbral de gap.** El 25 % surge de un análisis de sensibilidad, no de una validación externa.
- **Modelos de precio.** No observan el estado del edificio, el piso ni las terminaciones, y su error mediano ronda 12 %: sirven para priorizar y contrastar, no para tasar.


## Observaciones pendientes y plan

| Pendiente | Plan |
| --- | --- |
| Validación del clasificador de estado | Resuelto en gran parte (notebook 06: doble lectura independiente de 50 avisos de las cuatro categorías). Queda que un tercer integrante adjudique los 17 desacuerdos, porque hoy los adjudicó uno de los dos evaluadores |
| Categoría del edificio en los comparables | Resuelto con el benchmark ajustado por antigüedad y características (notebook 11, MAPE de 19,6 % a 15,3 %). Queda por evaluar un índice resumen de amenities |
| Costo de refacción y margen de flipping | Modelo calculado con supuestos con fuente (notebook 07). Falta reemplazarlos por cotizaciones propias por nivel de obra, actualizadas con el ICC |
| Tipo de cambio y brecha de cierre | Tipo de cambio definido (MEP, DolarHub, 02/11/2026, en `src/config.py`). Falta confirmar la disponibilidad de estadísticas de escrituras |
| Detección contextual de outliers | La detección global marca como atípicos a los segmentos de menor precio (por ejemplo, la comuna 8); evaluar una detección por segmento |
| Estado físico real | El estado se infiere del texto del aviso. Se podría complementar con una clasificación de las fotos del aviso (por ejemplo, un modelo de imágenes que detecte cocina, baño y pisos a renovar) y así reducir el 63,5 % de avisos sin clasificar y la incertidumbre del PER |
| Permanencia en el mercado | Nuevas capturas del extractor (con una columna de fecha de extracción) para medir la primera y la última aparición de cada aviso |
| Validación formal de hipótesis y micromercados | H1, H2 y H3 evaluadas. Se incorporó un análisis territorial exploratorio de 43 barrios (notebook 08). Queda profundizar con variables externas y controlar diferencias de composición entre barrios |
