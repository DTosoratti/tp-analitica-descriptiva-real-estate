# Hallazgos que cambian el rumbo del negocio

**Pre-Entrega 2 — Real Estate Analytics (ITBA, Analítica Descriptiva)**

**Cliente:** Fondo de Inversión Inmobiliario que busca propiedades subvaluadas en CABA y oportunidades de refacción y reventa (flipping).

**Base:** 9.499 departamentos usados en venta publicados en RE/MAX (corte aproximado: 26/09/2026). El detalle técnico está en `notebooks/03_features_kpis.ipynb` y `notebooks/04_eda.ipynb`.

---

## Resumen

El análisis confirma que existen oportunidades, pero también muestra que **buscarlas con un criterio simple de "precio bajo" llevaría al fondo a decisiones equivocadas**. Las oportunidades potenciales se concentran en zonas distintas de las que sugiere el precio por m², los avisos con descuento muestran más operaciones en curso y conviven con una proporción relevante de avisos con errores. Los cinco hallazgos siguientes cambian la forma en que el fondo debería buscar, priorizar y validar sus inversiones.

---

## 1. El flipping rinde más en las zonas caras, no en las baratas

**Evidencia.** Las unidades que necesitan obra se publican, en la mediana, un **17,4% por debajo** del precio de propiedades comparables de su misma zona. Ese descuento es **similar en toda la ciudad**: el gap de estado por comuna se ubica mayormente entre 18% y 25%, y no hay diferencias estadísticamente significativas entre comunas (Kruskal-Wallis, p = 0,26). En cambio, el nivel de precio sobre el que se aplica ese descuento varía mucho: la mediana del USD/m² va de USD 1.391 en Constitución a USD 2.852 en Palermo.

**Implicancia.** Si el descuento porcentual es parecido en todas las zonas, la ganancia en dólares que genera la obra es proporcional al precio del barrio. Un mismo descuento del 20% representa unos USD 570 por m² en Palermo y unos USD 280 por m² en Constitución. Si el costo de la obra por m² es similar en ambas zonas (supuesto a confirmar con las cotizaciones), **el margen del flipping es mucho mayor en los barrios de mayor valor**.

**Cambio de rumbo.** Lo intuitivo sería buscar oportunidades en las zonas más baratas. La evidencia sugiere lo contrario: si el costo de obra es similar entre zonas, el fondo debería **priorizar el centro y el corredor norte**, donde además se concentran las unidades a refaccionar con descuento (comuna 1: 72 unidades; comunas 13 y 14: 36 cada una). Esta prioridad queda sujeta a confirmar los costos de obra por zona.

**Actualización (PreEntrega 3, notebook 07).** El modelo económico completo, con obra, tenencia, transacción y costo de oportunidad, muestra que el flipping **no es rentable a precio publicado en ninguna zona**: ninguna unidad lo es en el escenario conservador y solo 2 de 428 en el base. El hallazgo se mantiene solo en términos relativos: aun aplicando un costo de obra 20 % mayor en los barrios caros, allí la proporción de unidades rentables en el escenario optimista es mayor (19 % contra 12 %), y las 7 unidades más cercanas a cerrar con un descuento de hasta 30 % están todas en Palermo, Recoleta y Belgrano. Si el fondo hace flipping, conviene hacerlo en esas zonas y solo comprando por debajo del precio máximo de oferta.

---

## 2. Los avisos con descuento muestran más operaciones en curso

**Evidencia.** Una cuarta parte de la oferta (24,6%) está reservada o en negociación. Esos avisos se publican, en la mediana, **8,4 puntos más baratos** respecto de sus comparables que los activos (Mann-Whitney, p < 0,001). Entre las propiedades clasificadas como baratas, el 34% tiene una operación en curso, y entre las que necesitan obra con descuento, el 40%, contra el 23% de las propiedades a precio de mercado.

**Implicancia.** Los avisos con descuento relativo atraen más demanda que los de precio de mercado. Sin embargo, el análisis se basa en una única captura: no permite medir la velocidad con la que estos avisos salen del mercado ni confirmar que los reservados o en negociación terminen en una venta.

**Cambio de rumbo.** Si el fondo quiere aprovechar estas propiedades, conviene acortar el ciclo de decisión y actualizar el ranking con nuevas corridas del extractor. Esas corridas sucesivas permitirían además medir la permanencia de cada aviso y probar si las oportunidades realmente se agotan rápido, algo que hoy no se puede afirmar.

---

## 3. No toda "ganga" es real: hay que verificar antes de ofertar

**Evidencia.** De las 836 propiedades que cumplen el criterio de barata, **120 tienen indicadores de posible error de carga** (precio atípicamente bajo, combinación inusual de superficie y ambientes, coordenadas inválidas o ficha sin descripción). Esas propiedades no atraen más demanda que una propiedad a precio de mercado: el 23% está reservada o en negociación, igual que las propiedades a precio de mercado. Si fueran oportunidades reales, deberían atraer más compradores. El problema se agrava en el sur: en la comuna 8, **18 de las 20 propiedades baratas** requieren verificación.

