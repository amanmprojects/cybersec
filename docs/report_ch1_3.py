"""Chapters 1-3 of the report."""
from __future__ import annotations


from report_common import ReportBuilder


def chapter1(B: ReportBuilder):
    B.chapter(1, "Introduction", first=True)

    B.section("1.1", "Background")
    B.p(
        "Organisations of every size now depend on email, collaboration platforms and cloud "
        "identity providers to conduct routine business. That dependence has made the human "
        "inbox a permanent attack surface. Phishing is the use of a deceptive message, usually "
        "but not exclusively email, to persuade a person to disclose credentials, open a "
        f"malicious attachment, transfer money or approve an attacker-initiated action {B.cite('aleroud2017')}. "
        "The attack succeeds by exploiting trust, habit and authority rather than a software "
        "defect, which is why it survives repeated improvements in spam filtering and endpoint "
        "protection."
    )
    B.p(
        "The scale of the problem is well documented. Verizon's 2025 Data Breach Investigations "
        f"Report attributes a human element to approximately 60% of breaches {B.cite('verizon2025')}, "
        "while the Anti-Phishing Working Group continues to record phishing volumes far above "
        f"the levels seen before 2020 {B.cite('apwg2025')}. The IBM Cost of a Data Breach Report "
        f"puts the global average cost of a breach at USD 4.44 million in 2025 {B.cite('ibm2025')}, "
        "and the United States Federal Trade Commission reports that consumers lost USD 12.5 "
        f"billion to fraud in 2024, a 25% increase over the previous year {B.cite('ftc2025')}. "
        "Phishing and spoofing remain among the most frequently reported categories in the FBI's "
        f"Internet Crime Report {B.cite('ic32025')}. These figures are not merely financial: they "
        "represent lost time, eroded trust and, in healthcare and critical infrastructure, risk "
        "to safety."
    )
    B.p(
        "Technical controls reduce exposure but cannot remove the problem. Sender authentication "
        "through SPF, DKIM and DMARC, link rewriting, attachment sandboxing, multi-factor "
        f"authentication and endpoint detection all raise the cost of an attack {B.cite('gupta2018')}. "
        "Attackers respond by registering look-alike domains, abusing legitimate file-sharing "
        "services, hijacking existing email threads and deploying adversary-in-the-middle proxies "
        f"that relay one-time codes in real time {B.cite('msddr2024')}. The result is a moving "
        "target in which the final decision is still made by a person under time pressure. "
        "Security awareness is therefore not an alternative to engineering controls; it is the "
        "layer that determines whether a convincing message is reported, ignored or actioned."
    )

    B.section("1.2", "Motivation")
    B.p(
        "Awareness programmes are frequently delivered as an annual slide deck, a poster campaign "
        "or a compliance module that employees click through without engagement. Such programmes "
        "are difficult to evaluate. An organisation may be unable to answer basic questions: what "
        "fraction of staff would submit credentials to a convincing login page, which departments "
        "are most exposed, whether reporting behaviour improves after coaching, and whether the "
        "same individuals are repeatedly caught. Without measurement, awareness spending becomes "
        "an act of faith."
    )
    B.p(
        "Commercial phishing simulation platforms answer part of this need, but they carry "
        "licensing costs, require cloud connectivity and place employee behaviour data with a "
        "third party. Open-source tools such as GoPhish and King Phisher remove the licence fee "
        f"but focus on campaign delivery rather than an integrated training and risk-analytics "
        f"workflow {B.cite('gophish', 'kingphisher')}. Small enterprises, colleges and public "
        "institutions often lack the staff to assemble these components into a defensible "
        "programme. There is a practical gap for a self-hosted, auditable platform that a small "
        "team can operate and explain."
    )
    B.p(
        "There is also a methodological gap. Evaluating a phishing-awareness intervention with "
        "real employees raises consent, privacy and industrial-relations questions. A platform "
        "that first demonstrates its measurement logic on a transparent synthetic population, "
        "and only then moves to a consented field pilot, offers a lower-risk route to evidence. "
        "The synthetic population is not a substitute for field data; it is a testbed for the "
        "instrument, the analytics and the ethics safeguards."
    )

    B.section("1.3", "Problem Statement")
    B.p(
        "The problem addressed by this project is the absence of an affordable, privacy-preserving "
        "and technically credible way to measure and reduce phishing susceptibility in a small or "
        "medium-sized organisation. Existing approaches tend to be either expensive commercial "
        "services with limited transparency, or campaign scripts that record clicks without "
        "closing the loop through coaching, assessment and individual risk communication. A "
        "usable solution must model the complete campaign lifecycle, record behavioural events "
        "without capturing secrets, convert those events into actionable aggregate and individual "
        "insight, and provide immediate education at the moment of failure."
    )

    B.section("1.4", "Aim and Objectives")
    B.p(
        "The aim of this project is to design, implement and evaluate a simulation-based framework "
        "for measuring and reducing phishing susceptibility in organisations. The objective is "
        "not to build another bulk mailer, but to build a defensible instrument that connects "
        "campaign design, behavioural telemetry, analytics, training and reporting in one "
        "auditable system. The specific objectives are:"
    )
    B.numbered([
        "To review the literature on phishing, human susceptibility, awareness training and "
        "simulation platforms, and to identify the requirements of a measurement-oriented system.",
        "To specify the functional and non-functional requirements, architecture, data model and "
        "security controls of such a system.",
        "To implement a working platform with a hardened administrative console, a campaign "
        "engine, per-recipient tracking, analytics, a coaching and quiz module, and exportable "
        "reporting.",
        "To validate the platform through automated unit, route, security and data-integrity "
        "tests, together with a performance and usability review.",
        "To evaluate behavioural outcomes in a controlled synthetic organisation and to derive "
        "practical implications for awareness programmes.",
        "To document the limitations of the evaluation and to define a realistic plan for a "
        "consented field deployment in the next semester.",
    ])

    B.section("1.5", "Scope and Boundaries")
    B.p(
        "The scope of the present work is a single-tenant web application that simulates an "
        "organisational email environment. It includes campaign authoring and lifecycle control, "
        "a catalogue of lures, a participant inbox and mail renderer, tokenised landing pages, "
        "event tracking, analytics, risk scoring, a training quiz, a printable report and CSV/JSON "
        f"exports. It is implemented using the Python standard library and SQLite "
        "and runs as a single process on commodity hardware."
    )
    B.p(
        "The following are explicitly out of scope for this semester: delivery of real email over "
        "SMTP, collection or storage of real credentials, integration with a production identity "
        "provider, mobile applications, generative artificial intelligence for lure creation, and "
        "formal certification against ISO 27001 or SOC 2. The evaluation uses a deterministic "
        "synthetic organisation of 24 employees and 104 simulated deliveries across five launched "
        "campaigns. Consequently, the reported percentages describe the behaviour of that "
        "synthetic cohort and the behaviour of the analytics pipeline; they are not population "
        "estimates for a real workforce. This boundary is deliberate and is revisited in the "
        "threats-to-validity discussion in Chapter 9."
    )

    B.section("1.6", "Contributions")
    B.p("The project makes six contributions to the practice of phishing-awareness engineering:")
    B.bullets([
        "**An integrated, dependency-free platform.** Campaign delivery, participant experience, "
        "analytics, training and reporting are combined in one Python package that can be audited "
        "end to end and deployed without a container or a cloud account.",
        "**Privacy-preserving telemetry.** Landing-page submissions record only the names of the "
        "fields that were filled, never their values. Session tokens are stored as hashes, and "
        "the public participant flow does not require an account.",
        "**A transparent composite risk model.** Click, submission, reporting and quiz performance "
        "are combined into a bounded score with explicit bands, so that the ranking can be "
        "explained to an employee rather than presented as an opaque vendor metric.",
        "**A closed training loop.** A failed simulation leads to an immediate coaching page and "
        "an eight-item quiz; the same M365 lure is repeated after training so that the change in "
        "behaviour can be observed on a like-for-like stimulus.",
        "**A reproducible evaluation artefact.** A fixed-seed synthetic organisation, a documented "
        "outcome model and an export of every reported number make the results reproducible by "
        "another student or reviewer.",
        "**An ethics-by-design demonstration.** The system proves that realistic behavioural "
        "measurement can be performed without sending real mail, collecting real secrets or "
        "exposing individuals to punitive consequences.",
    ])

    B.section("1.7", "Organisation of the Report")
    B.p(
        "Chapter 2 reviews the literature on phishing, human factors, awareness training and "
        "simulation platforms, and states the research gap. Chapter 3 presents the proposed system: "
        "design goals, architecture, requirements, data model, process design, use cases and threat "
        "model. Chapter 4 explains the research design, the simulation model, the metric definitions "
        "and the ethical framework. Chapter 5 describes the experimental setup, including the "
        "synthetic population, campaign schedule, lure catalogue and quiz instrument. Chapter 6 "
        "presents the implementation plan and the semester-wise schedule. Chapter 7 documents the "
        "implementation, including the security architecture and the principal screens. Chapter 8 "
        "reports testing and validation. Chapter 9 presents the results and discusses their "
        "meaning, limitations and threats to validity. Chapter 10 states the conclusions and the "
        "plan for future work. The appendices contain the route map, the quiz instrument and the "
        "export schema; the literature cited follows the IEEE numeric style."
    )


