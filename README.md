# 🎣 PhishStudy — Phishing Susceptibility Study

**BE Honours Major Project · Major Project-1 (Semester VII)**
**Team:** Shetty Vikyath Vishwanath (5) · Mehtar Aman Yasin (6) · Singh Yash Anil (7) · Singh Abhishek Shailesh (8)
**Guide:** Dr. Yogita Shelar · Department of Information Technology, Vidyavardhini's College of Engineering & Technology

PhishStudy is a self-hosted **phishing simulation platform** that measures how susceptible a
workforce is to phishing and helps reduce it. It is a working product, not a mock-up: campaigns
are created and launched, every recipient gets a unique tokenised link, behavioural events are
recorded, and the results feed an analytics workspace, an individual risk score, immediate
coaching and an awareness quiz.

> **Simulation only.** No email is ever sent, no real credential is ever collected or stored, and
> every page carries a *SIMULATION FOR EDUCATION ONLY* banner. The seeded study uses a
> deterministic synthetic organisation (fictional "NorthStar Technologies").

---

## Run it (30 seconds, nothing to install)

```bash
python3 app.py                 # http://127.0.0.1:8000
python3 app.py --port 8080     # different port
python3 app.py reset           # restore the seeded demonstration dataset
python3 app.py report          # print a text summary of the results
python3 app.py export out.json # write the full analytics snapshot
```

Default administrator: **admin / admin123** (change it under *Settings*).

Zero third-party dependencies — Python standard library only (`http.server` + `sqlite3`). Works
offline on any laptop. Tested on Python 3.13/3.14; needs 3.8+.

## The two-minute demo script

1. **Dashboard** (`/`) — KPI cards, delivery funnel, mutually exclusive outcome breakdown,
   campaign trend and the highest-risk employees.
2. **Campaigns** (`/campaigns`) — launch a campaign; every target is materialised and issued a
   unique token.
3. **Participant inbox** (`/inbox`) — open a simulated M365 lure, follow the tokenised link.
4. You land on a look-alike login page; submit anything — the values are **discarded**, only the
   event is stored — and are redirected to a coaching page listing the red flags in that exact
   message.
5. Back to the dashboard and refresh — the click, submission and reporting rates have moved.
6. **Report** a message instead and the reporting rate moves instead (reporting is an independent
   positive behaviour, not a later funnel stage).
7. **Training** (`/training`) — quiz attempts, pre/post scores, pass rate and item-level analysis.
8. **Export** CSV/JSON, print the A4 report, and read the audit log.

## Features

- Campaign lifecycle: draft → scheduled → live → paused → completed → archived, with
  per-campaign funnel and target table.
- Lure catalogue with sender identity, difficulty, category, landing form and coaching flags.
- Event telemetry with four behavioural events (open, click, submit, report), mutually exclusive
  outcome buckets and a single denominator per campaign.
- Analytics: campaign, department, lure, template and longitudinal views, plus a composite
  individual risk score (Low / Moderate / High / Critical).
- Training loop: immediate coaching with the red flags of the received message, an eight-item
  quiz, attempt history and item difficulty analysis.
- Reporting and exports: printable A4 report, per-target CSV, full analytics JSON, audit log.
- Security: PBKDF2-SHA256 (260k iterations) password hashing, hashed session tokens, per-session
  CSRF protection, login throttling, output escaping, security headers and an append-only audit
  log.

## Layout

| Path | Purpose |
|------|---------|
| `app.py` | CLI entry point (`serve`, `reset`, `report`, `export`) |
| `phishstudy/` | The application package (server, security, db, seed, analytics, views, UI) |
| `phishstudy/seed.py` | Deterministic synthetic dataset: 24 employees, 6 departments, 6 lures, 6 campaigns |
| `tests/test_app.py` | 24 automated tests (unit, route, flow and data-integrity) |
| `phishing.db` | SQLite database, created and seeded on first run |
| `docs/` | Report source: chapters, figures, charts and the WordCraft build script |
| `docs/figures/` | Diagrams and result charts used in the report |
| `assets/shots/` | Application screenshots used in the report |
| `Phishing_Susceptibility_Study_Report.docx` / `.pdf` | **The project report** (86 pages) |
| `TEMP_REPORT_FOR_REVIEW.docx` / `.pdf` | Same report, saved for review convenience |
| `Phishing_Susceptibility_PPT.pptx` | Presentation deck |
| `gen_ppt.py` | Regenerates the deck (needs `python-pptx`) |

## Tests

```bash
python3 -m unittest discover -s tests
```

24 tests covering the security module, the analytics definitions, every route, the participant
flows (click, submit, educate, report, quiz) and the data-integrity rules.

## The report

`Phishing_Susceptibility_Study_Report.docx` / `.pdf` is the deliverable: cover, declaration,
abstract, index, list of figures, list of tables, ten chapters, appendices A–C, a plagiarism
record, the literature cited and the acknowledgements.

It is generated with **WordCraft** (the Word-compatible engine) from the two supplied templates
and the chapter sources in `docs/`:

```bash
uv run --with python-docx python docs/wc_build.py
```

The build runs the report through `wordcraft-cli`:

- `docs/report_ch1_3.py`, `docs/report_ch4_6.py`, `docs/report_ch7_10.py` and `docs/wc_back.py`
  hold the prose, tables and captions; `docs/wc_builder.py` turns them into WordCraft commands
  (real Heading 1/2/3 styles, native tables, images, captions).
- `docs/wc_build.py` lays out the front matter and the body, sets the page geometry, the running
  header and the footers, and runs two passes: the first exports the PDF and reads back the page
  every chapter, section, figure and table lands on, the second rewrites the index and the lists
  of figures and tables with those page numbers.

Page setup follows the reference format — A4, 2.54 cm margins on every side, a running header
with the college name and department above a rule, and a centred page number (lower-roman for the
front matter, arabic from Chapter 1). Body text is Times New Roman 12 pt, justified, 1.5 spacing;
chapter headings are 16 pt bold, section headings 14 pt bold; tables use a light-grey header row,
banded rows and horizontal rules only.

The numbers quoted in the report come from `docs/results.json`, which is produced by
`python3 app.py export docs/results.json` against the seeded database. Diagrams and charts are
regenerated with `docs/make_figures.py` and `docs/make_charts.py`.

## Ethics

- No real email is sent; no external network call is made at runtime.
- Submitted values are discarded — only the fact of a submission and the field names are stored.
- The evaluation is a measurement-pipeline testbed on a synthetic cohort, not an empirical
  workforce sample; the report states this explicitly and does not make causal claims.
