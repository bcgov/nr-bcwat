get_watershed_region_by_id_query = """
    SELECT
        region_id
    FROM
        (
            SELECT
                region_id
            FROM
                bcwat_obs.region
            WHERE
                ST_Intersects(
                    region_click_studyarea,
                    (
                        SELECT
                            geom4326
                        FROM
                            bcwat_ws.fwa_fund
                        WHERE
                            watershed_feature_id = :watershed_feature_id
                    )
                )
            AND
                region_id IN (3,4,5,6)
            ORDER BY
                region_id
            LIMIT 1
        ) AS region
"""
