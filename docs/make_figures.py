#!/usr/bin/env python3
"""Generate the report diagrams as PNG files (Pillow only).

Run:  python3 docs/make_figures.py
Output: docs/figures/*.png
"""
from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
INK = "#111827"
MUTED = "#4b5563"
LINE = "#cbd5e1"
INDIGO = "#4338ca"
INDIGO_SOFT = "#eef2ff"
BLUE = "#1d4ed8"
BLUE_SOFT = "#e8f0fe"
GREEN = "#047857"
GREEN_SOFT = "#e7f7f1"
AMBER = "#b45309"
AMBER_SOFT = "#fdf3e4"
RED = "#b91c1c"
RED_SOFT = "#fdecec"
SLATE = "#0f172a"
SLATE_SOFT = "#f1f5f9"
WHITE = "#ffffff"

SCALE = 2


def font(size: int, bold: bool = False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size * SCALE)


def canvas(w: int, h: int):
    img = Image.new("RGB", (w * SCALE, h * SCALE), WHITE)
    return img, ImageDraw.Draw(img)


def rbox(d, xy, fill=WHITE, outline=LINE, radius=14, width=3):
    d.rounded_rectangle([v * SCALE for v in xy], radius=radius * SCALE,
                        fill=fill, outline=outline, width=width * SCALE)


def label(d, xy, text, f, fill=INK, anchor="mm"):
    d.text([v * SCALE for v in xy], text, font=f, fill=fill, anchor=anchor)


def wrapped(d, xy, text, f, fill=INK, max_width=300, line_gap=8, anchor="mm"):
    words, lines, current = text.split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if d.textlength(candidate, font=f) <= max_width * SCALE:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    heights = [d.textbbox((0, 0), line, font=f)[3] for line in lines]
    total = sum(heights) + line_gap * SCALE * (len(lines) - 1)
    x, y = xy[0] * SCALE, xy[1] * SCALE - total / 2
    for line, height in zip(lines, heights):
        d.text((x, y), line, font=f, fill=fill, anchor="ma")
        y += height + line_gap * SCALE


def arrow(d, p1, p2, color=MUTED, width=3, head=12):
    x1, y1 = [v * SCALE for v in p1]
    x2, y2 = [v * SCALE for v in p2]
    d.line([(x1, y1), (x2, y2)], fill=color, width=width * SCALE)
    angle = math.atan2(y2 - y1, x2 - x1)
    size = head * SCALE
    pts = [(x2, y2),
           (x2 - size * math.cos(angle - 0.4), y2 - size * math.sin(angle - 0.4)),
           (x2 - size * math.cos(angle + 0.4), y2 - size * math.sin(angle + 0.4))]
    d.polygon(pts, fill=color)


def poly_arrow(d, points, color=MUTED, width=3, head=12):
    for a, b in zip(points[:-2], points[1:-1]):
        d.line([(a[0] * SCALE, a[1] * SCALE), (b[0] * SCALE, b[1] * SCALE)],
               fill=color, width=width * SCALE)
    arrow(d, points[-2], points[-1], color, width, head)


def title(d, text, sub=""):
    label(d, (900, 44), text, font(30, True), INK)
    if sub:
        label(d, (900, 82), sub, font(15), MUTED)


