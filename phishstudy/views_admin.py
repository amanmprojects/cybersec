"""Server-rendered admin console pages."""
from __future__ import annotations

import json

from . import analytics as an
from .db import get_setting
from .seed import QUIZ
from .ui import (OUTCOME_CHIP, avatar, chip, department_bars, donut, empty_state, esc, funnel, kpi,
                 page_admin, page_public, risk_badge, risk_bar, sparkline, status_chip)
from .views_participant import render_mail as _render_mail


def _btn(path: str, label: str, csrf: str, *, cls: str = "btn btn-s btn-xs",
         confirm: str = "", name: str = "", value: str = "") -> str:
    extra = f' name="{esc(name)}" value="{esc(value)}"' if name else ""
    warn = f' onclick="return confirm(\'{confirm}\')"' if confirm else ""
    return (f'<form method=post action="{esc(path)}" style="display:inline">'
            f'<input type=hidden name=csrf value="{esc(csrf)}">'
            f'<button class="{cls}"{extra}{warn}>{label}</button></form>')


# ----------------------------------------------------------------------- login
def login_view(*, error: str = "", next_url: str = "/", demo: bool = True) -> str:
    demo_note = ("<div class=lfoot><b>Demo credentials</b><br>"
                 "Username <span class=mono>admin</span> · Password <span class=mono>admin123</span>"
                 "<br>Change this password in Settings after your first login.</div>") if demo else ""
    err = f'<div class="note bad" style="margin-bottom:14px">{esc(error)}</div>' if error else ""
    body = f"""<div class=login-stage><div style="width:100%;max-width:420px">
 <div style="text-align:center;margin-bottom:14px">
  <span class="chip warn" style="font-size:11.5px">Simulation for education only</span></div>
 <div class=login-card>
  <div class=lh><div class=lg2>🎣</div><h2>PhishStudy Console</h2>
   <p>Simulated phishing campaigns &amp; awareness training</p></div>
  <div class=lf>{err}
   <form method=post action="/login">
    <input type=hidden name=next value="{esc(next_url)}">
    <div class=field><label>Username</label><input name=username autocomplete=username autofocus required></div>
    <div class=field><label>Password</label><input name=password type=password autocomplete=current-password required></div>
    <button class="btn btn-p" type=submit>Sign in</button>
   </form>
  </div>{demo_note}
 </div>
 <p style="text-align:center;font-size:12px;color:var(--muted);margin-top:14px">
  All emails, employees and credentials are fictional. No mail is ever sent.</p>
</div></div>"""
    return page_public("Sign in", body)


# ------------------------------------------------------------------- dashboard
def dashboard_view(conn, admin: dict) -> str:
    ov = an.overview(conn)
    camps = an.campaigns(conn)
    risks = an.employee_risk(conn)
    quiz = an.quiz_stats(conn)
    trend = an.campaign_trend(conn)
    recent = [c for c in camps if c["status"] in ("Active", "Paused")][:3]
    pending = sum(1 for c in camps if c["status"] in ("Draft", "Scheduled"))
    critical = sum(1 for r in risks if r["band"] == "Critical")
    high = sum(1 for r in risks if r["band"] == "High")

    kpis = "".join([
        kpi("Overall phish rate", f'{ov["submit_rate"]}%', f'{ov["submitted"]} of {ov["sent"]} simulated recipients', "🎯", "#dc2626", "#fdecec"),
        kpi("Reporting rate", f'{ov["report_rate"]}%', f'{ov["reported"]} reported to IT', "🛡", "#059669", "#e7f7f1"),
        kpi("Training completion", f'{ov["training_completion"]}%', f'{quiz["attempts"]} quiz attempts recorded', "🎓", "#4f46e5", "#eef0ff"),
        kpi("High-risk people", critical + high, f'{critical} critical · {high} high', "⚠", "#d97706", "#fdf3e4"),
    ])

    trend_rows = "".join(
        f'<tr><td><a href="/campaigns/{c["id"]}">{esc(c["name"])}</a></td>'
        f'<td>{chip(c["difficulty"], "mute")}</td>'
        f'<td class=num>{c["sent"]}</td><td class=num>{c["submit_rate"]}%</td>'
        f'<td class=num>{c["report_rate"]}%</td></tr>' for c in trend)

    top = risks[:6]
    risk_rows = "".join(
        f'<tr><td><div class=who>{avatar(r["name"], r["department"])}'
        f'<div><div class=n>{esc(r["name"])}</div><div class=e>{esc(r["department"])} · {esc(r["designation"])}</div></div></div></td>'
        f'<td class=num>{r["submitted"]}/{r["sent"]}</td><td>{risk_bar(r["risk"], r["band"])}</td>'
        f'<td>{risk_badge(r["band"])}</td></tr>' for r in top)

    active_html = ""
    for c in recent:
        active_html += f"""<div class=card style="padding:16px 18px">
 <div class=chead style="margin-bottom:10px"><div><h3 style="font-size:14.5px">{esc(c['name'])}</h3>
  <div class=sub>{esc(c['template_name'])} · {c['audience']}</div></div>{status_chip(c['status'])}</div>
 <div class=strip style="margin-bottom:10px">{_mini(c)}</div>
 <div class=tiny>Click {c['click_rate']}% · Submit {c['submit_rate']}% · Report {c['report_rate']}%</div>
 <a class="btn btn-s btn-xs" style="margin-top:10px" href="/campaigns/{c['id']}">Open campaign →</a></div>"""
    if not active_html:
        active_html = empty_state("◈", "No live campaign", "Create a campaign to start measuring susceptibility.",
                                  '<a class="btn btn-p btn-xs" style="margin-top:12px" href="/campaigns">Create campaign</a>')

    body = f"""
<div class=hero><div><div class=eyebrow>Admin console</div>
 <h1>Phishing susceptibility overview</h1>
 <p>Every number below comes from a simulated campaign. Open rates, click rates and credential
 submissions are recorded on fictional employees so the programme can be measured without risk.</p></div>
 <div style="display:flex;gap:8px"><a class="btn btn-p" href="/campaigns">＋ New campaign</a>
 <a class="btn btn-s" href="/people">Manage people</a></div></div>
<div class="grid g4" style="margin-bottom:16px">{kpis}</div>
<div class="grid g2" style="margin-bottom:16px">
 <div class=card><div class=side-h style="margin:-20px -20px 16px">Funnel · all launched campaigns</div>
  {funnel(ov)}
  <div class="note" style="margin-top:18px"><b>How to read this:</b> a recipient who submits credentials
  would be fully compromised in a real attack. A recipient who reports stops the attack for the whole organisation.</div></div>
 <div class=card><div class=side-h style="margin:-20px -20px 16px">Outcome breakdown</div>
  {donut([("Submitted", ov["outcomes"].get("submitted", 0), "#dc2626"),
          ("Clicked only", ov["outcomes"].get("clicked", 0), "#f59e0b"),
          ("Opened only", ov["outcomes"].get("opened", 0), "#2563eb"),
          ("Reported", ov["outcomes"].get("reported", 0), "#059669"),
          ("No response", ov["outcomes"].get("sent", 0), "#cbd5e1")],
         f'{ov["submit_rate"]}%', "PHISHED")}
  <div class="note" style="margin-top:16px"><b>Reporting:</b> {ov["reported"]} of {ov["sent"]} recipients
  used the Report-Phish channel — {ov["report_rate"]}% against a {ov["click_rate"]}% click rate.</div></div>
</div>
<div class="grid g2" style="margin-bottom:16px">
 <div class=card><div class=chead><div><h3>Campaign trend</h3>
  <div class=sub>Submission rate should fall as awareness training lands</div></div>
  <a class="btn btn-s btn-xs" href="/analytics">Full analytics</a></div>
  {sparkline([c["submit_rate"] for c in trend], "#dc2626")}
  <div class="table-wrap" style="margin-top:12px"><table><thead><tr><th>Campaign</th><th>Difficulty</th>
   <th class=num>Sent</th><th class=num>Phished</th><th class=num>Reported</th></tr></thead><tbody>{trend_rows}</tbody></table></div>
 </div>
 <div class=card><div class=chead><div><h3>Highest-risk people</h3>
  <div class=sub>Risk combines submission, clicking, reporting and quiz performance</div></div>
  <a class="btn btn-s btn-xs" href="/people">All people</a></div>
  <div class=table-wrap><table><thead><tr><th>Person</th><th class=num>Phished</th><th>Risk</th><th></th></tr></thead>
  <tbody>{risk_rows}</tbody></table></div>
  <div class="note warn" style="margin-top:14px"><b>Priority:</b> start with the Critical band — a short
  face-to-face debrief plus a repeat quiz moves the score fastest.</div>
 </div>
</div>
<div class=chead><div><h3>Live &amp; paused campaigns</h3><div class=sub>{len(recent)} campaign(s) collecting responses</div></div>
 <a class="btn btn-s btn-xs" href="/campaigns">All campaigns</a></div>
<div class="grid g3" style="margin-bottom:18px">{active_html}</div>
<div class=card><div class=chead><div><h3>Programme checklist</h3>
 <div class=sub>What a complete simulation cycle looks like</div></div>
 <span class="chip {'ok' if ov['sent'] else 'warn'}">{'Data collected' if ov['sent'] else 'Not started'}</span></div>
<div class=steps>
 <div class=step><div class=n>1</div><b>Consent &amp; scope</b><p>Confirm written permission and the employee list. Record consent per person.</p></div>
 <div class=step><div class=n>2</div><b>Baseline campaign</b><p>Launch an Easy/Medium/Hard lure and measure click and submission rates.</p></div>
 <div class=step><div class=n>3</div><b>Debrief &amp; training</b><p>Show the red-flag page to everyone who engaged, then run the awareness quiz.</p></div>
 <div class=step><div class=n>4</div><b>Re-measure</b><p>Repeat with the same template and compare. A falling submission rate is the outcome.</p></div>
</div></div>"""
    return page_admin("Dashboard", body, "/", admin, pending=pending,
                      actions='<a class="btn btn-s btn-xs" href="/api/export.csv">⬇ CSV</a>'
                              '<a class="btn btn-s btn-xs" href="/report">▤ Report</a>')


