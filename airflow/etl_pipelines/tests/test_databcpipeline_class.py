from etl_pipelines.tests.test_utils.DataBcPipeline_object import TestDataBcPipeline
from etl_pipelines.utils.constants import EXPECTED_UNITS
import polars as pl
import polars.testing as plt
import pytest
import geopandas as gpd
from shapely.geometry import Point, Polygon
from unittest.mock import MagicMock, patch

def test_databcpipeline_init_defaults():
    pipeline = TestDataBcPipeline(None, {})
    assert pipeline.name is None
    assert pipeline.source_url is None
    assert pipeline.destination_tables == {}
    assert pipeline.expected_dtype is None
    assert pipeline.db_conn is None
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}

def test_databcpipeline_init_custom_values():
    name = "test"
    source_url = "http://example.com"
    destination_tables = {"table1": "dest_table"}
    expected_dtype = {"table1": {"col1": "str"}}
    databc_layer_name = "test_layer"
    db_conn = MagicMock()
    pipeline = TestDataBcPipeline(
        name,
        destination_tables,
        url = source_url,
        databc_layer_name = databc_layer_name,
        expected_dtype = expected_dtype,
        db_conn = db_conn
    )
    assert pipeline.name == name
    assert pipeline.source_url == source_url
    assert pipeline.destination_tables == destination_tables
    assert pipeline.expected_dtype == expected_dtype
    assert pipeline.db_conn == db_conn
    assert pipeline.databc_layer_name == databc_layer_name
    assert pipeline._EtlPipeline__download_num_retries == 0
    assert pipeline._EtlPipeline__downloaded_data == {}
    assert pipeline._EtlPipeline__transformed_data == {}

def test_download_data_live():
    # Below is a simple test to check that the download_data method works correctly. It will try to download the airport layer from DataBC (the same one databc uses in their test suite) essentially it is just testing that the bcdata package is working correctly.
    # This test may fail if the DataBC link format changes or if there are network issues. Please first try updating DataBC to its latest version. If this becomes a problem because the datasource changes often or the required internet remove this test.
    # Note: The expected_dtype below is based on the schema of the airport layer as of Aug 2025. If the schema changes in the future, this will need to be updated accordingly.
    airport_layer_name = 'WHSE_IMAGERY_AND_BASE_MAPS.GSR_AIRPORTS_SVW'
    expected_dtype = {
        airport_layer_name: {
            'geometry': pl.Binary,
            'CUSTODIAN_ORG_DESCRIPTION':pl.String,
            'BUSINESS_CATEGORY_CLASS':pl.String,
            'BUSINESS_CATEGORY_DESCRIPTION':pl.String,
            'OCCUPANT_TYPE_DESCRIPTION':pl.String,
            'SOURCE_DATA_ID': pl.String,
            'SUPPLIED_SOURCE_ID_IND': pl.String,
            'AIRPORT_NAME': pl.String,
            'DESCRIPTION':pl.String,
            'PHYSICAL_ADDRESS': pl.String,
            'ALIAS_ADDRESS':pl.String,
            'STREET_ADDRESS': pl.String,
            'POSTAL_CODE':pl.String,
            'LOCALITY': pl.String,
            'CONTACT_PHONE':pl.String,
            'CONTACT_EMAIL':pl.String,
            'CONTACT_FAX':pl.String,
            'WEBSITE_URL':pl.String,
            'IMAGE_URL':pl.String,
            'LATITUDE':pl.Float64,
            'LONGITUDE': pl.Float64,
            'KEYWORDS': pl.String,
            'DATE_UPDATED': pl.String,
            'SITE_GEOCODED_IND':pl.String,
            'AERODROME_STATUS': pl.String,
            'AIRCRAFT_ACCESS_IND':pl.String,
            'DATA_SOURCE':pl.String,
            'DATA_SOURCE_YEAR': pl.String,
            'ELEVATION': pl.Float64,
            'FUEL_AVAILABILITY_IND':pl.String,
            'HELICOPTER_ACCESS_IND':pl.String,
            'IATA_CODE':pl.String,
            'ICAO_CODE':pl.String,
            'MAX_RUNWAY_LENGTH': pl.Float64,
            'NUMBER_OF_RUNWAYS': pl.Int64,
            'OIL_AVAILABILITY_IND': pl.String,
            'RUNWAY_SURFACE': pl.String,
            'SEAPLANE_ACCESS_IND':pl.String,
            'TC_LID_CODE':pl.String,
            'SEQUENCE_ID': pl.Int64,
            'SE_ANNO_CAD_DATA': pl.String
        }
    }

    pipeline = TestDataBcPipeline('Test bc-airport pipeline', {}, databc_layer_name = airport_layer_name, expected_dtype=expected_dtype)
    assert pipeline.download_data() is None
    assert pipeline._EtlPipeline__downloaded_data[airport_layer_name] is not None

