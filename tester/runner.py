from datetime import datetime, timezone
import statistics
from .client import ApiClient
from .tests import run_all

API_NAME = "Agify"


def _safe_round(value: float | None) -> float | None:
    return round(value, 1) if value is not None else None


def run_tests() -> dict:
    client = ApiClient(timeout=3, max_retries=1, backoff=1.2)
    tests = run_all(client)
    latencies = [test.get("latency_ms", 0.0) for test in tests if test.get("latency_ms") is not None]
    passed = sum(1 for test in tests if test["status"] == "PASS")
    failed = sum(1 for test in tests if test["status"] != "PASS")
    error_rate = failed / len(tests) if tests else 0.0
    summary = {
        "passed": passed,
        "failed": failed,
        "error_rate": round(error_rate, 3),
        "latency_ms_avg": _safe_round(statistics.mean(latencies)) if latencies else None,
        "latency_ms_p95": _safe_round(statistics.quantiles(latencies, n=100)[94]) if len(latencies) >= 2 else (latencies[0] if latencies else None),
        "total_requests": len(tests),
        "availability": "UP" if failed == 0 else "DEGRADED",
    }
    return {
        "api": API_NAME,
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
        "summary": summary,
        "tests": tests,
    }
