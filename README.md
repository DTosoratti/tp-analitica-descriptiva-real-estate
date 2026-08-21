# Real Estate Analytics 🏠

## Analítica Descriptiva — ITBA

Trabajo Práctico Integrador de la materia **Analítica Descriptiva** de la Licenciatura en Analítica Empresarial y Social del ITBA.

### Integrantes
- Dante Tosoratti
- Martina Risso
- María Sol Allievi
- Tomás Agustín Picciolo

## Descripción

El proyecto tiene como objetivo analizar el mercado de departamentos usados en venta en la Ciudad Autónoma de Buenos Aires (CABA), con foco en la detección de propiedades potencialmente subvaluadas y oportunidades de inversión.

El análisis se desarrollará desde la perspectiva de un **fondo de inversión inmobiliaria**, buscando construir valores de referencia a partir de propiedades comparables según ubicación, superficie, cantidad de ambientes, estado y otras características relevantes.

Sobre las oportunidades detectadas se analizarán especialmente aquellas propiedades que requieran refacción y puedan presentar potencial para una estrategia de **flipping**.

## Fuente de datos

La fuente principal será **Argenprop**, mediante Web Scraping utilizando como punto de partida el scraper provisto por la cátedra.

Posteriormente, los datos serán enriquecidos con fuentes externas relevantes para el análisis.

## Estructura del repositorio

- `data/raw/`: datos originales obtenidos mediante scraping.
- `data/processed/`: datos limpios y transformados.
- `notebooks/`: notebooks de extracción y análisis.
- `src/`: scripts y funciones.
- `reports/`: informes y entregables.
