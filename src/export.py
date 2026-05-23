import logging
import shutil
import duckdb
from pathlib import Path
from tableauhyperapi import(
    HyperProcess, Telemetry, Connection, CreateMode,
    TableDefinition, TableName, SqlType
)

class HyperExporter:
    """
    Presentation Layer: Handles the bulk-load export into a Tableau .hyper file.
    """

    def __init__(self, db_conn: duckdb.DuckDBPyConnection):
        self.db = db_conn

    def export_to_hyper(self, output_filename: str = "paris_historical_eras.hyper") -> None:
        """
        Bypasses Pandas entirely. DuckDB writes a temporary CSV,
        and Hyper reads it natively for performance gains.
        """
        output_path = Path("data/processed") / output_filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if output_path.is_dir():
            shutil.rmtree(output_path)
        elif output_path.exists():
            output_path.unlink()

        temp_csv = Path("data/tmp/hyper_transfer.csv")

        logging.info("Exporting clean Silver data to temporary CSV...")

        # SELECT statement must match new columns from transformation layer.
        self.db.execute(f"""
            COPY(
                SELECT
                    arr_id,
                    arr_desc,
                    era_label,
                    era_interval,
                    geom_wkt
                FROM silver_paris_buildings
            ) TO '{temp_csv.as_posix()}' (HEADER, DELIMITER ',');
        """)

        logging.info("Bulk-loading CSV directly into Tableau Hyper Engine...")
        with HyperProcess(telemetry=Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            with Connection(hyper.endpoint, str(output_path), CreateMode.CREATE_AND_REPLACE) as conn:
                conn.catalog.create_schema_if_not_exists("Extract")
            
                # Table definition must align with CSV data types
                table_def = TableDefinition(
                    table_name=TableName("Extract", "buildings"),
                    columns = [
                        TableDefinition.Column("arr_code", SqlType.int()),
                        TableDefinition.Column("arr_name", SqlType.text()),
                        TableDefinition.Column("era_label", SqlType.text()),
                        TableDefinition.Column("era_interval", SqlType.text()),
                        # Convert wkt text into valid spatial format
                        TableDefinition.Column("geom", SqlType.geography()),
                    ],
                )

                conn.catalog.create_table(table_def)

                # Bulk-load command
                copy_command = f"""
                    COPY {table_def.table_name}
                    FROM '{temp_csv.absolute().as_posix()}'
                    WITH (FORMAT CSV, HEADER, DELIMITER ',')
                """
                count = conn.execute_command(copy_command)
                logging.info(f"Successfully bulk-loaded {count} buildings into Hyper.")

            # Cleanup temp file
        if temp_csv.exists():
            temp_csv.unlink()
        
        logging.info(f"Gold export complete: {output_path}")