def _mini(c: dict) -> str:
    return "".join(f'<div><div class=sl>{label}</div><div class=sv style="color:{color}">{c[key]}</div></div>'
                   for label, key, color in [("Sent", "sent", "#0d1424"), ("Opened", "opened", "#2563eb"),
                                             ("Clicked", "clicked", "#d97706"), ("Phished", "submitted", "#dc2626"),
                                             ("Reported", "reported", "#059669")])


# ------------------------------------------------------------------- campaigns
def campaigns_view(conn, admin: dict) -> str:
    camps = an.campaigns(conn)
    templates = conn.execute("SELECT * FROM templates WHERE active=1 ORDER BY difficulty DESC, name").fetchall()
    departments = [r["department"] for r in conn.execute(
        "SELECT DISTINCT department FROM employees WHERE active=1 ORDER BY department").fetchall()]

    rows = ""
    for c in camps:
        live = c["status"] not in ("Draft", "Scheduled")
        sent_cell = c["sent"] if live else "—"
        rows += f"""<tr>
 <td><a href="/campaigns/{c['id']}" style="font-weight:600">{esc(c['name'])}</a>
  <div class=tiny>{esc(c['template_name'])} · {esc(c['audience'])}</div></td>
 <td>{status_chip(c['status'])}</td>
 <td>{chip(c['difficulty'], 'mute')}</td>
 <td class=num>{sent_cell}</td><td class=num>{c['click_rate'] if live else '—'}%</td>
 <td class=num style="color:#b11d1d;font-weight:600">{c['submit_rate'] if live else '—'}%</td>
 <td class=num style="color:#046c50;font-weight:600">{c['report_rate'] if live else '—'}%</td>
 <td style="white-space:nowrap">{_actions(c, admin['csrf'])}</td></tr>"""
    if not rows:
        rows = '<tr><td colspan=8>' + empty_state("◈", "No campaigns yet", "Create your first simulated campaign on the right.") + '</td></tr>'

    dept_opts = "".join(f'<option value="{esc(d)}">{esc(d)}</option>' for d in departments)
    tpl_opts = "".join(
        f'<option value="{t["id"]}">{esc(t["name"])} · {esc(t["difficulty"])}</option>' for t in templates)

    body = f"""
<div class=hero><div><div class=eyebrow>Campaigns</div><h1>Simulated phishing campaigns</h1>
 <p>A campaign pairs one lure with an audience. Launching creates a unique tracking token per
 recipient; opening, clicking, submitting and reporting are timestamped independently.</p></div></div>
<div class=card style="margin-bottom:16px"><div class=chead><div><h3>All campaigns</h3>
 <div class=sub>{len(camps)} campaign(s) · {sum(c['sent'] for c in camps if c['status'] not in ('Draft', 'Scheduled'))} simulated deliveries</div></div></div>
 <div class=table-wrap><table><thead><tr><th>Campaign</th><th>Status</th><th>Difficulty</th>
  <th class=num>Sent</th><th class=num>Click</th><th class=num>Phished</th><th class=num>Reported</th><th></th></tr></thead>
  <tbody>{rows}</tbody></table></div></div>
<div class="grid g2">
 <div class=card><div class=chead><div><h3>Launch a campaign</h3><div class=sub>Targets are created immediately unless a start date is set</div></div></div>
  <form method=post action="/campaigns">
   <input type=hidden name=csrf value="{esc(admin['csrf'])}">
   <div class=field><label>Campaign name</label><input name=name placeholder="e.g. Q4 Baseline — Finance" required></div>
   <div class=field><label>Lure template</label><select name=template_id required>{tpl_opts}</select></div>
   <div class=field><label>Audience</label><select name=audience>
     <option value="All departments">All active employees</option>
     <option value="__dept__">One department…</option>
     <option value="__selected__">Selected departments…</option></select>
    <div class=hint>Choose <b>One department</b> below, or hold Ctrl/Cmd to pick several.</div></div>
   <div class=field><label>Department filter <span class=tiny>(optional)</span></label>
    <select name=departments multiple size=5>{dept_opts}</select></div>
   <div class=row><div class=field><label>Phase</label>
     <select name=phase><option>Baseline</option><option>Post-training</option><option>Live</option><option>Planned</option></select></div>
    <div class=field><label>Start date <span class=tiny>(optional)</span></label><input type=date name=scheduled_for></div></div>
   <div class=field><label>Notes</label><input name=notes placeholder="Scope, approval reference, etc."></div>
   <button class="btn btn-p">Create campaign</button>
  </form></div>
 <div class=card><div class=chead><div><h3>Campaign lifecycle</h3><div class=sub>Every transition is written to the audit log</div></div></div>
  <div class=dept>
   <div class=dp><span class=dp-n>Draft</span><span class=dp-v>Created, no targets yet</span></div>
   <div class=dp><span class=dp-n>Scheduled</span><span class=dp-v>Targets generated; waits for the start date</span></div>
   <div class=dp><span class=dp-n>Active</span><span class=dp-v>Collecting open / click / submit / report events</span></div>
   <div class=dp><span class=dp-n>Paused</span><span class=dp-v>Links stay valid, no new sends</span></div>
   <div class=dp><span class=dp-n>Completed</span><span class=dp-v>Closed and included in analytics</span></div>
   <div class=dp><span class=dp-n>Archived</span><span class=dp-v>Hidden from dashboards, retained for audit</span></div>
  </div>
  <div class="note" style="margin-top:16px"><b>Ethics gate:</b> a campaign can only be launched when every
  recipient has consent recorded. Manage consent on the People page.</div>
 </div>
</div>"""
    return page_admin("Campaigns", body, "/campaigns", admin)


