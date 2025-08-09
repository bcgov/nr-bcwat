WITH study_area AS (
    SELECT
        ST_Buffer(
            ST_Union(
                region_click_studyarea
            ),
            0.0001
        ) AS geom
    FROM
        bcwat_obs.region
    WHERE
        region_id IN (3,4,5,6)
)
UPDATE
    bcwat_ws.fwa_fund
SET
    in_study_area = True
WHERE
    ST_Intersects(
        geom4326,
        (
            SELECT
                geom
            FROM
                study_area
        )
    )
AND
    in_study_area = False;
