import os
import json
import requests
import sys
from dotenv import load_dotenv
from urllib.parse import urlencode
from jsonschema import validate, ValidationError
import time

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:5173/api")

with open("../../documentation/openapi.json") as f:
    spec = json.load(f)

def convert_nullable(schema):
    """
        Recursively convert None -> null values. Otherwise, schema validation fails.
    """
    if isinstance(schema, dict):
        if schema.get("nullable") and "type" in schema:
            t = schema["type"]
            schema["type"] = [t, "null"] if isinstance(t, str) else list(set(t + ["null"]))
            del schema["nullable"]
        for key in schema:
            convert_nullable(schema[key])
    elif isinstance(schema, list):
        for item in schema:
            convert_nullable(item)
    return schema


def resolve_path(path_template, path_params, query_params):
    """
        Construct full path using path params, query params.

        TODO - Allow for overrides, to handle multiple cases? With/without query params?
    """
    for key, value in path_params.items():
        path_template = path_template.replace(f"{{{key}}}", str(value))
    if not query_params:
        return path_template
    return f"{path_template}?{urlencode(query_params)}"


def extract_sample_payload(request_body):
    """
        Executes POST/PUT/PATCH Request using example object provided in openapi.json.

        As this API currently only uses GET Requests, unused, but included for future utility.
    """
    try:
        return next(iter(
            request_body["content"]["application/json"].get("example", {}) or
            request_body["content"]["application/json"]["examples"].values()
        ))
    except Exception:
        return {}

def extract_param_value(param):
    """
        Used to fetch values to replace pathParams.
        {id} -> (1)
    """
    # Prefer parameter-level "example"
    if "example" in param:
        return param["example"]
    # Fallback to schema-level "example"
    if "schema" in param and "example" in param["schema"]:
        return param["schema"]["example"]
    # Fallback defaults
    param_type = param.get("schema", {}).get("type")
    if param_type == "integer":
        return 1
    if param_type == "number":
        return 1.0
    if param_type == "boolean":
        return True
    return "sample"  # default for string or unknown types

def test_endpoint(path, method, operation):
    """
        Integration test for path as found within openapi.json.

        Validates status codes, output schema, with what is included within documentation.
    """
    print("-" * 120)
    method_upper = method.upper()

    path_params = {
        p["name"]: extract_param_value(p)
        for p in operation.get("parameters", [])
        if p.get("in") == "path"
    }

    query_params = {
        p["name"]: extract_param_value(p)
        for p in operation.get("parameters", [])
        if p.get("in") == "query"
    }

    resolved_path = resolve_path(path, path_params, query_params)
    full_url = BASE_URL + resolved_path

    payload = None
    if "requestBody" in operation and method_upper in ["POST", "PUT", "PATCH"]:
        payload = extract_sample_payload(operation["requestBody"])

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    print(f"Testing {method_upper} {full_url}")
    start = time.perf_counter()

    response = requests.request(method_upper, full_url, headers=headers, json=payload)
    duration = time.perf_counter() - start

    print(f"    Status: {response.status_code}")
    print(f"    Duration: {duration:.3f}s")

    responses = operation.get("responses", {})

    # Get numeric status codes only (ignore "default" or "4xx/5xx")
    valid_codes = [
        int(code) for code in responses.keys()
        if code.isdigit() and 200 <= int(code) < 400
    ]

    if not valid_codes:
        raise ValueError(f"No valid 2xx or 3xx response codes defined for this operation")

    expected_code = str(min(valid_codes))  # pick the lowest success/redirect code

    assert str(response.status_code) == expected_code, f"Expected {expected_code}, got {response.status_code}"

    response_schema = (
        responses[expected_code]
        .get("content", {})
        .get("application/json", {})
        .get("schema")
    )

    response_schema = convert_nullable(response_schema)

    if response_schema:
        try:
            json_data = response.json()
            validate(instance=json_data, schema=response_schema)
            print(f"  \033[92m✓\033[0m Schema validation succeeded.")
        except ValidationError as ve:
            print(f" \033[91m❌\033[0m Schema validation failed: {ve.message}")
            raise
        except Exception:
            print("  \033[93m⚠️\033[0m Could not parse JSON from response")
    else:
        print(" \033[93m⚠️\033[0m No schema provided for validation")


failed_tests = []

def main():
    """
        Iterates over all paths within openapi.json, testing each METHOD available for each Endpoint.
    """
    paths = spec.get("paths", {})
    for path, methods in paths.items():
        for method, operation in methods.items():
            try:
                test_endpoint(path, method, operation)
            except Exception as e:
                print(f" \033[91m❌\033[0m Test failed: {e}")
                failed_tests.append(f"{method.upper()} {path}")

    print("\n" + "=" * 120)
    if failed_tests:
        print(" \033[91m❌ Failed Tests:\033[0m")
        for test in failed_tests:
            print(f"   - {test}")
        print(f" \033[91m{len(failed_tests)} test(s) failed.\033[0m")

        # Indiciate Failure to Github Action Runner
        sys.exit(1)
    else:
        print(" \033[92m✓ All tests passed successfully.\033[0m")

if __name__ == "__main__":
    main()
