UPDATE
	bcwat_obs.station
SET
	station_status_id = 1
WHERE
	station_id IN (
	SELECT
		DISTINCT station_id
	FROM
		bcwat_obs.station_year
	WHERE
		station_id IN (
			SELECT
				station_id
			FROM
				bcwat_obs.station
			WHERE
				station_status_id = 5
			OR
				station_status_id IS NULL
		)
	);