# ------------------------------------------------------------------ architecture
def architecture():
    W, H = 1800, 1080
    img, d = canvas(W, H)
    title(d, "System architecture", "Three-tier, offline-first design — Python standard library and SQLite only")

    # clients
    rbox(d, (150, 140, 700, 250), SLATE_SOFT, SLATE)
    label(d, (425, 175), "Participant browser", font(19, True))
    label(d, (425, 213), "tokenised link  ·  inbox  ·  quiz", font(14), MUTED)
    rbox(d, (1100, 140, 1650, 250), SLATE_SOFT, SLATE)
    label(d, (1375, 175), "Administrator browser", font(19, True))
    label(d, (1375, 213), "login  ·  campaigns  ·  analytics", font(14), MUTED)

    # server
    rbox(d, (150, 330, 1650, 470), INDIGO_SOFT, INDIGO, radius=18)
    label(d, (900, 365), "HTTP layer  ·  phishstudy.server", font(20, True), INDIGO)
    label(d, (900, 405), "explicit routing  ·  session cookie  ·  CSRF verification  ·  login throttle  ·  security headers",
          font(14), MUTED)
    label(d, (900, 439), "server-rendered HTML — no JavaScript framework, no build step", font(14), MUTED)

    modules = [
        ("Campaigns", "lifecycle, audience,\ntracking tokens"),
        ("Lures", "templates, preview,\nred-flag library"),
        ("People", "directory, consent,\nbulk import"),
        ("Tracking", "open / click / submit /\nreport events"),
        ("Analytics", "funnel, departments,\nrisk scoring"),
        ("Training", "quiz bank, scoring,\npre/post comparison"),
        ("Audit", "append-only action\nlog"),
    ]
    x = 150
    width = (1500 - 6 * 18) / 7
    for name, sub in modules:
        rbox(d, (x, 540, x + width, 690), WHITE, LINE, radius=12)
        label(d, (x + width / 2, 575), name, font(15, True))
        wrapped(d, (x + width / 2, 638), sub, font(11), MUTED, max_width=width - 24, line_gap=4)
        x += width + 18

    # database
    rbox(d, (450, 780, 1350, 930), GREEN_SOFT, GREEN, radius=18)
    label(d, (900, 818), "SQLite database  ·  phishing.db  (WAL mode)", font(20, True), GREEN)
    label(d, (900, 858), "employees · templates · campaigns · targets · quiz_attempts · audit · sessions · settings",
          font(13), MUTED)
    label(d, (900, 890), "parameterised SQL everywhere  ·  foreign keys enforced  ·  cascade on delete", font(13), MUTED)

    # arrows: clients into the server
    arrow(d, (425, 250), (425, 328), SLATE)
    arrow(d, (1375, 250), (1375, 328), SLATE)

    # server distributes to every module through a bus
    d.line([(220 * SCALE, 510 * SCALE), (1580 * SCALE, 510 * SCALE)], fill=INDIGO, width=2 * SCALE)
    arrow(d, (900, 470), (900, 510), INDIGO, 2, 10)
    for mx in [int(150 + width / 2 + i * (width + 18)) for i in range(7)]:
        arrow(d, (mx, 510), (mx, 538), INDIGO, 2, 8)

    # every module reads and writes the database through a second bus
    d.line([(220 * SCALE, 726 * SCALE), (1580 * SCALE, 726 * SCALE)], fill=GREEN, width=2 * SCALE)
    for mx in [int(150 + width / 2 + i * (width + 18)) for i in range(7)]:
        arrow(d, (mx, 690), (mx, 726), GREEN, 2, 8)
    arrow(d, (900, 726), (900, 778), GREEN)

    # side notes
    rbox(d, (150, 970, 860, 1040), SLATE_SOFT, LINE, radius=10)
    label(d, (505, 1005), "No third-party packages · runs offline on any laptop", font(13), MUTED)
    rbox(d, (940, 970, 1650, 1040), AMBER_SOFT, "#f6dfb8", radius=10)
    label(d, (1295, 1005), "Simulation only — no SMTP, no real credentials", font(13), AMBER)

    img.save(os.path.join(OUT, "architecture.png"))


