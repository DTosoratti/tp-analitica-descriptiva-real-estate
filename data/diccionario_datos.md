# Diccionario de datos

Base: `data/processed/remax_deptos_features.csv` (9,499 avisos, 100 variables). Fecha de corte de la extracción: 26/09/2026 (aproximada).

| Variable | Descripción | Tipo | Unidad | Fuente | Transformación | Faltantes (%) |
| --- | --- | --- | --- | --- | --- | --- |
| ID | Identificador del aviso en RE/MAX | int64 | — | RE/MAX (base raw) | Sin cambios | 0.0 |
| ID_Entidad | Identificador interno de la entidad en la API | object | — | RE/MAX (base raw) | Sin cambios | 0.0 |
| Operacion | Tipo de operación (constante: venta) | object | — | RE/MAX (base raw) | Sin cambios | 0.0 |
| Tipo_Propiedad | Tipología homogeneizada (constante: departamento) | object | — | RE/MAX (base raw) | Subcategorías de departamento unificadas; la original se conserva en Tipo_Propiedad_Original | 0.0 |
| Titulo | Título del aviso | object | Texto | RE/MAX (base raw) | Sin cambios | 0.0 |
| Descripcion | Descripción del aviso | object | Texto | RE/MAX (base raw) | Sin cambios; falta en 54 avisos por falla del endpoint de detalle | 0.6 |
| Fecha_Publicacion | Fecha de publicación (no informada por la fuente) | float64 | Fecha | RE/MAX (base raw) | 100% faltante; se conserva para documentar la limitación | 100.0 |
| Antiguedad | Antigüedad del edificio | float64 | Años | RE/MAX (base raw) | Valores 0 en stock usado reemplazados por faltante | 3.4 |
| Apto_Credito | Indica si el aviso declara apto crédito hipotecario | object | Booleano | RE/MAX (base raw) | Sin cambios | 0.6 |
| Amenities | Lista de amenities informada por la fuente | object | Texto | RE/MAX (base raw) | Sin cambios | 17.3 |
| Moneda | Moneda del precio (constante: USD) | object | — | RE/MAX (base raw) | Se excluyeron los avisos con precio en pesos | 0.0 |
| Precio_Valor | Precio publicado | float64 | USD | RE/MAX (base raw) | Sin cambios | 0.0 |
| Moneda_Expensas | Moneda de las expensas | object | — | RE/MAX (base raw) | Corregida a ARS cuando el monto en USD era inverosímil | 0.0 |
| Expensas | Expensas mensuales informadas | float64 | ARS | RE/MAX (base raw) | Ceros sin mención de 'sin expensas', valores de relleno y montos menores a ARS 30.000 reemplazados por faltante | 12.3 |
| Precio_m2_Total | Precio por m² sobre la superficie total | float64 | USD/m² | RE/MAX (base raw) | Sin cambios | 0.0 |
| Precio_m2_Cubierto | Precio por m² sobre la superficie cubierta | float64 | USD/m² | RE/MAX (base raw) | Faltante si la superficie cubierta es 0 | 0.0 |
| Ambientes | Cantidad de ambientes | int64 | Unidades | RE/MAX (base raw) | Validada contra el título (ver Flag_Ambientes_Dudoso) | 0.0 |
| Dormitorios | Cantidad de dormitorios | int64 | Unidades | RE/MAX (base raw) | Monoambientes unificados con 0 dormitorios | 0.0 |
| Baños | Cantidad de baños | int64 | Unidades | RE/MAX (base raw) | Sin cambios | 0.0 |
| Superficie_Total_m2 | Superficie total | float64 | m² | RE/MAX (base raw) | Se excluyeron superficies mayores a 1.000 m² (errores de carga) | 0.0 |
| Superficie_Cubierta_m2 | Superficie cubierta | float64 | m² | RE/MAX (base raw) | Valor 0 reemplazado por faltante | 0.0 |
| Direccion | Dirección informada | object | Texto | RE/MAX (base raw) | Sin cambios | 0.0 |
| Barrio | Etiqueta de ubicación de la fuente (incluye subzonas informales) | object | Texto | RE/MAX (base raw) | Sin cambios; para el análisis se usa Barrio_Oficial | 0.0 |
| Ubicacion | Ubicación informada por la fuente | object | Texto | RE/MAX (base raw) | Sin cambios | 0.0 |
| Latitud | Latitud del aviso | float64 | Grados (WGS84) | RE/MAX (base raw) | Eliminada en 3 avisos con coordenadas fuera de CABA | 0.0 |
| Longitud | Longitud del aviso | float64 | Grados (WGS84) | RE/MAX (base raw) | Eliminada en 3 avisos con coordenadas fuera de CABA | 0.0 |
| Estado_Publicacion | Estado comercial de la publicación: active, reserved o negotiation | object | Categoría | RE/MAX (base raw) | Renombrada (en la fuente se llama Estado) | 0.0 |
| ID_Interno | Identificador interno de la publicación | object | — | RE/MAX (base raw) | Sin cambios | 0.0 |
| Link | URL del aviso | object | Texto | RE/MAX (base raw) | Sin cambios | 0.0 |
| Tipo_Propiedad_Original | Subcategoría de departamento según RE/MAX | object | Categoría | Notebook 02 (limpieza) | Copia de Tipo_Propiedad antes de homogeneizarla | 0.0 |
| Ambientes_Titulo | Cantidad de ambientes declarada en el título | float64 | Unidades | Notebook 02 (limpieza) | Extraída del título con expresiones regulares | 6.5 |
| Flag_Ambientes_Dudoso | El título contradice la variable Ambientes | bool | Booleano | Notebook 02 (limpieza) | Comparación Ambientes vs. Ambientes_Titulo | 0.0 |
| Flag_Dormitorios_Inconsistente | Dormitorios mayor o igual que ambientes en unidades de 2 o más ambientes | bool | Booleano | Notebook 02 (limpieza) | Regla de consistencia | 0.0 |
| Flag_Posible_Republicacion | Mismas coordenadas, superficies y ambientes que otro aviso, con distinto precio | bool | Booleano | Notebook 02 (limpieza) | Detección de duplicados (nivel 3) | 0.0 |
| Expensas_Informadas | El aviso informa expensas válidas | bool | Booleano | Notebook 03 (variables y KPIs) | Expensas no faltantes, después de tratar los valores de relleno | 0.0 |
| Antiguedad_Informada | El aviso informa la antigüedad | bool | Booleano | Notebook 02 (limpieza) | Antiguedad no faltante | 0.0 |
| Amenities_Informadas | El aviso informa la lista de amenities | bool | Booleano | Notebook 02 (limpieza) | Amenities no faltante | 0.0 |
| Flag_Atipico_Bajo | Valor atípicamente bajo en precio, superficie o USD/m² | bool | Booleano | Notebook 02 (limpieza) | Debajo de Q1 − 1,5 IQR en escala Box-Cox | 0.0 |
| Flag_Atipico_Alto | Valor atípicamente alto en precio, superficie o USD/m² | bool | Booleano | Notebook 02 (limpieza) | Encima de Q3 + 1,5 IQR en escala Box-Cox | 0.0 |
| Flag_Extremo | Valor extremo en precio, superficie o USD/m² | bool | Booleano | Notebook 02 (limpieza) | Fuera de 3 IQR en escala Box-Cox | 0.0 |
| Flag_Outlier_Multivariado | Combinación inusual de USD/m², superficie y ambientes | bool | Booleano | Notebook 02 (limpieza) | Distancia de Mahalanobis² mayor al percentil 97,5 de chi² con 3 gl | 0.0 |
| Barrio_Oficial | Barrio oficial de CABA | object | Categoría | BA Data — Barrios | Unión espacial punto en polígono; 3 avisos asignados por su etiqueta | 0.0 |
| Comuna | Comuna oficial de CABA | Int64 | 1 a 15 | BA Data — Barrios | Unión espacial punto en polígono | 0.0 |
| Flag_Coordenadas_Invalidas | Coordenadas fuera de CABA en una propiedad de la Ciudad | bool | Booleano | Notebook 03 (variables y KPIs) | Barrio asignado por la etiqueta y coordenadas eliminadas | 0.0 |
| Luminoso | El aviso menciona luminosidad | bool | Booleano | Notebook 03 (variables y KPIs) | RegEx sobre título y descripción, con control de negación | 0.0 |
| Vista | El aviso menciona vista abierta, panorámica o al río | bool | Booleano | Notebook 03 (variables y KPIs) | RegEx sobre título y descripción | 0.0 |
| Silencioso | El aviso menciona que la unidad o el entorno son silenciosos o tranquilos | bool | Booleano | Notebook 03 (variables y KPIs) | RegEx con control de negación | 0.0 |
| Contrafrente | El aviso menciona orientación al contrafrente | bool | Booleano | Notebook 03 (variables y KPIs) | RegEx sobre título y descripción | 0.0 |
| Al_Frente | El aviso menciona orientación al frente o a la calle | bool | Booleano | Notebook 03 (variables y KPIs) | RegEx; excluye 'al frente de…' | 0.0 |
| Apto_Profesional | El aviso declara apto profesional | bool | Booleano | Notebook 03 (variables y KPIs) | RegEx sobre título y descripción | 0.0 |
| Reciclado_Texto | El aviso menciona reciclado o refacción (de la unidad o de un ambiente) | bool | Booleano | Notebook 03 (variables y KPIs) | RegEx con control de negación | 0.0 |
| A_Refaccionar | El aviso indica que la unidad debe refaccionarse o reciclarse | bool | Booleano | Notebook 03 (variables y KPIs) | RegEx con control de negación | 0.0 |
| Pileta | Disponibilidad de pileta | bool | Booleano | Notebook 03 (variables y KPIs) | Lista de amenities de la fuente o mención en el texto | 0.0 |
| SUM | Disponibilidad de salón de usos múltiples | bool | Booleano | Notebook 03 (variables y KPIs) | Lista de amenities o texto | 0.0 |
| Parrilla | Disponibilidad de parrilla (propia o del edificio) | bool | Booleano | Notebook 03 (variables y KPIs) | Lista de amenities o texto | 0.0 |
| Gimnasio | Disponibilidad de gimnasio | bool | Booleano | Notebook 03 (variables y KPIs) | Lista de amenities o texto | 0.0 |
| Laundry | Disponibilidad de laundry o lavadero | bool | Booleano | Notebook 03 (variables y KPIs) | Lista de amenities o texto | 0.0 |
| Seguridad | Seguridad o vigilancia 24 horas | bool | Booleano | Notebook 03 (variables y KPIs) | Lista de amenities o texto | 0.0 |
| Solarium | Disponibilidad de solarium | bool | Booleano | Notebook 03 (variables y KPIs) | Lista de amenities o texto | 0.0 |
| Balcon | Disponibilidad de balcón | bool | Booleano | Notebook 03 (variables y KPIs) | Lista de amenities o texto | 0.0 |
| Terraza | Disponibilidad de terraza (propia o común) | bool | Booleano | Notebook 03 (variables y KPIs) | Lista de amenities o texto | 0.0 |
| Patio | Disponibilidad de patio | bool | Booleano | Notebook 03 (variables y KPIs) | Lista de amenities o texto | 0.0 |
| Ascensor | Disponibilidad de ascensor | bool | Booleano | Notebook 03 (variables y KPIs) | Lista de amenities o texto | 0.0 |
| Baulera | Disponibilidad de baulera | bool | Booleano | Notebook 03 (variables y KPIs) | Lista de amenities o texto | 0.0 |
| Cochera_Mencion | El aviso menciona una cochera | bool | Booleano | Notebook 03 (variables y KPIs) | RegEx (incluye plurales) | 0.0 |
| Cochera_No_Incluida | El aviso aclara que la cochera es opcional o no está incluida | bool | Booleano | Notebook 03 (variables y KPIs) | RegEx | 0.0 |
| Cochera_Incluida | Cochera incluida en el precio | bool | Booleano | Notebook 03 (variables y KPIs) | Cochera_Mencion y no Cochera_No_Incluida | 0.0 |
| Reciclado_Parcial | Menciona el reciclado de un solo ambiente sin evidencia de reciclado integral | bool | Booleano | Notebook 03 (variables y KPIs) | RegEx (cocina, baño) sin señal de reciclado integral | 0.0 |
| Estado_Propiedad | Estado de conservación: Necesita_obra, Reciclada_refaccionada, Buen_estado o Sin_clasificar | object | Categoría | Notebook 03 (variables y KPIs) | Jerarquía de señales RegEx con control de negación y excepciones manuales | 0.0 |
| Estado_Agrupado | Estado agrupado: Necesita_obra, Buen_o_reciclada o Sin_clasificar | object | Categoría | Notebook 03 (variables y KPIs) | Agrupa Buen_estado y Reciclada_refaccionada | 0.0 |
| Flag_Senal_Contradictoria | El texto del aviso combina señales de estado opuestas | bool | Booleano | Notebook 03 (variables y KPIs) | Señal de obra fuerte junto con buen estado o reciclado integral, o reciclado integral junto con señal de obra débil; no modifica la clasificación | 0.0 |
| Superficie_Descubierta_m2 | Superficie descubierta | float64 | m² | Notebook 03 (variables y KPIs) | Superficie total − superficie cubierta | 0.0 |
| Flag_Superficie_Homogeneizada_Imputada | La superficie homogeneizada se calculó con la total por falta de la cubierta | bool | Booleano | Notebook 03 (variables y KPIs) | — | 0.0 |
| Superficie_Homogeneizada_m2 | Superficie homogeneizada | float64 | m² | Notebook 03 (variables y KPIs) | Cubierta + 0,5 × descubierta | 0.0 |
| USD_m2_Homogeneizado | Precio por m² homogeneizado | float64 | USD/m² | Notebook 03 (variables y KPIs) | Precio_Valor / Superficie_Homogeneizada_m2 | 0.0 |
| Ambientes_Grupo | Grupo de ambientes: 1, 2, 3, 4, 5+ | object | Categoría | Notebook 03 (variables y KPIs) | Agrupación de Ambientes | 0.0 |
| Banda_Superficie | Tercil de superficie dentro del grupo de ambientes: Chica, Media, Grande | object | Categoría | Notebook 03 (variables y KPIs) | Terciles de Superficie_Homogeneizada_m2 por Ambientes_Grupo | 0.0 |
| Banda_Antiguedad | Banda de antigüedad: Hasta_10, 11_30, 31_50, Mas_50, Sin_dato | object | Categoría | Notebook 03 (variables y KPIs) | Cortes en 10, 30 y 50 años | 0.0 |
| Flag_Comparable_Valido | Puede actuar como comparable en el benchmark | bool | Booleano | Notebook 03 (variables y KPIs) | Excluye necesita obra, extremos y ambientes dudosos | 0.0 |
| Benchmark_USD_m2 | Mediana del USD/m² de los comparables | float64 | USD/m² | Notebook 03 (variables y KPIs) | Benchmark jerárquico (4 niveles, mínimo 10 comparables, leave-one-out) | 0.5 |
| P25_USD_m2_Comparable | Percentil 25 del USD/m² de los comparables | float64 | USD/m² | Notebook 03 (variables y KPIs) | Benchmark jerárquico | 0.5 |
| N_Comparables | Cantidad de comparables usados en el benchmark | float64 | Unidades | Notebook 03 (variables y KPIs) | Benchmark jerárquico | 0.5 |
| Nivel_Benchmark | Nivel de la jerarquía usado (1 = más fino, 4 = más amplio) | Int64 | 1 a 4 | Notebook 03 (variables y KPIs) | Benchmark jerárquico | 0.5 |
| Precio_Esperado | Precio esperado según comparables | float64 | USD | Notebook 03 (variables y KPIs) | Benchmark_USD_m2 × Superficie_Homogeneizada_m2 | 0.5 |
| Gap_Subvaluacion_pct | Gap de subvaluación | float64 | % | Notebook 03 (variables y KPIs) | (Precio_Esperado − Precio_Valor) / Precio_Esperado × 100 | 0.5 |
| Clasificacion_Oportunidad | Categoría según la definición de propiedad barata (umbral de gap 25%) | object | Categoría | Notebook 03 (variables y KPIs) | Gap, cuartil inferior del grupo, estado e indicadores de verificación | 0.0 |
| PER_USD_m2_P25 | Percentil 25 del USD/m² de comparables en buen estado o reciclados | float64 | USD/m² | Notebook 03 (variables y KPIs) | Benchmark jerárquico sobre Buen_o_reciclada; solo para Necesita_obra | 95.5 |
| PER_USD_m2_Base | Mediana del USD/m² de comparables en buen estado o reciclados | float64 | USD/m² | Notebook 03 (variables y KPIs) | Ídem | 95.5 |
| PER_USD_m2_P75 | Percentil 75 del USD/m² de comparables en buen estado o reciclados | float64 | USD/m² | Notebook 03 (variables y KPIs) | Ídem | 95.5 |
| PER_N_Comparables | Cantidad de comparables usados en el PER | float64 | Unidades | Notebook 03 (variables y KPIs) | Ídem | 95.5 |
| PER_Nivel | Nivel de la jerarquía usado en el PER | Int64 | 1 a 4 | Notebook 03 (variables y KPIs) | Ídem | 95.5 |
| PER_Conservador | Valor post-obra, escenario conservador | float64 | USD | Notebook 03 (variables y KPIs) | PER_USD_m2_P25 × Superficie_Homogeneizada_m2 | 95.5 |
| PER_Base | Valor post-obra, escenario base | float64 | USD | Notebook 03 (variables y KPIs) | PER_USD_m2_Base × Superficie_Homogeneizada_m2 | 95.5 |
| PER_Optimista | Valor post-obra, escenario optimista | float64 | USD | Notebook 03 (variables y KPIs) | PER_USD_m2_P75 × Superficie_Homogeneizada_m2 | 95.5 |
| Potencial_Bruto_Conservador_pct | Revalorización bruta, escenario conservador (no descuenta costos) | float64 | % | Notebook 03 (variables y KPIs) | (PER_Conservador − Precio_Valor) / Precio_Valor × 100 | 95.5 |
| Potencial_Bruto_Base_pct | Revalorización bruta, escenario base (no descuenta costos) | float64 | % | Notebook 03 (variables y KPIs) | (PER_Base − Precio_Valor) / Precio_Valor × 100 | 95.5 |
| Potencial_Bruto_Optimista_pct | Revalorización bruta, escenario optimista (no descuenta costos) | float64 | % | Notebook 03 (variables y KPIs) | (PER_Optimista − Precio_Valor) / Precio_Valor × 100 | 95.5 |
| Expensas_por_m2 | Expensas por m² homogeneizado | float64 | ARS/m² | Notebook 03 (variables y KPIs) | Expensas / Superficie_Homogeneizada_m2 | 10.3 |
| Expensas_Imputadas | Expensas con faltantes imputados | float64 | ARS | Notebook 03 (variables y KPIs) | KNN (k = 20) sobre el logaritmo, con factor de ajuste de nivel 1,119; los valores observados no se modifican | 0.0 |
| Flag_Expensas_Imputadas | Las expensas fueron imputadas | bool | Booleano | Notebook 03 (variables y KPIs) | — | 0.0 |
