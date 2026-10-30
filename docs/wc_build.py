#!/usr/bin/env python3
"""Build the project report with WordCraft and export the PDF.

    uv run --with python-docx python docs/wc_build.py

Two passes: the first builds the document with placeholder page numbers in the
index and in the lists of figures and tables, exports the PDF with WordCraft,
reads back the page every heading and caption lands on, and the second rebuilds
with the real numbers.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

from wc_builder import TABLE_TOKEN, WcBuilder, cm  # noqa: E402
from report_ch1_3 import chapter1, chapter2, chapter3  # noqa: E402
from report_ch4_6 import chapter4, chapter5, chapter6  # noqa: E402
from report_ch7_10 import chapter7, chapter8, chapter9, chapter10  # noqa: E402

OUT_DOCX = ROOT / "Phishing_Susceptibility_Study_Report.docx"
OUT_PDF = ROOT / "Phishing_Susceptibility_Study_Report.pdf"
LOGO = HERE / "figures" / "logo.png"

TITLE = "PhishStudy: A Simulation Platform for Measuring and Reducing Phishing Susceptibility"
NAMES = [
    "Shetty Vikyath Vishwanath (Roll No: 5)",
    "Mehtar Aman Yasin (Roll No: 6)",
    "Singh Yash Anil (Roll No: 7)",
    "Singh Abhishek Shailesh (Roll No: 8)",
]
ABSTRACT = (
    "Phishing remains one of the most effective ways to breach an organisation. Technical controls "
    "such as sender authentication, filtering and multi-factor authentication reduce volume and "
    "consequence, but the final decision is still made by a person under time pressure. This project "
    "designs, implements and evaluates PhishStudy, a self-hosted simulation platform that measures "
    "and helps reduce phishing susceptibility. The platform models the complete campaign lifecycle, "
    "issues a unique token to every recipient, records open, click, submit and report events without "
    "storing submitted values, computes funnel, department, lure and risk metrics, and closes the "
    "loop with immediate coaching and an eight-item awareness quiz. It is implemented using the "
    "Python standard library and SQLite, with a hardened administrative console that uses "
    "PBKDF2-SHA256 password hashing, hashed session tokens, per-session CSRF protection, login "
    "throttling, output escaping and an audit log. The evaluation uses a deterministic synthetic "
    "organisation of 24 employees in six departments, six lures and five launched campaigns "
    "(104 simulated deliveries). The platform records a 43.3% click rate, a 22.1% submission rate "
    "and a 19.2% reporting rate. Sales and Finance are the most exposed departments, while IT "
    "records no clicks and a 62.5% reporting rate. On the repeated M365 lure, the post-training "
    "campaign records an 8.3% submission rate and a 50.0% reporting rate against a baseline of "
    "33.3% and 8.3%, and the quiz mean rises from 3.25/8 to 6.21/8. The synthetic study validates "
    "the measurement pipeline and the analytics; it does not establish causal effects in a real "
    "workforce. The report documents the design, implementation, 24 automated tests, nine security "
    "probes, performance measurements, limitations and a plan for a consented field pilot."
)
DECLARATION = (
    "We declare that this written submission represents our ideas in our own words and where "
    "other’s ideas or words have been included, we have adequately cited and referenced the "
    "original sources. We also declare that we have adhered to all principles of academic honesty "
    "and integrity and have not misrepresented or fabricated or falsified any idea/data/fact/source "
    "in my submission. We understand that any violation of the above will be cause for disciplinary "
    "action by the Institute and can also evoke penal action from the sources which have thus not "
    "been properly cited or from whom proper permission has not been taken when needed."
)


# --------------------------------------------------------------------- commands
def style_commands(B: WcBuilder) -> None:
    """Define the Word styles the report uses."""
    B.cmd("styles.modify", style="Normal",
          chr={"font": "Times New Roman", "size": 12, "color": "000000"},
          para={"align": "justify", "lineSpacing": {"rule": "multiple", "value": 1.5},
                "spaceBefore": 0, "spaceAfter": 8, "widowControl": True})
    B.cmd("styles.modify", style="Heading 1",
          chr={"font": "Times New Roman", "size": 16, "bold": True, "color": "000000"},
          para={"align": "left", "lineSpacing": {"rule": "multiple", "value": 1.5},
                "spaceBefore": 16, "spaceAfter": 8, "keepNext": True,
                "pageBreakBefore": True, "outlineLevel": 0})
    B.cmd("styles.modify", style="Heading 2",
          chr={"font": "Times New Roman", "size": 14, "bold": True, "color": "000000"},
          para={"align": "left", "lineSpacing": {"rule": "multiple", "value": 1.5},
                "spaceBefore": 12, "spaceAfter": 6, "keepNext": True, "outlineLevel": 1})
    B.cmd("styles.modify", style="Heading 3",
          chr={"font": "Times New Roman", "size": 12, "bold": True, "color": "000000"},
          para={"align": "left", "lineSpacing": {"rule": "multiple", "value": 1.5},
                "spaceBefore": 8, "spaceAfter": 4, "keepNext": True, "outlineLevel": 2})
    B.cmd("styles.modify", style="Caption",
          chr={"font": "Times New Roman", "size": 10, "italic": True, "color": "000000"},
          para={"align": "left", "lineSpacing": {"rule": "multiple", "value": 1.0},
                "spaceBefore": 4, "spaceAfter": 12})
    B.cmd("styles.create", name="Front Heading", basedOn="Heading 1")
    B.cmd("styles.modify", style="Front Heading",
          chr={"font": "Times New Roman", "size": 16, "bold": True, "color": "000000"},
          para={"align": "center", "lineSpacing": {"rule": "multiple", "value": 1.5},
                "spaceBefore": 0, "spaceAfter": 18, "keepNext": True,
                "pageBreakBefore": False})


def page_setup(B: WcBuilder, title_page: bool = True) -> None:
    B.cmd("layout.pageSetup", section={
        "pageW": cm(21.0), "pageH": cm(29.7),
        "marginTop": cm(2.54), "marginBottom": cm(2.54),
        "marginLeft": cm(2.54), "marginRight": cm(2.54),
        "header": cm(1.27), "footer": cm(1.27),
        "titlePage": title_page,
    })


def centred(B: WcBuilder, text: str, size: float, bold: bool = False,
            before: float = 0, after: float = 8, italic: bool = False) -> None:
    B._style("Normal")
    B._char(size=size, bold=bold, italic=italic)
    B._para(align="center", spacing=1.0, before=before, after=after)
    B._text(text, bold=bold, italic=italic, size=size)
    B._new_paragraph()


def cover(B: WcBuilder) -> None:
    B._style("Normal")
    B._char(size=12, bold=False, italic=False)
    B._para(align="center", spacing=1.0, before=0, after=10)
    if LOGO.exists():
        B.cmd("insert.picture", path=str(LOGO), width=cm(2.6))
    B._new_paragraph()
    centred(B, TITLE, 22, bold=True, before=10, after=10)
    centred(B, "submitted in fulfilment of the requirements", 13.5, after=0)
    centred(B, "for Major Project-1, Semester VII", 13.5, after=10)
    centred(B, "BE Honors", 20, bold=True, after=16)
    B._style("Normal")
    B._char(size=15, bold=False, italic=False)
    B._para(align="right", spacing=1.0, before=0, after=10)
    B._text("By", size=15)
    B._new_paragraph()
    for i, name in enumerate(NAMES):
        centred(B, name, 15, bold=True, before=0 if i else 8, after=2)
    B._style("Normal")
    B._char(size=15, bold=True, italic=False)
    B._para(align="right", spacing=1.0, before=16, after=2)
    B._text("Under the guidance of", bold=True, size=15)
    B._new_paragraph()
    B._style("Normal")
    B._char(size=15, bold=True, italic=False)
    B._para(align="right", spacing=1.0, before=0, after=12)
    B._text("Dr. Yogita Shelar", bold=True, size=15)
    B._new_paragraph()
    centred(B, "Department of Information Technology", 16, bold=True, before=6, after=6)
    centred(B, "Vidyavardhini’s College of Engineering & Technology, Vasai (W)", 16,
            bold=True, after=2)
    centred(B, "(Affiliated with University of Mumbai)", 14, after=12)
    centred(B, "(2026-2027)", 14, bold=True, after=0)


def front_heading(B: WcBuilder, title: str) -> None:
    B._style("Front Heading")
    B._char(size=16, bold=True, italic=False)
    B._para(align="center", spacing=1.5, before=0, after=18, keep=True)
    B._text(title)
    B._new_paragraph()


def declaration(B: WcBuilder) -> None:
    front_heading(B, "Declaration")
    B.p(DECLARATION)
    for name in NAMES:
        B.rule(7.5, align="right", before=18, after=0)
        B._style("Normal")
        B._char(size=12, bold=False, italic=False)
        B._para(align="right", spacing=1.0, before=2, after=0)
        B._text(name, size=12)
        B._new_paragraph()
    B._style("Normal")
    B._char(size=12, bold=False, italic=False)
    B._para(align="left", spacing=1.0, before=20, after=0)
    B._text("Date: 21 October 2026", size=12)
    B._new_paragraph()


def abstract(B: WcBuilder) -> None:
    front_heading(B, "Abstract")
    B.p(ABSTRACT)


def index_table(B: WcBuilder, outline: list[tuple[str, str, str]],
                pages: dict[str, int]) -> None:
    front_heading(B, "Index")
    rows = []
    for kind, number, title in outline:
        key = f"{kind}:{number}"
        if kind == "chapter":
            rows.append([f"Chapter {number}", title, str(pages.get(key, "00"))])
        elif kind == "section":
            rows.append(["", f"{number}  {title}", str(pages.get(key, "00"))])
        else:
            rows.append([number, title, str(pages.get(key, "00"))])
    B._table(["Chapter No.", "Particulars", "Pg. No."], rows,
             [2.4, 11.9, 1.6], 10.5, ["c", "l", "c"], True, "E7E6E6", False)


def list_table(B: WcBuilder, title: str, entries: list[tuple[str, str]],
               pages: dict[str, int]) -> None:
    front_heading(B, title)
    rows = [[number, caption, str(pages.get(number, "00"))] for number, caption in entries]
    B._table(["Figure / Table No.", "Description", "Page"], rows,
             [2.4, 11.9, 1.6], 10.5, ["c", "l", "c"], True, "E7E6E6", True)


# ------------------------------------------------------------------------- runner
def run_commands(cmds: list[tuple[str, dict]], out: Path, template: str = "blank") -> None:
    """Run the command list through wordcraft-cli, in chunks."""
    chunk: list[str] = []
    size = 0
    chunks: list[list[str]] = []
    for cid, params in cmds:
        piece = f"{cid}={json.dumps(params, separators=(',', ':'))}"
        if size + len(piece) > 300_000:
            chunks.append(chunk)
            chunk, size = [], 0
        chunk.append(piece)
        size += len(piece) + 6
    if chunk:
        chunks.append(chunk)

    # never split a caret.set from the text.insert that follows it: a chunk
    # boundary in the middle of a cell fill would put the text at the end of
    # the document
    for i, piece in enumerate(chunks[:-1]):
        while piece and piece[-1].startswith("caret.set"):
            nxt = chunks[i + 1]
            if not nxt:
                break
            piece.append(nxt.pop(0))

    out.parent.mkdir(parents=True, exist_ok=True)
    args = ["wordcraft-cli", "run"]
    if template:
        args += ["--template", template]
    for index, piece in enumerate(chunks):
        if index:
            args += ["--cmd", "caret.docEnd={}"]
        for item in piece:
            args += ["--cmd", item]
        args += ["--save", str(out)]
        proc = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        noise = [line for line in proc.stdout.splitlines()
                 if "error" in line.lower() or "bad " in line.lower() or "refus" in line.lower()]
        if noise:
            print(f"  chunk {index}: {len(noise)} problem(s)")
            for line in noise[:6]:
                print("    ", line[:160])
        if proc.returncode != 0:
            raise SystemExit(f"wordcraft-cli failed in chunk {index}")
        args = ["wordcraft-cli", "run", "--file", str(out)]


def substitute_tables(cmds, indices):
    """Replace the table placeholders with the real block indices."""
    def fix(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            if value >= TABLE_TOKEN:
                return indices[value - TABLE_TOKEN]
            return value
        if isinstance(value, list):
            if len(value) == 2 and value[1] == "p":
                return [indices[value[0] - TABLE_TOKEN] + 1]
            return [fix(item) for item in value]
        if isinstance(value, dict):
            return {key: fix(item) for key, item in value.items()}
        return value

    return [(cid, fix(params)) for cid, params in cmds]


def verify_tables(docx: Path, expected: list[str]) -> None:
    """Check that every table carries the header the builder intended."""
    data = json.loads(subprocess.check_output(["wordcraft-cli", "inspect", str(docx)], text=True))
    tables = [b for b in data["blocks"] if b["type"] == "table"]
    problems = []
    for i, (block, head) in enumerate(zip(tables, expected)):
        got = str(block["cells"][0][0]).strip()
        if got != head.strip():
            problems.append((i, block["index"], head, got))
    print(f"  {len(tables)} tables checked, {len(problems)} mismatched")
    for i, idx, head, got in problems[:8]:
        print(f"    table {i} at block {idx}: expected {head!r}, found {got!r}")


def discover_table_indices(docx: Path) -> list[int]:
    data = json.loads(subprocess.check_output(["wordcraft-cli", "inspect", str(docx)], text=True))
    return [block["index"] for block in data["blocks"] if block["type"] == "table"]


def export_pdf(docx: Path, pdf: Path) -> None:
    subprocess.run(["wordcraft-cli", "convert", str(docx), str(pdf)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)


def pdf_pages(pdf: Path) -> list[str]:
    out = subprocess.check_output(["pdftotext", "-layout", str(pdf), "-"], text=True)
    return out.split("\f")


def measure(pdf: Path, outline, figures, tables) -> tuple[dict[str, int], int]:
    pages = pdf_pages(pdf)
    body_start = None
    for i, text in enumerate(pages):
        if re.search(r"^\s*Chapter 1:\s*Introduction", text, re.M):
            body_start = i
            break
    if body_start is None:
        body_start = 0
    found: dict[str, int] = {}

    for kind, number, title in outline:
        key = f"{kind}:{number}"
        if kind == "chapter":
            pattern = re.compile(rf"^\s*Chapter {re.escape(number)}:\s*{re.escape(title)}\s*$", re.M)
        elif kind == "section":
            pattern = re.compile(rf"^\s*{re.escape(number)}\s+{re.escape(title)}\s*$", re.M)
        else:
            pattern = re.compile(rf"^\s*{re.escape(title)}\s*$", re.M)
        for i in range(body_start, len(pages)):
            if pattern.search(pages[i]):
                found[key] = i - body_start + 1
                break

    for number, _caption in figures + tables:
        pattern = re.compile(rf"^\s*(Figure|Table)\s+{re.escape(number)}:", re.M)
        for i in range(body_start, len(pages)):
            if pattern.search(pages[i]):
                found[number] = i - body_start + 1
                break
    return found, body_start + 1


def build(page_map: dict[str, int] | None = None,
          skip_cells: bool = False) -> tuple[WcBuilder, list, list, list]:
    page_map = page_map or {}

    # a probe pass collects the outline, the figures and the tables
    probe = WcBuilder()
    for fn in (chapter1, chapter2, chapter3, chapter4, chapter5, chapter6,
               chapter7, chapter8, chapter9, chapter10):
        fn(probe)
    from wc_back import back_matter
    back_matter(probe)
    outline = probe.outline
    figures, tables = probe.figures, probe.tables

    B = WcBuilder()
    B.skip_cells = skip_cells
    style_commands(B)
    page_setup(B, title_page=True)

    cover(B)
    B.cmd("insert.pageBreak")
    declaration(B)
    B.cmd("insert.pageBreak")
    abstract(B)
    B.cmd("insert.pageBreak")
    index_table(B, outline, page_map)
    B.cmd("insert.pageBreak")
    list_table(B, "List of figures", figures, page_map)
    B.cmd("insert.pageBreak")
    list_table(B, "List of Tables", tables, page_map)

    # front matter: lower-roman page numbers, none on the cover
    B.cmd("layout.pageNumberFormat", format="lowerRoman", start=1)

    # the body is its own section with arabic numbering from 1
    # (a continuous break avoids a stray empty page; the first chapter
    # heading carries the page break instead)
    B.cmd("layout.break", kind="continuous")
    B.blocks += 1
    for fn in (chapter1, chapter2, chapter3, chapter4, chapter5, chapter6,
               chapter7, chapter8, chapter9, chapter10):
        fn(B)
    back_matter(B)
    page_setup(B, title_page=False)
    B.cmd("layout.pageNumberFormat", format="decimal", start=1)

    # running header on the body pages
    B.cmd("insert.editHeader")
    B._style("Normal")
    B._char(size=13, bold=True, italic=False)
    B._para(align="center", spacing=1.0, before=0, after=0)
    B._text("Vidyavardhini’s College of Engineering and Technology", bold=True, size=13)
    B._new_paragraph()
    B._style("Normal")
    B._char(size=11, bold=False, italic=False)
    B._para(align="center", spacing=1.0, before=0, after=2)
    B._text("Department of Information Technology", size=11)
    B._new_paragraph()
    B.cmd("insert.table", rows=1, cols=1, style="TableGrid")
    B.cmd("table.borders", kind="none", width=0.0, color="FFFFFF")
    B.cmd("table.borders", kind="bottom", width=1.0, color="000000")
    B.cmd("table.properties", align="center")
    B.cmd("table.rowHeight", height=2, rule="exact")
    B.cmd("insert.closeHeader")

    # page numbers: the body footer first (the caret is in the body), then the
    # front-matter footer, which is addressed by page index
    B.cmd("insert.editFooter")
    B.cmd("insert.pageNumber", position="bottom", align="center")
    B.cmd("insert.closeHeader")
    B.cmd("insert.editFooter", page=1)
    B.cmd("insert.pageNumber", position="bottom", align="center")
    B.cmd("insert.closeHeader")

    return B, outline, figures, tables


def main() -> None:
    work = Path(tempfile.mkdtemp(prefix="wc-report-"))
    try:
        print("pass 1 ...")
        b1, outline, figures, tables = build()
        run_commands(b1.cmds, work / "pass1.docx")
        export_pdf(work / "pass1.docx", work / "pass1.pdf")
        pages, body_start = measure(work / "pass1.pdf", outline, figures, tables)
        missing = [k for k in pages if k not in pages]
        print(f"  body starts on PDF page {body_start}; {len(pages)} anchors located")

        print("pass 2 ...")
        b2, outline, figures, tables = build(pages)
        run_commands(b2.cmds, OUT_DOCX)
        verify_tables(OUT_DOCX, b2.table_headers)
        export_pdf(OUT_DOCX, OUT_PDF)
        pages2, _ = measure(OUT_PDF, outline, figures, tables)
        drift = {k: (v, pages2.get(k)) for k, v in pages.items() if pages2.get(k) != v}
        print(f"  wrote {OUT_DOCX.name} and {OUT_PDF.name}")
        print(f"  page-number drift between passes: {len(drift)}")
        for k, (a, b) in list(drift.items())[:10]:
            print(f"    {k}: {a} -> {b}")
    finally:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
