get_surface_water_station_report_by_id_query = """
 SELECT
    wqh.station_id,
    wqh.datetimestamp,
    wqh.value,
    wqh.value_letter,
    wqp.parameter_id,
    wqp.parameter_name,
    wqpg.grouping_id,
    wqpg.grouping_name,
    wqu.unit_id,
    wqu.unit_name
  FROM
    bcwat_obs.water_quality_hourly wqh
  JOIN
    bcwat_obs.water_quality_parameter wqp
  USING
    (parameter_id)
  JOIN
    bcwat_obs.water_quality_parameter_grouping wqpg
  USING
    (grouping_id)
  JOIN
    bcwat_obs.water_quality_unit wqu
  USING
    (unit_id)
  WHERE
    station_id = :station_id
"""