@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.bcdata.get_data")
def test_mocked_download_data(get_data_mock):
    # Mock databc returning this simple geo data frame
    get_data_mock.return_value = gpd.GeoDataFrame({'col1': ['name1', 'name2'], 'geometry': [Point(1, 2), Point(2, 1)]}, crs="EPSG:4326")

    databc_layer_name = 'test_layer'
    pipeline = TestDataBcPipeline(None, {}, databc_layer_name = databc_layer_name, expected_dtype={databc_layer_name: {'col1': pl.String}})

    assert pipeline.download_data() is None
    pipeline._EtlPipeline__downloaded_data[databc_layer_name] = pipeline._EtlPipeline__downloaded_data[databc_layer_name].with_columns(
        geometry = pl.col('geometry').st.to_wkt()
    )
    # Validate data is not transformed by download function but is successfully loaded into the correct location, ultimately not a lot to test in the 'happy case'
    plt.assert_frame_equal(pipeline._EtlPipeline__downloaded_data[databc_layer_name],
                           pl.LazyFrame({
                               'col1': ['name1', 'name2'],
                               'geometry': ['POINT (1 2)', 'POINT (2 1)']
                           }))

import pytest
import polars as pl
from unittest.mock import MagicMock, patch

@pytest.mark.parametrize("truncate", [
    (True),
    (False),
])
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.execute_values")
def test__load_data_into_tables(mock_execute_values, truncate):
    fake_cursor = MagicMock()
    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor

    # Minimal polars DataFrame
    df = pl.DataFrame({
        "id": [1, 2],
        "name": ["Alice", "Bob"]
    })

    databc_layer_name = 'test_layer'
    pipeline = TestDataBcPipeline(
        None, {},
        databc_layer_name=databc_layer_name,
        expected_dtype={databc_layer_name: {'id': pl.Int64, 'name': pl.String}}
    )
    pipeline.db_conn = fake_conn

    pipeline._load_data_into_tables(
        insert_tablename="test_table",
        data=df,
        pkey=["id"],
        truncate=truncate
    )

    if truncate:
        fake_cursor.execute.assert_any_call("TRUNCATE TABLE test_table;")
    else:
        fake_cursor.execute.assert_not_called()

    expected_query = (
        "INSERT INTO test_table (id, name) VALUES %s "
        "ON CONFLICT (id) DO NOTHING;"
    )

    mock_execute_values.assert_called_once_with(
        fake_cursor,
        expected_query,
        [(1, "Alice"), (2, "Bob")],
        page_size=100000
    )

    fake_conn.commit.assert_called_once()
    fake_cursor.close.assert_called_once()

