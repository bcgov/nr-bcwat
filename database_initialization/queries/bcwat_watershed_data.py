fwa_stream_name_query = '''
    SELECT
        linear_feature_id,
        fwa_watershed_code,
        gnis_name,
        stream_magnitude,
        ST_AsGeoJSON(ST_Transform(geom, 4326)) AS geom4326,
        ST_AsGeoJSON(ST_Transform(st_point_on_line, 4326)) AS point_on_line4326
    FROM
        base.fwa_stream_names
'''

fwa_stream_name_unique_query = '''
    SELECT
        *
    FROM
        base.fwa_stream_names_unique
'''

fwa_fund_query = '''
WITH unioned AS (
        (SELECT
            watershed_feature_id,
            watershed_feature_id_foundry,
            fwa_watershed_code,
            local_watershed_code,
            ST_AsGeoJSON(the_geom) AS the_geom,
            ST_AsGeoJSON(centroid) AS centroid,
            lake_name,
            report,
            local_watershed_order,
            has_upstream,
            in_study_area,
            ST_AsGeoJSON(point_inside_poly) AS point_inside_poly,
            lake,
            area,
            ST_AsGeoJSON(ST_Transform(the_geom, 4326)) AS geom4326,
            ST_AsGeoJSON(ST_Transform(point_inside_poly, 4326)) AS point_inside_poly4326,
            ST_X(ST_Transform(point_inside_poly, 4326)) AS pip_x4326,
            ST_Y(ST_Transform(point_inside_poly, 4326)) AS pip_y4326
        FROM cariboo.fwa_funds)
        UNION
        (SELECT
            watershed_feature_id,
            watershed_feature_id_foundry,
            fwa_watershed_code,
            local_watershed_code,
            ST_AsGeoJSON(the_geom) AS the_geom,
            ST_AsGeoJSON(centroid) AS centroid,
            lake_name,
            report,
            local_watershed_order,
            has_upstream,
            in_study_area,
            ST_AsGeoJSON(point_inside_poly) AS point_inside_poly,
            lake,
            area,
            ST_AsGeoJSON(geom4326) AS geom4326,
            ST_AsGeoJSON(point_inside_poly_4326) AS point_inside_poly4326,
            pip_x AS pip_x4326,
            pip_y AS pip_y4326
        FROM kwt.fwa_funds)
        UNION
        (SELECT
            watershed_feature_id,
            watershed_feature_id_foundry,
            fwa_watershed_code,
            local_watershed_code,
            ST_AsGeoJSON(the_geom) AS the_geom,
            ST_AsGeoJSON(centroid) AS centroid,
            lake_name,
            report,
            local_watershed_order,
            has_upstream,
            in_study_area,
            ST_AsGeoJSON(point_inside_poly) AS point_inside_poly,
            lake,
            area,
            ST_AsGeoJSON(geom4326) AS geom4326,
            ST_AsGeoJSON(ST_Transform(point_inside_poly, 4326)) AS point_inside_poly4326,
            ST_X(ST_Transform(point_inside_poly, 4326)) AS pip_x4326,
            ST_Y(ST_Transform(point_inside_poly, 4326)) AS pip_y4326
        FROM nwwt.fwa_funds)
        UNION
        (SELECT
            watershed_feature_id,
            watershed_feature_id_foundry,
            fwa_watershed_code,
            local_watershed_code,
            ST_AsGeoJSON(the_geom) AS the_geom,
            ST_AsGeoJSON(centroid) AS centroid,
            lake_name,
            report,
            local_watershed_order,
            has_upstream,
            in_study_area,
            ST_AsGeoJSON(point_inside_poly) AS point_inside_poly,
            lake,
            area,
            ST_AsGeoJSON(geom4326) AS geom4326,
            ST_AsGeoJSON(ST_Transform(point_inside_poly, 4326)) AS point_inside_poly4326,
            ST_X(ST_Transform(point_inside_poly, 4326)) AS pip_x4326,
            ST_Y(ST_Transform(point_inside_poly, 4326)) AS pip_y4326
        FROM owt.fwa_funds)
    )
    SELECT
        DISTINCT ON (watershed_feature_id)
		(unioned).*,
        nwwt_fwa.watershed_feature_id_foundry_eca,
        kwt_fwa.has_netcdf
    FROM
        unioned
    LEFT JOIN
        (SELECT watershed_feature_id, watershed_feature_id_foundry_eca FROM nwwt.fwa_funds) nwwt_fwa
    USING
        (watershed_feature_id)
    LEFT JOIN
        (SELECT watershed_feature_id, has_netcdf FROM kwt.fwa_funds) kwt_fwa
    USING
        (watershed_feature_id)
'''

fwa_union_query = '''
    WITH unioned AS (
        (SELECT fwa_watershed_code, ST_AsGeoJSON(geom_simp4326) AS geom_simp4326 FROM kwt.fwa_union)
        UNION
        (SELECT fwa_watershed_code, ST_AsGeoJSON(geom_simp4326) AS geom_simp4326 FROM nwwt.fwa_union)
        UNION
        (SELECT fwa_watershed_code, ST_AsGeoJSON(geom_simp4326) AS geom_simp4326 FROM owt.fwa_union)
    ) SELECT DISTINCT ON (fwa_watershed_code) * FROM unioned
'''

geo_features_query = '''
    SELECT
        geoname,
        zoom,
        geocomment,
        conciscode AS concisecode,
        x,
        y,
        ST_AsGeoJSON(ST_SetSRID(ST_Point(x, y), 4326)) AS geom4326,
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
        ST_AsGeoJSON(ST_SetSRID(geom, 4326)) AS geom4326,
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
        ST_AsGeoJSON(ST_SetSRID(ST_Point(x, y), 4326)) AS geom4326,
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
        ST_AsGeoJSON(ST_SetSRID(ST_Point(x, y), 4326)) AS geom4326,
        NULL::TIMESTAMPTZ AS dt_imported
    FROM owt.geonames
'''

mapsearch2_query = '''
    SELECT
        geoname,
        x,
        y,
        zoom,
        geocomment,
        conciscode AS concisecode
    FROM water.mapsearch2
'''

fdc_query = """
    SELECT
        watershed_feature_id,
        month,
        (SELECT row_to_json(_) FROM
            (SELECT
                percs,
                c1,
                q_m3s_c1,
                c2,
                q_m3s_c2,
                c3,
                q_m3s_c3,
                percs_all,
                q_m3s_c1_all
            ) AS _
        ) AS month_value
    FROM owt.fdc
    UNION ALL
    SELECT
        watershed_feature_id,
        month,
        (SELECT row_to_json(_) FROM
            (SELECT
                percs,
                c1,
                q_m3s_c1,
                c2,
                q_m3s_c2,
                c3,
                q_m3s_c3,
                percs_all,
                q_m3s_c1_all
            ) AS _
        ) AS month_value
    FROM nwwt.fdc
"""

fdc_distance_query = """
    SELECT
    owt_fdc.watershed_feature_id,
    owt_fdc.candidate,
    (
        SELECT
            row_to_json(_)
        FROM
        (
            SELECT
                owt_fdc.month01,
                owt_fdc.month02,
                owt_fdc.month03,
                owt_fdc.month04,
                owt_fdc.month05,
                owt_fdc.month06,
                owt_fdc.month07,
                owt_fdc.month08,
                owt_fdc.month09,
                owt_fdc.month10,
                owt_fdc.month11,
                owt_fdc.month12
        ) AS _
    ) AS candidate_month_value
    FROM
    owt.fdc_distance owt_fdc
    UNION ALL
	SELECT
	nwwt_fdc.watershed_feature_id,
    nwwt_fdc.candidate,
	(
		SELECT
			row_to_json(_)
		FROM
		(
			SELECT
				nwwt_fdc.month01,
				nwwt_fdc.month02,
				nwwt_fdc.month03,
				nwwt_fdc.month04,
				nwwt_fdc.month05,
				nwwt_fdc.month06,
				nwwt_fdc.month07,
				nwwt_fdc.month08,
				nwwt_fdc.month09,
				nwwt_fdc.month10,
				nwwt_fdc.month11,
				nwwt_fdc.month12
		) AS _
	) AS candidate_month_value
FROM
	nwwt.fdc_distance nwwt_fdc
"""

