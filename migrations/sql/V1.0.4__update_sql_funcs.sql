DROP FUNCTION IF EXISTS bcwat_lic.get_allocs_by_industry(integer, text);

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
							round(sum(old_ann_adjust)::numeric, 0) as qm3
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
							round(sum(old_ann_adjust)::numeric, 0) as qm3
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

ALTER FUNCTION bcwat_lic.get_allocs_by_industry(integer, text)
    OWNER TO "bcwat-api-admin";

GRANT EXECUTE ON FUNCTION bcwat_lic.get_allocs_by_industry(integer, text) TO PUBLIC;

GRANT EXECUTE ON FUNCTION bcwat_lic.get_allocs_by_industry(integer, text) TO "bcwat-api-admin";

GRANT EXECUTE ON FUNCTION bcwat_lic.get_allocs_by_industry(integer, text) TO "bcwat-api-read-only";

DROP FUNCTION IF EXISTS bcwat_lic.get_each_allocs_monthly(integer, text, integer, text, date);

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
                                in_region_id = 3
                            THEN
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
                            WHEN
                                in_region_id IN (4,5,6)
                            THEN
                                CASE
                                    WHEN
                                        LOWER(purpose) ilike '%irrigation%'
                                    THEN
                                        0
                                    ELSE
                                        ((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
                        END
					WHEN year_fwd_month = 2 and licence_term = 'long' THEN
                        CASE
                            WHEN
                                in_region_id = 3
                            THEN
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
                            WHEN
                                in_region_id IN (4,5,6)
                            THEN
                                CASE
                                    WHEN
                                        LOWER(purpose) ilike '%irrigation%'
                                    THEN
                                        0
                                    ELSE
                                        ((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
                        END
					WHEN year_fwd_month = 3 and licence_term = 'long' THEN
                        CASE
                            WHEN
                                in_region_id = 3
                            THEN
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
                            WHEN
                                in_region_id IN (4,5,6)
                            THEN
                                CASE
                                    WHEN
                                        LOWER(purpose) ilike '%irrigation%'
                                    THEN
                                        0
                                    ELSE
                                        ((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
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
                                CASE
                                    WHEN
                                        LOWER(purpose) ilike '%irrigation%'
                                    THEN
                                        (old_ann_adjust_is_consumptive * 0) / (30*24*60*60)
                                    ELSE
                                        ((old_ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
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
										LOWER(purpose) ilike '%irrigation%'
									THEN
										(old_ann_adjust_is_consumptive * 0.15) / (31*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
								END
							WHEN
								in_region_id IN (5, 6)
							THEN
								CASE
                                    WHEN
                                        LOWER(purpose) ilike '%irrigation%'
                                    THEN
                                        0
                                    ELSE
                                        ((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
                                END
							ELSE ((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
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
										LOWER(purpose) ilike '%irrigation%'
									THEN
										(old_ann_adjust_is_consumptive * 0.2) / (30*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((old_ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							WHEN
								in_region_id = 5
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%'
									THEN
										(old_ann_adjust_is_consumptive * 0.15) / (30*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((old_ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							WHEN
								in_region_id = 6
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%'
									THEN
										(old_ann_adjust_is_consumptive * 0.3) / (30*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((old_ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							ELSE
								((old_ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
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
										((ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
								END
							WHEN
								in_region_id = 4
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%'
									THEN
										(old_ann_adjust_is_consumptive * 0.25) / (31*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
								END
							WHEN
								in_region_id = 5
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%'
									THEN
										(old_ann_adjust_is_consumptive * 0.5) / (31*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
								END
							WHEN
								in_region_id = 6
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%'
									THEN
										(old_ann_adjust_is_consumptive * 0.3) / (31*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
								END
							ELSE
								((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
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
										((ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
								END
							WHEN
								in_region_id IN (4, 5)
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%'
									THEN
										(old_ann_adjust_is_consumptive * 0.25) / (31*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
								END
							WHEN
								in_region_id = 6
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%'
									THEN
										(old_ann_adjust_is_consumptive * 0.3) / (31*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
								END
							ELSE
								((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
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
										LOWER(purpose) ilike '%irrigation%'
									THEN
										(old_ann_adjust_is_consumptive * 0.15) / (30*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((old_ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							WHEN
								in_region_id IN (5,6)
							THEN
								CASE
									WHEN
										LOWER(purpose) ilike '%irrigation%'
									THEN
										(old_ann_adjust_is_consumptive * 0.1) / (30*24*60*60)
									WHEN
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((old_ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							ELSE
								((old_ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
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
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
								END
							ELSE
								((old_ann_adjust_is_consumptive/365) * 31) /(31*24*60*60)
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
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((old_ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							ELSE
								((old_ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
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
										LOWER(purpose) ilike '%storage%'
									THEN
										0
									ELSE
										((old_ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
								END
							ELSE
								((old_ann_adjust_is_consumptive/365) * 30) /(30*24*60*60)
						END
					ELSE 0
					END as long_allocs,
				CASE
					WHEN year_fwd_month = 1 and alloc_year and licence_term = 'short' THEN
						CASE
                            WHEN
                                in_region_id = 3
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            WHEN
                                in_region_id IN (4,5,6)
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (old_ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 2 and alloc_year and licence_term = 'short' THEN
						CASE
                            WHEN
                                in_region_id = 3
                            THEN
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
                            WHEN
                                in_region_id IN (4,5,6)
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN
                                        CASE
                                            WHEN d_count > 28 THEN
                                            (old_ann_adjust_is_consumptive * d_count * (0/29)) / (29*24*60*60)
                                            ELSE (old_ann_adjust_is_consumptive * d_count * (0/28)) / (28*24*60*60)
                                        END
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((old_ann_adjust_is_consumptive/365.25) * 28.25) /(28.25*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365.25) * 28.25) /(28.25*24*60*60)
						END
					WHEN year_fwd_month = 3 and alloc_year and licence_term = 'short' THEN
						CASE
                            WHEN
                                in_region_id = 3
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            WHEN
                                in_region_id IN (4,5,6)
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (old_ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 4 and alloc_year and licence_term = 'short' THEN
						CASE
                            WHEN
                                in_region_id = 3
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0/30)) / (30*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
                                END
                            WHEN
                                in_region_id IN (4,5,6)
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (old_ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 5 and alloc_year and licence_term = 'short' THEN
						CASE
                            WHEN
                                in_region_id = 3
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0.35/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            WHEN
                                in_region_id IN (4,5,6)
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (old_ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 6 and alloc_year and licence_term = 'short' THEN
						CASE
                            WHEN
                                in_region_id = 3
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0.35/30)) / (30*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
                                END
                            WHEN
                                in_region_id IN (4,5,6)
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (old_ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 7 and alloc_year and licence_term = 'short' THEN
						CASE
                            WHEN
                                in_region_id = 3
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0.15/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            WHEN
                                in_region_id IN (4,5,6)
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (old_ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 8 and alloc_year and licence_term = 'short' THEN
						CASE
                            WHEN
                                in_region_id = 3
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0.15/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            WHEN
                                in_region_id IN (4,5,6)
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (old_ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 9 and alloc_year and licence_term = 'short' THEN
						CASE
                            WHEN
                                in_region_id = 3
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0/30)) / (30*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
                                END
                            WHEN
                                in_region_id IN (4,5,6)
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (old_ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 10 and alloc_year and licence_term = 'short' THEN
						CASE
                            WHEN
                                in_region_id = 3
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            WHEN
                                in_region_id IN (4,5,6)
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (old_ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 11 and alloc_year and licence_term = 'short' THEN
						CASE
                            WHEN
                                in_region_id = 3
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0/30)) / (30*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
                                END
                            WHEN
                                in_region_id IN (4,5,6)
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (old_ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
						END
					WHEN year_fwd_month = 12 and alloc_year and licence_term = 'short' THEN
						CASE
                            WHEN
                                in_region_id = 3
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            WHEN
                                in_region_id IN (4,5,6)
                            THEN
                                CASE
                                    WHEN LOWER(sourcetype) ilike '%dugout%' THEN (old_ann_adjust_is_consumptive * d_count * (0/31)) / (31*24*60*60)
                                    WHEN LOWER(sourcetype) ilike '%storage%' THEN 0
                                    ELSE ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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

ALTER FUNCTION bcwat_lic.get_each_allocs_monthly(integer, text, integer, text, date)
    OWNER TO "bcwat-api-admin";

GRANT EXECUTE ON FUNCTION bcwat_lic.get_each_allocs_monthly(integer, text, integer, text, date) TO PUBLIC;

GRANT EXECUTE ON FUNCTION bcwat_lic.get_each_allocs_monthly(integer, text, integer, text, date) TO "bcwat-api-admin";

GRANT EXECUTE ON FUNCTION bcwat_lic.get_each_allocs_monthly(integer, text, integer, text, date) TO "bcwat-api-read-only";