@pytest.mark.parametrize("has_geom", [
    (False),
    (True),
])
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.pl.read_database")
def test_get_whole_table(mock_read_database, has_geom):
    # Arrange
    fake_lazyframe = MagicMock()
    fake_df = MagicMock()
    fake_df.lazy.return_value = fake_lazyframe
    mock_read_database.return_value = fake_df

    databc_layer_name = 'test_layer'
    pipeline = TestDataBcPipeline(None, {}, databc_layer_name = databc_layer_name, expected_dtype={databc_layer_name: {'id': pl.Int64, 'name': pl.String}})
    pipeline.db_conn = MagicMock()

    result = pipeline.get_whole_table("my_table", has_geom=has_geom)

    assert result == fake_lazyframe

    # Assert read_database was called with expected SQL
    mock_read_database.assert_called_once()
    query = mock_read_database.call_args.kwargs["query"]

    if has_geom:
        assert "ST_AsGeoJSON" in query
    else:
        assert "ST_AsGeoJSON" not in query

    assert "my_table" in query
    assert mock_read_database.call_args.kwargs["connection"] == pipeline.db_conn
    assert mock_read_database.call_args.kwargs["infer_schema_length"] is None

def test_update_import_date_success():
    # Arrange
    fake_cursor = MagicMock()
    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor

    databc_layer_name = 'test_layer'
    pipeline = TestDataBcPipeline(None, {}, databc_layer_name = databc_layer_name, expected_dtype={databc_layer_name: {'id': pl.Int64, 'name': pl.String}})

    pipeline.db_conn = fake_conn

    pipeline.update_import_date("test_dataset")

    fake_conn.cursor.assert_called_once()
    fake_cursor.execute.assert_called_once()
    query_arg = fake_cursor.execute.call_args[0][0]
    assert "UPDATE" in query_arg
    assert "test_dataset" in query_arg
    fake_conn.commit.assert_called_once()
    fake_cursor.close.assert_called_once()

@pytest.mark.parametrize("units_list, expect_warning", [
    (["m3/year", "m3/day"], False),             # all expected
    (["Total Flow", "Foo"], True),              # one unexpected
    (["Foo", "Bar"], True),                     # all unexpected
])
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.logger") # patch logger to capture calls
def test_check_for_new_units(mock_logger, units_list, expect_warning):
    # Arrange
    df = pl.DataFrame({"units": units_list})

    databc_layer_name = 'test_layer'
    pipeline = TestDataBcPipeline('TestScraper', {}, databc_layer_name = databc_layer_name, expected_dtype={databc_layer_name: {'id': pl.Int64, 'name': pl.String}})

    pipeline._check_for_new_units(df)

    if expect_warning:
        mock_logger.warning.assert_called_once()
        msg = mock_logger.warning.call_args[0][0]
        for u in units_list:
            if u not in EXPECTED_UNITS:
                assert u in msg  # unexpected unit appears in warning
        assert "TestScraper" in msg # scraper name appears in warning
    else:
        mock_logger.warning.assert_not_called()


