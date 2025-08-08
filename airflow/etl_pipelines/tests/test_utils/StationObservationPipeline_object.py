from etl_pipelines.scrapers.StationObservationPipeline.StationObservationPipeline import StationObservationPipeline
import pendulum

"""
The class below is used to test StationObservationPipeline class' concrete methods which are:
    - download_data()
    - get_gauge_list()
So any abstract method will be defined to return None
"""
class TestStationObservationPipeline(StationObservationPipeline):
    __test__= False
    def __init__(
            self,
            name=None,
            source_url=None,
            destination_tables={},
            days=2,
            station_source=None,
            expected_dtype={},
            column_rename_dict={},
            go_through_all_stations=False,
            overrideable_dtype = False,
            network_ids=[],
            min_ratio=0,
            file_encoding="utf8",
            db_conn=None,
            date_now=pendulum.now("UTC")
        ):
        super().__init__(
            name=name,
            source_url=source_url,
            destination_tables=destination_tables,
            days=days,
            station_source=station_source,
            expected_dtype=expected_dtype,
            column_rename_dict=column_rename_dict,
            go_through_all_stations=go_through_all_stations,
            overrideable_dtype = overrideable_dtype,
            network_ids=network_ids,
            min_ratio=min_ratio,
            file_encoding=file_encoding,
            db_conn=db_conn,
            date_now=date_now
        )

    def transform_data(self):
        return None
