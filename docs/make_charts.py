#!/usr/bin/env python3
"""Generate the result charts used in the report (matplotlib)."""
from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "figures")
RES = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))

INK = "#1e293b"
MUTED = "#64748b"
GRID = "#e2e8f0"
INDIGO = "#4f46e5"
GREEN = "#059669"
AMBER = "#d97706"
RED = "#dc2626"
SLATE = "#94a3b8"

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK,
    "axes.titlecolor": INK,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})


def style(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), dpi=200)
    plt.close(fig)
    print("wrote", name)


def funnel():
    ov = RES["overview"]
    stages = [
        ("Delivered", ov["sent"], 100.0),
        ("Opened", ov["opened"], ov["open_rate"]),
        ("Clicked link", ov["clicked"], ov["click_rate"]),
        ("Submitted data", ov["submitted"], ov["submit_rate"]),
    ]
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    labels = [s[0] for s in stages][::-1]
    values = [s[1] for s in stages][::-1]
    rates = [s[2] for s in stages][::-1]
    colors = ["#cbd5e1", "#818cf8", "#f59e0b", RED][::-1]
    bars = ax.barh(labels, values, color=colors, height=0.58)
    for bar, v, p in zip(bars, values, rates):
        ax.text(v + 1.5, bar.get_y() + bar.get_height() / 2,
                f"{v}  ({p:.1f}% of delivered)", va="center", color=INK, fontsize=10, fontweight="bold")
    ax.set_xlim(0, max(values) * 1.32)
    ax.set_xlabel("Simulated recipients")
    ax.set_title("Delivery funnel across five launched campaigns", loc="left", fontsize=12, fontweight="bold")
    style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    save(fig, "funnel.png")


def campaigns():
    rows = RES["campaigns"]
    names = ["Password\nexpiry", "Festival\nbonus", "M365\nbaseline", "M365\npost-training", "Courier\n(live)"]
    click = [r["click_rate"] for r in rows]
    submit = [r["submit_rate"] for r in rows]
    report = [r["report_rate"] for r in rows]
    x = range(len(rows))
    w = 0.26
    fig, ax = plt.subplots(figsize=(10, 4.4))
    b1 = ax.bar([i - w for i in x], click, w, label="Clicked", color=SLATE)
    b2 = ax.bar(list(x), submit, w, label="Submitted data", color=RED)
    b3 = ax.bar([i + w for i in x], report, w, label="Reported", color=GREEN)
    for bars in (b1, b2, b3):
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.2,
                    f"{bar.get_height():.0f}", ha="center", fontsize=8, color=MUTED)
    ax.set_xticks(list(x))
    ax.set_xticklabels(names)
    ax.set_ylim(0, 62)
    ax.set_ylabel("Rate (%)")
    ax.set_title("Campaign-level outcomes", loc="left", fontsize=12, fontweight="bold")
    ax.legend(frameon=False, ncol=3, loc="upper right")
    style(ax)
    save(fig, "campaigns.png")


def departments():
    rows = sorted(RES["departments"], key=lambda r: -r["submit_rate"])
    names = [r["department"] for r in rows]
    click = [r["click_rate"] for r in rows]
    submit = [r["submit_rate"] for r in rows]
    report = [r["report_rate"] for r in rows]
    x = range(len(rows))
    w = 0.26
    fig, ax = plt.subplots(figsize=(10, 4.4))
    ax.bar([i - w for i in x], click, w, label="Clicked", color=SLATE)
    ax.bar(list(x), submit, w, label="Submitted data", color=RED)
    ax.bar([i + w for i in x], report, w, label="Reported", color=GREEN)
    ax.set_xticks(list(x))
    ax.set_xticklabels(names)
    ax.set_ylim(0, 95)
    ax.set_ylabel("Rate (%)")
    ax.set_title("Outcomes by department (all launched campaigns)", loc="left", fontsize=12, fontweight="bold")
    ax.legend(frameon=False, ncol=3, loc="upper right")
    style(ax)
    save(fig, "departments.png")


def difficulty():
    rows = RES["difficulties_baseline"]
    names = [r["difficulty"] for r in rows]
    submit = [r["submit_rate"] for r in rows]
    click = [r["click_rate"] for r in rows]
    report = [r["report_rate"] for r in rows]
    x = range(len(rows))
    w = 0.26
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    ax.bar([i - w for i in x], click, w, label="Clicked", color=SLATE)
    ax.bar(list(x), submit, w, label="Submitted data", color=RED)
    ax.bar([i + w for i in x], report, w, label="Reported", color=GREEN)
    ax.set_xticks(list(x))
    ax.set_xticklabels(names)
    ax.set_ylim(0, 70)
    ax.set_ylabel("Rate (%)")
    ax.set_title("Baseline outcomes by lure difficulty", loc="left", fontsize=12, fontweight="bold")
    ax.legend(frameon=False, ncol=3)
    style(ax)
    save(fig, "difficulty.png")