**Implicancia.** Una parte de los precios "excepcionalmente bajos" son errores de publicación, no descuentos.

**Cambio de rumbo.** El fondo debe **separar las propiedades con potencial bruto sin alertas de error (716) de las que requieren verificación (120)**, y revisar cada aviso dudoso antes de destinar tiempo a visitas. Que una propiedad no tenga alertas no la convierte en una oportunidad confirmada: todavía falta verificar su estado físico y el costo de la obra. En las zonas de menor precio, la verificación es obligatoria.

---

## 4. Comparar sin tener en cuenta la categoría del edificio genera falsas oportunidades

**Evidencia.** Las amenities del edificio son lo que más diferencia el precio entre propiedades de una misma zona y tamaño. Respecto de sus comparables, los departamentos en edificios con gimnasio se publican **27 puntos más caros**; con pileta o SUM, unos 18 puntos más; con seguridad, 15 puntos más. Las amenities aparecen juntas y en edificios más nuevos (por ejemplo, la pileta se asocia negativamente con la antigüedad, ρ = −0,43).

**Implicancia.** El benchmark actual compara por barrio, ambientes, superficie y antigüedad, pero no por categoría del edificio. Un departamento sin amenities, rodeado de comparables con amenities, aparece como "barato" aunque su precio sea el correcto para su producto.

**Cambio de rumbo.** Antes de ofertar, cada oportunidad debe compararse con **edificios de su misma categoría**. En la siguiente etapa se incorporará un índice de categoría del edificio al cálculo del benchmark, lo que reducirá las falsas oportunidades y el error de estimación (hoy, el error típico es del 15%).

---

## 5. Un criterio exigente da una lista accionable

**Evidencia.** Con un umbral de descuento del 15%, el 18,6% de la oferta resultaba "barata": casi uno de cada cinco departamentos. Ese nivel de descuento está dentro de la variación normal del mercado (el 25% de las propiedades ya tiene un gap de al menos 13,8%) y del error de estimación del benchmark. Con un umbral del **25%**, que supera ese error, la lista se reduce a **836 propiedades (8,8%)**.

**Cambio de rumbo.** El fondo no necesita revisar miles de avisos: con el umbral recalibrado y el ranking ordenado por descuento, puede **concentrar su esfuerzo en las primeras posiciones** y ampliar la búsqueda solo si lo necesita. El umbral es un parámetro que puede ajustarse según la capacidad de análisis del equipo.

---

## Recomendaciones para el fondo

| # | Recomendación | Basada en |
| --- | --- | --- |
| 1 | No hacer flipping a precio publicado; si se hace, ofertar por debajo del precio máximo de oferta y priorizar el corredor norte | Hallazgo 1 y notebook 07 |
| 1b | Visitar primero las 249 baratas confirmadas por dos métodos (`data/processed/ranking_visitas.csv`) | Notebooks 09 y 11 |
| 2 | Actualizar el ranking con capturas sucesivas, para medir la permanencia de los avisos y acortar el ciclo de decisión | Hallazgo 2 |
| 3 | Revisar cada aviso dudoso antes de visitar; verificación obligatoria en el sur | Hallazgo 3 |
| 4 | Comparar cada oportunidad con edificios de la misma categoría | Hallazgo 4 |
| 5 | Trabajar con el umbral de 25% y el ranking ordenado por descuento | Hallazgo 5 |

## Limitaciones

- Los precios son de publicación, no de cierre: el descuento es relativo a la oferta.
- El estado de la propiedad se infiere del texto de los avisos; su validación manual cubrió los 78 casos más dudosos, donde la categoría de reciclada resultó poco confiable (3 de 10 confirmadas), y una muestra aleatoria de 50 avisos de esa categoría, donde 47 (94 %) se confirmaron; ambas revisiones se hicieron sobre el texto del aviso, no sobre el estado físico real. El error de la categoría de reciclada parece concentrarse en los avisos con señales contradictorias. Además, el estado se informa de forma desigual (casi no lo declaran los edificios de hasta 10 años ni los avisos más caros), por lo que el precio esperado de reciclado es más confiable para unidades antiguas que para unidades nuevas o de precio alto. Las conclusiones no cambian con definiciones más estrictas o más laxas de "reciclada" (potencial bruto mediano entre 21 % y 31 %). En consecuencia, en las zonas de mayor precio, que son las que el hallazgo 1 sugiere priorizar, el valor post-obra estimado debe tomarse con más cautela.
- El margen de flipping usa costos de obra con fuente secundaria (prensa y cámaras del sector), no cotizaciones propias; el nivel de obra se infiere del texto del aviso.
- La base corresponde a una sola red inmobiliaria y a una única captura.
