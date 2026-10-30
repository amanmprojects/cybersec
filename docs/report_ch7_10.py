"""Chapters 7-10 of the report."""
from __future__ import annotations

import json
import os

from report_common import ReportBuilder

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RES = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
SHOTS = os.path.join(ROOT, "assets", "shots")


def _pct(v):
    return f"{v:.1f}"


def chapter7(B: ReportBuilder):
    B.chapter(7, "Implementation")

    B.lead(
        "This chapter describes the implemented system. It explains the technology choices, the "
        "package structure, the security architecture, the campaign engine, the tracking and "
        "analytics pipeline, the training module, the reporting functions and the principal "
        "screens. The emphasis is on the decisions that a reader would need to reproduce or extend "
        "the work, not on a line-by-line description of the code."
    )

    B.section("7.1", "Technology Stack")
    B.p(
        "PhishStudy is implemented in Python 3.14 using only the standard library at runtime. The "
        "HTTP server is built on `ThreadingHTTPServer`, with a custom request handler that performs "
        "routing, session resolution, CSRF validation, content negotiation and error handling. "
        "SQLite provides persistence through the `sqlite3` module. Password hashing uses "
        "`hashlib.pbkdf2_hmac`; session and CSRF tokens use `secrets`; constant-time comparison uses "
        "`hmac.compare_digest`. CSV export uses `csv`, JSON export uses `json`, and HTML escaping "
        "uses `html.escape`."
    )
    B.p(
        "The front end is server-rendered HTML with a single hand-written CSS design system. There "
        "is no React, Vue, Bootstrap or Tailwind, and no external font or icon request. A small "
        "amount of vanilla JavaScript handles confirmation dialogs and the mobile navigation "
        "toggle. This choice keeps the page weight low, makes the participant experience work on a "
        "slow connection, and removes the supply-chain risk of a front-end dependency tree. The "
        "trade-off is that the interface is less interactive than a single-page application; for a "
        "measurement tool, clarity and reliability matter more than animation."
    )
    B.p(
        "The development tooling is separate from the runtime. Figures are generated with "
        "matplotlib and Pillow, the report with python-docx and docxcompose, screen captures with "
        "Chromium via the WebDriver protocol, and PDF conversion with LibreOffice. None of these "
        "tools is required to run the application. This separation is important: the deployed "
        "artefact is a single Python package and a SQLite file, not a data-science environment."
    )

    B.section("7.2", "Package Structure")
    B.p(
        "The codebase is approximately 3,700 lines, including tests and the report generator. Table "
        "7.1 lists the principal modules and their responsibilities. The split follows the layers in "
        "Chapter 3: security, persistence, domain logic, views and transport."
    )
    B.table("7.1", "Package structure and responsibilities",
            ["Path", "Responsibility", "Lines"],
            [
                ["app.py", "Command-line entry point: serve, reset, report, export", "83"],
                ["phishstudy/security.py", "PBKDF2 hashing, session fingerprints, login throttle", "99"],
                ["phishstudy/db.py", "Schema, connection policy, reset and seed orchestration", "179"],
                ["phishstudy/seed.py", "Synthetic population, lures, campaigns, quiz, outcome model", "380"],
                ["phishstudy/analytics.py", "Funnel, departments, difficulty, risk, quiz, snapshot", "359"],
                ["phishstudy/ui.py", "Design system, admin shell, public layout, components", "517"],
                ["phishstudy/views_admin.py", "Login, dashboard, campaigns, lures, people, analytics, training, report", "794"],
                ["phishstudy/views_participant.py", "Inbox, mail, landing, coaching, report, quiz", "294"],
                ["phishstudy/server.py", "HTTP routing, auth, CSRF, exports, security headers", "747"],
                ["tests/test_app.py", "24 unit, analytics and HTTP tests", "262"],
            ],
            widths=[5.4, 8.8, 1.4], font=8.4, align=["l", "l", "c"])
    B.p(
        "The separation is not purely cosmetic. The analytics module has no dependency on the HTTP "
        "layer, so it can be tested with an in-memory or temporary database and reused by the CLI "
        "and the report builder. The views receive a database connection and return strings; they do "
        "not perform authentication or routing. The server owns the security boundary. This makes "
        "it possible to reason about authorisation in one place rather than in every view."
    )

    B.section("7.3", "Security Implementation")
    B.p(
        "The administrative console is the most sensitive part of the system: a compromised session "
        "can launch campaigns, read behavioural data and export records. The controls in Table 7.2 "
        "were implemented and tested. They follow the OWASP Top 10 and the ASVS verification "
        f"categories at a level appropriate to a single-process teaching application {B.cite('owasp2021', 'owaspasvs')}."
    )
    B.table("7.2", "Security controls implemented in the platform",
            ["Control", "Implementation", "Purpose"],
            [
                ["Password storage", "PBKDF2-HMAC-SHA256, 260,000 iterations, 16-byte random salt, constant-time compare", "Resist offline cracking and timing attacks"],
                ["Session token", "32 random bytes, URL-safe; SHA-256 hash stored in the database", "A database leak cannot be replayed"],
                ["Session cookie", "HttpOnly, SameSite=Lax, 8-hour max-age, path=/", "Limit script access and cross-site sending"],
                ["CSRF", "Per-session token in every state-changing form; server-side comparison", "Block cross-site forged requests"],
                ["Login throttle", "8 failures per 15 minutes per client/username; in-process sliding window", "Slow credential guessing"],
                ["SQL access", "Parameterised queries throughout; no string interpolation of user input", "Prevent SQL injection"],
                ["Output encoding", "html.escape on every dynamic value; CSP with frame-ancestors none", "Prevent XSS and clickjacking"],
                ["Security headers", "CSP, X-Frame-Options DENY, nosniff, Referrer-Policy no-referrer", "Reduce browser attack surface"],
                ["Audit log", "Actor, action, detail, timestamp for auth, campaign and export events", "Support accountability and review"],
                ["Tokenised links", "Random per-recipient token; unknown tokens return a neutral 404", "Prevent enumeration of participants"],
            ],
            widths=[3.2, 8.2, 4.2], font=8.4, align=["l", "l", "l"], bold_first=True)
    B.p(
        "Two limitations are stated explicitly. First, the cookie does not set the `Secure` flag "
        "because the demonstration runs over plain HTTP on localhost; a production deployment behind "
        "TLS must enable it. Second, the login throttle is in-process, so it resets when the server "
        "restarts and does not coordinate across multiple workers. A production deployment would "
        "move the throttle to SQLite or Redis. These are deployment hardening items, not defects in "
        "the present single-process design."
    )

    B.section("7.4", "Campaign Engine")
    B.p(
        "The campaign engine implements the lifecycle described in Chapter 3. Creating a campaign "
        "validates the lure, name, phase and audience, and stores the record in Draft. Launching "
        "materialises one target per recipient, generates a token of the form `s< campaign>-< employee>-< random>` "
        "and writes the launch timestamp. The token is random enough to be unguessable in the "
        "demonstration, but it is not a secret in the cryptographic sense; it is an opaque identifier "
        "that grants access to one simulated message. A production system would use a longer random "
        "value and a signed expiry."
    )
    B.p(
        "The engine enforces the state machine in the service layer. A campaign cannot be launched "
        "twice, a completed campaign cannot be resumed, and a paused campaign retains its existing "
        "tokens. Every transition writes an audit entry with the actor and the previous/new state. "
        "The audience is resolved at launch, not at creation, so that a change to the employee list "
        "cannot silently alter the denominator of a campaign that is already running. This is a "
        "small example of the measurement discipline that runs through the system."
    )
    B.p(
        "The participant routes are idempotent. Opening a message twice does not change the first "
        "open timestamp; clicking twice does not create a second click; reporting after clicking "
        "records both events. The submission handler sets the click timestamp if it is missing, "
        "because a direct POST to the landing endpoint is still evidence that the participant "
        "reached the page. This rule fixed a non-monotonic funnel defect found during testing and is "
        "covered by an automated test."
    )

    B.section("7.5", "Tracking and Analytics")
    B.p(
        "Tracking uses a one-pixel image for opens and a redirect for clicks. The pixel endpoint "
        "returns a transparent GIF and records the open only if the target exists. The click "
        "endpoint records the click and redirects to the landing page. The submission endpoint "
        "reads the field names from the form, discards the values, stores the names and redirects to "
        "coaching. The report endpoint records the report and redirects to a confirmation page. All "
        "timestamps use the server's local time in `YYYY-MM-DD HH:MM` format, which is sufficient "
        "for a single-site deployment but would need time-zone normalisation in a multi-region one."
    )
    B.p(
        "Analytics is implemented as a set of SQL aggregations followed by Python formatting. The "
        "funnel counts distinct targets with each timestamp, so a target is counted once per stage. "
        "The outcome breakdown uses mutually exclusive buckets (submitted, clicked only, opened "
        "only, reported, no response) so that the donut sums to the delivered total. Department, "
        "difficulty and template statistics use the same summary function, which guarantees that "
        "the denominators and rates are consistent across views. The risk function is the only "
        "place where an individual-level score is computed, and it is reused by the dashboard, the "
        "people page and the report."
    )
    B.p(
        "The analytics module returns plain dictionaries, not HTML. This makes it testable and "
        "reusable. The CLI `report` command prints a text summary; the `export` command writes the "
        "full snapshot to JSON; the HTTP export endpoints stream CSV and JSON. The report builder "
        "reads the same JSON, so the numbers in this document and the numbers in the application "
        "come from one source."
    )

    B.section("7.6", "Training Module")
    B.p(
        "The training module has three parts: the coaching page, the quiz and the attempt history. "
        "The coaching page is rendered after a submission and includes the original message, the "
        "specific red flags, a short explanation of what a real service would do differently, and a "
        "call to action for the quiz. The quiz is an eight-item multiple-choice form with a name or "
        "email selector, immediate scoring and an answer review. The attempt history is stored in "
        "`quiz_attempts` and summarised on the training page."
    )
    B.p(
        "The quiz does not require an account. A participant selects their name from a list or "
        "enters their email, and the attempt is linked to the employee record. This is a deliberate "
        "usability choice for a simulation: requiring a login would add friction and would make the "
        "training feel like a compliance system rather than a learning moment. The trade-off is that "
        "a participant could submit on behalf of a colleague; in a field deployment the quiz would "
        "be behind the organisation's SSO."
    )

    B.section("7.7", "Reporting and Exports")
    B.p(
        "The platform provides three reporting surfaces. The **printable report** is a server-rendered "
        "page with the overview, campaign table, department table, training results and risk list, "
        "styled for A4 and printable from the browser. The **CSV export** contains one row per "
        "target with campaign, phase, difficulty, employee, department and the four event "
        "timestamps; it is suitable for further analysis in a spreadsheet. The **JSON export** "
        "contains the full analytics snapshot, including the overview, campaign, department, "
        "difficulty, template, employee, repeat-clicker and quiz sections. Both exports require an "
        "administrator session and are recorded in the audit log."
    )
    B.p(
        "The exports contain employee names and email addresses because they are intended for the "
        "administrator who already has access to the people directory. They do not contain "
        "passwords, session tokens, submitted values or quiz answers. A production deployment would "
        "add a data-retention policy and possibly a pseudonymised export option for research use. "
        "The present export is a compromise between utility and minimisation, and it is documented "
        "in Appendix C."
    )

    B.section("7.8", "Principal Screens", page_break=True)
    B.p(
        "The following screens were captured from the running application with the seeded dataset. "
        "They are included to demonstrate that the system is a working product rather than a mock-up. "
        "The simulation banner is visible on every screen, and the navigation is consistent across "
        "the admin console."
    )
    B.figure("7.1", os.path.join(SHOTS, "login.png"),
             "Administrator sign-in. The demo credentials are shown for the laboratory environment; "
             "a production deployment would remove them.", width=14.4)
    B.figure("7.2", os.path.join(SHOTS, "dashboard.png"),
             "Dashboard: KPI cards, funnel, mutually exclusive outcome breakdown, campaign trend and "
             "the highest-risk employees.", width=14.4)
    B.figure("7.3", os.path.join(SHOTS, "campaigns.png"),
             "Campaign list with lifecycle state, recipient count and per-campaign rates.", width=14.4)
    B.figure("7.4", os.path.join(SHOTS, "campaign.png"),
             "Campaign detail for the post-training M365 lure, showing the funnel and the per-target "
             "event table.", width=14.4)
    B.figure("7.5", os.path.join(SHOTS, "templates.png"),
             "Lure catalogue. Each template carries a category, difficulty, sender identity and a "
             "list of red flags used by the coaching page.", width=14.4)
    B.figure("7.6", os.path.join(SHOTS, "people.png"),
             "People directory with department filters, consent state and the composite risk band.",
             width=14.4)
    B.figure("7.7", os.path.join(SHOTS, "analytics.png"),
             "Analytics workspace: department comparison, difficulty breakdown, template performance "
             "and the longitudinal trend.", width=14.4)
    B.figure("7.8", os.path.join(SHOTS, "training.png"),
             "Training dashboard: attempts, mean score, pass rate, pre/post comparison and item-level "
             "difficulty.", width=14.4)
    B.figure("7.9", os.path.join(SHOTS, "inbox.png"),
             "Participant inbox. Legitimate messages and simulated phishing messages share the same "
             "visual language.", width=14.4)
    B.figure("7.10", os.path.join(SHOTS, "mail.png"),
             "Rendered M365 lure. The misspelled sender domain is visible in the message header; the "
             "body uses fear and urgency.", width=14.4)
    B.figure("7.11", os.path.join(SHOTS, "landing.png"),
             "Look-alike landing page. The form is fictional and the submitted values are discarded.",
             width=14.4)
    B.figure("7.12", os.path.join(SHOTS, "educate.png"),
             "Coaching page. The participant sees the red flags in the exact message they received, "
             "followed by a route to the quiz.", width=14.4)

    B.section("7.9", "Implementation Challenges")
    B.p(
        "Several challenges shaped the implementation. **Session handling without a framework** "
        "required a careful separation between the cookie, the server-side session row and the CSRF "
        "secret; the first prototype stored the raw token in the database, which was corrected to a "
        "SHA-256 fingerprint. **Idempotent event tracking** required deciding which timestamp to set "
        "when a participant reached an endpoint out of order; the rule that a submission implies a "
        "click resolved the non-monotonic funnel. **Risk scoring** required a calibration pass: the "
        "first formula penalised reporting so heavily that employees who reported were ranked as "
        "high risk, which is the opposite of the intended behaviour. The negative reporting term was "
        "introduced to correct this. **Donut charts** initially double-counted employees who both "
        "clicked and reported; the outcome buckets were made mutually exclusive."
    )
    B.p(
        "The most time-consuming challenge was not a single feature but the consistency of the "
        "numbers across surfaces. The dashboard, the analytics page, the printable report and the "
        "JSON export each had their own query in the first prototype, and they drifted. The fix was "
        "to centralise every aggregation in `analytics.py` and to have every surface consume the same "
        "snapshot. This is a software-engineering lesson that is easy to state and hard to enforce: "
        "a single source of truth is a design property, not a documentation promise."
    )

    B.section("7.10", "Summary")
    B.p(
        "The implementation delivers a working, dependency-free platform with a hardened admin "
        "console, a campaign engine, idempotent tracking, a central analytics module, an embedded "
        "training loop and exportable reporting. The screens demonstrate the complete flow from lure "
        "authoring to participant coaching. The next chapter reports how the implementation was "
        "tested."
    )


