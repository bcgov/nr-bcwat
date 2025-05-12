post_import_query = '''    
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
		RETURN NEW;
	END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER "station_populate_station_region" AFTER INSERT ON bcwat_obs.station FOR EACH ROW EXECUTE FUNCTION bcwat_obs.insert_station_region();
    
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

INSERT INTO bcwat_obs.station_variable(station_id, variable_id) VALUES
	((SELECT station_id FROM bcwat_obs.station WHERE original_id = '08HB0012'), 1),
	((SELECT station_id FROM bcwat_obs.station WHERE original_id = '08HB0012'), 2);

INSERT INTO bcwat_obs.station_type_id(station_id, type_id) VALUES
	((SELECT station_id FROM bcwat_obs.station WHERE original_id = '08HB0012'), 1);
'''