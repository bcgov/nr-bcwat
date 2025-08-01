get_water_quality_station_statistics_query = """
WITH merged AS (
  SELECT
    wqh.datetimestamp,
    wqh.parameter_id
  FROM
    bcwat_obs.water_quality_hourly wqh
  WHERE
    wqh.station_id = %(station_id)s
), count_dates AS(
  SELECT
    COUNT(*) as sample_dates
  FROM
    (SELECT DISTINCT datetimestamp FROM merged)
  AS temp
), count_params AS (
  SELECT
    COUNT(*) as unique_params
  FROM
    (SELECT DISTINCT parameter_id FROM merged)
  AS temp
)
SELECT
  sample_dates,
  unique_params
FROM
  count_dates,
  count_params
"""
