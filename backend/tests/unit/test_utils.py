from pathlib import Path
import json

def load_fixture(*subpath_parts: str) -> dict:
    """
        Load a JSON fixture file located under tests/unit/fixtures.

        Example: load_fixture("climate", "router", "climateStationsResponse.json")
    """
    base = Path(__file__).parent.parent / "unit/fixtures"
    fixture_path = base.joinpath(*subpath_parts).resolve()
    with fixture_path.open() as f:
        return json.load(f)
