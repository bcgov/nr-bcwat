import math
import polars as pl
from utils.streamflow import prepare_lazyframes, compute_total_runoff, compute_monthly_flow_statistics, compute_flow_exceedance, compute_all_metrics

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

def test_generate_monthly_flow_statistics(streamflow_input_fixture, monthly_streamflow_output_fixture):
    """
      Unit test of Util function that computes monthly flow statistics
    """

    fd_lf = prepare_lazyframes(streamflow_input=streamflow_input_fixture)

    monthly_summary = compute_monthly_flow_statistics(fd_lf).collect().to_dicts()

    for row in monthly_summary:
      month = row["month"]
      if month in monthly_streamflow_output_fixture:
          for key in ["min", "max", "median", "p25", "p75"]:
            assert round(row[key] + 0.1, 1) == round(monthly_streamflow_output_fixture[month][key] + 0.1, 1), f"Month {month}, metric {key} mismatch: {round(row[key] + 1,1)} != {round(monthly_streamflow_output_fixture[month][key] + 1,1)}"

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

def test_compute_metrics(streamflow_input_fixture, monthly_streamflow_output_fixture, total_runoff_output_fixture, flow_exceedance_output_fixture):
  """
    Unit Test of Compute Metrics - calls all util functions in sequence
  """

  flow_duration = compute_all_metrics(streamflow_input_fixture)

  assert flow_duration['totalRunoff'] == total_runoff_output_fixture

  # Rounding Issues, validate data close
  for row in flow_duration['monthlyFlowStatistics']:
      month = row["month"]
      if month in monthly_streamflow_output_fixture:
          for key in ["min", "max", "median", "p25", "p75"]:
            assert round(row[key] + 0.1, 1) == round(monthly_streamflow_output_fixture[month][key] + 0.1, 1), f"Month {month}, metric {key} mismatch: {round(row[key] + 1,1)} != {round(monthly_streamflow_output_fixture[month][key] + 1,1)}"

  pairs = zip(flow_duration['flowExceedance'], flow_exceedance_output_fixture)

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
