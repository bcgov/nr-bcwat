variable_query = '''
    (SELECT
        variable_id,
        standard_name AS variable_name,
        long_name AS variable_description,
        display_name,
        cell_method,
        units AS unit
    FROM (
        SELECT * FROM bcwmd.climate_variables
        UNION
        SELECT * FROM cariboo.climate_variables
        UNION
        SELECT * FROM water.climate_variables
        ) unioned
    ORDER BY variable_id)
    UNION
    (SELECT
        variable_id,
        standard_name AS variable_name,
        long_name AS variable_description,
        display_name,
        cell_method,
        units AS unit
    FROM (
        SELECT
            variable_id,
            display_name,
            NULL AS standard_name,
            cell_method,
            description AS long_name,
            units
        FROM bcwmd.water_variables
        UNION
        SELECT
            variable_id,
            display_name,
            NULL AS standard_name,
            cell_method,
            description AS long_name,
            units
        FROM cariboo.water_variables
        UNION
        SELECT
            variable_id,
            display_name,
            standard_name,
            cell_method,
            long_name,
            units
        FROM water.water_variables
        ) unioned
    WHERE standard_name IS NOT NULL
    ORDER BY variable_id)
    ORDER BY variable_id, variable_name;
'''

network_query = '''
    SELECT
        DISTINCT ON (network_id)
        *
    FROM (
        SELECT * FROM bcwmd.network
        UNION
        SELECT * FROM cariboo.network
        ) unioned
    ORDER BY network_id;
'''

qa_type_query = '''
    SELECT
        qa_id as qa_type_id,
        description AS qa_type_name
    FROM cariboo.qa;
'''

region_query = '''
    SELECT
        1 AS region_id,
        'swp' AS region_name,
        geom AS region_click_studyarea,
        NULL::geometry as region_studyarea_allfunds
    FROM bcwmd.swp_study_area
    UNION
    SELECT
        2 AS region_id,
        'nwp' AS region_name,
        geom AS region_click_studyarea,
        NULL::geometry as region_studyarea_allfunds
    FROM bcwmd.nwp_study_area
    UNION
    SELECT
        3 AS region_id,
        'cariboo' AS region_name,
        geom AS region_click_studyarea,
        ST_Transform(geom3005, 4326) AS region_studyarea_allfunds
    FROM cariboo.cariboo_region
    CROSS JOIN cariboo.studyarea_allfunds
    UNION
    SELECT
        4 AS region_id,
        'kwt' AS region_name,
        ST_Transform(sr.geom4326, 4326) AS region_click_studyarea,
        af.geom4326 AS region_studyarea_allfunds
    FROM kwt.study_region sr
    CROSS JOIN kwt.studyarea_allfunds af
    UNION
    SELECT
        5 AS region_id,
        'nwwt' AS region_name,
        sa.geom4326_simplified AS region_click_studyarea,
        af.geom4326 AS region_studyarea_allfunds
    FROM nwwt.nwwt_click_study_area sa
    CROSS JOIN nwwt.studyarea_allfunds af
    UNION
    SELECT
        6 AS region_id,
        'owt' AS region_name,
        ST_SetSRID(sa.geom, 4326) AS region_click_studyarea,
        af.geom4326 AS region_studyarea_allfunds
    FROM owt.new_study_area_including_skeena sa
    CROSS JOIN owt.studyarea_allfunds af;
'''

operation_type_query = '''
    SELECT
        operation_id,
        operation_code AS operation_name,
        description
    FROM bcwmd.operation;
'''

station_type_query = '''
    SELECT
        type_id,
        code AS type_name,
        description AS type_description
    FROM cariboo.type;
'''

station_status_query = '''
    SELECT * FROM
    (SELECT * FROM bcwmd.status
    UNION
    SELECT * FROM cariboo.status) unioned
    WHERE status_name != 'Current';
'''

project_query = '''
    SELECT
        project_id,
        project_name,
        CASE
            WHEN project_id = 1 THEN (SELECT ST_UNION(geom) FROM wet.nwe_clip)
            WHEN project_id = 4 THEN (SELECT geom FROM wet.cariboo_region)
            ELSE Null
        END AS project_geom4326
    FROM wet.project;
'''

