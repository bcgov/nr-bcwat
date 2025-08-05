from etl_pipelines.scrapers.EtlPipeline import EtlPipeline
import polars as pl

"""
The class below is used to test the EtlPipeline class' concrete methods which are:
    - load_data()
    - __load_data_into_tables()
    - get_downloaded_data()
    - get_transformed_data()
So any abstract method will be defined to return None.
"""
class TestEtlPipeline(EtlPipeline):
    __test__ = False

    def __init__(self, name, source_url, destination_tables, expected_dtype, db_conn):
        super().__init__(name, source_url, destination_tables, expected_dtype, db_conn)

    def download_data(self):
        return None

    def transform_data(self):
        return None

    def _load_data_into_tables(self, insert_tablename=None, data=pl.DataFrame(), pkey=None, truncate=False):
        return None
