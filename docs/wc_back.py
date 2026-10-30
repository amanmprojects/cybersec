"""Back matter for the WordCraft build: appendices, plagiarism, references."""
from __future__ import annotations

from wc_builder import WcBuilder
from report_common import REFS


def back_heading(B: WcBuilder, number: str, title: str) -> None:
    B.back_chapter(number, title)


def back_matter(B: WcBuilder) -> None:
    appendix(B)
    plagiarism(B)
    literature(B)
    acknowledgements(B)


def appendix(B: WcBuilder) -> None:
    back_heading(B, "A", "Appendix A: Route Map")
    B.p(
        "Table A.1 lists the HTTP surface of the platform. 'Public' routes are reachable without a "
        "session because they are tokenised participant links or the quiz. 'Admin' routes require a "
        "valid session and, for state-changing requests, a valid CSRF token. The table is a summary; "
        "the authoritative list is in phishstudy/server.py."
    )
    B.table("A.1", "HTTP route map",
            ["Method", "Path", "Access", "Purpose"],
            [
                ["GET", "/login", "Public", "Administrator sign-in page"],
                ["POST", "/login", "Public", "Authenticate and create a session"],
                ["GET", "/", "Admin", "Dashboard with KPIs, funnel and high-risk list"],
                ["GET", "/campaigns", "Admin", "Campaign list and creation form"],
                ["GET", "/campaigns/<id>", "Admin", "Campaign detail, funnel and target events"],
                ["POST", "/campaigns", "Admin", "Create a campaign in Draft"],
                ["POST", "/campaigns/<id>/<action>", "Admin", "Launch, pause, resume, complete, archive or delete"],
                ["GET", "/templates", "Admin", "Lure catalogue"],
                ["POST", "/templates", "Admin", "Create or update a lure"],
                ["POST", "/templates/<id>/duplicate", "Admin", "Duplicate a lure"],
                ["GET", "/people", "Admin", "People directory and risk bands"],
                ["POST", "/people", "Admin", "Add a person"],
                ["POST", "/people/import", "Admin", "Bulk import from CSV text"],
                ["GET", "/analytics", "Admin", "Department, difficulty, template and trend analysis"],
                ["GET", "/training", "Admin", "Quiz attempts and item-level analysis"],
                ["GET", "/audit", "Admin", "Append-only audit log"],
                ["GET", "/settings", "Admin", "Organisation settings and password change"],
                ["GET", "/report", "Admin", "Printable A4 report"],
                ["GET", "/api/export.csv", "Admin", "Per-target CSV export"],
                ["GET", "/api/export.json", "Admin", "Full analytics JSON export"],
                ["GET", "/inbox", "Public", "Simulated participant inbox"],
                ["GET", "/legit/<id>", "Public", "Legitimate (non-phishing) message"],
                ["GET", "/t/<token>", "Public", "Render a simulated message and record an open"],
                ["GET", "/t/<token>/landing", "Public", "Landing page and click record"],
                ["POST", "/t/<token>/submit", "Public", "Record a submission, discard values, redirect to coaching"],
                ["GET", "/t/<token>/educate", "Public", "Coaching page with red flags"],
                ["POST", "/t/<token>/report", "Public", "Record a report and show confirmation"],
                ["GET", "/quiz", "Public", "Participant quiz"],
                ["POST", "/quiz", "Public", "Score a quiz attempt"],
            ],
            widths=[1.5, 5.6, 2.0, 6.5], font=8.0, align=["c", "l", "c", "l"])

    back_heading(B, "B", "Appendix B: Quiz Instrument")
    B.p(
        "The quiz is scored out of eight; the pass mark is six. Each item has three options and one "
        "correct answer. The table reproduces the instrument used in the seeded study."
    )
    B.table("B.1", "Eight-item awareness quiz",
            ["#", "Question", "Options", "Answer"],
            [
                ["Q1", "Which of these is the strongest sign of a phishing email?",
                 "(a) A message from a colleague you were expecting; (b) Urgent threats combined with a sender domain you do not recognise; (c) An email with your company logo in the signature", "b"],
                ["Q2", "The sender reads micorsoft-secure-auth.com. What do you do?",
                 "(a) Click quickly — it must be Microsoft; (b) Report it: the domain is misspelled; (c) Reply asking them to resend the link", "b"],
                ["Q3", "A link says northstar-portal.com but hovering shows bit.ly/xyz. You…",
                 "(a) Click it — the visible text says it is safe; (b) Verify through the official site and report the mail; (c) Forward it to colleagues so they are aware", "b"],
                ["Q4", "What is the best action on a suspected phishing mail?",
                 "(a) Delete it silently; (b) Report it through the Report-Phish channel and inform IT; (c) Enter your credentials once to check whether it is fake", "b"],
                ["Q5", "What does MFA protect against?",
                 "(a) A stolen password being enough on its own to log in; (b) All types of malware; (c) Unwanted marketing email", "a"],
                ["Q6", "An executive emails you asking for gift card codes and secrecy. What do you do?",
                 "(a) Buy the cards — it is the CEO; (b) Verify through a second channel and report the message; (c) Reply with the codes but keep a copy", "b"],
                ["Q7", "Which password practice is correct?",
                 "(a) Reuse a strong password across sites; (b) Use a unique passphrase stored in a password manager; (c) Use your date of birth with a symbol", "b"],
                ["Q8", "You already clicked a suspicious link and entered a password. What now?",
                 "(a) Change the password, report it immediately and watch for unusual activity; (b) Wait to see whether anything happens; (c) Delete the mail and say nothing", "a"],
            ],
            widths=[0.9, 5.0, 8.0, 1.4], font=7.8, align=["c", "l", "l", "c"])

    back_heading(B, "C", "Appendix C: Export Schema")
    B.p(
        "The CSV export contains one row per target. The JSON export contains the full analytics "
        "snapshot. Neither export contains submitted values, passwords, session tokens or quiz "
        "answers. Table C.1 lists the columns and the top-level JSON keys."
    )
    B.table("C.1", "Export schema",
            ["Surface", "Field", "Description"],
            [
                ["CSV", "campaign", "Campaign name"],
                ["CSV", "phase", "Baseline, Post-training or Live"],
                ["CSV", "difficulty", "Lure difficulty label"],
                ["CSV", "employee", "Employee full name"],
                ["CSV", "email", "Employee email address"],
                ["CSV", "department", "Department"],
                ["CSV", "sent_at", "Delivery timestamp"],
                ["CSV", "opened_at", "First open timestamp (nullable)"],
                ["CSV", "clicked_at", "First click timestamp (nullable)"],
                ["CSV", "submitted_at", "First submission timestamp (nullable)"],
                ["CSV", "reported_at", "First report timestamp (nullable)"],
                ["JSON", "overview", "Counts and rates for the whole programme"],
                ["JSON", "campaigns", "Per-campaign summary"],
                ["JSON", "departments", "Per-department summary"],
                ["JSON", "templates", "Per-lure summary"],
                ["JSON", "employees", "Per-employee counts, risk score and band"],
                ["JSON", "repeat_clickers", "Employees with two or more clicks"],
                ["JSON", "quiz", "Pre/post scores and item-level accuracy"],
                ["JSON", "generated_at", "Timestamp of the export"],
            ],
            widths=[1.8, 4.2, 9.6], font=8.2, align=["c", "l", "l"])