# -------------------------------------------------------------------------- dfd
def dfd():
    W, H = 1800, 1000
    img, d = canvas(W, H)
    title(d, "Data-flow diagram (Level 0)", "External entities, processes and data stores of the simulation")

    def entity(xy, text):
        rbox(d, xy, SLATE_SOFT, SLATE, radius=6)
        wrapped(d, ((xy[0] + xy[2]) / 2, (xy[1] + xy[3]) / 2), text, font(15, True), max_width=180)

    def process(cx, cy, text):
        r = 92
        d.ellipse([(cx - r) * SCALE, (cy - r) * SCALE, (cx + r) * SCALE, (cy + r) * SCALE],
                  fill=INDIGO_SOFT, outline=INDIGO, width=3 * SCALE)
        wrapped(d, (cx, cy), text, font(13, True), max_width=150, line_gap=3)

    def store(xy, text):
        x1, y1, x2, y2 = xy
        d.rectangle([x1 * SCALE, y1 * SCALE, x2 * SCALE, y2 * SCALE], fill=GREEN_SOFT,
                    outline=GREEN, width=3 * SCALE)
        d.line([(x1 + 18) * SCALE, y1 * SCALE, (x1 + 18) * SCALE, y2 * SCALE], fill=GREEN, width=2 * SCALE)
        wrapped(d, ((x1 + x2) / 2 + 9, (y1 + y2) / 2), text, font(13, True), max_width=x2 - x1 - 44)

    def flow_label(xy, text):
        f = font(11)
        w = d.textlength(text, font=f) / SCALE + 14
        rbox(d, (xy[0] - w / 2, xy[1] - 12, xy[0] + w / 2, xy[1] + 12), WHITE, WHITE, radius=5, width=1)
        label(d, xy, text, f, MUTED)

    entity((140, 300, 360, 410), "Participant")
    entity((140, 590, 360, 700), "Administrator")
    process(640, 360, "Simulated\ncampaign engine")
    process(1020, 360, "Tracking &\nanalytics")
    process(1400, 360, "Training &\ncoaching")
    store((480, 760, 800, 860), "D2  campaigns,\nlures, people")
    store((840, 760, 1160, 860), "D1  targets")
    store((1200, 760, 1560, 860), "D3  quiz_attempts")

    # participant <-> campaign engine (two parallel flows)
    arrow(d, (360, 330), (548, 330), SLATE)
    flow_label((455, 306), "open / click / submit")
    arrow(d, (548, 392), (360, 392), SLATE)
    flow_label((455, 416), "simulated mail")

    # administrator -> campaign engine, orthogonal
    poly_arrow(d, [(360, 615), (450, 615), (450, 430), (548, 430)], SLATE)
    flow_label((455, 540), "manage campaigns")

    # campaign engine -> stores and analytics
    arrow(d, (600, 452), (580, 758), GREEN)
    flow_label((560, 620), "store definitions")
    arrow(d, (680, 452), (980, 758), GREEN)
    flow_label((878, 620), "write events")
    arrow(d, (732, 360), (928, 360), INDIGO)
    flow_label((830, 336), "raw events")

    # analytics reads targets, passes risk scores to training
    arrow(d, (1020, 452), (1020, 758), GREEN)
    flow_label((1062, 620), "read / aggregate")
    arrow(d, (1112, 360), (1308, 360), INDIGO)
    flow_label((1210, 336), "risk scores")

    # training stores the quiz and returns coaching to the participant
    arrow(d, (1400, 452), (1400, 758), GREEN)
    flow_label((1444, 620), "store score")
    poly_arrow(d, [(1400, 268), (1400, 180), (250, 180), (250, 298)], INDIGO, 2, 10)
    flow_label((860, 158), "coaching page and awareness quiz")

    img.save(os.path.join(OUT, "dfd.png"))


# ---------------------------------------------------------------------- use case
def usecase():
    W, H = 1800, 1080
    img, d = canvas(W, H)
    title(d, "Use-case diagram", "Two actors: the administrator and the participant")

    def actor(cx, cy, name):
        d.ellipse([(cx - 16) * SCALE, (cy - 70) * SCALE, (cx + 16) * SCALE, (cy - 38) * SCALE],
                  outline=SLATE, width=3 * SCALE)
        d.line([(cx * SCALE, (cy - 38) * SCALE), (cx * SCALE, (cy + 20) * SCALE)], fill=SLATE, width=3 * SCALE)
        d.line([(cx * SCALE, (cy - 20) * SCALE), ((cx - 34) * SCALE, (cy + 2) * SCALE)], fill=SLATE, width=3 * SCALE)
        d.line([(cx * SCALE, (cy - 20) * SCALE), ((cx + 34) * SCALE, (cy + 2) * SCALE)], fill=SLATE, width=3 * SCALE)
        d.line([(cx * SCALE, (cy + 20) * SCALE), ((cx - 28) * SCALE, (cy + 62) * SCALE)], fill=SLATE, width=3 * SCALE)
        d.line([(cx * SCALE, (cy + 20) * SCALE), ((cx + 28) * SCALE, (cy + 62) * SCALE)], fill=SLATE, width=3 * SCALE)
        label(d, (cx, cy + 96), name, font(15, True))

    actor(140, 540, "Administrator")
    actor(1660, 540, "Participant")

    cases = [
        ("Sign in securely", 540, 140),
        ("Manage people & consent", 540, 300),
        ("Create and launch campaign", 540, 460),
        ("Manage lure templates", 540, 620),
        ("Review analytics & risk", 540, 780),
        ("Open simulated inbox", 1240, 180),
        ("Report a phishing mail", 1240, 340),
        ("Submit (fake) credentials", 1240, 500),
        ("Read coaching page", 1240, 660),
        ("Take awareness quiz", 1240, 820),
    ]
    for text, x, y in cases:
        r = 116
        d.ellipse([(x - r) * SCALE, (y - 48) * SCALE, (x + r) * SCALE, (y + 48) * SCALE],
                  fill=INDIGO_SOFT, outline=INDIGO, width=2 * SCALE)
        wrapped(d, (x, y), text, font(12, True), max_width=190, line_gap=2)

    for _, _, y in cases[:5]:
        arrow(d, (215, 540), (420, y), LINE, 2, 10)
    for _, _, y in cases[5:]:
        arrow(d, (1585, 540), (1360, y), LINE, 2, 10)

    img.save(os.path.join(OUT, "usecase.png"))