station_query = '''
    SELECT
        native_id AS original_id,
        station_id AS old_station_id,
        network_id,
        type_id,
        station_name,
        stream_name,
        description AS station_description,
        status_id::integer AS station_status_id,
        operation_id,
        longitude,
        latitude,
        geom AS geom4326,
        drainage_area,
        CASE
            WHEN metadata ->> 'elevation' = ''
            THEN NULL
            ELSE (metadata ->> 'elevation')::DOUBLE PRECISION
        END AS elevation,
        CASE
            WHEN scrape IS NOT NULL
            THEN scrape
            ELSE false
        END AS scrape,
        regulated,
        user_flag
    FROM
        wet.stations
    WHERE
        prov_terr_state_loc = 'BC'
    AND
        network_id != 30

    UNION

    SELECT
        CASE
            WHEN import_json IS NOT NULL
                THEN import_json->>'StationId'
            ELSE native_id
        END AS original_id,
        station_id AS old_station_id,
        network_id,
        type_id,
        station_name,
        stream_name,
        description AS station_description,
        status_id::integer AS station_status_id,
        operation_id,
        longitude,
        latitude,
        geom AS geom4326,
        drainage_area,
        CASE
            WHEN metadata ->> 'elevation' = ''
            THEN NULL
            ELSE (metadata ->> 'elevation')::DOUBLE PRECISION
        END AS elevation,
        CASE
            WHEN scrape IS NOT NULL
            THEN scrape
            ELSE false
        END AS scrape,
        regulated,
        user_flag
    FROM
        wet.stations
    WHERE
        prov_terr_state_loc = 'BC'
    AND
        network_id = 30;
'''

station_project_id_query = '''
    SELECT
        station_id AS old_station_id,
        unnest(project_id) AS project_id
    FROM
        wet.stations
    WHERE
        prov_terr_state_loc = 'BC'
    AND
        network_id != 30

    UNION

    SELECT
        station_id AS old_station_id,
        unnest(project_id) AS project_id
    FROM
        wet.stations
    WHERE
        prov_terr_state_loc = 'BC'
    AND
        network_id = 30;
'''

station_region_query = '''
    SELECT
        station_id,
        region_id
    FROM
        bcwat_obs.station
    JOIN
        bcwat_obs.region
    ON
        (ST_Within(geom4326, region_click_studyarea));
'''


water_station_variable_query= '''
    SELECT
        station_id AS old_station_id,
        unnest(var_array) AS variable_id
    FROM
        wet.stations
    WHERE
        prov_terr_state_loc = 'BC'
    AND
        climate_foundry_id IS NULL
    AND
        network_id NOT IN (25, 26, 27, 28, 30, 44, 51, 52)

    UNION

    SELECT
        station_id AS old_station_id,
        unnest(var_array) AS variable_id
    FROM
        wet.stations
    WHERE
        prov_terr_state_loc = 'BC'
    AND
        climate_foundry_id IS NULL
    AND
        network_id = 30;
'''

climate_station_variable_query = '''
    SELECT
        station_id AS old_station_id,
        unnest(var_array) AS variable_id
     FROM
        wet.stations
    WHERE
        prov_terr_state_loc = 'BC'
    AND
        climate_foundry_id IS NOT NULL
    AND
        network_id NOT IN (25, 26, 27, 28, 30, 44, 51, 52)

    UNION

    SELECT
        station_id AS old_station_id,
        unnest(var_array) AS variable_id
    FROM
        wet.stations
    WHERE
        prov_terr_state_loc = 'BC'
    AND
        climate_foundry_id IS NOT NULL
    AND
        network_id = 30;
'''

water_quality_station_parameter_query = """
    SELECT
        station_id AS old_station_id,
        unnest(var_array) AS parameter_id
    FROM
        wet.stations
    WHERE
        prov_terr_state_loc = 'BC'
    AND
        network_id IN (25, 26, 27, 28, 44, 51, 52)
"""

