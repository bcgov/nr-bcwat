fwa_stream_name_query = '''SELECT * FROM base.fwa_stream_names'''

fwa_stream_name_unique_query = ''' SELECT * FROM base.fwa_stream_names_unique'''

fwa_fund_query = '''
    WITH unioned AS (
        (SELECT
            watershed_feature_id,
            fwa_watershed_code,
            local_watershed_code,
            the_geom,
            centroid,
            lake_name,
            report,
            local_watershed_order,
            has_upstream,
            in_study_area,
            point_inside_poly,
            lake,
            area,
            ST_Transform(the_geom, 4326) AS geom4326,
            ST_Transform(point_inside_poly, 4326) AS point_inside_poly4326,
            ST_X(ST_Transform(point_inside_poly, 4326)) AS pip_x,
            ST_Y(ST_Transform(point_inside_poly, 4326)) AS pip_y
        FROM cariboo.fwa_funds)
        UNION
        (SELECT
            watershed_feature_id,
            fwa_watershed_code,
            local_watershed_code,
            the_geom,
            centroid,
            lake_name,
            report,
            local_watershed_order,
            has_upstream,
            in_study_area,
            point_inside_poly,
            lake,
            area,
            geom4326,
            point_inside_poly_4326 AS point_inside_poly4326,
            pip_x,
            pip_y
        FROM kwt.fwa_funds)
        UNION
        (SELECT
            watershed_feature_id,
            fwa_watershed_code,
            local_watershed_code,
            the_geom,
            centroid,
            lake_name,
            report,
            local_watershed_order,
            has_upstream,
            in_study_area,
            point_inside_poly,
            lake,
            area,
            geom4326,
            ST_Transform(point_inside_poly, 4326) AS point_inside_poly4326,
            ST_X(ST_Transform(point_inside_poly, 4326)) AS pip_x,
            ST_Y(ST_Transform(point_inside_poly, 4326)) AS pip_y
        FROM nwwt.fwa_funds)
        UNION
        (SELECT
            watershed_feature_id,
            fwa_watershed_code,
            local_watershed_code,
            the_geom,
            centroid,
            lake_name,
            report,
            local_watershed_order,
            has_upstream,
            in_study_area,
            point_inside_poly,
            lake,
            area,
            geom4326,
            ST_Transform(point_inside_poly, 4326) AS point_inside_poly4326,
            ST_X(ST_Transform(point_inside_poly, 4326)) AS pip_x,
            ST_Y(ST_Transform(point_inside_poly, 4326)) AS pip_y
        FROM owt.fwa_funds)
    ) SELECT DISTINCT ON (watershed_feature_id) (unioned).*,  nwwt_fwa.watershed_feature_id_foundry_eca, kwt_fwa.has_netcdf FROM unioned
    LEFT JOIN (SELECT watershed_feature_id, watershed_feature_id_foundry_eca FROM nwwt.fwa_funds) nwwt_fwa
    USING (watershed_feature_id)
    LEFT JOIN (SELECT watershed_feature_id, has_netcdf FROM kwt.fwa_funds) kwt_fwa
    USING (watershed_feature_id)
'''

fwa_union_query = '''
    WITH unioned AS (
        (SELECT fwa_watershed_code, geom_simp4326 FROM kwt.fwa_union)
        UNION
        (SELECT fwa_watershed_code, geom_simp4326 FROM nwwt.fwa_union)
        UNION
        (SELECT fwa_watershed_code, geom_simp4326 FROM owt.fwa_union)
    ) SELECT DISTINCT ON (fwa_watershed_code) * FROM unioned
'''

fund_rollup_query = '''
    WITH unioned AS (
        (SELECT * FROM cariboo.funds_rollups)
        UNION
        (SELECT * FROM kwt.funds_rollups)
    ) SELECT DISTINCT ON (watershed_feature_id) * FROM unioned;
'''

fund_rollup_report_query = '''
    WITH unioned AS (
        (SELECT * FROM nwwt.funds_rollups_report LIMIT 1000)
        UNION ALL
        (SELECT * FROM owt.funds_rollups_report LIMIT 1000)
    ) SELECT DISTINCT ON (watershed_feature_id) * FROM unioned
'''

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

geo_features_query = '''
    SELECT
		geoname,
		zoom,
		geocomment,
		conciscode AS concisecode,
		x,
		y,
		ST_SetSRID(ST_Point(x, y), 4326) AS geom4326,
		NULL::timestamptz AS dt_imported
	FROM cariboo.geonames
	UNION
	SELECT
		geoname,
		zoom,
		geocomment,
		conciscode AS concisecode,
		x,
		y,
		ST_SetSRID(geom, 4326) AS geom4326,
		dt_imported
	FROM kwt.geonames
	UNION
	SELECT
		geoname,
		zoom,
		geocomment,
		conciscode AS concisecode,
		x,
		y,
		ST_SetSRID(ST_Point(x, y), 4326) AS geom4326,
		NULL::TIMESTAMPTZ AS dt_imported
	FROM nwwt.geonames
	UNION
	SELECT
		geoname,
		zoom,
		geocomment,
		conciscode AS concisecode,
		x,
		y,
		ST_SetSRID(ST_Point(x, y), 4326) AS geom4326,
		NULL::TIMESTAMPTZ AS dt_imported
	FROM owt.geonames;
'''

mapsearch2_query = '''
    SELECT
		geoname,
        x,
        y,
        zoom,
        geocomment,
        conciscode AS concisecode
    FROM water.mapsearch2;
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
        DISTINCT ON (native_id)
        native_id AS original_id,
        station_name,
        stream_name,
        description AS station_description,
        status_id AS station_status_id,
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
        user_flag,
        import_json::json
    FROM
        wet.stations
    WHERE
        prov_terr_state_loc = 'BC';
'''

station_project_id_query = '''
    SELECT DISTINCT ON (original_id, project_id) native_id AS original_id, unnest(project_id) AS project_id FROM wet.stations
    WHERE prov_terr_state_loc = 'BC';
'''

station_region_query = '''
    SELECT station_id, region_id FROM bcwat_obs.station
    JOIN bcwat_obs.region
	ON (ST_Within(geom4326, region_click_studyarea));
'''

station_type_id_query = '''
    SELECT DISTINCT ON (original_id, type_id) native_id AS original_id, type_id FROM wet.stations
    WHERE prov_terr_state_loc = 'BC';
'''

water_station_variable_query= '''
    SELECT DISTINCT ON (original_id, variable_id) native_id AS original_id, unnest(var_array) AS variable_id FROM wet.stations
    WHERE prov_terr_state_loc = 'BC'
    AND climate_foundry_id IS NULL;
'''

climate_station_variable_query = '''
    SELECT DISTINCT ON (native_id, variable_id) native_id AS original_id, unnest(var_array) AS variable_id FROM wet.stations
    WHERE prov_terr_state_loc = 'BC'
    AND climate_foundry_id IS NOT NULL
'''

station_year_query = '''
    SELECT DISTINCT ON (original_id, year) native_id AS original_id, unnest(year_array) AS year FROM wet.stations
    WHERE prov_terr_state_loc = 'BC';
'''

station_network_id_query = '''
	SELECT DISTINCT ON (original_id, network_id) native_id AS original_id, network_id FROM wet.stations
    WHERE prov_terr_state_loc = 'BC';
'''