def quiz():
    pre, post = RES["quiz"]["pre"], RES["quiz"]["post"]
    items = RES["quiz"]["per_question_pre"]
    posts = RES["quiz"]["per_question_post"]
    labels = [f"Q{i+1}" for i in range(len(items))]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.0), gridspec_kw={"width_ratios": [1, 2.4]})
    bars = ax1.bar(["Pre-training", "Post-training"], [pre["average"], post["average"]],
                   color=[AMBER, GREEN], width=0.55)
    for bar, r in zip(bars, (pre, post)):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15,
                 f"{bar.get_height():.2f}/8\n({r['pass_rate']:.0f}% pass)", ha="center",
                 fontsize=9, color=INK, fontweight="bold")
    ax1.set_ylim(0, 8.8)
    ax1.set_ylabel("Mean score")
    ax1.set_title("Mean score", loc="left", fontsize=11, fontweight="bold")
    style(ax1)

    xs = range(len(items))
    for i, (a, b) in enumerate(zip(items, posts)):
        ax2.plot([i, i], [a["accuracy"], b["accuracy"]], color=GRID, linewidth=3, zorder=1)
    ax2.scatter(list(xs), [q["accuracy"] for q in items], color=AMBER, s=46, label="Pre-training", zorder=3)
    ax2.scatter(list(xs), [q["accuracy"] for q in posts], color=GREEN, s=46, label="Post-training", zorder=3)
    ax2.set_xticks(list(xs))
    ax2.set_xticklabels(labels)
    ax2.set_ylim(0, 105)
    ax2.set_ylabel("Accuracy (%)")
    ax2.set_title("Item-level accuracy before and after coaching", loc="left", fontsize=11, fontweight="bold")
    ax2.legend(frameon=False, ncol=2, loc="lower right")
    style(ax2)
    save(fig, "quiz.png")


def risk():
    bands = {"Low": 0, "Moderate": 0, "High": 0, "Critical": 0}
    for e in RES["employees"]:
        bands[e["band"]] += 1
    colors = [GREEN, AMBER, "#ea580c", RED]
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    bars = ax.bar(list(bands), list(bands.values()), color=colors, width=0.58)
    for bar, v in zip(bars, bands.values()):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.15, str(v),
                ha="center", fontsize=11, fontweight="bold", color=INK)
    ax.set_ylim(0, max(bands.values()) + 3)
    ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax.set_ylabel("Employees")
    ax.set_title("Distribution of composite risk bands (n = 24)", loc="left", fontsize=12, fontweight="bold")
    style(ax)
    save(fig, "risk.png")


def gantt():
    tasks = [
        ("Literature review and requirements", 0.0, 2.0, GREEN),
        ("System and security design", 0.6, 1.5, GREEN),
        ("Prototype implementation", 1.6, 2.0, GREEN),
        ("Testing and hardening", 2.4, 1.8, GREEN),
        ("Synthetic pilot and analysis", 3.2, 1.4, GREEN),
        ("Report and paper drafting", 2.0, 3.0, AMBER),
        ("Field pilot (Semester VIII)", 5.0, 3.0, SLATE),
        ("Longitudinal evaluation", 7.0, 3.0, SLATE),
        ("Final dissertation and defence", 8.0, 2.0, SLATE),
    ]
    months = ["Aug\n2026", "Sep", "Oct", "Nov", "Dec", "Jan\n2027", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    for i, (name, start, dur, color) in enumerate(tasks):
        ax.barh(i, dur, left=start, color=color, height=0.55)
        ax.text(start + dur + 0.12, i, f"{round(dur)} mo", va="center", fontsize=8, color=MUTED)
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels([t[0] for t in tasks], fontsize=9)
    ax.invert_yaxis()
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, fontsize=8)
    ax.set_xlim(0, 12)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.axvline(5.0, color=RED, linestyle="--", linewidth=1.0)
    ax.legend(handles=[Patch(color=GREEN, label="Completed"), Patch(color=AMBER, label="Ongoing"),
                       Patch(color=SLATE, label="Planned")],
              frameon=False, ncol=3, loc="lower right", bbox_to_anchor=(1.0, -0.30))
    ax.set_title("Work completed and planned, August 2026 – July 2027", loc="left", fontsize=12, fontweight="bold")
    save(fig, "gantt.png")


def workflow_bars():
    """Small chart for the testing chapter: requirement coverage."""
    labels = ["Unit", "Route", "Mutation", "Security", "Data"]
    values = [8, 24, 5, 6, 4]
    fig, ax = plt.subplots(figsize=(7.4, 3.4))
    bars = ax.bar(labels, values, color=[INDIGO, INDIGO, GREEN, RED, AMBER], width=0.55)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2, str(v),
                ha="center", fontsize=10, fontweight="bold", color=INK)
    ax.set_ylim(0, 30)
    ax.set_ylabel("Executed checks")
    ax.set_title("Automated checks executed in the final test run", loc="left", fontsize=12, fontweight="bold")
    style(ax)
    save(fig, "tests.png")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    funnel()
    campaigns()
    departments()
    difficulty()
    quiz()
    risk()
    gantt()