station_year_query = '''
    SELECT
        station_id AS old_station_id,
        unnest(year_array) AS year
    FROM
        wet.stations
    WHERE
        prov_terr_state_loc = 'BC'
    AND
        network_id != 30

    UNION

    SELECT
        station_id AS old_station_id,
        unnest(year_array) AS year
    FROM
        wet.stations
    WHERE
        prov_terr_state_loc = 'BC'
    AND
        network_id = 30;
'''

climate_hourly_realtime = """
    SELECT
        station_id AS old_station_id,
        variable_id,
        datetimestamp,
        val AS value,
        qa_id
    FROM
        (SELECT * FROM wet.climate_realtime_qa
        WHERE station_id IN (
            SELECT station_id
            FROM wet.stations
            WHERE network_id = 20
        )) AS data
    JOIN
        wet.stations
    USING (station_id);
"""

climate_msp_daily = """
    SELECT
        station_id AS old_station_id,
        variable_id,
        survey_period,
        datestamp,
        val AS value,
        code,
        qa_id
    FROM
        wet.climate_msp_daily
    JOIN
        wet.stations
    USING (station_id);
"""

climate_precipitation_realtime = """
    SELECT
        station_id AS old_station_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id
    FROM
        (
            SELECT
                *
            FROM
                wet.climate_daily_qa
            WHERE
                variable_id IN (1, 2, 3, 15, 17)
            AND
                val >= 0
        ) AS precip
    JOIN
        wet.stations
    USING (station_id);
"""

climate_snow_amount = """
    SELECT
        station_id AS old_station_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id
    FROM
        (
            SELECT
                *
            FROM
                wet.climate_daily_qa
            WHERE
                variable_id IN (4)
        ) AS snow
    JOIN
        wet.stations
    USING (station_id);
"""

climate_snow_depth = """
    SELECT
        station_id AS old_station_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id
    FROM
        (
            SELECT
                *
            FROM
                wet.climate_daily_qa
            WHERE
                variable_id IN (5)
            AND
                val >= 0
        ) AS sd
    JOIN
        wet.stations
    USING
        (station_id);
"""

climate_snow_water_equivalent = """
    SELECT
        station_id AS old_station_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id
    FROM
        (
            SELECT
                *
            FROM
                wet.climate_daily_qa
            WHERE
                variable_id IN (16)
        ) AS swe
    JOIN
        wet.stations
    USING (station_id);
"""

climate_temperature = """
    SELECT
        station_id AS old_station_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id
    FROM
        (
            SELECT
                *
            FROM
                wet.climate_daily_qa
            WHERE
                variable_id IN (6, 7, 8, 12)
        ) AS temp
    JOIN
        wet.stations
    USING (station_id);
"""

climate_wind = """
    SELECT
        station_id AS old_station_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id
    FROM
        (
            SELECT
                *
            FROM
                wet.climate_daily_qa
            WHERE
                variable_id IN (9, 10, 11)
        ) AS wind
    JOIN
        wet.stations
    USING (station_id);
"""

