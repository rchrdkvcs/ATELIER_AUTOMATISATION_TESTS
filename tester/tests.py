from typing import Any
from .client import ApiClient, ApiResponse

BASE_URL = "https://api.agify.io"


def _test_result(name: str, passed: bool, details: str = "", latency_ms: float | None = None) -> dict[str, Any]:
    result = {
        "name": name,
        "status": "PASS" if passed else "FAIL",
        "details": details,
    }
    if latency_ms is not None:
        result["latency_ms"] = round(latency_ms, 1)
    return result


def run_all(client: ApiClient) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    base_response = client.get(BASE_URL, params={"name": "michael"})
    results.append(_payload_status_test(base_response))
    results.append(_content_type_json_test(base_response))
    results.append(_schema_fields_test(base_response))
    results.append(_field_types_test(base_response))

    missing_name_response = client.get(BASE_URL)
    results.append(_missing_name_test(missing_name_response))

    empty_name_response = client.get(BASE_URL, params={"name": ""})
    results.append(_empty_name_test(empty_name_response))

    numeric_name_response = client.get(BASE_URL, params={"name": "123"})
    results.append(_numeric_name_test(numeric_name_response))

    return results


def _payload_status_test(response: ApiResponse) -> dict[str, Any]:
    if response.status_code == 200 and response.json is not None:
        return _test_result(
            "GET /?name=michael returns 200",
            True,
            latency_ms=response.latency_ms,
        )
    details = response.error or f"status={response.status_code}"
    return _test_result("GET /?name=michael returns 200", False, details, response.latency_ms)


def _content_type_json_test(response: ApiResponse) -> dict[str, Any]:
    content_type = response.headers.get("Content-Type", "")
    passed = response.status_code == 200 and content_type.lower().startswith("application/json")
    details = "Content-Type is not JSON" if not passed else ""
    return _test_result("Response Content-Type JSON", passed, details, response.latency_ms)


def _schema_fields_test(response: ApiResponse) -> dict[str, Any]:
    payload = response.json
    expected = {"name", "age", "count"}
    if not isinstance(payload, dict):
        return _test_result("Response contains name/age/count", False, "JSON response is not an object", response.latency_ms)
    missing = expected - payload.keys()
    if missing:
        return _test_result("Response contains name/age/count", False, f"Missing fields: {', '.join(sorted(missing))}", response.latency_ms)
    return _test_result("Response contains name/age/count", True, "", response.latency_ms)


def _field_types_test(response: ApiResponse) -> dict[str, Any]:
    payload = response.json
    if not isinstance(payload, dict):
        return _test_result("Field types are correct", False, "JSON response is not an object", response.latency_ms)
    name_ok = isinstance(payload.get("name"), str)
    age = payload.get("age")
    count = payload.get("count")
    age_ok = age is None or isinstance(age, int)
    count_ok = isinstance(count, int)
    if not (name_ok and age_ok and count_ok):
        details = []
        if not name_ok:
            details.append("name is not a string")
        if not age_ok:
            details.append("age is not int or null")
        if not count_ok:
            details.append("count is not int")
        return _test_result("Field types are correct", False, "; ".join(details), response.latency_ms)
    return _test_result("Field types are correct", True, "", response.latency_ms)


def _missing_name_test(response: ApiResponse) -> dict[str, Any]:
    passed = response.status_code == 422 and isinstance(response.json, dict) and response.json.get("error") is not None
    details = "Expected 422 with error payload" if not passed else ""
    return _test_result("Missing name returns 422", passed, details, response.latency_ms)


def _empty_name_test(response: ApiResponse) -> dict[str, Any]:
    payload = response.json
    passed = (
        response.status_code == 200
        and isinstance(payload, dict)
        and payload.get("name") == ""
        and payload.get("age") is None
        and payload.get("count") == 0
    )
    details = "Empty name should return name=\"\", age=null, count=0" if not passed else ""
    return _test_result("Empty name returns null age + count 0", passed, details, response.latency_ms)


def _numeric_name_test(response: ApiResponse) -> dict[str, Any]:
    payload = response.json
    passed = (
        response.status_code == 200
        and isinstance(payload, dict)
        and payload.get("name") == "123"
    )
    details = "Numeric name should be echoed as a string" if not passed else ""
    return _test_result("Numeric name is echoed as string", passed, details, response.latency_ms)
