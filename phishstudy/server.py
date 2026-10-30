"""HTTP routing, authentication and request handling.

A deliberately small WSGI-free server built on :mod:`http.server`. The routing
table is explicit so the whole application is easy to follow during a viva.
"""
from __future__ import annotations

import csv
import datetime as _dt
import html
import io
import json
import re
import secrets
import traceback
import urllib.parse
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from . import analytics as an
from . import views_admin as va
from . import views_participant as vp
from .db import (audit, connect, get_setting, init_db, now, reset_db, set_setting)
from .security import (LoginThrottle, hash_password, new_token, token_fingerprint,
                       verify_password, SESSION_TTL_SECONDS)
from .seed import QUIZ

HOST = "127.0.0.1"
PORT = 8000
COOKIE = "phish_session"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

PUBLIC_GET = ("/login", "/inbox", "/t/", "/legit/", "/quiz", "/favicon.ico")
PUBLIC_POST = ("/login", "/quiz")

THROTTLE = LoginThrottle()


class Handler(BaseHTTPRequestHandler):
    server_version = "PhishStudy/2.0"
    protocol_version = "HTTP/1.1"

    # -------------------------------------------------------------- utilities
    def log_message(self, fmt, *args):  # quiet by default
        if getattr(self.server, "verbose", False):
            super().log_message(fmt, *args)

    def _conn(self):
        return connect(getattr(self.server, "db_path", None))

    def _send(self, body: str | bytes, *, code: int = 200, ctype: str = "text/html; charset=utf-8",
              headers: list[tuple[str, str]] | None = None) -> None:
        data = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; style-src 'self' 'unsafe-inline'; "
                         "img-src 'self' data:; script-src 'self' 'unsafe-inline'; "
                         "form-action 'self'; frame-ancestors 'none'; base-uri 'none'")
        for key, value in headers or []:
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError):
                pass

    def _redirect(self, location: str, *, flash: str = "", kind: str = "ok") -> None:
        if flash:
            self._set_session_flash(flash, kind)
        self.send_response(303)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _error(self, code: int, message: str) -> None:
        body = (f"<!doctype html><html><head><title>{code}</title><style>body{{font-family:system-ui;"
                f"padding:60px;background:#f4f6fb}}main{{max-width:560px;margin:auto;background:#fff;"
                f"padding:32px;border-radius:14px;border:1px solid #e6eaf2}}</style></head><body><main>"
                f"<h1 style='margin:0 0 8px'>{code}</h1><p style='color:#48566b'>{html.escape(message)}</p>"
                f"<a href='/'>&larr; Back to dashboard</a></main></body></html>")
        self._send(body, code=code)

    # ---------------------------------------------------------------- cookies
    def _cookie(self, name: str) -> str:
        raw = self.headers.get("Cookie", "")
        try:
            jar = SimpleCookie(raw)
            return jar[name].value if name in jar else ""
        except Exception:
            return ""

    # --------------------------------------------------------------- sessions
    def _session(self, conn):
        token = self._cookie(COOKIE)
        if not token:
            return None
        row = conn.execute(
            """SELECT s.*, a.username, a.display_name FROM sessions s
               JOIN admins a ON a.id=s.admin_id WHERE s.token_hash=? AND s.expires_at>?""",
            (token_fingerprint(token), _dt.datetime.now().isoformat(timespec="seconds")),
        ).fetchone()
        if not row:
            return None
        return {"id": row["admin_id"], "username": row["username"],
                "display_name": row["display_name"], "csrf": row["csrf"],
                "token": token, "flash": row["flash"] or ""}

    def _set_session_flash(self, message: str, kind: str = "ok") -> None:
        token = self._cookie(COOKIE)
        if not token:
            return
        conn = self._conn()
        try:
            conn.execute("UPDATE sessions SET flash=? WHERE token_hash=?",
                         (f"{kind}|{message}", token_fingerprint(token)))
            conn.commit()
        finally:
            conn.close()

    def _take_flash(self, conn, admin):
        if not admin or not admin.get("flash"):
            return "", "ok"
        kind, _, message = admin["flash"].partition("|")
        conn.execute("UPDATE sessions SET flash='' WHERE token_hash=?", (token_fingerprint(admin["token"]),))
        conn.commit()
        return message, kind if kind in ("ok", "warn", "bad") else "ok"

    def _new_session(self, conn, admin_id: int) -> str:
        token = new_token()
        csrf = secrets.token_urlsafe(24)
        created = _dt.datetime.now()
        expires = created + _dt.timedelta(seconds=SESSION_TTL_SECONDS)
        conn.execute("DELETE FROM sessions WHERE expires_at<=?",
                     (created.isoformat(timespec="seconds"),))
        conn.execute(
            "INSERT INTO sessions(token_hash,admin_id,csrf,flash,created_at,expires_at) VALUES(?,?,?,?,?,?)",
            (token_fingerprint(token), admin_id, csrf, "",
             created.isoformat(timespec="seconds"), expires.isoformat(timespec="seconds")),
        )
        conn.commit()
        return token

    # ------------------------------------------------------------------ forms
    def _body(self) -> dict[str, list[str]]:
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length > 2_000_000:
            return {}
        raw = self.rfile.read(length).decode("utf-8", "replace")
        return urllib.parse.parse_qs(raw, keep_blank_values=True)

    def _client(self) -> str:
        return self.client_address[0] if self.client_address else "?"

    def _csrf_ok(self, admin, form) -> bool:
        given = (form.get("csrf") or [""])[0]
        return bool(admin and given) and secrets.compare_digest(given, admin["csrf"])

    # -------------------------------------------------------------------- GET
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = urllib.parse.parse_qs(parsed.query)
        conn = self._conn()
        try:
            admin = self._session(conn)
            if path == "/favicon.ico":
                return self._send(b"", code=204)
            if path == "/login":
                if admin:
                    return self._redirect("/")
                return self._send(va.login_view(next_url=(query.get("next") or ["/"])[0]))

            protected = not path.startswith(PUBLIC_GET)
            if protected and not admin:
                return self._redirect("/login?next=" + urllib.parse.quote(self.path))

            if path == "/":
                flash, kind = self._take_flash(conn, admin)
                return self._send(_with_flash(va.dashboard_view(conn, admin), flash, kind))
            if path == "/campaigns":
                flash, kind = self._take_flash(conn, admin)
                return self._send(_with_flash(va.campaigns_view(conn, admin), flash, kind))
            m = re.fullmatch(r"/campaigns/(\d+)", path)
            if m:
                flash, kind = self._take_flash(conn, admin)
                return self._send(_with_flash(va.campaign_detail_view(conn, admin, int(m.group(1))), flash, kind))
            if path == "/templates":
                flash, kind = self._take_flash(conn, admin)
                return self._send(_with_flash(va.templates_view(conn, admin), flash, kind))
            if path == "/templates/new":
                return self._send(va.template_form_view(conn, admin))
            m = re.fullmatch(r"/templates/(\d+)/preview", path)
            if m:
                return self._send(va.template_preview_view(conn, admin, int(m.group(1))))
            m = re.fullmatch(r"/templates/(\d+)", path)
            if m:
                template = conn.execute("SELECT * FROM templates WHERE id=?", (int(m.group(1)),)).fetchone()
                if not template:
                    return self._error(404, "That lure does not exist.")
                return self._send(va.template_form_view(conn, admin, template))
            if path == "/people":
                flash, kind = self._take_flash(conn, admin)
                body = va.people_view(conn, admin, q=(query.get("q") or [""])[0],
                                      dept=(query.get("dept") or [""])[0])
                return self._send(_with_flash(body, flash, kind))
            if path == "/analytics":
                return self._send(va.analytics_view(conn, admin))
            if path == "/training":
                return self._send(va.training_view(conn, admin))
            if path == "/audit":
                return self._send(va.audit_view(conn, admin))
            if path == "/settings":
                flash, kind = self._take_flash(conn, admin)
                return self._send(va.settings_view(conn, admin, message=flash if kind == "ok" else "",
                                                   error=flash if kind != "ok" else ""))
            if path == "/report":
                return self._send(va.report_view(conn, admin))
            if path == "/api/export.csv":
                return self._export_csv(conn)
            if path == "/api/export.json":
                return self._export_json(conn)

            # ------------------------------------------------ participant views
            if path == "/inbox":
                return self._send(vp.inbox_view(conn, (query.get("email") or [""])[0]))
            m = re.fullmatch(r"/legit/(\d+)", path)
            if m:
                return self._send(vp.legit_view(int(m.group(1)), (query.get("email") or [""])[0]))
            m = re.fullmatch(r"/t/([A-Za-z0-9_-]+)", path)
            if m:
                return self._send(vp.mail_view(conn, m.group(1)))
            m = re.fullmatch(r"/t/([A-Za-z0-9_-]+)/landing", path)
            if m:
                return self._send(vp.landing_view(conn, m.group(1)))
            m = re.fullmatch(r"/t/([A-Za-z0-9_-]+)/educate", path)
            if m:
                return self._send(vp.submitted_view(conn, m.group(1)))
            m = re.fullmatch(r"/t/([A-Za-z0-9_-]+)/reported", path)
            if m:
                return self._send(vp.reported_view(conn, m.group(1)))
            if path == "/quiz":
                return self._send(vp.quiz_view(conn, (query.get("email") or [""])[0]))

            return self._error(404, "The page you asked for does not exist.")
        except Exception:
            traceback.print_exc()
            return self._error(500, "Something went wrong while rendering this page.")
        finally:
            conn.close()

    # ------------------------------------------------------------------- POST
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = urllib.parse.parse_qs(parsed.query)
        form = self._body()
        conn = self._conn()
        try:
            admin = self._session(conn)
            if path == "/login":
                return self._login(conn, form)

            # Public participant actions (tokenised links / quiz)
            m = re.fullmatch(r"/t/([A-Za-z0-9_-]+)/(submit|report)", path)
            if m:
                token, action = m.group(1), m.group(2)
                if action == "submit":
                    return self._participant_submit(conn, token, form)
                return self._participant_report(conn, token)
            if path == "/quiz":
                return self._quiz_submit(conn, form)

            if not admin:
                return self._redirect("/login")
            if not self._csrf_ok(admin, form):
                return self._error(403, "CSRF token missing or invalid. Reload the page and try again.")

            if path == "/logout":
                conn.execute("DELETE FROM sessions WHERE token_hash=?", (token_fingerprint(admin["token"]),))
                audit(conn, admin["username"], "auth.logout", "Session ended")
                conn.commit()
                self.send_response(303)
                self.send_header("Location", "/login")
                self.send_header("Set-Cookie", f"{COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax")
                self.send_header("Content-Length", "0")
                self.end_headers()
                return

            if path == "/campaigns":
                return self._campaign_create(conn, admin, form)
            m = re.fullmatch(r"/campaigns/(\d+)/(launch|pause|resume|complete|archive|delete)", path)
            if m:
                return self._campaign_action(conn, admin, int(m.group(1)), m.group(2))

            if path == "/templates":
                return self._template_save(conn, admin, form, None)
            m = re.fullmatch(r"/templates/(\d+)/duplicate", path)
            if m:
                return self._template_duplicate(conn, admin, int(m.group(1)))
            m = re.fullmatch(r"/templates/(\d+)/delete", path)
            if m:
                return self._template_delete(conn, admin, int(m.group(1)))
            m = re.fullmatch(r"/templates/(\d+)", path)
            if m:
                return self._template_save(conn, admin, form, int(m.group(1)))

            if path == "/people":
                return self._person_add(conn, admin, form)
            if path == "/people/import":
                return self._people_import(conn, admin, form)
            m = re.fullmatch(r"/people/(\d+)/(delete|consent)", path)
            if m:
                return self._person_action(conn, admin, int(m.group(1)), m.group(2))

            if path == "/settings":
                return self._settings_save(conn, admin, form)
            if path == "/settings/password":
                return self._password_change(conn, admin, form)
            if path == "/settings/reset":
                return self._settings_reset(conn, admin)

            return self._error(404, "Unknown action.")
        except Exception:
            traceback.print_exc()
            return self._error(500, "The action could not be completed.")
        finally:
            conn.close()

    # ------------------------------------------------------------------ login
    def _login(self, conn, form):
        username = (form.get("username") or [""])[0].strip()
        password = (form.get("password") or [""])[0]
        next_url = (form.get("next") or ["/"])[0]
        if not next_url.startswith("/") or next_url.startswith("//"):
            next_url = "/"

        wait = THROTTLE.blocked(self._client(), username)
        if wait:
            audit(conn, username or "unknown", "auth.throttled", f"Blocked for {wait}s")
            conn.commit()
            return self._send(va.login_view(error=f"Too many attempts. Try again in {wait} seconds.",
                                            next_url=next_url), code=429)

        row = conn.execute("SELECT * FROM admins WHERE username=?", (username,)).fetchone()
        if not row or not verify_password(password, row["password_hash"]):
            THROTTLE.fail(self._client(), username)
            audit(conn, username or "unknown", "auth.login_failed", "Invalid credentials")
            conn.commit()
            return self._send(va.login_view(error="Incorrect username or password.",
                                            next_url=next_url), code=401)

        THROTTLE.reset(self._client(), username)
        token = self._new_session(conn, row["id"])
        conn.execute("UPDATE admins SET last_login=? WHERE id=?", (now(), row["id"]))
        audit(conn, username, "auth.login", "Signed in")
        conn.commit()
        self.send_response(303)
        self.send_header("Location", next_url)
        self.send_header("Set-Cookie",
                         f"{COOKIE}={token}; Path=/; Max-Age={SESSION_TTL_SECONDS}; HttpOnly; SameSite=Lax")
        self.send_header("Content-Length", "0")
        self.end_headers()

    # -------------------------------------------------------------- campaigns
    def _audience(self, conn, form) -> tuple[str, list]:
        marker = (form.get("audience") or ["All departments"])[0]
        departments = [d for d in (form.get("departments") or []) if d]
        if marker in ("__dept__", "__selected__") and departments:
            placeholders = ",".join("?" for _ in departments)
            rows = conn.execute(
                f"SELECT * FROM employees WHERE active=1 AND department IN ({placeholders}) ORDER BY name",
                departments).fetchall()
            label = ", ".join(departments) if len(departments) <= 3 else f"{len(departments)} departments"
            return label, rows
        rows = conn.execute("SELECT * FROM employees WHERE active=1 ORDER BY name").fetchall()
        return "All departments", rows

    def _campaign_create(self, conn, admin, form):
        name = (form.get("name") or [""])[0].strip()[:120]
        try:
            template_id = int((form.get("template_id") or ["0"])[0])
        except ValueError:
            template_id = 0
        phase = (form.get("phase") or ["Baseline"])[0]
        notes = (form.get("notes") or [""])[0].strip()[:300]
        scheduled = (form.get("scheduled_for") or [""])[0].strip()
        template = conn.execute("SELECT * FROM templates WHERE id=?", (template_id,)).fetchone()
        if not name or not template:
            return self._redirect("/campaigns", flash="Give the campaign a name and choose a lure.", kind="bad")

        label, recipients = self._audience(conn, form)
        if not recipients:
            return self._redirect("/campaigns", flash="That audience has no active participants.", kind="bad")
        without_consent = [e["name"] for e in recipients if not e["consent"]]
        if without_consent:
            return self._redirect(
                "/campaigns",
                flash=f"Consent is missing for {len(without_consent)} participant(s). Record consent first.",
                kind="bad")

        status = "Scheduled" if scheduled else "Active"
        launched = None if scheduled else now()
        cur = conn.execute(
            """INSERT INTO campaigns(name,template_id,status,phase,audience,scheduled_for,created_at,
               launched_at,notes,created_by) VALUES(?,?,?,?,?,?,?,?,?,?)""",
            (name, template_id, status, phase if phase in ("Baseline", "Post-training", "Live", "Planned") else "Baseline",
             label, scheduled or None, now(), launched, notes, admin["username"]))
        campaign_id = cur.lastrowid
        sent = None if scheduled else now()
        for employee in recipients:
            conn.execute(
                "INSERT INTO targets(campaign_id,employee_id,token,sent_at) VALUES(?,?,?,?)",
                (campaign_id, employee["id"], secrets.token_urlsafe(9), sent))
        audit(conn, admin["username"], "campaign.create",
              f"{name} → {len(recipients)} recipients ({status})")
        conn.commit()
        return self._redirect(f"/campaigns/{campaign_id}",
                              flash=f"Campaign created for {len(recipients)} participant(s).")

    def _campaign_action(self, conn, admin, campaign_id: int, action: str):
        c = conn.execute("SELECT * FROM campaigns WHERE id=?", (campaign_id,)).fetchone()
        if not c:
            return self._redirect("/campaigns", flash="Campaign not found.", kind="bad")
        if action == "delete":
            conn.execute("DELETE FROM campaigns WHERE id=?", (campaign_id,))
            audit(conn, admin["username"], "campaign.delete", c["name"])
            conn.commit()
            return self._redirect("/campaigns", flash="Campaign deleted.")
        if action == "launch":
            if c["status"] not in ("Draft", "Scheduled"):
                return self._redirect(f"/campaigns/{campaign_id}", flash="Only draft or scheduled campaigns can be launched.", kind="warn")
            rows = conn.execute("SELECT COUNT(*) c FROM targets WHERE campaign_id=?", (campaign_id,)).fetchone()["c"]
            if not rows:
                recipients = conn.execute("SELECT id FROM employees WHERE active=1 AND consent=1").fetchall()
                for e in recipients:
                    conn.execute("INSERT INTO targets(campaign_id,employee_id,token,sent_at) VALUES(?,?,?,?)",
                                 (campaign_id, e["id"], secrets.token_urlsafe(9), now()))
            else:
                conn.execute("UPDATE targets SET sent_at=? WHERE campaign_id=? AND sent_at IS NULL",
                             (now(), campaign_id))
            conn.execute("UPDATE campaigns SET status='Active',launched_at=? WHERE id=?", (now(), campaign_id))
            audit(conn, admin["username"], "campaign.launch", c["name"])
            conn.commit()
            return self._redirect(f"/campaigns/{campaign_id}", flash="Campaign launched.")
        new_status = {"pause": "Paused", "resume": "Active", "complete": "Completed",
                      "archive": "Archived"}.get(action)
        if not new_status:
            return self._error(400, "Unknown campaign action.")
        completed = now() if new_status == "Completed" else c["completed_at"]
        conn.execute("UPDATE campaigns SET status=?,completed_at=? WHERE id=?",
                     (new_status, completed, campaign_id))
        audit(conn, admin["username"], f"campaign.{action}", c["name"])
        conn.commit()
        return self._redirect(f"/campaigns/{campaign_id}", flash=f"Campaign marked {new_status}.")

    # -------------------------------------------------------------- templates
    def _template_fields(self, form):
        fields = {}
        for key in ("name", "category", "difficulty", "subject", "sender_name", "sender_email",
                    "brand", "cta", "tagline", "body", "landing"):
            fields[key] = (form.get(key) or [""])[0].strip()
        flags = [line.strip() for line in (form.get("flags") or [""])[0].splitlines() if line.strip()]
        fields["flags"] = "||".join(flags)
        fields["difficulty"] = fields["difficulty"] if fields["difficulty"] in ("Easy", "Medium", "Hard") else "Medium"
        return fields

    def _template_save(self, conn, admin, form, template_id):
        f = self._template_fields(form)
        if not f["name"] or not f["subject"]:
            return self._redirect("/templates", flash="A lure needs a name and a subject line.", kind="bad")
        if template_id:
            conn.execute(
                """UPDATE templates SET name=?,category=?,difficulty=?,subject=?,sender_name=?,sender_email=?,
                   brand=?,cta=?,tagline=?,body=?,landing=?,flags=? WHERE id=?""",
                (f["name"], f["category"], f["difficulty"], f["subject"], f["sender_name"], f["sender_email"],
                 f["brand"], f["cta"], f["tagline"], f["body"], f["landing"], f["flags"], template_id))
            audit(conn, admin["username"], "template.update", f["name"])
            target = f"/templates/{template_id}"
        else:
            cur = conn.execute(
                """INSERT INTO templates(name,category,difficulty,subject,sender_name,sender_email,
                   brand,cta,tagline,body,landing,flags,active,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,1,?)""",
                (f["name"], f["category"], f["difficulty"], f["subject"], f["sender_name"], f["sender_email"],
                 f["brand"], f["cta"], f["tagline"], f["body"], f["landing"], f["flags"], now()))
            target = f"/templates/{cur.lastrowid}"
            audit(conn, admin["username"], "template.create", f["name"])
        conn.commit()
        return self._redirect(target, flash="Lure saved.")

    def _template_duplicate(self, conn, admin, template_id):
        t = conn.execute("SELECT * FROM templates WHERE id=?", (template_id,)).fetchone()
        if not t:
            return self._redirect("/templates", flash="Lure not found.", kind="bad")
        cur = conn.execute(
            """INSERT INTO templates(name,category,difficulty,subject,sender_name,sender_email,brand,cta,
               tagline,body,landing,flags,active,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,1,?)""",
            (t["name"] + " (copy)", t["category"], t["difficulty"], t["subject"], t["sender_name"],
             t["sender_email"], t["brand"], t["cta"], t["tagline"], t["body"], t["landing"], t["flags"], now()))
        audit(conn, admin["username"], "template.duplicate", t["name"])
        conn.commit()
        return self._redirect(f"/templates/{cur.lastrowid}", flash="Lure duplicated.")

    def _template_delete(self, conn, admin, template_id):
        t = conn.execute("SELECT * FROM templates WHERE id=?", (template_id,)).fetchone()
        if not t:
            return self._redirect("/templates", flash="Lure not found.", kind="bad")
        used = conn.execute("SELECT COUNT(*) c FROM campaigns WHERE template_id=?", (template_id,)).fetchone()["c"]
        if used:
            conn.execute("UPDATE templates SET active=0 WHERE id=?", (template_id,))
            audit(conn, admin["username"], "template.deactivate", t["name"])
            conn.commit()
            return self._redirect("/templates", flash=f"Lure deactivated — it is used by {used} campaign(s).", kind="warn")
        conn.execute("DELETE FROM templates WHERE id=?", (template_id,))
        audit(conn, admin["username"], "template.delete", t["name"])
        conn.commit()
        return self._redirect("/templates", flash="Lure deleted.")

    # ----------------------------------------------------------------- people
    def _person_add(self, conn, admin, form):
        name = (form.get("name") or [""])[0].strip()[:80]
        email = (form.get("email") or [""])[0].strip().lower()[:120]
        department = (form.get("department") or [""])[0].strip()[:40] or "General"
        designation = (form.get("designation") or [""])[0].strip()[:80]
        consent = 1 if (form.get("consent") or [""])[0] else 0
        if not name or not EMAIL_RE.match(email):
            return self._redirect("/people", flash="Enter a name and a valid email address.", kind="bad")
        try:
            conn.execute(
                "INSERT INTO employees(name,email,department,designation,active,consent,consent_at,created_at)"
                " VALUES(?,?,?,?,1,?,?,?)",
                (name, email, department, designation, consent, now() if consent else None, now()))
        except Exception:
            conn.rollback()
            return self._redirect("/people", flash="That email address already exists.", kind="warn")
        audit(conn, admin["username"], "person.add", f"{name} <{email}>")
        conn.commit()
        return self._redirect("/people", flash=f"{name} added.")

    def _people_import(self, conn, admin, form):
        raw = (form.get("csv") or [""])[0]
        added = updated = skipped = 0
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.lower().startswith("name,"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 3:
                skipped += 1
                continue
            name, email, department = parts[0][:80], parts[1].lower()[:120], parts[2][:40] or "General"
            designation = parts[3][:80] if len(parts) > 3 else ""
            if not name or not EMAIL_RE.match(email):
                skipped += 1
                continue
            existing = conn.execute("SELECT id FROM employees WHERE email=?", (email,)).fetchone()
            if existing:
                conn.execute("UPDATE employees SET name=?,department=?,designation=?,active=1 WHERE id=?",
                             (name, department, designation, existing["id"]))
                updated += 1
            else:
                conn.execute(
                    "INSERT INTO employees(name,email,department,designation,active,consent,created_at)"
                    " VALUES(?,?,?,?,1,0,?)", (name, email, department, designation, now()))
                added += 1
        audit(conn, admin["username"], "person.import", f"{added} added, {updated} updated, {skipped} skipped")
        conn.commit()
        return self._redirect("/people", flash=f"Import complete: {added} added, {updated} updated, {skipped} skipped. "
                                               f"New people start without consent.")

    def _person_action(self, conn, admin, employee_id, action):
        e = conn.execute("SELECT * FROM employees WHERE id=?", (employee_id,)).fetchone()
        if not e:
            return self._redirect("/people", flash="Person not found.", kind="bad")
        if action == "delete":
            conn.execute("DELETE FROM employees WHERE id=?", (employee_id,))
            audit(conn, admin["username"], "person.delete", e["email"])
            conn.commit()
            return self._redirect("/people", flash=f"{e['name']} removed.")
        if action == "consent":
            if e["consent"]:
                conn.execute("UPDATE employees SET consent=0,consent_at=NULL WHERE id=?", (employee_id,))
                message = f"Consent withdrawn for {e['name']}."
            else:
                conn.execute("UPDATE employees SET consent=1,consent_at=? WHERE id=?", (now(), employee_id))
                message = f"Consent recorded for {e['name']}."
            audit(conn, admin["username"], "person.consent", e["email"])
            conn.commit()
            return self._redirect("/people", flash=message)

    # --------------------------------------------------------------- settings
    def _settings_save(self, conn, admin, form):
        company = (form.get("company_name") or [""])[0].strip()[:80]
        domain = (form.get("company_domain") or [""])[0].strip()[:80]
        pass_mark = (form.get("training_pass_mark") or ["6"])[0].strip()
        if not pass_mark.isdigit() or not 1 <= int(pass_mark) <= len(QUIZ):
            return self._redirect("/settings", flash=f"Pass mark must be between 1 and {len(QUIZ)}.", kind="bad")
        set_setting(conn, "company_name", company)
        set_setting(conn, "company_domain", domain)
        set_setting(conn, "training_pass_mark", pass_mark)
        audit(conn, admin["username"], "settings.update", f"{company} / {domain} / pass {pass_mark}")
        conn.commit()
        return self._redirect("/settings", flash="Settings saved.")

    def _password_change(self, conn, admin, form):
        current = (form.get("current") or [""])[0]
        new = (form.get("new") or [""])[0]
        confirm = (form.get("confirm") or [""])[0]
        row = conn.execute("SELECT * FROM admins WHERE id=?", (admin["id"],)).fetchone()
        if not row or not verify_password(current, row["password_hash"]):
            return self._redirect("/settings", flash="The current password is incorrect.", kind="bad")
        if len(new) < 8:
            return self._redirect("/settings", flash="The new password must be at least 8 characters.", kind="bad")
        if new != confirm:
            return self._redirect("/settings", flash="The new passwords do not match.", kind="bad")
        conn.execute("UPDATE admins SET password_hash=? WHERE id=?", (hash_password(new), admin["id"]))
        conn.execute("DELETE FROM sessions WHERE admin_id=?", (admin["id"],))
        audit(conn, admin["username"], "auth.password_change", "Password updated; other sessions revoked")
        conn.commit()
        return self._redirect("/login", flash="Password changed. Please sign in again.")

    def _settings_reset(self, conn, admin):
        conn.close()
        reset_db(getattr(self.server, "db_path", None))
        fresh = connect(getattr(self.server, "db_path", None))
        audit(fresh, admin["username"], "settings.reset", "Demo data reset")
        fresh.close()
        self.send_response(303)
        self.send_header("Location", "/login")
        self.send_header("Set-Cookie", f"{COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax")
        self.send_header("Content-Length", "0")
        self.end_headers()

    # -------------------------------------------------------------- participant
    def _participant_submit(self, conn, token, form):
        row = conn.execute("SELECT * FROM targets WHERE token=?", (token,)).fetchone()
        if not row:
            return self._error(404, "This simulated link is not valid.")
        # Deliberately store only the field NAMES. Values are discarded unread.
        fields = json.dumps(sorted(k for k in form if k not in ("csrf",)))[:300]
        stamp = now()
        conn.execute(
            "UPDATE targets SET submitted_at=COALESCE(submitted_at,?), submitted_fields=?,"
            " clicked_at=COALESCE(clicked_at,?), opened_at=COALESCE(opened_at,?) WHERE token=?",
            (stamp, fields, stamp, stamp, token))
        audit(conn, "participant", "sim.submit", f"token {token[:6]}… submitted (values discarded)")
        conn.commit()
        return self._redirect(f"/t/{token}/educate")

    def _participant_report(self, conn, token):
        row = conn.execute("SELECT * FROM targets WHERE token=?", (token,)).fetchone()
        if not row:
            return self._error(404, "This simulated link is not valid.")
        conn.execute("UPDATE targets SET reported_at=COALESCE(reported_at,?),"
                     " opened_at=COALESCE(opened_at,?) WHERE token=?", (now(), now(), token))
        audit(conn, "participant", "sim.report", f"token {token[:6]}… reported to IT")
        conn.commit()
        return self._redirect(f"/t/{token}/reported")

    def _quiz_submit(self, conn, form):
        email = (form.get("email") or [""])[0].strip().lower()
        employee = conn.execute("SELECT * FROM employees WHERE email=?", (email,)).fetchone()
        if not employee:
            return self._error(400, "Choose a participant before submitting the quiz.")
        answers, score = [], 0
        for i, (_prompt, _options, correct) in enumerate(QUIZ):
            try:
                given = int((form.get(f"q{i}") or ["-1"])[0])
            except ValueError:
                given = -1
            answers.append(given)
            if given == correct:
                score += 1
        conn.execute(
            "INSERT INTO quiz_attempts(employee_id,campaign_id,score,total,answers,taken_at) VALUES(?,?,?,?,?,?)",
            (employee["id"], None, score, len(QUIZ), json.dumps(answers), now()))
        audit(conn, "participant", "training.quiz", f"{email} scored {score}/{len(QUIZ)}")
        conn.commit()
        return self._send(vp.quiz_result_view(conn, email=email, score=score, answers=answers))

    # ------------------------------------------------------------------ export
    def _export_csv(self, conn):
        rows = conn.execute(
            """SELECT c.name campaign, c.phase, t.difficulty, e.name, e.email, e.department,
                      tg.sent_at, tg.opened_at, tg.clicked_at, tg.submitted_at, tg.reported_at
               FROM targets tg JOIN campaigns c ON c.id=tg.campaign_id
               JOIN templates t ON t.id=c.template_id JOIN employees e ON e.id=tg.employee_id
               ORDER BY c.id, e.name""").fetchall()
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["campaign", "phase", "difficulty", "participant", "email", "department",
                         "sent_at", "opened_at", "clicked_at", "submitted_at", "reported_at", "outcome"])
        for r in rows:
            writer.writerow([r["campaign"], r["phase"], r["difficulty"], r["name"], r["email"],
                             r["department"], r["sent_at"] or "", r["opened_at"] or "", r["clicked_at"] or "",
                             r["submitted_at"] or "", r["reported_at"] or "", an.outcome_of(r)])
        self._send(buffer.getvalue(), ctype="text/csv; charset=utf-8",
                   headers=[("Content-Disposition", 'attachment; filename="phishstudy-results.csv"')])

    def _export_json(self, conn):
        payload = json.dumps(an.results_snapshot(conn), indent=2)
        self._send(payload, ctype="application/json; charset=utf-8",
                   headers=[("Content-Disposition", 'attachment; filename="phishstudy-results.json"')])


def _with_flash(page: str, message: str, kind: str = "ok") -> str:
    if not message:
        return page
    banner = f'<div class="note {html.escape(kind)}" style="margin-bottom:16px">{html.escape(message)}</div>'
    marker = '<div class="wrap '
    idx = page.find(marker)
    if idx == -1:
        return page
    end = page.find(">", idx) + 1
    return page[:end] + banner + page[end:]


def make_server(host: str = HOST, port: int = PORT, *, db_path: str | None = None,
                verbose: bool = False) -> ThreadingHTTPServer:
    init_db(db_path)
    server = ThreadingHTTPServer((host, port), Handler)
    server.db_path = db_path
    server.verbose = verbose
    return server


def run(host: str = HOST, port: int = PORT, *, db_path: str | None = None, verbose: bool = False) -> None:
    server = make_server(host, port, db_path=db_path, verbose=verbose)
    company = get_setting(connect(db_path), "company_name", "NorthStar Technologies")
    print(f"PhishStudy 2.0 — {company}")
    print(f"Admin console : http://{host}:{port}/login   (admin / admin123)")
    print(f"Participant   : http://{host}:{port}/inbox")
    print("Simulation only — no real email is ever sent. Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
