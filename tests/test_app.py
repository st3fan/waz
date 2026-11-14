from datetime import date

from fastapi.testclient import TestClient

from waz.app import create_app
from waz.planner import PlanningError
from waz.storage import PlanStore


class FakePlanner:
    def __init__(self):
        self.calls = []

    def plan(self, days, existing):
        self.calls.append((days, existing.copy()))
        return {day: f"Dinner for {day.isoformat()}" for day in days}


def signed_in_client(path, planner, user="Ada"):
    client = TestClient(create_app(data_path=path, planner=planner))
    response = client.post("/login", data={"user": user})
    assert response.status_code == 200
    return client


def test_name_selection_sign_out_and_monday_navigation(tmp_path):
    client = TestClient(create_app(data_path=tmp_path / "plan.json", planner=FakePlanner()))
    assert client.get("/", follow_redirects=False).headers["location"] == "/login"
    assert client.post("/login", data={"user": "Mallory"}).status_code == 400
    client.post("/login", data={"user": "Ada"})
    response = client.get("/?week=2027-01-03")
    assert "Planning as <strong>Ada</strong>" in response.text
    assert 'datetime="2026-12-28"' in response.text
    assert 'datetime="2027-01-03"' in response.text
    assert response.text.count("Plan this day") == 7
    assert "/?week=2026-12-21" in response.text
    assert "/?week=2027-01-04" in response.text
    client.post("/logout")
    assert client.get("/", follow_redirects=False).headers["location"] == "/login"


def test_day_replan_week_fill_and_shared_persistence(tmp_path):
    path = tmp_path / "plan.json"
    planner = FakePlanner()
    client = signed_in_client(path, planner)
    week = "2026-12-28"
    monday = date(2026, 12, 28)

    client.post("/plan/day", data={"day": week, "week": week})
    PlanStore(path).replace_day(monday, "Family choice")
    response = client.post("/plan/week", data={"week": week})
    assert response.status_code == 200
    assert len(planner.calls[-1][0]) == 6
    assert PlanStore(path).read()[monday] == "Family choice"
    assert "Plan whole week" not in client.get(f"/?week={week}").text

    client.post("/plan/day", data={"day": week, "week": week})
    assert PlanStore(path).read()[monday] == "Dinner for 2026-12-28"
    client.post("/logout")
    client.post("/login", data={"user": "Bob"})
    assert "Planning as <strong>Bob</strong>" in client.get(f"/?week={week}").text
    assert "Dinner for 2026-12-28" in client.get(f"/?week={week}").text
    assert len(PlanStore(path).read()) == 7

    restarted = signed_in_client(path, FakePlanner(), user="Cat")
    assert "Dinner for 2026-12-28" in restarted.get(f"/?week={week}").text


def test_failed_planning_keeps_existing_dinner(tmp_path):
    class FailingPlanner:
        def plan(self, days, existing):
            raise PlanningError("Planner unavailable. Try again.")

    path = tmp_path / "plan.json"
    day = date(2026, 12, 28)
    PlanStore(path).replace_day(day, "Pasta")
    client = signed_in_client(path, FailingPlanner())
    response = client.post("/plan/day", data={"day": day.isoformat(), "week": day.isoformat()})
    assert response.status_code == 502
    assert "Planner unavailable. Try again." in response.text
    assert PlanStore(path).read()[day] == "Pasta"