def chapter8(B: ReportBuilder):
    B.chapter(8, "Testing and Validation")

    B.lead(
        "This chapter reports the testing and validation of the platform. It describes the test "
        "strategy, the automated suites, the route and flow checks, the security probes, the data-"
        "integrity checks, the performance measurements, the usability review and the defects found "
        "and fixed. The purpose is to establish that the software is correct with respect to its "
        "specification and that its numbers are internally consistent, not to establish that the "
        "synthetic cohort is representative of a real workforce."
    )

    B.section("8.1", "Test Strategy")
    B.p(
        "Testing followed a four-level pyramid. **Unit tests** exercise pure functions: password "
        "hashing, token fingerprinting, the login throttle and the analytics calculations. "
        "**Integration tests** start the HTTP server on an ephemeral port with a temporary database "
        "and drive real requests through login, campaign creation, participant flows, exports and the "
        "quiz. **Security probes** attempt authentication bypass, CSRF forgery, SQL injection, "
        "cross-site scripting and open redirects. **Data-integrity checks** assert invariants that "
        "must hold for any valid dataset: the funnel is monotonic, a submission implies a click, "
        "department totals reconcile with the overview, and risk scores are bounded. A performance "
        "test measures response times at two dataset sizes, and a heuristic review assesses the "
        "principal screens against Nielsen's ten heuristics."
    )
    B.p(
        "The automated suite is run with `python3 -m unittest discover -s tests`. It uses a temporary "
        "SQLite file per test class, starts the real server in a background thread and makes real "
        "HTTP requests with `urllib`. This is slower than mocking, but it exercises the routing, "
        "session, CSRF and template layers together. The final run completed 24 tests in 1.56 seconds "
        "with no failures or errors."
    )

    B.section("8.2", "Automated Test Suites")
    B.p(
        "Table 8.1 summarises the three test classes and the behaviour they verify. The counts are "
        "the number of test methods, not the number of assertions; several methods assert multiple "
        "properties."
    )
    B.table("8.1", "Automated test suites",
            ["Suite", "Tests", "Focus", "Representative checks"],
            [
                ["SecurityTests", "5", "Cryptographic primitives and throttling", "Password round-trip; salted hashes; malformed hash rejection; token fingerprint stability; throttle lockout"],
                ["AnalyticsTests", "9", "Funnel, rates, departments, risk, quiz", "Seed shape; monotonic funnel; percentage bounds; department reconciliation; risk bounds; quiz split"],
                ["HttpTests", "10", "Routes, auth, CSRF, participant flow, exports", "Auth redirect; login; bad password; CSRF 403; campaign creation; value discard; reporting; CSV; JSON; quiz"],
                ["Total", "24", "—", "All passing in 1.56 s"],
            ],
            widths=[2.7, 1.2, 4.1, 7.6], font=8.4, align=["l", "c", "l", "l"], bold_first=True)
    B.p(
        "The analytics tests deserve particular attention because they protect the credibility of the "
        "report. `test_funnel_is_monotonic` asserts that opened ≥ clicked ≥ submitted for every "
        "campaign summary. `test_no_submission_without_click` asserts the event-order invariant. "
        "`test_department_totals_match_overview` asserts that the sum of department counts equals the "
        "overview counts. `test_rates_are_percentages` asserts that every rate lies between 0 and 100. "
        "`test_risk_scores_are_bounded` asserts that no score escapes the 0–100 range. These are "
        "simple invariants, but each one corresponds to a defect that was found during development."
    )

    B.section("8.3", "Route and Flow Validation")
    B.p(
        "Every administrative and participant route was exercised manually and through the HTTP "
        "suite. The administrative routes return 200 after login and 303 to the login page without a "
        "session. The participant routes return 200 for a valid token and a neutral 404 for an "
        "unknown token. The mutation flows were exercised end to end: create a campaign, launch it, "
        "pause it, resume it, complete it, create a lure, duplicate a lure, add a person, import a "
        "CSV, update settings, change the password, reset the dataset, export CSV and JSON, and print "
        "the report. Each mutation produced a redirect and an audit entry, and the resulting state "
        "was visible on the next page load."
    )
    B.p(
        "The participant flow was exercised with a real token from the seeded database: open the "
        "inbox, open the mail, click the link, submit the form, view the coaching page, report a "
        "second message, and take the quiz. The submission test deliberately entered a real-looking "
        "email and password and then queried the database to confirm that neither value was stored. "
        "Only the field names `username` and `password` were retained. This is the most important "
        "privacy assertion in the suite."
    )

    B.section("8.4", "Security Probes")
    B.p(
        "Table 8.2 records the security probes and their results. The probes were run against the "
        "local server with a temporary database. A probe passes when the system exhibits the "
        "expected defensive behaviour, not when it returns a particular status code for its own "
        "sake."
    )
    B.table("8.2", "Security probes and results",
            ["Probe", "Method", "Observed result", "Status"],
            [
                ["Unauthenticated admin access", "GET / without a session", "303 redirect to /login", "Pass"],
                ["Bad password", "POST /login with a wrong password", "401; generic error; no user enumeration", "Pass"],
                ["CSRF forgery", "POST /campaigns with an invalid token", "403; no state change", "Pass"],
                ["SQL injection", "Username `admin' OR 1=1--` with any password", "401; parameterised query unaffected", "Pass"],
                ["Stored XSS", "Create a person named `<script>alert(1)</script>`", "Rendered as `&lt;script&gt;`; no execution", "Pass"],
                ["Open redirect", "POST /login with `next=//evil.example`", "Redirect to `/`; external target rejected", "Pass"],
                ["Session cookie", "Inspect Set-Cookie after login", "HttpOnly; SameSite=Lax; Max-Age=28800; Path=/", "Pass"],
                ["Security headers", "HEAD /login", "CSP, X-Frame-Options DENY, nosniff, no-referrer", "Pass"],
                ["Login throttle", "Unit test with eight failures", "Ninth attempt blocked for the window", "Pass"],
            ],
            widths=[3.6, 5.2, 5.6, 1.2], font=8.4, align=["l", "l", "l", "c"], bold_first=True)
    B.p(
        "One probe is worth highlighting. The open-redirect test submitted a `next` value of "
        "`//evil.example`, which browsers interpret as a protocol-relative URL. The login handler "
        "accepts only a path that starts with a single `/`, so the value was rejected and the user "
        "was sent to the dashboard. This is a small control, but it prevents a phishing campaign "
        "from using the platform's own login page as a redirector. The stored-XSS probe created a "
        "person record with a script tag in the name and confirmed that the people page rendered it "
        "as text. The probe record was created in a disposable database, not in the report dataset."
    )

    B.section("8.5", "Data Integrity and Reproducibility")
    B.p(
        "The dataset is deterministic. Resetting the database with `python3 app.py reset` produces "
        "the same 24 employees, six lures, six campaigns, 104 delivered targets and 48 quiz attempts. "
        "The event timestamps depend on the date of the reset, but the counts, rates and ranks are "
        "stable. The exported JSON records the generated-at timestamp so that a reader can tell which "
        "run produced a table. The CSV export contains one row per target and can be used to "
        "recompute every rate in Chapter 9."
    )
    B.p(
        "Three integrity checks are enforced in code. Foreign keys are enabled on every connection, "
        "so a target cannot reference a missing campaign or employee. The submission handler sets "
        "the click timestamp if it is missing, so the funnel cannot become non-monotonic. The "
        "analytics summary raises an error if a rate falls outside 0–100, which would indicate a "
        "counting bug. These checks are not a formal proof, but they catch the failure modes that "
        "actually occurred during development."
    )

    B.section("8.6", "Performance")
    B.p(
        "Performance was measured with a single client over loopback, using 40 requests per "
        "administrative route and 60 requests for the public quiz page. The demonstration dataset "
        "has 24 employees and 104 delivered targets. A second dataset was created by adding 1,000 "
        "employees and 4,800 targets to a disposable copy of the database, producing 1,024 employees "
        "and 6,128 targets. The results are shown in Table 8.3."
    )
    B.table("8.3", "Response times at two dataset sizes (milliseconds)",
            ["Route", "Demo median", "Demo p95", "Load median", "Load max"],
            [
                ["Dashboard /", "8.0", "12.9", "106.4", "118.6"],
                ["Analytics", "11.6", "20.9", "154.5", "172.6"],
                ["People", "7.9", "11.3", "73.0", "98.9"],
                ["Campaigns", "3.7", "5.9", "—", "—"],
                ["Training", "5.0", "6.7", "—", "—"],
                ["Audit log", "2.3", "2.7", "—", "—"],
                ["Participant quiz", "4.3", "5.5", "—", "—"],
                ["Login (PBKDF2)", "115.0", "—", "—", "—"],
            ],
            widths=[4.2, 3.0, 3.0, 3.0, 2.4], font=8.6, align=["l", "c", "c", "c", "c"], bold_first=True)
    B.p(
        "At the demonstration scale, every page responds in under 21 ms at the 95th percentile. At "
        "1,024 employees and 6,128 targets, the dashboard and analytics pages remain under 200 ms. "
        "The login time is dominated by the 260,000 PBKDF2 iterations; 115 ms is an acceptable cost "
        "for a password hash that is expensive to attack offline. The analytics page is the slowest "
        "because it performs several aggregations and a per-employee risk query; at 1,024 employees "
        "this is the first place where an N+1 pattern appears. A production deployment would replace "
        "the per-employee loop with a single grouped query, which is the main performance item in the "
        "Semester VIII plan."
    )

    B.section("8.7", "Usability Review")
    B.p(
        "A heuristic review was conducted against Nielsen's ten heuristics rather than a formal "
        "usability test with external participants. The review covered the login, dashboard, "
        "campaign list, campaign detail, lure catalogue, people directory, analytics, training, "
        "participant inbox, mail, landing and coaching screens. The most positive findings were "
        "consistent navigation, visible system status (the simulation banner), clear error messages "
        "and a readable visual hierarchy. The most significant issues were the density of the "
        "analytics page on a small laptop, the lack of inline validation on the campaign form, and "
        "the absence of a bulk-delete action for test campaigns."
    )
    B.p(
        "The density issue was addressed by grouping the analytics into cards and by allowing the "
        "page to scroll rather than compressing the charts. The validation issue was addressed by "
        "relying on HTML5 required fields and server-side checks, which give a clear message but not "
        "an inline hint. The bulk-delete issue was left as a deliberate safety choice: deleting a "
        "campaign is a destructive action, and the single-record delete is sufficient for the "
        "demonstration. A formal usability test with five to eight participants is planned for "
        "Semester VIII."
    )

    B.section("8.8", "Defects Found and Fixed")
    B.p(
        "Testing was valuable because it found real defects. Table 8.4 lists the six defects that "
        "affected behaviour, the symptom, the root cause and the fix. Each fix is covered by a test "
        "or a manual check."
    )
    B.table("8.4", "Defects found during testing and their fixes",
            ["#", "Symptom", "Root cause", "Fix"],
            [
                ["1", "Mail view returned 500", "Missing `_render_mail` import in the participant view", "Imported the helper and added a route test"],
                ["2", "Campaign trend crashed", "`phase` key absent from the trend row", "Added the key to the query and the summary"],
                ["3", "Coaching page crashed", "`employee_email` not passed to the template", "Passed the employee record through the view"],
                ["4", "Reporters ranked as high risk", "Reporting was weighted as a risk factor", "Changed the formula to subtract a reporting term"],
                ["5", "Funnel became non-monotonic", "A submission could be recorded without a click", "Set the click timestamp when a submission arrives"],
                ["6", "Donut totals exceeded the cohort", "Clicked and reported were counted twice", "Introduced mutually exclusive outcome buckets"],
            ],
            widths=[0.8, 4.1, 5.4, 5.3], font=8.4, align=["c", "l", "l", "l"])
    B.p(
        "Defect 5 is a good example of why the analytics invariants matter. A participant who "
        "bookmarked the landing page could submit without a recorded click, which produced a "
        "submission rate above the click rate for that campaign. The immediate fix was to set the "
        "click timestamp on submission; the longer-term fix was the test that asserts the invariant "
        "for every campaign. Defect 6 was a visualisation bug with a substantive consequence: the "
        "dashboard claimed more outcomes than there were recipients, which undermined trust in every "
        "other number. The fix was to define five exclusive buckets and to assert that they sum to "
        "the delivered total."
    )

    B.section("8.9", "Limitations of the Validation")
    B.p(
        "The validation establishes functional correctness, basic security and acceptable "
        "performance at the tested scale. It does not establish usability for a representative "
        "group of administrators, accessibility conformance against WCAG 2.2, resistance to a "
        "determined attacker with network access, or behaviour under concurrent write load. The "
        "security probes are targeted checks, not a penetration test. The performance test uses a "
        "single client and a local connection, so it understates network latency. The usability "
        "review is a heuristic inspection by the developer, which is weaker than an independent "
        "review. These limitations are stated so that the results are not over-read."
    )

    B.section("8.10", "Summary")
    B.p(
        "The platform passes 24 automated tests, the principal routes and mutation flows work, the "
        "security probes produce the expected defensive behaviour, and the analytics satisfy their "
        "invariants. Performance is comfortable at the demonstration scale and remains under 200 ms "
        "at 1,024 employees and 6,128 targets. Six defects were found and fixed, each with a "
        "regression check. The next chapter presents the behavioural results and discusses what they "
        "do and do not show."
    )


