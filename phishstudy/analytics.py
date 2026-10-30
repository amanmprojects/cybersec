"""Analytics: funnel metrics, department breakdowns, risk scoring and trends.

All numbers in the dashboard and the generated report come from these
functions, so the UI and the written report can never drift apart.
"""
from __future__ import annotations

import datetime as _dt
import html
import json
import re
import statistics
from collections import Counter
from typing import Iterable

from .db import connect

LIVE_STATUSES = ("Active", "Paused", "Completed")
DIFFICULTY_ORDER = {"Easy": 0, "Medium": 1, "Hard": 2}


def pct(part: float, whole: float, digits: int = 1) -> float:
    return round(100.0 * part / whole, digits) if whole else 0.0


def _rate(part: int, whole: int) -> float:
    return pct(part, whole)


def outcome_of(row) -> str:
    """Classify a target into the single outcome shown in the dashboard."""
    if row["submitted_at"]:
        return "submitted"
    if row["reported_at"]:
        return "reported"
    if row["clicked_at"]:
        return "clicked"
    if row["opened_at"]:
        return "opened"
    return "sent"


OUTCOME_LABELS = {
    "submitted": "Submitted credentials",
    "reported": "Reported to IT",
    "clicked": "Clicked, no submission",
    "opened": "Opened only",
    "sent": "No response",
}


def _summary(rows: Iterable) -> dict:
    rows = list(rows)
    n = len(rows)
    counts = {
        "sent": n,
        "opened": sum(1 for r in rows if r["opened_at"]),
        "clicked": sum(1 for r in rows if r["clicked_at"]),
        "submitted": sum(1 for r in rows if r["submitted_at"]),
        "reported": sum(1 for r in rows if r["reported_at"]),
    }
    counts.update(
        click_rate=_rate(counts["clicked"], n),
        submit_rate=_rate(counts["submitted"], n),
        report_rate=_rate(counts["reported"], n),
        open_rate=_rate(counts["opened"], n),
        # Exclusive final outcomes — each target contributes to exactly one bucket.
        outcomes=dict(Counter(outcome_of(r) for r in rows)),
        # Of the people who clicked, how many alerted IT instead of / after doing so.
        report_to_click=_rate(counts["reported"], counts["clicked"]) if counts["clicked"] else 0.0,
    )
    return counts


# ------------------------------------------------------------------- campaigns
def campaign_stats(conn, campaign_id: int) -> dict:
    rows = conn.execute("SELECT * FROM targets WHERE campaign_id=?", (campaign_id,)).fetchall()
    return _summary(rows)


def campaigns(conn, *, include_archived: bool = False) -> list:
    sql = """SELECT c.*, t.name AS template_name, t.difficulty, t.category,
                    (SELECT COUNT(*) FROM targets x WHERE x.campaign_id=c.id) AS targets
             FROM campaigns c JOIN templates t ON t.id=c.template_id"""
    if not include_archived:
        sql += " WHERE c.status <> 'Archived'"
    sql += " ORDER BY c.id DESC"
    out = []
    for row in conn.execute(sql).fetchall():
        d = dict(row)
        d.update(campaign_stats(conn, row["id"]))
        out.append(d)
    return out


def overview(conn) -> dict:
    """Aggregate metrics across every launched (non-draft) campaign."""
    rows = conn.execute(
        """SELECT tg.* FROM targets tg JOIN campaigns c ON c.id=tg.campaign_id
           WHERE c.status IN ('Active','Paused','Completed')"""
    ).fetchall()
    s = _summary(rows)
    s["campaigns"] = conn.execute(
        "SELECT COUNT(*) c FROM campaigns WHERE status IN ('Active','Paused','Completed')"
    ).fetchone()["c"]
    s["employees"] = conn.execute("SELECT COUNT(*) c FROM employees WHERE active=1").fetchone()["c"]
    s["training_completion"] = _rate(
        conn.execute("SELECT COUNT(DISTINCT employee_id) c FROM quiz_attempts").fetchone()["c"],
        s["employees"],
    )
    return s


# ------------------------------------------------------------------ departments
def department_stats(conn, campaign_id: int | None = None) -> list:
    where, params = "", []
    if campaign_id:
        where, params = " AND tg.campaign_id=?", [campaign_id]
    rows = conn.execute(
        f"""SELECT e.department, tg.* FROM targets tg
            JOIN employees e ON e.id=tg.employee_id
            JOIN campaigns c ON c.id=tg.campaign_id
            WHERE c.status IN ('Active','Paused','Completed'){where}""",
        params,
    ).fetchall()
    groups: dict[str, list] = {}
    for r in rows:
        groups.setdefault(r["department"], []).append(r)
    out = []
    for dept, items in groups.items():
        s = _summary(items)
        s["department"] = dept
        out.append(s)
    return sorted(out, key=lambda d: (-d["submit_rate"], -d["click_rate"], d["department"]))


