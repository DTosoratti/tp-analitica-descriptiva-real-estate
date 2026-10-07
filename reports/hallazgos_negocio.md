# Hallazgos que cambian el rumbo del negocio

**Pre-Entrega 2 — Real Estate Analytics (ITBA, Analítica Descriptiva)**

**Cliente:** Fondo de Inversión Inmobiliario que busca propiedades subvaluadas en CABA y oportunidades de refacción y reventa (flipping).

**Base:** 9.499 departamentos usados en venta publicados en RE/MAX (corte aproximado: 26/09/2026). El detalle técnico está en `notebooks/03_features_kpis.ipynb` y `notebooks/04_eda.ipynb`.

---

## Resumen

El análisis confirma que existen oportunidades, pero también muestra que **buscarlas con un criterio simple de "precio bajo" llevaría al fondo a decisiones equivocadas**. Las oportunidades reales se concentran en zonas distintas de las que sugiere el precio por m², se agotan rápido y conviven con una proporción relevante de avisos con errores. Los cinco hallazgos siguientes cambian la forma en que el fondo debería buscar, priorizar y validar sus inversiones.

---

## 1. El flipping rinde más en las zonas caras, no en las baratas

**Evidencia.** Las unidades que necesitan obra se publican, en la mediana, un **17,4% por debajo** del precio de propiedades comparables de su misma zona. Ese descuento es **similar en toda la ciudad**: el gap de estado por comuna se ubica mayormente entre 18% y 25%, y no hay diferencias estadísticamente significativas entre comunas (Kruskal-Wallis, p = 0,26). En cambio, el nivel de precio sobre el que se aplica ese descuento varía mucho: la mediana del USD/m² va de USD 1.391 en Constitución a USD 2.852 en Palermo.

**Implicancia.** Si el descuento porcentual es parecido en todas las zonas, la ganancia en dólares que genera la obra es proporcional al precio del barrio. Un mismo descuento del 20% representa unos USD 570 por m² en Palermo y unos USD 280 por m² en Constitución. Si el costo de la obra por m² es similar en ambas zonas (supuesto a confirmar con las cotizaciones), **el margen del flipping es mucho mayor en los barrios de mayor valor**.

**Cambio de rumbo.** Lo intuitivo sería buscar oportunidades en las zonas más baratas. La evidencia sugiere lo contrario: si el costo de obra es similar entre zonas, el fondo debería **priorizar el centro y el corredor norte**, donde además se concentran las unidades a refaccionar con descuento (comuna 1: 72 unidades; comunas 13 y 14: 36 cada una). Esta prioridad queda sujeta a confirmar los costos de obra por zona.

---

## 2. Las oportunidades se agotan rápido

**Evidencia.** Una cuarta parte de la oferta (24,6%) está reservada o en negociación. Esos avisos se publican, en la mediana, **8,4 puntos más baratos** respecto de sus comparables que los activos (Mann-Whitney, p < 0,001). Entre las propiedades clasificadas como baratas, el 34% ya tiene una operación en curso, y entre las que necesitan obra con descuento, el 40%, contra el 23% de las propiedades a precio de mercado.

**Implicancia.** El mercado detecta las mismas oportunidades que el modelo, y las toma. Una propiedad barata que hoy está disponible puede no estarlo en pocas semanas.

**Cambio de rumbo.** El ranking de oportunidades no puede ser un informe estático: tiene que **actualizarse con frecuencia** (con nuevas corridas del extractor) y el fondo necesita un **proceso de decisión rápido** (visita y oferta en pocos días) para competir con otros compradores.

---

## 3. No toda "ganga" es real: hay que verificar antes de ofertar

**Evidencia.** De las 836 propiedades que cumplen el criterio de barata, **120 tienen indicadores de posible error de carga** (precio atípicamente bajo, combinación inusual de superficie y ambientes, coordenadas inválidas o ficha sin descripción). Esas propiedades no atraen más demanda que una propiedad a precio de mercado: el 23% está reservada o en negociación, igual que las propiedades a precio de mercado. Si fueran oportunidades reales, deberían atraer más compradores. El problema se agrava en el sur: en la comuna 8, **18 de las 20 propiedades baratas** requieren verificación.

**Implicancia.** Una parte de los precios "excepcionalmente bajos" son errores de publicación, no descuentos.

**Cambio de rumbo.** El fondo debe **separar las oportunidades confirmadas (716) de las que requieren verificación (120)**, y revisar cada aviso dudoso antes de destinar tiempo a visitas. En las zonas de menor precio, la verificación es obligatoria.

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
| 1 | Priorizar el flipping en el centro y el corredor norte | Hallazgo 1 |
| 2 | Actualizar el ranking con frecuencia y acortar el ciclo de decisión | Hallazgo 2 |
| 3 | Revisar cada aviso dudoso antes de visitar; verificación obligatoria en el sur | Hallazgo 3 |
| 4 | Comparar cada oportunidad con edificios de la misma categoría | Hallazgo 4 |
| 5 | Trabajar con el umbral de 25% y el ranking ordenado por descuento | Hallazgo 5 |

## Limitaciones

- Los precios son de publicación, no de cierre: el descuento es relativo a la oferta.
- El estado de la propiedad se infiere del texto de los avisos; su validación manual cubrió los 78 casos más dudosos, donde la categoría de reciclada resultó poco confiable (3 de 10 confirmadas), y una muestra aleatoria de 50 avisos de esa categoría, donde 47 (94 %) se confirmaron; ambas revisiones se hicieron sobre el texto del aviso, no sobre el estado físico real. El error de la categoría de reciclada parece concentrarse en los avisos con señales contradictorias. Además, el estado se informa de forma desigual (casi no lo declaran los edificios de hasta 10 años ni los avisos más caros), por lo que el precio esperado de reciclado es más confiable para unidades antiguas que para unidades nuevas o de precio alto. Las conclusiones no cambian con definiciones más estrictas o más laxas de "reciclada" (potencial bruto mediano entre 21 % y 31 %). En consecuencia, en las zonas de mayor precio, que son las que el hallazgo 1 sugiere priorizar, el valor post-obra estimado debe tomarse con más cautela.
- El margen de flipping todavía no descuenta el costo de la obra, que se definirá con cotizaciones por nivel de obra.
- La base corresponde a una sola red inmobiliaria y a una única captura.
