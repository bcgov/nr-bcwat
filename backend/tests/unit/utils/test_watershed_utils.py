from utils.watershed import (
    build_climate_chart_data
)

def test_build_climate_chart_data():
    """
        Test building the climate chart data. Simple reformatting data function
    """
    # Simple case of reformatting
    watershed_metadata = {
        "watershed_metadata": {
            "tave_monthly_hist": [1,2,3,4,5,6,7,8,9,10,11,12],
            "tave_monthly_future_min": [1,2,3,4,5,6,7,8,9,10,11,12],
            "tave_monthly_future_max": [1,2,3,4,5,6,7,8,9,10,11,12],
            "ppt_monthly_hist": [1,2,3,4,5,6,7,8,9,10,11,12],
            "ppt_monthly_future_min": [1,2,3,4,5,6,7,8,9,10,11,12],
            "ppt_monthly_future_max": [1,2,3,4,5,6,7,8,9,10,11,12],
            "pas_monthly_hist": [1,2,3,4,5,6,7,8,9,10,11,12],
            "pas_monthly_future_min": [1,2,3,4,5,6,7,8,9,10,11,12],
            "pas_monthly_future_max": [1,2,3,4,5,6,7,8,9,10,11,12]
        }
    }

    response = build_climate_chart_data(watershed_metadata)
    assert response['temperature']['historical'] == [1,2,3,4,5,6,7,8,9,10,11,12]
    assert response['temperature']['future'] == [{"min": i+1, "max": i+1} for i in range(12)]
    assert response['precipitation']['historical'] == [1,2,3,4,5,6,7,8,9,10,11,12]
    assert response['precipitation']['future'] == [{"min": i+1, "max": i+1} for i in range(12)]
    assert response['snow']['historical'] == [1,2,3,4,5,6,7,8,9,10,11,12]
    assert response['snow']['future'] == [{"min": i+1, "max": i+1} for i in range(12)]

    # Fill null behavior
    watershed_metadata = {
        "watershed_metadata": {
            # Nothing in here!!!
            # "tave_monthly_hist": [1,2,3,4,5,6,7,8,9,10,11,12],
            # "tave_monthly_future_min": [1,2,3,4,5,6,7,8,9,10,11,12],
            # "tave_monthly_future_max": [1,2,3,4,5,6,7,8,9,10,11,12],
            # "ppt_monthly_hist": [1,2,3,4,5,6,7,8,9,10,11,12],
            # "ppt_monthly_future_min": [1,2,3,4,5,6,7,8,9,10,11,12],
            # "ppt_monthly_future_max": [1,2,3,4,5,6,7,8,9,10,11,12],
            # "pas_monthly_hist": [1,2,3,4,5,6,7,8,9,10,11,12],
            # "pas_monthly_future_min": [1,2,3,4,5,6,7,8,9,10,11,12],
            # "pas_monthly_future_max": [1,2,3,4,5,6,7,8,9,10,11,12]
        }
    }

    response = build_climate_chart_data(watershed_metadata)
    assert response['temperature']['historical'] == [None] * 12
    assert response['temperature']['future'] == [{"min": None, "max": None}] * 12
    assert response['precipitation']['historical'] == [None] * 12
    assert response['precipitation']['future'] == [{"min": None, "max": None}] * 12
    assert response['snow']['historical'] == [None] * 12
    assert response['snow']['future'] == [{"min": None, "max": None}] * 12

