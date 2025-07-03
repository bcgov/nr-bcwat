get_groundwater_level_station_report_by_id_query = """
    SELECT
      gwl.station_id,
      gwl.datestamp,
      gwl.variable_id,
      v.display_name,
      gwl.value,
      gwl.qa_id,
      qat.qa_type_name
    FROM
      bcwat_obs.ground_water_level gwl
    JOIN
      bcwat_obs.variable v
    USING
      (variable_id)
    JOIN
      bcwat_obs.qa_type qat
    ON
      gwl.qa_id = qat.qa_type_id
    WHERE
      gwl.station_id = %(station_id)s

"""
