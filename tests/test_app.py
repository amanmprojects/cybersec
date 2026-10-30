"""Test suite for PhishStudy.

Run with:  python3 -m unittest discover -s tests -v
"""
from __future__ import annotations

import http.cookiejar
import os
import re
import sys
import tempfile
import threading
import unittest
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phishstudy import analytics as an
from phishstudy.db import connect, init_db
from phishstudy.security import LoginThrottle, hash_password, token_fingerprint, verify_password
from phishstudy.server import make_server


class SecurityTests(unittest.TestCase):
    def test_password_roundtrip(self):
        encoded = hash_password("correct horse battery staple")
        self.assertTrue(verify_password("correct horse battery staple", encoded))
        self.assertFalse(verify_password("wrong", encoded))
        self.assertTrue(encoded.startswith("260000$"))

    def test_hash_is_salted(self):
        self.assertNotEqual(hash_password("same"), hash_password("same"))

    def test_malformed_hash_rejected(self):
        self.assertFalse(verify_password("x", "not-a-hash"))
        self.assertFalse(verify_password("x", ""))

    def test_token_fingerprint_is_stable_and_not_plaintext(self):
        token = "abc123"
        self.assertEqual(token_fingerprint(token), token_fingerprint(token))
        self.assertNotIn(token, token_fingerprint(token))

    def test_throttle_blocks_after_limit(self):
        throttle = LoginThrottle(max_attempts=3, window=60)
        for _ in range(3):
            self.assertEqual(throttle.blocked("ip", "user"), 0)
            throttle.fail("ip", "user")
        self.assertGreater(throttle.blocked("ip", "user"), 0)
        throttle.reset("ip", "user")
        self.assertEqual(throttle.blocked("ip", "user"), 0)


class AnalyticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.tmp.close()
        cls.conn = init_db(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()
        for suffix in ("", "-wal", "-shm"):
            try:
                os.remove(cls.tmp.name + suffix)
            except FileNotFoundError:
                pass

    def test_seed_shape(self):
        self.assertEqual(self.conn.execute("SELECT COUNT(*) c FROM employees").fetchone()["c"], 24)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) c FROM templates").fetchone()["c"], 6)
        self.assertEqual(self.conn.execute("SELECT COUNT(*) c FROM campaigns").fetchone()["c"], 6)

    def test_funnel_is_monotonic(self):
        ov = an.overview(self.conn)
        self.assertGreaterEqual(ov["opened"], ov["clicked"])
        self.assertGreaterEqual(ov["clicked"], ov["submitted"])
        self.assertGreater(ov["sent"], 0)

    def test_rates_are_percentages(self):
        for stats in [an.overview(self.conn)] + an.department_stats(self.conn):
            for key in ("click_rate", "submit_rate", "report_rate", "open_rate"):
                self.assertGreaterEqual(stats[key], 0)
                self.assertLessEqual(stats[key], 100)

    def test_department_totals_match_overview(self):
        depts = an.department_stats(self.conn)
        self.assertEqual(sum(d["sent"] for d in depts), an.overview(self.conn)["sent"])

    def test_baseline_difficulty_is_ordered(self):
        rows = an.difficulty_stats(self.conn, baseline_only=True)
        rates = {r["difficulty"]: r["submit_rate"] for r in rows}
        self.assertLess(rates["Easy"], rates["Medium"])
        self.assertLess(rates["Medium"], rates["Hard"])

    def test_training_reduces_submissions(self):
        camps = {c["phase"]: c for c in an.campaign_trend(self.conn)}
        self.assertLess(camps["Post-training"]["submit_rate"], camps["Baseline"]["submit_rate"])

    def test_risk_scores_are_bounded(self):
        for row in an.employee_risk(self.conn):
            self.assertGreaterEqual(row["risk"], 0)
            self.assertLessEqual(row["risk"], 100)
            self.assertIn(row["band"], ("Low", "Moderate", "High", "Critical"))

    def test_no_submission_without_click(self):
        bad = self.conn.execute(
            "SELECT COUNT(*) c FROM targets WHERE submitted_at IS NOT NULL AND clicked_at IS NULL"
        ).fetchone()["c"]
        self.assertEqual(bad, 0)

    def test_quiz_pre_post_split(self):
        quiz = an.quiz_stats(self.conn)
        self.assertEqual(quiz["attempts"], 48)
        self.assertGreater(quiz["post"]["average"], quiz["pre"]["average"])


class HttpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        cls.tmp.close()
        cls.server = make_server("127.0.0.1", 0, db_path=cls.tmp.name)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        for suffix in ("", "-wal", "-shm"):
            try:
                os.remove(cls.tmp.name + suffix)
            except FileNotFoundError:
                pass

    def setUp(self):
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.jar),
            NoRedirect(),
        )

    def get(self, path):
        return self.opener.open(self.base + path)

    def post(self, path, data):
        encoded = urllib.parse.urlencode(data).encode()
        return self.opener.open(urllib.request.Request(self.base + path, data=encoded))

    def login(self):
        self.post("/login", {"username": "admin", "password": "admin123", "next": "/"})
        page = self.get("/campaigns").read().decode()
        match = re.search(r'name=csrf value="([^"]+)"', page)
        self.assertIsNotNone(match)
        return match.group(1)

    def test_login_required(self):
        response = self.get("/")
        self.assertEqual(response.status, 303)
        self.assertIn("/login", response.headers.get("Location", ""))

    def test_login_and_dashboard(self):
        csrf = self.login()
        self.assertTrue(csrf)
        page = self.get("/").read().decode()
        self.assertIn("Phishing susceptibility overview", page)
        self.assertIn("Submission", page)

    def test_bad_password_is_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.post("/login", {"username": "admin", "password": "nope"})
        self.assertEqual(ctx.exception.code, 401)

    def test_csrf_is_enforced(self):
        self.login()
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.post("/campaigns", {"csrf": "wrong", "name": "x"})
        self.assertEqual(ctx.exception.code, 403)

    def test_campaign_creation(self):
        csrf = self.login()
        response = self.post("/campaigns", {
            "csrf": csrf, "name": "Test Campaign", "template_id": "1",
            "audience": "All departments", "phase": "Baseline",
        })
        self.assertEqual(response.status, 303)
        page = self.get("/campaigns").read().decode()
        self.assertIn("Test Campaign", page)

    def test_participant_flow_records_events_without_values(self):
        conn = connect(self.tmp.name)
        token = conn.execute("SELECT token FROM targets LIMIT 1").fetchone()["token"]
        conn.close()
        self.assertEqual(self.get(f"/t/{token}").status, 200)
        self.assertEqual(self.get(f"/t/{token}/landing").status, 200)
        response = self.post(f"/t/{token}/submit", {"username": "secret@example.com", "password": "hunter2"})
        self.assertEqual(response.status, 303)
        conn = connect(self.tmp.name)
        row = conn.execute("SELECT * FROM targets WHERE token=?", (token,)).fetchone()
        conn.close()
        self.assertIsNotNone(row["submitted_at"])
        self.assertIsNotNone(row["clicked_at"])
        self.assertIn("username", row["submitted_fields"])
        self.assertNotIn("hunter2", row["submitted_fields"])
        self.assertNotIn("secret@example.com", row["submitted_fields"])

    def test_reporting_flow(self):
        conn = connect(self.tmp.name)
        token = conn.execute("SELECT token FROM targets LIMIT 1 OFFSET 1").fetchone()["token"]
        conn.close()
        response = self.post(f"/t/{token}/report", {})
        self.assertEqual(response.status, 303)
        conn = connect(self.tmp.name)
        row = conn.execute("SELECT reported_at FROM targets WHERE token=?", (token,)).fetchone()
        conn.close()
        self.assertIsNotNone(row["reported_at"])

    def test_csv_export(self):
        self.login()
        response = self.get("/api/export.csv")
        body = response.read().decode()
        self.assertTrue(body.startswith("campaign,phase,difficulty"))
        self.assertIn("northstar.example", body)

    def test_json_export_has_no_plaintext_passwords(self):
        self.login()
        body = self.get("/api/export.json").read().decode()
        self.assertNotIn("admin123", body)
        self.assertIn("overview", body)

    def test_quiz_scores_and_stores_attempt(self):
        data = {"email": "aarav.sharma@northstar.example"}
        for i in range(8):
            data[f"q{i}"] = "1"
        response = self.post("/quiz", data)
        self.assertEqual(response.status, 200)
        self.assertIn("Answer review", response.read().decode())
        conn = connect(self.tmp.name)
        count = conn.execute("SELECT COUNT(*) c FROM quiz_attempts").fetchone()["c"]
        conn.close()
        self.assertGreater(count, 48)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    """Return the redirect response instead of following it (like allow_redirects=False)."""

    def _passthrough(self, req, fp, code, msg, headers):
        return fp

    http_error_301 = _passthrough
    http_error_302 = _passthrough
    http_error_303 = _passthrough
    http_error_307 = _passthrough
    http_error_308 = _passthrough


if __name__ == "__main__":
    unittest.main(verbosity=2)
