bcwat_lic_query = '''

    CREATE SCHEMA "bcwat_lic";

    -- TABLE CREATION --

    CREATE TABLE "bcwat_lic"."lake_licence" (
    "waterbody_poly_id" integer,
    "lake_name" text DEFAULT '',
    "lake_licence_id" text DEFAULT '',
    "licence_stream_name" text DEFAULT '',
    PRIMARY KEY ("waterbody_poly_id", "lake_licence_id")
    );

    CREATE TABLE "bcwat_lic"."bc_wls_water_approval" (
    "bc_wls_water_approval_id" integer PRIMARY KEY,
    "wsd_region" text DEFAULT '',
    "approval_type" text DEFAULT '',
    "approval_file_number" text DEFAULT '',
    "fcbc_tracking_number" text DEFAULT '',
    "source" text DEFAULT '',
    "works_description" text DEFAULT '',
    "quantity" DOUBLE PRECISION,
    "quantity_units" text DEFAULT '',
    "qty_diversion_max_rate" DOUBLE PRECISION,
    "qty_units_diversion_max_rate" text DEFAULT '',
    "water_district" text DEFAULT '',
    "precinct" text DEFAULT '',
    "latitude" DOUBLE PRECISION,
    "longitude" DOUBLE PRECISION,
    "approval_status" text DEFAULT '',
    "application_date" date,
    "fcbc_acceptance_date" date,
    "approval_issuance_date" date,
    "approval_start_date" date,
    "approval_expiry_date" date,
    "approval_refuse_abandon_date" date,
    "geom4326" geometry(Point,4326) NOT NULL,
    "created" date NOT NULL DEFAULT now(),
    "proponent" text DEFAULT '',
    "podno" text DEFAULT ''
    );

    CREATE TABLE "bcwat_lic"."bc_wls_wrl_wra" (
    "wls_wrl_wra_id" text PRIMARY KEY,
    "licence_no" varchar(16) NOT NULL DEFAULT '',
    "tpod_tag" varchar(10) NOT NULL DEFAULT '',
    "purpose" text NOT NULL DEFAULT '',
    "pcl_no" varchar(15) DEFAULT '',
    "qty_original" DOUBLE PRECISION,
    "qty_flag" varchar(1) DEFAULT '',
    "qty_units" varchar(25) DEFAULT '',
    "licensee" varchar NOT NULL DEFAULT '',
    "lic_status_date" date,
    "priority_date" date,
    "expiry_date" date,
    "longitude" DOUBLE PRECISION,
    "latitude" DOUBLE PRECISION,
    "stream_name" varchar DEFAULT '',
    "quantity_day_m3" DOUBLE PRECISION,
    "quantity_sec_m3" DOUBLE PRECISION,
    "quantity_ann_m3" DOUBLE PRECISION,
    "lic_status" text DEFAULT '',
    "rediversion_flag" varchar(1) DEFAULT '',
    "flag_desc" varchar(100) DEFAULT '',
    "file_no" varchar(10) DEFAULT '',
    "water_allocation_type" varchar(2) NOT NULL DEFAULT '',
    "geom4326" geometry(Point,4326),
    "water_source_type_desc" text DEFAULT '',
    "hydraulic_connectivity" varchar(215) DEFAULT '',
    "well_tag_number" DOUBLE PRECISION,
    "related_licences" text[] DEFAULT array[]::text[],
    "industry_activity" text NOT NULL DEFAULT '',
    "purpose_groups" text NOT NULL DEFAULT '',
    "is_consumptive" boolean NOT NULL,
    "ann_adjust" DOUBLE PRECISION,
    "quantity_ann_m3_storage_adjust" DOUBLE PRECISION DEFAULT NULL,
    "documentation" json,
    "qty_display" text DEFAULT '',
    "puc_groupings_storage" text DEFAULT '',
    "date_updated" timestamptz,
    CONSTRAINT bc_wls_wrl_wra_unique UNIQUE ("licence_no", "tpod_tag", "purpose", "pcl_no")
    );

    CREATE TABLE "bcwat_lic"."licence_ogc_short_term_approval" (
    "short_term_approval_id" text PRIMARY KEY,
    "pod_number" text DEFAULT '',
    "short_term_water_use_num" text DEFAULT '',
    "water_source_type" text DEFAULT '',
    "water_source_type_desc" text DEFAULT '',
    "water_source_name" text DEFAULT '',
    "purpose" text DEFAULT '',
    "purpose_desc" text DEFAULT '',
    "approved_volume_per_day" integer,
    "approved_total_volume" integer,
    "approved_start_date" date,
    "approved_end_date" date,
    "status" text DEFAULT '',
    "application_determination_num" text DEFAULT '',
    "activity_approval_date" date,
    "activity_cancel_date" date,
    "legacy_ogc_file_number" text DEFAULT '',
    "proponent" text NOT NULL DEFAULT '',
    "authority_type" text DEFAULT '',
    "land_type" text DEFAULT '',
    "data_source" text DEFAULT '',
    "geom4326" geometry(Point,4326),
    "latitude" DOUBLE PRECISION,
    "longitude" DOUBLE PRECISION,
    "is_consumptive" boolean,
    "qty_display" text DEFAULT ''
    );

    CREATE TABLE "bcwat_lic"."elevation_bookend" (
    "elevation_flat" DOUBLE PRECISION[],
    "elevation_steep" DOUBLE PRECISION[]
    );

    CREATE TABLE "bcwat_lic"."hypsometric_elevation_rollup" (
    "watershed_feature_id" integer PRIMARY KEY,
    "elevs" DOUBLE PRECISION[]
    );

    CREATE TABLE "bcwat_lic"."bc_data_import_date" (
    "dataset" text PRIMARY KEY,
    "import_date" date,
    "description" text DEFAULT ''
    );

    CREATE TABLE IF NOT EXISTS "bcwat_lic"."licence_bc_purpose" (
        "purpose" text PRIMARY KEY,
        "general_activity_code" text DEFAULT 'Other',
        "purpose_name" text,
        "purpose_code" text UNIQUE,
        "purpose_groups" text,
        "is_consumptive" boolean,
        "puc_groupings_newt" text NOT NULL,
        "puc_groupings_storage" text,
        "pid" integer NOT NULL,
        "still_used_by_databc" boolean DEFAULT false
    );

    CREATE TABLE IF NOT EXISTS "bcwat_lic"."wls_water_approval_deanna" (
    "gid" integer NOT NULL GENERATED BY DEFAULT AS IDENTITY ( INCREMENT 1 START 1 MINVALUE 1 MAXVALUE 2147483647 CACHE 1 ),
    "appfileno" text NOT NULL,
    "proponent" text NOT NULL,
    "podno" text,
    "latitude" DOUBLE PRECISION NOT NULL,
    "longitude" DOUBLE PRECISION NOT NULL,
    "purpose" text,
    "sourcetype" text,
    "sourcename" text,
    "fishpresence" text,
    "startdate" date,
    "expirationdate" date,
    "ms" DOUBLE PRECISION,
    "md" DOUBLE PRECISION,
    "my" DOUBLE PRECISION,
    "geom4326" geometry(Point,4326),
    "deanna_id" text,
    "quantity" DOUBLE PRECISION,
    "quantity_units" text,
    "qty_diversion_max_rate" DOUBLE PRECISION,
    "qty_units_diversion_max_rate" text,
    "approval_status" text DEFAULT 'Current'::text,
    CONSTRAINT wls_water_approval_deanna_pkey PRIMARY KEY (gid)
);

CREATE TABLE IF NOT EXISTS "bcwat_lic"."water_management_district_area" (
    district_id integer PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    district_name text NOT NULL UNIQUE,
    geom4326 geometry(MultiPolygon,4326)
);

    -- COMMENTS --

    COMMENT ON SCHEMA "bcwat_lic" IS 'The full name of this schema is bcwat_licence. This is where all the DataBC water licencing data gets scraped to and served to the frontend.';

    -- FOREIGN KEYS --

    ALTER TABLE "bcwat_lic"."lake_licence" ADD CONSTRAINT "lake_licence_waterbody_poly_id_fkey" FOREIGN KEY ("waterbody_poly_id") REFERENCES "bcwat_ws"."lake" ("waterbody_poly_id");

    ALTER TABLE "bcwat_lic"."hypsometric_elevation_rollup" ADD CONSTRAINT "hypsometric_elevation_rollup_watershed_feature_id_fkey" FOREIGN KEY ("watershed_feature_id") REFERENCES "bcwat_ws"."fwa_fund" ("watershed_feature_id");
'''
