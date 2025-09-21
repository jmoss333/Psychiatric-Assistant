"""Prometheus and OpenTelemetry friendly metrics exporters."""
from __future__ import annotations

from typing import Any, Dict

from prometheus_client import Counter, Histogram

TRANSLATION_COUNTER = Counter(
    "bridge_translations_total", "Number of MCP translations", ["method", "success"]
)
TRANSLATION_LATENCY = Histogram(
    "bridge_translation_latency_seconds", "Translation latency", ["method"]
)


class MetricsExporter:
    """Minimal metrics wrapper used by the bridge."""

    def record_translation(self, method: str, success: bool, latency_seconds: float) -> None:
        TRANSLATION_COUNTER.labels(method=method, success=str(success).lower()).inc()
        TRANSLATION_LATENCY.labels(method=method).observe(latency_seconds)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "counters": {
                "bridge_translations_total": TRANSLATION_COUNTER._value.get(),  # type: ignore[attr-defined]
            }
        }
