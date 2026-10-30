"""Participant-facing pages: inbox, mail, landing, coaching and quiz."""
from __future__ import annotations

import json

from . import analytics as an
from .db import now
from .seed import QUIZ
from .ui import avatar, chip, esc, page_public

LEGIT_MAILS = [
    ("Team lunch on Friday — please RSVP", "Alex Fernandes", "manager@northstar.example",
     "<p>Hi team,</p><p>Team lunch is this Friday at 1 PM in the cafeteria. Please reply by Thursday "
     "so I can book the table.</p><p>Thanks,<br>Alex</p>"),
    ("Your leave request has been approved", "HR Desk", "hr@northstar.example",
     "<p>Hi,</p><p>Your leave request for 12 October has been <b>approved</b>. Please update your "
     "team calendar.</p><p>Regards,<br>Human Resources</p>"),
    ("Payroll calendar for next month", "Payroll", "payroll@northstar.example",
     "<p>Hello,</p><p>The payroll cut-off for next month is the 25th. No action is needed if your "
     "bank details are unchanged.</p><p>Payroll Team</p>"),
]


def render_mail(t, token: str, *, preview: bool = False, back: str = "/inbox") -> str:
    """Render a simulated email exactly as the recipient would see it."""
    href = "#" if preview else f"/t/{esc(token)}/landing"
    domain = (t["sender_email"] or "mail.example").split("@")[-1]
    shown_url = f"https://{domain}/account/verify?session=8f2c"
    flags = [f for f in (t["flags"] or "").split("||") if f]
    spoiler = ""
    if flags:
        spoiler = (f'<details class=spoiler><summary>Training aid — reveal the red flags in this mail</summary>'
                   f'<div class=in><ul>{"".join(f"<li>{f}</li>" for f in flags)}</ul></div></details>')
    report_button = ""
    if not preview:
        report_button = (f'<form method=post action="/t/{esc(token)}/report" style="display:inline">'
                         f'<button class="btn btn-ok">🛡 Report as phishing</button></form>')
    return f"""<div class=mwin>
 <div class=mbar><span class=traffic><i style="background:#ef4444"></i><i style="background:#f59e0b"></i><i style="background:#22c55e"></i></span>
  Simulated mailbox — {esc(t['brand'] or 'Mail')}</div>
 <div class=mhdr><div style="flex:1">
   <div class=sj>{esc(t['subject'])}</div>
   <div class=mfield><b>From</b> {esc(t['sender_name'])} &lt;{esc(t['sender_email'])}&gt;</div>
   <div class=mfield><b>To</b> you</div>
  </div></div>
 <div class=mbody>{t['body']}
  <div><a class=fakelink href="{href}">{esc(t['cta'] or 'Open Link')} →</a></div>
  <div class=urlpeek>Link destination: {esc(shown_url)}</div>
 </div>
 <div class=mfoot>
  {'<span class="chip warn">Preview only — no tracking</span>' if preview else report_button}
  <a class="btn btn-s" href="{esc(back)}">← Back to inbox</a>
  <span class=spacer></span><span class=tiny>Simulation only</span>
 </div>
 {spoiler}
</div>"""


