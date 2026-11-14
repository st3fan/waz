"""Single-process JSON persistence for the shared dinner plan."""

from __future__ import annotations

from datetime import date, timedelta
import json
import os
from pathlib import Path
import tempfile
from threading import RLock


def monday_of(day: date) -> date:
    return day - timedelta(days=day.weekday())


def week_days(day: date) -> list[date]:
    monday = monday_of(day)
    return [monday + timedelta(days=offset) for offset in range(7)]


class PlanStore:
    """Read and update one shared JSON file in a single server process."""

    def __init__(self, path: Path):
        self.path = path
        self._lock = RLock()

    def read(self) -> dict[date, str]:
        with self._lock:
            if not self.path.exists():
                return {}
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("Dinner plan must be a JSON object")
            result: dict[date, str] = {}
            for key, value in raw.items():
                parsed = date.fromisoformat(key)
                if parsed.isoformat() != key or not isinstance(value, str) or not value.strip():
                    raise ValueError("Dinner plan contains an invalid entry")
                result[parsed] = value
            return result

    def replace_day(self, day: date, dinner: str) -> None:
        with self._lock:
            plan = self.read()
            plan[day] = dinner
            self._write(plan)

    def fill_missing(self, dinners: dict[date, str]) -> None:
        with self._lock:
            plan = self.read()
            for day, dinner in dinners.items():
                plan.setdefault(day, dinner)
            self._write(plan)

    def _write(self, plan: dict[date, str]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {day.isoformat(): dinner for day, dinner in sorted(plan.items())}
        temporary: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.path.parent, prefix=".plan-", delete=False
            ) as stream:
                temporary = stream.name
                json.dump(payload, stream, indent=2, ensure_ascii=False)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)
