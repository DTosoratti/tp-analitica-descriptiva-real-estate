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

**Resultado de la validación (notebook 03, sección 11):** el benchmark tiene un
error porcentual mediano (MdAPE) de 14,7 % y un MAPE de 19,5 %; el PER, de
14,0 % y 17,6 %. El MAPE supera el criterio inicial porque está influido por
propiedades muy alejadas de sus comparables; el error típico se ubica cerca del
15 %. El umbral de gap del 25 % supera ambas medidas de error.

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

### Costo de la operación de flipping

El costo no es un único valor por m²: se descompone en cinco dimensiones.

| Dimensión | Qué incluye | Cómo se estima |
| --- | --- | --- |
| Calidad | Nivel de terminaciones | Tres niveles de obra con costo propio por m² |
| Alcance | Partes de la unidad intervenidas | Superficie cubierta intervenida × costo por m² del nivel |
| Tiempo | Duración de la obra y de la venta | Meses de obra y de comercialización, con expensas y capital inmovilizado |
| Transacción | Costos de compra y de venta | Porcentajes sobre el precio |
| Contingencias | Desvíos e imprevistos de obra | Porcentaje sobre el costo de obra |

**Origen del costo de refacción.** El índice de costo de la construcción del INDEC no es un costo por m², sino un índice para actualizar un valor base. Por eso se triangula con tres fuentes:

1. **Costo base por nivel de obra (USD/m²):** al menos tres cotizaciones de profesionales o empresas por nivel, verificadas contra informes de costos de la cámara del sector. Niveles: liviana (pintura, pisos, iluminación), media (liviana más cocina y baño) e integral (media más instalaciones y carpinterías).
2. **Actualización con el ICC del INDEC:** el costo base se lleva a la fecha de análisis con la variación del índice y se convierte a USD con el tipo de cambio definido.
3. **Cota implícita del mercado:** la diferencia entre la mediana de USD/m² de las unidades recicladas y la de las que necesitan obra, dentro de un mismo estrato, indica cuánto paga el mercado por la obra. Si el costo estimado la supera, el flipping no cierra en ese estrato.

El nivel de obra se asigna según la evidencia del aviso ("a reciclar" → integral; "a actualizar" → media). Sin evidencia, se usa el nivel integral como caso conservador. Para obras de nivel liviano, el valor post-obra se toma del escenario conservador del PER.

**Parámetros iniciales (supuestos a validar con un escribano o corredor):**

| Parámetro | Valor inicial |
| --- | --- |
| Costos de compra (escritura, sellos, comisión) | 6 % a 8 % del precio |
| Costos de venta (comisión e impuestos) | 4 % a 6 % del precio de reventa |
| Contingencia de obra | 10 % a 20 % del costo de obra |
| Plazo de obra | 2 a 6 meses según nivel |
| Plazo de comercialización | 3 a 9 meses |

Todos se tratan como hiperparámetros. Se informa cuántas oportunidades siguen siendo positivas en el escenario más desfavorable.


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

1. **Gap de subvaluación ≥ 25 %.**
2. **USD/m² en el cuartil inferior de su grupo** (por debajo del percentil 25).
   Esta condición controla la dispersión: en un grupo heterogéneo, un descuento
   del 25 % respecto de la mediana puede estar dentro del rango habitual.
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