def plagiarism(B: WcBuilder) -> None:
    back_heading(B, "", "Plagiarism Report")
    B.p(
        "The similarity report generated by the Institute's plagiarism-detection account will be "
        "inserted on this page before final submission. The report must show the overall similarity "
        "index, the list of matching sources, the date of generation and the signature of the "
        "project guide. The Institute's permissible limit applies."
    )
    B.table("P.1", "Plagiarism verification record",
            ["Field", "Detail"],
            [
                ["Overall similarity index", "____________________ %"],
                ["Similarity excluding quotes and bibliography", "____________________ %"],
                ["Matching sources", "Attach the full Turnitin/IThenticate report"],
                ["Date of verification", "____________________"],
                ["Verified by (guide)", "Dr. Yogita Shelar"],
                ["Student signature", "____________________"],
            ],
            widths=[6.8, 8.8], font=9.0, align=["l", "l"], bold_first=True, zebra=False)
    B.p(
        "Note: the report in this document is the student's own work. The platform, the synthetic "
        "dataset and the figures were produced for this project. External sources are cited in the "
        "text and listed in the Literature Cited section.",
        italic=True,
    )


def literature(B: WcBuilder) -> None:
    back_heading(B, "", "Literature Cited")
    B.p(
        "References are numbered in the order of first citation and follow the IEEE numeric style.",
        align="left", after=8,
    )
    for i, key in enumerate(B.cited, 1):
        B.ref_paragraph(f"[{i}]  {REFS[key]}")


def acknowledgements(B: WcBuilder) -> None:
    back_heading(B, "", "Acknowledgements")
    B.p(
        "I would like to express my sincere gratitude to my project guide, Dr. Yogita Shelar, for "
        "her guidance, patience and constructive criticism throughout this project. Her questions "
        "about the measurement model and the ethics of simulation shaped the work more than any "
        "other input."
    )
    B.p(
        "I am grateful to the Head of the Department of Information Technology and to the faculty "
        "and staff of Vidyavardhini's College of Engineering & Technology for providing the "
        "laboratory facilities and the academic environment in which this work was carried out. I "
        "also thank the project coordinators for their timely reviews and for insisting on a "
        "working demonstration rather than a slide deck."
    )
    B.p(
        "I thank my project teammates for their contributions to the literature review, the "
        "testing and the presentation, and my family and friends for their encouragement during "
        "the long debugging sessions. Finally, I acknowledge the open-source community behind "
        "Python, SQLite and LibreOffice; this project would not have been possible without their "
        "work."
    )