fdc_physical_query = """
    SELECT
        watershed_feature_id,
        (SELECT row_to_json(_) FROM
            (SELECT
                lat,
                lon,
                upstream_area_km2,
                min_elev,
                avg_elev,
                max_elev,
                month,
                ppt,
                tave,
                pas
            ) AS _
        ) AS watershed_fdc_data
    FROM
        owt.fdc_physical
    UNION ALL
    SELECT
        watershed_feature_id,
        (SELECT row_to_json(_) FROM
            (SELECT
                lat,
                lon,
                upstream_area_km2,
                min_elev,
                avg_elev,
                max_elev,
                month,
                ppt,
                tave,
                pas
            ) AS _
        ) AS watershed_fdc_data
    FROM
        nwwt.fdc_physical
"""


watershed_funds_reports = """
    SELECT
        cariboo_rollup.watershed_feature_id,
        cariboo_rollup.downstream_id,
        (SELECT row_to_json(_) FROM
            (SELECT
                cariboo_rollup.upstream_area / 1000000 AS watershed_area_km2,
                cariboo_rollup.dem400,
                ARRAY[
                    cariboo_rollup.ppt01,
                    cariboo_rollup.ppt02,
                    cariboo_rollup.ppt03,
                    cariboo_rollup.ppt04,
                    cariboo_rollup.ppt05,
                    cariboo_rollup.ppt06,
                    cariboo_rollup.ppt07,
                    cariboo_rollup.ppt08,
                    cariboo_rollup.ppt09,
                    cariboo_rollup.ppt10,
                    cariboo_rollup.ppt11,
                    cariboo_rollup.ppt12
                ] AS ppt_monthly_hist,
                ARRAY[
                    cariboo_rollup.tave01,
                    cariboo_rollup.tave02,
                    cariboo_rollup.tave03,
                    cariboo_rollup.tave04,
                    cariboo_rollup.tave05,
                    cariboo_rollup.tave06,
                    cariboo_rollup.tave07,
                    cariboo_rollup.tave08,
                    cariboo_rollup.tave09,
                    cariboo_rollup.tave10,
                    cariboo_rollup.tave11,
                    cariboo_rollup.tave12
                ] AS tave_monthly_hist,
                ARRAY[
                    cariboo_rollup.pas01,
                    cariboo_rollup.pas02,
                    cariboo_rollup.pas03,
                    cariboo_rollup.pas04,
                    cariboo_rollup.pas05,
                    cariboo_rollup.pas06,
                    cariboo_rollup.pas07,
                    cariboo_rollup.pas08,
                    cariboo_rollup.pas09,
                    cariboo_rollup.pas10,
                    cariboo_rollup.pas11,
                    cariboo_rollup.pas12
                ] AS ppt_monthly_hist,
                ARRAY[
                    GREATEST(
                        cariboo_rollup.pas01_a2,
                        cariboo_rollup.pas01_a1b,
                        cariboo_rollup.pas01_b1
                    ),
                    GREATEST(
                        cariboo_rollup.pas02_a2,
                        cariboo_rollup.pas02_a1b,
                        cariboo_rollup.pas02_b1
                    ),
                    GREATEST(
                        cariboo_rollup.pas03_a2,
                        cariboo_rollup.pas03_a1b,
                        cariboo_rollup.pas03_b1
                    ),
                    GREATEST(
                        cariboo_rollup.pas04_a2,
                        cariboo_rollup.pas04_a1b,
                        cariboo_rollup.pas04_b1
                    ),
                    GREATEST(
                        cariboo_rollup.pas05_a2,
                        cariboo_rollup.pas05_a1b,
                        cariboo_rollup.pas05_b1
                    ),
                    GREATEST(
                        cariboo_rollup.pas06_a2,
                        cariboo_rollup.pas06_a1b,
                        cariboo_rollup.pas06_b1
                    ),
                    GREATEST(
                        cariboo_rollup.pas07_a2,
                        cariboo_rollup.pas07_a1b,
                        cariboo_rollup.pas07_b1
                    ),
                    GREATEST(
                        cariboo_rollup.pas08_a2,
                        cariboo_rollup.pas08_a1b,
                        cariboo_rollup.pas08_b1
                    ),
                    GREATEST(
                        cariboo_rollup.pas09_a2,
                        cariboo_rollup.pas09_a1b,
                        cariboo_rollup.pas09_b1
                    ),
                    GREATEST(
                        cariboo_rollup.pas10_a2,
                        cariboo_rollup.pas10_a1b,
                        cariboo_rollup.pas10_b1
                    ),
                    GREATEST(
                        cariboo_rollup.pas11_a2,
                        cariboo_rollup.pas11_a1b,
                        cariboo_rollup.pas11_b1
                    ),
                    GREATEST(
                        cariboo_rollup.pas12_a2,
                        cariboo_rollup.pas12_a1b,
                        cariboo_rollup.pas12_b1
                    )
                ]::DOUBLE PRECISION[12] AS pas_monthly_future_max,
                ARRAY[
                    LEAST(
                        cariboo_rollup.pas01_a2,
                        cariboo_rollup.pas01_a1b,
                        cariboo_rollup.pas01_b1
                    ),
                    LEAST(
                        cariboo_rollup.pas02_a2,
                        cariboo_rollup.pas02_a1b,
                        cariboo_rollup.pas02_b1
                    ),
                    LEAST(
                        cariboo_rollup.pas03_a2,
                        cariboo_rollup.pas03_a1b,
                        cariboo_rollup.pas03_b1
                    ),
                    LEAST(
                        cariboo_rollup.pas04_a2,
                        cariboo_rollup.pas04_a1b,
                        cariboo_rollup.pas04_b1
                    ),
                    LEAST(
                        cariboo_rollup.pas05_a2,
                        cariboo_rollup.pas05_a1b,
                        cariboo_rollup.pas05_b1
                    ),
                    LEAST(
                        cariboo_rollup.pas06_a2,
                        cariboo_rollup.pas06_a1b,
                        cariboo_rollup.pas06_b1
                    ),
                    LEAST(
                        cariboo_rollup.pas07_a2,
                        cariboo_rollup.pas07_a1b,
                        cariboo_rollup.pas07_b1
                    ),
                    LEAST(
                        cariboo_rollup.pas08_a2,
                        cariboo_rollup.pas08_a1b,
                        cariboo_rollup.pas08_b1
                    ),
                    LEAST(
                        cariboo_rollup.pas09_a2,
                        cariboo_rollup.pas09_a1b,
                        cariboo_rollup.pas09_b1
                    ),
                    LEAST(
                        cariboo_rollup.pas10_a2,
                        cariboo_rollup.pas10_a1b,
                        cariboo_rollup.pas10_b1
                    ),
                    LEAST(
                        cariboo_rollup.pas11_a2,
                        cariboo_rollup.pas11_a1b,
                        cariboo_rollup.pas11_b1
                    ),
                    LEAST(
                        cariboo_rollup.pas12_a2,
                        cariboo_rollup.pas12_a1b,
                        cariboo_rollup.pas12_b1
                    )
                ]::DOUBLE PRECISION[12] AS pas_monthly_future_min,
                ARRAY[
                    GREATEST(
                        cariboo_rollup.ppt01_a2,
                        cariboo_rollup.ppt01_a1b,
                        cariboo_rollup.ppt01_b1
                    ),
                    GREATEST(
                        cariboo_rollup.ppt02_a2,
                        cariboo_rollup.ppt02_a1b,
                        cariboo_rollup.ppt02_b1
                    ),
                    GREATEST(
                        cariboo_rollup.ppt03_a2,
                        cariboo_rollup.ppt03_a1b,
                        cariboo_rollup.ppt03_b1
                    ),
                    GREATEST(
                        cariboo_rollup.ppt04_a2,
                        cariboo_rollup.ppt04_a1b,
                        cariboo_rollup.ppt04_b1
                    ),
                    GREATEST(
                        cariboo_rollup.ppt05_a2,
                        cariboo_rollup.ppt05_a1b,
                        cariboo_rollup.ppt05_b1
                    ),
                    GREATEST(
                        cariboo_rollup.ppt06_a2,
                        cariboo_rollup.ppt06_a1b,
                        cariboo_rollup.ppt06_b1
                    ),
                    GREATEST(
                        cariboo_rollup.ppt07_a2,
                        cariboo_rollup.ppt07_a1b,
                        cariboo_rollup.ppt07_b1
                    ),
                    GREATEST(
                        cariboo_rollup.ppt08_a2,
                        cariboo_rollup.ppt08_a1b,
                        cariboo_rollup.ppt08_b1
                    ),
                    GREATEST(
                        cariboo_rollup.ppt09_a2,
                        cariboo_rollup.ppt09_a1b,
                        cariboo_rollup.ppt09_b1
                    ),
                    GREATEST(
                        cariboo_rollup.ppt10_a2,
                        cariboo_rollup.ppt10_a1b,
                        cariboo_rollup.ppt10_b1
                    ),
                    GREATEST(
                        cariboo_rollup.ppt11_a2,
                        cariboo_rollup.ppt11_a1b,
                        cariboo_rollup.ppt11_b1
                    ),
                    GREATEST(
                        cariboo_rollup.ppt12_a2,
                        cariboo_rollup.ppt12_a1b,
                        cariboo_rollup.ppt12_b1
                    )
                ]::DOUBLE PRECISION[12] AS ppt_monthly_future_max,
                ARRAY[
                    LEAST(
                        cariboo_rollup.ppt01_a2,
                        cariboo_rollup.ppt01_a1b,
                        cariboo_rollup.ppt01_b1
                    ),
                    LEAST(
                        cariboo_rollup.ppt02_a2,
                        cariboo_rollup.ppt02_a1b,
                        cariboo_rollup.ppt02_b1
                    ),
                    LEAST(
                        cariboo_rollup.ppt03_a2,
                        cariboo_rollup.ppt03_a1b,
                        cariboo_rollup.ppt03_b1
                    ),
                    LEAST(
                        cariboo_rollup.ppt04_a2,
                        cariboo_rollup.ppt04_a1b,
                        cariboo_rollup.ppt04_b1
                    ),
                    LEAST(
                        cariboo_rollup.ppt05_a2,
                        cariboo_rollup.ppt05_a1b,
                        cariboo_rollup.ppt05_b1
                    ),
                    LEAST(
                        cariboo_rollup.ppt06_a2,
                        cariboo_rollup.ppt06_a1b,
                        cariboo_rollup.ppt06_b1
                    ),
                    LEAST(
                        cariboo_rollup.ppt07_a2,
                        cariboo_rollup.ppt07_a1b,
                        cariboo_rollup.ppt07_b1
                    ),
                    LEAST(
                        cariboo_rollup.ppt08_a2,
                        cariboo_rollup.ppt08_a1b,
                        cariboo_rollup.ppt08_b1
                    ),
                    LEAST(
                        cariboo_rollup.ppt09_a2,
                        cariboo_rollup.ppt09_a1b,
                        cariboo_rollup.ppt09_b1
                    ),
                    LEAST(
                        cariboo_rollup.ppt10_a2,
                        cariboo_rollup.ppt10_a1b,
                        cariboo_rollup.ppt10_b1
                    ),
                    LEAST(
                        cariboo_rollup.ppt11_a2,
                        cariboo_rollup.ppt11_a1b,
                        cariboo_rollup.ppt11_b1
                    ),
                    LEAST(
                        cariboo_rollup.ppt12_a2,
                        cariboo_rollup.ppt12_a1b,
                        cariboo_rollup.ppt12_b1
                    )
                ]::DOUBLE PRECISION[12] AS ppt_monthly_future_min,
                ARRAY[
                    GREATEST(
                        cariboo_rollup.tave01_a2,
                        cariboo_rollup.tave01_a1b,
                        cariboo_rollup.tave01_b1
                    ),
                    GREATEST(
                        cariboo_rollup.tave02_a2,
                        cariboo_rollup.tave02_a1b,
                        cariboo_rollup.tave02_b1
                    ),
                    GREATEST(
                        cariboo_rollup.tave03_a2,
                        cariboo_rollup.tave03_a1b,
                        cariboo_rollup.tave03_b1
                    ),
                    GREATEST(
                        cariboo_rollup.tave04_a2,
                        cariboo_rollup.tave04_a1b,
                        cariboo_rollup.tave04_b1
                    ),
                    GREATEST(
                        cariboo_rollup.tave05_a2,
                        cariboo_rollup.tave05_a1b,
                        cariboo_rollup.tave05_b1
                    ),
                    GREATEST(
                        cariboo_rollup.tave06_a2,
                        cariboo_rollup.tave06_a1b,
                        cariboo_rollup.tave06_b1
                    ),
                    GREATEST(
                        cariboo_rollup.tave07_a2,
                        cariboo_rollup.tave07_a1b,
                        cariboo_rollup.tave07_b1
                    ),
                    GREATEST(
                        cariboo_rollup.tave08_a2,
                        cariboo_rollup.tave08_a1b,
                        cariboo_rollup.tave08_b1
                    ),
                    GREATEST(
                        cariboo_rollup.tave09_a2,
                        cariboo_rollup.tave09_a1b,
                        cariboo_rollup.tave09_b1
                    ),
                    GREATEST(
                        cariboo_rollup.tave10_a2,
                        cariboo_rollup.tave10_a1b,
                        cariboo_rollup.tave10_b1
                    ),
                    GREATEST(
                        cariboo_rollup.tave11_a2,
                        cariboo_rollup.tave11_a1b,
                        cariboo_rollup.tave11_b1
                    ),
                    GREATEST(
                        cariboo_rollup.tave12_a2,
                        cariboo_rollup.tave12_a1b,
                        cariboo_rollup.tave12_b1
                    )
                ]::DOUBLE PRECISION[12] AS tave_monthly_future_max,
                ARRAY[
                    LEAST(
                        cariboo_rollup.tave01_a2,
                        cariboo_rollup.tave01_a1b,
                        cariboo_rollup.tave01_b1
                    ),
                    LEAST(
                        cariboo_rollup.tave02_a2,
                        cariboo_rollup.tave02_a1b,
                        cariboo_rollup.tave02_b1
                    ),
                    LEAST(
                        cariboo_rollup.tave03_a2,
                        cariboo_rollup.tave03_a1b,
                        cariboo_rollup.tave03_b1
                    ),
                    LEAST(
                        cariboo_rollup.tave04_a2,
                        cariboo_rollup.tave04_a1b,
                        cariboo_rollup.tave04_b1
                    ),
                    LEAST(
                        cariboo_rollup.tave05_a2,
                        cariboo_rollup.tave05_a1b,
                        cariboo_rollup.tave05_b1
                    ),
                    LEAST(
                        cariboo_rollup.tave06_a2,
                        cariboo_rollup.tave06_a1b,
                        cariboo_rollup.tave06_b1
                    ),
                    LEAST(
                        cariboo_rollup.tave07_a2,
                        cariboo_rollup.tave07_a1b,
                        cariboo_rollup.tave07_b1
                    ),
                    LEAST(
                        cariboo_rollup.tave08_a2,
                        cariboo_rollup.tave08_a1b,
                        cariboo_rollup.tave08_b1
                    ),
                    LEAST(
                        cariboo_rollup.tave09_a2,
                        cariboo_rollup.tave09_a1b,
                        cariboo_rollup.tave09_b1
                    ),
                    LEAST(
                        cariboo_rollup.tave10_a2,
                        cariboo_rollup.tave10_a1b,
                        cariboo_rollup.tave10_b1
                    ),
                    LEAST(
                        cariboo_rollup.tave11_a2,
                        cariboo_rollup.tave11_a1b,
                        cariboo_rollup.tave11_b1
                    ),
                    LEAST(
                        cariboo_rollup.tave12_a2,
                        cariboo_rollup.tave12_a1b,
                        cariboo_rollup.tave12_b1
                    )
                ]::DOUBLE PRECISION[12] AS tave_monthly_future_min,
                cariboo_rollup.lcc_shrub AS shrub,
                cariboo_rollup.lcc_grassland AS grassland,
                cariboo_rollup.lcc_coniferous AS coniferous,
                cariboo_rollup.lcc_water AS water,
                cariboo_rollup.lcc_snow AS snow,
                cariboo_rollup.lcc_developed AS developed,
                cariboo_rollup.lcc_wetland AS wetland,
                cariboo_rollup.lcc_herb AS herb,
                cariboo_rollup.lcc_deciduous AS deciduous,
                cariboo_rollup.lcc_mixed AS "mixed",
                cariboo_rollup.lcc_barren AS barren,
                cariboo_rollup.lcc_cropland AS cropland,
                (cariboo_rollup.qyr/1000) * (cariboo_rollup.upstream_area / (365.25 * 86400)) AS mad_m3s,
                (cariboo_rollup.qyr/1000) * cariboo_rollup.upstream_area AS mean_annual_runoff_m3yr,
                ARRAY[
                    ((cariboo_rollup.q01/1000) * cariboo_rollup.upstream_area)/ (86400 * 31),
                    ((cariboo_rollup.q02/1000) * cariboo_rollup.upstream_area)/ (86400 * 28),
                    ((cariboo_rollup.q03/1000) * cariboo_rollup.upstream_area)/ (86400 * 31),
                    ((cariboo_rollup.q04/1000) * cariboo_rollup.upstream_area)/ (86400 * 30),
                    ((cariboo_rollup.q05/1000) * cariboo_rollup.upstream_area)/ (86400 * 31),
                    ((cariboo_rollup.q06/1000) * cariboo_rollup.upstream_area)/ (86400 * 30),
                    ((cariboo_rollup.q07/1000) * cariboo_rollup.upstream_area)/ (86400 * 31),
                    ((cariboo_rollup.q08/1000) * cariboo_rollup.upstream_area)/ (86400 * 31),
                    ((cariboo_rollup.q09/1000) * cariboo_rollup.upstream_area)/ (86400 * 30),
                    ((cariboo_rollup.q10/1000) * cariboo_rollup.upstream_area)/ (86400 * 31),
                    ((cariboo_rollup.q11/1000) * cariboo_rollup.upstream_area)/ (86400 * 30),
                    ((cariboo_rollup.q12/1000) * cariboo_rollup.upstream_area)/ (86400 * 31)
                ] AS mean_monthly_discharge_m3s,
                cariboo_rollup.rr,
                cariboo_rollup.summer_sensitivity,
                cariboo_rollup.winter_sensitivity,
                hypso.elevs AS elevs,
                downstream.x4326 AS mgmt_lng,
                downstream.y4326 AS mgmt_lat,
                downstream.gnis_name AS downstream_gnis_name,
                downstream.area / 1000000 AS downstream_area_km2,
                NULL::smallint AS local_watershed_order) AS _) AS watershed_metadata

    FROM
        cariboo.funds_rollups AS cariboo_rollup
    JOIN
        cariboo.hypso_rollup AS hypso
    USING
        (watershed_feature_id)
    JOIN
        cariboo.ws_geoms_all_report downstream
    ON
        (downstream.watershed_feature_id = cariboo_rollup.downstream_id)
    JOIN
        (SELECT watershed_feature_id, upstream_geom AS upstream_geom3005 FROM cariboo.ws_geoms_all_report) upstream
    ON
        (cariboo_rollup.watershed_feature_id = upstream.watershed_feature_id)
    UNION ALL
    SELECT
        kwt_rollup.watershed_feature_id,
        kwt_rollup.downstream_id,
        (SELECT row_to_json(_) FROM
            (SELECT
                kwt_rollup.upstream_area / 1000000 AS watershed_area_km2,
                kwt_rollup.dem400,
                ARRAY[
                    kwt_rollup.ppt01,
                    kwt_rollup.ppt02,
                    kwt_rollup.ppt03,
                    kwt_rollup.ppt04,
                    kwt_rollup.ppt05,
                    kwt_rollup.ppt06,
                    kwt_rollup.ppt07,
                    kwt_rollup.ppt08,
                    kwt_rollup.ppt09,
                    kwt_rollup.ppt10,
                    kwt_rollup.ppt11,
                    kwt_rollup.ppt12
                ] AS ppt_monthly_hist,
                ARRAY[
                    kwt_rollup.tave01,
                    kwt_rollup.tave02,
                    kwt_rollup.tave03,
                    kwt_rollup.tave04,
                    kwt_rollup.tave05,
                    kwt_rollup.tave06,
                    kwt_rollup.tave07,
                    kwt_rollup.tave08,
                    kwt_rollup.tave09,
                    kwt_rollup.tave10,
                    kwt_rollup.tave11,
                    kwt_rollup.tave12
                ] AS tave_monthly_hist,
                ARRAY[
                    kwt_rollup.pas01,
                    kwt_rollup.pas02,
                    kwt_rollup.pas03,
                    kwt_rollup.pas04,
                    kwt_rollup.pas05,
                    kwt_rollup.pas06,
                    kwt_rollup.pas07,
                    kwt_rollup.pas08,
                    kwt_rollup.pas09,
                    kwt_rollup.pas10,
                    kwt_rollup.pas11,
                    kwt_rollup.pas12
                ] AS ppt_monthly_hist,
                ARRAY[
                    GREATEST(
                        kwt_rollup.pas01_access1,
                        kwt_rollup.pas01_canesm2,
                        kwt_rollup.pas01_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.pas02_access1,
                        kwt_rollup.pas02_canesm2,
                        kwt_rollup.pas02_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.pas03_access1,
                        kwt_rollup.pas03_canesm2,
                        kwt_rollup.pas03_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.pas04_access1,
                        kwt_rollup.pas04_canesm2,
                        kwt_rollup.pas04_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.pas05_access1,
                        kwt_rollup.pas05_canesm2,
                        kwt_rollup.pas05_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.pas06_access1,
                        kwt_rollup.pas06_canesm2,
                        kwt_rollup.pas06_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.pas07_access1,
                        kwt_rollup.pas07_canesm2,
                        kwt_rollup.pas07_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.pas08_access1,
                        kwt_rollup.pas08_canesm2,
                        kwt_rollup.pas08_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.pas09_access1,
                        kwt_rollup.pas09_canesm2,
                        kwt_rollup.pas09_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.pas10_access1,
                        kwt_rollup.pas10_canesm2,
                        kwt_rollup.pas10_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.pas11_access1,
                        kwt_rollup.pas11_canesm2,
                        kwt_rollup.pas11_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.pas12_access1,
                        kwt_rollup.pas12_canesm2,
                        kwt_rollup.pas12_cnrm
                    )
                ]::DOUBLE PRECISION[12] AS pas_monthly_future_max,
                ARRAY[
                    LEAST(
                        kwt_rollup.pas01_access1,
                        kwt_rollup.pas01_canesm2,
                        kwt_rollup.pas01_cnrm
                    ),
                    LEAST(
                        kwt_rollup.pas02_access1,
                        kwt_rollup.pas02_canesm2,
                        kwt_rollup.pas02_cnrm
                    ),
                    LEAST(
                        kwt_rollup.pas03_access1,
                        kwt_rollup.pas03_canesm2,
                        kwt_rollup.pas03_cnrm
                    ),
                    LEAST(
                        kwt_rollup.pas04_access1,
                        kwt_rollup.pas04_canesm2,
                        kwt_rollup.pas04_cnrm
                    ),
                    LEAST(
                        kwt_rollup.pas05_access1,
                        kwt_rollup.pas05_canesm2,
                        kwt_rollup.pas05_cnrm
                    ),
                    LEAST(
                        kwt_rollup.pas06_access1,
                        kwt_rollup.pas06_canesm2,
                        kwt_rollup.pas06_cnrm
                    ),
                    LEAST(
                        kwt_rollup.pas07_access1,
                        kwt_rollup.pas07_canesm2,
                        kwt_rollup.pas07_cnrm
                    ),
                    LEAST(
                        kwt_rollup.pas08_access1,
                        kwt_rollup.pas08_canesm2,
                        kwt_rollup.pas08_cnrm
                    ),
                    LEAST(
                        kwt_rollup.pas09_access1,
                        kwt_rollup.pas09_canesm2,
                        kwt_rollup.pas09_cnrm
                    ),
                    LEAST(
                        kwt_rollup.pas10_access1,
                        kwt_rollup.pas10_canesm2,
                        kwt_rollup.pas10_cnrm
                    ),
                    LEAST(
                        kwt_rollup.pas11_access1,
                        kwt_rollup.pas11_canesm2,
                        kwt_rollup.pas11_cnrm
                    ),
                    LEAST(
                        kwt_rollup.pas12_access1,
                        kwt_rollup.pas12_canesm2,
                        kwt_rollup.pas12_cnrm
                    )
                ]::DOUBLE PRECISION[12] AS pas_monthly_future_min,
                ARRAY[
                    GREATEST(
                        kwt_rollup.ppt01_access1,
                        kwt_rollup.ppt01_canesm2,
                        kwt_rollup.ppt01_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.ppt02_access1,
                        kwt_rollup.ppt02_canesm2,
                        kwt_rollup.ppt02_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.ppt03_access1,
                        kwt_rollup.ppt03_canesm2,
                        kwt_rollup.ppt03_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.ppt04_access1,
                        kwt_rollup.ppt04_canesm2,
                        kwt_rollup.ppt04_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.ppt05_access1,
                        kwt_rollup.ppt05_canesm2,
                        kwt_rollup.ppt05_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.ppt06_access1,
                        kwt_rollup.ppt06_canesm2,
                        kwt_rollup.ppt06_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.ppt07_access1,
                        kwt_rollup.ppt07_canesm2,
                        kwt_rollup.ppt07_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.ppt08_access1,
                        kwt_rollup.ppt08_canesm2,
                        kwt_rollup.ppt08_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.ppt09_access1,
                        kwt_rollup.ppt09_canesm2,
                        kwt_rollup.ppt09_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.ppt10_access1,
                        kwt_rollup.ppt10_canesm2,
                        kwt_rollup.ppt10_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.ppt11_access1,
                        kwt_rollup.ppt11_canesm2,
                        kwt_rollup.ppt11_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.ppt12_access1,
                        kwt_rollup.ppt12_canesm2,
                        kwt_rollup.ppt12_cnrm
                    )
                ]::DOUBLE PRECISION[12] AS ppt_monthly_future_max,
                ARRAY[
                    LEAST(
                        kwt_rollup.ppt01_access1,
                        kwt_rollup.ppt01_canesm2,
                        kwt_rollup.ppt01_cnrm
                    ),
                    LEAST(
                        kwt_rollup.ppt02_access1,
                        kwt_rollup.ppt02_canesm2,
                        kwt_rollup.ppt02_cnrm
                    ),
                    LEAST(
                        kwt_rollup.ppt03_access1,
                        kwt_rollup.ppt03_canesm2,
                        kwt_rollup.ppt03_cnrm
                    ),
                    LEAST(
                        kwt_rollup.ppt04_access1,
                        kwt_rollup.ppt04_canesm2,
                        kwt_rollup.ppt04_cnrm
                    ),
                    LEAST(
                        kwt_rollup.ppt05_access1,
                        kwt_rollup.ppt05_canesm2,
                        kwt_rollup.ppt05_cnrm
                    ),
                    LEAST(
                        kwt_rollup.ppt06_access1,
                        kwt_rollup.ppt06_canesm2,
                        kwt_rollup.ppt06_cnrm
                    ),
                    LEAST(
                        kwt_rollup.ppt07_access1,
                        kwt_rollup.ppt07_canesm2,
                        kwt_rollup.ppt07_cnrm
                    ),
                    LEAST(
                        kwt_rollup.ppt08_access1,
                        kwt_rollup.ppt08_canesm2,
                        kwt_rollup.ppt08_cnrm
                    ),
                    LEAST(
                        kwt_rollup.ppt09_access1,
                        kwt_rollup.ppt09_canesm2,
                        kwt_rollup.ppt09_cnrm
                    ),
                    LEAST(
                        kwt_rollup.ppt10_access1,
                        kwt_rollup.ppt10_canesm2,
                        kwt_rollup.ppt10_cnrm
                    ),
                    LEAST(
                        kwt_rollup.ppt11_access1,
                        kwt_rollup.ppt11_canesm2,
                        kwt_rollup.ppt11_cnrm
                    ),
                    LEAST(
                        kwt_rollup.ppt12_access1,
                        kwt_rollup.ppt12_canesm2,
                        kwt_rollup.ppt12_cnrm
                    )
                ]::DOUBLE PRECISION[12] AS ppt_monthly_future_min,
                ARRAY[
                    GREATEST(
                        kwt_rollup.tave01_access1,
                        kwt_rollup.tave01_canesm2,
                        kwt_rollup.tave01_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.tave02_access1,
                        kwt_rollup.tave02_canesm2,
                        kwt_rollup.tave02_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.tave03_access1,
                        kwt_rollup.tave03_canesm2,
                        kwt_rollup.tave03_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.tave04_access1,
                        kwt_rollup.tave04_canesm2,
                        kwt_rollup.tave04_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.tave05_access1,
                        kwt_rollup.tave05_canesm2,
                        kwt_rollup.tave05_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.tave06_access1,
                        kwt_rollup.tave06_canesm2,
                        kwt_rollup.tave06_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.tave07_access1,
                        kwt_rollup.tave07_canesm2,
                        kwt_rollup.tave07_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.tave08_access1,
                        kwt_rollup.tave08_canesm2,
                        kwt_rollup.tave08_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.tave09_access1,
                        kwt_rollup.tave09_canesm2,
                        kwt_rollup.tave09_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.tave10_access1,
                        kwt_rollup.tave10_canesm2,
                        kwt_rollup.tave10_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.tave11_access1,
                        kwt_rollup.tave11_canesm2,
                        kwt_rollup.tave11_cnrm
                    ),
                    GREATEST(
                        kwt_rollup.tave12_access1,
                        kwt_rollup.tave12_canesm2,
                        kwt_rollup.tave12_cnrm
                    )
                ]::DOUBLE PRECISION[12] AS tave_monthly_future_max,
                ARRAY[
                    LEAST(
                        kwt_rollup.tave01_access1,
                        kwt_rollup.tave01_canesm2,
                        kwt_rollup.tave01_cnrm
                    ),
                    LEAST(
                        kwt_rollup.tave02_access1,
                        kwt_rollup.tave02_canesm2,
                        kwt_rollup.tave02_cnrm
                    ),
                    LEAST(
                        kwt_rollup.tave03_access1,
                        kwt_rollup.tave03_canesm2,
                        kwt_rollup.tave03_cnrm
                    ),
                    LEAST(
                        kwt_rollup.tave04_access1,
                        kwt_rollup.tave04_canesm2,
                        kwt_rollup.tave04_cnrm
                    ),
                    LEAST(
                        kwt_rollup.tave05_access1,
                        kwt_rollup.tave05_canesm2,
                        kwt_rollup.tave05_cnrm
                    ),
                    LEAST(
                        kwt_rollup.tave06_access1,
                        kwt_rollup.tave06_canesm2,
                        kwt_rollup.tave06_cnrm
                    ),
                    LEAST(
                        kwt_rollup.tave07_access1,
                        kwt_rollup.tave07_canesm2,
                        kwt_rollup.tave07_cnrm
                    ),
                    LEAST(
                        kwt_rollup.tave08_access1,
                        kwt_rollup.tave08_canesm2,
                        kwt_rollup.tave08_cnrm
                    ),
                    LEAST(
                        kwt_rollup.tave09_access1,
                        kwt_rollup.tave09_canesm2,
                        kwt_rollup.tave09_cnrm
                    ),
                    LEAST(
                        kwt_rollup.tave10_access1,
                        kwt_rollup.tave10_canesm2,
                        kwt_rollup.tave10_cnrm
                    ),
                    LEAST(
                        kwt_rollup.tave11_access1,
                        kwt_rollup.tave11_canesm2,
                        kwt_rollup.tave11_cnrm
                    ),
                    LEAST(
                        kwt_rollup.tave12_access1,
                        kwt_rollup.tave12_canesm2,
                        kwt_rollup.tave12_cnrm
                    )
                ]::DOUBLE PRECISION[12] AS tave_monthly_future_min,
                kwt_rollup.lcc_shrub AS shrub,
                kwt_rollup.lcc_grassland AS grassland,
                kwt_rollup.lcc_coniferous AS coniferous,
                kwt_rollup.lcc_water AS water,
                kwt_rollup.lcc_snow AS snow,
                kwt_rollup.lcc_developed AS developed,
                kwt_rollup.lcc_wetland AS wetland,
                kwt_rollup.lcc_herb AS herb,
                kwt_rollup.lcc_deciduous AS deciduous,
                kwt_rollup.lcc_mixed AS "mixed",
                kwt_rollup.lcc_barren AS barren,
                kwt_rollup.lcc_cropland AS cropland,
                (kwt_rollup.qyr/1000) * (kwt_rollup.upstream_area / (365.25 * 86400)) AS mad_m3s,
                (kwt_rollup.qyr/1000) * kwt_rollup.upstream_area AS mean_annual_runoff_m3yr,
                ARRAY[
                    ((kwt_rollup.q01/1000) * kwt_rollup.upstream_area)/ (86400 * 31),
                    ((kwt_rollup.q02/1000) * kwt_rollup.upstream_area)/ (86400 * 28),
                    ((kwt_rollup.q03/1000) * kwt_rollup.upstream_area)/ (86400 * 31),
                    ((kwt_rollup.q04/1000) * kwt_rollup.upstream_area)/ (86400 * 30),
                    ((kwt_rollup.q05/1000) * kwt_rollup.upstream_area)/ (86400 * 31),
                    ((kwt_rollup.q06/1000) * kwt_rollup.upstream_area)/ (86400 * 30),
                    ((kwt_rollup.q07/1000) * kwt_rollup.upstream_area)/ (86400 * 31),
                    ((kwt_rollup.q08/1000) * kwt_rollup.upstream_area)/ (86400 * 31),
                    ((kwt_rollup.q09/1000) * kwt_rollup.upstream_area)/ (86400 * 30),
                    ((kwt_rollup.q10/1000) * kwt_rollup.upstream_area)/ (86400 * 31),
                    ((kwt_rollup.q11/1000) * kwt_rollup.upstream_area)/ (86400 * 30),
                    ((kwt_rollup.q12/1000) * kwt_rollup.upstream_area)/ (86400 * 31)
                ] AS mean_monthly_discharge_m3s,
                kwt_rollup.rr,
                kwt_rollup.summer_sensitivity,
                kwt_rollup.winter_sensitivity,
                hypso.elevs AS elevs,
                downstream.x4326 AS mgmt_lng,
                downstream.y4326 AS mgmt_lat,
                downstream.gnis_name AS downstream_gnis_name,
                downstream.area / 1000000 AS downstream_area_km2,
                NULL::smallint AS local_watershed_order) AS _) AS watershed_metadata
    FROM
        kwt.funds_rollups AS kwt_rollup
    JOIN
        kwt.hypso_rollup AS hypso
    USING
        (watershed_feature_id)
    JOIN
        kwt.ws_geoms_all_report downstream
    ON
        (downstream.watershed_feature_id = kwt_rollup.downstream_id)
    JOIN
        (SELECT watershed_feature_id, upstream_geom4326 FROM kwt.ws_geoms_all_report) upstream
    ON
        (kwt_rollup.watershed_feature_id = upstream.watershed_feature_id)
    UNION ALL
    SELECT
        watershed_feature_id,
        owt_rollup.downstream_id,
        (SELECT row_to_json(_) FROM
            (SELECT
                owt_rollup."watershedArea" AS watershed_area_km2,
                owt_rollup.dem400,
                owt_rollup.ppt_mon_hist AS ppt_monthly_hist,
                owt_rollup.tave_mon_hist AS tave_monthly_hist,
                owt_rollup.pas_mon_hist AS pas_monthly_hist,
                owt_rollup.pas_mon_fut_max AS pas_monthly_future_max,
                owt_rollup.pas_mon_fut_min AS pas_monthly_future_min,
                owt_rollup.ppt_mon_fut_max AS ppt_monthly_future_max,
                owt_rollup.ppt_mon_fut_min AS ppt_monthly_future_min,
                owt_rollup.tave_mon_fut_max AS tave_monthly_future_max,
                owt_rollup.tave_mon_fut_min AS tave_monthly_future_min,
                owt_rollup.shrub,
                owt_rollup.grassland,
                owt_rollup.coniferous,
                owt_rollup.water,
                owt_rollup.snow,
                owt_rollup.developed,
                owt_rollup.wetland,
                owt_rollup.herb,
                owt_rollup.deciduous,
                owt_rollup.mixed,
                owt_rollup.barren,
                owt_rollup.cropland,
                owt_rollup.mad_m3s,
                owt_rollup.mad_m3yr AS mean_annual_runoff_m3yr,
                owt_rollup.qmon_m3s AS mean_monthly_discharge_m3s,
                owt_rollup.rr,
                owt_rollup.summer_sensitivity,
                owt_rollup.winter_sensitivity,
                owt_rollup.elevs,
                owt_rollup.mgmt_lng,
                owt_rollup.mgmt_lat,
                owt_rollup.gnis_name AS downstream_gnis_name,
                owt_rollup.downstream_area AS downstream_area_km2,
                owt_rollup.local_watershed_order) AS _) AS watershed_metadata
    FROM owt.funds_rollups_report AS owt_rollup
    UNION ALL
    SELECT
        watershed_feature_id,
        nwwt_rollup.downstream_id,
        (SELECT row_to_json(_) FROM
            (SELECT
                nwwt_rollup."watershedArea" AS watershed_area_km2,
                nwwt_rollup.dem400,
                nwwt_rollup.ppt_mon_hist AS ppt_monthly_hist,
                nwwt_rollup.tave_mon_hist AS tave_monthly_hist,
                nwwt_rollup.pas_mon_hist AS pas_monthly_hist,
                nwwt_rollup.pas_mon_fut_max AS pas_monthly_future_max,
                nwwt_rollup.pas_mon_fut_min AS pas_monthly_future_min,
                nwwt_rollup.ppt_mon_fut_max AS ppt_monthly_future_max,
                nwwt_rollup.ppt_mon_fut_min AS ppt_monthly_future_min,
                nwwt_rollup.tave_mon_fut_max AS tave_monthly_future_max,
                nwwt_rollup.tave_mon_fut_min AS tave_monthly_future_min,
                nwwt_rollup.shrub,
                nwwt_rollup.grassland,
                nwwt_rollup.coniferous,
                nwwt_rollup.water,
                nwwt_rollup.snow,
                nwwt_rollup.developed,
                nwwt_rollup.wetland,
                nwwt_rollup.herb,
                nwwt_rollup.deciduous,
                nwwt_rollup.mixed,
                nwwt_rollup.barren,
                nwwt_rollup.cropland,
                nwwt_rollup.mad_m3s,
                nwwt_rollup.mad_m3yr AS mean_annual_runoff_m3yr,
                nwwt_rollup.qmon_m3s AS mean_monthly_discharge_m3s,
                nwwt_rollup.rr,
                nwwt_rollup.summer_sensitivity,
                nwwt_rollup.winter_sensitivity,
                nwwt_rollup.elevs,
                nwwt_rollup.mgmt_lng,
                nwwt_rollup.mgmt_lat,
                nwwt_rollup.gnis_name AS downstream_gnis_name,
                nwwt_rollup.downstream_area AS downstream_area_km2,
                nwwt_rollup.local_watershed_order) AS _) AS watershed_metadata
    FROM nwwt.funds_rollups_report AS nwwt_rollup
"""


