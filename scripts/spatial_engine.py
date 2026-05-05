import duckdb
import logging
from pathlib import Path


# Let's setup a basic logging to track our script's progress
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class SpatialEngine:
    """
    Handles the spatial integration of tree points and district boundaries.
    Executes the INNER JOIN to filter out external forests
    and prepares the final dataset for Tableau.
    """

    def __init__(self,
                 trees_path: str = "data/processed/trees_clean.parquet",
                 geo_path: str = "data/raw/arrondissements.geojson",
                 output_dir: str = "data/processed"):
        """
        Initializes the engine with paths to the cleaned trees and raw geography.
        """
        self.trees_path = Path(trees_path)
        self.geo_path = Path(geo_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.conn = duckdb.connect(database=":memory:")

    def _setup_extensions(self) -> None:
        """
        Installs and loads the spatial extensions required to read GeoJSON.
        """
        logging.info("Loading DuckDB spatial extension...")
        self.conn.execute("INSTALL spatial;")
        self.conn.execute("LOAD spatial;")

    def merge_and_export(self, filename: str = "trees_final.parquet") -> None:
        """
        Extracts the numeric arrondissement ID, joins the trees to the GeoJSON boundaries,
        and exports the final matched dataset.
        """
        self._setup_extensions()
        output_path = self.output_dir / filename

        logging.info("Executing spatial merge (INNER JOIN)...")

        # Logic:
        # 1. Read the GeoJSON using st_read() spatial function.
        # 2. Extract the integer from thr tree's arrondissement string.
        # 3. INNER JOIN where extracted integer matches `c_ar` from arrondissements table.

        query = f"""
            COPY(
                WITH geo_data AS (
                    SELECT
                        CAST(c_ar AS INTEGER) AS district_id,
                        l_ar AS district_label,
                        l_aroff AS district_name
                    FROM st_read('{self.geo_path.resolve().as_posix()}')
                ),
                tree_data AS (
                    SELECT
                        *,
                        -- Extract forst sequence of numbers found in the string of arrondissement
                        TRY_CAST(REGEXP_EXTRACT(arrondissement, '\\d+') AS INTEGER) AS extracted_id
                    FROM read_parquet('{self.trees_path.resolve().as_posix()}')
                )

                SELECT
                    t.tree_id,
                    t.height_m,
                    t.circumference_cm,
                    t.genre,
                    t.espece,
                    t.dev_stage,
                    t.latitude,
                    t.longitude,
                    g.district_id,
                    g.district_label,
                    g.district_name
                FROM tree_data t
                INNER JOIN geo_data g ON t.extracted_id = g.district_id
            ) TO '{output_path.as_posix()}' (FORMAT 'PARQUET');
        """
        try:
            self.conn.execute(query)
            logging.info(f"Merge successful! Final dataset saved to {output_path}")

            # Validate drop in tree count
            final_count = self.conn.execute(f"SELECT COUNT(*) FROM read_parquet('{output_path}')").fetchone()[0]
            logging.info(f"Trees within the 20 Arrondissements: {final_count:,}")

        except Exception as e:
            logging.error(f"Merge failed: {e}")
            raise

if __name__ == "__main__":
    engine = SpatialEngine()
    engine.merge_and_export()