def chapter9(B: ReportBuilder):
    B.chapter(9, "Results and Discussions")

    ov = RES["overview"]
    q = RES["quiz"]

    B.lead(
        "This chapter presents the results recorded by the platform and discusses their meaning. It "
        "reports the delivery funnel, campaign outcomes, department and difficulty breakdowns, "
        "repeat behaviour, time-to-event, the composite risk distribution and the training results. "
        "It then discusses the patterns, states the threats to validity and draws the implications "
        "that are supported by a synthetic study. The chapter is explicit about the difference "
        "between a number that the platform measured correctly and a claim that the number supports "
        "about a real workforce."
    )

    B.section("9.1", "Overview")
    B.p(
        f"The seeded programme delivered {ov['sent']} simulated messages across five launched "
        f"campaigns to {ov['employees']} employees. Of these, {ov['opened']} were opened "
        f"({_pct(ov['open_rate'])}%), {ov['clicked']} were clicked ({_pct(ov['click_rate'])}%), "
        f"{ov['submitted']} resulted in a submitted form ({_pct(ov['submit_rate'])}%) and "
        f"{ov['reported']} were reported through the Report-Phish channel ({_pct(ov['report_rate'])}%). "
        "The open rate is high because the generator assumes that most recipients render the "
        "message; the click and submission rates are the more meaningful behavioural signals. "
        "Table 9.1 and Figure 9.1 present the funnel."
    )
    B.table("9.1", "Delivery funnel",
            ["Stage", "Count", "% of delivered"],
            [
                ["Delivered", ov["sent"], "100.0"],
                ["Opened", ov["opened"], _pct(ov["open_rate"])],
                ["Clicked", ov["clicked"], _pct(ov["click_rate"])],
                ["Submitted", ov["submitted"], _pct(ov["submit_rate"])],
                ["Reported (independent behaviour)", ov["reported"], _pct(ov["report_rate"])],
            ],
            widths=[8.0, 3.2, 4.4], font=9.0, align=["l", "c", "c"])
    B.figure("9.1", os.path.join(HERE, "figures", "funnel.png"),
             "Delivery funnel. Reporting is an independent positive behaviour, not a later stage of "
             "the delivery funnel.", width=15.2)
    B.p(
        "The relationship between clicking and submitting is informative. Of the 45 employees who "
        "clicked, 23 submitted a form, a conditional submission rate of 51.1%. This is consistent "
        "with the design of the lures: the landing pages ask for credentials or employee details, and "
        "a participant who has already accepted the premise of the message is likely to complete the "
        "form. The 22 employees who clicked but did not submit either abandoned the page or "
        "recognised the deception at the landing stage. The platform does not record why, which is a "
        "limitation of event-level telemetry."
    )

    B.section("9.2", "Campaign Outcomes")
    B.p(
        "Table 9.2 and Figure 9.2 show the five launched campaigns. The three baseline campaigns "
        "produced submission rates of 20.8%, 29.2% and 33.3%, with reporting rates between 8.3% and "
        "12.5%. The post-training M365 campaign produced a submission rate of 8.3% and a reporting "
        f"rate of 50.0%. The live courier campaign, delivered to eight recipients in Sales and "
        "Operations, produced a 12.5% submission rate and a 12.5% reporting rate."
    )
    B.table("9.2", "Campaign-level outcomes",
            ["Campaign", "Phase", "Sent", "Clicked", "Submitted", "Reported", "Click %", "Submit %", "Report %"],
            [
                [c["name"].replace(" — ", " — "), c["phase"], c["sent"], c["clicked"], c["submitted"],
                 c["reported"], _pct(c["click_rate"]), _pct(c["submit_rate"]), _pct(c["report_rate"])]
                for c in RES["campaigns"]
            ],
            widths=[4.6, 1.7, 1.0, 1.2, 1.3, 1.3, 1.2, 1.2, 1.3], font=7.8,
            align=["l", "l", "c", "c", "c", "c", "c", "c", "c"])
    B.figure("9.2", os.path.join(HERE, "figures", "campaigns.png"),
             "Campaign-level click, submission and reporting rates. The post-training M365 campaign "
             "reverses the baseline pattern.", width=15.2)
    B.p(
        "The most striking comparison is between campaign 3 and campaign 4, which used the same M365 "
        "lure, the same audience and the same difficulty. Clicking fell from 50.0% to 29.2% "
        "(a 20.8 percentage-point reduction), submission fell from 33.3% to 8.3% (a 25.0-point "
        "reduction, or 75% in relative terms), and reporting rose from 8.3% to 50.0% (a 41.7-point "
        "increase, or a six-fold relative increase). This is the pattern that an awareness programme "
        "would hope to see. It is also the pattern that was parameterised into the synthetic cohort: "
        "the post-training targets were set to 28% click, 8% submit and 50% report. The comparison "
        "therefore demonstrates that the platform can detect and display a large behavioural shift "
        "on a like-for-like stimulus; it does not demonstrate that training caused the shift in a "
        "real organisation."
    )

    B.section("9.3", "Department Analysis")
    B.p(
        "Table 9.3 and Figure 9.3 break the results down by department. Sales and Finance are the "
        "most exposed: Sales recorded an 85.0% click rate and a 65.0% submission rate, and Finance "
        "recorded 81.2% and 50.0%. IT recorded no clicks and a 62.5% reporting rate. Legal and "
        "Operations recorded no submissions and moderate reporting rates. HR occupied an "
        "intermediate position with a 37.5% click rate and a 12.5% submission rate."
    )
    B.table("9.3", "Outcomes by department",
            ["Department", "Sent", "Clicked", "Submitted", "Reported", "Click %", "Submit %", "Report %"],
            [
                [d["department"], d["sent"], d["clicked"], d["submitted"], d["reported"],
                 _pct(d["click_rate"]), _pct(d["submit_rate"]), _pct(d["report_rate"])]
                for d in RES["departments"]
            ],
            widths=[2.8, 1.4, 1.6, 1.8, 1.8, 1.8, 1.8, 1.8], font=8.6,
            align=["l", "c", "c", "c", "c", "c", "c", "c"])
    B.figure("9.3", os.path.join(HERE, "figures", "departments.png"),
             "Outcomes by department across all launched campaigns. Sales and Finance combine high "
             "click rates with high submission rates; IT combines zero clicks with high reporting.",
             width=15.2)
    B.p(
        "The department pattern is consistent with the literature on role congruence: employees who "
        "handle external requests, invoices and payment approvals encounter messages that resemble "
        "their normal work, so a convincing lure is less likely to feel anomalous. The Sales result "
        "is also consistent with a culture that rewards speed and responsiveness; a message that "
        "promises a bonus or threatens a lost deal receives attention. IT's zero-click result is "
        "consistent with security training and with the daily experience of inspecting suspicious "
        "mail. The HR result is intermediate, which is plausible because HR staff handle confidential "
        "records but are not primarily responsible for payments or external sales."
    )
    B.p(
        "These interpretations are hypotheses, not findings. The department assignment is correlated "
        "with the latent susceptibility values used by the generator, so the pattern is partly a "
        "property of the seed. The value of the table is that it demonstrates the kind of "
        "department-level view a security manager needs, and it generates testable hypotheses for "
        "the field pilot: are Sales and Finance still the highest-risk groups when real roles and "
        "real workloads are measured? Does IT's advantage persist when the lure is tailored to IT "
        "systems rather than to Microsoft 365?"
    )

    B.section("9.4", "Lure Difficulty")
    B.p(
        "Table 9.4 and Figure 9.4 compare the three baseline campaigns by their difficulty label. "
        "The submission rate rises from 20.8% for the easy password-expiry lure to 29.2% for the "
        "medium festival-bonus lure and 33.3% for the hard M365 alert. The reporting rate moves in "
        "the opposite direction, from 12.5% to 8.3% to 8.3%."
    )
    B.table("9.4", "Baseline outcomes by lure difficulty",
            ["Difficulty", "Lure", "Sent", "Clicked", "Submitted", "Reported", "Submit %", "Report %"],
            [
                [d["difficulty"], ["IT Password Expiry", "HR Festival Bonus", "M365 Security Alert"][i],
                 d["sent"], d["clicked"], d["submitted"], d["reported"],
                 _pct(d["submit_rate"]), _pct(d["report_rate"])]
                for i, d in enumerate(RES["difficulties_baseline"])
            ],
            widths=[2.2, 4.2, 1.3, 1.6, 1.8, 1.8, 1.7, 1.7], font=8.6,
            align=["l", "l", "c", "c", "c", "c", "c", "c"])
    B.figure("9.4", os.path.join(HERE, "figures", "difficulty.png"),
             "Baseline outcomes by lure difficulty. The ordering is counter-intuitive and is explained "
             "by confounding between difficulty, lure and campaign timing.", width=14.6)
    B.p(
        "The ordering is counter-intuitive: the 'hard' lure produced the highest submission rate. "
        "There are three explanations, and none of them supports the conclusion that hard lures are "
        "more dangerous in general. First, difficulty is a designer's label, not a measured property. "
        "The M365 alert is visually polished, uses a familiar brand and a fear appeal, and may be "
        "more credible than a generic password-expiry message that many employees have learned to "
        "recognise. Second, difficulty is perfectly confounded with campaign and time: the easy lure "
        "was the first campaign, the hard lure was the third, and the cohort may have become more "
        "engaged or more fatigued over the period. Third, each cell has only 24 observations, so a "
        "difference of three or four submissions is within the range of random variation. The honest "
        "conclusion is that the difficulty label did not predict behaviour in this cohort, and that a "
        "future study should randomise difficulty within phase and use more than one lure per level."
    )

    B.section("9.5", "Repeat Behaviour and Time-to-Event")
    B.p(
        "Thirteen employees clicked at least two campaigns, and those thirteen account for all 23 "
        "submissions. The concentration is partly a consequence of the generator, which ranks the "
        "same high-susceptibility employees at the top of every campaign, and partly a plausible "
        "feature of real behaviour: a small group of repeat clickers can account for a "
        "disproportionate share of incidents. Table 9.5 lists the eight employees with the highest "
        "click counts. The top two, Divya Rao and Pooja Bhatt, clicked and submitted in every "
        "campaign they received and never reported."
    )
    B.table("9.5", "Employees with the highest repeat-click counts",
            ["Employee", "Department", "Campaigns", "Submissions", "Reports"],
            [
                [e["name"], e["department"], e["campaigns"], e["submissions"], e["reports"]]
                for e in RES["repeat_clickers"][:8]
            ],
            widths=[4.2, 3.0, 3.0, 3.0, 2.4], font=8.8, align=["l", "l", "c", "c", "c"], bold_first=True)
    B.p(
        "The median time from delivery to first click was 6.9 hours, and the median time from click "
        "to submission was 0.85 hours (about 51 minutes). The median time from delivery to report "
        "was 11.15 hours. These figures suggest a pattern in which a click is followed quickly by a "
        "submission, while reporting is slower and more deliberate. The platform records the "
        "timestamps but not the participant's reason, so the interpretation is speculative. A field "
        "study could add a short, optional debrief question to distinguish curiosity, confusion and "
        "deliberate compliance."
    )

    B.section("9.6", "Composite Risk")
    B.p(
        "Table 9.6 and Figure 9.5 show the distribution of the composite risk score. Sixteen "
        "employees are in the low band, two in moderate, three in high and three in critical. The "
        "six employees in the high and critical bands account for 20 of the 23 submissions (87%). "
        "This concentration is the practical justification for a risk score: a small group can be "
        "offered additional support without subjecting the whole organisation to more training."
    )
    B.table("9.6", "Distribution of composite risk bands",
            ["Band", "Employees", "Share", "Interpretation"],
            [
                ["Low", "16", "66.7%", "Resilient; no individual action"],
                ["Moderate", "2", "8.3%", "Occasional clicks; monitor"],
                ["High", "3", "12.5%", "Repeated clicks or submission; coach"],
                ["Critical", "3", "12.5%", "Repeated submissions; immediate support"],
            ],
            widths=[2.6, 2.6, 2.4, 8.0], font=9.0, align=["l", "c", "c", "l"], bold_first=True)
    B.figure("9.5", os.path.join(HERE, "figures", "risk.png"),
             "Distribution of composite risk bands. The score is a triage tool, not a psychometric "
             "measurement.", width=13.0)
    B.p(
        "The risk score should be used carefully. It combines behaviours that are not equally "
        "harmful, it ignores the sensitivity of the account and the presence of technical controls, "
        "and it can label a curious employee as high risk even when no harm occurred. The platform "
        "therefore presents the score alongside the underlying counts (campaigns, clicks, "
        "submissions, reports) and the quiz result, so that an administrator can see why a person "
        "was ranked. The recommended action for the high and critical bands is coaching and "
        "additional support, not discipline. A production deployment should add a review step "
        "before any individual-level action is taken."
    )

    B.section("9.7", "Training Outcomes")
    B.p(
        f"The pre-training quiz mean was {q['pre']['average']:.2f}/8 ({q['pre']['average_pct']:.1f}%) "
        f"with a {q['pre']['pass_rate']:.1f}% pass rate. The post-training mean was "
        f"{q['post']['average']:.2f}/8 ({q['post']['average_pct']:.1f}%) with an "
        f"{q['post']['pass_rate']:.1f}% pass rate. The mean improved by "
        f"{q['post']['average'] - q['pre']['average']:.2f} points, a relative improvement of "
        f"{((q['post']['average'] - q['pre']['average']) / q['pre']['average'] * 100):.0f}%. "
        "Table 9.7 and Figure 9.6 present the result and the item-level breakdown."
    )
    B.table("9.7", "Quiz results before and after training",
            ["Round", "Attempts", "Mean / 8", "Mean %", "Pass rate"],
            [
                ["Pre-training", q["pre"]["attempts"], f"{q['pre']['average']:.2f}", _pct(q["pre"]["average_pct"]), _pct(q["pre"]["pass_rate"])],
                ["Post-training", q["post"]["attempts"], f"{q['post']['average']:.2f}", _pct(q["post"]["average_pct"]), _pct(q["post"]["pass_rate"])],
                ["All attempts", q["attempts"], f"{q['average']:.2f}", _pct(q["average_pct"]), _pct(q["pass_rate"])],
            ],
            widths=[3.6, 2.4, 2.6, 2.6, 2.6], font=9.0, align=["l", "c", "c", "c", "c"])
    B.figure("9.6", os.path.join(HERE, "figures", "quiz.png"),
             "Mean score and item-level accuracy before and after coaching. The post-training round "
             "improves on every item.", width=15.4)
    B.table("9.8", "Item-level accuracy before and after coaching",
            ["Item", "Pre %", "Post %", "Change (pp)"],
            [
                [f"Q{i+1}", _pct(pre["accuracy"]), _pct(post["accuracy"]),
                 f"{post['accuracy'] - pre['accuracy']:+.1f}"]
                for i, (pre, post) in enumerate(zip(q["per_question_pre"], q["per_question_post"]))
            ],
            widths=[2.0, 4.4, 4.4, 4.0], font=9.0, align=["c", "c", "c", "c"])
    B.p(
        "Every item improved. The largest absolute gains were on Q4 (the correct reporting action, "
        "+45.8 points), Q5 (what MFA protects, +62.5 points) and Q1 (the strongest sign of phishing, "
        "+37.5 points). The smallest gain was on Q6 (business email compromise, +12.5 points), which "
        "was already the strongest item before training (54.2%). The weakest post-training items were "
        "Q3 (link inspection, 66.7%) and Q6 and Q8 (both 66.7%). The pattern suggests that "
        "participants learned the reporting routine and the limits of MFA quickly, but that link "
        "inspection and post-incident response need more practice."
    )
    B.p(
        "The improvement cannot be attributed to training alone. The same instrument was used before "
        "and after, so a practice effect is plausible; the post-training round followed the coaching "
        "and was taken shortly afterwards; and there was no control group. The synthetic generator "
        "also parameterised a higher post-training score. The result therefore demonstrates that the "
        "training module can record a large knowledge gain and that the item analysis can identify "
        "specific weaknesses. A field study with a comparison group and a delayed post-test is needed "
        "to estimate the causal effect and its retention."
    )

    B.section("9.8", "Discussion")
    B.p(
        "Four findings emerge from the results, each with a different evidential status. First, the "
        "platform measures the funnel correctly and the numbers reconcile across surfaces; this is a "
        "software-engineering finding supported by the tests and the reconciliation checks. Second, "
        "the synthetic cohort exhibits the expected concentration of risk: a small group of repeat "
        "clickers accounts for most submissions. This is a demonstration of the analytics, and it is "
        "consistent with the literature on repeat clickers, but it is not an empirical estimate of "
        "prevalence. Third, the post-training campaign shows a large improvement on a like-for-like "
        "lure; this is a demonstration that the instrument can capture a behavioural shift, not proof "
        "that the training caused it. Fourth, the department and difficulty patterns generate "
        "hypotheses about role congruence and lure credibility that a field study can test."
    )
    B.p(
        "The practical implication is that a small organisation can run a credible measurement loop "
        "without a commercial platform. The platform produces four artefacts that a security manager "
        "can use: a campaign report, a department heat map, a risk list with underlying counts, and a "
        "training report with item-level weaknesses. The artefacts are only as good as the campaign "
        "design and the honesty of the reporting culture, which is why the recommendations emphasise "
        "blameless feedback and avoid punitive use of individual scores."
    )
    B.p(
        "The theoretical implication is that phishing susceptibility is better treated as a "
        "context-dependent behaviour than as a stable trait. The same employee can click one lure and "
        "report another; the same department can be high risk for a payment lure and low risk for a "
        "password lure. A measurement system should therefore report the interaction between person, "
        "lure and context, not only an organisational average. The platform's data model supports "
        "that analysis at the target level, but the present report aggregates at the department level "
        "to keep the tables readable. The exported CSV allows a finer analysis."
    )

    B.section("9.9", "Threats to Validity")
    B.p(
        "**Internal validity.** The synthetic cohort is generated from explicit prevalence targets and "
        "a latent-susceptibility ranking. The post-training improvement is parameterised, not "
        "discovered. The difficulty comparison is confounded with campaign and time. The quiz "
        "improvement may reflect practice, immediate coaching and the generator. These factors limit "
        "causal inference."
    )
    B.p(
        "**External validity.** The cohort is 24 fictional employees in one fictional organisation, "
        "with hand-tuned susceptibility values and a small set of lures. The results cannot be "
        "generalised to a real workforce, industry or culture. The platform is designed to be "
        "deployed in a real organisation, but the present evaluation does not test that deployment."
    )
    B.p(
        "**Construct validity.** Clicking a link is not the same as being compromised; submitting a "
        "form is not the same as losing an account, because no real credential is captured and no "
        "account is accessed. Reporting a simulated message is not the same as reporting a real one, "
        "although the interface is designed to make the action similar. The metrics are proxies for "
        "risk, not measures of harm."
    )
    B.p(
        "**Statistical validity.** The sample is small, the cells are unbalanced (the live campaign "
        "has eight recipients), and the report does not present confidence intervals for every rate. "
        "A difference of a few percentage points in a cell of 24 should not be over-interpreted. The "
        "field study will use a pre-registered analysis and a power calculation."
    )
    B.p(
        "**Ecological validity.** The participant experience is a web inbox, not the organisation's "
        "real mail client. The visual language is realistic, but the context is not. A field "
        "deployment should use the real client or a faithful replica, and should measure whether the "
        "reporting action is as easy as it is in the simulation."
    )

    B.section("9.10", "Summary")
    B.p(
        "The platform recorded a 43.3% click rate, a 22.1% submission rate and a 19.2% reporting rate "
        "across 104 deliveries. Sales and Finance were the most exposed departments, IT the least. "
        "The post-training M365 campaign reversed the baseline pattern on the same lure, and the quiz "
        "mean rose from 3.25 to 6.21. The results demonstrate that the measurement pipeline works and "
        "that the analytics can produce actionable views. They do not establish causal effects in a "
        "real workforce; that is the task of the field pilot described in Chapter 6."
    )


