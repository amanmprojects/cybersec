"""Chapters 4-6 of the report."""
from __future__ import annotations

from report_common import ReportBuilder


def chapter4(B: ReportBuilder):
    B.chapter(4, "Methodology")

    B.lead(
        "This chapter explains how the system was designed and evaluated. It describes the design-"
        "science stance, the simulation model that produces the synthetic cohort, the operational "
        "definitions of every metric, the risk-scoring formula, the training design, the data-"
        "protection rules and the validation strategy. The chapter is deliberately explicit about "
        "what the synthetic evaluation can and cannot establish, because that distinction governs "
        "how the results in Chapter 9 should be read."
    )

    B.section("4.1", "Research Design")
    B.p(
        "The project follows the design-science research paradigm described by Hevner et al., in "
        "which knowledge is produced through the construction and evaluation of an artefact "
        f"{B.cite('hevner2004')}. The artefact is the PhishStudy platform: a software system, a data "
        "model and an evaluation pipeline. The evaluation has two strands. The first is **technical "
        "validation**: does the system behave correctly under unit, integration, security and load "
        "tests? The second is **behavioural illustration**: does the analytics pipeline recover the "
        "patterns that were designed into a calibrated synthetic cohort, and are those patterns "
        "presented in a way that a security manager can act on?"
    )
    B.p(
        "The two strands answer different questions. Technical validation can establish that the "
        "software is correct with respect to its specification. Behavioural illustration cannot "
        "establish that a real workforce would behave in the same way; it can only show that the "
        "instrument is capable of measuring and explaining a realistic pattern. The report keeps "
        "these claims separate. The field deployment that would support causal claims about training "
        "is planned for Semester VIII and is described in Chapter 6."
    )
    B.p(
        "The development process was iterative. Requirements were elicited from the literature and "
        "from the practical constraints of a college laboratory; a prototype was built; each "
        "prototype was exercised through the participant and administrator flows; defects were "
        "recorded and fixed; and the test suite was expanded after each defect. This is closer to "
        "action research than to a waterfall, and it produced a system that is shaped by use rather "
        "than by an abstract specification."
    )

    B.section("4.2", "Simulation Model")
    B.p(
        "The demonstration dataset represents a fictional company, NorthStar Technologies, with 24 "
        "employees in six departments. Each employee has a **latent susceptibility** value between "
        "zero and one. The values are hand-tuned so that the cohort has a believable spread: IT has "
        "the lowest values, Sales and Finance the highest, and the other departments sit in between. "
        "The latent value is not shown to the administrator; it is an input to the data generator, "
        "used to make the same people behave coherently across campaigns."
    )
    B.p(
        "Each campaign has three **prevalence targets**: the percentage of recipients expected to "
        "click, to submit and to report. At launch, recipients are ranked by latent susceptibility "
        "plus a small Gaussian noise term. The top-ranked recipients become clickers, the "
        "highest-ranked become submitters, and reporters are drawn from the non-clickers with the "
        "lowest latent values. This quota-based construction guarantees that the cohort exhibits the "
        "intended aggregate pattern while preserving individual coherence: a person who is "
        "susceptible in one campaign is likely to be susceptible in the next. Open events occur with "
        "probability 0.92, and reporters always open the message. Timestamps are drawn uniformly "
        "within realistic windows: 0.4–7 hours to open, 0.2–5 hours from open to click, 0.1–1.5 "
        "hours from click to submission, and 0.3–20 hours from launch to report."
    )
    B.p(
        "The generator is seeded with a fixed value, so every fresh installation produces the same "
        "numbers. This is a deliberate methodological choice. It makes the report reproducible, "
        "allows a reviewer to recompute every percentage, and ensures that screenshots and tables "
        "agree. It also means that the results are a **calibration scenario**, not a random sample. "
        "The five campaign targets were chosen to represent a plausible baseline, a training "
        "intervention and a live campaign; they were not estimated from a real organisation. The "
        "evaluation therefore tests the measurement pipeline against known inputs, not the "
        "effectiveness of training in the field."
    )
    B.p(
        "The lure difficulty label is metadata attached to a template. It is **not** used as a "
        "causal input to the outcome model. In the seeded schedule, difficulty is correlated with "
        "campaign and phase, so the difficulty table in Chapter 9 must not be read as an "
        "experimental comparison of easy, medium and hard lures. This limitation is stated again in "
        "the threats-to-validity section. A future version of the generator will randomise "
        "difficulty within phase so that the effect can be isolated."
    )
    B.figure("4.1", "docs/figures/attack_chain.png",
             "Anatomy of a phishing attack, adapted from the campaign phases modelled by the "
             "platform. The platform instruments planning, delivery, interaction, capture and "
             "feedback; it stops short of exploitation.", width=15.6)

    B.section("4.3", "Campaign Lifecycle and Experimental Procedure")
    B.p(
        "The experimental procedure follows the lifecycle described in Chapter 3. In the baseline "
        "phase, three campaigns are launched one week apart to the whole population: a password-"
        "expiry lure (easy), a festival-bonus lure (medium) and an M365 security alert (hard). Each "
        "campaign runs for seven days. The first two establish a broad baseline; the third provides "
        "the like-for-like stimulus for the post-training comparison."
    )
    B.p(
        "After the third campaign, every employee takes the eight-item quiz as a pre-training "
        "measure. The coaching page and quiz are available to all participants, and the administrator "
        "can see aggregate scores but not individual answers in the dashboard. A post-training "
        "campaign then repeats the M365 lure to the whole population. Because the lure, audience and "
        "difficulty are held constant, any change in the click, submission or report rate can be "
        "attributed to the passage of time and the training, subject to the limitations discussed in "
        "Chapter 9. A fifth campaign, a courier-delivery lure, is launched to the Operations and "
        "Sales departments only, to demonstrate a live, smaller-audience campaign."
    )
    B.p(
        "All campaigns are launched manually by the administrator in the demonstration. The "
        "scheduler is implemented, but the seed uses explicit launch times so that the dataset is "
        "reproducible. The campaign state is advanced through the console, and every transition is "
        "written to the audit log. The procedure is summarised in Table 5.2."
    )

    B.section("4.4", "Metrics and Operational Definitions")
    B.p(
        "A metric is only useful if its denominator and its event semantics are explicit. Table 4.1 "
        "defines the metrics used in the dashboard, the report and the exports. All rates are "
        "percentages of delivered targets, not of employees, because an employee may receive "
        "several campaigns. A target is counted once per event, using the first timestamp; repeated "
        "requests do not inflate the numerator."
    )
    B.table("4.1", "Operational definitions of the reported metrics",
            ["Metric", "Definition", "Denominator", "Interpretation"],
            [
                ["Delivered", "Targets materialised at launch", "—", "Size of the campaign"],
                ["Open rate", "Targets with opened_at set", "Delivered", "Message was rendered; pixel blocking can undercount"],
                ["Click rate", "Targets with clicked_at set", "Delivered", "Link was followed; strongest behavioural signal"],
                ["Submission rate", "Targets with submitted_at set", "Delivered", "Form was submitted; values are not stored"],
                ["Report rate", "Targets with reported_at set", "Delivered", "Positive security behaviour"],
                ["Median time to click", "Median of clicked_at − sent_at", "Clickers", "Speed of engagement, in hours"],
                ["Repeat click rate", "Share of employees clicking ≥2 campaigns", "Employees", "Persistence of susceptibility"],
                ["Quiz score", "Correct answers out of eight", "Attempts", "Knowledge after coaching"],
                ["Pass rate", "Attempts scoring ≥6/8", "Attempts", "Threshold used by the training module"],
                ["Risk score", "Composite formula in Section 4.5", "Employee", "Bounded 0–100; higher is riskier"],
            ],
            widths=[3.4, 5.4, 2.6, 4.2], font=8.6, align=["l", "l", "l", "l"], bold_first=True)
    B.p(
        "Two metrics require a caveat. Open rate is measured by a tracking pixel; privacy proxies "
        "and image blocking can suppress the request, so a low open rate is not necessarily a low "
        "level of attention. Report rate is modelled as an alternative to engagement in the "
        "synthetic cohort: reporters are drawn from non-clickers. In a real deployment a person "
        "could click and then report, so the reporting and clicking categories would overlap. The "
        "platform records both timestamps independently and can represent that overlap; the "
        "synthetic generator chooses not to, for narrative clarity."
    )

    B.section("4.5", "Composite Risk Score")
    B.p(
        "The individual risk score combines four observable signals. Submission is weighted most "
        "heavily because it represents the greatest potential harm; clicking is weighted next; "
        "reporting is treated as a protective behaviour and subtracts a small amount; and quiz "
        "performance contributes a penalty when knowledge is weak. The formula is:"
    )
    B.callout("Risk formula",
              "risk = 0.60 × submission_rate + 0.25 × click_rate + 15 × (1 − quiz_accuracy) − 0.10 × report_rate")
    B.p(
        "The raw score is clipped to the range 0–100 and rounded to one decimal place. When an "
        "employee has no quiz attempt, the training penalty is set to 10, a neutral value that does "
        "not reward or punish missing data. The bands are shown in Table 4.2. The weights are a "
        "design choice, not an empirical finding; they were chosen so that a person who submits on "
        "every campaign and never reports is classified as critical, while a person who clicks but "
        "never submits, reports consistently and scores well on the quiz remains in the low or "
        "moderate band."
    )
    B.table("4.2", "Risk bands and recommended action",
            ["Band", "Score range", "Interpretation", "Recommended action"],
            [
                ["Low", "0 – 24.9", "Resilient behaviour; reports or ignores most lures", "Maintain awareness; no individual action"],
                ["Moderate", "25 – 49.9", "Occasional clicks; limited submission", "Targeted micro-training; monitor trend"],
                ["High", "50 – 74.9", "Repeated clicks or a submission", "Coaching conversation; priority for the next round"],
                ["Critical", "75 – 100", "Repeated submissions; no reporting", "Immediate support; review account controls; avoid blame"],
            ],
            widths=[2.4, 2.6, 5.6, 5.0], font=8.8, align=["l", "c", "l", "l"], bold_first=True)
    B.p(
        "The score is deliberately transparent. An administrator can see the four inputs, and the "
        "report explains the formula. This is a contrast to commercial platforms that present a "
        "single 'phishing-prone' percentage without a published derivation. The trade-off is that a "
        "simple linear formula cannot capture every interaction; it is a communication and "
        "triage tool, not a psychometric instrument."
    )

    B.section("4.6", "Training Design")
    B.p(
        "The training is embedded in the moment of failure. When a participant submits a landing "
        "page, the platform does not simply display a generic warning. It renders the original "
        "message alongside a list of the specific red flags in that message: the look-alike domain, "
        "the urgency cue, the generic greeting, the request for a password or OTP. It then offers an "
        "eight-item quiz that tests recognition, safe action, MFA, password practice and incident "
        "response. The quiz is scored immediately, with the correct answer and a short explanation "
        "for each item."
    )
    B.p(
        "The item bank is fixed so that scores are comparable across rounds. The pass mark is six "
        "out of eight (75%), stored in the settings table. The quiz is not designed to certify "
        "competence; it is designed to reinforce the coaching and to give the administrator a "
        "second, knowledge-based signal alongside behaviour. The questions avoid jargon and use the "
        "same fictional brand and domain as the lures, so that the transfer from the simulation to "
        "the assessment is direct. Appendix B reproduces the instrument."
    )

    B.section("4.7", "Data Collection, Consent and Privacy")
    B.p(
        "The platform collects four categories of data: identity data for the fictional employees "
        "(name, email, department, designation), campaign definitions, behavioural timestamps and "
        "quiz responses. It does not collect passwords, OTPs, payment details or any other value "
        "entered into a landing page. The submission handler reads the field names from the form, "
        "stores them as a JSON array, and discards the values before rendering the response. This "
        "is the most important privacy control in the system: even if the database were disclosed, "
        "it would not contain a credential."
    )
    B.p(
        "In a real deployment, the lawful basis for processing would be the employer's legitimate "
        "interest in information security, supported by a transparency notice, a programme-level "
        "consent process and a data-protection impact assessment. The platform provides the "
        "technical preconditions: purpose limitation (behavioural data is used only for the "
        "awareness programme), minimisation (no values), storage limitation (a retention setting is "
        "planned), integrity (hashed tokens, parameterised queries) and accountability (audit log). "
        "The synthetic demonstration avoids the legal question entirely, but the design is intended "
        "to be deployable under the GDPR and the Indian DPDP Act with the appropriate organisational "
        f"safeguards {B.cite('gdpr', 'dpdp')}."
    )

    B.section("4.8", "Validation Approach")
    B.p(
        "Validation combines four levels. **Unit tests** exercise the security primitives and the "
        "analytics functions in isolation. **Integration tests** drive the HTTP server through "
        "login, campaign creation, participant flows, exports and quiz submission. **Security tests** "
        "probe authentication, CSRF, session handling, open redirects and output escaping. **Data-"
        "integrity tests** check that the funnel is monotonic, that no submission exists without a "
        "click, that department totals reconcile with the overview, and that the seeded dataset has "
        "the expected shape. A performance test measures response times at the demonstration scale "
        "and at a synthetically enlarged scale. A heuristic usability review applies Nielsen's ten "
        f"heuristics to the principal screens {B.cite('nielsen1994')}."
    )
    B.p(
        "The validation is not a substitute for a field trial. It can show that the software does "
        "what it claims and that the analytics are internally consistent; it cannot show that the "
        "metrics predict real-world compromise. The next chapter describes the experimental setup "
        "in enough detail for another team to reproduce the synthetic study."
    )

    B.section("4.9", "Ethical Framework")
    B.p(
        "The project follows five ethical principles. **No real deception:** no message leaves the "
        "application, and the demonstration population is fictional. **No real secrets:** submitted "
        "values are discarded. **Informed participation:** in a field deployment, employees would "
        "receive a programme notice and an opt-out. **Blameless feedback:** individual results are "
        "used for coaching, not discipline, and the report recommends against punitive use. "
        "**Proportionate data:** only the minimum data needed for the metric is retained, and access "
        "to the console is restricted."
    )
    B.p(
        "These principles are not merely stated in a policy; they are reflected in the code. The "
        "simulation banner is rendered on every page. The participant routes are tokenised and do "
        "not expose a directory of employees. The export endpoints require an administrator session. "
        "The audit log records exports. The report itself aggregates departments and does not "
        "publish individual quiz answers. The ethics review is therefore an input to the design, not "
        "an afterthought."
    )

    B.section("4.10", "Summary")
    B.p(
        "The methodology combines design-science construction with a transparent synthetic "
        "evaluation. The simulation model is quota-based and calibrated, not predictive; it exists "
        "to test the measurement pipeline and to produce a coherent demonstration. The metrics are "
        "defined operationally, the risk score is published, the training is embedded, and the "
        "privacy controls are enforced in code. The next chapter describes the experimental setup "
        "in detail."
    )


