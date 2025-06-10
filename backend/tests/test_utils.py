import math
import polars as pl
from utils.streamflow import prepare_lazyframes, compute_total_runoff, compute_monthly_flow_statistics, compute_flow_exceedance

def test_generate_total_runoff(streamflow_input_fixture, total_runoff_output_fixture):
    """
      Unit test of Util function that computes total runoff
    """
    fd_lf = prepare_lazyframes(streamflow_input=streamflow_input_fixture)

    total_runoff = compute_total_runoff(fd_lf).collect().to_dicts()

    # I know this is slow - but its easier to debug when tests fail by seeing specific value failures, rather than object drift that would appear with `assert result_dicts == total_runoff_output_fixture`
    for row in total_runoff:
      year = row['year']
      for expected_row in total_runoff_output_fixture:
        if expected_row['year'] == year:
           assert row['value'] == expected_row['value'], f"Year {year}, value mismatch: {row['value']} != {expected_row['value']}"

def test_generate_monthly_flow_statistics(streamflow_input_fixture):
    """
      Unit test of Util function that computes monthly flow statistics
    """

    fd_lf = prepare_lazyframes(streamflow_input=streamflow_input_fixture)

    monthly_summary = compute_monthly_flow_statistics(fd_lf).collect().to_dicts()

    expected = {
        1: {
            "max": 30.6,
            "p75": 4.84,
            "median": 3.4,
            "p25": 1.4,
            "min": 0.44
        },
        2: {
          "max": 23.2,
          "p75": 4.36,
          "median": 3.37,
          "p25": 1.33,
          "min": 0.5
        },
        3: {
          "max": 14.8,
          "p75": 4.45,
          "median": 3.46,
          "p25": 1.4925,
          "min": 0.549
        },
        4: {
          "max": 53,
          "p75": 7.05,
          "median": 4.25,
          "p25": 1.68,
          "min": 0.261
        },
        5: {
          "max": 143,
          "p75": 34.8,
          "median": 19.8,
          "p25": 8.21,
          "min": 0.913
        },
        6: {
          "max": 211,
          "p75": 63.4,
          "median": 43.5,
          "p25": 26.4,
          "min": 1.15
        },
        7: {
          "max": 170,
          "p75": 48.1,
          "median": 31.5,
          "p25": 12.3,
          "min": 0.777
        },
        8: {
          "max": 98.8,
          "p75": 21.95,
          "median": 3.72,
          "p25": 2.145,
          "min": 0.515
        },
        9: {
          "max": 76.3,
          "p75": 11.6,
          "median": 2.23,
          "p25": 1.58,
          "min": 0.314
        },
        10: {
          "max": 48.7,
          "p75": 8.59,
          "median": 2.05,
          "p25": 1.41,
          "min": 0.377
        },
        11: {
          "max": 61.4,
          "p75": 7.36,
          "median": 1.94,
          "p25": 1.4,
          "min": 0.456
        },
        12: {
          "max": 72.1,
          "p75": 6.34,
          "median": 3.4,
          "p25": 1.46,
          "min": 0.17
        }
    }

    for row in monthly_summary:
      month = row["month"]
      if month in expected:
          for key in ["min", "max", "median", "p25", "p75"]:
            assert round(row[key] + 0.1, 1) == round(expected[month][key] + 0.1, 1), f"Month {month}, metric {key} mismatch: {round(row[key] + 1,1)} != {round(expected[month][key] + 1,1)}"

def test_flow_exceedance(streamflow_input_fixture, flow_exceedance_output_fixture):
  """
    Unit test of Util Function that Computes Flow Exceedance
  """

  fd_lf = prepare_lazyframes(streamflow_input=streamflow_input_fixture)

  lf_exceedance = compute_flow_exceedance(fd_lf).collect().to_dicts()

  pairs = zip(lf_exceedance, flow_exceedance_output_fixture)

  value_mismatches = []
  exceedance_mismatches = []

  # I added this block to output all of the mismatches. Otherwise, it would be near impossible to debug.
  for i, (x, y) in enumerate(pairs):
      # The Additions are to escape rounding problems caused by Pythons method of rounding - Bankers Rounding
      x_val = round(x['value'] + 0.00001, 5)
      y_val = round(y['value'] + 0.00001, 5)
      if x_val != y_val:
          value_mismatches.append((i, x['value'], y['value']))

      x_exc = round(x['exceedance'] + 0.00001, 5)
      y_exc = round(y['exceedance'] + 0.00001, 5)
      if x_exc != y_exc:
          exceedance_mismatches.append((i, x['exceedance'], y['exceedance']))

  assert not value_mismatches, f"Value mismatches at indices: {value_mismatches}"
  assert not exceedance_mismatches, f"Exceedance mismatches at indices: {exceedance_mismatches}"
