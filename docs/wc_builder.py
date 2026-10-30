"""Build the project report with WordCraft (native Word engine).

The report is generated as a sequence of WordCraft commands: real Word styles,
Heading 1/2/3 outline levels, section breaks with independent page numbering,
a running header and a centred page number in the footer.  WordCraft renders
and exports the PDF with its own layout engine, so the DOCX and the PDF agree.

Usage:
    uv run --with python-docx python docs/wc_build.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from refs import REFS  # noqa: E402

CM = 28.3464567  # points per centimetre
TABLE_TOKEN = 999999  # placeholder for "the table that was just created"

ALIGN = {"l": "left", "c": "center", "r": "right",
         "left": "left", "center": "center", "right": "right",
         "justify": "justify"}


def cm(value: float) -> float:
    return round(value * CM, 2)


# --------------------------------------------------------------------------- builder
class WcBuilder:
    """Emits WordCraft commands; mirrors the ReportBuilder API of report_common."""

    def __init__(self) -> None:
        self.cmds: list[tuple[str, dict]] = []
        self.cited: list[str] = []
        self.figures: list[tuple[str, str]] = []   # (number, caption)
        self.tables: list[tuple[str, str]] = []     # (number, caption)
        self.outline: list[tuple[str, str, str]] = []  # (kind, number, title)
        self.table_seq = 0                              # tables created so far
        self.table_headers: list[str] = []              # first cell of every table
        self.skip_cells = False                          # skeleton mode
        self.blocks = 1                              # blocks in the document so far

    # -- low level ---------------------------------------------------------
    def cmd(self, cid: str, **params) -> None:
        self.cmds.append((cid, params))

    def _new_paragraph(self) -> None:
        self.cmd("text.newParagraph")
        self.blocks += 1

    def _table_paragraph(self) -> None:
        """The empty paragraph that follows a table (the caret lands there)."""
        self.cmd("text.newParagraph")
        self.blocks += 1

    def _style(self, name: str) -> None:
        self.cmd("para.style", style=name)

    def _char(self, size=None, bold=None, italic=None, font="Times New Roman",
              color="000000") -> None:
        """Set the character formatting applied to the text inserted next."""
        props: dict = {"font": font, "color": color}
        props["size"] = size
        props["bold"] = bold
        props["italic"] = italic
        self.cmd("format.set", props=props)

    def _para(self, align="left", spacing=1.5, before=0, after=8, indent=0.0,
              first=0.0, keep=False, page_break=False, borders=None) -> None:
        # every flag is set explicitly: para.set merges, so a flag left out
        # would be inherited from the previous paragraph
        props: dict = {
            "align": align,
            "lineSpacing": {"rule": "multiple", "value": spacing},
            "spaceBefore": before,
            "spaceAfter": after,
            "indentLeft": indent,
            "indentFirst": first,
            "keepNext": keep,
            "pageBreakBefore": page_break,
            "widowControl": True,
        }
        if borders is not None:
            props["borders"] = borders
        self.cmd("para.set", props=props)

    def _text(self, text: str, bold=False, italic=False, size=None) -> None:
        """Insert text, honouring **bold** inline markup."""
        if size is not None:
            self.cmd("format.size", size=size)
        if bold:
            self.cmd("format.bold", value=True)
        if italic:
            self.cmd("format.italic", value=True)
        for part in re.split(r"(\*\*.+?\*\*)", text):
            if not part:
                continue
            is_bold = part.startswith("**") and part.endswith("**") and len(part) > 4
            if is_bold and not bold:
                self.cmd("format.bold", value=True)
            self.cmd("text.insert", text=part[2:-2] if is_bold else part)
            if is_bold and not bold:
                self.cmd("format.bold", value=False)
        if bold:
            self.cmd("format.bold", value=False)
        if italic:
            self.cmd("format.italic", value=False)

    # -- citations ---------------------------------------------------------
    def cite(self, *keys: str) -> str:
        out = []
        for key in keys:
            if key not in REFS:
                raise KeyError(f"unknown reference {key}")
            if key not in self.cited:
                self.cited.append(key)
            out.append(f"[{self.cited.index(key) + 1}]")
        return ", ".join(out)

    # -- text blocks -------------------------------------------------------
    def p(self, text: str, size: float = 12, bold: bool = False, italic: bool = False,
          align: str = "justify", spacing: float = 1.5, before: float = 0,
          after: float = 8, indent: float | None = None, first: float | None = None):
        self._style("Normal")
        self._char(size=size, bold=bold, italic=italic)
        self._para(align=align, spacing=spacing, before=before, after=after,
                   indent=0.0 if indent is None else cm(indent),
                   first=0.0 if first is None else cm(first))
        self._text(text, bold=bold, italic=italic, size=size)
        self._new_paragraph()

    def lead(self, text: str):
        self.p(text, after=8)

    def bullets(self, items: list[str], size: float = 12, spacing: float = 1.5):
        for item in items:
            self._style("Normal")
            self._char(size=size, bold=False, italic=False)
            self._para(align="justify", spacing=spacing, before=0, after=4,
                       indent=cm(0.9), first=cm(-0.45))
            self._text("•\t" + item, size=size)
            self._new_paragraph()

    def numbered(self, items: list[str], size: float = 12, spacing: float = 1.5):
        for i, item in enumerate(items, 1):
            self._style("Normal")
            self._char(size=size, bold=False, italic=False)
            self._para(align="justify", spacing=spacing, before=0, after=4,
                       indent=cm(0.9), first=cm(-0.6))
            self._text(f"{i}.\t" + item, size=size)
            self._new_paragraph()

    # -- headings ----------------------------------------------------------
    def _heading(self, style: str, text: str, size: float, before: float,
                 after: float, page_break=None) -> None:
        self._style(style)
        self._char(size=size, bold=True, italic=False)
        self._para(align="left", spacing=1.5, before=before, after=after,
                   keep=True, page_break=page_break)
        self._text(text)
        # make the heading's own character formatting explicit so that nothing
        # leaks in from the previous paragraph
        self._new_paragraph()

    def chapter(self, number: int, title: str, first: bool = False):
        self._heading("Heading 1", f"Chapter {number}: {title}", 16,
                      0 if first else 16, 8,
                      page_break=True)
        self.outline.append(("chapter", str(number), title))

    def section(self, number: str, title: str, page_break: bool = False):
        self._heading("Heading 2", f"{number}  {title}", 14, 12, 6,
                      page_break=page_break)
        self.outline.append(("section", number, title))

    def back_chapter(self, number: str, title: str):
        """A back-matter heading (appendix, references) that lands in the index."""
        self._heading("Heading 1", title, 16, 16, 8, page_break=True)
        self.outline.append(("back", number, title))

    def sub(self, number: str, title: str):
        self._heading("Heading 3", f"{number}  {title}", 12, 8, 4)

    # -- objects -----------------------------------------------------------
    def figure(self, number: str, path: str, caption: str, width: float = 15.0):
        self._style("Normal")
        self._char(size=12, bold=False, italic=False)
        self._para(align="center", spacing=1.0, before=6, after=2, keep=True)
        self.cmd("insert.picture", path=str(path), width=cm(width))
        self._new_paragraph()
        self._style("Caption")
        self._char(size=10, bold=False, italic=True)
        self._para(align="left", spacing=1.0, before=2, after=12)
        self._text(f"**Figure {number}:** {caption}", italic=True)
        self._new_paragraph()
        self.figures.append((number, caption))

    def _cell(self, block: int, row: int, col: int, value: str, align: str,
              size: float, bold: bool) -> None:
        if self.skip_cells:
            return
        self.cmd("caret.set", pos={"story": "body", "path": [block, row, col, 0], "off": 0})
        self.cmd("para.set", props={
            "align": ALIGN.get(align, align),
            "lineSpacing": {"rule": "multiple", "value": 1.0},
            "spaceBefore": 2, "spaceAfter": 2,
            "indentLeft": 0, "indentFirst": 0,
        })
        self._char(size=size, bold=bold, italic=False)
        self.cmd("text.insert", text=str(value))

    def _table(self, headers: list[str], rows: list[list[str]], widths: list[float],
               font: float, align: list[str], bold_first: bool, header_fill: str,
               zebra: bool) -> None:
        cols = len(headers)
        self.table_headers.append(str(headers[0]) if headers else "")
        self.cmd("insert.table", rows=len(rows) + 1, cols=cols, style="TableGrid")
        block = self.blocks - 1
        self.blocks += 1

        for c in range(cols):
            self._cell(block, 0, c, headers[c], "center", font, True)
        for r, row in enumerate(rows, start=1):
            for c in range(cols):
                value = row[c] if c < len(row) else ""
                bold = bold_first and c == 0
                self._cell(block, r, c, value, align[c] if c < len(align) else "l",
                           font, bold)

        if not self.skip_cells:
            # header row: shading, bold, repeated on every page
            self.cmd("caret.set", pos={"story": "body", "path": [block, 0, 0, 0], "off": 0})
            self.cmd("table.selectRow")
            self.cmd("table.shading", color=header_fill)
            self.cmd("select.collapse")

            # banded rows
            if zebra:
                for r in range(2, len(rows) + 1, 2):
                    self.cmd("caret.set", pos={"story": "body", "path": [block, r, 0, 0], "off": 0})
                    self.cmd("table.selectRow")
                    self.cmd("table.shading", color="F7F7F7")
                    self.cmd("select.collapse")

            # column widths
            for c, width in enumerate(widths):
                self.cmd("caret.set", pos={"story": "body", "path": [block, 0, c, 0], "off": 0})
                self.cmd("table.selectColumn")
                self.cmd("table.columnWidth", width=cm(width))
                self.cmd("select.collapse")

        # table frame
        self.cmd("table.borders", kind="all", width=0.5, color="BFBFBF")
        self.cmd("table.borders", kind="outside", width=1.0, color="000000")
        self.cmd("table.properties", align="center", headerRow=True, allowBreak=True)
        self.cmd("table.repeatHeader")
        # insert.table leaves the caret inside the first cell: step into the
        # empty paragraph that follows the table and normalise it (it would
        # otherwise inherit the heading's keep-with-next)
        self.cmd("caret.set", pos={"story": "body", "path": [block + 1], "off": 0})
        self._style("Normal")
        self._char(size=1, bold=False, italic=False)
        self._para(align="left", spacing=1.0, before=0, after=0)

    def table(self, number: str, caption: str, headers: list[str], rows: list[list[str]],
              widths: list[float], font: float = 9.2, align: list[str] | None = None,
              bold_first: bool = False, header_fill: str = "E7E6E6",
              zebra: bool = True):
        cols = len(headers)
        align = align or ["l"] + ["c"] * (cols - 1)
        self._table(headers, rows, widths, font, align, bold_first, header_fill, zebra)
        self._style("Caption")
        self._char(size=10, bold=False, italic=True)
        self._para(align="left", spacing=1.0, before=4, after=12)
        self._text(f"**Table {number}:** {caption}", italic=True)
        self._new_paragraph()
        self.tables.append((number, caption))

    def callout(self, title: str, text: str, fill: str = "F2F5FF", border: str = "C7D2FE"):
        self.cmd("insert.table", rows=1, cols=1, style="TableGrid")
        block = self.blocks - 1
        self.blocks += 1
        self.table_headers.append(f"{title} {text}")
        self._cell(block, 0, 0, f"{title} {text}", "left", 11, False)
        self.cmd("caret.set", pos={"story": "body", "path": [block, 0, 0, 0], "off": 0})
        self.cmd("table.shading", color=fill)
        self.cmd("table.borders", kind="outside", width=1.0, color=border)
        self.cmd("table.borders", kind="all", width=0.0, color=fill)
        self.cmd("table.properties", align="center")
        self.cmd("caret.set", pos={"story": "body", "path": [block + 1], "off": 0})

    def rule(self, width: float, align: str = "right", before: float = 12,
             after: float = 0) -> None:
        """A horizontal rule drawn as a one-cell table with a bottom border."""
        self.cmd("insert.table", rows=1, cols=1, style="TableGrid")
        block = self.blocks - 1
        self.blocks += 1
        self.table_headers.append("")
        self.cmd("table.borders", kind="none", width=0.0, color="FFFFFF")
        self.cmd("table.borders", kind="bottom", width=1.0, color="000000")
        self.cmd("table.properties", align=align, width=cm(width))
        self.cmd("table.rowHeight", height=2, rule="exact")
        self.cmd("caret.set", pos={"story": "body", "path": [block + 1], "off": 0})
        self._style("Normal")
        self._char(size=1, bold=False, italic=False)
        self._para(align=align, spacing=1.0, before=before, after=after)
        self._new_paragraph()

    def ref_paragraph(self, text: str):
        """A hanging-indent bibliography entry."""
        self._style("Normal")
        self._char(size=10.5, bold=False, italic=False)
        self._para(align="left", spacing=1.0, before=0, after=5,
                   indent=cm(0.9), first=cm(-0.9))
        self._text(text, size=10.5)
        self._new_paragraph()
