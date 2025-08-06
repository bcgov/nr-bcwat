import inspect
import os
import psycopg2
import inspect
import time
from constants import logger
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Database:
    def __init__(self):
        logger.info("Connecting to PostgreSQL Database...")
        port = os.getenv("POSTGRES_PORT")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")
        database = os.getenv("POSTGRES_DB")
        host = os.getenv("POSTGRES_HOST")

        try:
            self.pool = ThreadedConnectionPool(minconn=1, maxconn=5, host = host, database = database, user = user, password = password, port = port, keepalives=1, keepalives_idle=30, keepalives_interval=10, keepalives_count=5)
            logger.info("Connection Successful.")
        except psycopg2.OperationalError as e:
            logger.info(f"Could not connect to Database: {e}")

    def execute_as_dict(self, sql, args=[], fetch_one = False):
        caller_function_name = inspect.stack()[1].function
        retry_count = 0

        while retry_count < 5:
            connection = self.get_valid_conn()
            try:
                with connection.cursor(cursor_factory=RealDictCursor) as conn:
                    # Need to unpack - cant read in a dict. requires list of variables.
                    conn.execute(sql, args)
                    results = None

                    if fetch_one:
                        results = conn.fetchone()
                    else:
                        results = conn.fetchall()

                    connection.commit()
                    return results

            except psycopg2.OperationalError as op_error:
                connection.rollback()
                error_message = f"Caller Function: {caller_function_name} - Exceeded Retry Limit with Error: {op_error}"
                # Gradual Break on psycopg2.OperationalError - retry on SSL errors
                retry_count += 1
                time.sleep(5)
            except Exception as error:
                connection.rollback()
                # Exit While Loop without explicit break
                error_message = f"Caller Function: {caller_function_name} - Error in Execute Function: {error}"
                raise Exception({
                    "user_message": "Something went wrong! Please try again later.",
                    "server_message": error_message,
                    "status_code": 500
                })
                # Error in execute function
            finally:
                self.pool.putconn(connection)

        raise Exception({
                    "user_message": "Something went wrong! Please try again later.",
                    "server_message": error_message,
                    "status_code": 500
                })

    def get_valid_conn(self, max_attempts=5): # max attempts 5 (for all the conns)
        attempts = 0
        while attempts < max_attempts:
            conn = self.pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                return conn
            except Exception:
                logger.warning("Stale DB connection detected. Discarding and retrying.")
                self.pool.putconn(conn, close=True)
                attempts += 1
        raise Exception("Failed to get a valid database connection after several attempts.")

    def get_stations_by_type(self, **args):
        """
            Build and Return Dictionary of Features that are GeoJson compatible.
        """
        from queries.shared.get_stations_by_type import get_stations_by_type_query

        response = self.execute_as_dict(sql=get_stations_by_type_query, args=args, fetch_one=True)
        return response

    def get_station_by_type_and_id(self, **args):
        from queries.shared.get_station_by_type_and_id import get_station_by_type_and_id

        response = self.execute_as_dict(sql=get_station_by_type_and_id, args=args, fetch_one=True)
        return response

    def get_station_csv_metadata_by_type_and_id(self, **args):
        from queries.shared.get_station_csv_metadata_by_type_and_id import get_station_csv_metadata_by_type_and_id_query

        response = self.execute_as_dict(sql=get_station_csv_metadata_by_type_and_id_query, args=args, fetch_one=True)
        return response

    def get_climate_station_report_by_id(self, **args):
        from queries.climate.get_climate_station_report_by_id import get_climate_station_report_by_id_query

        response = self.execute_as_dict(sql=get_climate_station_report_by_id_query, args=args)
        return response

    def get_climate_station_csv_by_id(self, **args):
        from queries.climate.get_climate_station_csv_by_id import get_climate_station_csv_by_id_query

        response = self.execute_as_dict(sql=get_climate_station_csv_by_id_query, args=args)
        return response

    def get_groundwater_level_station_report_by_id(self, **args):
        from queries.groundwater.get_groundwater_level_station_report_by_id import get_groundwater_level_station_report_by_id_query

        response = self.execute_as_dict(sql=get_groundwater_level_station_report_by_id_query, args=args)
        return response

    def get_groundwater_level_station_csv_by_id(self, **args):
        from queries.groundwater.get_groundwater_level_station_csv_by_id import get_groundwater_level_station_csv_by_id_query

        response = self.execute_as_dict(sql=get_groundwater_level_station_csv_by_id_query, args=args)
        return response

    def get_groundwater_quality_station_report_by_id(self, **args):
        from queries.groundwater.get_groundwater_quality_station_report_by_id import get_groundwater_quality_station_report_by_id_query

        response = self.execute_as_dict(sql=get_groundwater_quality_station_report_by_id_query, args=args)
        return response

    def get_streamflow_station_report_by_id(self, **args):
        from queries.streamflow.get_streamflow_station_report_by_id import get_streamflow_station_report_by_id_query

        response = self.execute_as_dict(sql=get_streamflow_station_report_by_id_query, args=args)
        return response

    def get_streamflow_station_flow_metrics_by_id(self, **args):
        from queries.streamflow.get_streamflow_station_flow_metrics_by_id import get_streamflow_station_flow_metrics_by_id_query

        response = self.execute_as_dict(sql=get_streamflow_station_flow_metrics_by_id_query, args=args, fetch_one=True)
        return response

    def get_streamflow_station_csv_by_id(self, **args):
        from queries.streamflow.get_streamflow_station_csv_by_id import get_streamflow_station_csv_by_id_query

        response = self.execute_as_dict(sql=get_streamflow_station_csv_by_id_query, args=args)
        return response

    def get_surface_water_station_report_by_id(self, **args):
        from queries.surface_water.get_surface_water_station_report_by_id import get_surface_water_station_report_by_id_query

        response = self.execute_as_dict(sql=get_surface_water_station_report_by_id_query, args=args)
        return response

    def get_watershed_licences(self, **args):
        from queries.watershed.get_watershed_licences import get_watershed_licences_query

        response = self.execute_as_dict(get_watershed_licences_query , args=args, fetch_one=True)
        return response

    def get_watershed_by_lat_lng(self, **args):
        from queries.watershed.get_watershed_by_lat_lng import get_watershed_by_lat_lng_query

        response = self.execute_as_dict(get_watershed_by_lat_lng_query, args=args, fetch_one=True)
        return response

    def get_watershed_by_id(self, **args):
        from queries.watershed.get_watershed_by_id import get_watershed_by_id_query

        response = self.execute_as_dict(sql=get_watershed_by_id_query, args=args, fetch_one=True)
        return response

    def get_watershed_report_by_id(self, **args):
        from queries.watershed.get_watershed_report_by_id import get_watershed_report_by_id_query

        response = self.execute_as_dict(get_watershed_report_by_id_query, args=args, fetch_one=True)
        return response

    def get_watershed_region_by_id(self, **args):
        from queries.watershed.get_watershed_region_by_id import get_watershed_region_by_id_query

        response = self.execute_as_dict(get_watershed_region_by_id_query, args=args, fetch_one=True)
        return response

    def get_watershed_by_search_term(self, **args):
        from queries.watershed.get_watershed_by_search_term import get_watershed_by_search_term_query

        response = self.execute_as_dict(get_watershed_by_search_term_query, args=args)
        return response

    def get_watershed_licences_by_search_term(self, **args):
        from queries.watershed.get_watershed_licences_by_search_term import get_watershed_licences_by_search_term_query

        response = self.execute_as_dict(get_watershed_licences_by_search_term_query, args=args)
        return response

    def get_watershed_candidates_by_id(self, **args):
        from queries.watershed.get_watershed_candidates_by_id import get_watershed_candidates_by_id_query

        response = self.execute_as_dict(get_watershed_candidates_by_id_query, args=args)
        return response

    def get_watershed_monthly_hydrology_by_id(self, **args):
        from queries.watershed.get_watershed_monthly_hydrology_by_id import get_watershed_monthly_hydrology_by_id_query

        response = self.execute_as_dict(get_watershed_monthly_hydrology_by_id_query, args=args, fetch_one=True)
        return response

    def get_watershed_allocations_by_id(self, **args):
        from queries.watershed.get_watershed_allocations_by_id import get_watershed_allocations_by_id_query

        response = self.execute_as_dict(get_watershed_allocations_by_id_query, args=args)
        return response

    def get_watershed_industry_allocations_by_id(self, **args):
        from queries.watershed.get_watershed_industry_allocations_by_id import get_watershed_industry_allocations_by_id_query

        response = self.execute_as_dict(get_watershed_industry_allocations_by_id_query, args=args, fetch_one=True)
        return response

    def get_watershed_bus_stops_by_id(self, **args):
        from queries.watershed.get_watershed_bus_stops_by_id import get_bus_stops_query

        response = self.execute_as_dict(get_bus_stops_query, args=args)
        return response

    def get_watershed_hydrologic_variability_by_id(self, **args):
        from queries.watershed.get_watershed_hydrologic_variability_by_id import get_watershed_hydrologic_variability_by_id_query

        response = self.execute_as_dict(get_watershed_hydrologic_variability_by_id_query, args=args)
        return response

    def get_watershed_annual_hydrology_by_id(self, **args):
        from queries.watershed.get_watershed_annual_hydrology_by_id import get_watershed_annual_hydrology_by_id_query

        response = self.execute_as_dict(get_watershed_annual_hydrology_by_id_query, args=args, fetch_one=True)
        return response

    def get_licence_import_dates(self, **args):
        from queries.watershed.get_licence_import_dates import get_licence_import_dates_query

        response = self.execute_as_dict(get_licence_import_dates_query, args=args)
        return response

    def get_water_quality_station_statistics(self, **args):
        from queries.shared.get_water_quality_station_statistics import get_water_quality_station_statistics_query

        response = self.execute_as_dict(get_water_quality_station_statistics_query, args=args, fetch_one=True)
        return response

    def get_water_quality_station_csv_by_id(self, **args):
        from queries.shared.get_water_quality_csv_data_by_station_id import get_water_quality_station_csv_by_id_query

        response = self.execute_as_dict(sql=get_water_quality_station_csv_by_id_query, args=args)
        return response

    def get_streamflow_stations(self, **args):
        from queries.streamflow.get_streamflow_stations import get_streamflow_stations_query

        response = self.execute_as_dict(get_streamflow_stations_query, args, fetch_one=True)
        return response

    def get_climate_stations(self, **args):
        from queries.climate.get_climate_stations import get_climate_stations_query

        response = self.execute_as_dict(get_climate_stations_query, args, fetch_one=True)
        return response

    def get_kwt_hydrologic_variability_by_id(self, **args):
        from queries.watershed.get_kwt_hydrologic_variability_by_id import get_kwt_hydrologic_variability_by_id_query

        return {"hydrological_variability" :{"nc_p10_m01_06":0.0234501688544748,"nc_p10_m02_06":0.0142845766154894,"nc_p10_m03_06":0.00937997303911421,"nc_p10_m04_06":0.00709816141517962,"nc_p10_m05_06":0.0177846917780209,"nc_p10_m06_06":0.686108978083406,"nc_p10_m07_06":0.962611526923289,"nc_p10_m08_06":0.597310765847712,"nc_p10_m09_06":0.304500280283248,"nc_p10_m10_06":0.173541753255265,"nc_p10_m11_06":0.0965186322117663,"nc_p10_m12_06":0.0459922942562482,"nc_p25_m01_06":0.0277272767997474,"nc_p25_m02_06":0.0160743557338342,"nc_p25_m03_06":0.0102549991495117,"nc_p25_m04_06":0.00764348765851579,"nc_p25_m05_06":0.102806893485604,"nc_p25_m06_06":1.1345712970873,"nc_p25_m07_06":1.31586857864605,"nc_p25_m08_06":0.810012581032713,"nc_p25_m09_06":0.390738513867863,"nc_p25_m10_06":0.226306132790865,"nc_p25_m11_06":0.120182118360443,"nc_p25_m12_06":0.0560111231794676,"nc_p50_m01_06":0.0335068820289116,"nc_p50_m02_06":0.0185724583089615,"nc_p50_m03_06":0.011530198122916,"nc_p50_m04_06":0.00854055598521243,"nc_p50_m05_06":0.331959483014853,"nc_p50_m06_06":1.8063802342914,"nc_p50_m07_06":1.98340147457891,"nc_p50_m08_06":1.16084426463805,"nc_p50_m09_06":0.530226760031326,"nc_p50_m10_06":0.305149607766676,"nc_p50_m11_06":0.157318777687434,"nc_p50_m12_06":0.0708536995051434,"nc_p75_m01_06":0.0412984148673297,"nc_p75_m02_06":0.0217063510544334,"nc_p75_m03_06":0.0132236167232737,"nc_p75_m04_06":0.013196501189879,"nc_p75_m05_06":0.909154413241198,"nc_p75_m06_06":2.63235756647282,"nc_p75_m07_06":3.41619195809612,"nc_p75_m08_06":1.80112508215393,"nc_p75_m09_06":0.845778604397043,"nc_p75_m10_06":0.421884972217166,"nc_p75_m11_06":0.19941966337652,"nc_p75_m12_06":0.0895341942370667,"nc_p90_m01_06":0.0493626817976279,"nc_p90_m02_06":0.0244275173264492,"nc_p90_m03_06":0.0149718453798872,"nc_p90_m04_06":0.110343978793575,"nc_p90_m05_06":1.62513659583496,"nc_p90_m06_06":3.65591499223756,"nc_p90_m07_06":4.71808579845102,"nc_p90_m08_06":3.07035472226349,"nc_p90_m09_06":1.30770114271375,"nc_p90_m10_06":0.586976027591288,"nc_p90_m11_06":0.255278263184522,"nc_p90_m12_06":0.109572303721913,"nc_p10_m01_20":0.0196158092082693,"nc_p10_m02_20":0.0120877479426651,"nc_p10_m03_20":0.00838710970768905,"nc_p10_m04_20":0.00834714245789075,"nc_p10_m05_20":0.0240841936897277,"nc_p10_m06_20":0.785796973517317,"nc_p10_m07_20":1.00907113115192,"nc_p10_m08_20":0.580403235012916,"nc_p10_m09_20":0.239523680607712,"nc_p10_m10_20":0.129140795758892,"nc_p10_m11_20":0.0694789964775816,"nc_p10_m12_20":0.0358210907719725,"nc_p25_m01_20":0.0319225594804218,"nc_p25_m02_20":0.0184381157437711,"nc_p25_m03_20":0.0118465798862915,"nc_p25_m04_20":0.00991007938774928,"nc_p25_m05_20":0.0437137362272158,"nc_p25_m06_20":1.23616598117729,"nc_p25_m07_20":1.30405955742743,"nc_p25_m08_20":0.787162100368609,"nc_p25_m09_20":0.308658484056728,"nc_p25_m10_20":0.183057098930962,"nc_p25_m11_20":0.101048824115025,"nc_p25_m12_20":0.0573559190161008,"nc_p50_m01_20":0.0521323372424434,"nc_p50_m02_20":0.0323674483336387,"nc_p50_m03_20":0.0229300860478304,"nc_p50_m04_20":0.0278953207508135,"nc_p50_m05_20":0.437777300964592,"nc_p50_m06_20":2.03210065772628,"nc_p50_m07_20":2.00763060833698,"nc_p50_m08_20":1.17780634689771,"nc_p50_m09_20":0.544096348804935,"nc_p50_m10_20":0.326958370928494,"nc_p50_m11_20":0.196962127275675,"nc_p50_m12_20":0.095539088383658,"nc_p75_m01_20":0.0647484869997941,"nc_p75_m02_20":0.0404462365122421,"nc_p75_m03_20":0.0302132634046532,"nc_p75_m04_20":0.0370252197661313,"nc_p75_m05_20":0.586411610318686,"nc_p75_m06_20":2.25655984915631,"nc_p75_m07_20":2.57913665330705,"nc_p75_m08_20":1.48293435536187,"nc_p75_m09_20":0.696128868979222,"nc_p75_m10_20":0.423203776199694,"nc_p75_m11_20":0.239566536690999,"nc_p75_m12_20":0.122218915611058,"nc_p90_m01_20":0.100523342627805,"nc_p90_m02_20":0.0774482988452804,"nc_p90_m03_20":0.0645110686179184,"nc_p90_m04_20":0.058379345254354,"nc_p90_m05_20":1.10323359152204,"nc_p90_m06_20":3.60655439347768,"nc_p90_m07_20":4.17083347433984,"nc_p90_m08_20":2.07610943680124,"nc_p90_m09_20":1.05022721274552,"nc_p90_m10_20":0.627597847829362,"nc_p90_m11_20":0.331441747611989,"nc_p90_m12_20":0.177789638333956,"nc_p10_m01_50":0.0235213971191782,"nc_p10_m02_50":0.0150368849777335,"nc_p10_m03_50":0.0105186475748327,"nc_p10_m04_50":0.00856948956704431,"nc_p10_m05_50":0.0448026681653545,"nc_p10_m06_50":1.01699452349685,"nc_p10_m07_50":0.983417093440261,"nc_p10_m08_50":0.308772571343713,"nc_p10_m09_50":0.173649684112568,"nc_p10_m10_50":0.117921730277192,"nc_p10_m11_50":0.0800529925837918,"nc_p10_m12_50":0.0418349655516039,"nc_p25_m01_50":0.0330093078921854,"nc_p25_m02_50":0.0192554535978642,"nc_p25_m03_50":0.0127354407326474,"nc_p25_m04_50":0.0111064045447482,"nc_p25_m05_50":0.144394450318725,"nc_p25_m06_50":1.47512520802426,"nc_p25_m07_50":1.28066925070156,"nc_p25_m08_50":0.616601870663724,"nc_p25_m09_50":0.273462320365564,"nc_p25_m10_50":0.184305955741002,"nc_p25_m11_50":0.125360519338418,"nc_p25_m12_50":0.0646754276728033,"nc_p50_m01_50":0.0562684852234553,"nc_p50_m02_50":0.0357636452818038,"nc_p50_m03_50":0.0267598520698169,"nc_p50_m04_50":0.0508613643158299,"nc_p50_m05_50":0.666709480947171,"nc_p50_m06_50":2.23193886126682,"nc_p50_m07_50":1.80088052335733,"nc_p50_m08_50":0.968978183147272,"nc_p50_m09_50":0.452618776552365,"nc_p50_m10_50":0.322672100981402,"nc_p50_m11_50":0.221587305998961,"nc_p50_m12_50":0.105620330198269,"nc_p75_m01_50":0.0784598048295404,"nc_p75_m02_50":0.0572428720433994,"nc_p75_m03_50":0.0447387970669174,"nc_p75_m04_50":0.0474054652710236,"nc_p75_m05_50":1.07835823180943,"nc_p75_m06_50":2.99265665248519,"nc_p75_m07_50":2.594333030491,"nc_p75_m08_50":1.10342066283152,"nc_p75_m09_50":0.635577022233793,"nc_p75_m10_50":0.435692325124599,"nc_p75_m11_50":0.260184669723411,"nc_p75_m12_50":0.134369326322269,"nc_p90_m01_50":0.136306426948864,"nc_p90_m02_50":0.109018192006376,"nc_p90_m03_50":0.0806508385510399,"nc_p90_m04_50":0.107876250599662,"nc_p90_m05_50":1.82954975594566,"nc_p90_m06_50":4.05469332409236,"nc_p90_m07_50":3.79366971914783,"nc_p90_m08_50":1.3338235470919,"nc_p90_m09_50":0.865207507173232,"nc_p90_m10_50":0.6314302955074,"nc_p90_m11_50":0.370302513876792,"nc_p90_m12_50":0.212342751802343,"nc_p10_m01_80":0.0269669261276967,"nc_p10_m02_80":0.0186288550757016,"nc_p10_m03_80":0.0153103769607652,"nc_p10_m04_80":0.0181896580463014,"nc_p10_m05_80":0.165600680736191,"nc_p10_m06_80":1.01723037426566,"nc_p10_m07_80":0.328949704536239,"nc_p10_m08_80":0.139535386356846,"nc_p10_m09_80":0.0774975307116765,"nc_p10_m10_80":0.0665410841319856,"nc_p10_m11_80":0.0642013446373113,"nc_p10_m12_80":0.0433717515265612,"nc_p25_m01_80":0.0366142085510578,"nc_p25_m02_80":0.0248041664263084,"nc_p25_m03_80":0.0310619988177943,"nc_p25_m04_80":0.0371672979222502,"nc_p25_m05_80":0.397278850157788,"nc_p25_m06_80":1.52677958000018,"nc_p25_m07_80":0.430236982781336,"nc_p25_m08_80":0.186520055862916,"nc_p25_m09_80":0.112321588020349,"nc_p25_m10_80":0.126396835305554,"nc_p25_m11_80":0.110977768069234,"nc_p25_m12_80":0.0632176088057924,"nc_p50_m01_80":0.0765693771240403,"nc_p50_m02_80":0.0594053974455339,"nc_p50_m03_80":0.0618245439608877,"nc_p50_m04_80":0.138860258556748,"nc_p50_m05_80":1.15303082630618,"nc_p50_m06_80":2.76691895690949,"nc_p50_m07_80":1.50895079062496,"nc_p50_m08_80":0.549803144990276,"nc_p50_m09_80":0.314887262822063,"nc_p50_m10_80":0.35411489869643,"nc_p50_m11_80":0.276574650370243,"nc_p50_m12_80":0.139878313309427,"nc_p75_m01_80":0.0950317194623877,"nc_p75_m02_80":0.106118643866045,"nc_p75_m03_80":0.117684928273239,"nc_p75_m04_80":0.194143525132364,"nc_p75_m05_80":1.56133141323194,"nc_p75_m06_80":3.76919696996408,"nc_p75_m07_80":1.58775215976769,"nc_p75_m08_80":0.375234481448894,"nc_p75_m09_80":0.336043391943766,"nc_p75_m10_80":0.388959520820575,"nc_p75_m11_80":0.255122401617763,"nc_p75_m12_80":0.152027440338407,"nc_p90_m01_80":0.159736720330251,"nc_p90_m02_80":0.261140070797598,"nc_p90_m03_80":0.217503503257678,"nc_p90_m04_80":0.360124153872487,"nc_p90_m05_80":2.27384163095425,"nc_p90_m06_80":4.93700926392408,"nc_p90_m07_80":3.41367419023846,"nc_p90_m08_80":0.602904799489096,"nc_p90_m09_80":0.548884395028863,"nc_p90_m10_80":0.643319491042418,"nc_p90_m11_80":0.35796333627053,"nc_p90_m12_80":0.218544266983221}}

        response = self.execute_as_dict(get_kwt_hydrologic_variability_by_id_query, args, fetch_one = True)
        return response