@pytest.mark.parametrize(
    "wrap_date, wrlp_date, df_shape, expect_exception, expect_warning, expect_final",
    [
        # mismatched dates raises ValueError
        ("2025-01-01", "2025-01-02", (30000, 5), ValueError, False, False),
        # empty df raises ValueError
        ("2025-01-01", "2025-01-01", (0, 5), ValueError, False, False),
        # df is too small, should warn
        ("2025-01-01", "2025-01-01", (20000, 5), None, True, False),
        # good case
        ("2025-01-01", "2025-01-01", (50000, 5), None, False, True),
    ]
)
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.gpd.read_postgis")
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.st.from_geopandas")
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.logger")
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.pl.concat")
@patch.object(TestDataBcPipeline, "_check_for_new_units")
@patch.object(TestDataBcPipeline, "get_whole_table")
def test_mocked__transform_bc_wls_wrl_wra_data(
    mock_get_whole_table,
    mock_check_units,
    mock_concat,
    mock_logger,
    mock_from_geopandas,
    mock_read_postgis,
    wrap_date, wrlp_date, df_shape,
    expect_exception, expect_warning, expect_final
):
    # Heavily mocked test that tests the flow of the code ie: when it errors and when it warns. The actual polars logic is tested in the next test
    databc_layer_name = 'test_layer'
    pipeline = TestDataBcPipeline(None, {}, databc_layer_name = databc_layer_name, expected_dtype={databc_layer_name: {'id': pl.Int64, 'name': pl.String}})
    pipeline.date_now = MagicMock()
    pipeline.date_now.date.return_value = "2025-01-01"
    pipeline._EtlPipeline__transformed_data = {}
    mock_check_units.return_value = None
    mock_read_postgis.return_value = None

    df_result = pl.DataFrame({"wls_wrl_wra_id": list(range(df_shape[0])), "qty_units": list(range(df_shape[0]))})
    bc_concat_mock = MagicMock()
    bc_concat_mock.is_empty.return_value = df_shape[0] == 0
    bc_concat_mock.shape = df_shape
    bc_concat_mock.join_where.return_value = bc_concat_mock
    bc_concat_mock.with_columns.return_value = bc_concat_mock
    bc_concat_mock.drop.return_value = bc_concat_mock
    bc_concat_mock.select.return_value = bc_concat_mock
    bc_concat_mock.collect.return_value = df_result

    mock_concat.return_value = bc_concat_mock

    def get_whole_table_side_effect(table_name, has_geom):
        import_date_df = pl.LazyFrame({
            "dataset": ["water_rights_applications_public", "water_rights_licences_public"],
            "import_date": [wrap_date, wrlp_date]
        })

        if table_name == "bc_data_import_date":
            return import_date_df
        elif table_name == "bc_water_rights_applications_public":
            return MagicMock()
        elif table_name == "bc_water_rights_licences_public":
            return MagicMock()

    mock_get_whole_table.side_effect = get_whole_table_side_effect

    mock_lazy_polygon = MagicMock()
    mock_from_geopandas.return_value.lazy.return_value = mock_lazy_polygon

    if expect_exception:
        with pytest.raises(expect_exception):
            pipeline.transform_bc_wls_wrl_wra_data()
    else:
        pipeline.transform_bc_wls_wrl_wra_data()

    if expect_warning:
        mock_logger.warning.assert_called()
        assert "__transformed_data" not in pipeline._EtlPipeline__transformed_data
    elif expect_final:
        # expecting the final table data to be loaded in the correct spots
        assert "final_table" in pipeline._EtlPipeline__transformed_data
        plt.assert_frame_equal(pipeline._EtlPipeline__transformed_data["final_table"]["df"], df_result)
        assert pipeline._EtlPipeline__transformed_data["final_table"]["truncate"] is True
    elif expect_exception:
        # Exceptions are already asserted in the context manager above
        pass


def generate_mock_applications_public(num_rows):

    return pl.LazyFrame({
        "wrap_id": pl.Series("wrap_id", range(1, num_rows + 1), dtype=pl.Int64),
        "geojson": pl.Series("geojson", ['{"type": "Point", "coordinates": [0, 0]}'] * num_rows, dtype=pl.Utf8),

        "licence_no": pl.Series("licence_no", [None] * num_rows, dtype=pl.Utf8),
        "tpod_tag": pl.Series("tpod_tag", [None] * num_rows, dtype=pl.Utf8),
        "purpose": pl.Series("purpose", [None] * num_rows, dtype=pl.Utf8),
        "licensee": pl.Series("licensee", [None] * num_rows, dtype=pl.Utf8),
        "longitude": pl.Series("longitude", [None] * num_rows, dtype=pl.Float64),
        "latitude": pl.Series("latitude", [None] * num_rows, dtype=pl.Float64),
        "lic_status": pl.Series("lic_status", [None] * num_rows, dtype=pl.Utf8),
        "file_no": pl.Series("file_no", [None] * num_rows, dtype=pl.Utf8),
        "water_allocation_type": pl.Series("water_allocation_type", [None] * num_rows, dtype=pl.Utf8),
        "pod_diversion_type": pl.Series("pod_diversion_type", [None] * num_rows, dtype=pl.Utf8),
        "well_tag_number": pl.Series("well_tag_number", [None] * num_rows, dtype=pl.Utf8),
        "industry_activity": pl.Series("industry_activity", [None] * num_rows, dtype=pl.Utf8),
        "purpose_groups": pl.Series("purpose_groups", [None] * num_rows, dtype=pl.Utf8),
        "is_consumptive": pl.Series("is_consumptive", [None] * num_rows, dtype=pl.Boolean),
        "qty_units_diversion_max_rate": pl.Series("qty_units_diversion_max_rate", [None] * num_rows, dtype=pl.Utf8),
        "puc_groupings_storage": pl.Series("puc_groupings_storage", [None] * num_rows, dtype=pl.Utf8),
        "qty_diversion_max_rate": pl.Series("qty_diversion_max_rate", [None] * num_rows, dtype=pl.Float64),

    })