def chapter5(B: ReportBuilder):
    B.chapter(5, "Experimental Setup")

    B.lead(
        "This chapter describes the environment, the synthetic population, the campaign schedule, "
        "the lure catalogue, the quiz instrument and the procedure used to produce the results in "
        "Chapter 9. The level of detail is intentional: a reader should be able to recreate the "
        "dataset from the seed and compare their numbers with those reported here."
    )

    B.section("5.1", "Environment")
    B.p(
        "The platform was developed and evaluated on a Linux workstation with an Intel Core "
        "i7-13620H processor and 16 GB of RAM. The runtime is Python 3.14.7 with the standard "
        "library only; SQLite 3.53.4 provides persistence. LibreOffice 26.8 was used to render the "
        "report and to convert it to PDF. Chromium in headless mode was used to capture the screen "
        "images in Chapter 7. No container, cloud service or external database was used. The "
        "application listens on 127.0.0.1 by default and binds to a configurable host and port."
    )

    B.section("5.2", "Synthetic Organisation")
    B.p(
        "NorthStar Technologies is a fictional 24-person organisation with six departments of four "
        "employees each. The names, email addresses and designations are synthetic; the domain "
        "`northstar.example` is reserved for documentation and cannot receive mail. The population "
        "was designed to include a range of roles that plausibly encounter external requests: "
        "account executives and a regional sales lead; accounts, billing, audit and financial "
        "analysts; HR managers, recruiters and payroll staff; legal counsel, compliance and contract "
        "staff; operations leads, process analysts and support staff; and IT engineers, "
        "administrators, analysts and DevOps staff. Table 5.1 summarises the population."
    )
    B.table("5.1", "Composition of the synthetic population",
            ["Department", "Employees", "Representative roles", "Expected exposure"],
            [
                ["IT", "4", "Systems engineer, network administrator, security analyst, DevOps", "Low (security-trained)"],
                ["HR", "4", "HR manager, recruiter, payroll officer, HR executive", "Moderate"],
                ["Finance", "4", "Accounts manager, financial analyst, auditor, billing", "High (payments, invoices)"],
                ["Sales", "4", "Regional lead, account executive, business development, inside sales", "High (external mail, urgency)"],
                ["Operations", "4", "Operations lead, process analyst, logistics, support", "Moderate"],
                ["Legal", "4", "Legal counsel, compliance officer, contract analyst, paralegal", "Moderate"],
            ],
            widths=[2.8, 2.0, 7.4, 3.4], font=8.8, align=["l", "c", "l", "l"], bold_first=True)
    B.p(
        "The latent susceptibility values were assigned by department and then varied within each "
        "department to avoid a deterministic mapping. IT has the lowest values, Sales and Finance "
        "the highest, and HR, Operations and Legal occupy the middle. The values are an input to the "
        "generator, not a claim about real employees. Their purpose is to create a cohort in which "
        "individual behaviour is coherent across campaigns, so that repeat-clicking and risk "
        "ranking are meaningful."
    )

    B.section("5.3", "Campaign Schedule")
    B.p(
        "Five campaigns were launched between 24 August and 18 October 2026, and a sixth is "
        "scheduled for January 2027. The first three form the baseline; the fourth repeats the M365 "
        "lure after training; the fifth is a live, smaller-audience campaign. Table 5.2 gives the "
        "schedule and the number of recipients."
    )
    B.table("5.2", "Campaign schedule",
            ["#", "Campaign", "Launched", "Phase", "Lure", "Audience", "Sent"],
            [
                ["1", "Q1 Baseline — Password Expiry", "24 Aug 2026", "Baseline", "IT Password Expiry", "All (24)", "24"],
                ["2", "Q1 Baseline — Festival Bonus", "31 Aug 2026", "Baseline", "HR Festival Bonus", "All (24)", "24"],
                ["3", "Q2 Baseline — M365 Alert", "07 Sep 2026", "Baseline", "M365 Security Alert", "All (24)", "24"],
                ["4", "Q3 Post-training — M365 Alert", "08 Oct 2026", "Post-training", "M365 Security Alert", "All (24)", "24"],
                ["5", "Q3 Live — Courier Delivery", "18 Oct 2026", "Live", "Courier Delivery Failure", "Sales + Operations (8)", "8"],
                ["6", "Q4 Planned — Shared Document", "Jan 2027", "Planned", "Shared Document Review", "All (24)", "0"],
            ],
            widths=[0.8, 4.1, 2.3, 2.2, 3.4, 2.4, 1.0], font=8.2, align=["c", "l", "l", "l", "l", "l", "c"])
    B.p(
        "The total number of delivered targets is 104. The sixth campaign is in Draft/Scheduled "
        "state and is excluded from all rate calculations because it has no delivered targets. This "
        "is why the overview reports five campaigns rather than six: the denominator is delivered "
        "targets, not campaign records."
    )

    B.section("5.4", "Lure Catalogue")
    B.p(
        "Six lure templates were authored. Each has a sender name, a look-alike domain, a subject, "
        "an HTML body, a landing form and a list of red flags used by the coaching page. Table 5.3 "
        "summarises the catalogue. The templates cover credential theft, financial reward, malware "
        "delivery, business email compromise and document sharing, which are the categories most "
        "frequently encountered in the literature."
    )
    B.table("5.3", "Lure catalogue",
            ["Lure", "Category", "Difficulty", "Sender domain", "Landing fields", "Red flags"],
            [
                ["IT Password Expiry", "Credential theft", "Easy", "northstar-supportdesk.com", "Email, password, OTP", "4"],
                ["HR Festival Bonus", "Financial lure", "Medium", "northstar-hrportal.com", "Name, employee ID / DOB", "4"],
                ["M365 Security Alert", "Credential theft", "Hard", "micorsoft-secure-auth.com", "Email, password", "4"],
                ["Courier Delivery Failure", "Malware delivery", "Medium", "swiftcourier-delivery.net", "Tracking reference", "4"],
                ["CEO Gift Card Request", "Business email compromise", "Hard", "northstar-ceo.example", "Reply by email", "4"],
                ["Shared Document Review", "Credential theft", "Hard", "northstar-sharepoint.example", "Email, password", "4"],
            ],
            widths=[3.5, 3.2, 1.9, 4.1, 2.4, 1.3], font=8.2, align=["l", "l", "c", "l", "l", "c"], bold_first=True)
    B.p(
        "The first four lures were used in launched campaigns; the last two are available in the "
        "catalogue but were not delivered in the present study. The CEO gift-card lure is included "
        "because BEC is a distinct and high-impact category, and the shared-document lure is "
        "included because it exercises a different pretext (collaboration) from the password-expiry "
        "and security-alert lures. Both are available for the field pilot."
    )

    B.section("5.5", "Quiz Instrument")
    B.p(
        "The quiz has eight multiple-choice items, each with three options and one correct answer. "
        "It covers recognition of a phishing message, domain verification, link inspection, the "
        "correct reporting action, the scope of MFA, business email compromise, password practice and "
        "post-incident response. The blueprint is shown in Table 5.4 and the full instrument is "
        "reproduced in Appendix B. The pass mark is six out of eight."
    )
    B.table("5.4", "Quiz blueprint",
            ["Item", "Theme", "What it tests"],
            [
                ["Q1", "Recognition", "Urgency combined with an unrecognised sender domain"],
                ["Q2", "Domain verification", "A misspelled look-alike domain"],
                ["Q3", "Link inspection", "Visible text versus the actual destination"],
                ["Q4", "Reporting", "The correct action on a suspected message"],
                ["Q5", "MFA", "What multi-factor authentication does and does not protect"],
                ["Q6", "BEC", "An executive request for gift cards and secrecy"],
                ["Q7", "Passwords", "Unique passphrases and a password manager"],
                ["Q8", "Response", "What to do after clicking and entering a password"],
            ],
            widths=[1.6, 4.0, 10.0], font=9.0, align=["c", "l", "l"])
    B.p(
        "The items are deliberately practical. They do not ask the participant to define phishing; "
        "they ask what to do when a domain is misspelled, when a link is shortened, or when an "
        "executive asks for secrecy. The distractors are plausible rather than absurd, so a guess is "
        "not rewarded. The same instrument is used before and after training, which permits a "
        "paired comparison at the cohort level while acknowledging the practice effect discussed in "
        "Chapter 9."
    )

    B.section("5.6", "Experimental Procedure")
    B.p(
        "The procedure has six steps. First, the database is reset to the seeded dataset, which "
        "creates the 24 employees, six lures and six campaign records. Second, the three baseline "
        "campaigns are launched at weekly intervals and allowed to run for seven days. Third, the "
        "participant inbox is used to exercise the flows: open, click, submit and report. Fourth, "
        "the pre-training quiz is administered to the cohort. Fifth, the post-training M365 campaign "
        "and the live courier campaign are launched. Sixth, the analytics are exported to JSON and "
        "the figures and tables in this report are generated from that export."
    )
    B.p(
        "In the demonstration, the participant actions are generated by the seed rather than typed "
        "by 24 people. The administrator can still exercise the live flows manually: the inbox, the "
        "mail view, the landing page, the coaching page and the quiz are fully interactive. This "
        "dual mode is useful for a demonstration and for testing. The seeded data provides the "
        "aggregate cohort; the manual flow proves that a real participant would experience the same "
        "pages."
    )

    B.section("5.7", "Variables and Operationalisation")
    B.p(
        "The independent variables in the synthetic design are the campaign (and therefore the lure, "
        "difficulty and phase), the department, and the training round. The dependent variables are "
        "the click, submission and report indicators, the time to first click, the quiz score and "
        "the composite risk score. Employee identity is a grouping variable that links observations "
        "across campaigns. The unit of analysis for rates is the target; for repeat behaviour and "
        "risk it is the employee."
    )
    B.p(
        "Because the data are synthetic, no confounding adjustment is required for the generator to "
        "produce a coherent dataset. In a field study the same variables would require a pre-"
        "registered analysis plan, a power calculation and adjustment for department, role, tenure "
        "and baseline score. Chapter 6 describes how the field version will address these issues."
    )

    B.section("5.8", "Hardware and Software")
    B.p("Table 5.5 records the environment so that the performance measurements in Chapter 8 can be "
        "interpreted in context.")
    B.table("5.5", "Hardware and software environment",
            ["Component", "Specification"],
            [
                ["Processor", "13th Gen Intel Core i7-13620H, 16 logical CPUs"],
                ["Memory", "16 GB"],
                ["Operating system", "Linux 7.2.5"],
                ["Runtime", "Python 3.14.7 (standard library only)"],
                ["Database", "SQLite 3.53.4, WAL mode, foreign keys enabled"],
                ["Browser", "Chromium (headless) for screen capture"],
                ["Document tooling", "LibreOffice 26.8, python-docx, docxcompose, matplotlib"],
                ["Deployment", "Single process, 127.0.0.1:8000 by default"],
            ],
            widths=[4.0, 11.6], font=9.0, align=["l", "l"], bold_first=True)

    B.section("5.9", "Summary")
    B.p(
        "The experimental setup is a 24-person synthetic organisation, six lures, five launched "
        "campaigns and 104 deliveries, executed on a single Linux workstation with a standard-"
        "library Python stack. The next chapter describes the plan that produced this setup and the "
        "plan for extending it to a consented field pilot."
    )


