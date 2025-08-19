DROP FUNCTION IF EXISTS bcwat_lic.get_annual_hydrology(integer, text);

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
						(ru.watershed_metadata ->> ''mad_m3s'')::text,
						round(allocs.annual_allocs_m3_s, 5)::text,
						CASE
							WHEN allocs.annual_allocs_m3_s = 0 THEN 0::text
							ELSE
							round(((allocs.annual_allocs_m3_s/(ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION)*100)::numeric, 5)::text
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
						round(allocs.annual_allocs_m3_s, 5)::text,
						CASE
							WHEN allocs.annual_allocs_m3_s = 0 THEN 0::text
							ELSE
								round(((allocs.annual_allocs_m3_s/(ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION)*100)::numeric, 5)::text
							END::text,
						CASE
							when (ru.watershed_metadata ->> ''rr'')::BOOLEAN then ''Present''::text
							else ''None''::text
						END,
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
					(ru.watershed_metadata ->> ''mad_m3s'')::text,
					round(allocs.annual_allocs_m3_s, 5)::text,
					CASE
						WHEN allocs.annual_allocs_m3_s = 0 THEN 0::text
						ELSE
						round(((allocs.annual_allocs_m3_s/(ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION)*100)::numeric, 5)::text
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
					round(allocs.annual_allocs_m3_s, 5)::text,
					CASE
						WHEN allocs.annual_allocs_m3_s = 0 THEN 0::text
						ELSE
						round(((allocs.annual_allocs_m3_s/(ru.watershed_metadata ->> ''mad_m3s'')::DOUBLE PRECISION)*100)::numeric, 5)::text
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

DROP FUNCTION IF EXISTS bcwat_lic.get_monthly_hydrology(integer, text, integer, text, date);

CREATE OR REPLACE FUNCTION bcwat_lic.get_monthly_hydrology(
	in_wfi integer,
	in_basin text,
	in_region_id integer,
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
		SELECT downstream_id INTO fx_wfi FROM bcwat_ws.fund_rollup_report WHERE watershed_feature_id = in_wfi;
	ELSE
		fx_wfi := in_wfi;
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
				rollup.watershed_feature_id = %L
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
					bcwat_lic.get_allocs_monthly(%L, %L, ''%s'')
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
				round(long_allocs, 5)::text
				)::text[]
			from mad_allocs
			union all
			select ''short_display'' as keyname,
			array_agg(
					round(short_allocs, 5)::text
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
            (in_region_id),
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
				bcwat_lic.get_allocs_monthly(%L, %L, ''%s'', ''%s'', ''%s'')
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
				round(long_allocs, 5)::text
				end
			)::text[]
		from mad_allocs
		union all
		select ''short_display'' as keyname,
		array_agg(
			case
				round(short_allocs, 5)::text
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
            (in_region_id),
			(in_wfi),
			(in_basin),
			(in_table_name),
			(in_datestamp)
			);
	END IF;
	END

$BODY$;