def chapter2(B: ReportBuilder):
    B.chapter(2, "Review of Literature")

    B.lead(
        "This chapter reviews the body of work that informs the design of the platform. It begins "
        "with definitions and the anatomy of a phishing attack, then examines why individuals "
        "respond to deceptive messages, what awareness interventions have been shown to work, and "
        "how simulation platforms measure behaviour. It closes with the ethical and legal "
        "constraints that shape any realistic study, and with the gap that this project addresses."
    )

    B.section("2.1", "Review Method")
    B.p(
        "Sources were identified through IEEE Xplore, the ACM Digital Library, ScienceDirect, "
        "Google Scholar and the public reports of security vendors, regulators and standards "
        "bodies. Search terms included combinations of phishing, social engineering, "
        "susceptibility, awareness training, phishing simulation, embedded training, security "
        "behaviour and risk score. The review prioritised peer-reviewed empirical studies and "
        "technical surveys published between 2006 and 2026, supplemented by current industry "
        "reports where up-to-date prevalence or cost data were required. Detection-only machine "
        "learning papers were included only where they illuminated the limits of technical "
        "filtering. The sources cited in this report span empirical studies, surveys, standards and current industry reports."
    )

    B.section("2.2", "Phishing: Definitions and Attack Lifecycle")
    B.p(
        "Phishing is a form of social engineering in which an attacker impersonates a trusted "
        "entity in order to induce a target to perform an action that benefits the attacker. "
        "Aleroud and Zhou define it as a fraudulent process that combines technical deception "
        f"with social persuasion to acquire sensitive information {B.cite('aleroud2017')}. Chiew "
        "et al. broaden the definition to include the delivery of malware and the manipulation of "
        f"financial transactions {B.cite('chiew2018')}. The common thread is that the message, "
        "not a software vulnerability, is the exploit."
    )
    B.p(
        "A phishing campaign can be described as a sequence of phases. **Planning and targeting** "
        "selects a population and gathers naming conventions, brands, suppliers and organisational "
        "relationships. **Lure construction** creates a pretext, a sender identity, a message body "
        "and a landing page that mimics a legitimate service. **Delivery** distributes the message "
        "through email, SMS, voice, QR codes or a collaboration platform. **Interaction** moves the "
        "target from message to link, attachment or reply. **Capture** records credentials, session "
        "cookies, payment details or malware execution. **Exploitation** uses the captured material "
        "to access accounts, move laterally, commit fraud or deploy ransomware. **Monetisation and "
        "clean-up** convert access into revenue and remove evidence. The platform in this project "
        "models the first five phases in a safe, instrumented form."
    )
    B.p(
        "Phishing is not a single technique. Bulk phishing sends a generic lure to many recipients; "
        "spear phishing tailors the message to a small group or individual; whaling targets senior "
        "executives; clone phishing copies a genuine message and replaces its links; thread "
        "hijacking continues an existing conversation from a compromised mailbox; business email "
        "compromise (BEC) impersonates an executive or supplier to authorise a payment; and "
        "callback phishing uses a benign-looking message to persuade the target to telephone a "
        "fraudulent help desk. Multi-channel attacks combine email with SMS or voice to increase "
        "credibility. Table 2.1 summarises the principal channels."
    )
    B.table("2.1", "Phishing channels and their characteristics",
            ["Channel", "Typical delivery", "Representative lure", "Why it works"],
            [
                ["Email", "Bulk or targeted message with link or attachment", "Password expiry, invoice, shared document", "Ubiquitous, asynchronous, easy to spoof"],
                ["Smishing", "SMS or messaging app", "Parcel delivery, bank alert, toll charge", "Personal device, short message, strong urgency"],
                ["Vishing", "Telephone or voice note", "Help-desk callback, fraud investigation", "Real-time pressure, authority of a live voice"],
                ["Quishing", "QR code in email or physical poster", "Parking fine, menu, MFA enrolment", "Opaque destination, mobile browser"],
                ["BEC", "Compromised or look-alike mailbox", "Payment instruction, gift-card request", "Internal authority, existing trust"],
                ["Adversary-in-the-middle", "Reverse-proxy landing page", "M365 or SSO login", "Relays password and OTP in real time"],
            ],
            widths=[2.6, 3.9, 4.3, 4.8], font=8.8, align=["l", "l", "l", "l"], bold_first=True)
    B.p(
        "The technical sophistication of the landing page matters, but the decisive variable is "
        "often the pretext. A message that arrives at the right moment, from a plausible sender, "
        "with a consequence that feels immediate, can succeed even when the target has been trained "
        "to look for spelling errors. This is why measurement must consider the whole campaign, "
        "not only whether a URL was clicked."
    )

    B.section("2.3", "Human Factors in Susceptibility")
    B.p(
        "Research on phishing susceptibility draws on dual-process theories of judgement. "
        "Kahneman distinguishes fast, automatic processing from slow, deliberate reasoning "
        f"{B.cite('kahneman2011')}. Most email is processed quickly: the reader classifies the "
        "message by sender, subject and visual familiarity, and acts on a heuristic rather than "
        "inspecting the underlying link. Cialdini's principles of influence — authority, scarcity, "
        "urgency, social proof, liking and commitment — describe the levers that a lure pulls "
        f"{B.cite('cialdini2009')}. A message from 'IT Security' that threatens account deletion "
        "within 24 hours combines authority, scarcity and loss aversion in a single sentence."
    )
    B.p(
        "Downs et al. found that users with more web experience relied on a wider range of cues, "
        "including URL structure and security indicators, whereas less experienced users relied on "
        f"surface features such as logos and sender names {B.cite('downs2006')}. Jagatic et al. "
        "showed that a message that appeared to come from a friend was far more effective than the "
        f"same message from a stranger {B.cite('jagatic2007')}. Vishwanath et al. integrated "
        "individual differences, information processing and involvement into a model in which "
        "heuristic processing and lack of systematic scrutiny increased vulnerability "
        f"{B.cite('vishwanath2011')}. Together these studies suggest that susceptibility is not a "
        "stable personality trait but a context-dependent outcome of cue availability, cognitive "
        "load and prior experience."
    )
    B.p(
        "Organisational context adds further variation. Sales and finance staff handle external "
        "requests, invoices and payment approvals as part of their daily work, so a convincing "
        "business message is congruent with their task. IT staff encounter security warnings "
        "constantly and may be either more sceptical or more habituated. Junior employees may be "
        "reluctant to question an executive instruction; senior employees may be less accustomed "
        "to scrutiny. Workload, fatigue, device, time of day and the presence of a reporting "
        "culture all influence the outcome. A measurement platform should therefore report results "
        "by department and by lure, not only as a single organisational average."
    )

    B.section("2.4", "Awareness Interventions")
    B.p(
        "Awareness interventions range from posters and annual e-learning to embedded training, "
        "serious games and simulated phishing with immediate feedback. Kumaraguru et al. evaluated "
        "an embedded training email that taught users at the moment they encountered a phishing "
        f"message; participants improved their detection performance relative to a control group "
        f"{B.cite('kumaraguru2007', 'kumaraguru2009')}. A later longitudinal study found that "
        "repeated training and feedback were needed to sustain the effect, and that retention "
        f"declined over time {B.cite('kumaraguru2010')}. Caputo et al. explored embedded training "
        "in a spear-phishing exercise and highlighted the tension between realistic deception and "
        f"the ethical obligation to inform participants {B.cite('caputo2014')}."
    )
    B.p(
        "Wash and Cooper examined what makes training credible. Employees valued stories from "
        "people like themselves and concrete examples over abstract warnings; generic facts and "
        f"fear appeals were less persuasive {B.cite('wash2018')}. This finding supports a design in "
        "which the coaching page uses the exact lure that the participant has just encountered, "
        "explains the specific red flags in that message, and avoids blaming the individual. The "
        "teachable moment is strongest immediately after the action, when the consequence is "
        "concrete and the message is still on screen."
    )
    B.p(
        "Simulation-based training has become the dominant industry model. A campaign is sent, "
        "behaviour is recorded, and users who fail are enrolled in training. The approach has "
        "obvious advantages: it measures behaviour rather than self-reported knowledge, and it can "
        "be repeated. It also has known weaknesses. Click rates are sensitive to lure quality, "
        "audience and timing; repeated simulations can breed habituation or resentment; and a "
        "focus on catching individuals can discourage reporting. The design in this project "
        "therefore treats reporting as a first-class positive behaviour and couples every failure "
        "with immediate, non-punitive coaching."
    )

    B.section("2.5", "Simulation Platforms and Measurement")
    B.p(
        "A phishing simulation platform must perform five functions: author a credible lure, "
        "deliver it to a defined audience, track per-recipient interaction, present a landing page, "
        "and report the results. GoPhish provides these functions in a single Go binary with a web "
        f"console, campaign scheduling, templates and landing pages {B.cite('gophish')}. King "
        "Phisher offers a client/server architecture, campaign management and a template library "
        f"{B.cite('kingphisher')}. Both are mature and widely used, but neither includes a built-in "
        "training curriculum, a risk score or an integrated printable report; those functions are "
        "left to separate tools or manual analysis."
    )
    B.p(
        "Commercial platforms such as KnowBe4, Proofpoint and Cofense add large content libraries, "
        "automated enrolment, benchmarking and reporting. They reduce operational effort but "
        "introduce recurring cost, data-processing agreements and a dependency on the vendor's "
        "definition of risk. For a college or a small enterprise, the total cost of ownership and "
        "the difficulty of explaining the metric to employees can outweigh the convenience. The "
        "platform described in this report is deliberately narrower: it implements the core "
        "measurement loop, keeps the data local, and exposes the formula behind every number."
    )
    B.p(
        "Measurement itself is contested. Open rates are unreliable because mail clients block "
        "tracking pixels or proxy images. Click rates depend on whether a click on a harmless "
        "landing page is counted as a failure, and submission rates depend on whether the landing "
        "page actually requests credentials. Reporting rates depend on how easy it is to report and "
        "whether reporters are praised or punished. Time-to-click and repeat-click measures add "
        "useful context. A credible report should define each metric operationally, state the "
        "denominator, and avoid comparing campaigns that differ in audience or difficulty. Table "
        "2.2 compares representative platforms and studies."
    )
    B.table("2.2", "Comparison of representative platforms and studies",
            ["Approach", "Primary focus", "Strengths", "Limitations"],
            [
                ["GoPhish", "Campaign delivery", "Lightweight, open source, templates, landing pages", "No training loop or risk model"],
                ["King Phisher", "Campaign delivery", "Client/server, scheduling, extensible", "Operational setup; analytics external"],
                ["KnowBe4 / Proofpoint", "Managed awareness", "Content library, automation, benchmarking", "Cost, vendor data processing, opaque scoring"],
                ["Kumaraguru et al.", "Embedded training", "Teachable moment, empirical evaluation", "Email client dependency; retention decay"],
                ["Caputo et al.", "Spear-phishing exercise", "Realistic target group; ethics discussion", "Small scale; limited platform reuse"],
                ["This work", "Measurement and training loop", "Self-hosted, private, integrated, reproducible", "Synthetic pilot; no SMTP; small cohort"],
            ],
            widths=[3.0, 3.2, 4.8, 4.6], font=8.8, align=["l", "l", "l", "l"], bold_first=True)

    B.section("2.6", "Technical Controls and the Human Layer")
    B.p(
        "Email authentication is the first line of defence. SPF authorises sending hosts, DKIM "
        "cryptographically signs messages, and DMARC tells the receiver what to do when alignment "
        "fails. Together they make exact-domain spoofing harder, but they do not prevent look-alike "
        "domains, compromised legitimate accounts or messages sent through a permitted bulk "
        f"provider {B.cite('gupta2018')}. Link rewriting and detonation sandboxes can block known "
        "malicious URLs, but attackers rotate domains and abuse trusted file-sharing services. "
        "Multi-factor authentication raises the cost of credential theft, yet push-notification "
        "fatigue and adversary-in-the-middle proxies can defeat one-time codes "
        f"{B.cite('nist63b', 'msddr2024')}. Phishing-resistant authenticators such as FIDO2 security "
        "keys address the proxy problem, but deployment is uneven."
    )
    B.p(
        "The implication is not that technical controls are futile, but that they shift the "
        "residual risk to the person. A defence-in-depth strategy combines prevention, detection "
        "and response: filtering and authentication reduce volume; endpoint and identity controls "
        "limit the consequences of a click; and a fast, blameless reporting channel turns employees "
        "into sensors. The platform in this project is positioned at the measurement and response "
        "end of that chain. It does not replace a mail gateway or an endpoint agent; it provides "
        "the evidence needed to target them."
    )

    B.section("2.7", "Ethics and Legal Considerations")
    B.p(
        "Phishing simulations involve deception, even when the deception is benign. The ethical "
        "literature converges on several safeguards: informed consent at the programme level, a "
        "clear statement of purpose, an opt-out for vulnerable staff, immediate debriefing after "
        "the exercise, no collection of real secrets, and a commitment not to use individual "
        f"results for discipline {B.cite('caputo2014', 'nist80050')}. The General Data Protection "
        "Regulation in the European Union and the Digital Personal Data Protection Act in India "
        f"impose additional duties of purpose limitation, minimisation and security {B.cite('gdpr', 'dpdp')}. "
        "Employee monitoring law and works-council agreements may apply in some jurisdictions."
    )
    B.p(
        "The platform addresses these constraints by design rather than by policy alone. It never "
        "sends real email, so no external recipient can be deceived. It never stores the values "
        "entered into a landing page; it records only which field names were submitted. It uses "
        "fictional employees and a fictional company in the demonstration dataset. It displays a "
        "persistent banner stating that the environment is a simulation. It gives the participant "
        "immediate feedback and a route to report the message. These choices make the artefact "
        "suitable for a college laboratory and provide a template for a consented field deployment."
    )

    B.section("2.8", "Research Gap")
    B.p(
        "The literature establishes that human susceptibility is context-dependent, that embedded "
        "feedback is more effective than annual awareness, and that simulation is a useful "
        "measurement method. It also reveals three gaps. First, most open-source tools stop at "
        "campaign delivery; training, risk scoring and reporting are separate. Second, most studies "
        "evaluate a training intervention rather than the measurement instrument, so the "
        "reproducibility of the analytics is rarely discussed. Third, small organisations lack a "
        "deployable artefact that respects privacy by design and can be operated without a cloud "
        "subscription."
    )
    B.p(
        "This project addresses the gap by building an integrated, self-hosted platform and by "
        "evaluating it on a transparent synthetic cohort. The contribution is not a new theory of "
        "phishing; it is an engineering artefact and an evaluation method that make the theory "
        "operational for a small team. The next chapter turns the requirements implied by this "
        "review into a system design."
    )

    B.section("2.9", "Summary")
    B.p(
        "Phishing exploits human judgement through authority, urgency and familiarity. Technical "
        "controls reduce volume and consequence but leave a residual human decision. Awareness "
        "training works best when it is concrete, timely and repeated, and simulation is the most "
        "direct way to measure behaviour. Existing platforms are either commercial and opaque or "
        "open and incomplete. The gap is an integrated, privacy-preserving, reproducible platform "
        "that connects campaign delivery, analytics, coaching and reporting. Chapters 3 to 8 "
        "describe how that platform was designed, built and tested."
    )


