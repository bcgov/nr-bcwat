from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    ASP_DESTINATION_TABLES,
    ASP_BASE_URLS,
    ASP_DTYPE_SCHEMA,
    ASP_NAME,
    ASP_NETWORK,
    ASP_RENAME_DICT,
    ASP_STATION_SOURCE,
)
from etl_pipelines.utils.functions import (
    setup_logging
)
import polars as pl

logger = setup_logging()

class AspPipeline(StationObservationPipeline):
    def __init__(self, db_conn = None, date_now = None):
        super().__init__(
            name=ASP_NAME, 
            source_url=ASP_BASE_URLS, 
            destination_tables=ASP_DESTINATION_TABLES,
            days=3,
            station_source=ASP_STATION_SOURCE,
            expected_dtype=ASP_DTYPE_SCHEMA,
            column_rename_dict=ASP_RENAME_DICT,
            go_through_all_stations=False,
            network_ids= ASP_NETWORK,
            db_conn=db_conn
        )

        ## Add Implementation Specific attributes below
        self.date_now = date_now.in_tz("America/Vancouver")
        self.end_date = self.date_now.in_tz("UTC")
        self.start_date = self.end_date.subtract(days=self.days).start_of("day")

        self.get_station_list()


    def validate_downloaded_data(self):
        """
        Same method as the method in StationObservationPipeline. The only difference is that the data get's reshaped a little bit.
        By default, the csv that is obtained has it's station IDs as it's columns and datetime as rows. This will be hard to work with later on so edit it before validation. Else we would have to make a dictionary of varying length, depending on the number of station IDs, which will not be ideal.

        Args:   
            None

        Output: 
            None
        """
        for key in self._EtlPipeline__downloaded_data.keys():
            self._EtlPipeline__downloaded_data[key] = (
                self._EtlPipeline__downloaded_data[key]
                .unpivot(index="DATE(UTC)")
            )

        super().validate_downloaded_data()

    def transform_data(self):
        downloaded_data = self.get_downloaded_data()

        if not downloaded_data:
            logger.error(f"No data was downloaded for {self.name}! The attribute __downloaded_data is empty. Exiting")
            raise RuntimeError(f"No data was downloaded for {self.name}! The attribute __downloaded_data is empty. Exiting")
        
        # TODO: Check for new stations and insert them and associated metadata into the database here

        for key in self._EtlPipeline__downloaded_data.keys():
            df = self._EtlPipeline__downloaded_data[key]

            try:
                df = (
                    df
                    .rename(self.column_rename_dict)
                    .with_columns(
                        datestamp = pl.col("datestamp").str.to_datetime("%Y-%m-%d %H:%M", time_zone="UTC", ambiguous="earliest"),
                        qa_id = 0,
                        variable_id = pl.when(key == 'SW')
                            .then(16)
                            .when(key == 'SD')
                            .then(5)
                            .when(key == 'PC')
                            .then(28)
                            .when(key == 'TA')
                            .then(7)
                            .otherise(None),
                        value = pl.col("value").cast(pl.Float64)
                    )
                    .filter(
                        (pl.col("datestamp") >= self.start_date) & 
                        (pl.col("value").is_not_null()) & 
                        (pl.col("value") != pl.lit("99999")) &
                        (pl.col("value") >= 0) if key == 'SW' else True
                    )
                    .select(
                        pl.col("datestamp"),
                        pl.col("variable").str.slice(offset=0, length=5).alias("original_id"),
                        pl.col("value"),
                        pl.col("qa_id"),
                        pl.col("variable_id")
                    )
                    .join(self.station_list, on="original_id", how="inner")
                )
            except Exception as e:
                logger.error(f"Error when trying to transform the data for {self.name}. Error: {e}", exc_info=True)
                raise RuntimeError(f"Error when trying to transform the data for {self.name}. Error: {e}")
        


    def __implementation_specific_private_func(self):
        pass
