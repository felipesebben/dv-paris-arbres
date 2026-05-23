import logging
from src.infrastructure import DataWarehouse
from src.transformations import BDNBTransformer
from src.export import HyperExporter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

def run_pipeline():
    # 1. start the engine
    warehouse = DataWarehouse(db_path="data/warehouse.duckdb")

    try:
        # 2. transform the data
        transformer = BDNBTransformer(db_conn=warehouse.conn)
        transformer.build_silver_layer()

        # 3. export to Tableau
        exporter = HyperExporter(db_conn=warehouse.conn)
        exporter.export_to_hyper(output_filename="paris_historical_eras.hyper")

    finally:
        # 4. close the connection
        warehouse.close()

if __name__ == "__main__":
    run_pipeline()