def generate_mock_licences_public(num_rows, lat, lon):

    return pl.LazyFrame({
        "wrlp_id": pl.Series("wrlp_id", range(num_rows + 1, num_rows * 2 + 1), dtype=pl.Int64),
        "geojson": pl.Series(
            "geojson",
            [f'{{"type": "Point", "coordinates": [{lon}, {lat}]}}'] * num_rows,
            dtype=pl.Utf8
        ),
        "qty_diversion_max_rate": pl.Series("qty_diversion_max_rate", [100.0] * num_rows, dtype=pl.Float64),

        "licence_no": pl.Series("licence_no", [None] * num_rows, dtype=pl.Utf8),
        "tpod_tag": pl.Series("tpod_tag", [None] * num_rows, dtype=pl.Utf8),
        "purpose": pl.Series("purpose", [None] * num_rows, dtype=pl.Utf8),
        "pcl_no": pl.Series("pcl_no", [None] * num_rows, dtype=pl.Utf8),
        "qty_original": pl.Series("qty_original", [None] * num_rows, dtype=pl.Float64),
        "qty_flag": pl.Series("qty_flag", [None] * num_rows, dtype=pl.Utf8),
        "qty_units": pl.Series("qty_units", [None] * num_rows, dtype=pl.Utf8),
        "licensee": pl.Series("licensee", [None] * num_rows, dtype=pl.Utf8),
        "lic_status_date": pl.Series("lic_status_date", [None] * num_rows, dtype=pl.Date),
        "priority_date": pl.Series("priority_date", [None] * num_rows, dtype=pl.Date),
        "expiry_date": pl.Series("expiry_date", [None] * num_rows, dtype=pl.Date),
        "longitude": pl.Series("longitude", [None] * num_rows, dtype=pl.Float64),
        "latitude": pl.Series("latitude", [None] * num_rows, dtype=pl.Float64),
        "stream_name": pl.Series("stream_name", [None] * num_rows, dtype=pl.Utf8),
        "quantity_day_m3": pl.Series("quantity_day_m3", [None] * num_rows, dtype=pl.Float64),
        "quantity_sec_m3": pl.Series("quantity_sec_m3", [None] * num_rows, dtype=pl.Float64),
        "quantity_ann_m3": pl.Series("quantity_ann_m3", [None] * num_rows, dtype=pl.Float64),
        "lic_status": pl.Series("lic_status", [None] * num_rows, dtype=pl.Utf8),
        "rediversion_flag": pl.Series("rediversion_flag", [None] * num_rows, dtype=pl.Utf8),
        "flag_desc": pl.Series("flag_desc", [None] * num_rows, dtype=pl.Utf8),
        "file_no": pl.Series("file_no", [None] * num_rows, dtype=pl.Utf8),
        "water_allocation_type": pl.Series("water_allocation_type", [None] * num_rows, dtype=pl.Utf8),
        "pod_diversion_type": pl.Series("pod_diversion_type", [None] * num_rows, dtype=pl.Utf8),
        "water_source_type_desc": pl.Series("water_source_type_desc", [None] * num_rows, dtype=pl.Utf8),
        "hydraulic_connectivity": pl.Series("hydraulic_connectivity", [None] * num_rows, dtype=pl.Utf8),
        "well_tag_number": pl.Series("well_tag_number", [None] * num_rows, dtype=pl.Utf8),
        "related_licences": pl.Series("related_licences", [None] * num_rows, dtype=pl.List(pl.Utf8)),
        "industry_activity": pl.Series("industry_activity", [None] * num_rows, dtype=pl.Utf8),
        "purpose_groups": pl.Series("purpose_groups", [None] * num_rows, dtype=pl.Utf8),
        "is_consumptive": pl.Series("is_consumptive", [None] * num_rows, dtype=pl.Boolean),
        "ann_adjust": pl.Series("ann_adjust", [None] * num_rows, dtype=pl.Float64),
        "qty_units_diversion_max_rate": pl.Series("qty_units_diversion_max_rate", [None] * num_rows, dtype=pl.Utf8),
        "puc_groupings_storage": pl.Series("puc_groupings_storage", [None] * num_rows, dtype=pl.Utf8),
    })