ws_geom_fund_report = """
    SELECT
        watershed_feature_id,
        fwa_watershed_code,
        local_watershed_code,
        ST_AsGeoJSON(ST_Transform(upstream_geom_3857_z12, 4326)) AS upstream_geom_4326_z12,
        area AS area_m2,
        x4326 AS longitude,
        y4326 AS latitude,
        gnis_name,
        ST_NPoints(ST_Transform(upstream_geom, 4326)) AS number_of_points_in_polygon
    FROM cariboo.ws_geoms_all_report
    UNION ALL
    SELECT
        watershed_feature_id,
        fwa_watershed_code,
        local_watershed_code,
        ST_AsGeoJSON(ST_Transform(upstream_geom_3857_z12, 4326)) AS upstream_geom_4326_z12,
        area AS area_m2,
        x4326 AS longitude,
        y4326 AS latitude,
        gnis_name,
        ST_NPoints(upstream_geom4326) AS number_of_points_in_polygon
    FROM kwt.ws_geoms_all_report
    UNION ALL
    SELECT
        watershed_feature_id,
        fwa_watershed_code,
        local_watershed_code,
        ST_AsGeoJSON(ST_Transform(upstream_geom_3857_z12, 4326)) AS upstream_geom_4326_z12,
        area AS area_m2,
        x4326 AS longitude,
        y4326 AS latitude,
        gnis_name,
        st_npoints AS number_of_points_in_polygon
    FROM nwwt.ws_geoms_all_report
    UNION ALL
    SELECT
	watershed_feature_id,
	fwa_watershed_code,
	local_watershed_code,
	ST_AsGeoJSON(ST_Transform(upstream_geom_3857_z12, 4326)) AS upstream_geom_4326_z12,
	area AS area_m2,
	x4326 AS longitude,
	y4326 AS latitude,
	gnis_name,
	st_npoints AS number_of_points_in_polygon
    FROM owt.ws_geoms_all_report
"""