flow_metrics_query = """
    WITH a AS (SELECT
        station_id AS old_station_id,
        (SELECT row_to_json(_) FROM
            (SELECT
                ROUND(ipf_200::NUMERIC, 2)::DOUBLE PRECISION AS ipf_200,
                ROUND(ipf_100::NUMERIC, 2)::DOUBLE PRECISION AS ipf_100,
                ROUND(ipf_50::NUMERIC, 2)::DOUBLE PRECISION AS ipf_50,
                ROUND(ipf_25::NUMERIC, 2)::DOUBLE PRECISION AS ipf_25,
                ROUND(ipf_20::NUMERIC, 2)::DOUBLE PRECISION AS ipf_20,
                ROUND(ipf_10::NUMERIC, 2)::DOUBLE PRECISION AS ipf_10,
                ROUND(ipf_5::NUMERIC, 2)::DOUBLE PRECISION AS ipf_5,
                ROUND(ipf_2::NUMERIC, 2)::DOUBLE PRECISION AS ipf_2,
                ROUND(ipf_1::NUMERIC, 2)::DOUBLE PRECISION AS ipf_1,
                ROUND(ipf_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ipf_1_01,
                ROUND(ipf_yr::NUMERIC, 2)::DOUBLE PRECISION AS ipf_yr,
                ROUND(amfh_200::NUMERIC, 2)::DOUBLE PRECISION AS amfh_200,
                ROUND(amfh_100::NUMERIC, 2)::DOUBLE PRECISION AS amfh_100,
                ROUND(amfh_50::NUMERIC, 2)::DOUBLE PRECISION AS amfh_50,
                ROUND(amfh_25::NUMERIC, 2)::DOUBLE PRECISION AS amfh_25,
                ROUND(amfh_20::NUMERIC, 2)::DOUBLE PRECISION AS amfh_20,
                ROUND(amfh_10::NUMERIC, 2)::DOUBLE PRECISION AS amfh_10,
                ROUND(amfh_5::NUMERIC, 2)::DOUBLE PRECISION AS amfh_5,
                ROUND(amfh_2::NUMERIC, 2)::DOUBLE PRECISION AS amfh_2,
                ROUND(amfh_1::NUMERIC, 2)::DOUBLE PRECISION AS amfh_1,
                ROUND(amfh_1_01::NUMERIC, 2)::DOUBLE PRECISION AS amfh_1_01,
                ROUND(amfh_yr::NUMERIC, 2)::DOUBLE PRECISION AS amfh_yr,
                ROUND(amfl_200::NUMERIC, 2)::DOUBLE PRECISION AS amfl_200,
                ROUND(amfl_100::NUMERIC, 2)::DOUBLE PRECISION AS amfl_100,
                ROUND(amfl_50::NUMERIC, 2)::DOUBLE PRECISION AS amfl_50,
                ROUND(amfl_25::NUMERIC, 2)::DOUBLE PRECISION AS amfl_25,
                ROUND(amfl_20::NUMERIC, 2)::DOUBLE PRECISION AS amfl_20,
                ROUND(amfl_10::NUMERIC, 2)::DOUBLE PRECISION AS amfl_10,
                ROUND(amfl_5::NUMERIC, 2)::DOUBLE PRECISION AS amfl_5,
                ROUND(amfl_2::NUMERIC, 2)::DOUBLE PRECISION AS amfl_2,
                ROUND(amfl_1::NUMERIC, 2)::DOUBLE PRECISION AS amfl_1,
                ROUND(amfl_1_01::NUMERIC, 2)::DOUBLE PRECISION AS amfl_1_01,
                ROUND(amfl_yr::NUMERIC, 2)::DOUBLE PRECISION AS amfl_yr,
                ROUND(js_7df_200::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_200,
                ROUND(js_7df_100::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_100,
                ROUND(js_7df_50::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_50,
                ROUND(js_7df_25::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_25,
                ROUND(js_7df_20::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_20,
                ROUND(js_7df_10::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_10,
                ROUND(js_7df_5::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_5,
                ROUND(js_7df_2::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_2,
                ROUND(js_7df_1::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_1,
                ROUND(js_7df_1_01::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_1_01,
                ROUND(js_7df_yr::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_yr,
                ROUND(ann_7df_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_200,
                ROUND(ann_7df_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_100,
                ROUND(ann_7df_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_50,
                ROUND(ann_7df_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_25,
                ROUND(ann_7df_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_20,
                ROUND(ann_7df_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_10,
                ROUND(ann_7df_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_5,
                ROUND(ann_7df_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_2,
                ROUND(ann_7df_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_1,
                ROUND(ann_7df_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_1_01,
                ROUND(ann_7df_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr
            ) AS _
        ) AS station_flow_metric
    FROM bcwmd.flow_metrics
    JOIN bcwmd.stations
    USING (station_id)
    UNION ALL
    SELECT
        station_id AS old_station_id,
        (SELECT row_to_json(_) FROM
            (SELECT
                ROUND(ipf_200::NUMERIC, 2)::DOUBLE PRECISION AS ipf_200,
                ROUND(ipf_100::NUMERIC, 2)::DOUBLE PRECISION AS ipf_100,
                ROUND(ipf_50::NUMERIC, 2)::DOUBLE PRECISION AS ipf_50,
                ROUND(ipf_25::NUMERIC, 2)::DOUBLE PRECISION AS ipf_25,
                ROUND(ipf_20::NUMERIC, 2)::DOUBLE PRECISION AS ipf_20,
                ROUND(ipf_10::NUMERIC, 2)::DOUBLE PRECISION AS ipf_10,
                ROUND(ipf_5::NUMERIC, 2)::DOUBLE PRECISION AS ipf_5,
                ROUND(ipf_2::NUMERIC, 2)::DOUBLE PRECISION AS ipf_2,
                ROUND(ipf_1::NUMERIC, 2)::DOUBLE PRECISION AS ipf_1,
                ROUND(ipf_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ipf_1_01,
                ROUND(ipf_yr::NUMERIC, 2)::DOUBLE PRECISION AS ipf_yr,
                ROUND(amfh_200::NUMERIC, 2)::DOUBLE PRECISION AS amfh_200,
                ROUND(amfh_100::NUMERIC, 2)::DOUBLE PRECISION AS amfh_100,
                ROUND(amfh_50::NUMERIC, 2)::DOUBLE PRECISION AS amfh_50,
                ROUND(amfh_25::NUMERIC, 2)::DOUBLE PRECISION AS amfh_25,
                ROUND(amfh_20::NUMERIC, 2)::DOUBLE PRECISION AS amfh_20,
                ROUND(amfh_10::NUMERIC, 2)::DOUBLE PRECISION AS amfh_10,
                ROUND(amfh_5::NUMERIC, 2)::DOUBLE PRECISION AS amfh_5,
                ROUND(amfh_2::NUMERIC, 2)::DOUBLE PRECISION AS amfh_2,
                ROUND(amfh_1::NUMERIC, 2)::DOUBLE PRECISION AS amfh_1,
                ROUND(amfh_1_01::NUMERIC, 2)::DOUBLE PRECISION AS amfh_1_01,
                ROUND(amfh_yr::NUMERIC, 2)::DOUBLE PRECISION AS amfh_yr,
                ROUND(amfl_200::NUMERIC, 2)::DOUBLE PRECISION AS amfl_200,
                ROUND(amfl_100::NUMERIC, 2)::DOUBLE PRECISION AS amfl_100,
                ROUND(amfl_50::NUMERIC, 2)::DOUBLE PRECISION AS amfl_50,
                ROUND(amfl_25::NUMERIC, 2)::DOUBLE PRECISION AS amfl_25,
                ROUND(amfl_20::NUMERIC, 2)::DOUBLE PRECISION AS amfl_20,
                ROUND(amfl_10::NUMERIC, 2)::DOUBLE PRECISION AS amfl_10,
                ROUND(amfl_5::NUMERIC, 2)::DOUBLE PRECISION AS amfl_5,
                ROUND(amfl_2::NUMERIC, 2)::DOUBLE PRECISION AS amfl_2,
                ROUND(amfl_1::NUMERIC, 2)::DOUBLE PRECISION AS amfl_1,
                ROUND(amfl_1_01::NUMERIC, 2)::DOUBLE PRECISION AS amfl_1_01,
                ROUND(amfl_yr::NUMERIC, 2)::DOUBLE PRECISION AS amfl_yr,
                ROUND(js_7df_200::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_200,
                ROUND(js_7df_100::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_100,
                ROUND(js_7df_50::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_50,
                ROUND(js_7df_25::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_25,
                ROUND(js_7df_20::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_20,
                ROUND(js_7df_10::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_10,
                ROUND(js_7df_5::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_5,
                ROUND(js_7df_2::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_2,
                ROUND(js_7df_1::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_1,
                ROUND(js_7df_1_01::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_1_01,
                ROUND(js_7df_yr::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_yr,
                ROUND(ann_7df_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_200,
                ROUND(ann_7df_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_100,
                ROUND(ann_7df_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_50,
                ROUND(ann_7df_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_25,
                ROUND(ann_7df_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_20,
                ROUND(ann_7df_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_10,
                ROUND(ann_7df_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_5,
                ROUND(ann_7df_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_2,
                ROUND(ann_7df_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_1,
                ROUND(ann_7df_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_1_01,
                ROUND(ann_7df_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr
            ) AS _
        ) AS station_flow_metric
    FROM water.flow_metrics
    JOIN water.nwp_stations
    USING (foundry_id)
    UNION ALL
    SELECT
        station_id AS old_station_id,
        (SELECT row_to_json(_) FROM
            (SELECT
                ROUND(ipf_200::NUMERIC, 2)::DOUBLE PRECISION AS ipf_200,
                ROUND(ipf_100::NUMERIC, 2)::DOUBLE PRECISION AS ipf_100,
                ROUND(ipf_50::NUMERIC, 2)::DOUBLE PRECISION AS ipf_50,
                ROUND(ipf_25::NUMERIC, 2)::DOUBLE PRECISION AS ipf_25,
                ROUND(ipf_20::NUMERIC, 2)::DOUBLE PRECISION AS ipf_20,
                ROUND(ipf_10::NUMERIC, 2)::DOUBLE PRECISION AS ipf_10,
                ROUND(ipf_5::NUMERIC, 2)::DOUBLE PRECISION AS ipf_5,
                ROUND(ipf_2::NUMERIC, 2)::DOUBLE PRECISION AS ipf_2,
                ROUND(ipf_1::NUMERIC, 2)::DOUBLE PRECISION AS ipf_1,
                ROUND(ipf_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ipf_1_01,
                ROUND(ipf_yr::NUMERIC, 2)::DOUBLE PRECISION AS ipf_yr,
                ROUND(amfh_200::NUMERIC, 2)::DOUBLE PRECISION AS amfh_200,
                ROUND(amfh_100::NUMERIC, 2)::DOUBLE PRECISION AS amfh_100,
                ROUND(amfh_50::NUMERIC, 2)::DOUBLE PRECISION AS amfh_50,
                ROUND(amfh_25::NUMERIC, 2)::DOUBLE PRECISION AS amfh_25,
                ROUND(amfh_20::NUMERIC, 2)::DOUBLE PRECISION AS amfh_20,
                ROUND(amfh_10::NUMERIC, 2)::DOUBLE PRECISION AS amfh_10,
                ROUND(amfh_5::NUMERIC, 2)::DOUBLE PRECISION AS amfh_5,
                ROUND(amfh_2::NUMERIC, 2)::DOUBLE PRECISION AS amfh_2,
                ROUND(amfh_1::NUMERIC, 2)::DOUBLE PRECISION AS amfh_1,
                ROUND(amfh_1_01::NUMERIC, 2)::DOUBLE PRECISION AS amfh_1_01,
                ROUND(amfh_yr::NUMERIC, 2)::DOUBLE PRECISION AS amfh_yr,
                ROUND(amfl_200::NUMERIC, 2)::DOUBLE PRECISION AS amfl_200,
                ROUND(amfl_100::NUMERIC, 2)::DOUBLE PRECISION AS amfl_100,
                ROUND(amfl_50::NUMERIC, 2)::DOUBLE PRECISION AS amfl_50,
                ROUND(amfl_25::NUMERIC, 2)::DOUBLE PRECISION AS amfl_25,
                ROUND(amfl_20::NUMERIC, 2)::DOUBLE PRECISION AS amfl_20,
                ROUND(amfl_10::NUMERIC, 2)::DOUBLE PRECISION AS amfl_10,
                ROUND(amfl_5::NUMERIC, 2)::DOUBLE PRECISION AS amfl_5,
                ROUND(amfl_2::NUMERIC, 2)::DOUBLE PRECISION AS amfl_2,
                ROUND(amfl_1::NUMERIC, 2)::DOUBLE PRECISION AS amfl_1,
                ROUND(amfl_1_01::NUMERIC, 2)::DOUBLE PRECISION AS amfl_1_01,
                ROUND(amfl_yr::NUMERIC, 2)::DOUBLE PRECISION AS amfl_yr,
                ROUND(js_7df_200::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_200,
                ROUND(js_7df_100::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_100,
                ROUND(js_7df_50::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_50,
                ROUND(js_7df_25::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_25,
                ROUND(js_7df_20::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_20,
                ROUND(js_7df_10::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_10,
                ROUND(js_7df_5::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_5,
                ROUND(js_7df_2::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_2,
                ROUND(js_7df_1::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_1,
                ROUND(js_7df_1_01::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_1_01,
                ROUND(js_7df_yr::NUMERIC, 2)::DOUBLE PRECISION AS js_7df_yr,
                ROUND(ann_7df_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_200,
                ROUND(ann_7df_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_100,
                ROUND(ann_7df_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_50,
                ROUND(ann_7df_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_25,
                ROUND(ann_7df_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_20,
                ROUND(ann_7df_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_10,
                ROUND(ann_7df_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_5,
                ROUND(ann_7df_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_2,
                ROUND(ann_7df_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_1,
                ROUND(ann_7df_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_1_01,
                ROUND(ann_7df_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr
            ) AS _
        ) AS station_flow_metric
    FROM cariboo.flow_metrics
    JOIN cariboo.stations
    USING (station_id))
    SELECT DISTINCT ON (original_id) * FROM a;
"""

