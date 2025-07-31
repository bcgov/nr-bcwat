get_water_quality_station_statistics_query = """
SELECT
	COUNT(DISTINCT wqh.datetimestamp) AS sample_dates,
	COUNT(DISTINCT wqh.parameter_id) AS unique_params
FROM
  bcwat_obs.water_quality_hourly wqh
WHERE
  wqh.station_id = %(station_id)s
"""