lakes_query = """
    SELECT
        waterbody_poly_id,
        ST_AsGeoJSON(geom4326) AS geom4326,
        gnis_name_1 AS gnis_name,
        area_m2,
        fwa_watershed_code,
        local_watershed_code,
        ST_AsGeoJSON(geom4326_buffer_100) AS geom4326_buffer_100,
        winter_allocs_m3
    FROM owt.lakes
    UNION
    SELECT
        waterbody_poly_id,
        ST_AsGeoJSON(geom4326) AS geom4326,
        gnis_name_1 AS gnis_name,
        area_m2,
        fwa_watershed_code,
        local_watershed_code,
        ST_AsGeoJSON(geom4326_buffer_100) AS geom4326_buffer_100,
        winter_allocs_m3
    FROM kwt.lakes
    UNION
    SELECT
        waterbody_poly_id,
        ST_AsGeoJSON(geom4326) AS geom4326,
        gnis_name_1 AS gnis_name,
        area_m2,
        fwa_watershed_code,
        local_watershed_code,
        ST_AsGeoJSON(geom4326_buffer_100) AS geom4326_buffer_100,
        winter_allocs_m3
    FROM nwwt.lakes
"""

fdc_wsc_station_in_model_query = """
    SELECT
        station_number AS original_id,
        watershed_feature_id,
        area_km AS area_km2,
        station_name,
        excluded,
        exclusion_reason,
        wfi_fake,
        ST_AsGeoJSON(ST_SetSRID(ST_GeomFromGeoJson(geom_geojson4326), 4326)) AS geom4326
    FROM nwwt.fdc_wsc_stations_in_model
    UNION
    SELECT
        station_number AS original_id,
        watershed_feature_id,
        area_km AS area_km2,
        station_name,
        excluded,
        exclusion_reason,
        wfi_fake,
        ST_AsGeoJSON(ST_SetSRID(ST_GeomFromGeoJson(geom_geojson4326), 4326)) AS geom4326
    FROM owt.fdc_wsc_stations_in_model
"""

