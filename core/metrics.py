from __future__ import annotations

from threading import Lock


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: dict[tuple[str, str], int] = {}
        self._histograms: dict[str, list[float]] = {}

    def increment(self, name: str, labels: str = "") -> None:
        with self._lock:
            key = (name, labels)
            self._counters[key] = self._counters.get(key, 0) + 1

    def observe(self, name: str, value: float) -> None:
        with self._lock:
            self._histograms.setdefault(name, []).append(value)

    def render(self) -> str:
        lines: list[str] = []
        with self._lock:
            for (name, labels), value in sorted(self._counters.items()):
                label_part = f"{{{labels}}}" if labels else ""
                lines.append(f"{name}{label_part} {value}")

            for name, values in sorted(self._histograms.items()):
                if not values:
                    continue
                ordered = sorted(values)
                count = len(ordered)
                lines.extend([
                    f"{name}_count {count}",
                    f"{name}_sum {sum(ordered):.6f}",
                    f"{name}_min {ordered[0]:.6f}",
                    f"{name}_max {ordered[-1]:.6f}",
                ])
        return "\n".join(lines) + "\n"


metrics = MetricsRegistry()
