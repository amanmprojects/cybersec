#!/usr/bin/env python3
"""PhishStudy — simulated phishing campaign & awareness platform.

RUN
    python3 app.py                 # http://127.0.0.1:8000
    python3 app.py --port 8080
    python3 app.py reset           # restore the seeded demo dataset
    python3 app.py report          # print a text summary of the results

Zero third-party dependencies: Python standard library only.
No real email is sent and no real credential is ever collected.
"""
from __future__ import annotations

import argparse
import json
import sys

from phishstudy import __version__


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="app.py", description="PhishStudy 2.0")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--db", default=None, help="SQLite file (default: phishing.db)")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--version", action="version", version=f"PhishStudy {__version__}")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("serve", help="run the web application (default)")
    sub.add_parser("reset", help="delete and reseed the database")
    sub.add_parser("report", help="print a text summary")
    export = sub.add_parser("export", help="write the analytics snapshot")
    export.add_argument("path", nargs="?", default="results.json")
    args = parser.parse_args(argv)

    from phishstudy.server import run

    if args.command == "reset":
        from phishstudy.db import reset_db
        reset_db(args.db)
        print("Database reset to the seeded demonstration dataset.")
        return 0

    if args.command in ("report", "export"):
        from phishstudy.analytics import results_snapshot
        from phishstudy.db import connect, init_db
        init_db(args.db)
        snap = results_snapshot(connect(args.db))
        if args.command == "export":
            with open(args.path, "w", encoding="utf-8") as fh:
                json.dump(snap, fh, indent=2)
            print(f"Wrote {args.path}")
            return 0
        _print_report(snap)
        return 0

    run(args.host, args.port, db_path=args.db, verbose=args.verbose)
    return 0


def _print_report(snap: dict) -> None:
    ov = snap["overview"]
    print(f"PhishStudy results — generated {snap['generated_at']}")
    print("=" * 62)
    print(f"Recipients {ov['sent']}  ·  click {ov['click_rate']}%  ·  "
          f"submitted {ov['submit_rate']}%  ·  reported {ov['report_rate']}%")
    print("\nCampaigns")
    for c in snap["campaigns"]:
        print(f"  {c['name'][:40]:42} sent={c['sent']:3} click={c['click_rate']:5}% "
              f"phish={c['submit_rate']:5}% report={c['report_rate']:5}%")
    print("\nDepartments")
    for d in snap["departments"]:
        print(f"  {d['department']:12} sent={d['sent']:3} phish={d['submit_rate']:5}% report={d['report_rate']:5}%")
    print("\nQuiz")
    print(f"  pre  {snap['quiz']['pre']['average']}/{snap['quiz_question_count']} "
          f"({snap['quiz']['pre']['pass_rate']}% pass)")
    print(f"  post {snap['quiz']['post']['average']}/{snap['quiz_question_count']} "
          f"({snap['quiz']['post']['pass_rate']}% pass)")


if __name__ == "__main__":
    sys.exit(main())
