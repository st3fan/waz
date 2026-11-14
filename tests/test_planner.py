from datetime import date
from types import SimpleNamespace

import pytest

from waz.planner import Dinner, DinnerPlan, OpenAIPlanner, PlanningError


def test_planner_requests_history_and_validates_dates(monkeypatch, tmp_path):
    history = tmp_path / "previous.txt"
    history.write_text("2026-11-01: Pasta\n", encoding="utf-8")
    requested = date(2026, 11, 16)
    seen = {}

    def parse(**kwargs):
        seen.update(kwargs)
        return SimpleNamespace(output_parsed=DinnerPlan(dinners=[Dinner(date=requested, dinner=" Tacos ")]))

    monkeypatch.setenv("OPENAI_API_KEY", "test-only")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setattr("waz.planner.OpenAI", lambda: SimpleNamespace(responses=SimpleNamespace(parse=parse)))

    assert OpenAIPlanner(history).plan([requested], {}) == {requested: "Tacos"}
    assert "2026-11-01: Pasta" in seen["input"][1]["content"]
    assert seen["text_format"] is DinnerPlan


def test_planner_rejects_wrong_dates(monkeypatch, tmp_path):
    history = tmp_path / "previous.txt"
    history.write_text("Pasta\n", encoding="utf-8")
    wrong = date(2026, 11, 17)
    response = SimpleNamespace(output_parsed=DinnerPlan(dinners=[Dinner(date=wrong, dinner="Soup")]))
    monkeypatch.setenv("OPENAI_API_KEY", "test-only")
    monkeypatch.setenv("OPENAI_MODEL", "test-model")
    monkeypatch.setattr("waz.planner.OpenAI", lambda: SimpleNamespace(responses=SimpleNamespace(parse=lambda **_: response)))

    with pytest.raises(PlanningError, match="invalid dinner plan"):
        OpenAIPlanner(history).plan([date(2026, 11, 16)], {})


def test_planner_requires_api_configuration(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    with pytest.raises(PlanningError, match="OPENAI_API_KEY"):
        OpenAIPlanner(tmp_path / "missing.txt").plan([date(2026, 11, 16)], {})