# --------------------------------------------------------------------------- er
def er():
    W, H = 1800, 1000
    img, d = canvas(W, H)
    title(d, "Entity–relationship diagram", "Nine tables; foreign keys enforce referential integrity")

    def entity(xy, name, attrs):
        x1, y1, x2, y2 = xy
        rbox(d, xy, WHITE, INDIGO, radius=8)
        d.rectangle([x1 * SCALE, y1 * SCALE, x2 * SCALE, (y1 + 36) * SCALE], fill=INDIGO)
        label(d, ((x1 + x2) / 2, y1 + 18), name, font(14, True), WHITE)
        for i, a in enumerate(attrs):
            label(d, (x1 + 12, y1 + 58 + i * 24), a, font(11), MUTED, anchor="lm")

    entity((80, 140, 400, 330), "employees",
           ["id  PK", "name, email  UNIQUE", "department, designation", "active, consent"])
    entity((550, 140, 900, 360), "targets",
           ["id  PK", "campaign_id  FK", "employee_id  FK", "token  UNIQUE", "opened / clicked / submitted /", "reported timestamps"])
    entity((1050, 140, 1400, 360), "campaigns",
           ["id  PK", "template_id  FK", "status, phase, audience", "scheduled_for, launched_at"])
    entity((1450, 140, 1740, 320), "templates",
           ["id  PK", "name, category, difficulty", "subject, sender_email", "body, landing, flags"])
    entity((80, 470, 400, 690), "quiz_attempts",
           ["id  PK", "employee_id  FK", "campaign_id  FK", "score, total, answers", "taken_at"])
    entity((550, 470, 900, 650), "admins",
           ["id  PK", "username  UNIQUE", "password_hash (PBKDF2)", "created_at, last_login"])
    entity((1050, 470, 1400, 650), "sessions",
           ["token_hash  PK", "admin_id  FK", "csrf, flash", "expires_at"])
    entity((1050, 760, 1400, 920), "audit",
           ["id  PK", "actor, action", "detail, at"])
    entity((550, 760, 900, 900), "settings",
           ["key  PK", "value"])

    def rel(points, text, at):
        poly_arrow(d, points, MUTED, 2, 10)
        f = font(11)
        w = d.textlength(text, font=f) / SCALE + 12
        rbox(d, (at[0] - w / 2, at[1] - 12, at[0] + w / 2, at[1] + 12), WHITE, WHITE, radius=4, width=1)
        label(d, at, text, f, MUTED)

    # employees 1:N targets
    rel([(400, 220), (548, 220)], "1 : N", (475, 196))
    # campaigns 1:N targets
    rel([(1050, 300), (902, 300)], "1 : N", (975, 276))
    # templates 1:N campaigns
    rel([(1450, 220), (1402, 220)], "1 : N", (1426, 196))
    # employees 1:N quiz_attempts
    rel([(240, 330), (240, 468)], "1 : N", (300, 400))
    # campaigns 1:N quiz_attempts (route below the targets row)
    rel([(1150, 360), (1150, 415), (400, 415), (400, 468)], "1 : N", (760, 392))
    # admins 1:N sessions
    rel([(900, 560), (1048, 560)], "1 : N", (975, 536))

    rbox(d, (550, 930, 1400, 975), SLATE_SOFT, LINE, radius=8)
    label(d, (975, 952), "Deleting an employee cascades to targets and nulls quiz references.", font(11), MUTED)

    img.save(os.path.join(OUT, "er.png"))


