import polars as pl

def generate_stations_as_features(stations: pl.LazyFrame) -> list[dict]:
    features = (
        stations
        .group_by("id", "name", "latitude", "longitude", "nid", "net", "ty", "area")
        .agg([
            pl.col("yr").unique().sort().alias("yr")
        ])
        .with_columns([
            pl.struct([
                pl.col("id"),
                pl.col("nid"),
                pl.col("name"),
                pl.col("net"),
                pl.col("ty"),
                pl.col("yr"),
                pl.col("area"),
            ]).alias("properties"),
            pl.struct([
                pl.concat_list(["longitude", "latitude"]).alias("coordinates"),
                pl.lit("Point").alias("type"),
            ]).alias("geometry"),
            pl.lit("Feature").alias("type"),
        ])
        .select(["properties", "geometry", "type"])
    )

    return features.collect().to_dicts()
