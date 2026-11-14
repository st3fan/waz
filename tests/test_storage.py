from datetime import date

from waz.storage import PlanStore, monday_of, week_days


def test_week_starts_monday_across_year_boundary():
    assert monday_of(date(2027, 1, 3)) == date(2026, 12, 28)
    assert week_days(date(2027, 1, 3)) == [
        date(2026, 12, 28), date(2026, 12, 29), date(2026, 12, 30),
        date(2026, 12, 31), date(2027, 1, 1), date(2027, 1, 2), date(2027, 1, 3),
    ]


def test_json_store_survives_reopening_and_preserves_existing_dinners(tmp_path):
    path = tmp_path / "data" / "plan.json"
    monday = date(2026, 12, 28)
    tuesday = date(2026, 12, 29)
    store = PlanStore(path)
    store.replace_day(monday, "Pasta")
    store.fill_missing({monday: "Tacos", tuesday: "Soup"})

    assert PlanStore(path).read() == {monday: "Pasta", tuesday: "Soup"}
    store.replace_day(monday, "Risotto")
    assert PlanStore(path).read()[monday] == "Risotto"
