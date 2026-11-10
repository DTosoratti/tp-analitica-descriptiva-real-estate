# Hallazgos que cambian el rumbo del negocio

**Real Estate Analytics (ITBA, Analítica Descriptiva)**

**Cliente:** Fondo de Inversión Inmobiliario que busca propiedades subvaluadas en CABA y oportunidades de refacción y reventa (flipping).

**Base:** 9.499 departamentos usados en venta publicados en RE/MAX (corte aproximado: 26/09/2026). El detalle técnico está en las notebooks 03 a 11; las cifras de este documento salen de ellas.

---

## Resumen

El fondo buscaba dos cosas: propiedades publicadas por debajo de su valor y unidades a reciclar en las que el descuento pague la obra. Con los datos de RE/MAX, **ninguna de las dos aparece como una estrategia general**: el mercado ya descuenta el estado de las unidades, pero no lo suficiente para pagar una obra, y buena parte de lo que parece "muy barato" es un producto distinto. Lo que sí deja el análisis es una lista corta y revisada de candidatas, un techo de oferta para cada unidad a reciclar y una explicación de por qué el resultado es este.

---

## 1. El mercado ya descuenta el estado, pero no paga la obra

**Evidencia.** Las unidades que necesitan obra se publican, en la mediana, **17,4 % por debajo de su benchmark**; las que están en buen estado o recicladas, en el benchmark. La diferencia entre ambos grupos es de **17,5 puntos** (IC 95 %: 15,3 a 19,9), similar en todas las comunas (Kruskal-Wallis, p = 0,26) y estable al controlar por ubicación, antigüedad y amenities (≈ 14 % en el modelo hedónico). Pero, una vez descontados obra, contingencia, transacción, tenencia y costo de oportunidad, **ninguna de las 428 unidades es rentable en el escenario conservador y solo 2 en el base**. En la mediana, el descuento alcanza para pagar unos 24 USD/m² de obra, cuando una obra media cuesta unos 500 y una integral unos 1.150. La mitad de las unidades (212) no cierra a ningún precio de compra.

**Cambio de rumbo.** No comprar unidades a reciclar al precio publicado para hacer flipping. Usar el **precio máximo de oferta** de cada unidad como techo: el mayor precio al que se cumplen a la vez un ROI base de 15 %, un ROI no negativo en el escenario conservador y una brecha de al menos 25 %. Con esa regla, ninguna unidad cierra con un descuento de hasta 10 % y solo una con hasta 30 %. Antes de cualquier oferta, **visitar y cotizar la obra**: el nivel de obra es el supuesto que más mueve el resultado (si todas fueran livianas, 137 serían rentables en el escenario base); el tipo de cambio casi no influye.

---

## 2. Lo que parece "muy barato" suele ser otro producto

**Evidencia.** Al leer título y descripción de los primeros puestos del ranking de visitas aparecieron un precio que es solo un anticipo del 50 %, dos ventas de nuda propiedad, una unidad escriturada como cochera, oficinas, un PH y tres avisos con las coordenadas en otro barrio (por lo que su benchmark se calculó contra el barrio equivocado). Se excluyeron 12 de las 249 candidatas; otras 29 tienen una razón identificable para el descuento (inquilino, uso profesional, sucesión, posible duplicado) y quedan marcadas para verificar. Además, 120 de las 836 baratas de la base tienen indicadores de posible error de carga y no atraen más demanda que una propiedad a precio de mercado.

**Cambio de rumbo.** Ningún ranking automático se presenta sin revisar los primeros puestos. La revisión quedó incorporada al pipeline (`src/revision_avisos.py` y `data/validation/revision_lista_visitas.csv`) y el fondo recibe **237 candidatas revisadas**.

---

## 3. Por qué casi nada cierra: la fuente

**Evidencia.** En RE/MAX cada aviso lo publica un agente que tasa la propiedad antes de publicarla y cuya comisión depende de vender. Es poco probable que publique con errores de valuación groseros. Los resultados son coherentes con eso: la cola de la brecha está poblada por diferencias de producto (hallazgo 2) y el descuento por estado está bien calibrado, pero no sobra para la obra (hallazgo 1).

