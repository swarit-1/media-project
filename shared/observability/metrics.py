import time
from collections import defaultdict
from typing import Callable

from fastapi import APIRouter, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class PrometheusMetrics:
    """Simple Prometheus-compatible metrics collector."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self._request_count: dict[tuple, int] = defaultdict(int)
        self._request_duration_sum: dict[tuple, float] = defaultdict(float)
        self._request_duration_count: dict[tuple, int] = defaultdict(int)
        self._active_requests: int = 0
        self._errors_count: dict[tuple, int] = defaultdict(int)

    def record_request(
        self, method: str, path: str, status_code: int, duration: float
    ) -> None:
        """Record a completed HTTP request."""
        key = (method, path, str(status_code))
        self._request_count[key] += 1
        self._request_duration_sum[key] += duration
        self._request_duration_count[key] += 1

        if status_code >= 400:
            error_key = (method, path, str(status_code))
            self._errors_count[error_key] += 1

    def increment_active(self) -> None:
        self._active_requests += 1

    def decrement_active(self) -> None:
        self._active_requests = max(0, self._active_requests - 1)

    def export(self) -> str:
        """Export metrics in Prometheus text format."""
        lines = []
        prefix = self.service_name.replace("-", "_")

        # Request count
        lines.append(f"# HELP {prefix}_http_requests_total Total HTTP requests")
        lines.append(f"# TYPE {prefix}_http_requests_total counter")
        for (method, path, status), count in sorted(self._request_count.items()):
            lines.append(
                f'{prefix}_http_requests_total{{method="{method}",path="{path}",status="{status}"}} {count}'
            )

        # Request duration
        lines.append(f"# HELP {prefix}_http_request_duration_seconds HTTP request duration")
        lines.append(f"# TYPE {prefix}_http_request_duration_seconds summary")
        for (method, path, status), total in sorted(self._request_duration_sum.items()):
            count = self._request_duration_count[(method, path, status)]
            lines.append(
                f'{prefix}_http_request_duration_seconds_sum{{method="{method}",path="{path}",status="{status}"}} {total:.6f}'
            )
            lines.append(
                f'{prefix}_http_request_duration_seconds_count{{method="{method}",path="{path}",status="{status}"}} {count}'
            )

        # Active requests
        lines.append(f"# HELP {prefix}_http_active_requests Active HTTP requests")
        lines.append(f"# TYPE {prefix}_http_active_requests gauge")
        lines.append(f"{prefix}_http_active_requests {self._active_requests}")

        # Error count
        lines.append(f"# HELP {prefix}_http_errors_total Total HTTP errors")
        lines.append(f"# TYPE {prefix}_http_errors_total counter")
        for (method, path, status), count in sorted(self._errors_count.items()):
            lines.append(
                f'{prefix}_http_errors_total{{method="{method}",path="{path}",status="{status}"}} {count}'
            )

        return "\n".join(lines) + "\n"


# Global metrics instances per service
_metrics_registry: dict[str, PrometheusMetrics] = {}


def get_metrics(service_name: str) -> PrometheusMetrics:
    """Get or create a metrics instance for a service."""
    if service_name not in _metrics_registry:
        _metrics_registry[service_name] = PrometheusMetrics(service_name)
    return _metrics_registry[service_name]


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP request metrics."""

    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.metrics = get_metrics(service_name)

    async def dispatch(self, request: Request, call_next):
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        self.metrics.increment_active()
        start_time = time.monotonic()

        try:
            response = await call_next(request)
            duration = time.monotonic() - start_time
            self.metrics.record_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration,
            )
            return response
        except Exception:
            duration = time.monotonic() - start_time
            self.metrics.record_request(
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration=duration,
            )
            raise
        finally:
            self.metrics.decrement_active()


def get_metrics_router(service_name: str) -> APIRouter:
    """Create a router with the /metrics endpoint."""
    router = APIRouter()
    metrics = get_metrics(service_name)

    @router.get("/metrics")
    async def prometheus_metrics():
        return Response(
            content=metrics.export(),
            media_type="text/plain; version=0.0.4; charset=utf-8",
        )

    return router
