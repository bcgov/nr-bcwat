post_import_query = '''

ALTER TABLE IF EXISTS "bcwat_obs"."station" DROP COLUMN IF EXISTS "old_station_id";

-- TRIGGERS --
    CREATE OR REPLACE FUNCTION bcwat_obs.fill_geom_point() RETURNS TRIGGER AS $$
    BEGIN
        IF NEW."longitude" IS NULL OR NEW."latitude" IS NULL THEN
            NEW."geom4326" := NULL;
            RETURN NEW;
        ELSE
            NEW."geom4326" := ST_Point(NEW."longitude", NEW."latitude", 4326);
            RETURN NEW;
        END IF;
    END $$ LANGUAGE plpgsql;

    CREATE OR REPLACE TRIGGER "station_populate_geom4326" BEFORE INSERT ON bcwat_obs.station FOR EACH ROW EXECUTE FUNCTION bcwat_obs.fill_geom_point();

    CREATE OR REPLACE FUNCTION bcwat_obs.insert_station_region() RETURNS TRIGGER AS $$
    BEGIN
        INSERT INTO bcwat_obs.station_region
            SELECT
                NEW.station_id,
                region_id
            FROM
                bcwat_obs.region
            WHERE
                ST_WITHIN(ST_Point(NEW."longitude", NEW."latitude", 4326), region_click_studyarea)
        ON CONFLICT (station_id, region_id) DO NOTHING;

        INSERT INTO bcwat_obs.station_project_id
            SELECT
                NEW.station_id,
                project_id
            FROM
                bcwat_obs.project_id
            WHERE
                ST_WITHIN(ST_Point(NEW."longitude", NEW."latitude", 4326), project_geom4326)
            ON CONFLICT (station_id, project_id) DO NOTHING;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    CREATE OR REPLACE TRIGGER "station_populate_station_region" AFTER INSERT ON bcwat_obs.station FOR EACH ROW EXECUTE FUNCTION bcwat_obs.insert_station_region();

-- OTHER --
    INSERT INTO bcwat_obs.bc_boundary
        SELECT
            1 AS gid,
            ST_Union(
                ST_Union(
                    ST_Union(
                        ST_Union(
                            ST_Intersection((SELECT region_click_studyarea FROM bcwat_obs.region WHERE region_id = 4),(SELECT region_click_studyarea FROM bcwat_obs.region WHERE region_id = 2)),
                            (SELECT region_click_studyarea FROM bcwat_obs.region WHERE region_id = 4)
                        ),
                        (SELECT region_click_studyarea FROM bcwat_obs.region WHERE region_id = 1)
                    ),
                    ST_Buffer((SELECT region_click_studyarea FROM bcwat_obs.region WHERE region_id = 3), 0.01)
                ),
                ST_Buffer((SELECT region_click_studyarea FROM bcwat_obs.region WHERE region_id = 5), 0.0015)
            ) AS geom4326;

-- SET SEQUENCES TO CORRECT VALUE --
    SELECT
	    setval('bcwat_obs.water_quality_unit_unit_id_seq', (SELECT MAX(unit_id) FROM bcwat_obs.water_quality_unit));

    SELECT
        setval('bcwat_obs.water_quality_parameter_parameter_id_seq', (SELECT MAX(parameter_id) FROM bcwat_obs.water_quality_parameter));

    SELECT
        setval('bcwat_obs.water_quality_parameter_grouping_grouping_id_seq', (SELECT MAX(grouping_id) FROM bcwat_obs.water_quality_parameter_grouping));

    SELECT
        setval('bcwat_obs.variable_variable_id_seq', (SELECT MAX(variable_id) FROM bcwat_obs.variable));

    SELECT
        setval('bcwat_obs.station_type_type_id_seq', (SELECT MAX(type_id) FROM bcwat_obs.station_type));

    SELECT
        setval('bcwat_obs.station_status_status_id_seq', (SELECT MAX(status_id) FROM bcwat_obs.station_status));

    SELECT
        setval('bcwat_obs.region_region_id_seq', (SELECT MAX(region_id) FROM bcwat_obs.region));

    SELECT
        setval('bcwat_obs.operation_operation_id_seq', (SELECT MAX(operation_id) FROM bcwat_obs.operation));

    SELECT
        setval('bcwat_obs.network_network_id_seq', (SELECT MAX(network_id) FROM bcwat_obs.network));

-- INDICES --

    CREATE INDEX IF NOT EXISTS fwa_stream_name_geom4326_idx
        ON bcwat_ws.fwa_stream_name USING gist
        (geom4326);

    CREATE INDEX IF NOT EXISTS fwa_funds_geom4326_idx
        ON bcwat_ws.fwa_fund USING gist
        (geom4326);

    CREATE INDEX IF NOT EXISTS sation_observation_composit_idx
        ON bcwat_obs.station_observation
        USING btree (station_id, variable_id)
		INCLUDE (value, datestamp);

-- FUNCTIONS --
CREATE OR REPLACE FUNCTION bcwat_lic.get_allocs_per_wfi(
	in_wfi integer,
	in_table_name text DEFAULT 'bcwat_lic.licence_wls_map'::text,
	OUT wls_id text,
	OUT licensee text,
	OUT rediversion_flag character varying,
	OUT purpose character varying,
	OUT licence_no character varying,
	OUT file_no character varying,
	OUT pod character varying,
	OUT organization text,
	OUT lic_status_date date,
	OUT start_date date,
	OUT priority_date date,
	OUT expiry_date date,
	OUT stream_name character varying,
	OUT sourcetype text,
	OUT lat numeric,
	OUT lng numeric,
	OUT flag_desc character varying,
	OUT qty_flag character varying,
	OUT lic_status character varying,
	OUT ann_adjust double precision,
	OUT old_ann_adjust double precision,
	OUT well_tag_number integer,
	OUT industry_activity text,
	OUT licence_term text,
	OUT hydraulic_connectivity character varying,
	OUT is_consumptive boolean,
	OUT purpose_groups text,
	OUT water_allocation_type text,
	OUT lic_type text,
	OUT lic_type_tt text,
	OUT puc_groupings_storage text,
	OUT row_number integer,
	OUT quantity_day_m3 numeric,
	OUT quantity_sec_m3 numeric)
    RETURNS SETOF record
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 10000

AS $BODY$
		BEGIN
		IF in_table_name = 'bcwat_lic.licence_wls_map' THEN
			RETURN QUERY EXECUTE format('
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
								start_date,
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
								CASE
									WHEN old_ann_adjust IS NULL THEN 0
									ELSE old_ann_adjust
								END AS old_ann_adjust,
								well_tag_number,
								industry_activity,
								licence_term,
								hydraulic_connectivity,
								is_consumptive,
								purpose_groups,
								water_allocation_type,
								CASE
									WHEN lic_status = ''CURRENT'' AND licence_term = ''long'' THEN concat(lower(water_allocation_type), ''-lic'')
									WHEN lic_status = ''CURRENT'' AND licence_term = ''short'' THEN concat(lower(water_allocation_type), ''-stu'')
									WHEN lic_status = ''ACTIVE APPL.'' AND licence_term = ''long'' THEN concat(lower(water_allocation_type), ''-app'')
								END AS lic_type,
								CASE
									WHEN water_allocation_type = ''SW'' THEN
										CASE
											WHEN lic_status = ''CURRENT'' AND licence_term = ''long'' THEN ''Surface Water Long Term Licence''
											WHEN lic_status = ''CURRENT'' AND licence_term = ''short'' THEN ''Surface Water Short Term Use Approval''
											WHEN lic_status = ''ACTIVE APPL.'' AND licence_term = ''long'' THEN ''Surface Water Long Term Application''
										END
									when water_allocation_type = ''GW'' THEN
										CASE
											WHEN lic_status = ''CURRENT'' AND licence_term = ''long'' THEN ''Groundwater Long Term Licence''
											WHEN lic_status = ''CURRENT'' AND licence_term = ''short'' THEN ''Groundwater Short Term Use Approval''
											WHEN lic_status = ''ACTIVE APPL.'' AND licence_term = ''long'' THEN ''Groundwater Long Term Application''
										END
								END AS lic_type_tt,
								puc_groupings_storage,
								quantity_day_m3::numeric,
								quantity_sec_m3::numeric
							FROM
								%s
							JOIN
								(
									SELECT
										upstream_geom_4326_z12
									FROM
										bcwat_ws.ws_geom_all_report
									WHERE
										watershed_feature_id = %s
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
						a.start_date,
						a.priority_date,
						a.expiry_date,
						a.stream_name,
						a.sourcetype,
						a.lat,
						a.lng,
						a.flag_desc,
						CASE
							WHEN (b.wls_id IS NULL) OR (NOT a.is_consumptive) OR (a.licence_term = ''long'' AND a.water_allocation_type = ''GW'') or (a.lic_status = ''ACTIVE APPL.'')THEN
								CASE
									WHEN a.qty_flag IS NULL THEN
										CASE
											WHEN a.rediversion_flag = ''Y'' THEN concat(a.qty_flag, ''R, N'')
											ELSE concat(a.qty_flag, ''N'')
										END
									ELSE
										CASE
											WHEN a.rediversion_flag = ''Y'' THEN concat(a.qty_flag, '', R, N'')
											ELSE concat(a.qty_flag, '', N'')
										END
								END
							ELSE a.qty_flag
						END AS qty_flag,
						a.lic_status,
						CASE
							WHEN b.wls_id IS null THEN 0
							ELSE b.ann_adjust
						END AS ann_adjust,
						CASE
							WHEN b.wls_id IS null THEN 0
							ELSE b.old_ann_adjust
						END AS old_ann_adjust,
						a.well_tag_number,
						a.industry_activity,
						a.licence_term,
						a.hydraulic_connectivity,
						a.is_consumptive,
						a.purpose_groups,
						a.water_allocation_type,
						a.lic_type,
						a.lic_type_tt,
						a.puc_groupings_storage,
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
								start_date,
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
								old_ann_adjust,
								well_tag_number,
								industry_activity,
								licence_term,
								hydraulic_connectivity,
								is_consumptive,
								purpose_groups,
								water_allocation_type,
								lic_type,
								lic_type_tt,
								puc_groupings_storage,
								row_number,
								quantity_day_m3,
								quantity_sec_m3
						FROM
							a
						WHERE
							qty_flag = ''M''
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
								start_date,
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
								old_ann_adjust,
								well_tag_number,
								industry_activity,
								licence_term,
								hydraulic_connectivity,
								is_consumptive,
								purpose_groups,
								water_allocation_type,
								lic_type,
								lic_type_tt,
								puc_groupings_storage,
								row_number,
								quantity_day_m3,
								quantity_sec_m3
						FROM
							a
						WHERE
							qty_flag != ''M'' or qty_flag is null
						) b
					USING (wls_id)
					ORDER BY
						priority_date,
						licence_no,
						purpose,
						ann_adjust DESC,
						pod;',
					(in_table_name),
					(in_wfi)
					);
		ELSIF in_table_name = 'bcwat_ws.lakes' THEN
			RETURN QUERY EXECUTE format('
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
							start_date,
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
							CASE
								WHEN old_ann_adjust IS NULL THEN 0
								ELSE old_ann_adjust
							END AS old_ann_adjust,
							well_tag_number,
							industry_activity,
							licence_term,
							hydraulic_connectivity,
							is_consumptive,
							purpose_groups,
							water_allocation_type,
							CASE
								WHEN lic_status = ''CURRENT'' AND licence_term = ''long'' THEN concat(lower(water_allocation_type), ''-lic'')
								WHEN lic_status = ''CURRENT'' AND licence_term = ''short'' THEN concat(lower(water_allocation_type), ''-stu'')
								WHEN lic_status = ''ACTIVE APPL.'' AND licence_term = ''long'' THEN concat(lower(water_allocation_type), ''-app'')
							END AS lic_type,
							CASE
								WHEN water_allocation_type = ''SW'' THEN
									CASE
										WHEN lic_status = ''CURRENT'' AND licence_term = ''long'' THEN ''Surface Water Long Term Licence''
										WHEN lic_status = ''CURRENT'' AND licence_term = ''short'' THEN ''Surface Water Short Term Use Approval''
										WHEN lic_status = ''ACTIVE APPL.'' AND licence_term = ''long'' THEN ''Surface Water Long Term Application''
									END
								when water_allocation_type = ''GW'' THEN
									CASE
										WHEN lic_status = ''CURRENT'' AND licence_term = ''long'' THEN ''Groundwater Long Term Licence''
										WHEN lic_status = ''CURRENT'' AND licence_term = ''short'' THEN ''Groundwater Short Term Use Approval''
										WHEN lic_status = ''ACTIVE APPL.'' AND licence_term = ''long'' THEN ''Groundwater Long Term Application''
									END
							END AS lic_type_tt,
							puc_groupings_storage,
							quantity_day_m3::numeric,
							quantity_sec_m3::numeric
						FROM
							bcwat_lic.licence_wls_map
						JOIN
							(
								SELECT
									geom4326_buffer_100 as upstream_geom4326
								FROM
									%s
								WHERE
									waterbody_poly_id = %s
							) g
						ON
							ST_Intersects(g.upstream_geom4326, geom4326)
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
					a.start_date,
					a.priority_date,
					a.expiry_date,
					a.stream_name,
					a.sourcetype,
					a.lat,
					a.lng,
					a.flag_desc,
					CASE
						WHEN (b.wls_id IS NULL) OR (NOT a.is_consumptive) OR (a.licence_term = ''long'' AND a.water_allocation_type = ''GW'') or (a.lic_status = ''ACTIVE APPL.'')THEN
							CASE
								WHEN a.qty_flag IS NULL THEN
									CASE
										WHEN a.rediversion_flag = ''Y'' THEN concat(a.qty_flag, ''R, N'')
										ELSE concat(a.qty_flag, ''N'')
									END
								ELSE
									CASE
										WHEN a.rediversion_flag = ''Y'' THEN concat(a.qty_flag, '', R, N'')
										ELSE concat(a.qty_flag, '', N'')
									END
							END
						ELSE a.qty_flag
					END AS qty_flag,
					a.lic_status,
					CASE
						WHEN b.wls_id IS null THEN 0
						ELSE b.ann_adjust
					END AS ann_adjust,
					CASE
						WHEN b.wls_id IS null THEN 0
						ELSE b.old_ann_adjust
					END AS old_ann_adjust,
					a.well_tag_number,
					a.industry_activity,
					a.licence_term,
					a.hydraulic_connectivity,
					a.is_consumptive,
					a.purpose_groups,
					a.water_allocation_type,
					a.lic_type,
					a.lic_type_tt,
					a.puc_groupings_storage,
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
							start_date,
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
							old_ann_adjust,
							well_tag_number,
							industry_activity,
							licence_term,
							hydraulic_connectivity,
							is_consumptive,
							purpose_groups,
							water_allocation_type,
							lic_type,
							lic_type_tt,
							puc_groupings_storage,
							row_number,
							quantity_day_m3,
							quantity_sec_m3
					FROM
						a
					WHERE
						qty_flag = ''M''
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
							start_date,
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
							old_ann_adjust,
							well_tag_number,
							industry_activity,
							licence_term,
							hydraulic_connectivity,
							is_consumptive,
							purpose_groups,
							water_allocation_type,
							lic_type,
							lic_type_tt,
							puc_groupings_storage,
							row_number,
							quantity_day_m3,
							quantity_sec_m3
					FROM
						a
					WHERE
						qty_flag != ''M'' or qty_flag is null
					) b
				USING (wls_id)
				ORDER BY
					priority_date,
					licence_no,
					purpose,
					ann_adjust DESC,
					pod;',
				(in_table_name),
				(in_wfi)
				);
		ELSIF in_table_name != 'bcwat_lic.licence_wls_map' THEN
			RETURN QUERY EXECUTE format('
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
							start_date,
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
							CASE
								WHEN old_ann_adjust IS NULL THEN 0
								ELSE old_ann_adjust
							END AS old_ann_adjust,
							well_tag_number,
							industry_activity,
							licence_term,
							hydraulic_connectivity,
							is_consumptive,
							purpose_groups,
							water_allocation_type,
							CASE
								WHEN lic_status = ''CURRENT'' AND licence_term = ''long'' THEN concat(lower(water_allocation_type), ''-lic'')
								WHEN lic_status = ''CURRENT'' AND licence_term = ''short'' THEN concat(lower(water_allocation_type), ''-stu'')
								WHEN lic_status = ''ACTIVE APPL.'' AND licence_term = ''long'' THEN concat(lower(water_allocation_type), ''-app'')
							END AS lic_type,
							CASE
								WHEN water_allocation_type = ''SW'' THEN
									CASE
										WHEN lic_status = ''CURRENT'' AND licence_term = ''long'' THEN ''Surface Water Long Term Licence''
										WHEN lic_status = ''CURRENT'' AND licence_term = ''short'' THEN ''Surface Water Short Term Use Approval''
										WHEN lic_status = ''ACTIVE APPL.'' AND licence_term = ''long'' THEN ''Surface Water Long Term Application''
									END
								when water_allocation_type = ''GW'' THEN
									CASE
										WHEN lic_status = ''CURRENT'' AND licence_term = ''long'' THEN ''Groundwater Long Term Licence''
										WHEN lic_status = ''CURRENT'' AND licence_term = ''short'' THEN ''Groundwater Short Term Use Approval''
										WHEN lic_status = ''ACTIVE APPL.'' AND licence_term = ''long'' THEN ''Groundwater Long Term Application''
									END
							END AS lic_type_tt,
							puc_groupings_storage,
							quantity_day_m3::numeric,
							quantity_sec_m3::numeric
						FROM
							%s
						JOIN
							(
								SELECT
									upstream_geom_4326_z12
								FROM
									bcwat_ws.ws_geom_all_report
								WHERE
									watershed_feature_id = %s
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
					a.start_date,
					a.priority_date,
					a.expiry_date,
					a.stream_name,
					a.sourcetype,
					a.lat,
					a.lng,
					a.flag_desc,
					CASE
						WHEN (b.wls_id IS NULL) OR (NOT a.is_consumptive) OR (a.licence_term = ''long'' AND a.water_allocation_type = ''GW'') or (a.lic_status = ''ACTIVE APPL.'')THEN
							CASE
								WHEN a.qty_flag IS NULL THEN
									CASE
										WHEN a.rediversion_flag = ''Y'' THEN concat(a.qty_flag, ''R, N'')
										ELSE concat(a.qty_flag, ''N'')
									END
								ELSE
									CASE
										WHEN a.rediversion_flag = ''Y'' THEN concat(a.qty_flag, '', R, N'')
										ELSE concat(a.qty_flag, '', N'')
									END
							END
						ELSE a.qty_flag
					END AS qty_flag,
					a.lic_status,
					CASE
						WHEN b.wls_id IS null THEN 0
						ELSE b.ann_adjust
					END AS ann_adjust,
					CASE
						WHEN b.wls_id IS null THEN 0
						ELSE b.old_ann_adjust
					END AS old_ann_adjust,
					a.well_tag_number,
					a.industry_activity,
					a.licence_term,
					a.hydraulic_connectivity,
					a.is_consumptive,
					a.purpose_groups,
					a.water_allocation_type,
					a.lic_type,
					a.lic_type_tt,
					a.puc_groupings_storage,
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
							start_date,
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
							old_ann_adjust,
							well_tag_number,
							industry_activity,
							licence_term,
							hydraulic_connectivity,
							is_consumptive,
							purpose_groups,
							water_allocation_type,
							lic_type,
							lic_type_tt,
							puc_groupings_storage,
							row_number,
							quantity_day_m3,
							quantity_sec_m3
					FROM
						a
					WHERE
						qty_flag = ''M''
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
							start_date,
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
							old_ann_adjust,
							well_tag_number,
							industry_activity,
							licence_term,
							hydraulic_connectivity,
							is_consumptive,
							purpose_groups,
							water_allocation_type,
							lic_type,
							lic_type_tt,
							puc_groupings_storage,
							row_number,
							quantity_day_m3,
							quantity_sec_m3
					FROM
						a
					WHERE
						qty_flag != ''M'' or qty_flag is null
					) b
				USING (wls_id)
				ORDER BY
					priority_date,
					licence_no,
					purpose,
					ann_adjust DESC,
					pod;',
				(in_table_name),
				(in_wfi)
				);

			END IF;
		END

$BODY$;

CREATE OR REPLACE FUNCTION bcwat_lic.get_allocs_adjusted_quantity(
	in_wfi integer,
	in_basin text,
	in_table_name text DEFAULT 'bcwat_lic.licence_wls_map'::text,
	OUT wls_id text,
	OUT purpose character varying,
	OUT water_allocation_type text,
	OUT licence_term text,
	OUT purpose_groups text,
	OUT start_date date,
	OUT expiry_date date,
	OUT ann_adjust_is_consumptive numeric,
	OUT ann_adjust numeric,
	OUT old_ann_adjust_is_consumptive numeric,
	OUT old_ann_adjust numeric,
	OUT quantity_day_m3 numeric,
	OUT quantity_sec_m3 numeric,
	OUT sourcetype text)
    RETURNS SETOF record
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
	BEGIN
		IF in_basin::text = 'query'::text and in_table_name = 'bcwat_lic.licence_wls_map' THEN
			RETURN QUERY
				SELECT
					f.wls_id,
					f.purpose,
					f.water_allocation_type,
					f.licence_term,
					f.purpose_groups,
					f.start_date,
					f.expiry_date,
					case
						when f.ann_adjust is null then 0::numeric
						when f.is_consumptive is False then 0::numeric
						when f.is_consumptive then f.ann_adjust::numeric
					end as ann_adjust_is_consumptive,
					f.ann_adjust::numeric,
					case
						when f.old_ann_adjust is null then 0::numeric
						when f.is_consumptive is False then 0::numeric
						when f.is_consumptive then f.old_ann_adjust::numeric
					end as old_ann_adjust_is_consumptive,
					f.old_ann_adjust::numeric,
					f.quantity_day_m3,
					f.quantity_sec_m3,
					f.sourcetype
				FROM
					bcwat_lic.get_allocs_per_wfi(in_wfi::int) f
				WHERE
					f.lic_status = 'CURRENT'::text
				AND
					(f.licence_term = 'long'::text AND f.water_allocation_type = 'SW'::text)
				OR
					(f.licence_term = 'short'::text);
		ELSIF in_basin = 'downstream'::text and in_table_name = 'bcwat_lic.licence_wls_map' THEN
			RETURN QUERY
				SELECT
					downstream.wls_id,
					downstream.purpose,
					downstream.water_allocation_type,
					downstream.licence_term,
					downstream.purpose_groups,
					downstream.start_date,
					downstream.expiry_date,
					CASE
						-- never include storage amounts, not even in downstream
						WHEN downstream.purpose in ('Stream Storage: Power', 'Stream Storage: Non-Power', 'Aquifer Storage: Non-Power', 'Aquifer Storage: Power') THEN 0::numeric
						WHEN query.wls_id IS NULL THEN downstream.ann_adjust::numeric
						ELSE downstream.ann_adjust_is_consumptive::numeric
					END AS ann_adjust_is_consumptive,
					downstream.ann_adjust::numeric,
					CASE
						-- never include storage amounts, not even in downstream
						WHEN downstream.purpose in ('Stream Storage: Power', 'Stream Storage: Non-Power', 'Aquifer Storage: Non-Power', 'Aquifer Storage: Power') THEN 0::numeric
						WHEN query.wls_id IS NULL THEN downstream.old_ann_adjust::numeric
						ELSE downstream.old_ann_adjust_is_consumptive::numeric
					END AS old_ann_adjust_is_consumptive,
					downstream.old_ann_adjust::numeric,
					downstream.quantity_day_m3,
					downstream.quantity_sec_m3,
					downstream.sourcetype
				FROM
					(
						SELECT
							d.wls_id,
							d.purpose,
							d.water_allocation_type,
							d.licence_term,
							d.purpose_groups,
							d.start_date,
							d.expiry_date,
							case
								when d.ann_adjust is null then 0::numeric
								when d.is_consumptive is False then 0::numeric
								when d.is_consumptive then d.ann_adjust::numeric
							end as ann_adjust_is_consumptive,
							d.ann_adjust::numeric,
							case
								when d.old_ann_adjust is null then 0::numeric
								when d.is_consumptive is False then 0::numeric
								when d.is_consumptive then d.old_ann_adjust::numeric
							end as old_ann_adjust_is_consumptive,
							d.old_ann_adjust::numeric,
							d.quantity_day_m3,
							d.quantity_sec_m3,
							d.sourcetype
						FROM
							bcwat_lic.get_allocs_per_wfi((SELECT downstream_id FROM bcwat_ws.fund_rollup_report WHERE watershed_feature_id = in_wfi::int)) d
						WHERE
							d.lic_status = 'CURRENT'::text
						AND
							(d.licence_term = 'long'::text AND d.water_allocation_type = 'SW'::text)
						OR
							(d.licence_term = 'short'::text)
					) downstream
				LEFT JOIN
					(
						SELECT
							q.wls_id
						FROM
							bcwat_lic.get_allocs_per_wfi(in_wfi::int) q
						WHERE
							q.lic_status = 'CURRENT'::text
						AND
							(q.licence_term = 'long'::text AND q.water_allocation_type = 'SW'::text)
						OR
							(q.licence_term = 'short'::text)
					) query
				on downstream.wls_id = query.wls_id;
		ELSIF in_basin::text = 'query'::text and in_table_name != 'bcwat_lic.licence_wls_map' THEN
			RETURN QUERY
				SELECT
					f.wls_id,
					f.purpose,
					f.water_allocation_type,
					f.licence_term,
					f.purpose_groups,
					f.start_date,
					f.expiry_date,
					case
						when f.ann_adjust is null then 0::numeric
						when f.is_consumptive is False then 0::numeric
						when f.is_consumptive then f.ann_adjust::numeric
					end as ann_adjust_is_consumptive,
					f.ann_adjust::numeric,
					case
						when f.old_ann_adjust is null then 0::numeric
						when f.is_consumptive is False then 0::numeric
						when f.is_consumptive then f.old_ann_adjust::numeric
					end as old_ann_adjust_is_consumptive,
					f.old_ann_adjust::numeric,
					f.quantity_day_m3,
					f.quantity_sec_m3,
					f.sourcetype
				FROM
					bcwat_lic.get_allocs_per_wfi(in_wfi::int, in_table_name) f
				WHERE
					f.lic_status = 'CURRENT'::text
				AND
					(f.licence_term = 'long'::text AND f.water_allocation_type = 'SW'::text)
				OR
					(f.licence_term = 'short'::text);
		ELSIF in_basin = 'downstream'::text and in_table_name != 'bcwat_lic.licence_wls_map' THEN
			RETURN QUERY
				SELECT
					downstream.wls_id,
					downstream.purpose,
					downstream.water_allocation_type,
					downstream.licence_term,
					downstream.purpose_groups,
					downstream.start_date,
					downstream.expiry_date,
					CASE
						-- never include storage amounts, not even in downstream
						WHEN downstream.purpose in ('Stream Storage: Power', 'Stream Storage: Non-Power', 'Aquifer Storage: Non-Power', 'Aquifer Storage: Power') THEN 0::numeric
						WHEN query.wls_id IS NULL THEN downstream.ann_adjust::numeric
						ELSE downstream.ann_adjust_is_consumptive::numeric
					END AS ann_adjust_is_consumptive,
					downstream.ann_adjust::numeric,
					CASE
						-- never include storage amounts, not even in downstream
						WHEN downstream.purpose in ('Stream Storage: Power', 'Stream Storage: Non-Power', 'Aquifer Storage: Non-Power', 'Aquifer Storage: Power') THEN 0::numeric
						WHEN query.wls_id IS NULL THEN downstream.old_ann_adjust::numeric
						ELSE downstream.old_ann_adjust_is_consumptive::numeric
					END AS old_ann_adjust_is_consumptive,
					downstream.old_ann_adjust::numeric,
					downstream.quantity_day_m3,
					downstream.quantity_sec_m3,
					downstream.sourcetype
				FROM
					(
						SELECT
							d.wls_id,
							d.purpose,
							d.water_allocation_type,
							d.licence_term,
							d.purpose_groups,
							d.start_date,
							d.expiry_date,
							case
								when d.ann_adjust is null then 0::numeric
								when d.is_consumptive is False then 0::numeric
								when d.is_consumptive then d.ann_adjust::numeric
							end as ann_adjust_is_consumptive,
							d.ann_adjust::numeric,
							case
								when d.old_ann_adjust is null then 0::numeric
								when d.is_consumptive is False then 0::numeric
								when d.is_consumptive then d.old_ann_adjust::numeric
							end as old_ann_adjust_is_consumptive,
							d.old_ann_adjust::numeric,
							d.quantity_day_m3,
							d.quantity_sec_m3,
							d.sourcetype
						FROM
							bcwat_lic.get_allocs_per_wfi((SELECT downstream_id FROM bcwat_ws.fund_rollup_report WHERE watershed_feature_id = in_wfi::int), in_table_name) d
						WHERE
							d.lic_status = 'CURRENT'::text
						AND
							(d.licence_term = 'long'::text AND d.water_allocation_type = 'SW'::text)
						OR
							(d.licence_term = 'short'::text)
					) downstream
				LEFT JOIN
					(
						SELECT
							q.wls_id
						FROM
							bcwat_lic.get_allocs_per_wfi(in_wfi::int, in_table_name) q
						WHERE
							q.lic_status = 'CURRENT'::text
						AND
							(q.licence_term = 'long'::text AND q.water_allocation_type = 'SW'::text)
						OR
							(q.licence_term = 'short'::text)
					) query
				on downstream.wls_id = query.wls_id;
		ELSE
			RAISE EXCEPTION 'Error, in_basin argument is neither query or downstream';
		END IF;
	END

$BODY$;

CREATE OR REPLACE FUNCTION bcwat_lic.get_each_allocs_monthly(
	in_wfi integer,
	in_basin text,
	in_region_id integer,
	in_table_name text DEFAULT 'bcwat_lic.licence_wls_map'::text,
	in_datestamp date DEFAULT now(),
	OUT wls_id text,
	OUT month_forward integer,
	OUT long_allocs numeric,
	OUT short_allocs numeric)
    RETURNS SETOF record
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
		BEGIN
			RETURN QUERY
				SELECT
				s.wls_id,
				year_fwd_month::int as month_forward,
				CASE
					WHEN year_fwd_month = 1 and licence_term = 'long' THEN
						CASE
							WHEN
								LOWER(purpose) ilike '%irrigation%' OR
								LOWER(purpose) ilike '%lwn, fairway grdn%' OR
								LOWER(purpose) ilike '%storage%' OR
								LOWER(purpose) ilike '%mining%' OR
								LOWER(purpose) ilike '%transport mgmt%' OR
								LOWER(purpose) ilike '%crops%'
							THEN
								0
							ELSE
								((ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 2 and licence_term = 'long' THEN
						CASE
							WHEN
								LOWER(purpose) ilike '%irrigation%' OR
								LOWER(purpose) ilike '%lwn, fairway grdn%' OR
								LOWER(purpose) ilike '%storage%' OR
								LOWER(purpose) ilike '%mining%' OR
								LOWER(purpose) ilike '%transport mgmt%' OR
								LOWER(purpose) ilike '%crops%'
							THEN
								0
							ELSE
								((ann_adjust_is_consumptive/365) * 28.25) /(28.25*24*60*60)
						END
					WHEN year_fwd_month = 3 and licence_term = 'long' THEN
						CASE
							WHEN
								LOWER(purpose) ilike '%irrigation%' OR
								LOWER(purpose) ilike '%lwn, fairway grdn%' OR
								LOWER(purpose) ilike '%storage%' OR
								LOWER(purpose) ilike '%mining%' OR
								LOWER(purpose) ilike '%transport mgmt%' OR
								LOWER(purpose) ilike '%crops%'
							THEN
								0
							ELSE
								((ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 4 and licence_term = 'long' THEN
						CASE
							WHEN
								in_region_id = 3
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%'
									THEN
										CASE
											WHEN
												ann_adjust IS NOT NULL
											THEN
												(ann_adjust * 0.167) / (30*24*60*60)
											ELSE
												(ann_adjust_is_consumptive * 0.167) / (30*24*60*60)
										END
									WHEN
										LOWER(purpose) ilike '%storage%' OR
										LOWER(purpose) ilike '%mining%'
									THEN
										0
									WHEN
										LOWER(purpose) ilike '%transport mgmt%' OR
										LOWER(purpose) ilike '%crops%'
									THEN
										CASE
											WHEN
												ann_adjust IS NOT NULL
											THEN
												(ann_adjust * 0.1432) / (30*24*60*60)
											ELSE
												(ann_adjust_is_consumptive * 0.1432) / (30*24*60*60)
										END
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							WHEN
								in_region_id IN (4,5,6)
							THEN
								(ann_adjust_is_consumptive * 0) / (30*24*60*60)
						END
					WHEN year_fwd_month = 5 and licence_term = 'long' THEN
						CASE
							WHEN
								in_region_id = 3
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%' OR
										LOWER(purpose) ilike '%mining%'
									THEN
										CASE
											WHEN
												ann_adjust IS NOT NULL
											THEN
												(ann_adjust * 0.167) / (31*24*60*60)
											ELSE
												(ann_adjust_is_consumptive * 0.167) / (31*24*60*60)
										END
									WHEN
										LOWER(purpose) ilike '%transport mgmt%' OR
										LOWER(purpose) ilike '%crops%'
									THEN
										CASE
											WHEN
												ann_adjust IS NOT NULL
											THEN
												(ann_adjust * 0.1428) / (31*24*60*60)
											ELSE
												(ann_adjust_is_consumptive * 0.1428) / (31*24*60*60)
										END
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
								END
							WHEN
								in_region_id = 4
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%'
									THEN
										(ann_adjust_is_consumptive * 0.15) / (31*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
								END
							WHEN
								in_region_id IN (5, 6)
							THEN
								0
							ELSE ((ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 6 and licence_term = 'long' THEN
						CASE
							WHEN
								in_region_id = 3
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%' OR
										LOWER(purpose) ilike '%mining%'
									THEN
										CASE
											WHEN
												ann_adjust IS NOT NULL
											THEN
												(ann_adjust * 0.167) / (31*24*60*60)
											ELSE
												(ann_adjust_is_consumptive * 0.167) / (31*24*60*60)
										END
									WHEN
										LOWER(purpose) ilike '%transport mgmt%' OR
										LOWER(purpose) ilike '%crops%'
									THEN
										CASE
											WHEN
												ann_adjust IS NOT NULL
											THEN
												(ann_adjust * 0.1428) / (31*24*60*60)
											ELSE
												(ann_adjust_is_consumptive * 0.1428) / (31*24*60*60)
										END
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							WHEN
								in_region_id = 4
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%'
									THEN
										(ann_adjust_is_consumptive * 0.2) / (30*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							WHEN
								in_region_id = 5
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%'
									THEN
										(ann_adjust_is_consumptive * 0.15) / (30*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							WHEN
								in_region_id = 6
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%'
									THEN
										(ann_adjust_is_consumptive * 0.3) / (30*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							ELSE
								((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
						END
					WHEN year_fwd_month = 7 and licence_term = 'long' THEN
						CASE
							WHEN
								in_region_id = 3
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%' OR
										LOWER(purpose) ilike '%mining%'
									THEN
										CASE
											WHEN
												ann_adjust IS NOT NULL
											THEN
												(ann_adjust * 0.167) / (31*24*60*60)
											ELSE
												(ann_adjust_is_consumptive * 0.167) / (31*24*60*60)
										END
									WHEN
										LOWER(purpose) ilike '%transport mgmt%' OR
										LOWER(purpose) ilike '%crops%'
									THEN
										CASE
											WHEN
												ann_adjust IS NOT NULL
											THEN
												(ann_adjust * 0.1428) / (31*24*60*60)
											ELSE
												(ann_adjust_is_consumptive * 0.1428) / (31*24*60*60)
										END
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							WHEN
								in_region_id = 4
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%'
									THEN
										(ann_adjust_is_consumptive * 0.25) / (30*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							WHEN
								in_region_id = 5
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%'
									THEN
										(ann_adjust_is_consumptive * 0.5) / (30*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							WHEN
								in_region_id = 6
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%'
									THEN
										(ann_adjust_is_consumptive * 0.3) / (30*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							ELSE
								((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
						END
					WHEN year_fwd_month = 8 and licence_term = 'long' THEN
						CASE
							WHEN
								in_region_id = 3
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%'
									THEN
										CASE
											WHEN
												ann_adjust IS NOT NULL
											THEN
												(ann_adjust * 0.166) / (31*24*60*60)
											ELSE
												(ann_adjust_is_consumptive * 0.166) / (31*24*60*60)
										END
									WHEN
										LOWER(purpose) ilike '%mining%'
									THEN
										CASE
											WHEN
												ann_adjust IS NOT NULL
											THEN
												(ann_adjust * 0.167) / (31*24*60*60)
											ELSE
												(ann_adjust_is_consumptive * 0.167) / (31*24*60*60)
										END
									WHEN
										LOWER(purpose) ilike '%transport mgmt%' OR
										LOWER(purpose) ilike '%crops%'
									THEN
										CASE
											WHEN
												ann_adjust IS NOT NULL
											THEN
												(ann_adjust * 0.1428) / (31*24*60*60)
											ELSE
												(ann_adjust_is_consumptive * 0.1428) / (31*24*60*60)
										END
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							WHEN
								in_region_id IN (4, 5)
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%'
									THEN
										(ann_adjust_is_consumptive * 0.25) / (30*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							WHEN
								in_region_id = 6
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%'
									THEN
										(ann_adjust_is_consumptive * 0.3) / (30*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							ELSE
								((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
						END
					WHEN year_fwd_month = 9 and licence_term = 'long' THEN
						CASE
							WHEN
								in_region_id = 3
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%' OR
										LOWER(purpose) ilike '%mining%'
									THEN
										CASE
											WHEN
												ann_adjust IS NOT NULL
											THEN
												(ann_adjust * 0.166) / (31*24*60*60)
											ELSE
												(ann_adjust_is_consumptive * 0.166) / (31*24*60*60)
										END
									WHEN
										LOWER(purpose) ilike '%transport mgmt%' OR
										LOWER(purpose) ilike '%crops%'
									THEN
										CASE
											WHEN
												ann_adjust IS NOT NULL
											THEN
												(ann_adjust * 0.1428) / (31*24*60*60)
											ELSE
												(ann_adjust_is_consumptive * 0.1428) / (31*24*60*60)
										END
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							WHEN
								in_region_id = 4
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%'
									THEN
										(ann_adjust_is_consumptive * 0.15) / (30*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							WHEN
								in_region_id IN (5,6)
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%'
									THEN
										(ann_adjust_is_consumptive * 0.1) / (30*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							ELSE
								((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
						END
					WHEN year_fwd_month = 10 and licence_term = 'long' THEN
						CASE
							WHEN
								in_region_id = 3
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%mining%'
									THEN
										CASE
											WHEN
												ann_adjust IS NOT NULL
											THEN
												(ann_adjust * 0.166) / (31*24*60*60)
											ELSE
												(ann_adjust_is_consumptive * 0.166) / (31*24*60*60)
										END
									WHEN
										LOWER(purpose) ilike '%transport mgmt%' OR
										LOWER(purpose) ilike '%crops%'
									THEN
										CASE
											WHEN
												ann_adjust IS NOT NULL
											THEN
												(ann_adjust * 0.1428) / (31*24*60*60)
											ELSE
												(ann_adjust_is_consumptive * 0.1428) / (31*24*60*60)
										END
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%' OR
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
								END
							WHEN
								in_region_id IN (4,5,6)
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%' OR
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
								END
							ELSE
								((ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 11 and licence_term = 'long' THEN
						CASE
							WHEN
								in_region_id = 3
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%' OR
										LOWER(purpose) ilike '%storage%' OR
										LOWER(purpose) ilike '%transport mgmt%' OR
										LOWER(purpose) ilike '%crops%' OR
										LOWER(purpose) ilike '%mining%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							WHEN
								in_region_id IN (4,5,6)
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%' OR
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							ELSE
								((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
						END
					WHEN year_fwd_month = 12 and licence_term = 'long' THEN
						CASE
							WHEN
								in_region_id = 3
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%' OR
										LOWER(purpose) ilike '%storage%' OR
										LOWER(purpose) ilike '%transport mgmt%' OR
										LOWER(purpose) ilike '%crops%' OR
										LOWER(purpose) ilike '%mining%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							WHEN
								in_region_id IN (4,5,6)
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%' OR
										LOWER(purpose) ilike '%lwn, fairway grdn%' OR
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							ELSE
								((ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
						END
					ELSE 0
					END as long_allocs,
				CASE
					WHEN year_fwd_month = 1 and alloc_year and licence_term = 'short' THEN
						CASE
							WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
							WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
							ELSE ((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 2 and alloc_year and licence_term = 'short' THEN
						CASE
							WHEN LOWER(sourcetype) ilike '%dugout%' THEN
								CASE
									WHEN d_count > 28 THEN
									(ann_adjust_is_consumptive * d_count * (0/29)) / (29*24*60*60)
									ELSE (ann_adjust_is_consumptive * d_count * (0/28)) / (28*24*60*60)
								END
							WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
							ELSE ((ann_adjust_is_consumptive/365.25) * 28.25) /(28.25*24*60*60)
						END
					WHEN year_fwd_month = 3 and alloc_year and licence_term = 'short' THEN
						CASE
							WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
							WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
							ELSE ((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 4 and alloc_year and licence_term = 'short' THEN
						CASE
							WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0/30)) / (30*24*60*60)
							WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
							ELSE ((ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
						END
					WHEN year_fwd_month = 5 and alloc_year and licence_term = 'short' THEN
						CASE
							WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0.35/31)) / (31*24*60*60)
							WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
							ELSE ((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 6 and alloc_year and licence_term = 'short' THEN
						CASE
							WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0.35/30)) / (30*24*60*60)
							WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
							ELSE ((ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
						END
					WHEN year_fwd_month = 7 and alloc_year and licence_term = 'short' THEN
						CASE
							WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0.15/31)) / (31*24*60*60)
							WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
							ELSE ((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 8 and alloc_year and licence_term = 'short' THEN
						CASE
							WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0.15/31)) / (31*24*60*60)
							WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
							ELSE ((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 9 and alloc_year and licence_term = 'short' THEN
						CASE
							WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0/30)) / (30*24*60*60)
							WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
							ELSE ((ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
						END
					WHEN year_fwd_month = 10 and alloc_year and licence_term = 'short' THEN
						CASE
							WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
							WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
							ELSE ((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 11 and alloc_year and licence_term = 'short' THEN
						CASE
							WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0/30)) / (30*24*60*60)
							WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
							ELSE ((ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
						END
					WHEN year_fwd_month = 12 and alloc_year and licence_term = 'short' THEN
						CASE
							WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
							WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
							ELSE ((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					ELSE 0
					END as short_allocs
				FROM
				bcwat_lic.get_allocs_adjusted_quantity(in_wfi::int, in_basin::text, in_table_name::text) s
				LEFT JOIN LATERAL
				(
					SELECT
						extract('month' from year_forward) as year_fwd_month,
						NOT(bool_and(alloc_year is null)) as alloc_year,
						count(*) filter(where alloc_year is not null) d_count
					FROM
						(
							SELECT
								-- create a time series of the the first of the month of the date when the report was generated
								-- eg. if you print a report on aug. 20, 2020 - create a time series from aug 1, 2020 to july 31, 2021
								generate_series(
									make_date(extract('year' from in_datestamp)::int, extract('month' from in_datestamp)::int, 1),
									make_date(extract('year' from in_datestamp)::int, extract('month' from in_datestamp)::int, 1) + interval '1 years' - interval '1 days',
									interval '1 days'
								)::date
						) AS cal(year_forward)
					LEFT JOIN
						(
							SELECT
								generate_series(
									start_date,
									expiry_date,
									interval '1 days'
								)::date
							FROM bcwat_lic.get_allocs_adjusted_quantity(in_wfi::int, in_basin::text, in_table_name::text) alad
							WHERE
								licence_term = 'short' and alad.wls_id = s.wls_id
						) AS cal2(alloc_year)
					ON
						year_forward = alloc_year
					group by
						extract('month' from year_forward)
				) cal(year_fwd_month, alloc_year, d_count) on true;
		END

$BODY$;

CREATE OR REPLACE FUNCTION bcwat_lic.get_allocs_monthly(
	in_region_id integer,
	in_wfi integer,
	in_basin text,
	in_table_name text DEFAULT 'bcwat_lic.licence_wls_map'::text,
	in_datestamp date DEFAULT now(),
	OUT month_forward integer,
	OUT long_allocs numeric,
	OUT short_allocs numeric,
	OUT all_allocs numeric)
    RETURNS SETOF record
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 1000

AS $BODY$
	BEGIN
		RETURN QUERY
			SELECT
				em.month_forward,
				sum(em.long_allocs),
				sum(em.short_allocs),
				sum(em.long_allocs)+sum(em.short_allocs) as all_allocs
			FROM
				bcwat_lic.get_each_allocs_monthly(in_wfi::int, in_basin::text,  in_region_id::int, in_table_name::text, in_datestamp::date) em
			GROUP BY
				em.month_forward;
	END

$BODY$;

CREATE OR REPLACE FUNCTION bcwat_lic.get_monthly_hydrology(
	in_wfi integer,
	in_basin text,
	in_table_name text DEFAULT 'bcwat_lic.licence_wls_map'::text,
	in_datestamp date DEFAULT now(),
	OUT results json)
    RETURNS SETOF json
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 10

AS $BODY$
	DECLARE fx_wfi integer;
		BEGIN
		IF in_basin = 'downstream'::text
		THEN
			SELECT downstream_id FROM bcwat_lic.fund_rollup_report WHERE watershed_feature_id = in_wfi INTO fx_wfi;
		ELSE
			SELECT in_wfi INTO fx_wfi;
		END IF;
	IF in_table_name = 'bcwat_lic.licence_wls_map' THEN
		RETURN QUERY EXECUTE format('
			with mad as (
			select
				unnest(STRING_TO_ARRAY(TRIM(''[|]'' FROM watershed_metadata->>''mean_monthly_discharge_m3s''::text), '','')::NUMERIC[]) as qmon_m3s,
				unnest(ARRAY[1,2,3,4,5,6,7,8,9,10,11,12]) as month_forward,
				(watershed_metadata->>''mad_m3s'')::NUMERIC AS mad_m3s
			from
				bcwat_ws.fund_rollup_report rollup
			where
				rollup.watershed_feature_id = %s
			), region_id AS (
				SELECT
					region_id
				FROM
					(
						SELECT
							region_id
						FROM
							bcwat_obs.region
						WHERE
							ST_Intersects(
								region_click_studyarea,
								(
									SELECT
										geom4326
									FROM
										bcwat_ws.fwa_fund
									WHERE
										watershed_feature_id = %s
								)
							)
						AND
							region_id IN (3,4,5,6)
						ORDER BY
							region_id
						LIMIT 1
					) AS region
			), mad_allocs as (
				SELECT
					qmon_m3s,
					mad_m3s,
					case
						when mad_m3s = 0 then 0
						else (qmon_m3s/mad_m3s)*100
					end as pct_mad,
					coalesce(long_allocs, 0) as long_allocs,
					coalesce(short_allocs, 0) as short_allocs,
					coalesce(all_allocs, 0) as all_allocs
				FROM
					mad
				LEFT JOIN
					bcwat_lic.get_allocs_monthly((SELECT region_id FROM region_id), %s, ''%s'')
				USING (month_forward)
				ORDER BY month_forward
			)
			SELECT
				json_object_agg(
				rowname, vals
			) as results
			FROM
			(
			select
			''pct_mad''::text as rowname,
			array_agg(round(pct_mad::numeric, 5))::text[] as vals
			from
			mad_allocs
			union all
			select
			''flow_sens''::text as keyname,
			array_agg(case
				when pct_mad > 20 then ''Low''::text
				when pct_mad < 10 then ''High''::text
				else ''Mod''::text
			end) as flow_sens
			from
			mad_allocs
			union all
			select ''long_display'' as keyname,
			array_agg(
				case
					when long_allocs < 0.01 and long_allocs > 0 then ''< 0.01''::text
					else round(long_allocs, 5)::text
					end
				)::text[]
			from mad_allocs
			union all
			select ''short_display'' as keyname,
			array_agg(
				case
					when short_allocs < 0.01 and short_allocs > 0 then ''< 0.01''::text
					else round(short_allocs, 5)::text
					end
				)::text[]
			from mad_allocs
			union all
			select ''ea_all'' as keyname,
			array_agg(
				all_allocs
				)::text[]
			from mad_allocs
			union all
			select
				''mad_m3s''::text as keyname,
				array_agg(round(qmon_m3s, 2))::text[]
			FROM
				mad_allocs
			union all
			SELECT
			''risk1''::text as keyname,
			array_agg(round(case
				-- low sensitivity
				when pct_mad > 20 then
					case
						when all_allocs > (qmon_m3s*0.15) then 0
						else (qmon_m3s*0.15) - all_allocs
					end
				-- high sensitivity, small stream
				when (pct_mad < 10 and mad_m3s < 10) THEN 0
				when pct_mad < 10 and mad_m3s >= 10 THEN
						case
							when all_allocs > (qmon_m3s*0.05) then 0
							else qmon_m3s*0.05 - all_allocs
						end
				else
					case
						-- moderate sensitivity, small stream
						when mad_m3s < 10 then 0
						-- moderate sensitivity, medium/large stream
						when mad_m3s >= 10 then
							case
							when all_allocs > qmon_m3s*0.1 then 0
							else qmon_m3s*0.1 - all_allocs
							end
					end
			end, 5))::text[] as flow_sens
			FROM
			mad_allocs
			union all
			SELECT
			''risk2''::text as keyname,
			array_agg(round(case
				-- low sensitivity
				when pct_mad > 20 then
					case
						when all_allocs > (qmon_m3s*0.2) then 0
						else (qmon_m3s*0.2) - all_allocs
					end
				-- high sensitivity, small stream
				when pct_mad < 10 and mad_m3s < 10 THEN
					case
						when all_allocs > qmon_m3s*0.05 then 0
						else qmon_m3s*0.05 - all_allocs
					end
				when pct_mad < 10 and mad_m3s >= 10 THEN
					case
						when all_allocs > (qmon_m3s*0.1) then 0
						else qmon_m3s*0.1 - all_allocs
					end
				else
					case
						-- moderate sensitivity, small stream
						when mad_m3s < 10 then
							case
								when all_allocs > (qmon_m3s*0.1) then 0
								else qmon_m3s*0.1 - all_allocs
							end
						-- moderate sensitivity, medium/large stream
						when mad_m3s >= 10 then
							case
								when all_allocs > (qmon_m3s*0.15) then 0
								else qmon_m3s*0.15 - all_allocs
							end
					end
			end, 5))::text[] as flow_sens
			FROM
			mad_allocs
			union all
			SELECT
			''risk3''::text as keyname,
			array_agg(case
				-- low sensitivity
				when pct_mad > 20 then
					case
						when all_allocs > (qmon_m3s*0.2) then concat(''≥ '', 0.00::text)
						else concat(''≥ '', (round((qmon_m3s*0.2 - all_allocs)::numeric, 5)::text))
					end
				-- high sensitivity, small stream
				when pct_mad < 10 and mad_m3s < 10 THEN
					case
						when all_allocs > qmon_m3s*0.05 then concat(''≥ '', 0::text)
						else concat(''≥ '', round((qmon_m3s*0.05 - all_allocs)::numeric, 5)::text)
					end
				when pct_mad < 10 and mad_m3s >= 10 THEN
					case
						when all_allocs > (qmon_m3s*0.1) then concat(''≥ '', 0.00::text)
						else concat(''≥ '', round((qmon_m3s*0.1 - all_allocs)::numeric, 5)::text)
					end
				else
					case
						-- moderate sensitivity, small stream
						when mad_m3s < 10 then
							case
								when all_allocs > (qmon_m3s*0.1) then concat(''≥ '', 0.00::text)
								else concat(''≥ '', round((qmon_m3s*0.1 - all_allocs)::numeric, 5)::text)
							end
						-- moderate sensitivity, medium/large stream
						when mad_m3s >= 10 then
							case
								when all_allocs > (qmon_m3s*0.15) then concat(''≥ '', 0.00::text)
								else concat(''≥ '', round((qmon_m3s*0.15 - all_allocs)::numeric, 5)::text)
							end
					end
			end)::text[] as flow_sens
			FROM
			mad_allocs
			) sq;',
			(fx_wfi),
			(in_wfi),
			(in_wfi),
			(in_basin)
			);
	ELSE
		RETURN QUERY EXECUTE format('
			with mad as (
			select
				unnest(STRING_TO_ARRAY(TRIM(''[|]'' FROM watershed_metadata->>''mean_monthly_discharge_m3s''::text), '','')::NUMERIC[]) as qmon_m3s,
				unnest(ARRAY[1,2,3,4,5,6,7,8,9,10,11,12]) as month_forward,
				(watershed_metadata->>''mad_m3s'')::NUMERIC AS mad_m3s
			from
				bcwat_ws.fund_rollup_report rollup
			where
				rollup.watershed_feature_id = %s
		), region_id AS (
				SELECT
					region_id
				FROM
					(
						SELECT
							region_id
						FROM
							bcwat_obs.region
						WHERE
							ST_Intersects(
								region_click_studyarea,
								(
									SELECT
										geom4326
									FROM
										bcwat_ws.fwa_fund
									WHERE
										watershed_feature_id = %s
								)
							)
						AND
							region_id IN (3,4,5,6)
						ORDER BY
							region_id
						LIMIT 1
					) AS region
			), mad_allocs as (
			SELECT
				qmon_m3s,
				mad_m3s,
				(qmon_m3s/mad_m3s)*100 as pct_mad,
				coalesce(long_allocs, 0) as long_allocs,
				coalesce(short_allocs, 0) as short_allocs,
				coalesce(all_allocs, 0) as all_allocs
			FROM
				mad
			LEFT JOIN
				bcwat_lic.get_allocs_monthly((SELECT region_id FROM region_id), %s, ''%s'', ''%s'', ''%s'')
			USING (month_forward)
			ORDER BY month_forward
		)
		SELECT
			json_object_agg(
			rowname, vals
		) as results
		FROM
		(
		select
		''pct_mad''::text as rowname,
		array_agg(round(pct_mad::numeric, 5))::text[] as vals
		from
		mad_allocs
		union all
		select
		''flow_sens''::text as keyname,
		array_agg(case
			when pct_mad > 20 then ''Low''::text
			when pct_mad < 10 then ''High''::text
			else ''Mod''::text
		end) as flow_sens
		from
		mad_allocs
		union all
		select ''long_display'' as keyname,
		array_agg(
			case
				when long_allocs < 0.01 and long_allocs > 0 then ''< 0.01''::text
				else round(long_allocs, 5)::text
				end
			)::text[]
		from mad_allocs
		union all
		select ''short_display'' as keyname,
		array_agg(
			case
				when short_allocs < 0.01 and short_allocs > 0 then ''< 0.01''::text
				else round(short_allocs, 5)::text
				end
			)::text[]
		from mad_allocs
		union all
		select ''ea_all'' as keyname,
		array_agg(
			all_allocs
			)::text[]
		from mad_allocs
		union all
		select
			''mad_m3s''::text as keyname,
			array_agg(round(qmon_m3s, 5))::text[]
		FROM
			mad_allocs
		union all
		SELECT
		''risk1''::text as keyname,
		array_agg(round(case
			-- low sensitivity
			when pct_mad > 20 then
				case
					when all_allocs > (qmon_m3s*0.15) then 0
					else (qmon_m3s*0.15) - all_allocs
				end
			-- high sensitivity, small stream
			when (pct_mad < 10 and mad_m3s < 10) THEN 0
			when pct_mad < 10 and mad_m3s >= 10 THEN
					case
						when all_allocs > (qmon_m3s*0.05) then 0
						else qmon_m3s*0.05 - all_allocs
					end
			else
				case
					-- moderate sensitivity, small stream
					when mad_m3s < 10 then 0
					-- moderate sensitivity, medium/large stream
					when mad_m3s >= 10 then
						case
						when all_allocs > qmon_m3s*0.1 then 0
						else qmon_m3s*0.1 - all_allocs
						end
				end
		end, 5))::text[] as flow_sens
		FROM
		mad_allocs
		union all
		SELECT
		''risk2''::text as keyname,
		array_agg(round(case
			-- low sensitivity
			when pct_mad > 20 then
				case
					when all_allocs > (qmon_m3s*0.2) then 0
					else (qmon_m3s*0.2) - all_allocs
				end
			-- high sensitivity, small stream
			when pct_mad < 10 and mad_m3s < 10 THEN
				case
					when all_allocs < qmon_m3s*0.05 then 0
					else qmon_m3s*0.05 - all_allocs
				end
			when pct_mad < 10 and mad_m3s >= 10 THEN
				case
					when all_allocs > (qmon_m3s*0.1) then 0
					else qmon_m3s*0.1 - all_allocs
				end
			else
				case
					-- moderate sensitivity, small stream
					when mad_m3s < 10 then
						case
							when all_allocs > (qmon_m3s*0.1) then 0
							else qmon_m3s*0.1 - all_allocs
						end
					-- moderate sensitivity, medium/large stream
					when mad_m3s >= 10 then
						case
							when all_allocs > (qmon_m3s*0.15) then 0
							else qmon_m3s*0.15 - all_allocs
						end
				end
		end, 5))::text[] as flow_sens
		FROM
		mad_allocs
		union all
		SELECT
		''risk3''::text as keyname,
		array_agg(case
			-- low sensitivity
			when pct_mad > 20 then
				case
					when all_allocs > (qmon_m3s*0.2) then concat(''≥ '', 0.00::text)
					else concat(''≥ '', (round((qmon_m3s*0.2 - all_allocs)::numeric, 5)::text))
				end
			-- high sensitivity, small stream
			when pct_mad < 10 and mad_m3s < 10 THEN
				case
					when all_allocs < qmon_m3s*0.05 then concat(''≥ '', 0::text)
					else concat(''≥ '', round((qmon_m3s*0.05 - all_allocs)::numeric, 5)::text)
				end
			when pct_mad < 10 and mad_m3s >= 10 THEN
				case
					when all_allocs > (qmon_m3s*0.1) then concat(''≥ '', 0.00::text)
					else concat(''≥ '', round((qmon_m3s*0.1 - all_allocs)::numeric, 5)::text)
				end
			else
				case
					-- moderate sensitivity, small stream
					when mad_m3s < 10 then
						case
							when all_allocs > (qmon_m3s*0.1) then concat(''≥ '', 0.00::text)
							else concat(''≥ '', round((qmon_m3s*0.1 - all_allocs)::numeric, 5)::text)
						end
					-- moderate sensitivity, medium/large stream
					when mad_m3s >= 10 then
						case
							when all_allocs > (qmon_m3s*0.15) then concat(''≥ '', 0.00::text)
							else concat(''≥ '', round((qmon_m3s*0.15 - all_allocs)::numeric, 5)::text)
						end
				end
		end)::text[] as flow_sens
		FROM
		mad_allocs
		) sq;',
			(fx_wfi),
			(fx_wfi),
			(fx_wfi),
			(in_basin),
			(in_table_name),
			(in_datestamp)
			);
	END IF;
	END

$BODY$;


CREATE OR REPLACE FUNCTION bcwat_lic.get_allocs_by_industry(
	in_wfi integer,
	in_table_name text DEFAULT 'bcwat_lic.licence_wls_map'::text,
	OUT results json)
    RETURNS SETOF json
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 10

AS $BODY$
		BEGIN
		IF in_table_name = 'bcwat_lic.licence_wls_map' THEN
			RETURN QUERY EXECUTE format('
			SELECT
				json_object_agg(purpose_groups,
					row_to_json((
					select d from
					(
						select
							sw_long,
							sw_short,
							gw_long,
							gw_short
					) d
				))) as results
				FROM (
					SELECT
						puc.puc_groupings_storage as purpose_groups,
						SUM(CASE
							WHEN water_allocation_type = ''SW''::text and licence_term = ''long''::text then qm3
							ELSE 0
						END) as sw_long,
						SUM(CASE
							WHEN water_allocation_type = ''SW''::text and licence_term = ''short''::text then qm3
							ELSE 0
						END) as sw_short,
						SUM(CASE
							WHEN water_allocation_type = ''GW''::text and licence_term = ''long''::text then qm3
							ELSE 0
						END) as gw_long,
						SUM(CASE
							WHEN water_allocation_type = ''GW''::text and licence_term = ''short''::text then qm3
							ELSE 0
						END) as gw_short
					from
						(
							SELECT
								puc_groupings_storage
							from
								%s
							group by
								puc_groupings_storage
						) puc
					LEFT JOIN
						(
						select
							puc_groupings_storage,
							water_allocation_type,
							licence_term,
							round(sum(ann_adjust)::numeric, 0) as qm3
						from
							bcwat_lic.get_allocs_per_wfi(%s::int)
						group by
							puc_groupings_storage,
							water_allocation_type,
							licence_term
						) allocs
				USING
					(puc_groupings_storage)
				GROUP BY
					puc_groupings_storage
				ORDER BY
					puc_groupings_storage
				) sq;',
				(in_table_name),
				(in_wfi)
				);
		ELSIF in_table_name != 'bcwat_lic.licence_wls_map' THEN
			RETURN QUERY EXECUTE format('
				SELECT
				json_object_agg(purpose_groups,
					row_to_json((
					select d from
					(
						select
							sw_long,
							sw_short,
							gw_long,
							gw_short
					) d
				))) as results
				FROM (
					SELECT
						puc.puc_groupings_storage as purpose_groups,
						SUM(CASE
							WHEN water_allocation_type = ''SW''::text and licence_term = ''long''::text then qm3
							ELSE 0
						END) as sw_long,
						SUM(CASE
							WHEN water_allocation_type = ''SW''::text and licence_term = ''short''::text then qm3
							ELSE 0
						END) as sw_short,
						SUM(CASE
							WHEN water_allocation_type = ''GW''::text and licence_term = ''long''::text then qm3
							ELSE 0
						END) as gw_long,
						SUM(CASE
							WHEN water_allocation_type = ''GW''::text and licence_term = ''short''::text then qm3
							ELSE 0
						END) as gw_short
					from
						(
							SELECT
								puc_groupings_storage
							from
								%s
							group by
								puc_groupings_storage
						) puc
					LEFT JOIN
						(
						select
							puc_groupings_storage,
							water_allocation_type,
							licence_term,
							round(sum(ann_adjust)::numeric, 0) as qm3
						from
							bcwat_lic.get_allocs_per_wfi(%s::int, ''%s'')
						group by
							puc_groupings_storage,
							water_allocation_type,
							licence_term
						) allocs
				USING
					(puc_groupings_storage)
				GROUP BY
					puc_groupings_storage
				ORDER BY
					puc_groupings_storage
				) sq',
				(in_table_name),
				(in_wfi),
				(in_table_name)
				);
		END IF;
		END

$BODY$;


CREATE OR REPLACE FUNCTION bcwat_lic.get_annual_hydrology(
	in_wfi integer,
	in_table_name text DEFAULT 'bcwat_lic.licence_wls_map'::text,
	OUT results json)
    RETURNS SETOF json
    LANGUAGE 'plpgsql'
    COST 100
    VOLATILE PARALLEL UNSAFE
    ROWS 10

AS $BODY$
	BEGIN
	IF in_table_name = 'bcwat_lic.licence_wls_map' THEN
		RETURN QUERY EXECUTE format('
			SELECT
				json_object_agg(rowname,
				row_to_json(( select d FROM ( select query, downstream) d ))) as results
			FROM
			(
			SELECT
				unnest(ARRAY[''area_km2'', ''mad_m3s'', ''allocs_m3s'', ''allocs_pct'', ''rr'', ''runoff_m3yr'', ''allocs_m3yr'', ''seasonal_sens'']) as rowname,
				unnest(q.query) as query,
				unnest(d.downstream) as downstream
			FROM
				(SELECT
					ARRAY[
						(ru.watershed_metadata ->> ''watershed_area_km2'')::text,
						CASE
							WHEN ((ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION > 0) AND ((ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION < 0.001) THEN ''< 0.001''::text
							ELSE (ru.watershed_metadata ->> ''mad_m3s'')::text
						END,
						CASE
							WHEN (allocs.annual_allocs_m3_s > 0) AND (allocs.annual_allocs_m3_s < 0.001) THEN ''< 0.001''::text
							ELSE round(allocs.annual_allocs_m3_s, 5)::text
						END,
						CASE
							WHEN allocs.annual_allocs_m3_s = 0 THEN 0::text
							ELSE
								CASE
								WHEN ((allocs.annual_allocs_m3_s/(ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION)*100) > 0 and ((allocs.annual_allocs_m3_s/(ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION)*100) < 0.1 THEN ''< 0.1''::text
								ELSE round(((allocs.annual_allocs_m3_s/(ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION)*100)::numeric, 5)::text
								END
							END::text,
						CASE
							WHEN (ru.watershed_metadata ->> ''rr'')::BOOLEAN THEN ''Present''::text
							ELSE ''None''::text
						END,
						(ru.watershed_metadata ->> ''mean_annual_runoff_m3yr'')::text,
						round(allocs.annual_allocs_m3_yr, 5)::text,
						CASE
							WHEN (ru.watershed_metadata ->> ''summer_sensitivity'')::BOOLEAN AND (ru.watershed_metadata ->> ''winter_sensitivity'')::BOOLEAN THEN ''Winter, Summer''::text
							WHEN (ru.watershed_metadata ->> ''summer_sensitivity'')::BOOLEAN AND NOT (ru.watershed_metadata ->> ''winter_sensitivity'')::BOOLEAN THEN ''Summer''::text
							WHEN NOT (ru.watershed_metadata ->> ''summer_sensitivity'')::BOOLEAN AND (ru.watershed_metadata ->> ''winter_sensitivity'')::BOOLEAN THEN ''Winter''::text
							ELSE ''None''::text
						end
					] AS query
					FROM
						(
						SELECT
							CASE
								WHEN SUM(old_ann_adjust_is_consumptive) IS NULL then 0::numeric
								ELSE SUM(old_ann_adjust_is_consumptive)
							END AS annual_allocs_m3_yr,
							CASE
								WHEN SUM(old_ann_adjust_is_consumptive)/(365.25*24*60*60) IS NULL then 0::numeric
								ELSE SUM(old_ann_adjust_is_consumptive)/(365.25*24*60*60)
							END AS annual_allocs_m3_s
						FROM
							bcwat_lic.get_allocs_adjusted_quantity(%s, ''query'')
						) allocs
				CROSS JOIN
					bcwat_ws.fund_rollup_report ru
				WHERE ru.watershed_feature_id = %s) q
			JOIN
				(SELECT
					ARRAY[
						(ru.watershed_metadata ->> ''watershed_area_km2'')::text,
						(ru.watershed_metadata ->> ''mad_m3s'')::text,
						CASE
							WHEN allocs.annual_allocs_m3_s > 0 AND allocs.annual_allocs_m3_s < 0.001 then ''< 0.001''::text
							ELSE round(allocs.annual_allocs_m3_s, 5)::text
						END,
						CASE
							WHEN allocs.annual_allocs_m3_s = 0 THEN 0::text
							ELSE
								CASE
								WHEN ((allocs.annual_allocs_m3_s/(ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION)*100) > 0 and ((allocs.annual_allocs_m3_s/(ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION)*100) < 0.1 then ''< 0.1''::text
								ELSE round(((allocs.annual_allocs_m3_s/(ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION)*100)::numeric, 5)::text
								END
							END::text,
						case
							when (ru.watershed_metadata ->> ''rr'')::BOOLEAN then ''Present''::text
							else ''None''::text
						end,
						(ru.watershed_metadata ->> ''mean_annual_runoff_m3yr'')::text,
						round(allocs.annual_allocs_m3_yr, 5)::text,
						case
							WHEN (ru.watershed_metadata ->> ''summer_sensitivity'')::BOOLEAN AND (ru.watershed_metadata ->> ''winter_sensitivity'')::BOOLEAN THEN ''Winter, Summer''::text
							WHEN (ru.watershed_metadata ->> ''summer_sensitivity'')::BOOLEAN AND NOT (ru.watershed_metadata ->> ''winter_sensitivity'')::BOOLEAN THEN ''Summer''::text
							WHEN NOT (ru.watershed_metadata ->> ''summer_sensitivity'')::BOOLEAN AND (ru.watershed_metadata ->> ''winter_sensitivity'')::BOOLEAN THEN ''Winter''::text
							ELSE ''None''::text
						end
					] as downstream
					FROM
						(
						SELECT
							CASE
								WHEN SUM(old_ann_adjust_is_consumptive) IS NULL then 0::numeric
								ELSE SUM(old_ann_adjust_is_consumptive)
							END AS annual_allocs_m3_yr,
							CASE
								WHEN SUM(old_ann_adjust_is_consumptive)/(365.25*24*60*60) IS NULL then 0::numeric
								ELSE SUM(old_ann_adjust_is_consumptive)/(365.25*24*60*60)
							END AS annual_allocs_m3_s
						FROM
							bcwat_lic.get_allocs_adjusted_quantity(%s, ''downstream'')
						) allocs
				CROSS JOIN
					bcwat_ws.fund_rollup_report ru
				WHERE ru.watershed_feature_id = (SELECT downstream_id FROM bcwat_ws.fund_rollup_report WHERE watershed_feature_id = %s)
				) d
			ON TRUE
			) sq;',
			(in_wfi),
			(in_wfi),
			(in_wfi),
			(in_wfi)
			);
	ELSIF in_table_name != 'bcwat_lic.licence_wls_map' THEN
		RETURN QUERY EXECUTE format('
		SELECT
			json_object_agg(rowname,
			row_to_json(( select d FROM ( select query, downstream) d ))) as results
		FROM
		(
		SELECT
			unnest(ARRAY[''area_km2'', ''mad_m3s'', ''allocs_m3s'', ''allocs_pct'', ''rr'', ''runoff_m3yr'', ''allocs_m3yr'', ''seasonal_sens'']) as rowname,
			unnest(q.query) as query,
			unnest(d.downstream) as downstream
		FROM
			(SELECT
				ARRAY[
					(ru.watershed_metadata ->> ''watershed_area_km2'')::text,
					CASE
						WHEN ((ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION > 0) AND ((ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION < 0.001) THEN ''< 0.001''::text
						ELSE (ru.watershed_metadata ->> ''mad_m3s'')::text
					END,
					CASE
						WHEN (allocs.annual_allocs_m3_s > 0) AND (allocs.annual_allocs_m3_s < 0.001) THEN ''< 0.001''::text
						ELSE round(allocs.annual_allocs_m3_s, 5)::text
					END,
					CASE
						WHEN allocs.annual_allocs_m3_s = 0 THEN 0::text
						ELSE
							CASE
							WHEN ((allocs.annual_allocs_m3_s/(ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION)*100) > 0 and ((allocs.annual_allocs_m3_s/(ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION)*100) < 0.1 THEN ''< 0.1''::text
							ELSE round(((allocs.annual_allocs_m3_s/(ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION)*100)::numeric, 5)::text
							END
						END::text,
					CASE
						WHEN (ru.watershed_metadata ->> ''rr'')::BOOLEAN THEN ''Present''::text
						ELSE ''None''::text
					END,
					(ru.watershed_metadata ->> ''mean_annual_runoff_m3yr'')::text,
					round(allocs.annual_allocs_m3_yr, 5)::text,
					CASE
						WHEN (ru.watershed_metadata ->> ''summer_sensitivity'')::BOOLEAN AND (ru.watershed_metadata ->> ''winter_sensitivity'')::BOOLEAN THEN ''Winter, Summer''::text
						WHEN (ru.watershed_metadata ->> ''summer_sensitivity'')::BOOLEAN AND NOT (ru.watershed_metadata ->> ''winter_sensitivity'')::BOOLEAN THEN ''Summer''::text
						WHEN NOT (ru.watershed_metadata ->> ''summer_sensitivity'')::BOOLEAN AND (ru.watershed_metadata ->> ''winter_sensitivity'')::BOOLEAN THEN ''Winter''::text
						ELSE ''None''::text
					end
				] AS query
				FROM
					(
					SELECT
						CASE
							WHEN SUM(old_ann_adjust_is_consumptive) IS NULL then 0::numeric
							ELSE SUM(old_ann_adjust_is_consumptive)
						END AS annual_allocs_m3_yr,
						CASE
							WHEN SUM(old_ann_adjust_is_consumptive)/(365.25*24*60*60) IS NULL then 0::numeric
							ELSE SUM(old_ann_adjust_is_consumptive)/(365.25*24*60*60)
						END AS annual_allocs_m3_s
					FROM
						bcwat_lic.get_allocs_adjusted_quantity(%s, ''query'', ''%s'')
					) allocs
			CROSS JOIN
				bcwat_ws.fund_rollup_report ru
			WHERE ru.watershed_feature_id = %s) q
		JOIN
			(SELECT
				ARRAY[
					(ru.watershed_metadata ->> ''watershed_area_km2'')::text,
					(ru.watershed_metadata ->> ''mad_m3s'')::text,
					CASE
						WHEN allocs.annual_allocs_m3_s > 0 AND allocs.annual_allocs_m3_s < 0.001 then ''< 0.001''::text
						ELSE round(allocs.annual_allocs_m3_s, 5)::text
					END,
					CASE
						WHEN allocs.annual_allocs_m3_s = 0 THEN 0::text
						ELSE
							CASE
							WHEN ((allocs.annual_allocs_m3_s/(ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION)*100) > 0 and ((allocs.annual_allocs_m3_s/(ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION)*100) < 0.1 then ''< 0.1''::text
							ELSE round(((allocs.annual_allocs_m3_s/(ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION)*100)::numeric, 5)::text
							END
						END::text,
					case
						when (ru.watershed_metadata ->> ''rr'')::BOOLEAN then ''Present''::text
						else ''None''::text
					end,
					(ru.watershed_metadata ->> ''mean_annual_runoff_m3yr'')::text,
					round(allocs.annual_allocs_m3_yr, 5)::text,
					case
						when (ru.watershed_metadata ->> ''summer_sensitivity'')::BOOLEAN and (ru.watershed_metadata ->> ''winter_sensitivity'')::BOOLEAN then ''Winter, Summer''::text
						when (ru.watershed_metadata ->> ''summer_sensitivity'')::BOOLEAN and not (ru.watershed_metadata ->> ''winter_sensitivity'')::BOOLEAN then ''Summer''::text
						when not (ru.watershed_metadata ->> ''summer_sensitivity'')::BOOLEAN and (ru.watershed_metadata ->> ''winter_sensitivity'')::BOOLEAN then ''Winter''::text
						else ''None''::text
					end
				] as downstream
				FROM
					(
					SELECT
						CASE
							WHEN SUM(old_ann_adjust_is_consumptive) IS NULL then 0::numeric
							ELSE SUM(old_ann_adjust_is_consumptive)
						END AS annual_allocs_m3_yr,
						CASE
							WHEN SUM(old_ann_adjust_is_consumptive)/(365.25*24*60*60) IS NULL then 0::numeric
							ELSE SUM(old_ann_adjust_is_consumptive)/(365.25*24*60*60)
						END AS annual_allocs_m3_s
					FROM
						bcwat_lic.get_allocs_adjusted_quantity(%s, ''downstream'', ''%s'')
					) allocs
			CROSS JOIN
				bcwat_ws.fund_rollup_report ru
			WHERE ru.watershed_feature_id = (SELECT downstream_id FROM bcwat_ws.fund_rollup_report WHERE watershed_feature_id = %s)
			) d
		ON TRUE
		) sq;',
		(in_wfi),
		(in_table_name),
		(in_wfi),
		(in_wfi),
		(in_table_name),
		(in_wfi)
		);
	END IF;
	END

$BODY$;

'''