extreme_flow_query = """
    SELECT
        station_id AS old_station_id,
        val AS value,
        variable_id AS variable_name
    FROM water.extreme_flow
    JOIN water.nwp_stations
    USING (foundry_id);
"""

water_level_query = """
    SELECT
        station_id AS old_station_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id,
        CASE
            WHEN symbol IS NULL
                THEN 6
            ELSE symbol
        END AS symbol_id
    FROM
        (
            SELECT
                *
            FROM
                wet.water_daily
            WHERE
                variable_id IN (2)
        ) AS precip
    JOIN
        wet.stations
    USING (station_id);
"""

water_discharge_query = """
    SELECT
        station_id AS old_station_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id,
        CASE
            WHEN symbol IS NULL
                THEN 6
            ELSE symbol
        END AS symbol_id
    FROM
        (
            SELECT
                *
            FROM
                wet.water_daily
            WHERE
                variable_id IN (1)
        ) AS precip
    JOIN
        wet.stations
    USING (station_id);
"""

exclude_reason_query = """
    SELECT
        excludetype AS exclude_id,
        description AS exclude_description
    FROM
        wet.water_exclude_type;
"""

exclude_station_year_query = """
    SELECT
        station_id AS old_station_id,
        excludetype AS exclude_id,
        dateyear
    FROM
        wet.water_exclude
    JOIN wet.stations
    USING (station_id);
"""