# -------------------------------------------------------------------- templates
def difficulty_stats(conn, *, baseline_only: bool = False) -> list:
    extra = " AND c.phase='Baseline'" if baseline_only else ""
    rows = conn.execute(
        f"""SELECT t.difficulty, tg.* FROM targets tg
           JOIN campaigns c ON c.id=tg.campaign_id
           JOIN templates t ON t.id=c.template_id
           WHERE c.status IN ('Active','Paused','Completed'){extra}"""
    ).fetchall()
    groups: dict[str, list] = {}
    for r in rows:
        groups.setdefault(r["difficulty"], []).append(r)
    out = []
    for diff, items in groups.items():
        s = _summary(items)
        s["difficulty"] = diff
        out.append(s)
    return sorted(out, key=lambda d: DIFFICULTY_ORDER.get(d["difficulty"], 9))


def template_stats(conn) -> list:
    out = []
    for t in conn.execute("SELECT * FROM templates ORDER BY id").fetchall():
        rows = conn.execute(
            """SELECT tg.* FROM targets tg JOIN campaigns c ON c.id=tg.campaign_id
               WHERE c.template_id=? AND c.status IN ('Active','Paused','Completed')""",
            (t["id"],),
        ).fetchall()
        s = _summary(rows)
        s.update(id=t["id"], name=t["name"], difficulty=t["difficulty"],
                 category=t["category"], active=t["active"])
        out.append(s)
    return out


# ------------------------------------------------------------------ employees
def employee_rows(conn, campaign_id: int | None = None) -> list:
    where, params = "", []
    if campaign_id:
        where, params = " AND c.id=?", [campaign_id]
    rows = conn.execute(
        f"""SELECT e.id, e.name, e.email, e.department, e.designation, e.active,
                   tg.campaign_id, c.name AS campaign_name, c.status,
                   tg.token, tg.opened_at, tg.clicked_at, tg.submitted_at, tg.reported_at,
                   tg.sent_at
            FROM employees e
            LEFT JOIN targets tg ON tg.employee_id=e.id
            LEFT JOIN campaigns c ON c.id=tg.campaign_id AND c.status IN ('Active','Paused','Completed')
            WHERE 1=1{where}
            ORDER BY e.name""",
        params,
    ).fetchall()
    return [dict(r) for r in rows]


def employee_risk(conn) -> list:
    employees = conn.execute("SELECT * FROM employees WHERE active=1 ORDER BY name").fetchall()
    out = []
    for e in employees:
        rows = conn.execute(
            """SELECT tg.* FROM targets tg JOIN campaigns c ON c.id=tg.campaign_id
               WHERE tg.employee_id=? AND c.status IN ('Active','Paused','Completed')""",
            (e["id"],),
        ).fetchall()
        s = _summary(rows)
        quiz = conn.execute(
            "SELECT score,total FROM quiz_attempts WHERE employee_id=? ORDER BY taken_at DESC LIMIT 1",
            (e["id"],),
        ).fetchone()
        accuracy = (quiz["score"] / quiz["total"]) if quiz and quiz["total"] else None
        training_penalty = 15 * (1 - accuracy) if accuracy is not None else 10
        score = (0.60 * s["submit_rate"] + 0.25 * s["click_rate"]
                 + training_penalty - 0.10 * s["report_rate"])
        score = max(0, min(100, round(score, 1)))
        band = "Low" if score < 25 else "Moderate" if score < 50 else "High" if score < 75 else "Critical"
        out.append({
            **s, "id": e["id"], "name": e["name"], "email": e["email"],
            "department": e["department"], "designation": e["designation"],
            "risk": score, "band": band,
            "quiz_score": quiz["score"] if quiz else None,
            "quiz_total": quiz["total"] if quiz else None,
        })
    return sorted(out, key=lambda r: -r["risk"])


def repeat_clickers(conn, minimum: int = 2) -> list:
    rows = conn.execute(
        """SELECT e.name, e.email, e.department, COUNT(*) AS campaigns,
                  SUM(CASE WHEN tg.submitted_at IS NOT NULL THEN 1 ELSE 0 END) AS submissions,
                  SUM(CASE WHEN tg.reported_at IS NOT NULL THEN 1 ELSE 0 END) AS reports
           FROM targets tg JOIN employees e ON e.id=tg.employee_id
           JOIN campaigns c ON c.id=tg.campaign_id
           WHERE c.status IN ('Active','Paused','Completed') AND tg.clicked_at IS NOT NULL
           GROUP BY e.id HAVING campaigns >= ? ORDER BY submissions DESC, campaigns DESC""",
        (minimum,),
    ).fetchall()
    return [dict(r) for r in rows]