def chapter6(B: ReportBuilder):
    B.chapter(6, "Implementation Plan")

    B.lead(
        "This chapter describes how the work was planned and how it will continue. It presents the "
        "development approach, the work breakdown, the schedule, the risk register, the quality "
        "assurance process and the plan for Semester VIII. The plan is written in the past tense for "
        "the work already completed and in the future tense for the field pilot, so that the reader "
        "can distinguish delivered outcomes from intentions."
    )

    B.section("6.1", "Development Approach")
    B.p(
        "The project used an iterative, test-driven approach organised around two-week increments. "
        "Each increment began with a small set of requirements, produced a working vertical slice, "
        "and ended with a manual walkthrough and an expanded automated test. The first increment "
        "delivered authentication and the admin shell; the second delivered lure and campaign "
        "management; the third delivered the participant flow and event tracking; the fourth "
        "delivered analytics and risk scoring; the fifth delivered training, reporting and exports. "
        "The later increments hardened the system: CSRF, throttling, security headers, audit logging "
        "and the performance pass."
    )
    B.p(
        "The approach was chosen because the requirements were not fully knowable in advance. "
        "Building the participant flow revealed that the landing page needed to discard values and "
        "that the coaching page needed the original message; building the analytics revealed that "
        "the funnel could become non-monotonic if a submission was recorded without a click. These "
        "discoveries shaped the next increment. A waterfall plan would have deferred them to "
        "integration, where they would have been more expensive to fix."
    )

    B.section("6.2", "Work Breakdown Structure")
    B.p(
        "The work was decomposed into seven work packages. Table 6.1 lists the packages, the "
        "principal deliverables and the effort. The effort is expressed in person-weeks for a "
        "single developer and includes design, implementation and testing."
    )
    B.table("6.1", "Work breakdown structure",
            ["WP", "Work package", "Deliverables", "Effort"],
            [
                ["WP1", "Literature and requirements", "Review, requirements catalogue, success criteria", "2 weeks"],
                ["WP2", "Architecture and data model", "Layer diagram, ER model, threat model", "1.5 weeks"],
                ["WP3", "Security and identity", "PBKDF2, sessions, CSRF, throttle, audit", "2 weeks"],
                ["WP4", "Campaign and lure management", "CRUD, lifecycle, audience, tokens", "2.5 weeks"],
                ["WP5", "Participant experience", "Inbox, mail, landing, coaching, report", "2 weeks"],
                ["WP6", "Analytics and training", "Funnel, departments, risk, quiz, exports", "2.5 weeks"],
                ["WP7", "Validation and documentation", "24 tests, performance, report, figures", "3 weeks"],
            ],
            widths=[1.2, 4.2, 8.0, 2.2], font=8.8, align=["c", "l", "l", "c"], bold_first=True)

    B.section("6.3", "Schedule")
    B.p(
        "Figure 6.1 shows the schedule from August 2026 to July 2027. The work completed in "
        "Semester VII is shown in green; report drafting is ongoing; the field pilot, longitudinal "
        "evaluation and final dissertation are planned for Semester VIII. The dashed line marks the "
        "semester boundary."
    )
    B.figure("6.1", "docs/figures/gantt.png",
             "Work completed and planned. The Semester VII prototype and synthetic pilot are "
             "complete; the Semester VIII field pilot and longitudinal evaluation are planned.",
             width=15.6)
    B.p("Table 6.2 lists the milestones and their acceptance criteria.")
    B.table("6.2", "Milestones and acceptance criteria",
            ["Milestone", "Date", "Acceptance criterion"],
            [
                ["M1 Requirements baseline", "Aug 2026", "Requirements catalogue approved by the guide"],
                ["M2 Architecture review", "Sep 2026", "ER model, DFD and threat model reviewed"],
                ["M3 Working prototype", "Sep 2026", "Login, campaign creation and participant flow demonstrable"],
                ["M4 Feature complete", "Oct 2026", "All mandatory FRs implemented; 24 tests passing"],
                ["M5 Synthetic pilot complete", "Oct 2026", "Five campaigns, 104 targets, results exported"],
                ["M6 Report submitted", "Nov 2026", "Report, figures, code and test evidence submitted"],
                ["M7 Ethics approval for field pilot", "Dec 2026", "Institutional approval and participant notice"],
                ["M8 Field pilot complete", "Mar 2027", "Two organisations, pre/post data collected"],
                ["M9 Final dissertation", "May 2027", "Dissertation submitted and defended"],
            ],
            widths=[4.8, 2.6, 8.2], font=8.8, align=["l", "c", "l"])

    B.section("6.4", "Risk Management")
    B.p(
        "The project faced technical, ethical and organisational risks. Table 6.3 records the "
        "principal risks, their assessment and the mitigation actually adopted or planned. The "
        "register was reviewed at the start of each increment."
    )
    B.table("6.3", "Risk register",
            ["Risk", "Likelihood", "Impact", "Mitigation"],
            [
                ["Scope creep beyond a one-semester prototype", "High", "High", "Mandatory FRs frozen at M4; should-have items deferred"],
                ["Security defect in the admin console", "Medium", "High", "Threat model, CSRF on every mutation, 24 tests, manual review"],
                ["Data loss during development", "Medium", "Medium", "SQLite WAL, reset command, seeded reproducibility, exports"],
                ["Ethical objection to phishing simulation", "Medium", "High", "Synthetic data only in Sem VII; consent and debrief plan for Sem VIII"],
                ["Single-developer bandwidth", "High", "Medium", "Two-week increments; reuse of standard-library components"],
                ["Small sample limits external validity", "High", "Medium", "Explicit limitations; field pilot in Sem VIII"],
                ["Performance degradation at scale", "Low", "Medium", "Indexed queries, benchmark at 1,024 employees, pagination"],
            ],
            widths=[5.0, 2.0, 2.0, 6.6], font=8.4, align=["l", "c", "c", "l"], bold_first=True)

    B.section("6.5", "Quality Assurance")
    B.p(
        "Quality assurance combined automated and manual activities. The automated suite is run with "
        "`python3 -m unittest discover -s tests` and covers security primitives, analytics, HTTP "
        "routes, the participant flow, exports and quiz submission. The manual checklist covers the "
        "visual design, keyboard navigation, mobile layout, error messages, empty states and the "
        "printable report. Every defect found in manual testing was reproduced as an automated test "
        "where possible, so that the suite grew with the system."
    )
    B.p(
        "Code quality was maintained through small modules, type hints, docstrings on public "
        "functions and a consistent naming convention. The project has no third-party runtime "
        "dependencies, which removes a large class of supply-chain and upgrade risks. The trade-off "
        "is that some functionality (routing, sessions, CSRF) is implemented in-house; the security "
        "tests are the compensating control. The code is organised so that a reviewer can read the "
        "security module, the analytics module and the server module independently."
    )

    B.section("6.6", "Plan for Semester VIII")
    B.p(
        "Semester VIII will move from a synthetic cohort to a consented field pilot. The plan has "
        "four workstreams. **Ethics and governance:** obtain institutional approval, prepare a "
        "participant notice, a data-protection impact assessment and an opt-out process; agree with "
        "the host organisation that individual results will not be used for discipline. **Pilot "
        "design:** recruit two organisations or two departments, with a baseline campaign, a training "
        "round and a post-training campaign; randomise the order of lures within phase; pre-register "
        "the primary outcome (submission rate on the repeated lure). **Platform hardening:** add "
        "SSO or at least per-administrator accounts, a retention policy, encrypted backups, "
        "pagination for large populations and a mail-gateway adapter that can deliver through a "
        "sandboxed SMTP relay if the host insists on realism. **Analysis:** estimate the required "
        "sample size, analyse paired outcomes at the employee level, report effect sizes with "
        "confidence intervals, and publish the anonymised aggregate dataset."
    )
    B.p(
        "The field pilot will not attempt to replicate a commercial platform's content library. Its "
        "value is the combination of a transparent risk model, a reproducible pipeline and a "
        "blameless training loop. The target is a defensible within-subject comparison on a "
        "like-for-like lure, with enough participants to detect a meaningful change in submission "
        "rate. If recruitment is insufficient, the study will be reported as a feasibility pilot "
        "rather than as a hypothesis test."
    )

    B.section("6.7", "Summary")
    B.p(
        "The project was delivered through seven work packages and nine milestones. The schedule, "
        "risk register and quality process are documented, and the Semester VIII plan converts the "
        "synthetic evaluation into a field study with appropriate ethical safeguards. The next "
        "chapter describes the implementation in detail."
    )
