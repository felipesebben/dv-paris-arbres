import duckdb
import logging


class BDNBTransformer:
    """
    Business Layer: Executes the spatial joins and era categorizations.
    """
    def __init__(self, db_conn: duckdb.DuckDBPyConnection):
        # Accept single active connection passed from the orchestrator
        self.db = db_conn

    def build_silver_layer(self) -> None:
        """
        Reads GeoJson directly, performs an Inner Join against the Arrondissements,
        calculates the historical eras, preps the geometry for Tableau.
        """
        logging.info("Executing Spatial Join and Historical Calculations...")

        self.db.execute("""
            CREATE OR REPLACE TABLE silver_paris_buildings AS 
            
            WITH districts AS (
                    SELECT
                        c_ar AS arr_id,
                        l_ar AS arr_desc,
                        l_aroff AS arr_name_desc,
                        geom AS district_geom
                    FROM st_read('data/raw/arrondissements.geojson')
            ),
            buildings AS (
                    SELECT
                        c_perconst AS id_era,
                        geom AS bldg_geom
                    FROM st_read('data/raw/EMPRISE_BATIE_PARIS.geojson')
            )
            
            SELECT
                d.arr_id,
                d.arr_desc,
                b.id_era,
                CASE
                    WHEN b.id_era IN (1, 2) THEN 'Pre-Haussmannian'
                    WHEN b.id_era = 3 THEN 'Haussman & Belle Époque'
                    WHEN b.id_era = 4 THEN 'Interwar'
                    WHEN b.id_era IN(5, 6) THEN 'Les Trente Glorieuses'
                    WHEN b.id_era BETWEEN 7 AND 11 THEN 'Contemporary'
                    WHEN b.id_era = 99 THEN 'Unknown'
                    ELSE 'Unknown'
                END as era_label,
                CASE
                    WHEN b.id_era IN (1, 2) THEN 'Before 1850'
                    WHEN b.id_era = 3 THEN '1851 – 1914'
                    WHEN b.id_era = 4 THEN '1915 – 1939'
                    WHEN b.id_era IN(5, 6) THEN '1940 – 1975'
                    WHEN b.id_era BETWEEN 7 AND 11 THEN '1976 – Present'
                    WHEN b.id_era = 99 THEN 'Unknown'
                    ELSE 'Unknown'
                END as era_interval,
                ST_AsText(b.bldg_geom) AS geom_wkt
            FROM buildings b
            INNER JOIN districts d
            ON ST_Intersects(b.bldg_geom, d.district_geom)
        """
        )

        logging.info("Silver Layer complete. Ready for bulk-load export.")