def inbox_view(conn, employee_email: str) -> str:
    employees = conn.execute("SELECT * FROM employees WHERE active=1 ORDER BY name").fetchall()
    if not employees:
        return page_public("Inbox", '<div class=card>No participants yet.</div>')

    email = employee_email or employees[0]["email"]
    employee = next((e for e in employees if e["email"] == email), employees[0])
    rows = conn.execute(
        """SELECT tg.*, t.subject, t.sender_name, t.sender_email, t.difficulty, t.brand,
                  c.name campaign_name, c.status
           FROM targets tg JOIN campaigns c ON c.id=tg.campaign_id JOIN templates t ON t.id=c.template_id
           WHERE tg.employee_id=? AND c.status IN ('Active','Paused','Completed') ORDER BY tg.id DESC""",
        (employee["id"],)).fetchall()

    side = "".join(
        f'<a class="pick{" on" if e["email"] == email else ""}" href="/inbox?email={esc(e["email"])}">'
        f'{avatar(e["name"], e["department"])}<div><div class=n>{esc(e["name"])}</div>'
        f'<div class=e>{esc(e["department"])}</div></div></a>' for e in employees)

    mails = ""
    for t in rows:
        if t["reported_at"]:
            badge = chip("Reported", "ok")
        elif t["submitted_at"]:
            badge = chip("Submitted", "bad")
        elif t["clicked_at"]:
            badge = chip("Clicked", "warn")
        elif t["opened_at"]:
            badge = chip("Opened", "info")
        else:
            badge = chip("Unread", "mute")
        mails += f"""<div class=mailrow><div class=mtop><span class=unread></span>
 <span class=sj>{esc(t['subject'])}</span>{badge}</div>
 <div class=tiny style="margin:4px 0 0 18px">{esc(t['sender_name'])} &lt;{esc(t['sender_email'])}&gt; · {esc(t['campaign_name'])}</div>
 <div class=macts><a class="btn btn-s btn-xs" href="/t/{esc(t['token'])}">Open mail</a>
 {'' if t['reported_at'] else f'<form method=post action="/t/{esc(t["token"])}/report" style="display:inline"><button class="btn btn-s btn-xs">🛡 Report phish</button></form>'}
 {'<span class="chip ok">Already reported</span>' if t['reported_at'] else ''}</div></div>"""

    legit = "".join(
        f"""<div class=mailrow><div class=mtop><span class=sj>{esc(subject)}</span>{chip('Legitimate', 'ok')}</div>
 <div class=tiny style="margin:4px 0 0 0">{esc(sender)} &lt;{esc(addr)}&gt;</div>
 <div class=macts><a class="btn btn-s btn-xs" href="/legit/{i}?email={esc(email)}">Open mail</a>
 <span class=tiny>No tracking — this one is genuine.</span></div></div>"""
        for i, (subject, sender, addr, _) in enumerate(LEGIT_MAILS))

    body = f"""
<div class=hero><div><div class=eyebrow>Participant view</div><h1>Simulated inbox</h1>
 <p>Each mailbox mixes simulated phishing with legitimate internal mail, so the task is to
 discriminate — not simply to distrust everything.</p></div>
 <span class="chip warn">Simulation only</span></div>
<div class=inbox>
 <div class=side><div class=side-h>Participants ({len(employees)})</div>{side}</div>
 <div class=card style="padding:0;overflow:hidden">
  <div class=chead style="padding:16px 18px;margin:0"><div><h3>{esc(employee['name'])}</h3>
   <div class=sub>{esc(employee['email'])} · {esc(employee['department'])} · {len(rows)} simulated campaign mail(s)</div></div>
   {'<span class="chip ok">Consent recorded</span>' if employee['consent'] else '<span class="chip bad">Consent missing</span>'}</div>
  <div style="padding:0 18px 8px"><div class="note" style="margin:10px 0 4px">
   <b>Your task:</b> open the mail, decide whether it is genuine, and use <b>Report as phishing</b>
   when something is wrong. Every action is recorded for the study — not for performance review.</div></div>
  <div class=side-h style="margin-top:8px">Campaign mail</div>{mails or '<div class=empty>No campaign mail yet.</div>'}
  <div class=side-h>Legitimate mail</div>{legit}
 </div>
</div>"""
    return page_public("Inbox", body, wide=True)


def legit_view(index: int, email: str) -> str:
    if not 0 <= index < len(LEGIT_MAILS):
        return page_public("Not found", '<div class=card>Message not found.</div>')
    subject, sender, addr, body_html = LEGIT_MAILS[index]
    body = f"""<div class=mwin><div class=mbar><span class=traffic><i style="background:#ef4444"></i>
 <i style="background:#f59e0b"></i><i style="background:#22c55e"></i></span>Simulated mailbox — genuine mail</div>
 <div class=mhdr><div><div class=sj>{esc(subject)}</div>
  <div class=mfield><b>From</b> {esc(sender)} &lt;{esc(addr)}&gt;</div></div></div>
 <div class=mbody>{body_html}</div>
 <div class=mfoot><a class="btn btn-s" href="/inbox?email={esc(email)}">← Back to inbox</a>
  <span class="chip ok">No tracking on this message</span></div></div>"""
    return page_public("Legitimate mail", body)


def mail_view(conn, token: str) -> str:
    row = conn.execute(
        """SELECT tg.*, t.*, c.name campaign_name, c.status, e.name employee_name, e.email employee_email
           FROM targets tg JOIN campaigns c ON c.id=tg.campaign_id JOIN templates t ON t.id=c.template_id
           JOIN employees e ON e.id=tg.employee_id WHERE tg.token=?""", (token,)).fetchone()
    if not row:
        return page_public("Not found", '<div class=card>This simulated link is not valid.</div>')
    if not row["opened_at"] and row["status"] not in ("Draft", "Scheduled"):
        conn.execute("UPDATE targets SET opened_at=? WHERE token=? AND opened_at IS NULL", (now(), token))
        conn.commit()
    header = f"""<div class=hero><div><div class=eyebrow>Simulated mail</div>
 <h1>{esc(row['subject'])}</h1><p>Delivered from <span class=mono>{esc(row['sender_email'])}</span>
 in campaign <b>{esc(row['campaign_name'])}</b>.</p></div></div>"""
    return page_public("Mail", header + render_mail(row, token),
                       wide=True)