El umbral inicial del 15 % se recalibró a **25 %** a partir del análisis de
sensibilidad (notebook 03, sección 7.3). Con 15 %, el 18,6 % de los avisos
resultaba barato, lo que refleja la dispersión normal del mercado más que una
subvaluación (el percentil 75 del gap es 13,8 %). El umbral de 25 % se aproxima
al percentil 90 del gap e identifica al 8,8 % de los avisos. El coeficiente de
0,5 de la superficie descubierta es un supuesto; su sensibilidad se evaluó
entre 0,3 y 0,7 (notebook 03, sección 7.4): la clasificación coincide con la
base en el 97,3 % y el 97,7 % de los avisos, y las propiedades baratas
(incluidas las que requieren verificación) son 853, 836 y 851 con los
coeficientes 0,3, 0,5 y 0,7.


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
- La precisión del clasificador se valida manualmente (ver "Criterio de revisión
  manual"). Criterio inicial: al menos 80 % de precisión en Necesita_obra y
  Reciclada_refaccionada.

Resultado de la clasificación: 63,5 % sin clasificar, 21,6 % buen estado,
10,3 % reciclada o refaccionada y 4,6 % necesita obra (439 avisos). Además,
343 avisos mencionan el reciclado de un solo ambiente y se marcan como
`Reciclado_Parcial`.

### Criterio de revisión manual

La validación compara la clasificación automática con la lectura de una persona
sobre el título y la descripción del aviso (las fotos no se usan para decidir; si
aportan información, se anota en una columna de notas). Los cuatro integrantes
aplican el mismo criterio:

- **Necesita_obra:** el aviso ofrece la unidad para reciclar, refaccionar o hacer
  flipping de forma explícita ("a reciclar", "oportunidad de reciclar", "ideal
  flipping"), aunque diga que es habitable.
- **Buen_o_reciclada:** el aviso dice explícitamente que está en buen estado o que
  ya fue reciclado o refaccionado.
- **Sin_clasificar:** todo lo demás, incluidas las señales mezcladas y los detalles
  sueltos (por ejemplo, una cocina vieja).
- **Señales opuestas en el mismo aviso:** si la descripción del estado es específica
  y repetida (ambientes, baño, pisos) y la frase de reciclar es genérica o de cierre
  comercial, prevalece el estado descripto; si se describe obra concreta, prevalece
  Necesita_obra; si no se puede decidir, Sin_clasificar.

Este criterio es un protocolo de revisión y no cambia la clasificación automática,
que da prioridad a las señales de obra. Las diferencias entre ambos son lo que la
validación mide. Se revisan en primer lugar los 78 avisos con
`Flag_Senal_Contradictoria` (`reports/validacion_estado_contradictorios.csv`,
repartidos entre los cuatro integrantes) y, si hay tiempo, una muestra de la
estratificada de 200 avisos. Los errores de precisión (clasificó mal) se reportan
por separado de los de cobertura (no detectó una frase que indica obra, por
ejemplo "oportunidad de reciclar" o "ideal flipping"), ya que estos últimos
indican que el clasificador subestima la cantidad de unidades que necesitan obra.

### Qué se midió sobre la calidad de la señal (notebook 03)

| Aspecto | Qué se hizo | Resultado |
| --- | --- | --- |
| Señales contradictorias (sección 5.4) | Conteo de avisos con señales opuestas en el texto; se resuelven dando prioridad a las señales de obra | 66 de los 439 `Necesita_obra` (15 %) también mencionan buen estado o reciclado integral; otros 20 avisos combinan reciclado integral con "a actualizar" (78 avisos en total, marcados con `Flag_Senal_Contradictoria`). La regla es conservadora: ante la duda, el aviso queda fuera de los comparables |
| Sesgo de declaración (sección 6.4) | % de `Sin_clasificar` por antigüedad, cuartil de USD/m², comuna y amenities, con chi-cuadrado | El estado se informa de forma desigual. Casi no lo informan los edificios de hasta 10 años (87 % sin clasificar) ni los avisos sin dato de antigüedad (99 %), frente a 51–55 % en los de más de 30 años. Los avisos más caros lo informan menos (75 % sin clasificar en el cuartil superior contra 57 % en el inferior). Por comuna varía entre 52 % y 73 %. Informar amenities casi no influye (3 puntos de diferencia) |
| Cruce con señales no textuales (sección 6.5) | Antigüedad, amenities y expensas por m² según el estado | Los `Necesita_obra` son los más antiguos (mediana de 56 años contra 47 y 36) y tienen las expensas por m² más bajas, y el 31 % tiene perfil de edificio viejo sin amenities (22 % y 14 % en los otros grupos). Kruskal-Wallis (sección 6.6) rechaza que los tres grupos tengan la misma distribución en antigüedad, amenities y expensas por m² (esta última con diferencia chica), y Mann-Whitney confirma que los `Necesita_obra` son más antiguos que los `Buen_o_reciclada` (56 contra 47 años). Es un respaldo indirecto y no reemplaza la validación manual |
| Sensibilidad a la definición de "reciclada" (sección 8.3) | PER con una definición estricta, la base y dos más laxas; clasificación con comparables solo de avisos con estado informado | El potencial bruto mediano se mantiene entre 21 % y 31 % y el 66–74 % de las propiedades con PER supera el 12 %. Usar solo comparables con estado informado reduce las `Barata` de 716 a 663 y deja sin benchmark a 174 avisos (antes 49) |
| Revisión manual de los avisos con señales contradictorias (sección 10.3) | Los cuatro integrantes revisaron los 78 avisos con `Flag_Senal_Contradictoria` según el criterio de revisión manual | Coincidencia global de 79,5 % (62 de 78). De los 68 clasificados como `Necesita_obra`, 59 se confirmaron (86,8 %); los otros 9 eran buen estado o reciclado (4) o no permitían decidir (5). De los 10 clasificados como `Reciclada_refaccionada`, solo 3 se confirmaron (30 %): 7 eran en realidad unidades a renovar, con frases como "gran potencial de reciclado", "ideal para modernizar" o "invita a una renovación integral", que la expresión regular de reciclada interpreta como reciclado ya hecho. Son los casos más dudosos (0,8 % de la base) y no hubo una segunda lectura independiente, por lo que los porcentajes son indicativos |
| Revisión manual de una muestra aleatoria de `Reciclada_refaccionada` (`reports/validacion_reciclada_muestra.csv`) | Los cuatro integrantes revisaron, solo a partir del título y la descripción, 50 avisos `Reciclada_refaccionada` tomados al azar de la muestra estratificada, con el mismo criterio de revisión manual | 47 de 50 se confirmaron como `Buen_o_reciclada` (94 %; intervalo de Wilson al 95 %: 84 %–98 %). Los otros 3 necesitaban obra y ninguno quedó como `Sin_clasificar`. Supera el 80 % fijado como criterio, por lo que no se modificó el patrón de reciclada. Es una revisión sobre el texto del aviso, no sobre el estado físico real, y sin segunda lectura independiente |

Implicancias: los comparables en buen estado o reciclados provienen sobre todo
de edificios más antiguos y de menor precio, por lo que el PER no debe
extrapolarse a unidades nuevas o de precio alto. Para las unidades que
necesitan obra, que también son antiguas, el sesgo es menos grave. Las
conclusiones sobre el PER y la clasificación de oportunidades no dependen de la
definición adoptada. La revisión manual de los casos contradictorios muestra que la
categoría `Reciclada_refaccionada`, que alimenta el PER, puede incluir unidades
que en realidad necesitan obra (7 de 10 en ese subconjunto). Ese error está
concentrado en los casos contradictorios: en una muestra aleatoria de 50 avisos
de la categoría, 47 (94 %) se confirmaron como buen estado o reciclados. Por eso el
PER se mantiene, y los avisos con `Flag_Senal_Contradictoria` quedan como los más
propensos a error.

La columna `Estado` de la base raw no describe la condición física del inmueble,
sino el estado comercial de la publicación (`active`, `reserved` o
`negotiation`). Para evitar confusiones se renombra como `Estado_Publicacion`
en el notebook 03, y se conserva como indicador de liquidez: una reserva o
negociación indica que hubo demanda al precio publicado.


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
| Fecha de corte | 26 de septiembre de 2026 (aproximada, según la fecha de creación del archivo de la extracción) |
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
| [BA Data — Barrios](https://data.buenosaires.gob.ar/dataset/barrios) — **integrada** | CABA; versión actualizada el 29/07/2026 (licencia CC-BY-2.5-AR) | Polígonos de barrio. Unión espacial punto en polígono con la latitud y longitud de cada aviso | `Barrio_Oficial`, `Comuna` | Estratos del benchmark y del PER (niveles 1 a 4) | 4 avisos con coordenadas fuera de CABA: uno excluido (propiedad en provincia) y tres asignados por su etiqueta y marcados con `Flag_Coordenadas_Invalidas`. La etiqueta de la fuente coincide con el barrio oficial en el 83,8 % de los avisos |
| [INDEC — Índice del Costo de la Construcción](https://www.indec.gob.ar/indec/web/Nivel4-Tema-3-5-33) | Gran Buenos Aires; serie mensual | Serie temporal; se une por fecha (cotización y fecha de análisis) | Factor de actualización del costo de obra | Costo de refacción | Es un índice, no un costo por m²; está en pesos |
| Tipo de cambio histórico (BCRA; MEP como alternativa) | Argentina; serie diaria | Serie temporal; se une por fecha de referencia | Costos de obra y expensas en USD | Inversión total y margen | El margen cambia según el tipo de cambio elegido; se informa la sensibilidad |
| Estadísticas de escrituras o precios de cierre (por ejemplo, Colegio de Escribanos de CABA) | CABA; mensual | Agregado por zona o ciudad (desagregación a confirmar) | Brecha estimada entre precio publicado y de cierre | Ajuste del gap y del valor post-obra | Disponibilidad y nivel de desagregación por confirmar |

### Complementarias (Pre-Entrega 3)

Todas las fuentes complementarias tienen cobertura de CABA y granularidad de punto o polígono, por lo que son compatibles con la unidad de análisis (aviso individual con coordenadas): permiten calcular una variable distinta para cada propiedad y explicar diferencias de precio dentro de un mismo barrio.

| Fuente | Cobertura y período | Granularidad y mecanismo de unión | Variable derivada | Aporta a | Limitaciones |
| --- | --- | --- | --- | --- | --- |
| [BA Data — Estaciones de subte](https://data.buenosaires.gob.ar/dataset/subte-estaciones) | CABA; red vigente a la fecha de descarga | Puntos; distancia de cada aviso a la estación más cercana | Distancia al subte (m) | Pregunta diagnóstica 1: diferencias de USD/m² dentro de un estrato | Foto de la red actual: no refleja obras futuras ni la frecuencia del servicio |
| [BA Data — Estaciones de ferrocarril](https://data.buenosaires.gob.ar/dataset/estaciones-ferrocarril) | CABA; red vigente a la fecha de descarga | Puntos; distancia a la estación más cercana | Distancia al tren (m) | Pregunta diagnóstica 1 | No distingue líneas ni calidad del servicio |
| [BA Data — Espacios verdes](https://data.buenosaires.gob.ar/dataset/espacios-verdes) | CABA; inventario vigente a la fecha de descarga | Polígonos; distancia al espacio verde más cercano, según tamaño o tipo | Distancia a plaza o parque (m) | Pregunta diagnóstica 1 | Una plaza pequeña y un parque grande no tienen el mismo efecto: requiere clasificar por tamaño |
| [BA Data — Establecimientos educativos](https://data.buenosaires.gob.ar/dataset/establecimientos-educativos) | CABA; padrón vigente a la fecha de descarga | Puntos; distancia por tipo de gestión y nivel educativo | Distancia a escuelas (m) | Pregunta diagnóstica 1 | No informa la calidad de las instituciones; el efecto puede diferir entre gestión pública y privada |

## Estructura del repositorio

```
├── README.md
├── data/
│   ├── raw/
│   │   ├── remax_caba_propiedades_muestra.csv   # muestra de la base raw
│   │   └── (base completa: se descarga desde Drive, ver Reproducción)
│   ├── processed/
│   │   ├── remax_deptos_limpio.csv              # base analítica (9.500 × 41)
│   │   ├── registro_limpieza.csv                # registro de cada paso de limpieza
│   │   ├── remax_deptos_features.csv            # base con variables derivadas y KPIs (9.499 × 100)
│   │   └── registro_features.csv                # registro de pasos del notebook 03
│   ├── external/                                # fuentes externas (se descargan al ejecutar el notebook 03)
│   │   └── barrios_caba.geojson
│   ├── excepciones_manuales.csv                 # correcciones puntuales documentadas
│   ├── diccionario_variables.csv                # descripciones de las variables (insumo del diccionario)
│   └── diccionario_datos.md                     # diccionario de datos (100 variables)
├── notebooks/
│   ├── 01_extraccion_remax.ipynb
│   ├── 02_limpieza_remax.ipynb
│   ├── 03_features_kpis.ipynb
│   └── 04_eda.ipynb
├── src/
│   ├── scraper_remax.py                         # extractor (requests, reintentos, paralelismo)
│   ├── scrapers_alternativos.py                 # pruebas con Cabaprop y Zonaprop (fuentes descartadas, ver anexo del notebook 01)
│   ├── limpieza.py                              # auditorías, registro de pasos, excepciones, texto
│   ├── patrones.py                              # expresiones regulares (limpieza, texto, estado, amenities)
│   ├── diagnostico.py                           # validación de ambientes, faltantes y outliers
│   ├── benchmark.py                             # bandas, benchmark jerárquico, PER y clasificación
│   └── eda.py                                   # estadísticos robustos y tests no paramétricos
└── reports/
    ├── informe_preentrega_1.docx                # informe ejecutivo de la Pre-Entrega 1 (editable)
    ├── informe_preentrega_1.pdf                 # informe ejecutivo de la Pre-Entrega 1
    ├── hallazgos_negocio.md                     # hallazgos que cambian el rumbo del negocio
    ├── validacion_benchmark.csv                 # métricas de la validación del benchmark y del PER
    ├── validacion_estado_muestra.csv            # muestra estratificada para la validación manual del estado
    ├── validacion_estado_contradictorios.csv    # avisos con señales contradictorias, con la revisión manual
    └── validacion_reciclada_muestra.csv         # 50 avisos Reciclada_refaccionada al azar, con la revisión manual
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
4. **Ingeniería de variables y KPIs.** `03_features_kpis.ipynb` parte de
   `data/processed/remax_deptos_limpio.csv`, descarga los límites de barrios
   de BA Data en `data/external/`, construye las variables derivadas y los
   KPIs, y exporta `data/processed/remax_deptos_features.csv`, el registro de
   pasos, el diccionario de datos y la validación del benchmark.
5. **Análisis exploratorio.** `04_eda.ipynb` parte de
   `data/processed/remax_deptos_features.csv` y responde las preguntas
   descriptivas y diagnósticas, con evidencia preliminar sobre las hipótesis.


## Principales hallazgos del análisis exploratorio

El detalle está en `notebooks/04_eda.ipynb`, sección 12. Las implicancias para
el fondo de inversión se desarrollan en
[`reports/hallazgos_negocio.md`](reports/hallazgos_negocio.md).

- **La ubicación es el principal determinante del precio.** La mediana del
  USD/m² va de USD 917 en Villa Lugano a USD 5.110 en Puerto Madero, con un
  gradiente norte–sur. La antigüedad es la variable física más asociada con el
  precio por m² (Spearman ρ = −0,48).
- **El descuento por necesitar obra es real y homogéneo.** Las unidades que
  necesitan obra se publican, en la mediana, 17,4 % por debajo del benchmark de
  sus comparables (Mann-Whitney, p < 0,001), y el descuento no difiere
  significativamente entre comunas (Kruskal-Wallis, p = 0,26).
- **La categoría del edificio explica diferencias que el benchmark no captura.**
  Los avisos con gimnasio, pileta, SUM o seguridad se publican entre 15 y 27
  puntos por encima de sus comparables. Las amenities aparecen juntas y en
  edificios más nuevos, por lo que conviene resumirlas en un índice de
  categoría del edificio.
- **El mercado toma las oportunidades.** Los avisos reservados o en negociación
  están 8,4 puntos más baratos respecto de su benchmark que los activos, y las
  propiedades clasificadas como baratas tienen más operaciones en curso (34 %
  contra 23 %). Las que requieren verificación se comportan como las de precio
  de mercado, lo que sugiere que una parte son errores de carga.
- **Hay candidatas a flipping.** 290 unidades que necesitan obra tienen un
  potencial bruto superior a los costos de transacción en el escenario base.

### Estado de las hipótesis

| Hipótesis | Evidencia preliminar |
| --- | --- |
| **H1.** Descuento por condición | **A favor.** Descuento de 17,4 % respecto de comparables, significativo y similar entre comunas |
| **H2.** Dispersión condicional | **Parcialmente a favor.** La dispersión difiere entre barrios y los estratos más dispersos concentran más oportunidades (3,5 % contra 11,7 %), pero también más casos con indicadores de error |
| **H3.** Oportunidades de flipping | **Preliminarmente a favor.** 290 unidades superan los costos de transacción; falta descontar el costo de la obra y de tenencia |

La validación formal de las hipótesis corresponde a la Pre-Entrega 3.


## Cambios a partir de la devolución de la PreEntrega 1

| Observación | Cambio realizado |
| --- | --- |
| El contexto requería mayor profundidad | Se incorporaron el crédito hipotecario, la dolarización, la iliquidez y la brecha entre precio publicado y de cierre, y su efecto sobre la señal de descuento y la salida del flipping |
| Lo predictivo y prescriptivo quedó como intención futura | Se definió la variable a estimar (PER), su validación (holdout, MAE, MAPE, cobertura) y una regla de decisión con umbrales, presupuesto y mínimo de comparables |
| Mayor dispersión no implica más oportunidades | H2 se reformuló en términos condicionales a estratos homogéneos, descartando errores de carga como causa alternativa |
| El valor post-obra y el costo de flipping no diferenciaban sus componentes | El costo se descompone en calidad, alcance, tiempo, transacción y contingencias; el valor post-obra se estima con tres escenarios |
| La variable "estado" es ruidosa | Se usa como señal imperfecta con categorías agrupadas, sin imputar. Se midieron el sesgo de declaración, las señales contradictorias, el cruce con variables no textuales y la sensibilidad del PER a la definición; la validación manual cubrió los 78 casos más dudosos y detectó baja precisión de la categoría de reciclada en ese subconjunto, que no se repitió en una muestra aleatoria de 50 avisos (94 % de precisión) |
| Definir operativamente qué es una propiedad "barata" | Benchmark de comparables con mínimo de casos, ampliación jerárquica, control de dispersión y separación de las unidades que necesitan obra; el umbral de gap se recalibró de 15 % a 25 % con un análisis de sensibilidad |
| Fuentes externas sin nivel ni comparación | Se separaron indispensables y complementarias, indicando nivel, mecanismo de unión y aporte a la regla |
| El scraper ocupaba una celda muy extensa | La lógica se trasladó a `src/scraper_remax.py`; el notebook contiene configuración, ejecución y controles |
| Chequeos repetidos, patrones redefinidos y correcciones hardcodeadas en la limpieza | Auditorías encapsuladas en `src/limpieza.py`, patrones únicos en `src/patrones.py`, excepciones en `data/excepciones_manuales.csv` y registro de cada paso |
| El README mencionaba Argenprop | Se corrigió la fuente (RE/MAX) y se documentaron la ejecución, las salidas de cada notebook y la ubicación de los datos |


## Limitaciones

- **Una sola fuente.** Los avisos provienen de RE/MAX; no representan a todo el mercado, y un mismo inmueble puede estar publicado por otras inmobiliarias.
- **Precio de publicación.** Se analizan precios pedidos, no de cierre. La brecha entre ambos no está medida (ver pendientes).
- **Una única captura.** La base es una foto a la fecha de corte; no se observa la permanencia ni la evolución del precio de cada aviso.
- **Estado inferido del texto.** El 63,5 % de los avisos no informa el estado y la precisión del clasificador solo se validó manualmente sobre los 78 avisos con
  señales contradictorias, donde `Reciclada_refaccionada` tuvo baja precisión (3 de 10), y sobre una muestra aleatoria de 50 avisos `Reciclada_refaccionada`, donde la precisión fue de 94 % (47 de 50). Ambas revisiones se hicieron sobre el texto del aviso, no sobre el estado físico real, y sin segunda lectura independiente. Las otras categorías (`Buen_estado` y `Sin_clasificar`) no se validaron en una muestra aleatoria.
- **Potencial bruto.** El PER estima el valor post-obra, no el margen de flipping: faltan el costo de obra, la tenencia y el tipo de cambio.
- **Umbral de gap.** El 25 % surge de un análisis de sensibilidad (aproximadamente el percentil 90 del gap) y no de una validación externa; como evidencia indirecta, las propiedades clasificadas como baratas tienen más operaciones en curso.


## Observaciones pendientes y plan

| Pendiente | Plan |
| --- | --- |
| Validación del clasificador de estado | Se revisaron los 78 avisos con señales contradictorias y 50 avisos `Reciclada_refaccionada` de la muestra aleatoria (resultados en "Qué se midió sobre la calidad de la señal"). Falta revisar las otras tres categorías de la muestra estratificada (`reports/validacion_estado_muestra.csv`) y obtener una segunda lectura independiente de una parte de los avisos. Opcionalmente, evaluar si excluir de los comparables del PER los avisos con `Flag_Senal_Contradictoria` |
| Categoría del edificio en los comparables | Construir un índice de amenities mediante reducción de dimensionalidad e incorporarlo al benchmark, para reducir su error |
| Costo de refacción y margen de flipping | Cotizaciones por nivel de obra (liviana, media, integral), actualizadas con el ICC y convertidas a USD, para pasar del potencial bruto al margen y evaluar H3 |
| Tipo de cambio y brecha de cierre | Definir la fuente del tipo de cambio (también para convertir las expensas) y confirmar la disponibilidad de estadísticas de escrituras |
| Detección contextual de outliers | La detección global marca como atípicos a los segmentos de menor precio (por ejemplo, la comuna 8); evaluar una detección por segmento |
| Permanencia en el mercado | Nuevas capturas del extractor (con una columna de fecha de extracción) para medir la primera y la última aparición de cada aviso |
| Validación formal de hipótesis y micromercados | Tests formales de H1 a H3, fuentes externas complementarias y clustering de micromercados (Pre-Entrega 3) |