wsc_station_query = """
    SELECT
        native_id AS original_id,
        station_id AS old_station_id
    FROM
        wet.stations
    WHERE
        network_id IN (1, 3, 8)
"""

kwt_rollups_percentiles_query = """
    SELECT
        watershed_feature_id,
        (SELECT row_to_json(_) FROM
            (SELECT
                kwt_data.nc_p10_m01_06,
                kwt_data.nc_p10_m02_06,
                kwt_data.nc_p10_m03_06,
                kwt_data.nc_p10_m04_06,
                kwt_data.nc_p10_m05_06,
                kwt_data.nc_p10_m06_06,
                kwt_data.nc_p10_m07_06,
                kwt_data.nc_p10_m08_06,
                kwt_data.nc_p10_m09_06,
                kwt_data.nc_p10_m10_06,
                kwt_data.nc_p10_m11_06,
                kwt_data.nc_p10_m12_06,
                kwt_data.nc_p25_m01_06,
                kwt_data.nc_p25_m02_06,
                kwt_data.nc_p25_m03_06,
                kwt_data.nc_p25_m04_06,
                kwt_data.nc_p25_m05_06,
                kwt_data.nc_p25_m06_06,
                kwt_data.nc_p25_m07_06,
                kwt_data.nc_p25_m08_06,
                kwt_data.nc_p25_m09_06,
                kwt_data.nc_p25_m10_06,
                kwt_data.nc_p25_m11_06,
                kwt_data.nc_p25_m12_06,
                kwt_data.nc_p50_m01_06,
                kwt_data.nc_p50_m02_06,
                kwt_data.nc_p50_m03_06,
                kwt_data.nc_p50_m04_06,
                kwt_data.nc_p50_m05_06,
                kwt_data.nc_p50_m06_06,
                kwt_data.nc_p50_m07_06,
                kwt_data.nc_p50_m08_06,
                kwt_data.nc_p50_m09_06,
                kwt_data.nc_p50_m10_06,
                kwt_data.nc_p50_m11_06,
                kwt_data.nc_p50_m12_06,
                kwt_data.nc_p75_m01_06,
                kwt_data.nc_p75_m02_06,
                kwt_data.nc_p75_m03_06,
                kwt_data.nc_p75_m04_06,
                kwt_data.nc_p75_m05_06,
                kwt_data.nc_p75_m06_06,
                kwt_data.nc_p75_m07_06,
                kwt_data.nc_p75_m08_06,
                kwt_data.nc_p75_m09_06,
                kwt_data.nc_p75_m10_06,
                kwt_data.nc_p75_m11_06,
                kwt_data.nc_p75_m12_06,
                kwt_data.nc_p90_m01_06,
                kwt_data.nc_p90_m02_06,
                kwt_data.nc_p90_m03_06,
                kwt_data.nc_p90_m04_06,
                kwt_data.nc_p90_m05_06,
                kwt_data.nc_p90_m06_06,
                kwt_data.nc_p90_m07_06,
                kwt_data.nc_p90_m08_06,
                kwt_data.nc_p90_m09_06,
                kwt_data.nc_p90_m10_06,
                kwt_data.nc_p90_m11_06,
                kwt_data.nc_p90_m12_06,
                kwt_data.nc_p10_m01_20,
                kwt_data.nc_p10_m02_20,
                kwt_data.nc_p10_m03_20,
                kwt_data.nc_p10_m04_20,
                kwt_data.nc_p10_m05_20,
                kwt_data.nc_p10_m06_20,
                kwt_data.nc_p10_m07_20,
                kwt_data.nc_p10_m08_20,
                kwt_data.nc_p10_m09_20,
                kwt_data.nc_p10_m10_20,
                kwt_data.nc_p10_m11_20,
                kwt_data.nc_p10_m12_20,
                kwt_data.nc_p25_m01_20,
                kwt_data.nc_p25_m02_20,
                kwt_data.nc_p25_m03_20,
                kwt_data.nc_p25_m04_20,
                kwt_data.nc_p25_m05_20,
                kwt_data.nc_p25_m06_20,
                kwt_data.nc_p25_m07_20,
                kwt_data.nc_p25_m08_20,
                kwt_data.nc_p25_m09_20,
                kwt_data.nc_p25_m10_20,
                kwt_data.nc_p25_m11_20,
                kwt_data.nc_p25_m12_20,
                kwt_data.nc_p50_m01_20,
                kwt_data.nc_p50_m02_20,
                kwt_data.nc_p50_m03_20,
                kwt_data.nc_p50_m04_20,
                kwt_data.nc_p50_m05_20,
                kwt_data.nc_p50_m06_20,
                kwt_data.nc_p50_m07_20,
                kwt_data.nc_p50_m08_20,
                kwt_data.nc_p50_m09_20,
                kwt_data.nc_p50_m10_20,
                kwt_data.nc_p50_m11_20,
                kwt_data.nc_p50_m12_20,
                kwt_data.nc_p75_m01_20,
                kwt_data.nc_p75_m02_20,
                kwt_data.nc_p75_m03_20,
                kwt_data.nc_p75_m04_20,
                kwt_data.nc_p75_m05_20,
                kwt_data.nc_p75_m06_20,
                kwt_data.nc_p75_m07_20,
                kwt_data.nc_p75_m08_20,
                kwt_data.nc_p75_m09_20,
                kwt_data.nc_p75_m10_20,
                kwt_data.nc_p75_m11_20,
                kwt_data.nc_p75_m12_20,
                kwt_data.nc_p90_m01_20,
                kwt_data.nc_p90_m02_20,
                kwt_data.nc_p90_m03_20,
                kwt_data.nc_p90_m04_20,
                kwt_data.nc_p90_m05_20,
                kwt_data.nc_p90_m06_20,
                kwt_data.nc_p90_m07_20,
                kwt_data.nc_p90_m08_20,
                kwt_data.nc_p90_m09_20,
                kwt_data.nc_p90_m10_20,
                kwt_data.nc_p90_m11_20,
                kwt_data.nc_p90_m12_20,
                kwt_data.nc_p10_m01_50,
                kwt_data.nc_p10_m02_50,
                kwt_data.nc_p10_m03_50,
                kwt_data.nc_p10_m04_50,
                kwt_data.nc_p10_m05_50,
                kwt_data.nc_p10_m06_50,
                kwt_data.nc_p10_m07_50,
                kwt_data.nc_p10_m08_50,
                kwt_data.nc_p10_m09_50,
                kwt_data.nc_p10_m10_50,
                kwt_data.nc_p10_m11_50,
                kwt_data.nc_p10_m12_50,
                kwt_data.nc_p25_m01_50,
                kwt_data.nc_p25_m02_50,
                kwt_data.nc_p25_m03_50,
                kwt_data.nc_p25_m04_50,
                kwt_data.nc_p25_m05_50,
                kwt_data.nc_p25_m06_50,
                kwt_data.nc_p25_m07_50,
                kwt_data.nc_p25_m08_50,
                kwt_data.nc_p25_m09_50,
                kwt_data.nc_p25_m10_50,
                kwt_data.nc_p25_m11_50,
                kwt_data.nc_p25_m12_50,
                kwt_data.nc_p50_m01_50,
                kwt_data.nc_p50_m02_50,
                kwt_data.nc_p50_m03_50,
                kwt_data.nc_p50_m04_50,
                kwt_data.nc_p50_m05_50,
                kwt_data.nc_p50_m06_50,
                kwt_data.nc_p50_m07_50,
                kwt_data.nc_p50_m08_50,
                kwt_data.nc_p50_m09_50,
                kwt_data.nc_p50_m10_50,
                kwt_data.nc_p50_m11_50,
                kwt_data.nc_p50_m12_50,
                kwt_data.nc_p75_m01_50,
                kwt_data.nc_p75_m02_50,
                kwt_data.nc_p75_m03_50,
                kwt_data.nc_p75_m04_50,
                kwt_data.nc_p75_m05_50,
                kwt_data.nc_p75_m06_50,
                kwt_data.nc_p75_m07_50,
                kwt_data.nc_p75_m08_50,
                kwt_data.nc_p75_m09_50,
                kwt_data.nc_p75_m10_50,
                kwt_data.nc_p75_m11_50,
                kwt_data.nc_p75_m12_50,
                kwt_data.nc_p90_m01_50,
                kwt_data.nc_p90_m02_50,
                kwt_data.nc_p90_m03_50,
                kwt_data.nc_p90_m04_50,
                kwt_data.nc_p90_m05_50,
                kwt_data.nc_p90_m06_50,
                kwt_data.nc_p90_m07_50,
                kwt_data.nc_p90_m08_50,
                kwt_data.nc_p90_m09_50,
                kwt_data.nc_p90_m10_50,
                kwt_data.nc_p90_m11_50,
                kwt_data.nc_p90_m12_50,
                kwt_data.nc_p10_m01_80,
                kwt_data.nc_p10_m02_80,
                kwt_data.nc_p10_m03_80,
                kwt_data.nc_p10_m04_80,
                kwt_data.nc_p10_m05_80,
                kwt_data.nc_p10_m06_80,
                kwt_data.nc_p10_m07_80,
                kwt_data.nc_p10_m08_80,
                kwt_data.nc_p10_m09_80,
                kwt_data.nc_p10_m10_80,
                kwt_data.nc_p10_m11_80,
                kwt_data.nc_p10_m12_80,
                kwt_data.nc_p25_m01_80,
                kwt_data.nc_p25_m02_80,
                kwt_data.nc_p25_m03_80,
                kwt_data.nc_p25_m04_80,
                kwt_data.nc_p25_m05_80,
                kwt_data.nc_p25_m06_80,
                kwt_data.nc_p25_m07_80,
                kwt_data.nc_p25_m08_80,
                kwt_data.nc_p25_m09_80,
                kwt_data.nc_p25_m10_80,
                kwt_data.nc_p25_m11_80,
                kwt_data.nc_p25_m12_80,
                kwt_data.nc_p50_m01_80,
                kwt_data.nc_p50_m02_80,
                kwt_data.nc_p50_m03_80,
                kwt_data.nc_p50_m04_80,
                kwt_data.nc_p50_m05_80,
                kwt_data.nc_p50_m06_80,
                kwt_data.nc_p50_m07_80,
                kwt_data.nc_p50_m08_80,
                kwt_data.nc_p50_m09_80,
                kwt_data.nc_p50_m10_80,
                kwt_data.nc_p50_m11_80,
                kwt_data.nc_p50_m12_80,
                kwt_data.nc_p75_m01_80,
                kwt_data.nc_p75_m02_80,
                kwt_data.nc_p75_m03_80,
                kwt_data.nc_p75_m04_80,
                kwt_data.nc_p75_m05_80,
                kwt_data.nc_p75_m06_80,
                kwt_data.nc_p75_m07_80,
                kwt_data.nc_p75_m08_80,
                kwt_data.nc_p75_m09_80,
                kwt_data.nc_p75_m10_80,
                kwt_data.nc_p75_m11_80,
                kwt_data.nc_p75_m12_80,
                kwt_data.nc_p90_m01_80,
                kwt_data.nc_p90_m02_80,
                kwt_data.nc_p90_m03_80,
                kwt_data.nc_p90_m04_80,
                kwt_data.nc_p90_m05_80,
                kwt_data.nc_p90_m06_80,
                kwt_data.nc_p90_m07_80,
                kwt_data.nc_p90_m08_80,
                kwt_data.nc_p90_m09_80,
                kwt_data.nc_p90_m10_80,
                kwt_data.nc_p90_m11_80,
                kwt_data.nc_p90_m12_80) AS _ ) AS hydrological_variability
        FROM kwt.funds_rollups_percentiles AS kwt_data
"""
