# Paris and its Trees

A data art and engineering project visualizing the natural structure of Paris using the city's open data on its tree population (`les-arbres`). This project transforms over 200,000 geographic data points into a minimalist, high-resolution poster featuring a main map and small multiples analyzing tree density by arrondissement.

## Tech Stack
* **Data Extraction & Transformation:** DuckDB (Spatial Extension)
* **Geospatial Processing:** QGIS
* **Visualization Engine:** Tableau
* **Design & Typography:** Figma
* **Environment Management:** Python / Poetry

## Project Structure
```text
paris-trees-canopy/
├── data/
│   ├── raw/            # Ignored: Raw Open Data CSVs and Shapefiles
│   └── processed/      # Ignored: Processed GeoJSONs and CSVs
├── scripts/            # DuckDB and Python ETL scripts
├── output/             # Final visualization assets
├── .env                # Local environment variables (Ignored)
└── pyproject.toml      # Poetry dependencies
```

## Methodology & Stages
### Stage 1: Setup & Infrastructure (Current)

Initialized Git repository and environment using Poetry.

Established standard folder structure for ETL workflows.

### Stage 2: Data Extraction & Transformation (DuckDB) (Upcoming)

Connect to Paris Open Data API to extract the Les arbres dataset.

Perform spatial joins against arrondissement boundaries.

Calculate density and summary statistics (e.g., oldest tree, most common species).

### Stage 3: Geometry & Masking (QGIS) (Upcoming)

Dissolve building footprints into a single optimized vector shape.

Create the "Inverse Mask" to generate the map's edge-fade vignette.

### Stage 4: Visualization & Rendering (Tableau) (Upcoming)

Plot tree coordinates using an additive opacity technique for density shading.

Generate "Ghost Map" small multiples for the 20 arrondissements.

### Stage 5: Final Composition (Figma) (Upcoming)

Assemble vector PDFs, apply the vignette mask, and add Futura typography.

Export print-ready file.