def _actions(c: dict, csrf: str) -> str:
    out = []
    if c["status"] in ("Draft", "Scheduled"):
        out.append(_btn(f"/campaigns/{c['id']}/launch", "Launch", csrf, cls="btn btn-p btn-xs"))
    if c["status"] == "Active":
        out.append(_btn(f"/campaigns/{c['id']}/pause", "Pause", csrf, cls="btn btn-s btn-xs"))
    if c["status"] == "Paused":
        out.append(_btn(f"/campaigns/{c['id']}/resume", "Resume", csrf, cls="btn btn-p btn-xs"))
    if c["status"] in ("Active", "Paused"):
        out.append(_btn(f"/campaigns/{c['id']}/complete", "Complete", csrf, cls="btn btn-s btn-xs"))
    out.append(f'<a class="btn btn-s btn-xs" href="/campaigns/{c["id"]}">Open</a>')
    return " ".join(out)


def campaign_detail_view(conn, admin: dict, campaign_id: int) -> str:
    c = conn.execute("""SELECT c.*, t.name template_name, t.difficulty, t.category, t.subject, t.id template_id
                        FROM campaigns c JOIN templates t ON t.id=c.template_id WHERE c.id=?""",
                     (campaign_id,)).fetchone()
    if not c:
        return page_admin("Not found", empty_state("✕", "Campaign not found", "It may have been deleted."),
                          "/campaigns", admin)
    stats = an.campaign_stats(conn, campaign_id)
    targets = conn.execute(
        """SELECT tg.*, e.name, e.email, e.department, e.designation FROM targets tg
           JOIN employees e ON e.id=tg.employee_id WHERE tg.campaign_id=? ORDER BY e.name""",
        (campaign_id,)).fetchall()
    depts = _campaign_departments(targets)
    timeline = _timeline(targets)

    rows = ""
    for t in targets:
        outcome = an.outcome_of(t)
        cls, icon, label = OUTCOME_CHIP[outcome]
        rows += f"""<tr><td><div class=who>{avatar(t['name'], t['department'])}
 <div><div class=n>{esc(t['name'])}</div><div class=e>{esc(t['email'])}</div></div></div></td>
 <td>{chip(t['department'], 'mute')}</td>
 <td>{chip(f'{icon} {label}', cls)}</td>
 <td class=num>{esc(t['opened_at'] or '—')}</td>
 <td class=num>{esc(t['clicked_at'] or '—')}</td>
 <td class=num>{esc(t['submitted_at'] or '—')}</td>
 <td class=num>{esc(t['reported_at'] or '—')}</td>
 <td><a class="btn btn-s btn-xs" href="/t/{esc(t['token'])}">View mail</a></td></tr>"""

    actions = _actions(dict(c, **stats), admin['csrf'])
    body = f"""
<div class=hero><div><div class=eyebrow>Campaign</div><h1>{esc(c['name'])}</h1>
 <p>{esc(c['template_name'])} · {esc(c['category'])} · audience: {esc(c['audience'])}</p>
 <div class=ctag style="margin-top:9px">{status_chip(c['status'])} {chip(c['phase'], 'brand')}
  {chip('Difficulty · ' + c['difficulty'], 'warn')}</div></div>
 <div style="display:flex;gap:8px;flex-wrap:wrap">{actions}</div></div>
<div class=strip>{_mini(stats)}</div>
<div class="grid g2" style="margin-bottom:16px">
 <div class=card><div class=side-h style="margin:-20px -20px 16px">Funnel</div>{funnel(stats)}
  <div class="note" style="margin-top:16px"><b>Submission rate {stats['submit_rate']}%</b> ·
  reporting {stats['report_rate']}% · click {stats['click_rate']}%. Reporting is counted against
  recipients who did not submit, so it measures positive behaviour rather than damage control.</div></div>
 <div class=card><div class=side-h style="margin:-20px -20px 16px">Susceptibility by department</div>
  {department_bars(depts)}
  <div class=note style="margin-top:16px"><b>Highest risk:</b> {esc(depts[0]['department']) if depts else '—'} ·
  {depts[0]['submitted'] if depts else 0} of {depts[0]['sent'] if depts else 0} submitted.</div></div>
</div>
<div class="grid g2" style="margin-bottom:16px">
 <div class=card><div class=chead><div><h3>Targets</h3><div class=sub>{len(targets)} recipient(s)</div></div></div>
  <div class=table-wrap style="max-height:420px;overflow:auto"><table><thead><tr><th>Person</th><th>Dept</th><th>Outcome</th>
   <th class=num>Opened</th><th class=num>Clicked</th><th class=num>Submitted</th><th class=num>Reported</th><th></th></tr></thead>
   <tbody>{rows or '<tr><td colspan=8>No targets yet — launch the campaign.</td></tr>'}</tbody></table></div></div>
 <div class=card><div class=chead><div><h3>Event timeline</h3><div class=sub>Most recent simulated interactions</div></div></div>
  {timeline or empty_state('◷', 'No events yet', 'Events appear as recipients interact with the simulated mail.')}</div>
</div>
<div class=card><div class=chead><div><h3>Campaign metadata</h3></div></div>
 <dl class=kv><dt>Template</dt><dd>{esc(c['template_name'])} ({esc(c['difficulty'])})</dd>
 <dt>Subject line</dt><dd class=mono>{esc(c['subject'])}</dd>
 <dt>Audience</dt><dd>{esc(c['audience'])}</dd>
 <dt>Created</dt><dd>{esc(c['created_at'])}</dd><dt>Launched</dt><dd>{esc(c['launched_at'] or '—')}</dd>
 <dt>Completed</dt><dd>{esc(c['completed_at'] or '—')}</dd><dt>Notes</dt><dd>{esc(c['notes'] or '—')}</dd></dl></div>"""
    return page_admin(c['name'], body, "/campaigns", admin, crumb="Campaigns › " + c['name'])


