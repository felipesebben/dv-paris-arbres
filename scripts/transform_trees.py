import duckdb
import logging
from pathlib import Path

# Configre terminal logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class TreeDataTransformer:
    """
    Handles the transformation of raw tree data into a clean, optimized format.
    Applies filtering, column selection, renaming, and coordinate extraction based on EDA specifications.
    """

    def __init__(self, raw_data_path: str = "data/raw/trees_raw.parquet",
                 processed_dir: str = "data/processed"):
        """
        Initializes the transformer with the file paths.

        Args:
            raw_data_path (str): Path to the raw input Parquet file.
            processed_dir (str): Directory where the clean data will be saved.
        """
        self.raw_data_path = Path(raw_data_path)
        self.processed_dir = Path(processed_dir)

        # Make sure directory exists
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        # Initialize DuckDB in-memory connection
        self.conn = duckdb.connect(database=":memory:")

    def clean_and_export(self, filename: str = "trees_clean.parquet") -> None:
        """
        Executes the SQL transformation to clean the data and exports it directly to a new Parquet file.
        
        Args:
            filename (str): The desired name for the processed output file.
        """

        output_file = self.processed_dir / filename
        logging.info(f"Starting transformation of {self.raw_data_path}...")

        # Embody EDA conclusions in SQL query
        query = f"""
            COPY(
                SELECT
                    IDBASE AS tree_id,
                    "HAUTEUR (m)" AS height_m,
                    "CIRCONFERENCE (cm)" AS circumference_cm,
                    ARRONDISSEMENT,
                    GENRE,
                    "LIBELLE FRANCAIS",
                    ESPECE,
                    "STADE DE DEVELOPPEMENT" AS dev_stage,
                    
                    TRY_CAST(split_part(geo_point_2d, ',', 1) AS DOUBLE) AS latitude,
                    TRY_CAST(split_part(geo_point_2d, ',', 2) AS DOUBLE) AS longitude
                FROM read_parquet('{self.raw_data_path}')
                WHERE "HAUTEUR (m)" BETWEEN 0 AND 50
                AND "CIRCONFERENCE (cm)"  BETWEEN 0 AND 750     
                ) TO '{output_file}' (FORMAT 'PARQUET');
        """

        try:
            self.conn.execute(query)
            logging.info(f"Transformation complete! Clean data saved to {output_file}")

            # Run quick validation to show final row count
            count = self.conn.execute(f"SELECT COUNT(*) FROM read_parquet('{output_file}')").fetchone()[0]
            logging.info(f"Final tree count after filtering: {count:,}")

        except Exception as e:
            logging.error(f"Transformation failed: {e}")
            raise

if __name__ == "__main__":
    transformer = TreeDataTransformer()
    transformer.clean_and_export()
        