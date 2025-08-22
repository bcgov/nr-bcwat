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
                                        ((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
                                        ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
                                        ((ann_adjust_is_consumptive/365.25) * 28.25) /(28.25*24*60*60)
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
                                        ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
                                        ((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
                                        ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
										((ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
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
                                        ((old_ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
                                END
                            ELSE
                                ((old_ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
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
										((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
										((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
                                        ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
                                END
							ELSE ((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
										((ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
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
										((old_ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
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
										((old_ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
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
										((old_ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
								END
							ELSE
								((old_ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
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
										((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
										((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
										((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
										((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
								END
							ELSE
								((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
										((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
										((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
										((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
								END
							ELSE
								((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
										((ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
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
										((old_ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
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
										((old_ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
								END
							ELSE
								((old_ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
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
										((ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
										((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
								END
							ELSE
								((old_ann_adjust_is_consumptive/365.25) * 31) /(31*24*60*60)
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
										((ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
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
										((old_ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
								END
							ELSE
								((old_ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
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
										((ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
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
										((old_ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
								END
							ELSE
								((old_ann_adjust_is_consumptive/365.25) * 30) /(30*24*60*60)
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

DROP FUNCTION IF EXISTS bcwat_lic.get_allocs_per_wfi(integer, text);

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
	OUT display_ann_qty double precision,
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
								CASE
									WHEN old_ann_adjust IS NULL THEN 0
									ELSE old_ann_adjust
								END AS display_ann_qty,
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
						a.display_ann_qty,
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
								display_ann_qty,
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
								display_ann_qty,
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
							CASE
								WHEN old_ann_adjust IS NULL THEN 0
								ELSE old_ann_adjust
							END AS display_ann_qty,
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
					a.display_ann_qty,
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
							display_ann_qty,
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
							display_ann_qty,
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
							CASE
								WHEN old_ann_adjust IS NULL THEN 0
								ELSE old_ann_adjust
							END AS display_ann_qty,
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
					a.display_ann_qty,
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
							display_ann_qty,
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
							display_ann_qty,
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

ALTER FUNCTION bcwat_lic.get_allocs_per_wfi(integer, text)
    OWNER TO "bcwat-api-admin";

GRANT EXECUTE ON FUNCTION bcwat_lic.get_allocs_per_wfi(integer, text) TO PUBLIC;

GRANT EXECUTE ON FUNCTION bcwat_lic.get_allocs_per_wfi(integer, text) TO "bcwat-api-admin";

GRANT EXECUTE ON FUNCTION bcwat_lic.get_allocs_per_wfi(integer, text) TO "bcwat-api-read-only";