def _campaign_departments(targets) -> list:
    groups = {}
    for t in targets:
        groups.setdefault(t["department"], []).append(t)
    out = []
    for dept, items in groups.items():
        n = len(items)
        submitted = sum(1 for t in items if t["submitted_at"])
        clicked = sum(1 for t in items if t["clicked_at"])
        reported = sum(1 for t in items if t["reported_at"])
        opened = sum(1 for t in items if t["opened_at"])
        out.append({"department": dept, "sent": n, "submitted": submitted, "clicked": clicked,
                    "reported": reported, "opened": opened,
                    "submit_rate": an.pct(submitted, n), "click_rate": an.pct(clicked, n),
                    "report_rate": an.pct(reported, n)})
    return sorted(out, key=lambda d: (-d["submit_rate"], -d["click_rate"]))


def _timeline(targets, limit: int = 12) -> str:
    events = []
    for t in targets:
        for key, label, color in [("opened_at", "opened", "#2563eb"), ("clicked_at", "clicked the link", "#d97706"),
                                  ("submitted_at", "submitted credentials", "#dc2626"),
                                  ("reported_at", "reported to IT", "#059669")]:
            if t[key]:
                events.append((t[key], t["name"], label, color))
    events.sort(reverse=True)
    rows = ""
    for when, who, label, color in events[:limit]:
        rows += (f'<div style="display:flex;gap:10px;padding:9px 0;border-bottom:1px solid var(--line2)">'
                 f'<span style="width:8px;height:8px;border-radius:50%;background:{color};margin-top:7px;flex:none"></span>'
                 f'<div><div style="font-size:13px"><b>{esc(who)}</b> {esc(label)}</div>'
                 f'<div class=tiny>{esc(when)}</div></div></div>')
    return rows


# -------------------------------------------------------------------- templates
def templates_view(conn, admin: dict) -> str:
    stats = {t["id"]: t for t in an.template_stats(conn)}
    cards = ""
    for t in conn.execute("SELECT * FROM templates ORDER BY difficulty DESC, id").fetchall():
        s = stats.get(t["id"], {})
        flags = [f for f in (t["flags"] or "").split("||") if f]
        cards += f"""<div class=card>
 <div class=chead style="margin-bottom:10px"><div><h3 style="font-size:15.5px">{esc(t['name'])}</h3>
  <div class=sub>{esc(t['category'])}</div></div>
  <div style="display:flex;gap:6px">{chip(t['difficulty'], 'warn' if t['difficulty']=='Hard' else 'info' if t['difficulty']=='Medium' else 'ok')}
   {'' if t['active'] else chip('Inactive', 'mute')}</div></div>
 <div style="font-size:13px;color:var(--ink2);margin-bottom:10px"><b>Subject:</b> {esc(t['subject'])}</div>
 <div class=tiny style="margin-bottom:12px">From <span class=mono>{esc(t['sender_email'])}</span></div>
 <div class=strip style="grid-template-columns:repeat(3,1fr);margin-bottom:12px">
  <div><div class=sl>Sent</div><div class=sv>{s.get('sent',0)}</div></div>
  <div><div class=sl>Phished</div><div class=sv style="color:#b11d1d">{s.get('submit_rate',0)}%</div></div>
  <div><div class=sl>Reported</div><div class=sv style="color:#046c50">{s.get('report_rate',0)}%</div></div></div>
 <div class=tiny style="margin-bottom:12px">{len(flags)} teaching point(s) · used in {s.get('sent',0)} deliveries</div>
 <div class=toolbar style="margin:0">
  <a class="btn btn-s btn-xs" href="/templates/{t['id']}">Edit</a>
  {_btn(f"/templates/{t['id']}/duplicate", "Duplicate", admin['csrf'])}
  {_btn(f"/templates/{t['id']}/delete", "Delete", admin['csrf'], cls="btn btn-s btn-xs", confirm="Delete this lure?")}
  <a class="btn btn-s btn-xs" href="/templates/{t['id']}/preview">Preview</a>
 </div></div>"""
    body = f"""
<div class=hero><div><div class=eyebrow>Lure library</div><h1>Phishing templates</h1>
 <p>Each lure records a sender, a body, a credential form and the red flags taught after a
 submission. Difficulty controls how subtle the tells are, not whether the mail is safe.</p></div>
 <a class="btn btn-p" href="/templates/new">＋ New lure</a></div>
<div class="grid g3">{cards}</div>"""
    return page_admin("Lures", body, "/templates", admin)


def template_form_view(conn, admin: dict, template=None) -> str:
    t = dict(template) if template else {
        "name": "", "category": "Credential theft", "difficulty": "Medium", "subject": "",
        "sender_name": "", "sender_email": "", "brand": "", "cta": "Open Link", "tagline": "",
        "body": "<p>Dear employee,</p><p>Write the lure here.</p>", "landing":
        '<input name="username" placeholder="Email address" required>\n<input name="password" type="password" placeholder="Password" required>',
        "flags": "Sender domain does not match the real service\nArtificial urgency\nUnexpected request for credentials",
    }
    editing = bool(template)
    flag_text = "\n".join(f for f in (t["flags"] or "").split("||") if f)
    sel = lambda v: " selected" if t["difficulty"] == v else ""
    body = f"""
<div class=hero><div><div class=eyebrow>{'Edit lure' if editing else 'New lure'}</div>
 <h1>{esc(t['name']) if editing else 'Create a phishing lure'}</h1>
 <p>Body and landing form accept HTML because the simulated mail is rendered exactly as a
 recipient would see it. Everything is escaped on output except these deliberate fragments.</p></div>
 <a class="btn btn-s" href="/templates">← Back to library</a></div>
<form method=post action="{'/templates/' + str(t['id']) if editing else '/templates'}">
 <input type=hidden name=csrf value="{esc(admin['csrf'])}">
 <div class="grid g2">
  <div class=card><div class=chead><div><h3>Message</h3></div></div>
   <div class=row><div class=field><label>Name</label><input name=name value="{esc(t['name'])}" required></div>
    <div class=field><label>Category</label><input name=category value="{esc(t['category'])}"></div></div>
   <div class=row><div class=field><label>Difficulty</label><select name=difficulty>
     <option{sel('Easy')}>Easy</option><option{sel('Medium')}>Medium</option><option{sel('Hard')}>Hard</option></select></div>
    <div class=field><label>Brand shown on landing page</label><input name=brand value="{esc(t['brand'])}"></div></div>
   <div class=field><label>Subject line</label><input name=subject value="{esc(t['subject'])}" required></div>
   <div class=row><div class=field><label>Sender name</label><input name=sender_name value="{esc(t['sender_name'])}"></div>
    <div class=field><label>Sender email</label><input name=sender_email value="{esc(t['sender_email'])}"></div></div>
   <div class=field><label>Email body (HTML)</label><textarea name=body rows=12>{esc(t['body'])}</textarea></div>
  </div>
  <div class=card><div class=chead><div><h3>Landing page &amp; teaching</h3></div></div>
   <div class=row><div class=field><label>Call-to-action label</label><input name=cta value="{esc(t['cta'])}"></div>
    <div class=field><label>Landing tagline</label><input name=tagline value="{esc(t['tagline'])}"></div></div>
   <div class=field><label>Credential form (HTML)</label><textarea name=landing rows=6>{esc(t['landing'])}</textarea></div>
   <div class=field><label>Red flags — one per line</label><textarea name=flags rows=7>{esc(flag_text)}</textarea>
    <div class=hint>Shown on the coaching page immediately after a simulated submission.</div></div>
   <button class="btn btn-p">Save lure</button>
   <a class="btn btn-s" href="/templates">Cancel</a>
  </div>
 </div>
</form>"""
    return page_admin("Edit lure" if editing else "New lure", body, "/templates", admin)


