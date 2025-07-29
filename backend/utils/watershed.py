import json

def build_climate_chart_data(watershed_metadata: dict) -> dict:
    """
        Unpack the Precipitation/Snow/Temperature Climate Data for ease of integration with Frontend

        Ensure that any missing data is Null filled - IE Key does not exist Err
    """
    def safe_get(path: list, default=None):
        """
            Safely get a nested value from a dict.
            path: list of keys to traverse
        """
        curr = watershed_metadata
        try:
            for key in path:
                curr = curr[key]
            return curr
        except (KeyError, TypeError):
            return default

    chart_keys = {
        "temperature": {
            "hist": ["watershed_metadata", "tave_monthly_hist"],
            "fut_min": ["watershed_metadata", "tave_monthly_future_min"],
            "fut_max": ["watershed_metadata", "tave_monthly_future_max"]
        },
        "precipitation": {
            "hist": ["watershed_metadata", "ppt_monthly_hist"],
            "fut_min": ["watershed_metadata", "ppt_monthly_future_min"],
            "fut_max": ["watershed_metadata", "ppt_monthly_future_max"]
        },
        "snow": {
            "hist": ["watershed_metadata", "pas_monthly_hist"],
            "fut_min": ["watershed_metadata", "pas_monthly_future_min"],
            "fut_max": ["watershed_metadata", "pas_monthly_future_max"]
        }
    }

    climate_chart_data = {}

    for category, keys in chart_keys.items():

        historical = safe_get(keys["hist"], default=[None] * 12)
        future_min = safe_get(keys["fut_min"], default=[None] * 12)
        future_max = safe_get(keys["fut_max"], default=[None] * 12)

        future_combined = [
            {"min": future_min[i], "max": future_max[i]}
            for i in range(12)
        ]

        climate_chart_data[category] = {
            "historical": historical,
            "future": future_combined
        }

    return climate_chart_data

def unpack_candidate_metadata(c_md_raw: list[dict]):
    """
        Build Candidate Metadata Sub Sections
    """

    hv_mmg = []
    hv_dv = []
    hv_cd = []

    for candidate in c_md_raw:
        hv_mmg_entry = {
            "candidate": candidate['candidate'],
            "geom": json.loads(candidate['candidate_polygon_4326'])
        }

        hv_dv_entry = candidate['candidate_month_value'].copy()
        hv_dv_entry['candidate'] = candidate['candidate']

        hv_cd_entry = {
            "station_number": candidate['candidate_station_id'],
            "station_name": candidate['candidate_name'],
            "lat": candidate['candidate_climate_data']['lat'],
            "lng": candidate['candidate_climate_data']['lon'],
            "area_km2": candidate['candidate_area_km2'],
            "min_elev": candidate['candidate_climate_data']['min_elev'],
            "avg_elev": candidate['candidate_climate_data']['avg_elev'],
            "max_elev": candidate['candidate_climate_data']['max_elev'],
            "month": candidate['candidate_climate_data']['month'],
            "ppt": candidate['candidate_climate_data']['ppt'],
            "pas": candidate['candidate_climate_data']['pas'],
            "tave": candidate['candidate_climate_data']['tave']
        }

        hv_mmg.append(hv_mmg_entry)
        hv_dv.append(hv_dv_entry)
        hv_cd.append(hv_cd_entry)

    return {
        "hydrologicVariabilityMiniMapGeoJson": hv_mmg,
        "hydrologicVariabilityDistanceValues": hv_dv,
        "hydrologicVariabilityClimateData": hv_cd
    }

def generate_hydrologic_variability(hv_raw: list[dict]) -> list[dict]:
    """
        Build Hydrologic Variability Schema
    """

    hv_computed = {
        "Candidate1": {
            "candidates": {},
            "90th": {},
            "75th": {},
            "50th": {},
            "25th": {},
            "10th": {}
        },
        "Candidate2": {
            "candidates": {},
            "90th": {},
            "75th": {},
            "50th": {},
            "25th": {},
            "10th": {}

        },
        "Candidate3": {
            "candidates": {},
            "90th": {},
            "75th": {},
            "50th": {},
            "25th": {},
            "10th": {}
        }
    }

    for entry in hv_raw:
        month = entry['month']

        hv_computed['Candidate1']['candidates'][month] = entry['month_value']['c1']
        hv_computed['Candidate1']['10th'][month] = entry['month_value']['q_m3s_c1'][0]
        hv_computed['Candidate1']['25th'][month] = entry['month_value']['q_m3s_c1'][1]
        hv_computed['Candidate1']['50th'][month] = entry['month_value']['q_m3s_c1'][2]
        hv_computed['Candidate1']['75th'][month] = entry['month_value']['q_m3s_c1'][3]
        hv_computed['Candidate1']['90th'][month] = entry['month_value']['q_m3s_c1'][4]

        hv_computed['Candidate2']['candidates'][month] = entry['month_value']['c2']
        hv_computed['Candidate2']['10th'][month] = entry['month_value']['q_m3s_c2'][0]
        hv_computed['Candidate2']['25th'][month] = entry['month_value']['q_m3s_c2'][1]
        hv_computed['Candidate2']['50th'][month] = entry['month_value']['q_m3s_c2'][2]
        hv_computed['Candidate2']['75th'][month] = entry['month_value']['q_m3s_c2'][3]
        hv_computed['Candidate2']['90th'][month] = entry['month_value']['q_m3s_c2'][4]

        hv_computed['Candidate3']['candidates'][month] = entry['month_value']['c3']
        hv_computed['Candidate3']['10th'][month] = entry['month_value']['q_m3s_c3'][0]
        hv_computed['Candidate3']['25th'][month] = entry['month_value']['q_m3s_c3'][1]
        hv_computed['Candidate3']['50th'][month] = entry['month_value']['q_m3s_c3'][2]
        hv_computed['Candidate3']['75th'][month] = entry['month_value']['q_m3s_c3'][3]
        hv_computed['Candidate3']['90th'][month] = entry['month_value']['q_m3s_c3'][4]

    return hv_computed
