import polars as pl

def generate_stations_as_features(stations: list[dict]) -> list[dict]:
    stations_lf = pl.LazyFrame(
        stations,
        schema_overrides={
            'id': pl.Int32,
            'name': pl.String,
            'latitude': pl.Float64,
            'longitude': pl.Float64,
            'nid': pl.String,
            'net': pl.String,
            'ty': pl.String,
            'yr': pl.Int32,
            'status': pl.String,
            'area': pl.Float64,
            'variable_id': pl.Int32
        }
    )

    features = (
        stations_lf
        .group_by("id", "name", "latitude", "longitude", "nid", "net", "ty", "status", "area")
        .agg([
            pl.col("yr").unique().sort().alias("yr"),
            pl.col("variable_id").unique().sort().alias("analysesObj")
        ])
        .with_columns([
            pl.struct([
                pl.col("id"),
                pl.col("nid"),
                pl.col("name"),
                pl.col("net"),
                pl.col("ty"),
                pl.col("yr"),
                pl.col("status"),
                pl.col("area"),
                pl.col("analysesObj")
            ]).alias("properties"),
            pl.struct([
                pl.concat_list([pl.col("longitude"), pl.col("latitude")]).alias("coordinates"),
                pl.lit("Point").alias("type"),
            ]).alias("geometry"),
            pl.lit("Feature").alias("type"),
        ])
        .select(["properties", "geometry", "type"])
    )

    return features.collect().to_dicts()