def landing_view(conn, token: str) -> str:
    row = conn.execute(
        """SELECT tg.*, t.* FROM targets tg JOIN campaigns c ON c.id=tg.campaign_id
           JOIN templates t ON t.id=c.template_id WHERE tg.token=?""", (token,)).fetchone()
    if not row:
        return page_public("Not found", '<div class=card>This simulated link is not valid.</div>')
    if not row["clicked_at"]:
        conn.execute("UPDATE targets SET clicked_at=? WHERE token=? AND clicked_at IS NULL", (now(), token))
        conn.commit()
    brand = row["brand"] or "Sign in"
    body = f"""
<div class=hero style="max-width:460px;margin:0 auto 14px"><div style="text-align:center;width:100%">
 <span class="chip warn">Simulated login page — do not enter a real password</span></div></div>
<div style="max-width:440px;margin:0 auto">
 <div class=urlbar style="background:#fff;border:1px solid var(--line);border-radius:10px;padding:9px 14px;
  box-shadow:var(--sh);display:flex;align-items:center;gap:10px;font-size:12.5px;margin-bottom:14px">
  <span style="color:#059669">🔒</span><span class=mono style="color:#48566b">http://127.0.0.1:8000/t/{esc(token[:8])}…</span>
  <span class=tiny style="margin-left:auto">not {esc(brand.lower())}.com</span></div>
 <div class=login-card>
  <div class=lh><div class=lg2 style="font-size:13px;letter-spacing:.02em">{esc(brand[:2].upper())}</div>
   <h2>{esc(brand)}</h2><p>{esc(row['tagline'])}</p></div>
  <div class=lf>
   <div class="note warn" style="margin-bottom:14px;font-size:12.5px"><b>This is a simulation.</b>
    Type anything you like — values are discarded, only the field names are stored.</div>
   <form method=post action="/t/{esc(token)}/submit">{row['landing']}
    <button class="btn btn-p" type=submit>{esc(row['cta'] or 'Sign in')}</button></form>
  </div>
  <div class=lfoot>Your IT department will never ask you to sign in from an email link.
   <a href="/t/{esc(token)}">← Back to the message</a></div>
 </div>
</div>"""
    return page_public("Sign in", body)


def submitted_view(conn, token: str) -> str:
    row = conn.execute(
        """SELECT tg.*, t.*, c.name campaign_name, e.email AS employee_email
           FROM targets tg JOIN campaigns c ON c.id=tg.campaign_id
           JOIN templates t ON t.id=c.template_id
           JOIN employees e ON e.id=tg.employee_id WHERE tg.token=?""", (token,)).fetchone()
    if not row:
        return page_public("Not found", '<div class=card>This simulated link is not valid.</div>')
    flags = [f for f in (row["flags"] or "").split("||") if f]
    body = f"""
<div class=rhero><div class=ico>⚠️</div><h2>You submitted credentials to a simulated phishing page</h2>
 <p>Nothing was stored and no account was harmed — but in a real attack this is the moment an
 attacker gains a foothold. Here is exactly what gave the message away.</p></div>
<div class="grid g2" style="margin-top:18px">
 {''.join(f'<div class=flag><div class=fh>🚩 Red flag {i + 1}</div><p>{f}</p></div>' for i, f in enumerate(flags))}
</div>
<div class=card style="margin-top:18px"><div class=chead><div><h3>What happens next in a real incident</h3></div></div>
 <div class=steps>
  <div class=step><div class=n>1</div><b>Credential replay</b><p>The attacker signs in from another country within minutes.</p></div>
  <div class=step><div class=n>2</div><b>Mailbox rules</b><p>Forwarding rules hide invoices and reset confirmations.</p></div>
  <div class=step><div class=n>3</div><b>Lateral movement</b><p>Shared drives and chat are used to phish colleagues.</p></div>
  <div class=step><div class=n>4</div><b>Containment</b><p>Password reset, session revocation and MFA re-enrolment.</p></div>
 </div></div>
<div style="text-align:center;margin-top:22px">
 <a class="btn btn-p" href="/quiz?email={esc(row['employee_email'])}">Take the 2-minute awareness quiz →</a>
 <a class="btn btn-s" href="/inbox?email={esc(row['employee_email'])}">Back to inbox</a></div>"""
    return page_public("You were phished", body, wide=True)


