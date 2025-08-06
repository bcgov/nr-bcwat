ALTER DEFAULT PRIVILEGES IN SCHEMA bcwat_lic GRANT SELECT ON TABLES TO "bcwat-api-read-only";
ALTER DEFAULT PRIVILEGES IN SCHEMA bcwat_obs GRANT SELECT ON TABLES TO "bcwat-api-read-only";
ALTER DEFAULT PRIVILEGES IN SCHEMA bcwat_ws GRANT SELECT ON TABLES TO "bcwat-api-read-only";

GRANT USAGE ON SCHEMA bcwat_lic TO "bcwat-api-read-only";
GRANT USAGE ON SCHEMA bcwat_obs TO "bcwat-api-read-only";
GRANT USAGE ON SCHEMA bcwat_ws TO "bcwat-api-read-only";

GRANT SELECT ON ALL TABLES IN SCHEMA bcwat_lic TO "bcwat-api-read-only";
GRANT SELECT ON ALL TABLES IN SCHEMA bcwat_obs TO "bcwat-api-read-only";
GRANT SELECT ON ALL TABLES IN SCHEMA bcwat_ws TO "bcwat-api-read-only";

GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA bcwat_lic TO "bcwat-api-read-only";

ALTER DEFAULT PRIVILEGES IN SCHEMA bcwat_lic GRANT SELECT, UPDATE, DELETE, TRUNCATE, INSERT ON TABLES TO "bcwat-airflow-read-write";
ALTER DEFAULT PRIVILEGES IN SCHEMA bcwat_obs GRANT SELECT, UPDATE, DELETE, TRUNCATE, INSERT ON TABLES TO "bcwat-airflow-read-write";
ALTER DEFAULT PRIVILEGES IN SCHEMA bcwat_ws GRANT SELECT, UPDATE, DELETE, TRUNCATE, INSERT ON TABLES TO "bcwat-airflow-read-write";

GRANT USAGE ON SCHEMA bcwat_lic TO "bcwat-airflow-read-write";
GRANT USAGE ON SCHEMA bcwat_obs TO "bcwat-airflow-read-write";
GRANT USAGE ON SCHEMA bcwat_ws TO "bcwat-airflow-read-write";

GRANT SELECT, UPDATE, DELETE, TRUNCATE, INSERT ON ALL TABLES IN SCHEMA bcwat_lic TO "bcwat-airflow-read-write";
GRANT SELECT, UPDATE, DELETE, TRUNCATE, INSERT ON ALL TABLES IN SCHEMA bcwat_obs TO "bcwat-airflow-read-write";
GRANT SELECT, UPDATE, DELETE, TRUNCATE, INSERT ON ALL TABLES IN SCHEMA bcwat_ws TO "bcwat-airflow-read-write";
