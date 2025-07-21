get_watershed_allocations_by_id_query = """
    with a as (
	SELECT
		*,
		row_number() OVER (PARTITION BY lic_type ORDER BY ann_adjust DESC)::int
	FROM
	(
		SELECT
			wls_id,
			licensee,
			rediversion_flag,
			purpose,
			licence_no,
			file_no,
			tpod_tag AS pod,
			branding_organization AS organization,
			lic_status_date,
			priority_date,
			expiry_date,
			stream_name,
			water_source_type_desc AS sourcetype,
			ROUND(latitude::NUMERIC, 5)::DECIMAL AS lat,
			ROUND(longitude::NUMERIC, 5)::DECIMAL AS lng,
			flag_desc,
			qty_flag,
			lic_status,
			CASE
				WHEN ann_adjust IS NULL THEN 0
				ELSE ann_adjust
			END AS ann_adjust,
			well_tag_number,
			licence_term,
			hydraulic_connectivity,
			is_consumptive,
			purpose_groups,
			water_allocation_type,
			CASE
				WHEN lic_status = 'CURRENT' AND licence_term = 'long' THEN concat(lower(water_allocation_type), '-lic')
				WHEN lic_status = 'CURRENT' AND licence_term = 'short' THEN concat(lower(water_allocation_type), '-stu')
				WHEN lic_status = 'ACTIVE APPL.' AND licence_term = 'long' THEN concat(lower(water_allocation_type), '-app')
			END AS lic_type,
			CASE
				WHEN water_allocation_type = 'SW' THEN
					CASE
						WHEN lic_status = 'CURRENT' AND licence_term = 'long' THEN 'Surface Water Long Term Licence'
						WHEN lic_status = 'CURRENT' AND licence_term = 'short' THEN 'Surface Water Short Term Use Approval'
						WHEN lic_status = 'ACTIVE APPL.' AND licence_term = 'long' THEN 'Surface Water Long Term Application'
					END
				when water_allocation_type = 'GW' THEN
					CASE
						WHEN lic_status = 'CURRENT' AND licence_term = 'long' THEN 'Groundwater Long Term Licence'
						WHEN lic_status = 'CURRENT' AND licence_term = 'short' THEN 'Groundwater Short Term Use Approval'
						WHEN lic_status = 'ACTIVE APPL.' AND licence_term = 'long' THEN 'Groundwater Long Term Application'
					END
			END AS lic_type_tt,
			quantity_day_m3::numeric,
			quantity_sec_m3::numeric
		FROM
			bcwat_lic.licence_wls_map
		JOIN
			(
				SELECT
					upstream_geom_4326_z12
				FROM
					bcwat_ws.ws_geom_all_report
				WHERE
					watershed_feature_id = %(watershed_feature_id)s
			) g
		ON
			ST_Intersects(g.upstream_geom_4326_z12, geom4326)
	) f
)
SELECT
	a.wls_id,
	a.licensee,
	a.rediversion_flag,
	a.purpose,
	a.licence_no,
	a.file_no,
	a.pod,
	a.organization,
	a.lic_status_date,
	a.lic_status_date,
	a.priority_date,
	a.expiry_date,
	a.stream_name,
	a.sourcetype,
	a.lat,
	a.lng,
	a.flag_desc,
	CASE
		WHEN (b.wls_id IS NULL) OR (NOT a.is_consumptive) OR (a.licence_term = 'long' AND a.water_allocation_type = 'GW') or (a.lic_status = 'ACTIVE APPL.')THEN
			CASE
				WHEN a.qty_flag IS NULL THEN
					CASE
						WHEN a.rediversion_flag = 'Y' THEN concat(a.qty_flag, 'R, N')
						ELSE concat(a.qty_flag, 'N')
					END
				ELSE
					CASE
						WHEN a.rediversion_flag = 'Y' THEN concat(a.qty_flag, ', R, N')
						ELSE concat(a.qty_flag, ', N')
					END
			END
		ELSE a.qty_flag
	END AS qty_flag,
	a.lic_status,
	CASE
		WHEN b.wls_id IS null THEN 0
		ELSE b.ann_adjust
	END AS ann_adjust,
	a.well_tag_number,
	a.licence_term,
	a.hydraulic_connectivity,
	a.is_consumptive,
	a.purpose_groups,
	a.water_allocation_type,
	a.lic_type,
	a.lic_type_tt,
	a.row_number,
	a.quantity_day_m3,
	a.quantity_sec_m3
FROM
	a
LEFT JOIN
	(
	(
		SELECT
			DISTINCT ON (licence_no, purpose, qty_flag)
			wls_id,
			licensee,
			rediversion_flag,
			purpose,
			licence_no,
			file_no,
			pod,
			organization,
			lic_status_date,
			lic_status_date,
			priority_date,
			expiry_date,
			stream_name,
			sourcetype,
			lat,
			lng,
			flag_desc,
			qty_flag,
			lic_status,
			ann_adjust,
			well_tag_number,
			licence_term,
			hydraulic_connectivity,
			is_consumptive,
			purpose_groups,
			water_allocation_type,
			lic_type,
			lic_type_tt,
			row_number,
			quantity_day_m3,
			quantity_sec_m3
	FROM
		a
	WHERE
		qty_flag = 'M'
	ORDER BY
		licence_no, purpose, qty_flag, water_allocation_type desc, ann_adjust desc)
	UNION ALL
		SELECT
			wls_id,
			licensee,
			rediversion_flag,
			purpose,
			licence_no,
			file_no,
			pod,
			organization,
			lic_status_date,
			lic_status_date,
			priority_date,
			expiry_date,
			stream_name,
			sourcetype,
			lat,
			lng,
			flag_desc,
			qty_flag,
			lic_status,
			ann_adjust,
			well_tag_number,
			licence_term,
			hydraulic_connectivity,
			is_consumptive,
			purpose_groups,
			water_allocation_type,
			lic_type,
			lic_type_tt,
			row_number,
			quantity_day_m3,
			quantity_sec_m3
	FROM
		a
	WHERE
		qty_flag != 'M' or qty_flag is null
	) b
USING (wls_id)
ORDER BY
	priority_date,
	licence_no,
	purpose,
	ann_adjust DESC,
	pod;
"""