def reported_view(conn, token: str) -> str:
    row = conn.execute(
        """SELECT tg.*, t.subject, e.name employee_name, e.email employee_email
           FROM targets tg JOIN templates t ON t.id=(SELECT template_id FROM campaigns WHERE id=tg.campaign_id)
           JOIN employees e ON e.id=tg.employee_id WHERE tg.token=?""", (token,)).fetchone()
    name = row["employee_name"] if row else "participant"
    email = row["employee_email"] if row else ""
    body = f"""
<div class="rhero good"><div class=ico>🛡️</div><h2>Reported. That is exactly the right action.</h2>
 <p>Your report lets IT block the sender for everyone. In a real campaign this is the single most
 valuable behaviour we measure.</p></div>
<div class=card style="margin-top:18px"><div class=chead><div><h3>Why reporting beats deleting</h3></div></div>
 <div class="grid g3">
  <div><b>It protects colleagues</b><p class=tiny style="margin-top:4px">IT can quarantine the sender and warn everyone who received the same mail.</p></div>
  <div><b>It creates evidence</b><p class=tiny style="margin-top:4px">Reported messages are analysed for new lures and indicators.</p></div>
  <div><b>It closes the loop</b><p class=tiny style="margin-top:4px">Your report is counted in the reporting rate — the metric we want to rise.</p></div>
 </div></div>
<div style="text-align:center;margin-top:22px">
 <a class="btn btn-p" href="/quiz?email={esc(email)}">Take the awareness quiz →</a>
 <a class="btn btn-s" href="/inbox?email={esc(email)}">Back to inbox</a></div>"""
    return page_public(f"Reported — {name}", body)


def quiz_view(conn, email: str = "") -> str:
    employees = conn.execute("SELECT * FROM employees WHERE active=1 ORDER BY name").fetchall()
    options = "".join(
        f'<option value="{esc(e["email"])}"{" selected" if e["email"] == email else ""}>{esc(e["name"])} — {esc(e["department"])}</option>'
        for e in employees)
    questions = ""
    for i, (prompt, answers, _correct) in enumerate(QUIZ):
        opts = "".join(
            f'<label class=opt><input type=radio name=q{i} value="{j}" required> {ans}</label>'
            for j, ans in enumerate(answers))
        questions += (f'<div class=q><div class=qh><div class=qn>{i + 1}</div>'
                      f'<div class=qt>{prompt}</div></div><div class=opts>{opts}</div></div>')
    body = f"""
<div class=hero><div><div class=eyebrow>Awareness training</div><h1>Phishing recognition quiz</h1>
 <p>{len(QUIZ)} questions, single best answer. Your score is stored against your participant record
 so the programme can measure whether training worked.</p></div>
 <span class="chip brand">~2 minutes</span></div>
<form method=post action="/quiz">
 <div class=card style="margin-bottom:14px"><div class=field style="margin:0">
  <label>Who is taking the quiz?</label><select name=email required>{options}</select></div></div>
 {questions}
 <button class="btn btn-p" type=submit>Submit answers</button>
 <a class="btn btn-s" href="/inbox">Cancel</a></form>"""
    return page_public("Quiz", body)


def quiz_result_view(conn, *, email: str, score: int, answers: list[int],
                     campaign_id: int | None = None) -> str:
    total = len(QUIZ)
    band = (("Excellent", "You can spot phishing reliably. Keep reporting and slow down on urgency.", "#059669")
            if score >= total * 0.875 else
            ("Good", "Most tells were caught. Review the questions you missed, then retake it.", "#2563eb")
            if score >= total * 0.625 else
            ("Needs practice", "Several core tells were missed. Read the red-flag pages again and retake.", "#d97706")
            if score >= total * 0.375 else
            ("At risk", "This score is in the high-risk band. Please complete a one-to-one debrief.", "#dc2626"))
    review = ""
    for i, (prompt, answers_text, correct) in enumerate(QUIZ):
        given = answers[i] if i < len(answers) else -1
        ok = given == correct
        review += f"""<div class=q style="border-color:{'#b9e8d5' if ok else '#f7c9c9'}">
 <div class=qh><div class=qn style="background:{'#e7f7f1' if ok else '#fdecec'};color:{'#047857' if ok else '#b11d1d'}">
  {'✓' if ok else '✕'}</div><div class=qt>{prompt}</div></div>
 <div style="font-size:13px;color:var(--ink2)">Your answer: <b>{esc(answers_text[given]) if 0 <= given < len(answers_text) else 'not answered'}</b>
 {'<br>Correct answer: <b>' + esc(answers_text[correct]) + '</b>' if not ok else ''}</div></div>"""
    body = f"""
<div class=card style="text-align:center;padding:30px"><div class=scorebig>{score} / {total}</div>
 <h2 style="margin:10px 0 6px;color:{band[2]}">{band[0]}</h2>
 <p style="color:var(--ink2);font-size:15px;max-width:52ch;margin:0 auto">{band[1]}</p>
 <div style="margin-top:20px"><a class="btn btn-s" href="/quiz?email={esc(email)}">Retake</a>
  <a class="btn btn-s" href="/inbox?email={esc(email)}">Inbox</a></div></div>
<div class=side-h style="margin:22px 0 10px">Answer review</div>{review}"""
    return page_public("Quiz result", body)