def template_preview_view(conn, admin: dict, template_id: int) -> str:
    t = conn.execute("SELECT * FROM templates WHERE id=?", (template_id,)).fetchone()
    if not t:
        return page_admin("Not found", empty_state("✕", "Lure not found", ""), "/templates", admin)
    flags = [f for f in (t["flags"] or "").split("||") if f]
    mail = _render_mail(t, "preview-token", preview=True)
    body = f"""
<div class=hero><div><div class=eyebrow>Preview</div><h1>{esc(t['name'])}</h1>
 <p>This is exactly what the recipient sees, minus live tracking. Difficulty: {esc(t['difficulty'])}.</p></div>
 <div style="display:flex;gap:8px"><a class="btn btn-s" href="/templates/{t['id']}">Edit</a>
  <a class="btn btn-s" href="/templates">← Library</a></div></div>
{mail}
<div class=card style="max-width:800px;margin:18px auto"><div class=chead><div><h3>Teaching points released after submission</h3></div></div>
 <ol style="margin:0;padding-left:20px;font-size:13.5px;line-height:1.8">{''.join(f'<li>{f}</li>' for f in flags)}</ol></div>"""
    return page_admin("Preview", body, "/templates", admin)


# ----------------------------------------------------------------------- people
def people_view(conn, admin: dict, *, q: str = "", dept: str = "") -> str:
    risks = {r["id"]: r for r in an.employee_risk(conn)}
    sql = "SELECT * FROM employees WHERE 1=1"
    params = []
    if q:
        sql += " AND (name LIKE ? OR email LIKE ?)"
        params += [f"%{q}%", f"%{q}%"]
    if dept:
        sql += " AND department=?"
        params.append(dept)
    sql += " ORDER BY name"
    employees = conn.execute(sql, params).fetchall()
    departments = [r["department"] for r in conn.execute(
        "SELECT DISTINCT department FROM employees ORDER BY department").fetchall()]

    rows = ""
    for e in employees:
        r = risks.get(e["id"], {})
        consent = chip("Consent recorded", "ok") if e["consent"] else chip("No consent", "warn")
        rows += f"""<tr><td><div class=who>{avatar(e['name'], e['department'])}
 <div><div class=n>{esc(e['name'])}</div><div class=e>{esc(e['email'])}</div></div></div></td>
 <td>{chip(e['department'], 'mute')}<div class=tiny>{esc(e['designation'])}</div></td>
 <td class=num>{r.get('sent', 0)}</td><td class=num>{r.get('submitted', 0)}</td>
 <td>{risk_bar(r.get('risk', 0), r.get('band', 'Low'))}</td>
 <td>{risk_badge(r.get('band', 'Low'))}</td>
 <td>{consent}</td>
 <td style="white-space:nowrap">
  {_btn(f"/people/{e['id']}/consent", "Toggle consent", admin['csrf']) if not e['consent'] else ''}
  {_btn(f"/people/{e['id']}/delete", "Delete", admin['csrf'], confirm="Remove this person and all their results?")}
 </td></tr>"""
    if not rows:
        rows = '<tr><td colspan=8>' + empty_state("☺", "No people found", "Adjust the filter or add someone.") + '</td></tr>'

    dept_opts = "".join(f'<option value="{esc(d)}"{" selected" if d == dept else ""}>{esc(d)}</option>' for d in departments)
    risk_counts = {band: sum(1 for r in risks.values() if r["band"] == band)
                   for band in ("Low", "Moderate", "High", "Critical")}

    body = f"""
<div class=hero><div><div class=eyebrow>People</div><h1>Participants</h1>
 <p>The employee directory is fictional. Consent must be recorded before a person can receive a
 simulated lure; deleting a person cascades to their tracking history.</p></div>
 <span class="chip brand">{len(employees)} shown · {len(risks)} active</span></div>
<div class="grid g4" style="margin-bottom:16px">
 {kpi("Low risk", risk_counts['Low'], "score below 25", "✓", "#059669", "#e7f7f1")}
 {kpi("Moderate", risk_counts['Moderate'], "score 25–49", "◐", "#d97706", "#fdf3e4")}
 {kpi("High", risk_counts['High'], "score 50–74", "⚠", "#ea580c", "#ffedd5")}
 {kpi("Critical", risk_counts['Critical'], "score 75+", "⛔", "#dc2626", "#fdecec")}
</div>
<div class=card style="margin-bottom:16px">
 <form method=get action="/people" class=toolbar>
  <input name=q value="{esc(q)}" placeholder="Search name or email" style="max-width:260px">
  <select name=dept style="max-width:180px"><option value="">All departments</option>{dept_opts}</select>
  <button class="btn btn-s btn-xs">Filter</button>
  <a class="btn btn-s btn-xs" href="/people">Clear</a>
  <span class=spacer></span>
  <a class="btn btn-s btn-xs" href="/api/export.csv">Export results</a>
 </form>
 <div class=table-wrap><table><thead><tr><th>Person</th><th>Department</th><th class=num>Lures</th>
  <th class=num>Phished</th><th>Risk score</th><th>Band</th><th>Consent</th><th></th></tr></thead>
  <tbody>{rows}</tbody></table></div></div>
<div class="grid g2">
 <div class=card><div class=chead><div><h3>Add a person</h3></div></div>
  <form method=post action="/people">
   <input type=hidden name=csrf value="{esc(admin['csrf'])}">
   <div class=row><div class=field><label>Full name</label><input name=name required></div>
    <div class=field><label>Email</label><input name=email type=email required></div></div>
   <div class=row><div class=field><label>Department</label><input name=department list=depts required>
     <datalist id=depts>{''.join(f'<option value="{esc(d)}">' for d in departments)}</datalist></div>
    <div class=field><label>Designation</label><input name=designation></div></div>
   <div class=field><label><input type=checkbox name=consent value=1 style="width:auto"> Consent recorded</label></div>
   <button class="btn btn-p">Add person</button></form></div>
 <div class=card><div class=chead><div><h3>Bulk import</h3><div class=sub>Paste CSV: name,email,department,designation</div></div></div>
  <form method=post action="/people/import">
   <input type=hidden name=csrf value="{esc(admin['csrf'])}">
   <div class=field><label>CSV rows</label><textarea name=csv rows=8 placeholder="Rahul Desai,rahul@northstar.example,Operations,Analyst"></textarea></div>
   <button class="btn btn-p">Import</button></form></div>
</div>"""
    return page_admin("People", body, "/people", admin)


