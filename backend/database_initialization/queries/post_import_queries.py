post_import_query = '''

ALTER TABLE "bcwat_obs"."station" DROP COLUMN "old_station_id";

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

    CREATE TRIGGER "station_populate_geom4326" BEFORE INSERT ON bcwat_obs.station FOR EACH ROW EXECUTE FUNCTION bcwat_obs.fill_geom_point();

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

    INSERT INTO bcwat_obs.station_variable(station_id, variable_id)
        SELECT station_id, 1 AS variable_id FROM bcwat_obs.station WHERE original_id = '08HB0012'
        UNION
        SELECT station_id, 2 AS variable_id FROM bcwat_obs.station WHERE original_id = '08HB0012';

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
'''
