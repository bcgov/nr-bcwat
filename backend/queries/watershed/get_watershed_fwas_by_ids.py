get_watershed_fwas_by_ids_query = """
    SELECT
        COALESCE(gnis_name, 'Unnamed Basin') AS name,
        fwa_watershed_code
    FROM
        bcwat_ws.fwa_stream_name_unique
    WHERE
        fwa_watershed_code = ANY(ARRAY[%(fwa_watershed_codes)s])
    ORDER BY
        fwa_watershed_code DESC;
   """
