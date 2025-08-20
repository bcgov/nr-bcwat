get_place_by_name_query = """
SELECT
	geoname,
	ST_X(ST_Transform(ST_Point(x, y, 3857), 4326)) AS longitude,
	ST_Y(ST_Transform(ST_Point(x, y, 3857), 4326)) AS latitude,
	zoom
FROM
	bcwat_ws.mapsearch2
WHERE
	geoname ILIKE %(location_name)s
AND
	ST_Contains(
		(SELECT
        	geom4326
        FROM
			bcwat_lic.water_licence_coverage
        ),
        ST_Transform(ST_Point(x, y, 3857), 4326)
    )
ORDER BY geoname
LIMIT 10;
"""
