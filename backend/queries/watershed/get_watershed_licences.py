get_watershed_licences_query = """
  SELECT
    jsonb_build_object(
      'features', jsonb_agg(
        jsonb_build_object(
        'type', 'Feature',
        'properties', jsonb_build_object(
          'id', wls_id,
          'net', branding_organization,
          'lic', licensee,
          'nid', licence_no,
          'qty', ann_adjust,
          'ind', industry_activity,
          'st', lic_status,
          'type', water_allocation_type,
          'org', purpose,
          'purpose_groups', purpose_groups,
		      'term', licence_term
        ),
        'geometry', jsonb_build_object(
          'type', 'Point',
          'coordinates', jsonb_build_array(longitude, latitude)
        )
      )
    )
    ) AS geojson
  FROM
    bcwat_lic.licence_wls_map
"""
