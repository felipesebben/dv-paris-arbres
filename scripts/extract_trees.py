import duckdb
import logging
from pathlib import Path


# Let's setup a basic logging to track our script's progress
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class ParisTreeExtractor:
    """
    A class to handle the extraction of tree data from the Paris Open Data API.

    This class utilize's DuckDB's httpfs extension to directly read a remote CSV stream and
    persist it locally as a Parquet file. This approach avoids loading the entire dataset into RAM and provides a highly 
    optimized format for subsequent spatial queries.
    """

    def __init__(self, raw_data_dir: str = "data/raw"):
        """
        Initializes the extractor and ensures the target directory exists.

        Args:
            raw_data_dir (str): The relative path to the directory where
                                the raw Parquet files should be saved
        """
        self.raw_data_dir = Path(raw_data_dir)
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)

        self.api_url = (
            "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/"
            "les-arbres/exports/csv?lang=fr&timezone=Europe%2FParis"
            "&use_labels=true&delimiter=%3B"
        )

        # Initialize an in-memory DuckDB connection
        self.conn = duckdb.connect(database= ':memory:')

    def _setup_extensions(self) -> None:
        """
        Installs and loads the necessary DuckDB extensions.
        The httpfs extension is required to read directly from HTTPS URLs.
        """
        logging.info("Installing and loading httpfs extension...")
        self.conn.execute("INSTALL httpfs;")
        self.conn.execute("LOAD httpfs;")

    def extract_to_parquet(self, filename: str = "trees_raw.parquet") -> None:
        """
        Streams the entire CSV from the API and saves it directly to a Parquet file.

        Args:
            filename (str): The desired name for the output Parquet file.
        """
        self._setup_extensions()
        output_path = self.raw_data_dir / filename

        logging.info(f"Initializing full data stream from API to {output_path}...")
        logging.info("This may take a moment depending on your speed connection.")

        # Wrap the read_csv_ayto in a COPY command so we stream directly to disk.
        query = f"""
            COPY (
                SELECT *
                FROM read_csv_auto('{self.api_url}', 
                header=true,
                ignore_errors=true,
                null_padding=true)
            ) TO '{output_path}' (FORMAT 'PARQUET');
        """

        try:
            self.conn.execute(query)
            logging.info("Extraction complete! Parquet file saved successfully.")
        except Exception as e:
            logging.error(f"An error ocurred during extraction: {e}")
            raise


if __name__ == "__main__":
    extractor = ParisTreeExtractor()
    extractor.extract_to_parquet()