# ----------------------------------------------------------------------- trends
def campaign_trend(conn) -> list:
    out = []
    for c in conn.execute(
        """SELECT c.id,c.name,c.phase,c.launched_at,t.difficulty FROM campaigns c
           JOIN templates t ON t.id=c.template_id
           WHERE c.status IN ('Active','Paused','Completed') ORDER BY c.id"""
    ).fetchall():
        s = campaign_stats(conn, c["id"])
        out.append({**dict(c), **s})
    return out


def median_time_to_click_hours(conn, campaign_id: int | None = None) -> float | None:
    where, params = "", []
    if campaign_id:
        where, params = " AND campaign_id=?", [campaign_id]
    rows = conn.execute(
        f"SELECT sent_at, clicked_at FROM targets WHERE clicked_at IS NOT NULL{where}", params
    ).fetchall()
    deltas = []
    for r in rows:
        try:
            a = _dt.datetime.strptime(r["sent_at"], "%Y-%m-%d %H:%M")
            b = _dt.datetime.strptime(r["clicked_at"], "%Y-%m-%d %H:%M")
            deltas.append((b - a).total_seconds() / 3600)
        except (TypeError, ValueError):
            continue
    return round(statistics.median(deltas), 1) if deltas else None


# --------------------------------------------------------------------- training
def quiz_stats(conn) -> dict:
    attempts = conn.execute(
        """SELECT q.*, e.name, e.department FROM quiz_attempts q
           LEFT JOIN employees e ON e.id=q.employee_id ORDER BY q.taken_at DESC"""
    ).fetchall()
    n = len(attempts)
    if not n:
        return {"attempts": 0, "average": 0.0, "pass_rate": 0.0, "per_question": [], "rows": []}
    total_marks = sum(a["total"] for a in attempts)
    average = round(sum(a["score"] for a in attempts) / n, 2)
    pass_rate = _rate(sum(1 for a in attempts if a["score"] >= max(1, round(a["total"] * 0.75))), n)

    # Per-question accuracy is only available for attempts that stored answers.
    from .seed import QUIZ

    def _items(rows: list) -> list:
        counts = [{"correct": 0, "answered": 0} for _ in QUIZ]
        for a in rows:
            try:
                answers = json.loads(a["answers"] or "[]")
            except (TypeError, ValueError):
                continue
            if not isinstance(answers, list) or len(answers) != len(QUIZ):
                continue
            for i, given in enumerate(answers):
                counts[i]["answered"] += 1
                if str(given) == str(QUIZ[i][2]):
                    counts[i]["correct"] += 1
        return [
            {"question": html.unescape(re.sub(r"<[^>]+>", "", QUIZ[i][0])),
             "accuracy": _rate(c["correct"], c["answered"]),
             "answered": c["answered"]}
            for i, c in enumerate(counts)
        ]

    per_question = _items(attempts)

    def _round(round_campaign: int) -> dict:
        rows = [a for a in attempts if a["campaign_id"] == round_campaign]
        if not rows:
            return {"attempts": 0, "average": 0.0, "average_pct": 0.0, "pass_rate": 0.0}
        marks = sum(a["total"] for a in rows)
        return {
            "attempts": len(rows),
            "average": round(sum(a["score"] for a in rows) / len(rows), 2),
            "average_pct": pct(sum(a["score"] for a in rows), marks) if marks else 0,
            "pass_rate": _rate(
                sum(1 for a in rows if a["score"] >= max(1, round(a["total"] * 0.75))), len(rows)
            ),
        }

    return {
        "attempts": n,
        "average": average,
        "average_pct": pct(sum(a["score"] for a in attempts), total_marks) if total_marks else 0,
        "pass_rate": pass_rate,
        # The seeded programme attaches the pre-training round to campaign 3
        # and the post-training round to campaign 4.
        "pre": _round(3),
        "post": _round(4),
        "per_question": per_question,
        "per_question_pre": _items([a for a in attempts if a["campaign_id"] == 3]),
        "per_question_post": _items([a for a in attempts if a["campaign_id"] == 4]),
        "rows": [dict(a) for a in attempts],
    }


# ------------------------------------------------------------------ full report
def results_snapshot(conn) -> dict:
    """Everything the generated report needs, in one JSON-serialisable dict."""
    from .seed import QUIZ

    ov = overview(conn)
    camps = campaign_trend(conn)
    return {
        "generated_at": _dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "overview": {k: v for k, v in ov.items() if not callable(v)},
        "campaigns": camps,
        "departments": department_stats(conn),
        "difficulties": difficulty_stats(conn),
        "difficulties_baseline": difficulty_stats(conn, baseline_only=True),
        "templates": template_stats(conn),
        "employees": employee_risk(conn),
        "repeat_clickers": repeat_clickers(conn),
        "median_time_to_click_hours": median_time_to_click_hours(conn),
        "quiz": {k: v for k, v in quiz_stats(conn).items() if k != "rows"},
        "quiz_question_count": len(QUIZ),
    }


def load_connection(path: str | None = None):
    return connect(path)
