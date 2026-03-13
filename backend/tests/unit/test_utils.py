from pathlib import Path
import json
import io
import zipfile

def load_fixture(*subpath_parts: str) -> dict:
    """
        Load a JSON fixture file located under tests/unit/fixtures.

        Example: load_fixture("climate", "router", "climateStationsResponse.json")
    """
    base = Path(__file__).parent.parent / "unit/fixtures"
    fixture_path = base.joinpath(*subpath_parts).resolve()
    with fixture_path.open() as f:
        return json.load(f)

def assert_zips_equal(data1, data2):
    with zipfile.ZipFile(io.BytesIO(data1)) as z1, \
         zipfile.ZipFile(io.BytesIO(data2)) as z2:
        assert z1.namelist() == z2.namelist()
        for name in z1.namelist():
            assert z1.read(name) == z2.read(name), f"Mismatch in {name}"