ems_location_type_query = """
    SELECT
        location_type_code,
        site_type_description AS location_type_description,
        "include"
    FROM wet.waterquality_ems_location_type_code;
"""

water_quality_parameter_query = """
    SELECT
        parameter_id,
        grouping_id,
        "parameter" AS parameter_name,
        parameter_simple AS parameter_desc
    FROM
        wet.waterquality_parameter_groupings;
"""

water_quality_parameter_grouping_query = """
    SELECT
        grouping_id,
        grouping_name,
        parent_group,
        child_group
    FROM
        wet.waterquality_parameter_groupings_unique;
"""

water_quality_units = """
    SELECT
        unit_id,
        unit AS unit_name
    FROM
        wet.waterquality_units;
"""

water_quality_hourly_data = """
    SELECT
        station_id AS old_station_id,
        datetimestamp,
        parameter_id,
        unit_id,
        qa_id,
        location_purpose,
        sampling_agency,
        analyzing_agency,
        collection_method,
        sample_state,
        sample_descriptor,
        analytical_method,
        qa_index_code,
        result AS value,
        result_text AS value_text,
        result_letter AS value_letter
    FROM wet.waterquality_hourly_hist_new
    JOIN wet.stations
    USING (station_id);
"""

symbol_id_query = """
    SELECT
        symbol_id,
        symbol_code,
        description
    FROM
        wet.symbols
    UNION
    SELECT
        6 AS symbol_id,
        'N' AS symbol_code,
        'No symbol provided for this data' AS description

	ORDER BY symbol_id;
"""

ground_water_query = """
    SELECT
        station_id AS old_station_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id,
        CASE
            WHEN symbol IS NULL
                THEN 6
            ELSE symbol
        END AS symbol_id
    FROM
        (
            SELECT
                *
            FROM
                wet.water_daily
            WHERE
                variable_id IN (3)
        ) AS gw
    JOIN
        wet.stations
    USING (station_id);
"""