**Cambio de rumbo.** En avisos tasados por un agente, "buscar precios mal puestos" rinde poco; la oportunidad está en descuentos con una causa que el fondo puede aceptar o resolver (inquilino, sucesión, obra liviana). La premisa original es más plausible en portales donde publican particulares (por ejemplo, avisos de dueño directo en Zonaprop o MercadoLibre). Antes de descartarla, conviene correr el mismo pipeline sobre esa fuente y comparar la proporción de baratas.

---

## 4. Comparar sin tener en cuenta la categoría del edificio genera falsas oportunidades

**Evidencia.** A igualdad de barrio, tamaño y antigüedad, la cochera incluida se asocia con un USD/m² 14 % mayor y el gimnasio con uno 10 % mayor. De las 801 propiedades baratas según el benchmark de comparables, solo **325 (41 %) siguen siéndolo** con un benchmark ajustado por antigüedad y características, que además tiene menor error fuera de muestra (MAPE de 15,3 % contra 19,6 %). Las demás tienen, sobre todo, menos amenities y menos cochera.

**Cambio de rumbo.** Priorizar las baratas según ambos benchmarks. Como los dos se estiman sobre los mismos avisos, su coincidencia es consistencia interna y no una confirmación independiente: sigue haciendo falta la visita.

---

## 5. La dispersión de precios no señala oportunidades

**Evidencia.** Los estratos con precios más dispersos tienen más baratas, pero eso ocurre por construcción: si "barata" es estar 25 % por debajo de la mediana, en un estrato más disperso más avisos caen lejos de ella. Frente a un nulo que preserva la dispersión de cada estrato, la proporción de avisos en la cola es la esperada (9,6 % observada contra 9,6 % esperada) y el exceso no crece con la dispersión.

**Cambio de rumbo.** No usar la dispersión de un barrio o estrato como criterio para buscar oportunidades. Sirve para describir dónde está la cola y como alerta de que el benchmark de ese estrato es menos confiable.

---

## 6. Las candidatas atraen demanda: hay que moverse rápido

**Evidencia.** El 41 % de las candidatas de mayor confianza ya está reservado o en negociación, contra el 23 % de las no baratas (chi-cuadrado, p < 0,001).

**Cambio de rumbo.** Acortar el ciclo de decisión y actualizar el ranking con capturas sucesivas del extractor. Con una sola captura no se puede medir la velocidad con que salen del mercado.

---

## Recomendaciones para el fondo

| # | Recomendación | Basada en |
| --- | --- | --- |
| 1 | Visitar las 237 candidatas revisadas (`data/processed/ranking_visitas.csv`), por tramos y no por puesto; confirmar primero las 29 marcadas para verificar | Hallazgos 2, 4 y 6; notebook 09 |
| 2 | No hacer flipping a precio publicado; ofertar como máximo el precio máximo de oferta de cada unidad | Hallazgo 1; notebook 07 |
| 3 | Antes de ofertar, visita técnica y cotización de obra propia | Hallazgo 1 |
| 4 | Revisar título, descripción y ubicación de cada aviso antes de visitarlo | Hallazgo 2 |
| 5 | Probar el pipeline sobre avisos de particulares antes de abandonar la búsqueda de precios mal puestos | Hallazgo 3 |
| 6 | Actualizar el ranking con capturas sucesivas | Hallazgo 6 |

## Limitaciones

- Los precios son de publicación, no de cierre: el descuento es relativo a la oferta, y la brecha entre publicación y cierre no está medida.
- Una sola red inmobiliaria y una sola captura: no representa a todo el mercado ni permite medir permanencia.
- El estado se infiere del texto de los avisos. Se validó con doble lectura (accuracy de 78 %, kappa de 0,70) y con muestras dirigidas, siempre sobre el texto y no sobre el estado físico real.
- Los costos de obra son supuestos con fuente secundaria, no cotizaciones propias, y el nivel de obra se infiere del texto.
- La revisión de la lista de visitas es manual en los primeros 42 puestos y automática en el resto.