@pytest.mark.parametrize("expect_warning, lat, lon, num_rows, expected_rows", [
    (False, 10, 10, 12505, 12505 * 2),
    (True, 180, 90, 12505, None),
])
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.gpd.read_postgis")
@patch("etl_pipelines.scrapers.DataBcPipeline.DataBcpipeline.logger")
@patch.object(TestDataBcPipeline, "get_whole_table")
def test_polars_transform_bc_wls_wrl_wra_data(
    mock_get_whole_table,
    mock_logger,
    mock_read_postgis,
    expect_warning,
    num_rows,
    lat,
    lon,
    expected_rows
):

    # Mock polygon covering the world (minus a small hole)
    world_coverage_poly = Polygon([
        (-180, -90),
        (-180,  90),
        (179,   89),
        (180,  -90),
        (-180, -90)
    ])
    gdf = gpd.GeoDataFrame(
        {'id': [1], 'geometry': [world_coverage_poly]},
        crs="EPSG:4326"
    ).rename(columns={'geometry': 'poly'})

    # mocking coverage polygon read from database
    mock_read_postgis.return_value = gdf

    # Side effect to return fake data tables
    def get_whole_table_side_effect(table_name, has_geom):
        if table_name == "bc_data_import_date":
            return pl.LazyFrame({
                "dataset": [
                    "water_rights_applications_public",
                    "water_rights_licences_public"
                ],
                "import_date": ['2025-01-01', '2025-01-01']
            })
        elif table_name == "bc_water_rights_applications_public":
            return generate_mock_applications_public(num_rows)
        elif table_name == "bc_water_rights_licences_public":
            return generate_mock_licences_public(num_rows, lat, lon)
    mock_get_whole_table.side_effect = get_whole_table_side_effect

    databc_layer_name = 'test_layer'
    pipeline = TestDataBcPipeline(
        None, {},
        databc_layer_name=databc_layer_name,
        expected_dtype={databc_layer_name: {'id': pl.Int64, 'name': pl.String}}
    )
    pipeline.transform_bc_wls_wrl_wra_data()

    if not expect_warning:
        assert "final_table" in pipeline._EtlPipeline__transformed_data
        df = pipeline._EtlPipeline__transformed_data["final_table"]["df"]
        assert isinstance(df, pl.DataFrame)
        assert df.height == expected_rows
        mock_logger.warning.assert_not_called()
    else:
        assert "final_table" not in pipeline._EtlPipeline__transformed_data
        mock_logger.warning.assert_called()
