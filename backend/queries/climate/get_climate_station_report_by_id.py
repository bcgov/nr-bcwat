get_climate_station_report_by_id_query = """
  SELECT
    'precipitation' AS source,
    cp.station_id,
    cp.datestamp,
    cp.variable_id,
    cp.value,
	  NULL::date as survey_period
  FROM
    bcwat_obs.climate_precipitation cp
  WHERE
    cp.station_id = %(station_id)s

  UNION ALL

  SELECT
    'temperature' AS source,
    ct.station_id,
    ct.datestamp,
    ct.variable_id,
    ct.value,
	  NULL::date as survey_period
  FROM
    bcwat_obs.climate_temperature ct
  WHERE
    ct.station_id = %(station_id)s

  UNION ALL

  SELECT
    'snow_amount' AS source,
    csa.station_id,
    csa.datestamp,
    csa.variable_id,
    csa.value,
	  NULL::date as survey_period
  FROM
    bcwat_obs.climate_snow_amount csa
  WHERE
    csa.station_id = %(station_id)s

  UNION ALL

  SELECT
    'snow_depth' AS source,
    csd.station_id,
    csd.datestamp,
    csd.variable_id,
    csd.value,
	  NULL::date as survey_period
  FROM
    bcwat_obs.climate_snow_depth csd
  WHERE
    csd.station_id = %(station_id)s

UNION ALL

SELECT
    'swe' AS source,
    cswe.station_id,
    cswe.datestamp,
    cswe.variable_id,
    cswe.value,
	  NULL::date as survey_period
FROM
    bcwat_obs.climate_swe cswe
WHERE
    cswe.station_id = %(station_id)s

UNION ALL

SELECT
    'msp' AS source,
    cmsp.station_id,
    cmsp.datestamp,
    cmsp.variable_id,
    cmsp.value,
	  cmsp.survey_period
FROM
    bcwat_obs.climate_msp cmsp
WHERE
    cmsp.station_id = %(station_id)s

ORDER BY
    datestamp ASC;
"""
