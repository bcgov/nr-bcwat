get_climate_station_report_by_id_query = """
  SELECT
    'precipitation' AS source,
    cp.station_id,
    cp.datestamp,
    cp.variable_id,
    v.display_name,
    cp.value,
    cp.qa_id,
    qat.qa_type_name
  FROM
    bcwat_obs.climate_precipitation cp
  JOIN
    bcwat_obs.variable v USING (variable_id)
  JOIN
    bcwat_obs.qa_type qat ON cp.qa_id = qat.qa_type_id
  WHERE
    cp.station_id = %(station_id)s

  UNION ALL

  SELECT
    'temperature' AS source,
    ct.station_id,
    ct.datestamp,
    ct.variable_id,
    v.display_name,
    ct.value,
    ct.qa_id,
    qat.qa_type_name
  FROM
    bcwat_obs.climate_temperature ct
  JOIN
    bcwat_obs.variable v USING (variable_id)
  JOIN
    bcwat_obs.qa_type qat ON ct.qa_id = qat.qa_type_id
  WHERE
    ct.station_id = %(station_id)s

  UNION ALL

  SELECT
    'wind' AS source,
    cw.station_id,
    cw.datestamp,
    cw.variable_id,
    v.display_name,
    cw.value,
    cw.qa_id,
    qat.qa_type_name
  FROM
    bcwat_obs.climate_wind cw
  JOIN
    bcwat_obs.variable v USING (variable_id)
  JOIN
    bcwat_obs.qa_type qat ON cw.qa_id = qat.qa_type_id
  WHERE
    cw.station_id = %(station_id)s

  UNION ALL

  SELECT
    'snow_amount' AS source,
    csa.station_id,
    csa.datestamp,
    csa.variable_id,
    v.display_name,
    csa.value,
    csa.qa_id,
    qat.qa_type_name
  FROM
    bcwat_obs.climate_snow_amount csa
  JOIN
    bcwat_obs.variable v USING (variable_id)
  JOIN
    bcwat_obs.qa_type qat ON csa.qa_id = qat.qa_type_id
  WHERE
    csa.station_id = %(station_id)s

  UNION ALL

  SELECT
    'snow_depth' AS source,
    csd.station_id,
    csd.datestamp,
    csd.variable_id,
    v.display_name,
    csd.value,
    csd.qa_id,
    qat.qa_type_name
  FROM
    bcwat_obs.climate_snow_depth csd
  JOIN
    bcwat_obs.variable v USING (variable_id)
  JOIN
    bcwat_obs.qa_type qat ON csd.qa_id = qat.qa_type_id
  WHERE
    csd.station_id = %(station_id)s

UNION ALL

SELECT
    'swe' AS source,
    cswe.station_id,
    cswe.datestamp,
    cswe.variable_id,
    v.display_name,
    cswe.value,
    cswe.qa_id,
    qat.qa_type_name
FROM
    bcwat_obs.climate_swe cswe
JOIN
    bcwat_obs.variable v USING (variable_id)
JOIN
    bcwat_obs.qa_type qat ON cswe.qa_id = qat.qa_type_id
WHERE
    cswe.station_id = %(station_id)s

UNION ALL

SELECT
    'msp' AS source,
    cmsp.station_id,
    cmsp.datestamp,
    cmsp.variable_id,
    v.display_name,
    cmsp.value,
    cmsp.qa_id,
    qat.qa_type_name
FROM
    bcwat_obs.climate_msp cmsp
JOIN
    bcwat_obs.variable v USING (variable_id)
JOIN
    bcwat_obs.qa_type qat ON cmsp.qa_id = qat.qa_type_id
WHERE
    cmsp.station_id = %(station_id)s

ORDER BY
    datestamp ASC;
"""
