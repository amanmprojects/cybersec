"""SQLite schema, connection handling and small query helpers.

The whole application shares one database file (``phishing.db`` by default).
Every query in the codebase uses parameter binding — no SQL is built by string
interpolation of user input.
"""
from __future__ import annotations

import datetime as _dt
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.environ.get("PHISHSTUDY_DB", os.path.join(BASE_DIR, "phishing.db"))

SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS admins(
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  salt TEXT DEFAULT '',
  display_name TEXT DEFAULT '',
  created_at TEXT,
  last_login TEXT
);

CREATE TABLE IF NOT EXISTS sessions(
  token_hash TEXT PRIMARY KEY,
  admin_id INTEGER NOT NULL REFERENCES admins(id) ON DELETE CASCADE,
  csrf TEXT NOT NULL,
  flash TEXT DEFAULT '',
  created_at TEXT NOT NULL,
  expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS employees(
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  department TEXT NOT NULL DEFAULT 'General',
  designation TEXT DEFAULT '',
  active INTEGER NOT NULL DEFAULT 1,
  consent INTEGER NOT NULL DEFAULT 0,
  consent_at TEXT,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS templates(
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT DEFAULT 'Credential theft',
  difficulty TEXT NOT NULL DEFAULT 'Medium',
  subject TEXT NOT NULL,
  sender_name TEXT DEFAULT '',
  sender_email TEXT DEFAULT '',
  brand TEXT DEFAULT '',
  cta TEXT DEFAULT 'Open Link',
  tagline TEXT DEFAULT '',
  body TEXT DEFAULT '',
  landing TEXT DEFAULT '',
  flags TEXT DEFAULT '',
  active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS campaigns(
  id INTEGER PRIMARY KEY,
  name TEXT NOT NULL,
  template_id INTEGER NOT NULL REFERENCES templates(id),
  status TEXT NOT NULL DEFAULT 'Draft',
  phase TEXT NOT NULL DEFAULT 'Baseline',
  audience TEXT DEFAULT 'All departments',
  scheduled_for TEXT,
  created_at TEXT,
  launched_at TEXT,
  completed_at TEXT,
  notes TEXT DEFAULT '',
  created_by TEXT DEFAULT 'admin'
);

CREATE TABLE IF NOT EXISTS targets(
  id INTEGER PRIMARY KEY,
  campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
  employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
  token TEXT UNIQUE NOT NULL,
  sent_at TEXT,
  opened_at TEXT,
  clicked_at TEXT,
  submitted_at TEXT,
  reported_at TEXT,
  submitted_fields TEXT,
  UNIQUE(campaign_id, employee_id)
);

CREATE TABLE IF NOT EXISTS quiz_attempts(
  id INTEGER PRIMARY KEY,
  employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
  campaign_id INTEGER REFERENCES campaigns(id) ON DELETE SET NULL,
  score INTEGER NOT NULL,
  total INTEGER NOT NULL,
  answers TEXT DEFAULT '[]',
  taken_at TEXT
);

CREATE TABLE IF NOT EXISTS audit(
  id INTEGER PRIMARY KEY,
  actor TEXT,
  action TEXT,
  detail TEXT,
  at TEXT
);

CREATE TABLE IF NOT EXISTS settings(
  key TEXT PRIMARY KEY,
  value TEXT
);

CREATE INDEX IF NOT EXISTS idx_targets_campaign ON targets(campaign_id);
CREATE INDEX IF NOT EXISTS idx_targets_employee ON targets(employee_id);
CREATE INDEX IF NOT EXISTS idx_quiz_employee ON quiz_attempts(employee_id);
CREATE INDEX IF NOT EXISTS idx_campaign_status ON campaigns(status);
"""


def now() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def today_offset(days: int) -> str:
    """Date string *days* away from today, keeping a plausible time of day."""
    d = _dt.datetime.now() + _dt.timedelta(days=days)
    return d.replace(hour=9, minute=30, second=0, microsecond=0).strftime("%Y-%m-%d %H:%M")


def connect(path: str | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(path or DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(path: str | None = None, *, seed: bool = True) -> sqlite3.Connection:
    """Create the schema and, on an empty database, load the demo dataset."""
    conn = connect(path)
    conn.executescript(SCHEMA)
    if seed and conn.execute("SELECT COUNT(*) c FROM employees").fetchone()["c"] == 0:
        from .seed import seed_database
        seed_database(conn)
    return conn


def reset_db(path: str | None = None) -> None:
    """Delete and recreate the database (used by the Reset button and tests)."""
    target = path or DB_PATH
    for suffix in ("", "-wal", "-shm"):
        try:
            os.remove(target + suffix)
        except FileNotFoundError:
            pass
    init_db(target, seed=True)


# ------------------------------------------------------------------ audit trail
def audit(conn: sqlite3.Connection, actor: str, action: str, detail: str = "") -> None:
    conn.execute("INSERT INTO audit(actor,action,detail,at) VALUES(?,?,?,?)",
                 (actor or "system", action, detail[:500], now()))


def get_setting(conn: sqlite3.Connection, key: str, default: str = "") -> str:
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row["value"] if row else default


def set_setting(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                 (key, value))
