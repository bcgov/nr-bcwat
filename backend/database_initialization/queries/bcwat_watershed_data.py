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
