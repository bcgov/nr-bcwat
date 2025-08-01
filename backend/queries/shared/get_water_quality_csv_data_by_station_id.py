get_water_quality_station_csv_by_id_query = """
 SELECT
    wqh.datetimestamp,
    wqh.value_text::text,
    wqh.location_purpose,
    wqh.sampling_agency,
    wqh.analyzing_agency,
    wqh.collection_method,
    wqh.sample_state,
    wqh.sample_descriptor,
    wqh.analytical_method,
    wqh.qa_id,
    wqp.parameter_id,
    wqp.parameter_name
  FROM
    bcwat_obs.water_quality_hourly wqh
  JOIN
    bcwat_obs.water_quality_parameter wqp
  USING
    (parameter_id)
  WHERE
    station_id = :station_id
"""