# -------------------------------------------------------------------- analytics
def analytics_view(conn, admin: dict) -> str:
    ov = an.overview(conn)
    depts = an.department_stats(conn)
    diffs = an.difficulty_stats(conn, baseline_only=True)
    tpls = an.template_stats(conn)
    risks = an.employee_risk(conn)
    repeat = an.repeat_clickers(conn)
    trend = an.campaign_trend(conn)
    quiz = an.quiz_stats(conn)
    ttc = an.median_time_to_click_hours(conn)

    dept_rows = "".join(
        f'<tr><td><b>{esc(d["department"])}</b></td><td class=num>{d["sent"]}</td>'
        f'<td class=num>{d["open_rate"]}%</td><td class=num>{d["click_rate"]}%</td>'
        f'<td class=num style="color:#b11d1d;font-weight:600">{d["submit_rate"]}%</td>'
        f'<td class=num style="color:#046c50;font-weight:600">{d["report_rate"]}%</td>'
        f'<td>{risk_bar(d["submit_rate"], "Critical" if d["submit_rate"] > 40 else "Moderate" if d["submit_rate"] > 15 else "Low")}</td></tr>'
        for d in depts)

    diff_rows = "".join(
        f'<div class=dp><span class=dp-n>{esc(d["difficulty"])}</span>'
        f'<span class=dp-v>{d["submitted"]}/{d["sent"]} · <b>{d["submit_rate"]}%</b></span>'
        f'<div class=dp-track><div class=dp-fill style="width:{d["submit_rate"]}%;background:'
        f'{"#dc2626" if d["difficulty"] == "Hard" else "#d97706" if d["difficulty"] == "Medium" else "#059669"}"></div></div></div>'
        for d in diffs)

    tpl_rows = "".join(
        f'<tr><td>{esc(t["name"])}</td><td>{chip(t["difficulty"], "mute")}</td>'
        f'<td class=num>{t["sent"]}</td><td class=num>{t["click_rate"]}%</td>'
        f'<td class=num>{t["submit_rate"]}%</td><td class=num>{t["report_rate"]}%</td></tr>'
        for t in tpls)

    risk_rows = "".join(
        f'<tr><td><div class=who>{avatar(r["name"], r["department"])}<div><div class=n>{esc(r["name"])}</div>'
        f'<div class=e>{esc(r["department"])}</div></div></div></td>'
        f'<td class=num>{r["submitted"]}/{r["sent"]}</td><td class=num>{r["click_rate"]}%</td>'
        f'<td class=num>{r["report_rate"]}%</td><td>{risk_bar(r["risk"], r["band"])}</td>'
        f'<td>{risk_badge(r["band"])}</td></tr>' for r in risks[:12])

    repeat_rows = "".join(
        f'<tr><td>{esc(r["name"])}</td><td>{chip(r["department"], "mute")}</td>'
        f'<td class=num>{r["campaigns"]}</td><td class=num>{r["submissions"]}</td>'
        f'<td class=num>{r["reports"]}</td></tr>' for r in repeat) or '<tr><td colspan=5>None — good sign.</td></tr>'

    body = f"""
<div class=hero><div><div class=eyebrow>Analytics</div><h1>What the data says</h1>
 <p>Aggregated across {ov['campaigns']} launched campaigns and {ov['sent']} simulated deliveries.
 Rates use recipients as the denominator so campaigns of different sizes stay comparable.</p></div>
 <a class="btn btn-s" href="/api/export.json">⬇ JSON</a></div>
<div class="grid g4" style="margin-bottom:16px">
 {kpi("Click rate", f'{ov["click_rate"]}%', f'{ov["clicked"]} recipients clicked', "🖱", "#d97706", "#fdf3e4")}
 {kpi("Submission rate", f'{ov["submit_rate"]}%', f'{ov["submitted"]} credentials submitted', "🎯", "#dc2626", "#fdecec")}
 {kpi("Report rate", f'{ov["report_rate"]}%', f'{ov["reported"]} used Report-Phish', "🛡", "#059669", "#e7f7f1")}
 {kpi("Median time to click", f'{ttc if ttc is not None else "—"} h', "from delivery to first click", "◷", "#4f46e5", "#eef0ff")}
</div>
<div class="grid g2" style="margin-bottom:16px">
 <div class=card><div class=chead><div><h3>Department comparison</h3>
  <div class=sub>Small cohorts: read the direction, not the decimal</div></div></div>
  <div class=table-wrap><table><thead><tr><th>Department</th><th class=num>Sent</th><th class=num>Open</th>
   <th class=num>Click</th><th class=num>Phished</th><th class=num>Reported</th><th>Phish rate</th></tr></thead>
   <tbody>{dept_rows}</tbody></table></div></div>
 <div class=card><div class=chead><div><h3>Difficulty ladder</h3>
  <div class=sub>Baseline campaigns only, so training does not confound the comparison</div></div></div>
  {diff_rows}
  <div class="note" style="margin-top:16px"><b>Finding:</b> the harder the lure, the higher the
  submission rate — spoofed brands and authority outperform generic urgency.</div></div>
</div>
<div class="grid g2" style="margin-bottom:16px">
 <div class=card><div class=chead><div><h3>Template performance</h3></div></div>
  <div class=table-wrap><table><thead><tr><th>Lure</th><th>Difficulty</th><th class=num>Sent</th>
   <th class=num>Click</th><th class=num>Phished</th><th class=num>Reported</th></tr></thead><tbody>{tpl_rows}</tbody></table></div></div>
 <div class=card><div class=chead><div><h3>Training effect</h3></div></div>
  <div class=strip style="grid-template-columns:repeat(2,1fr)">
   <div><div class=sl>Pre-training quiz</div><div class=sv>{quiz['pre']['average']}/{len(QUIZ)}</div>
    <div class=tiny>{quiz['pre']['pass_rate']}% pass</div></div>
   <div><div class=sl>Post-training quiz</div><div class=sv style="color:#046c50">{quiz['post']['average']}/{len(QUIZ)}</div>
    <div class=tiny>{quiz['post']['pass_rate']}% pass</div></div></div>
  <div style="margin-top:12px">{sparkline([quiz['pre']['average'], quiz['post']['average']], "#059669")}</div>
  <div class="note ok" style="margin-top:12px"><b>{quiz['post']['average'] - quiz['pre']['average']:+.2f} marks</b>
  between rounds. Combine this with the post-training campaign result on the Report page.</div></div>
</div>
<div class="grid g2">
 <div class=card><div class=chead><div><h3>Risk ranking</h3><div class=sub>Top 12 by composite score</div></div></div>
  <div class=table-wrap><table><thead><tr><th>Person</th><th class=num>Phished</th><th class=num>Click</th>
   <th class=num>Report</th><th>Risk</th><th></th></tr></thead><tbody>{risk_rows}</tbody></table></div></div>
 <div class=card><div class=chead><div><h3>Repeat clickers</h3><div class=sub>Clicked in two or more campaigns</div></div></div>
  <div class=table-wrap><table><thead><tr><th>Person</th><th>Dept</th><th class=num>Campaigns</th>
   <th class=num>Submissions</th><th class=num>Reports</th></tr></thead><tbody>{repeat_rows}</tbody></table></div>
  <div class="note warn" style="margin-top:14px"><b>Coaching target:</b> repeat clickers account for a
  disproportionate share of submissions. A short one-to-one debrief is more effective than another
  company-wide email.</div></div>
</div>"""
    return page_admin("Analytics", body, "/analytics", admin)


