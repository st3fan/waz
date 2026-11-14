"""Local web interface for a shared weekly dinner plan."""

from __future__ import annotations

from datetime import date, timedelta
import os
from pathlib import Path
import secrets
from typing import Protocol

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .planner import OpenAIPlanner, PlanningError
from .storage import PlanStore, monday_of, week_days


USERS = ("Ada", "Bob", "Cat")
ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = Jinja2Templates(directory=Path(__file__).parent / "templates")


class Planner(Protocol):
    def plan(self, days: list[date], existing: dict[date, str]) -> dict[date, str]: ...


def create_app(
    *, data_path: Path | None = None, history_path: Path | None = None, planner: Planner | None = None
) -> FastAPI:
    app = FastAPI(title="WAZ")
    app.add_middleware(
        SessionMiddleware,
        secret_key=os.getenv("WAZ_SESSION_SECRET") or secrets.token_urlsafe(32),
        same_site="lax",
    )
    app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
    store = PlanStore(data_path or ROOT / "data" / "plan.json")
    dinner_planner = planner or OpenAIPlanner(history_path or ROOT / "previous.txt")

    def current_user(request: Request) -> str | None:
        user = request.session.get("user")
        return user if user in USERS else None

    def calendar(request: Request, chosen: date, *, error: str | None = None, status_code: int = 200):
        monday = monday_of(chosen)
        plan = store.read()
        days = [{"date": day, "dinner": plan.get(day)} for day in week_days(monday)]
        return TEMPLATES.TemplateResponse(
            request=request,
            name="calendar.html",
            context={
                "user": current_user(request),
                "monday": monday,
                "sunday": monday + timedelta(days=6),
                "previous_week": monday - timedelta(days=7),
                "next_week": monday + timedelta(days=7),
                "days": days,
                "has_missing": any(item["dinner"] is None for item in days),
                "error": error,
            },
            status_code=status_code,
        )

    @app.get("/login", response_class=HTMLResponse)
    def login_page(request: Request):
        if current_user(request):
            return RedirectResponse("/", status_code=303)
        return TEMPLATES.TemplateResponse(request=request, name="login.html", context={"users": USERS})

    @app.post("/login")
    def login(request: Request, user: str = Form()):
        if user not in USERS:
            return TEMPLATES.TemplateResponse(
                request=request,
                name="login.html",
                context={"users": USERS, "error": "Choose Ada, Bob, or Cat."},
                status_code=400,
            )
        request.session["user"] = user
        return RedirectResponse("/", status_code=303)

    @app.post("/logout")
    def logout(request: Request):
        request.session.clear()
        return RedirectResponse("/login", status_code=303)

    @app.get("/", response_class=HTMLResponse)
    def show_week(request: Request, week: date | None = None):
        if not current_user(request):
            return RedirectResponse("/login", status_code=303)
        return calendar(request, week or date.today())

    @app.post("/plan/day", response_class=HTMLResponse)
    def plan_day(request: Request, day: date = Form(), week: date = Form()):
        if not current_user(request):
            return RedirectResponse("/login", status_code=303)
        if monday_of(day) != monday_of(week):
            raise HTTPException(status_code=400, detail="Day is outside the displayed week")
        try:
            dinners = dinner_planner.plan([day], store.read())
            store.replace_day(day, dinners[day])
        except PlanningError as exc:
            return calendar(request, week, error=str(exc), status_code=502)
        return RedirectResponse(f"/?week={monday_of(week).isoformat()}", status_code=303)

    @app.post("/plan/week", response_class=HTMLResponse)
    def plan_week(request: Request, week: date = Form()):
        if not current_user(request):
            return RedirectResponse("/login", status_code=303)
        existing = store.read()
        missing = [day for day in week_days(week) if day not in existing]
        if missing:
            try:
                dinners = dinner_planner.plan(missing, existing)
                store.fill_missing(dinners)
            except PlanningError as exc:
                return calendar(request, week, error=str(exc), status_code=502)
        return RedirectResponse(f"/?week={monday_of(week).isoformat()}", status_code=303)

    return app


app = create_app()