def chapter3(B: ReportBuilder):
    B.chapter(3, "Proposed System")

    B.lead(
        "This chapter specifies the proposed system. It states the design goals, presents the "
        "architecture and the data model, derives the functional and non-functional requirements, "
        "describes the principal processes and use cases, and analyses the threats that the "
        "platform must resist. The design is intentionally modest in its dependencies and "
        "aggressive in its auditability: every number shown to an administrator should be "
        "traceable to an event in the database."
    )

    B.section("3.1", "System Overview")
    B.p(
        "PhishStudy is a server-rendered web application with two audiences. The **administrator** "
        "signs in to a console, creates lures, defines an audience, launches a campaign, monitors "
        "the funnel and reads the analytics. The **participant** receives a simulated message in a "
        "web inbox, opens it, follows a tokenised link, sees a landing page, and either submits the "
        "form, reports the message or leaves. A submission leads to a coaching page that explains "
        "the red flags in that exact message and offers an eight-item quiz. The administrator can "
        "export the results, print a report and review the audit log."
    )
    B.p(
        "The system is organised into seven modules: identity and access, campaign management, lure "
        "management, people and consent, participant experience, analytics and training, and "
        "reporting. A small routing layer maps HTTP requests to views, and a persistence layer "
        "wraps SQLite. There is no JavaScript framework, no external CSS, no third-party analytics "
        "and no outbound network call at runtime. This makes the system easy to audit and easy to "
        "run on a laptop or a departmental server."
    )

    B.section("3.2", "Design Goals")
    B.p("The design is guided by eight goals, derived from the literature review and the constraints "
        "of a college project:")
    B.bullets([
        "**Safety before realism.** No real email, no real credentials and no external target. "
        "Realism is achieved through the quality of the simulated message, not through live delivery.",
        "**Measurability.** Every participant action is stored as a timestamped event with a "
        "well-defined denominator, so that rates can be recomputed and audited.",
        "**Privacy by design.** The minimum data needed for the metric is collected. Submitted "
        "values are discarded; only field names are retained.",
        "**Immediate feedback.** A failure is followed by an explanation and a short assessment, "
        "not by a punitive email to a manager.",
        "**Operational simplicity.** A single Python process, a single SQLite file and no external "
        "services. A new administrator can be productive in minutes.",
        "**Auditability.** Authentication events, campaign changes and exports are written to an "
        "append-only audit log with actor, action, detail and timestamp.",
        "**Extensibility.** Lures, audiences, quiz questions and metrics are data, not hard-coded "
        "branches, so the platform can grow without a rewrite.",
        "**Accessibility and clarity.** Semantic HTML, readable contrast, large touch targets and "
        "a layout that works on a phone, because participants may open the message on a mobile "
        "device.",
    ])

    B.section("3.3", "System Architecture")
    B.p(
        "Figure 3.1 shows the layered architecture. The presentation layer renders HTML templates "
        "and a small design system. The application layer contains the HTTP server, routing, "
        "authentication, CSRF checks and request handlers. The domain layer contains campaign "
        "lifecycle rules, analytics functions, risk scoring and quiz logic. The persistence layer "
        "is SQLite in WAL mode with foreign keys enabled. A cross-cutting security module provides "
        "password hashing, session tokens, CSRF tokens and login throttling."
    )
    B.figure("3.1", "docs/figures/architecture.png",
             "Layered architecture of PhishStudy. Every module reaches the database through the "
             "persistence layer, and every request passes through the security module.", width=14.2)
    B.p(
        "The request lifecycle is deliberately simple. The server parses the request, opens a "
        "short-lived database connection, resolves the session cookie, enforces the public/protected "
        "route boundary, validates the CSRF token for state-changing requests, dispatches to a view, "
        "renders HTML and closes the connection. There is no ORM and no connection pool. SQLite's "
        "write-ahead log allows concurrent readers while a campaign is being updated, which is "
        "sufficient for the expected load of a departmental deployment."
    )

    B.section("3.4", "Functional Requirements")
    B.p(
        "The functional requirements were derived from the campaign lifecycle and from the "
        "questions an administrator must answer. They are numbered for traceability to the tests in "
        "Chapter 8. Table 3.1 lists the requirements and their priority; 'M' denotes mandatory for "
        "the present release and 'S' denotes should-have."
    )
    B.table("3.1", "Functional requirements",
            ["ID", "Requirement", "Priority"],
            [
                ["FR-01", "Authenticate administrators with a username and password; lock out repeated failures.", "M"],
                ["FR-02", "Create, edit, duplicate, activate and deactivate lure templates.", "M"],
                ["FR-03", "Define an audience by department and preview the recipient count.", "M"],
                ["FR-04", "Create a campaign in Draft and move it through Scheduled, Active, Paused, Completed and Archived.", "M"],
                ["FR-05", "Generate a unique, unguessable tracking token for every recipient.", "M"],
                ["FR-06", "Render a simulated inbox and a faithful HTML mail view for each token.", "M"],
                ["FR-07", "Record open, click, submit and report events with timestamps.", "M"],
                ["FR-08", "Discard submitted values and retain only the field names.", "M"],
                ["FR-09", "Show a coaching page with the red flags of the exact lure after submission.", "M"],
                ["FR-10", "Provide an eight-item quiz with scoring, feedback and attempt history.", "M"],
                ["FR-11", "Compute funnel, campaign, department, lure and difficulty statistics.", "M"],
                ["FR-12", "Compute a bounded individual risk score and band.", "M"],
                ["FR-13", "Export the results as CSV and JSON and render a printable report.", "M"],
                ["FR-14", "Maintain an audit log of authentication, campaign and export events.", "M"],
                ["FR-15", "Allow an administrator to reset the demonstration dataset.", "S"],
                ["FR-16", "Show a persistent simulation banner on every page.", "M"],
                ["FR-17", "Support a participant reporting flow with a confirmation page.", "M"],
                ["FR-18", "Provide a settings page for organisation name, domain and pass mark.", "S"],
            ],
            widths=[1.5, 12.3, 1.8], font=8.8, align=["c", "l", "c"])

    B.section("3.5", "Non-Functional Requirements")
    B.p(
        "Non-functional requirements constrain how the system behaves. They are especially important "
        "for a security product, because a weak administrative console would undermine the credibility "
        "of the measurement. Table 3.2 lists the requirements and the design response."
    )
    B.table("3.2", "Non-functional requirements and design response",
            ["ID", "Quality attribute", "Requirement", "Design response"],
            [
                ["NFR-01", "Security", "Resist credential stuffing, session theft, CSRF and XSS.", "PBKDF2-SHA256, hashed session tokens, per-session CSRF, output escaping, CSP."],
                ["NFR-02", "Privacy", "Collect the minimum behavioural data.", "No value capture, no third-party scripts, aggregate exports."],
                ["NFR-03", "Performance", "Interactive pages under 200 ms at departmental scale.", "Indexed queries, WAL, server-side aggregation; measured in Chapter 8."],
                ["NFR-04", "Portability", "Run on Linux, macOS or Windows with Python 3.11+.", "Standard library only; SQLite file; no native extensions."],
                ["NFR-05", "Reliability", "Survive restarts without losing committed events.", "WAL journal, foreign keys, explicit commits, idempotent timestamps."],
                ["NFR-06", "Usability", "A new administrator can launch a campaign without training.", "Guided forms, inline help, empty states, consistent navigation."],
                ["NFR-07", "Accessibility", "Readable on mobile and with keyboard navigation.", "Semantic HTML, focus styles, contrast, responsive layout."],
                ["NFR-08", "Maintainability", "Small, testable modules with no hidden coupling.", "Package split by concern; 24 automated tests; typed helpers."],
                ["NFR-09", "Auditability", "Reconstruct who changed what and when.", "Append-only audit table; timestamps in local time; actor field."],
                ["NFR-10", "Scalability", "Support at least 1,000 employees and 5,000 targets.", "Set-based SQL, indexes, pagination; benchmark in Chapter 8."],
            ],
            widths=[1.5, 2.6, 5.2, 6.3], font=8.6, align=["c", "l", "l", "l"])

    B.section("3.6", "Data Model")
    B.p(
        "The data model has nine tables. **admins** stores the console account and its password "
        "hash. **sessions** stores a hash of each session token, the CSRF secret, a flash message "
        "and an expiry time. **employees** stores the fictional population, department, designation, "
        "active flag and consent flag. **templates** stores the lure: sender, subject, body, landing "
        "form, difficulty, category and red flags. **campaigns** stores the lifecycle state, phase, "
        "audience, schedule and timestamps. **targets** is the join between a campaign and an "
        "employee and carries the unique token and the four behavioural timestamps. **quiz_attempts** "
        "stores the score, total, chosen options and time. **audit** stores actor, action, detail and "
        "time. **settings** stores organisation-level configuration."
    )
    B.figure("3.2", "docs/figures/er.png",
             "Entity–relationship diagram. Foreign keys enforce referential integrity; deleting an "
             "employee cascades to targets and nulls quiz references.", width=15.6)
    B.p(
        "Two design choices deserve explanation. First, the behavioural events are nullable "
        "timestamps on the target row rather than separate event rows. This makes the funnel query "
        "a set of `COUNT` expressions over one table, which is fast and easy to audit. The trade-off "
        "is that the model cannot represent repeated clicks on the same target; for the present "
        "scope, first-event semantics are sufficient and are stated in the metric definitions. "
        "Second, the submitted field names are stored as a JSON array, while the values are never "
        "written. This preserves the ability to say 'the password field was filled' without "
        "retaining a secret."
    )

    B.section("3.7", "Process Design")
    B.p(
        "Figure 3.3 is a level-0 data-flow diagram. The participant exchanges simulated mail and "
        "event notifications with the campaign engine. The administrator manages campaigns and "
        "audiences. The campaign engine writes target events, the analytics process reads and "
        "aggregates them, and the training process stores quiz attempts and returns coaching. The "
        "three data stores correspond to the target events, the campaign definitions and the quiz "
        "history."
    )
    B.figure("3.3", "docs/figures/dfd.png",
             "Level-0 data-flow diagram. Events flow from the participant to the campaign engine and "
             "thence to analytics and training.", width=15.6)
    B.p(
        "The campaign lifecycle is a small state machine. A campaign begins in **Draft**, moves to "
        "**Scheduled** when a launch time is set, becomes **Active** when launched, may be **Paused** "
        "and resumed, and ends in **Completed** or **Archived**. A scheduled campaign materialises "
        "its targets at launch, which freezes the audience and guarantees that the denominator "
        "cannot change after the first event. Pausing stops new sends but leaves existing tokens "
        "valid, so a participant who opens an old message still sees a coherent page. These rules "
        "are enforced in the service layer, not only in the user interface."
    )
    B.figure("3.4", "docs/figures/workflow.png",
             "Campaign lifecycle. Targets are materialised at launch so that the denominator is "
             "stable for the whole campaign.", width=14.6)

    B.section("3.8", "Use Cases")
    B.p(
        "Figure 3.5 shows the actors and the principal use cases. The administrator manages lures, "
        "people, campaigns, analytics, training and settings. The participant opens a message, "
        "clicks, submits, reports, reads coaching and takes the quiz. The system actor performs "
        "scheduled launches, token generation and aggregation."
    )
    B.figure("3.5", "docs/figures/usecase.png",
             "Use-case diagram for the administrator, the participant and the scheduled system actor.",
             width=14.4)
    B.p("Three use cases are central to the contribution and are described below.")
    B.sub("3.8.1", "Launch a campaign")
    B.p(
        "**Precondition:** the administrator is authenticated and at least one active lure and one "
        "employee exist. **Main flow:** the administrator selects a lure, names the campaign, chooses "
        "a phase and audience, reviews the recipient count, and saves. The campaign is created in "
        "Draft. On launch, the system materialises one target per recipient with a random token, "
        "records the launch time, changes the status to Active and writes an audit entry. "
        "**Postcondition:** every recipient has exactly one token and the denominator is fixed. "
        "**Exception:** an empty audience is rejected with a validation message."
    )
    B.sub("3.8.2", "Respond to a simulated message")
    B.p(
        "**Precondition:** the participant holds a valid token. **Main flow:** the participant opens "
        "the mail view, which records the first open. A click records the first click and renders the "
        "landing page. A submission records the first submit, discards the values, stores the field "
        "names and redirects to coaching. A report records the first report and shows a confirmation. "
        "**Postcondition:** the event is timestamped once; repeated requests are idempotent. "
        "**Exception:** an unknown token returns a neutral 404 page without revealing whether the "
        "token ever existed."
    )
    B.sub("3.8.3", "Analyse and export results")
    B.p(
        "**Precondition:** the administrator is authenticated. **Main flow:** the analytics view "
        "aggregates targets by campaign, department, difficulty and template; the risk view ranks "
        "employees; the report view renders a printable summary; the export endpoints stream CSV and "
        "JSON. **Postcondition:** the numbers on screen and in the export are produced by the same "
        "analytics functions, so they cannot drift. **Exception:** an export request without a "
        "session is redirected to the login page."
    )

    B.section("3.9", "Threat Model and Safeguards")
    B.p(
        "The platform is itself a security-sensitive application: it holds behavioural data and an "
        "administrative session that can launch campaigns. A lightweight STRIDE analysis was used to "
        "identify threats and to choose proportionate controls (Table 3.3). The analysis assumes a "
        "network attacker, a malicious participant and an authorised administrator who makes a "
        "mistake; it does not assume a compromised host or a compromised Python runtime."
    )
    B.table("3.3", "STRIDE threat model and safeguards",
            ["Threat", "Example", "Safeguard"],
            [
                ["Spoofing", "Credential stuffing against the admin login", "PBKDF2-SHA256 with 260,000 iterations; login throttle; generic error message"],
                ["Tampering", "Forged campaign status or target timestamps", "Server-side state machine; parameterised SQL; CSRF token on every state change"],
                ["Repudiation", "An administrator denies launching a campaign", "Append-only audit log with actor, action, detail and timestamp"],
                ["Information disclosure", "Session theft or export leakage", "HttpOnly, SameSite=Lax cookie; hashed session tokens; no values stored; access-controlled exports"],
                ["Denial of service", "Repeated login or quiz submissions", "Per-IP and per-account throttle; bounded request body; short transactions"],
                ["Elevation of privilege", "Participant reaches admin routes", "Central protected-route check; no role parameter in the session; 404 on unknown tokens"],
            ],
            widths=[2.7, 5.6, 7.3], font=8.8, align=["l", "l", "l"], bold_first=True)

    B.section("3.10", "Design Trade-offs and Summary")
    B.p(
        "Every design choice excludes alternatives. Using the standard library instead of a web "
        "framework keeps the dependency surface at zero, but it means writing routing, sessions and "
        "CSRF handling by hand; the tests in Chapter 8 are the compensation. Server-rendered HTML "
        "instead of a single-page application keeps the participant experience fast and accessible, "
        "but it limits rich interactivity. SQLite instead of PostgreSQL makes deployment trivial, "
        "but it constrains multi-writer concurrency. A synthetic cohort instead of real employees "
        "makes the study ethical and reproducible, but it limits external validity. These trade-offs "
        "are stated here so that the evaluation in Chapters 8 and 9 can be read against the intended "
        "design rather than against an unstated ideal."
    )
    B.p(
        "In summary, the proposed system is a layered, dependency-free web application that connects "
        "campaign delivery, behavioural telemetry, analytics, coaching and reporting. Its requirements "
        "are traceable, its data model is normalised, its lifecycle is explicit, and its threat model "
        "is matched by concrete controls. The next chapter explains the methodology used to evaluate "
        "it and the simulation model that generates the synthetic cohort."
    )