# --------------------------------------------------------------------- training
def training_view(conn, admin: dict) -> str:
    quiz = an.quiz_stats(conn)
    rows = "".join(
        f'<tr><td>{esc(a["name"] or "—")}</td><td>{chip(a["department"] or "—", "mute")}</td>'
        f'<td class=num><b>{a["score"]}/{a["total"]}</b></td>'
        f'<td><div class=dp-track style="width:120px"><div class=dp-fill style="width:'
        f'{100 * a["score"] / max(1, a["total"])}%;background:{"#059669" if a["score"] >= 0.75 * a["total"] else "#d97706"}"></div></div></td>'
        f'<td class=num>{esc(a["taken_at"])}</td></tr>'
        for a in quiz["rows"][:40]) or '<tr><td colspan=5>No attempts yet.</td></tr>'

    q_rows = "".join(
        f'<tr><td style="font-size:13px">{esc(q["question"])}</td><td class=num>{q["accuracy"]}%</td>'
        f'<td><div class=dp-track style="width:140px"><div class=dp-fill style="width:{q["accuracy"]}%;background:'
        f'{"#059669" if q["accuracy"] >= 70 else "#d97706" if q["accuracy"] >= 40 else "#dc2626"}"></div></div></td></tr>'
        for q in quiz["per_question"])

    body = f"""
<div class=hero><div><div class=eyebrow>Training</div><h1>Awareness &amp; coaching</h1>
 <p>The quiz is the training instrument: it is scored, stored and compared across rounds. The
 question bank is fixed so scores remain comparable between campaigns.</p></div>
 <a class="btn btn-p" href="/quiz" target="_blank">Open participant quiz ↗</a></div>
<div class="grid g4" style="margin-bottom:16px">
 {kpi("Attempts", quiz['attempts'], "all rounds", "◉", "#4f46e5", "#eef0ff")}
 {kpi("Average score", f"{quiz['average']}/{len(QUIZ)}", f"{quiz['average_pct']}% of marks", "◎", "#2563eb", "#e8f0fe")}
 {kpi("Pass rate", f"{quiz['pass_rate']}%", "75% threshold", "✓", "#059669", "#e7f7f1")}
 {kpi("Pre → post", f"{quiz['pre']['average']} → {quiz['post']['average']}", "same cohort, two rounds", "↗", "#d97706", "#fdf3e4")}
</div>
<div class="grid g2" style="margin-bottom:16px">
 <div class=card><div class=chead><div><h3>Attempts</h3><div class=sub>Most recent 40</div></div></div>
  <div class=table-wrap style="max-height:440px;overflow:auto"><table><thead><tr><th>Person</th><th>Dept</th>
   <th class=num>Score</th><th>Progress</th><th class=num>Taken</th></tr></thead><tbody>{rows}</tbody></table></div></div>
 <div class=card><div class=chead><div><h3>Question difficulty</h3>
  <div class=sub>Accuracy per question across answered attempts</div></div></div>
  <div class=table-wrap><table><thead><tr><th>Question</th><th class=num>Correct</th><th></th></tr></thead>
   <tbody>{q_rows or '<tr><td colspan=3>No per-question data yet.</td></tr>'}</tbody></table></div>
  <div class=note style="margin-top:14px"><b>Teaching priority:</b> the weakest question identifies
  the next micro-learning topic. Re-run the quiz after the debrief and compare.</div></div>
</div>
<div class=card><div class=chead><div><h3>Question bank</h3><div class=sub>{len(QUIZ)} questions · single best answer</div></div></div>
 <ol style="margin:0;padding-left:20px;font-size:13.5px;line-height:1.9">
  {''.join(f"<li>{q[0]} <span class=tiny>— answer: {esc(q[1][q[2]])}</span></li>" for q in QUIZ)}</ol></div>"""
    return page_admin("Training", body, "/training", admin)


# ------------------------------------------------------------------------ audit
def audit_view(conn, admin: dict) -> str:
    rows = conn.execute("SELECT * FROM audit ORDER BY id DESC LIMIT 200").fetchall()
    body_rows = "".join(
        f'<tr><td class=mono>{esc(r["at"])}</td><td>{chip(r["actor"], "mute")}</td>'
        f'<td class=mono>{esc(r["action"])}</td><td>{esc(r["detail"])}</td></tr>' for r in rows)
    body = f"""
<div class=hero><div><div class=eyebrow>System</div><h1>Audit log</h1>
 <p>Every state-changing action is appended here with the actor and timestamp. The log is
 append-only from the application's point of view and is not editable in the UI.</p></div>
 <span class="chip brand">{len(rows)} entries</span></div>
<div class=card><div class=table-wrap><table><thead><tr><th>When</th><th>Actor</th><th>Action</th><th>Detail</th></tr></thead>
 <tbody>{body_rows or '<tr><td colspan=4>No entries.</td></tr>'}</tbody></table></div></div>"""
    return page_admin("Audit log", body, "/audit", admin)


# --------------------------------------------------------------------- settings
def settings_view(conn, admin: dict, *, message: str = "", error: str = "") -> str:
    company = get_setting(conn, "company_name", "NorthStar Technologies")
    domain = get_setting(conn, "company_domain", "northstar.example")
    pass_mark = get_setting(conn, "training_pass_mark", "6")
    notice = f'<div class="note ok" style="margin-bottom:14px">{esc(message)}</div>' if message else ""
    err = f'<div class="note bad" style="margin-bottom:14px">{esc(error)}</div>' if error else ""
    body = f"""
<div class=hero><div><div class=eyebrow>System</div><h1>Settings</h1>
 <p>Organisation metadata, the training pass mark and the administrator password.</p></div></div>
{notice}{err}
<div class="grid g2">
 <div class=card><div class=chead><div><h3>Organisation</h3></div></div>
  <form method=post action="/settings">
   <input type=hidden name=csrf value="{esc(admin['csrf'])}">
   <div class=field><label>Company name</label><input name=company_name value="{esc(company)}"></div>
   <div class=field><label>Email domain</label><input name=company_domain value="{esc(domain)}"></div>
   <div class=field><label>Quiz pass mark</label><input name=training_pass_mark type=number min=1 max=20 value="{esc(pass_mark)}"></div>
   <button class="btn btn-p">Save settings</button></form></div>
 <div class=card><div class=chead><div><h3>Administrator password</h3>
  <div class=sub>PBKDF2-SHA256 · 260,000 iterations · per-account salt</div></div></div>
  <form method=post action="/settings/password">
   <input type=hidden name=csrf value="{esc(admin['csrf'])}">
   <div class=field><label>Current password</label><input name=current type=password required></div>
   <div class=field><label>New password</label><input name=new type=password minlength=8 required>
    <div class=hint>Minimum 8 characters. Use a passphrase, not a reused password.</div></div>
   <div class=field><label>Confirm new password</label><input name=confirm type=password minlength=8 required></div>
   <button class="btn btn-p">Change password</button></form></div>
</div>
<div class=card style="margin-top:16px;border-color:#f7c9c9">
 <div class=chead style="border-bottom-color:#f7c9c9"><div><h3 style="color:#b11d1d">Danger zone</h3>
  <div class=sub>Reset restores the seeded demonstration dataset and deletes all recorded results.</div></div></div>
 <form method=post action="/settings/reset" onsubmit="return confirm('Reset ALL data back to the seeded demo? This cannot be undone.')">
  <input type=hidden name=csrf value="{esc(admin['csrf'])}">
  <button class="btn btn-bad">Reset demonstration data</button></form></div>"""
    return page_admin("Settings", body, "/settings", admin)


