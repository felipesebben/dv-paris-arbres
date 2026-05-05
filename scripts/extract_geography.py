import json
import logging
import requests
from pathlib import Path

# Configure our terminal logger
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class ParisGeographyExtractor:
    """
    Handles the extraction of geographic boundaries from the Paris Open Data API.
    Downloads vector data (polygons), handles automatic decompression, and saves
    as a clean GeoJSON file.
    """

    def __init__(self, raw_data_dir: str = "data/raw"):
        """
        Initializes the extractor with the API endpoint for the Arrondissements.
        
        Args:
            raw_data_dir (str): The relative path where the GeoJSON will be saved.
        """
        self.raw_data_dir = Path(raw_data_dir)
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        
        # The API endpoint requesting the data specifically in GeoJSON format
        self.api_url = (
            "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/"
            "arrondissements/exports/geojson?lang=fr&timezone=Europe%2FParis"
        )

    def download_arrondissements(self, filename: str = "arrondissements.geojson") -> None:
        """
        Connects to the API, decompresses the response, saves the GeoJSON natively,
        and prints a preview of the first row to the terminal.
        
        Args:
            filename (str): The desired name for the output file.
        """
        output_path = self.raw_data_dir / filename
        logging.info("Downloading Arrondissements boundaries from API...")
        
        try:
            # The 'requests' library automatically handles gzip decompression
            response = requests.get(self.api_url)
            response.raise_for_status() # Check for HTTP errors (like 404 or 500)
            
            # Parse the text into a Python list/dictionary
            geo_data = response.json()
            
            # Save the clean text to disk, preserving French characters (utf-8)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(geo_data, f, ensure_ascii=False, indent=2)
                
            logging.info(f"Success! Uncompressed GeoJSON saved to {output_path}")
            
            # --- The Data Preview ---
            logging.info("--- Data Preview (First Row Attributes) ---")
            features = geo_data.get("features", [])
            if features:
                first_row = features[0].get("properties", {})
                preview = {k:v for k, v in first_row.items() if k != "geom"}
                print(json.dumps(preview, indent=2, ensure_ascii=False))
            
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Network error during download: {e}")
            raise
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            raise

if __name__ == "__main__":
    extractor = ParisGeographyExtractor()
    extractor.download_arrondissements()