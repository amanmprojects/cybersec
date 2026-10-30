"""Deterministic demo data for PhishStudy.

The dataset is synthetic: a fictional company ("NorthStar Technologies"),
24 fictional employees and six simulated lures. Outcomes are generated from a
latent-susceptibility model so the same people tend to behave consistently
across campaigns — which makes the analytics meaningful rather than random.

A fixed seed is used, so every fresh install produces the same report numbers.
"""
from __future__ import annotations

import datetime as _dt
import json
import random

from .security import hash_password

COMPANY = "NorthStar Technologies"
COMPANY_DOMAIN = "northstar.example"


def _plus_hours(stamp: str, hours: float) -> str:
    """Return *stamp* shifted by *hours*, formatted like every other timestamp."""
    base = _dt.datetime.strptime(stamp, "%Y-%m-%d %H:%M")
    return (base + _dt.timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M")

DEPARTMENTS = ["IT", "HR", "Finance", "Sales", "Operations", "Legal"]

EMPLOYEES = [
    ("Aarav Sharma", "aarav.sharma", "IT", "Systems Engineer"),
    ("Arjun Patel", "arjun.patel", "IT", "Network Administrator"),
    ("Riya Kulkarni", "riya.kulkarni", "IT", "Security Analyst"),
    ("Kabir Shah", "kabir.shah", "IT", "DevOps Engineer"),
    ("Priya Nair", "priya.nair", "HR", "HR Executive"),
    ("Neha Singh", "neha.singh", "HR", "Recruiter"),
    ("Meera Joshi", "meera.joshi", "HR", "HR Manager"),
    ("Aditi Rao", "aditi.rao", "HR", "Payroll Officer"),
    ("Rohan Verma", "rohan.verma", "Finance", "Accounts Manager"),
    ("Sneha Iyer", "sneha.iyer", "Finance", "Financial Analyst"),
    ("Vikram Desai", "vikram.desai", "Finance", "Auditor"),
    ("Pooja Bhatt", "pooja.bhatt", "Finance", "Billing Executive"),
    ("Karan Mehta", "karan.mehta", "Sales", "Regional Sales Lead"),
    ("Divya Rao", "divya.rao", "Sales", "Account Executive"),
    ("Sameer Khan", "sameer.khan", "Sales", "Business Development"),
    ("Tanvi Gupta", "tanvi.gupta", "Sales", "Inside Sales"),
    ("Rahul Desai", "rahul.desai", "Operations", "Operations Lead"),
    ("Ishita Bose", "ishita.bose", "Operations", "Process Analyst"),
    ("Manav Jain", "manav.jain", "Operations", "Logistics Coordinator"),
    ("Shreya Pillai", "shreya.pillai", "Operations", "Support Specialist"),
    ("Ananya Menon", "ananya.menon", "Legal", "Legal Counsel"),
    ("Dhruv Kapoor", "dhruv.kapoor", "Legal", "Compliance Officer"),
    ("Nisha Kaur", "nisha.kaur", "Legal", "Contract Analyst"),
    ("Yash Thakur", "yash.thakur", "Legal", "Paralegal"),
]

# name, category, difficulty, subject, sender_name, sender_email, brand, cta,
# tagline, body, landing_form, red flags
TEMPLATES = [
    (
        "IT Password Expiry", "Credential theft", "Easy",
        "Action Required: Your password expires in 24 hours",
        "IT Helpdesk", "it-helpdesk@northstar-supportdesk.com",
        "NorthStar SSO", "Reset Password Now",
        "Sign in to continue to the Password Portal",
        """<p>Dear Employee,</p>
        <p>Our records show that your domain password will <b>expire in 24 hours</b>.
        If it is not updated, your access to email, VPN and shared drives will be suspended.</p>
        <p>Please act immediately to avoid any disruption to your work.</p>
        <p style="color:#64748b">IT Service Desk<br>Extension 4401 &middot; Building A, 2nd Floor</p>""",
        """<input name="username" placeholder="Company email address" required>
        <input name="password" type="password" placeholder="Password" required>
        <input name="otp" placeholder="One-time password (OTP)">""",
        ["The sender is on an <b>external domain</b> (northstar-supportdesk.com) &mdash; IT would never use it",
         "<b>Artificial urgency</b>: &ldquo;expires in 24 hours&rdquo; exists to stop you thinking",
         "<b>Generic greeting</b> (&ldquo;Dear Employee&rdquo;) with no name",
         "IT departments <b>never ask for passwords or OTPs by email</b>"],
    ),
    (
        "HR Festival Bonus", "Financial lure", "Medium",
        "You've been selected: Festival Bonus & Gift Claim",
        "HR Department", "hr-team@northstar-hrportal.com",
        "HR Rewards Portal", "Claim My Bonus",
        "Verify your details to receive your gift card",
        """<p>Hi,</p><p>Good news! You are among <b>20 employees</b> selected for a
        <b>&#8377;5,000 festival gift card</b> as part of our employee appreciation drive.</p>
        <p>This offer expires <b>today at 6:00 PM</b>. Unclaimed cards will be reissued to the next batch.</p>
        <p style="color:#64748b">Warm regards,<br>HR Team &middot; Human Resources</p>""",
        """<input name="username" placeholder="Full name" required>
        <input name="password" placeholder="Employee ID / Date of birth" required>""",
        ["A <b>prize you never entered a contest for</b> &mdash; unsolicited rewards are a classic lure",
         "<b>Artificial deadline</b> (&ldquo;today 6 PM&rdquo;) prevents you verifying with HR",
         "The sender domain <b>northstar-hrportal.com is not your real HR domain</b>",
         "A genuine bonus never needs your <b>date of birth or employee ID</b> to release a gift card"],
    ),
    (
        "M365 Security Alert", "Credential theft", "Hard",
        "Unusual sign-in activity on your Microsoft 365 account",
        "Microsoft Security", "no-reply@micorsoft-secure-auth.com",
        "Microsoft 365", "Review Sign-in Activity",
        "Verify it's you to keep your account secure",
        """<div style="background:#fef2f2;border:1px solid #fca5a5;border-radius:10px;padding:14px">
        <b>WARNING &mdash; unusual sign-in detected</b><br>We have blocked a login attempt to your account from
        <b>Moscow, Russia</b> (IP 185.220.101.xx) at 3:12 AM today.</div>
        <p style="margin-top:16px">If this was not you, your password may be compromised. Unverified accounts are
        <b>permanently deleted</b> after 24 hours. Secure your account immediately.</p>
        <p style="color:#64748b">Microsoft 365 Security Team<br>Microsoft Corporation</p>""",
        """<input name="username" placeholder="Email address" required>
        <input name="password" type="password" placeholder="Password" required>""",
        ["<b>Typosquatted domain</b> &mdash; &ldquo;micorsoft&rdquo;, not &ldquo;microsoft&rdquo;. This is the biggest tell",
         "<b>Fear tactic</b> &mdash; a foreign login used to panic you into acting",
         "Real Microsoft mail comes only from <b>@microsoft.com</b>",
         "No genuine provider asks you to &ldquo;verify&rdquo; by entering your password into a link"],
    ),
    (
        "Courier Delivery Failure", "Malware delivery", "Medium",
        "Delivery failed: parcel NS-4471 awaiting collection",
        "SwiftCourier Support", "tracking@swiftcourier-delivery.net",
        "SwiftCourier", "Reschedule Delivery",
        "Download the attached label to reschedule your parcel",
        """<p>Hello,</p><p>We attempted to deliver parcel <b>NS-4471</b> today but no one was available.
        The parcel will be returned to the sender in <b>48 hours</b> unless rescheduled.</p>
        <p>Download the delivery label and confirm a new time slot.</p>
        <p style="color:#64748b">SwiftCourier Customer Support</p>""",
        """<input name="username" placeholder="Email address" required>
        <input name="password" placeholder="Tracking reference" required>""",
        ["You were <b>not expecting a parcel</b> &mdash; verify the reference independently",
         "The link downloads a <b>.zip / .exe</b> instead of opening the courier website",
         "The domain <b>swiftcourier-delivery.net</b> is not the courier's official domain",
         "A <b>48-hour deadline</b> is designed to bypass your normal checks"],
    ),
    (
        "CEO Gift Card Request", "Business email compromise", "Hard",
        "Quick favour — are you at your desk?",
        "Ananya Menon", "ananya.menon@northstar-exechr.com",
        "Executive Office", "Reply with Gift Card Codes",
        "I need this handled discreetly before the client call",
        """<p>Hi,</p><p>I'm in back-to-back meetings and need a quick favour. Please purchase
        <b>five &#8377;2,000 gift cards</b> for a client appreciation gesture and send me the codes.</p>
        <p>I'll approve the reimbursement today. Please keep this <b>confidential</b> until the announcement.</p>
        <p style="color:#64748b">Sent from my iPhone</p>""",
        """<input name="username" placeholder="Email address" required>
        <input name="password" placeholder="Gift card codes" required>""",
        ["<b>Authority + secrecy</b> &mdash; an executive asking you to keep it confidential",
         "The reply-to domain <b>northstar-exechr.com</b> is not the company domain",
         "<b>Unusual payment method</b> &mdash; gift cards are untraceable and irreversible",
         "Urgency and &ldquo;sent from my iPhone&rdquo; are used to explain terse, odd wording"],
    ),
    (
        "Shared Document Review", "Credential theft", "Hard",
        "A document has been shared with you: Q3-Redundancy-Plan.docx",
        "NorthStar SharePoint", "sharepoint@northstar-docs.net",
        "SharePoint", "Open Document",
        "Sign in to view the shared document",
        """<p>Hello,</p><p><b>Meera Joshi</b> has shared a document with you:
        <b>Q3-Redundancy-Plan.docx</b></p>
        <p>This document contains confidential restructuring information. Please review it
        before the leadership meeting.</p>
        <p style="color:#64748b">This link expires in 24 hours.</p>""",
        """<input name="username" placeholder="Work email" required>
        <input name="password" type="password" placeholder="Password" required>""",
        ["A <b>fear-inducing filename</b> (redundancy plan) creates panic and curiosity",
         "The domain <b>northstar-docs.net</b> is not your SharePoint tenant",
         "Real SharePoint links open on <b>yourcompany.sharepoint.com</b>",
         "A <b>24-hour expiry</b> on an internal document is unusual"],
    ),
]

QUIZ = [
    ("Which of these is the strongest sign of a phishing email?",
     ["A message from a colleague you were expecting",
      "Urgent threats combined with a sender domain you do not recognise",
      "An email with your company logo in the signature"], 1),
    ("The sender reads <b>micorsoft-secure-auth.com</b>. What do you do?",
     ["Click quickly &mdash; it must be Microsoft",
      "Report it: the domain is misspelled (&ldquo;micorsoft&rdquo;)",
      "Reply asking them to resend the link"], 1),
    ("A link says <b>northstar-portal.com</b> but hovering shows <b>bit.ly/xyz</b>. You&hellip;",
     ["Click it &mdash; the visible text says it is safe",
      "Verify through the official site and report the mail",
      "Forward it to colleagues so they are aware"], 1),
    ("What is the best action on a suspected phishing mail?",
     ["Delete it silently",
      "Report it through the Report-Phish channel and inform IT",
      "Enter your credentials once to check whether it is fake"], 1),
    ("What does MFA protect against?",
     ["A stolen password being enough on its own to log in",
      "All types of malware",
      "Unwanted marketing email"], 0),
    ("An executive emails you asking for gift card codes and secrecy. This is&hellip;",
     ["Normal &mdash; executives often need quick favours",
      "A classic business email compromise pattern",
      "Safe if the email uses the executive's name"], 1),
    ("Which password practice is correct?",
     ["Reuse one strong password everywhere",
      "Use a unique passphrase per account, stored in a password manager",
      "Share passwords with your team lead for continuity"], 1),
    ("You already clicked a suspicious link and typed your password. What now?",
     ["Wait to see if anything happens",
      "Report immediately and change the password from a known-good device",
      "Delete the email and move on"], 1),
]

# name, template index, status, day offset, audience, phase
CAMPAIGNS = [
    ("Q1 Baseline — Password Expiry", 0, "Completed", 0, "All departments", "Baseline"),
    ("Q1 Baseline — Festival Bonus", 1, "Completed", 7, "All departments", "Baseline"),
    ("Q2 Baseline — M365 Alert", 2, "Completed", 14, "All departments", "Baseline"),
    ("Q3 Post-training — M365 Alert", 2, "Completed", 45, "All departments", "Post-training"),
    ("Q3 Live — Courier Delivery", 3, "Active", 55, "Operations, Sales", "Live"),
    ("Q4 Planned — Shared Document", 5, "Scheduled", 74, "All departments", "Planned"),
]

# Latent susceptibility per employee index (0 = very careful, 1 = very clicky).
# Hand-tuned so the demo has a believable spread and a stable, explainable
# narrative: IT is the most resistant department, Finance and Sales the least.
LATENT = [
    0.10, 0.30, 0.08, 0.22,   # IT
    0.45, 0.62, 0.35, 0.55,   # HR
    0.72, 0.60, 0.50, 0.80,   # Finance
    0.68, 0.85, 0.58, 0.64,   # Sales
    0.40, 0.52, 0.66, 0.38,   # Operations
    0.25, 0.44, 0.56, 0.18,   # Legal
]

# Per-campaign prevalence targets (percentage of recipients). Keeping the
# synthetic rates explicit makes the demo reproducible and easy to defend.
OUTCOME_TARGETS = {
    # campaign index: (click %, submit %, report %)
    0: (45, 22, 12),
    1: (55, 30, 10),
    2: (60, 38, 8),
    3: (28, 8, 50),
    4: (25, 12, 12),
}

DIFFICULTY_BONUS = {"Easy": 0.14, "Medium": 0.06, "Hard": 0.0}


def seed_database(conn, *, admin_password: str = "admin123") -> None:
    """Populate an empty database. Safe to call only once."""
    from .db import now, today_offset  # local import avoids a cycle

    cur = conn.cursor()

    cur.execute(
        "INSERT INTO admins(username,password_hash,salt,display_name,created_at) VALUES(?,?,?,?,?)",
        ("admin", hash_password(admin_password), "", "Campaign Administrator", now()),
    )

    for name, handle, dept, title in EMPLOYEES:
        cur.execute(
            "INSERT INTO employees(name,email,department,designation,active,consent,consent_at,created_at)"
            " VALUES(?,?,?,?,1,1,?,?)",
            (name, f"{handle}@{COMPANY_DOMAIN}", dept, title, now(), now()),
        )

    for (name, category, difficulty, subject, sender_name, sender_email, brand, cta,
         tagline, body, landing, flags) in TEMPLATES:
        cur.execute(
            """INSERT INTO templates(name,category,difficulty,subject,sender_name,sender_email,
               brand,cta,tagline,body,landing,flags,active,created_at)
               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,1,?)""",
            (name, category, difficulty, subject, sender_name, sender_email, brand, cta,
             tagline, body, landing, "||".join(flags), now()),
        )

    for key, value in {
        "company_name": COMPANY,
        "company_domain": COMPANY_DOMAIN,
        "default_sender": "it-helpdesk@northstar-supportdesk.com",
        "training_pass_mark": "6",
    }.items():
        cur.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, value))

    employees = cur.execute("SELECT id, department FROM employees ORDER BY id").fetchall()
    rng = random.Random(2026)

    for ci, (name, ti, status, day, audience, phase) in enumerate(CAMPAIGNS):
        created = today_offset(day - 60)
        launched = today_offset(day - 58) if status != "Scheduled" else None
        completed = today_offset(day - 50) if status == "Completed" else None

        cur.execute(
            """INSERT INTO campaigns(name,template_id,status,phase,audience,scheduled_for,created_at,
               launched_at,completed_at,notes,created_by) VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
            (name, ti + 1, status, phase, audience,
             today_offset(day) if status == "Scheduled" else None,
             created, launched, completed, "Seeded demonstration campaign", "admin"),
        )
        cid = cur.lastrowid

        # Audience filter
        if audience == "All departments":
            recipients = list(employees)
        else:
            wanted = {d.strip() for d in audience.split(",")}
            recipients = [e for e in employees if e["department"] in wanted]

        if status == "Scheduled":
            for e in recipients:
                cur.execute(
                    """INSERT INTO targets(campaign_id,employee_id,token,sent_at) VALUES(?,?,?,?)""",
                    (cid, e["id"], f"s{ci+1}-{e['id']:03d}-{rng.randrange(16**6):06x}", None),
                )
            continue

        # Rank recipients by latent susceptibility plus a little noise, then
        # assign outcomes from the fixed prevalence targets. This guarantees a
        # coherent cohort: the same people are phished across campaigns.
        ranked = sorted(
            recipients,
            key=lambda e: (LATENT[e["id"] - 1] + rng.gauss(0, 0.045)),
            reverse=True,
        )
        n = len(ranked)
        click_pct, submit_pct, report_pct = OUTCOME_TARGETS[ci]
        n_click = max(1, round(n * click_pct / 100))
        n_submit = max(1, round(n * submit_pct / 100))
        n_report = max(1, round(n * report_pct / 100))

        clickers = ranked[:n_click]
        submitters = ranked[:n_submit]
        # Reporting is drawn from the people who did not click, mirroring the
        # real behaviour we want to reward: report instead of engaging.
        non_clickers = ranked[n_click:]
        reporters = sorted(non_clickers, key=lambda e: LATENT[e["id"] - 1])[:n_report]

        clicked_ids = {e["id"] for e in clickers}
        submitted_ids = {e["id"] for e in submitters}
        reported_ids = {e["id"] for e in reporters}

        for e in recipients:
            opened = clicked = submitted = reported = None
            # Reporters must have opened the mail; a small share of others never
            # engage at all, which keeps the funnel realistic.
            if rng.random() < 0.92 or e["id"] in reported_ids:
                opened = _plus_hours(launched, rng.uniform(0.4, 7))
                if e["id"] in clicked_ids:
                    clicked = _plus_hours(opened, rng.uniform(0.2, 5))
                    if e["id"] in submitted_ids:
                        submitted = _plus_hours(clicked, rng.uniform(0.1, 1.5))
            if e["id"] in reported_ids:
                reported = _plus_hours(launched, rng.uniform(0.3, 20))

            cur.execute(
                """INSERT INTO targets(campaign_id,employee_id,token,sent_at,opened_at,clicked_at,
                   submitted_at,reported_at,submitted_fields) VALUES(?,?,?,?,?,?,?,?,?)""",
                (cid, e["id"], f"s{ci+1}-{e['id']:03d}-{rng.randrange(16**6):06x}",
                 launched, opened, clicked, submitted, reported,
                 '["username","password"]' if submitted else None),
            )

    # Training quiz attempts: one pre-training and one post-training round.
    # Scores are inversely related to latent susceptibility.
    quiz_ids = [e["id"] for e in employees]
    for round_index, (offset, campaign_id) in enumerate([(-45, 3), (-10, 4)]):
        for eid in quiz_ids:
            latent = LATENT[eid - 1]
            if round_index == 0:
                accuracy = 0.55 - 0.30 * latent
            else:
                accuracy = 0.94 - 0.34 * latent
            score = max(1, min(len(QUIZ), round(len(QUIZ) * accuracy + rng.uniform(-0.4, 0.4))))
            # Store which option was chosen so that item-level analysis is
            # possible.  The score is honoured exactly: a deterministic subset
            # of items is answered correctly and the rest get a wrong option.
            answers = [correct for _prompt, _options, correct in QUIZ]
            wrong_items = rng.sample(range(len(QUIZ)), len(QUIZ) - score)
            for qi in wrong_items:
                correct = QUIZ[qi][2]
                answers[qi] = (correct + 1 + rng.randrange(len(QUIZ[qi][1]) - 1)) % len(QUIZ[qi][1])
            cur.execute(
                "INSERT INTO quiz_attempts(employee_id,campaign_id,score,total,answers,taken_at)"
                " VALUES(?,?,?,?,?,?)",
                (eid, campaign_id, score, len(QUIZ), json.dumps(answers), today_offset(offset)),
            )

    cur.execute("INSERT INTO audit(actor,action,detail,at) VALUES(?,?,?,?)",
                ("system", "database.seed", "Seeded demonstration dataset", now()))
    conn.commit()