# ----------------------------------------------------------------------- report
def report_view(conn, admin: dict) -> str:
    snap = an.results_snapshot(conn)
    ov = snap["overview"]
    camps = snap["campaigns"]
    depts = snap["departments"]
    diffs = snap["difficulties_baseline"]
    quiz = snap["quiz"]
    risks = snap["employees"]
    ttc = snap["median_time_to_click_hours"]

    camp_rows = "".join(
        f'<tr><td>{esc(c["name"])}</td><td>{esc(c["difficulty"])}</td><td class=num>{c["sent"]}</td>'
        f'<td class=num>{c["click_rate"]}%</td><td class=num>{c["submit_rate"]}%</td>'
        f'<td class=num>{c["report_rate"]}%</td></tr>' for c in camps)
    dept_rows = "".join(
        f'<tr><td>{esc(d["department"])}</td><td class=num>{d["sent"]}</td><td class=num>{d["click_rate"]}%</td>'
        f'<td class=num>{d["submit_rate"]}%</td><td class=num>{d["report_rate"]}%</td></tr>' for d in depts)
    diff_rows = "".join(
        f'<tr><td>{esc(d["difficulty"])}</td><td class=num>{d["sent"]}</td>'
        f'<td class=num>{d["submit_rate"]}%</td><td class=num>{d["report_rate"]}%</td></tr>' for d in diffs)
    risk_rows = "".join(
        f'<tr><td>{esc(r["name"])}</td><td>{esc(r["department"])}</td><td class=num>{r["submitted"]}/{r["sent"]}</td>'
        f'<td class=num>{r["risk"]}</td><td>{esc(r["band"])}</td></tr>' for r in risks[:10])

    body = f"""
<div class="toolbar no-print"><div class=tiny>Generated {esc(snap['generated_at'])} from the live database.</div>
 <span class=spacer></span>
 <a class="btn btn-s btn-xs" href="/api/export.json">⬇ JSON snapshot</a>
 <button class="btn btn-p btn-xs" onclick="window.print()">🖨 Print / Save as PDF</button></div>
<div class=report>
 <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:20px">
  <div><h1>Phishing Susceptibility Study</h1>
   <div class=meta>Simulated campaign results and training effectiveness</div>
   <div class=meta>Department of Information Technology · 2026–2027</div></div>
  <div style="text-align:right" class=meta>Generated<br><b>{esc(snap['generated_at'])}</b></div></div>
 <div class=kpis>
  <div class=kpi><div class=k-lbl>Recipients</div><div class=k-val>{ov['sent']}</div></div>
  <div class=kpi><div class=k-lbl>Click rate</div><div class=k-val>{ov['click_rate']}%</div></div>
  <div class=kpi><div class=k-lbl>Submission rate</div><div class=k-val>{ov['submit_rate']}%</div></div>
  <div class=kpi><div class=k-lbl>Reporting rate</div><div class=k-val>{ov['report_rate']}%</div></div>
 </div>
 <h2>1. Campaign results</h2>
 <table><thead><tr><th>Campaign</th><th>Difficulty</th><th>Sent</th><th>Click</th><th>Phished</th><th>Reported</th></tr></thead>
  <tbody>{camp_rows}</tbody></table>
 <h2>2. Susceptibility by department</h2>
 <table><thead><tr><th>Department</th><th>Sent</th><th>Click</th><th>Phished</th><th>Reported</th></tr></thead>
  <tbody>{dept_rows}</tbody></table>
 <h2>3. Difficulty ladder (baseline campaigns)</h2>
 <table><thead><tr><th>Difficulty</th><th>Sent</th><th>Phished</th><th>Reported</th></tr></thead>
  <tbody>{diff_rows}</tbody></table>
 <h2>4. Highest-risk participants</h2>
 <table><thead><tr><th>Participant</th><th>Department</th><th>Phished</th><th>Risk</th><th>Band</th></tr></thead>
  <tbody>{risk_rows}</tbody></table>
 <h2>5. Training effectiveness</h2>
 <p>Pre-training quiz average <b>{quiz['pre']['average']}/{snap['quiz_question_count']}</b>
  ({quiz['pre']['pass_rate']}% pass); post-training average <b>{quiz['post']['average']}/{snap['quiz_question_count']}</b>
  ({quiz['post']['pass_rate']}% pass). Median time from delivery to click: <b>{ttc} hours</b>.</p>
 <h2>6. Key findings</h2>
 <ul>
  <li>Overall submission rate was <b>{ov['submit_rate']}%</b> across {ov['sent']} simulated deliveries.</li>
  <li>Difficulty correlated with risk: the hardest lure produced the highest submission rate in the baseline round.</li>
  <li>The post-training repeat of the same template reduced submissions from
      <b>{next((c['submit_rate'] for c in camps if c['phase'] == 'Baseline' and c['difficulty'] == 'Hard'), 0)}%</b>
      to <b>{next((c['submit_rate'] for c in camps if c['phase'] == 'Post-training'), 0)}%</b>.</li>
  <li>Reporting rose from <b>{next((c['report_rate'] for c in camps if c['phase'] == 'Baseline' and c['difficulty'] == 'Hard'), 0)}%</b>
      to <b>{next((c['report_rate'] for c in camps if c['phase'] == 'Post-training'), 0)}%</b> on the same lure.</li>
  <li>{len(snap['repeat_clickers'])} participants clicked in two or more campaigns and deserve one-to-one coaching.</li>
 </ul>
 <h2>7. Recommendations</h2>
 <ol>
  <li>Keep the Report-Phish channel visible in the mail client and acknowledge every report.</li>
  <li>Run a short debrief for the Critical risk band within 48 hours of a campaign.</li>
  <li>Repeat the same template after training rather than switching lures, so the comparison is valid.</li>
  <li>Enforce MFA and a password manager; both remove the value of a submitted password.</li>
 </ol>
 <div class=meta style="margin-top:24px">All data is synthetic. No real email was sent and no real credential was collected.</div>
</div>"""
    return page_admin("Report", body, "/report", admin)