# ---------------------------------------------------------------------- workflow
def workflow():
    W, H = 1800, 760
    img, d = canvas(W, H)
    title(d, "Campaign lifecycle", "State transitions recorded in the audit log")

    states = [("Draft", "created, audience fixed"), ("Scheduled", "targets generated, waiting"),
              ("Active", "collecting events"), ("Completed", "closed, included in analytics")]
    x = 100
    w = 360
    for i, (name, sub) in enumerate(states):
        fill = {"Draft": SLATE_SOFT, "Scheduled": BLUE_SOFT, "Active": GREEN_SOFT, "Completed": INDIGO_SOFT}[name]
        color = {"Draft": SLATE, "Scheduled": BLUE, "Active": GREEN, "Completed": INDIGO}[name]
        rbox(d, (x, 260, x + w, 400), fill, color, radius=16)
        label(d, (x + w / 2, 315), name, font(22, True), color)
        label(d, (x + w / 2, 355), sub, font(12), MUTED)
        if i < len(states) - 1:
            arrow(d, (x + w, 330), (x + w + 80, 330), color)
        x += w + 80

    rbox(d, (940, 500, 1260, 610), AMBER_SOFT, AMBER, radius=14)
    label(d, (1100, 540), "Paused", font(18, True), AMBER)
    label(d, (1100, 575), "links valid, no new sends", font(11), MUTED)
    arrow(d, (1160, 400), (1160, 498), AMBER, 2, 10)
    arrow(d, (1040, 498), (1040, 402), AMBER, 2, 10)
    label(d, (1012, 456), "resume", font(11), AMBER, anchor="rm")

    rbox(d, (1280, 500, 1560, 610), SLATE_SOFT, SLATE, radius=14)
    label(d, (1420, 540), "Archived", font(18, True), SLATE)
    label(d, (1420, 575), "hidden, retained for audit", font(11), MUTED)
    poly_arrow(d, [(1500, 400), (1500, 500)], SLATE, 2, 10)

    rbox(d, (100, 660, 1700, 720), SLATE_SOFT, LINE, radius=10)
    label(d, (900, 690), "Launch requires recorded consent for every recipient  ·  "
                         "every transition is written to the audit log", font(13), MUTED)

    img.save(os.path.join(OUT, "workflow.png"))


# ----------------------------------------------------------------- attack chain
def attack_chain():
    W, H = 1800, 560
    img, d = canvas(W, H)
    title(d, "Anatomy of a phishing attack", "Why a single click matters")

    steps = [
        ("Reconnaissance", "employee names, roles\nand public email addresses"),
        ("Lure delivery", "spoofed sender, urgency,\nbrand impersonation"),
        ("Interaction", "link click or\nmalicious attachment"),
        ("Credential capture", "fake sign-in page\ncollects the password"),
        ("Account takeover", "credential replay,\nMFA fatigue, mailbox rules"),
        ("Lateral movement", "internal phishing,\ninvoice fraud, data theft"),
    ]
    x, w, gap = 80, 250, 32
    for i, (name, sub) in enumerate(steps):
        fill = [RED_SOFT, AMBER_SOFT, AMBER_SOFT, RED_SOFT, RED_SOFT, RED_SOFT][i]
        color = [RED, AMBER, AMBER, RED, RED, RED][i]
        rbox(d, (x, 200, x + w, 360), fill, color, radius=14)
        label(d, (x + w / 2, 240), f"{i + 1}", font(22, True), color)
        label(d, (x + w / 2, 285), name, font(14, True), color)
        wrapped(d, (x + w / 2, 330), sub, font(10.5), MUTED, max_width=w - 30, line_gap=3)
        if i < len(steps) - 1:
            arrow(d, (x + w, 280), (x + w + gap, 280), color, 3, 12)
        x += w + gap

    rbox(d, (80, 420, 1720, 500), INDIGO_SOFT, INDIGO, radius=12)
    label(d, (900, 460), "Countermeasure at every stage:  training  ·  sender verification  ·  link inspection  ·  "
                         "MFA  ·  reporting  ·  least privilege", font(14, True), INDIGO)
    img.save(os.path.join(OUT, "attack_chain.png"))


if __name__ == "__main__":
    architecture()
    dfd()
    usecase()
    er()
    workflow()
    attack_chain()
    print("Wrote figures to", OUT)