def chapter10(B: ReportBuilder):
    B.chapter(10, "Conclusions")

    B.lead(
        "This chapter summarises the work, states the conclusions that are supported by the evidence, "
        "lists the contributions and limitations, and sets out the plan for future work. The tone is "
        "deliberately measured: the project delivered a working platform and a defensible synthetic "
        "evaluation, but it did not deliver a field trial, and the conclusions are framed accordingly."
    )

    B.section("10.1", "Summary of Work")
    B.p(
        "The project set out to design, implement and evaluate a simulation-based framework for "
        "measuring and reducing phishing susceptibility. The literature review established that "
        "phishing exploits human judgement, that technical controls leave a residual human decision, "
        "and that embedded, timely feedback is more effective than annual awareness. It also "
        "identified a gap between commercial platforms, which are opaque and costly, and open-source "
        "tools, which deliver campaigns but stop short of training, risk scoring and integrated "
        "reporting."
    )
    B.p(
        "The proposed system addresses that gap. PhishStudy is a dependency-free Python web "
        "application with a hardened admin console, a campaign engine, tokenised participant links, "
        "idempotent event tracking, a central analytics module, a composite risk score, an embedded "
        "coaching and quiz module, CSV/JSON exports and a printable report. The data model has nine "
        "tables and enforces referential integrity. The security model uses PBKDF2-SHA256, hashed "
        "session tokens, per-session CSRF, a login throttle, output escaping and a restrictive "
        "content-security policy."
    )
    B.p(
        "The system was validated with 24 automated tests, route and mutation walkthroughs, nine "
        "security probes, data-integrity invariants and a performance test at two dataset sizes. Six "
        "defects were found and fixed. The behavioural evaluation used a deterministic synthetic "
        "organisation of 24 employees and 104 deliveries across five campaigns. The platform recorded "
        "a 43.3% click rate, a 22.1% submission rate and a 19.2% reporting rate; the post-training "
        "M365 campaign produced an 8.3% submission rate and a 50.0% reporting rate, and the quiz mean "
        "rose from 3.25 to 6.21."
    )

    B.section("10.2", "Conclusions")
    B.p("The following conclusions are supported by the work:")
    B.numbered([
        "**A small, dependency-free platform can deliver a complete phishing measurement loop.** "
        "Campaign authoring, tokenised delivery, event tracking, analytics, coaching, assessment and "
        "reporting can be integrated in a single Python process without a commercial service.",
        "**Privacy can be engineered into the measurement.** Discarding submitted values, hashing "
        "session tokens and storing only field names preserves the behavioural signal while removing "
        "the most sensitive data. The design is a practical template for an ethics-by-design "
        "simulation.",
        "**A transparent risk score is more useful than an opaque vendor metric.** The composite "
        "formula, the underlying counts and the quiz result can be shown to an administrator and, if "
        "necessary, to the employee. The score is a triage tool, not a verdict.",
        "**Immediate coaching closes the loop between failure and learning.** The coaching page uses "
        "the exact lure that the participant encountered, which makes the red flags concrete and "
        "connects the assessment to the experience.",
        "**The synthetic evaluation validates the instrument, not the intervention.** The platform "
        "recovers the patterns that were designed into the cohort and presents them coherently. The "
        "post-training improvement is a demonstration of measurement capability, not proof that "
        "training caused the change.",
        "**A field pilot is necessary before making claims about a real workforce.** The synthetic "
        "cohort is too small and too controlled to support population estimates. The next step is a "
        "consented, pre-registered study with a comparison group and a delayed post-test.",
    ])

    B.section("10.3", "Contributions")
    B.p("The project makes four contributions that are useful beyond the immediate assignment:")
    B.bullets([
        "**Artefact.** A working, auditable platform that can be deployed on a laptop or a "
        "departmental server and extended without a commercial licence.",
        "**Method.** A reproducible synthetic evaluation that connects a documented data-generating "
        "process to an analytics pipeline and an exported results file.",
        "**Design knowledge.** A concrete demonstration that privacy-preserving telemetry, a "
        "transparent risk model and embedded coaching can coexist in a small system.",
        "**Teaching material.** A codebase and report that show how security engineering, data "
        "analysis and ethical reasoning fit together in a single project.",
    ])

    B.section("10.4", "Limitations")
    B.p(
        "The limitations are significant and should be stated plainly. The evaluation uses a "
        "synthetic cohort of 24 employees, so the rates are not population estimates. The "
        "post-training improvement is parameterised, so the study cannot attribute it to the "
        "training. The difficulty comparison is confounded with campaign and time. The platform does "
        "not send real email, integrate with a production identity provider or capture real "
        "credentials, which limits ecological validity. The security validation is a set of targeted "
        "probes, not a penetration test. The usability review is a heuristic inspection by the "
        "developer, not an independent user study. The performance test is single-client and local. "
        "The risk score is a linear heuristic, not a validated psychometric instrument."
    )
    B.p(
        "These limitations do not invalidate the artefact. They define the boundary of the claims "
        "that the artefact supports. The platform is a working measurement instrument; the synthetic "
        "study demonstrates that the instrument can measure; the field pilot is the next step in "
        "establishing whether the measurements are useful in practice."
    )

    B.section("10.5", "Future Work")
    B.p("Six directions are planned or recommended:")
    B.numbered([
        "**Consented field pilot.** Deploy in two organisations or departments with ethics approval, "
        "a participant notice, an opt-out and a pre-registered analysis plan. Use a baseline, a "
        "training round and a post-training round on a like-for-like lure.",
        "**Adaptive difficulty.** Randomise lure difficulty within phase and use more than one lure "
        "per level, so that the effect of difficulty can be separated from the effect of campaign and "
        "time. Add an adaptive algorithm that selects the next lure from the participant's prior "
        "performance.",
        "**Longitudinal measurement.** Add a delayed post-test at four to eight weeks to estimate "
        "retention, and a second training round to test whether booster sessions are needed.",
        "**Platform hardening.** Add per-administrator accounts and SSO, the Secure cookie flag, a "
        "database-backed throttle, encrypted backups, a retention policy, pagination for large "
        "populations and a grouped risk query to replace the per-employee loop.",
        "**Mail-gateway integration.** Provide an optional SMTP adapter that can deliver through a "
        "sandboxed relay when a host organisation requires realism, with a hard-coded allow-list and "
        "a kill switch.",
        "**Responsible lure generation.** Explore template assistance with a large language model "
        "under a strict review workflow, so that lures remain realistic without introducing harmful "
        "content or uncontrolled personalisation.",
    ])

    B.section("10.6", "Closing Remarks")
    B.p(
        "Phishing persists because it targets a human decision that no single control can remove. "
        "The contribution of this project is not a silver bullet but a measurement discipline: define "
        "the event, protect the person, close the loop with coaching, and publish the formula behind "
        "the score. A small organisation can adopt that discipline without a large budget, and a "
        "student team can build, test and explain it. The next step is to take the instrument into a "
        "real organisation and to let the evidence, rather than the demonstration, decide what works."
    )
