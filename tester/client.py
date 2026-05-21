from __future__ import annotations
import time
from dataclasses import dataclass
import requests

DEFAULT_TIMEOUT = 3
DEFAULT_MAX_RETRIES = 1
DEFAULT_BACKOFF = 1.0

@dataclass
class ApiResponse:
    status_code: int | None
    headers: dict
    text: str
    json: object | None
    latency_ms: float | None
    error: str | None = None

class ApiClient:
    def __init__(self, timeout: float = DEFAULT_TIMEOUT, max_retries: int = DEFAULT_MAX_RETRIES, backoff: float = DEFAULT_BACKOFF):
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff = backoff
        self.session = requests.Session()

    def get(self, url: str, params: dict | None = None, headers: dict | None = None) -> ApiResponse:
        attempt = 0
        while True:
            start = time.monotonic()
            try:
                response = self.session.get(url, params=params, headers=headers, timeout=self.timeout)
                latency_ms = (time.monotonic() - start) * 1000
                if response.status_code == 429 and attempt < self.max_retries:
                    time.sleep(self.backoff * (2 ** attempt))
                    attempt += 1
                    continue
                if 500 <= response.status_code < 600 and attempt < self.max_retries:
                    time.sleep(self.backoff * (2 ** attempt))
                    attempt += 1
                    continue
                data = None
                content_type = response.headers.get("Content-Type", "")
                if content_type.lower().startswith("application/json"):
                    try:
                        data = response.json()
                    except ValueError:
                        data = None
                return ApiResponse(
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    text=response.text,
                    json=data,
                    latency_ms=latency_ms,
                    error=None,
                )
            except requests.Timeout:
                latency_ms = (time.monotonic() - start) * 1000
                if attempt < self.max_retries:
                    time.sleep(self.backoff * (2 ** attempt))
                    attempt += 1
                    continue
                return ApiResponse(
                    status_code=None,
                    headers={},
                    text="",
                    json=None,
                    latency_ms=latency_ms,
                    error="timeout",
                )
            except requests.RequestException as exc:
                latency_ms = (time.monotonic() - start) * 1000
                if attempt < self.max_retries:
                    time.sleep(self.backoff * (2 ** attempt))
                    attempt += 1
                    continue
                return ApiResponse(
                    status_code=None,
                    headers={},
                    text="",
                    json=None,
                    latency_ms=latency_ms,
                    error=str(exc),
                )
