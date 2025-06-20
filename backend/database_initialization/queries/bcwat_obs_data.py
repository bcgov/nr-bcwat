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
        'swp' AS region_name,
        geom AS region_click_studyarea,
        NULL::geometry as region_studyarea_allfunds
    FROM bcwmd.swp_study_area
    UNION
    SELECT
        'nwp' AS region_name,
        geom AS region_click_studyarea,
        NULL::geometry as region_studyarea_allfunds
    FROM bcwmd.nwp_study_area
    UNION
    SELECT
        'cariboo' AS region_name,
        geom AS region_click_studyarea,
        ST_Transform(geom3005, 4326) AS region_studyarea_allfunds
    FROM cariboo.cariboo_region
    CROSS JOIN cariboo.studyarea_allfunds
    UNION
    SELECT
        'kwt' AS region_name,
        ST_Transform(sr.geom4326, 4326) AS region_click_studyarea,
        af.geom4326 AS region_studyarea_allfunds
    FROM kwt.study_region sr
    CROSS JOIN kwt.studyarea_allfunds af
    UNION
    SELECT
        'nwwt' AS region_name,
        sa.geom4326_simplified AS region_click_studyarea,
        af.geom4326 AS region_studyarea_allfunds
    FROM nwwt.nwwt_click_study_area sa
    CROSS JOIN nwwt.studyarea_allfunds af
    UNION
    SELECT
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
    SELECT * FROM wet.project;
'''

station_query = '''
    SELECT
        native_id AS original_id,
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
        native_id AS original_id,
        unnest(project_id) AS project_id,
        longitude,
        latitude
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
        unnest(project_id) AS project_id,
        longitude,
        latitude
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
        native_id AS original_id,
        unnest(var_array) AS variable_id,
        longitude,
        latitude
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
        CASE
            WHEN import_json IS NOT NULL
                THEN import_json->>'StationId'
            ELSE native_id
        END AS original_id,
        unnest(var_array) AS variable_id,
        longitude,
        latitude
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
        native_id AS original_id,
        unnest(var_array) AS variable_id,
        longitude,
        latitude
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
        CASE
            WHEN import_json IS NOT NULL
                THEN import_json->>'StationId'
            ELSE native_id
        END AS original_id,
        unnest(var_array) AS variable_id,
        longitude,
        latitude
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
        native_id AS original_id,
        unnest(var_array) AS parameter_id,
        longitude,
        latitude
    FROM
        wet.stations
    WHERE
        prov_terr_state_loc = 'BC'
    AND
        network_id IN (25, 26, 27, 28, 44, 51, 52)
"""

station_year_query = '''
    SELECT
        native_id AS original_id,
        unnest(year_array) AS year,
        longitude,
        latitude
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
        unnest(year_array) AS year,
        longitude,
        latitude
    FROM
        wet.stations
    WHERE
        prov_terr_state_loc = 'BC'
    AND
        network_id = 30;
'''

climate_hourly_realtime = """
    SELECT
        native_id AS original_id,
        variable_id,
        datetimestamp,
        val AS value,
        qa_id,
        longitude,
        latitude
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
        native_id AS original_id,
        variable_id,
        survey_period,
        datestamp,
        val AS value,
        code,
        qa_id,
        longitude,
        latitude
    FROM
        wet.climate_msp_daily
    JOIN
        wet.stations
    USING (station_id);
"""

climate_precipitation_realtime = """
    SELECT
        native_id AS original_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id,
        longitude,
        latitude
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
        native_id AS original_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id,
        longitude,
        latitude
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
        native_id AS original_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id,
        longitude,
        latitude
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
        native_id AS original_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id,
        longitude,
        latitude
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
        native_id AS original_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id,
        longitude,
        latitude
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
        native_id AS original_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id,
        longitude,
        latitude
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
        native_id AS original_id,
        longitude,
        latitude,
        (SELECT row_to_json(_) FROM
            (SELECT
                ROUND(ipf_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr
            ) AS _
        ) AS station_flow_metric
    FROM bcwmd.flow_metrics
    JOIN bcwmd.stations
    USING (station_id)
    UNION ALL
    SELECT
        native_id AS original_id,
        ST_X(geom) AS longitude,
        ST_Y(geom) AS latitude,
        (SELECT row_to_json(_) FROM
            (SELECT
                ROUND(ipf_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr
            ) AS _
        ) AS station_flow_metric
    FROM water.flow_metrics
    JOIN water.nwp_stations
    USING (foundry_id)
    UNION ALL
    SELECT
        native_id AS original_id,
        longitude,
        latitude,
        (SELECT row_to_json(_) FROM
            (SELECT
                ROUND(ipf_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ipf_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfh_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(amfl_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(js_7df_yr::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_200::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_100::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_50::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_25::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_20::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_10::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_5::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_2::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_1::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
                ROUND(ann_7df_1_01::NUMERIC, 2)::DOUBLE PRECISION AS ann_7df_yr,
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
        native_id AS original_id,
        val AS value,
        variable_id AS variable_name,
        ST_X(geom) AS longitude,
        ST_Y(geom) latitude
    FROM water.extreme_flow
    JOIN water.nwp_stations
    USING (foundry_id);
"""

water_level_query = """
    SELECT
        native_id AS original_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id,
        longitude,
        latitude
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
        native_id AS original_id,
        variable_id,
        datestamp,
        val AS value,
        qa_id,
        longitude,
        latitude
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
        native_id AS original_id,
        excludetype AS exclude_id,
        dateyear,
        longitude,
        latitude
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
        native_id AS original_id,
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
        result,
        result_text,
        result_letter,
        longitude,
        latitude
    FROM wet.waterquality_hourly_hist_new
    JOIN wet.stations
    USING (station_id);
"""
