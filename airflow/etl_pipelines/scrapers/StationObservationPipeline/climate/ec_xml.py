from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
from etl_pipelines.utils.constants import (
    EC_XML_BASE_URL,
    EC_XML_DESTINATION_TABLES,
    EC_XML_DTYPE_SCHEMA,
    EC_XML_NAME,
    EC_XML_NETWORK_ID,
    EC_XML_STATON_SOURCE,
    EC_XML_RENAME_DICT,
    EC_XML_MIN_RATIO,
    STR_DIRECTION_TO_DEGREES
)
from etl_pipelines.utils.functions import setup_logging
import polars as pl
import xmltodict

logger = setup_logging()

class EcXmlPipeline(StationObservationPipeline):
    def __init__(self, db_conn=None, date_now=None):
        super().__init__(
            name=EC_XML_NAME,
            source_url=[],
            destination_tables=EC_XML_DESTINATION_TABLES,
            days=3,
            station_source=EC_XML_STATON_SOURCE,
            expected_dtype=EC_XML_DTYPE_SCHEMA,
            column_rename_dict=EC_XML_RENAME_DICT,
            go_through_all_stations=True,
            overrideable_dtype=True,
            network_ids= EC_XML_NETWORK_ID,
            min_ratio=EC_XML_MIN_RATIO,
            db_conn=db_conn,
            date_now=date_now
        )

        ## Add Implementation Specific attributes below
        date_list = [self.date_now.subtract(days=x).start_of("day") for x in reversed(range(1, self.days))]
        self.source_url = {date.strftime("%Y%m%d"): EC_XML_BASE_URL.format(date.strftime("%Y%m%d"), date.strftime("%Y%m%d")) for date in date_list}

    def transform_data(self):
        """
        Implementation of the transform_data method for the class EcXmlPipeline. This method will transform the downloaded data from the Environment and Climate Change Canada website into a format that is ready to be inserted into the database. The main transformation happening here will be the following:
            - Rename Columns
            - Unpivot the data
            - Remove rows with null values
            - Convert datestamp column from string to datetime
            - Convert direction from string to degrees
            - Assign proper variable_id's to the values
            - Join downloaded data with the station list
            - Filter data into different tables

        Args:
            None

        Output:
            None
        """
        logger.info(f"Transforming downloaded data for {self.name}")

        downloaded_data = self.get_downloaded_data()

        if not downloaded_data:
            logger.error(f"No data was downloaded for {self.name}! The attribute __downloaded_data is empty. Exiting")
            raise RuntimeError(f"No data was downloaded for {self.name}! The attribute __downloaded_data is empty. Exiting")

        # TODO: Check for new stations, and insert them into the database if they are new, along with their metadata. Send Email after completion.

        logger.debug(f"Starting Transformation")

        df = downloaded_data["station_data"]

        try:
            df = (
                df
                .rename(self.column_rename_dict)
                .unpivot(index=[
                    "station_name",
                    "latitude",
                    "longitude",
                    "transport_canada_id",
                    "obs_date_utc",
                    "datestamp",
                    "original_id",
                    "wmo_stn_num"
                ])
                # Not really sure what this "Trace" is about. But I haven't encountered it in the data anywhere. Going to keep it from the old scraper
                .remove(pl.col("value").is_null() | (pl.col("value") == pl.lit("Trace")))
                .with_columns(
                    datestamp = (
                        # Remove PST/PDT from datestamp string and convert to datetime obj
                        pl.col("datestamp")
                        .str.slice(offset=0, length=19)
                        .str.to_datetime("%Y-%m-%dT%H:%M:%S", time_zone="America/Vancouver")
                    ),
                    value = (
                        # Convert direction from string to degrees. Cast all value to float since direction has been changed to floats as well
                        pl.col("value")
                        .replace_strict(STR_DIRECTION_TO_DEGREES, default=pl.col("value"))
                        .cast(pl.Float64)
                    ),
                    qa_id = 0,
                    # Assign proper variable_id's to the values
                    variable_id = (pl
                        .when(pl.col("variable") == pl.lit("snow_amt")).then(4)
                        .when(pl.col("variable") == pl.lit("air_temp_yesterday_high")).then(6)
                        .when(pl.col("variable") == pl.lit("air_temp_yesterday_low")).then(8)
                        .when(pl.col("variable") == pl.lit("wind_spd")).then(9)
                        .when(pl.col("variable") == pl.lit("wind_dir")).then(11)
                        .when(pl.col("variable") == pl.lit("total_precip")).then(27)
                        .when(pl.col("variable") == pl.lit("rain_amnt")).then(29)
                        .otherwise(None)
                    )
                )
                .join(self.station_list, on="original_id", how="inner")
                .select(
                    "station_id",
                    "variable_id",
                    "qa_id",
                    "value",
                    "datestamp"
                )
            ).collect()

        except Exception as e:
            logger.error(f"Error when trying to transform the data for {self.name}. Error: {e}", exc_info=True)
            raise RuntimeError(f"Error when trying to transform the data for {self.name}. Error: {e}")

        precip_df = (
            df
            .filter(pl.col("variable_id").is_in([27, 29]))
        )

        temperature_df = pl.concat([
            df.filter(pl.col("variable_id").is_in([6, 8])),
            df
                .filter(pl.col("variable_id").is_in([6, 8]))
                .drop("variable_id")
                .group_by(["station_id", "datestamp", "qa_id"]).mean()
                .with_columns(
                    variable_id = 7
                )
                .select(
                    "station_id",
                    "variable_id",
                    "qa_id",
                    "value",
                    "datestamp"
                )
        ])

        snow_df = (
            df
            .filter(pl.col("variable_id") == 4)
        )

        wind_df = (
            df
            .filter(pl.col("variable_id").is_in([9, 11]))
        )

        self._EtlPipeline__transformed_data = {
            "station_data": {"df": pl.concat([precip_df, temperature_df, snow_df, wind_df]), "pkey": ["station_id", "datestamp", "variable_id"], "truncate": False},
        }

        logger.info(f"Finished Transforming data for {self.name}")

    def get_and_insert_new_stations(self, station_data=None):
        pass

    def _StationObservationPipeline__make_polars_lazyframe(sefl, response, key=None):
        """
        Unfortunately Polars does not have a easy way of converting from XML string to polars. So this function takes an XML file from the source_url and converts it to a polars dataframe.

        The package xmltodict converts a XML string to a nested Python dictionary. The dictionary is unnested by hard coding it's keys. This should be a fine solution since the old scrapers have the keys also hard coded, and it has not ran into any issues as of yet.

        Args:
            response (string): XML string that came from the response of the Get request to the source_url.

        Output:
            station_data_in_dict (polars.LazyFrame): A polars LazyFrame object with all the stations and it's corresponding data from the XML.
        """
        logger.info("Decoding XML data")

        # Convert XML string to dictionary, a small amount of unnesting happens here since all data is located within these two dicts.
        xml_dict = xmltodict.parse(response.text)["om:ObservationCollection"]["om:member"]

        # List to store the joined station data and climate data.
        station_data_in_dict = []

        # Ignoring the first dictionary since it contains metadata about the data source (ie. Who it's from, when the file was created, etc)
        for member in xml_dict[1:]:
            # Convert the nested station dictionary to a Polars LazyFrame. The LazyFrame is transposed so that the data for each station is in a row and not a column.
            station = (
                pl.DataFrame(member["om:Observation"]["om:metadata"]["set"]["identification-elements"]["element"])
                .drop("@name", "@uom")
                .transpose(
                    include_header=False,
                    column_names=[
                        "station_name",
                        "latitude",
                        "longitude",
                        "transport_canada_id",
                        "obs_date_utc",
                        "obs_date_local",
                        "climate_stn_num",
                        "wmo_stn_num"
                    ]
                )
            ).lazy()

            # Convert the nested climate data dictionary to a Polars LazyFrame. Similar to before, transpose is used to turn columnar data to rowwise data. Also nodata values were empty strings, so convert them to Null values.
            data = (
                pl.DataFrame(
                    member["om:Observation"]["om:result"]["elements"]["element"]
                )
                .drop("@name", "@uom")
                .with_columns(
                    pl.when(pl.col("@value").str.len_chars() == 0).then(None).otherwise(pl.col("@value")).name.keep()
                ).transpose(
                    include_header=False,
                    column_names=[
                        "air_temp_yesterday_high",
                        "air_temp_yesterday_low",
                        "total_precip",
                        "rain_amnt",
                        "snow_amnt",
                        "wind_spd",
                        "wind_dir"
                    ]
                )
            ).lazy()

            # Append to final list.
            station_data_in_dict.append(station.join(data, how="cross"))

        logger.info("Finished decoding and converting XML data into polars LazyFrame.")

        # Concat all the lazyframes together before returning the result.
        return pl.concat(station_data_in_dict)
