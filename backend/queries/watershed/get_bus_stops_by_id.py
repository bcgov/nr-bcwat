get_bus_stops_query = """
    WITH RECURSIVE upstream_watersheds AS (
        -- Step 1: Get initial watershed code for the given feature ID
        SELECT
            fsnu.fwa_watershed_code,
            fsnu.gnis_name,
            string_to_array(fsnu.fwa_watershed_code, '-') AS segments,
            1 AS level
        FROM
            bcwat_ws.fwa_stream_name_unique fsnu
        JOIN
            bcwat_ws.ws_geom_all_report wgar USING (fwa_watershed_code)
        WHERE
            wgar.watershed_feature_id = %(wfi)s

        UNION ALL

        -- Step 2: Recursively zero out the last non-zero segment AND everything after
        SELECT
            fsnu.fwa_watershed_code,
            fsnu.gnis_name,
            new_segments,
            u.level + 1
        FROM
            upstream_watersheds u
        JOIN LATERAL (
            SELECT
                max(i) AS last_nonzero_index
            FROM generate_subscripts(u.segments, 1) AS i
            WHERE u.segments[i] != '000000'
        ) idx ON true
        JOIN LATERAL (
            SELECT ARRAY(
                SELECT CASE
                    WHEN i <= idx.last_nonzero_index - 1 THEN u.segments[i]
                    ELSE '000000'
                END
                FROM generate_subscripts(u.segments, 1) AS i
            ) AS new_segments
        ) segs ON true
        JOIN
            bcwat_ws.fwa_stream_name_unique fsnu
        ON
            fsnu.fwa_watershed_code = array_to_string(segs.new_segments, '-')
        WHERE
            u.fwa_watershed_code != array_to_string(segs.new_segments, '-')
        AND
            u.level < 20
    )

    SELECT
        level,
        COALESCE(gnis_name, 'Unnamed Basin') AS name,
        fwa_watershed_code
    FROM
        upstream_watersheds
    ORDER BY level;
"""
