import urllib.request
import logging
from pathlib import Path

# Configure our terminal logger
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class ParisGeographyExtractor:
    """
    Handles the extraction of geographi boundaries from the Paris Open Data API
    Downloads vector data required for spatial joins and masking.
    """

    def __init__(self, raw_data_dir: str = "data/raw"):
        """
        Initializes the extractor with the API endpoint for the Arrondissements.

        Args:
            raw_data_dir (str): The relative path where the GeoJson will be saved.
        """
        self.raw_data_dir = Path(raw_data_dir)
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)

        # API endpoint for GeoJSON format
        self.api_url = (
            "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/"
            "arrondissements/exports/geojson?lang=fr&timezone=Europe%2FParis"
        )

    def download_arrondissements(self, filename: str = "arrondissements.geojson") -> None:
        """
        Connects to the API and downloads the GeoJSON boundary file directly to the raw data directory

        Args:
            filename (str): The desired name for the output file.
        """
        output_path = self.raw_data_dir / filename
        logging.info(f"Downloading Arrondissements boundaries to {output_path}...")

        try:
            urllib.request.urlretrieve(self.api_url, output_path)
            logging.info("Success! Arrondissements GeoJSON secured.")
        except Exception as e:
            logging.error(f"Failed to download file: {e}")
            raise

if __name__ == "__main__":
    extractor = ParisGeographyExtractor()
    extractor.download_arrondissements()