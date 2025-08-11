WITH bc_poly AS (
  SELECT
    ST_MakePolygon(
      ST_ExteriorRing(
        ST_Union(region_click_studyarea)
      )
    ) AS geom
  FROM
    bcwat_obs.region
  WHERE
    region_name = ANY (ARRAY[ 'swp', 'nwp', 'nwwt' ])
)
UPDATE
  bcwat_obs.station s
SET
  prov_terr_state_loc = CASE WHEN ST_Intersects(bc_poly.geom, s.geom4326) THEN 'BC' ELSE 'NOT BC' END
FROM
  bc_poly;

UPDATE
  bcwat_obs.station s
SET
  longitude = -1 * longitude,
  geom4326 = ST_SETSRID(
    ST_MAKEPOINT(-1 * longitude, latitude),
    4326
  )
where
  station_name ilike '%Valemount (Cranberry Marsh)%';

UPDATE
  bcwat_obs.bc_boundary
SET
  geom4326 =(
    SELECT
      ST_MakePolygon(
        ST_ExteriorRing(
          ST_UNION(region_click_studyarea)
        )
      )
    FROM
      bcwat_obs.region
    where
      region_name = ANY(ARRAY[ 'swp', 'nwp', 'nwwt' ])
  )
WHERE
  gid = 1;
