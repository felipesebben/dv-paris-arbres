import duckdb
import logging
from pathlib import Path

class DataWarehouse:
    """
    Infrastructure Layer: Handles persistent DuckDB connection and environment PRAGMAs.
    """
    def __init__(self, db_path: str = "data/warehouse.duckdb"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = duckdb.connect(str(self.db_path))
        self._setup_extensions()

    def _setup_extensions(self) -> None:
        logging.info("Configuring memory limits and loading spatial extensions...")
        
        # Leash the RAM to prevent OS panics, set temp directory for disk spilling
        self.conn.execute("PRAGMA memory_limit='4GB';")
        temp_dir = Path("data/tmp")
        temp_dir.mkdir(parents=True, exist_ok=True)
        self.conn.execute(f"PRAGMA temp_directory='{temp_dir.as_posix()}';")
        
        # Load the spatial engine (must be two separate calls — combined silently fails)
        self.conn.execute("INSTALL spatial;")
        self.conn.execute("LOAD spatial;")

    def close(self):
        self.conn.close()