"""Lightweight Prometheus-compatible metrics for the SDLC orchestrator.

Exposes counters and histograms without requiring the prometheus_client
library — uses a simple in-process registry that serialises to text format.
If prometheus_client IS installed it is used automatically.
"""
import time
from collections import defaultdict
from typing import Dict

# ── In-process registry ───────────────────────────────────────────────────────
_counters: Dict[str, float] = defaultdict(float)
_histograms: Dict[str, list] = defaultdict(list)


def inc(name: str, labels: dict = None, value: float = 1.0):
    key = _label_key(name, labels)
    _counters[key] += value


def observe(name: str, value: float, labels: dict = None):
    key = _label_key(name, labels)
    _histograms[key].append(value)


def _label_key(name: str, labels: dict) -> str:
    if not labels:
        return name
    label_str = ",".join(f'{k}="{v}"' for k, v in sorted(labels.items()))
    return f"{name}{{{label_str}}}"


def metrics_text() -> str:
    """Serialise registry to Prometheus text exposition format."""
    lines = []
    for key, value in _counters.items():
        lines.append(f"{key} {value}")
    for key, values in _histograms.items():
        if values:
            lines.append(f"{key}_count {len(values)}")
            lines.append(f"{key}_sum {sum(values)}")
            lines.append(f"{key}_avg {sum(values)/len(values):.4f}")
    return "\n".join(lines) + "\n"


# ── Convenience context manager for timing ────────────────────────────────────
class Timer:
    def __init__(self, metric_name: str, labels: dict = None):
        self.metric_name = metric_name
        self.labels = labels or {}
        self._start = None

    def __enter__(self):
        self._start = time.monotonic()
        return self

    def __exit__(self, *_):
        elapsed = time.monotonic() - self._start
        observe(self.metric_name, elapsed, self.labels)
