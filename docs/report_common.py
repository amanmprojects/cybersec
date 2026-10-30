"""Shared DOCX formatting helpers and the reference database for the report."""
from __future__ import annotations

import html
import re

from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

TEXT_WIDTH = 15.92  # cm, A4 with 2.54 cm margins on every side
INK = RGBColor(0x00, 0x00, 0x00)
MUTED = RGBColor(0x33, 0x33, 0x33)
ACCENT = RGBColor(0x4F, 0x46, 0xE5)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)

from refs import REFS  # noqa: F401


class ReportBuilder:
    """Thin wrapper around python-docx with the formatting rules of the template."""

    def __init__(self, doc):
        self.doc = doc
        self.cited: list[str] = []
        self._setup_styles()

    # ------------------------------------------------------------------ setup
    def _setup_styles(self):
        normal = self.doc.styles["Normal"]
        normal.font.name = "Times New Roman"
        normal.font.size = Pt(12)
        normal.font.color.rgb = INK
        rpr = normal.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.append(rfonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rfonts.set(qn(attr), "Times New Roman")
        normal.paragraph_format.line_spacing = 1.5
        normal.paragraph_format.space_after = Pt(8)
        normal.paragraph_format.space_before = Pt(0)

    # -------------------------------------------------------------- citations
    def cite(self, *keys: str) -> str:
        out = []
        for key in keys:
            if key not in REFS:
                raise KeyError(f"unknown reference {key}")
            if key not in self.cited:
                self.cited.append(key)
            out.append(f"[{self.cited.index(key) + 1}]")
        return ", ".join(out)

    # ------------------------------------------------------------------ text
    def _runs(self, paragraph, text: str, size: float, bold: bool = False,
              italic: bool = False, color=None):
        # **bold** inline markup only; everything else is literal.
        for part in re.split(r"(\*\*.+?\*\*)", text):
            if not part:
                continue
            is_bold = part.startswith("**") and part.endswith("**") and len(part) > 4
            run = paragraph.add_run(part[2:-2] if is_bold else part)
            run.font.name = "Times New Roman"
            run.font.size = Pt(size)
            run.bold = bold or is_bold
            run.italic = italic
            if color is not None:
                run.font.color.rgb = color
            rpr = run._element.get_or_add_rPr()
            rfonts = rpr.find(qn("w:rFonts"))
            if rfonts is None:
                rfonts = OxmlElement("w:rFonts")
                rpr.append(rfonts)
            for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
                rfonts.set(qn(attr), "Times New Roman")
        return paragraph

    def p(self, text: str, size: float = 12, bold: bool = False, italic: bool = False,
          align=WD_ALIGN_PARAGRAPH.JUSTIFY, spacing: float = 1.5, before: float = 0,
          after: float = 8, indent: float | None = None,
          first: float | None = None, keep: bool = False, color=None):
        para = self.doc.add_paragraph()
        pf = para.paragraph_format
        pf.alignment = align
        pf.line_spacing = spacing
        pf.space_before = Pt(before)
        pf.space_after = Pt(after)
        pf.keep_with_next = keep
        if indent is not None:
            pf.left_indent = Cm(indent)
        if first is not None:
            pf.first_line_indent = Cm(first)
        self._runs(para, text, size, bold, italic, color)
        return para

    def lead(self, text: str):
        """First paragraph after a chapter heading, with a drop-cap feel."""
        return self.p(text, after=8)

    def bullets(self, items: list[str], size: float = 12, spacing: float = 1.5):
        for item in items:
            para = self.doc.add_paragraph()
            pf = para.paragraph_format
            pf.left_indent = Cm(0.9)
            pf.first_line_indent = Cm(-0.45)
            pf.line_spacing = spacing
            pf.space_after = Pt(4)
            pf.tab_stops.add_tab_stop(Cm(0.9))
            self._runs(para, "\u2022\t" + item, size)

    def numbered(self, items: list[str], size: float = 12, spacing: float = 1.5):
        for i, item in enumerate(items, 1):
            para = self.doc.add_paragraph()
            pf = para.paragraph_format
            pf.left_indent = Cm(0.9)
            pf.first_line_indent = Cm(-0.6)
            pf.line_spacing = spacing
            pf.space_after = Pt(4)
            pf.tab_stops.add_tab_stop(Cm(0.9))
            self._runs(para, f"{i}.\t" + item, size)

    # --------------------------------------------------------------- headings
    def chapter(self, number: int, title: str, first: bool = False):
        para = self.doc.add_paragraph()
        pf = para.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf.line_spacing = 1.5
        pf.space_before = Pt(0 if first else 16)
        pf.space_after = Pt(8)
        pf.keep_with_next = True
        if not first:
            pf.page_break_before = True
        self._runs(para, f"Chapter {number}: {title}", 16, bold=True)

    def section(self, number: str, title: str, page_break: bool = False):
        para = self.doc.add_paragraph()
        pf = para.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf.line_spacing = 1.5
        pf.space_before = Pt(12)
        pf.space_after = Pt(6)
        pf.keep_with_next = True
        if page_break:
            pf.page_break_before = True
        self._runs(para, f"{number}  {title}", 14, bold=True)
        return para

    def sub(self, number: str, title: str):
        para = self.doc.add_paragraph()
        pf = para.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.LEFT
        pf.line_spacing = 1.5
        pf.space_before = Pt(8)
        pf.space_after = Pt(4)
        pf.keep_with_next = True
        self._runs(para, f"{number}  {title}", 12, bold=True)

    # ---------------------------------------------------------------- objects
    def figure(self, number: str, path: str, caption: str, width: float = 15.0):
        import os

        if not os.path.exists(path):
            raise FileNotFoundError(path)
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.space_before = Pt(6)
        para.paragraph_format.space_after = Pt(4)
        para.paragraph_format.keep_with_next = True
        para.add_run().add_picture(path, width=Cm(width))
        cap = self.doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
        cap.paragraph_format.space_before = Pt(2)
        cap.paragraph_format.space_after = Pt(12)
        cap.paragraph_format.line_spacing = 1.0
        self._runs(cap, f"**Figure {number}:** ", 10.5)
        self._runs(cap, caption, 10.5, italic=True)

    def table(self, number: str, caption: str, headers: list[str], rows: list[list[str]],
              widths: list[float], font: float = 9.2, align: list[str] | None = None,
              bold_first: bool = False, header_fill: str = "E7E6E6",
              zebra: bool = True):
        cap = self.doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
        cap.paragraph_format.space_before = Pt(8)
        cap.paragraph_format.space_after = Pt(4)
        cap.paragraph_format.keep_with_next = True
        self._runs(cap, f"**Table {number}:** ", 10.5)
        self._runs(cap, caption, 10.5, italic=True)

        table = self.doc.add_table(rows=1, cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        table.allow_autofit = False
        tblPr = table._tbl.tblPr
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "fixed")
        tblPr.append(layout)
        # borders: horizontal rules only, like the reference format
        borders = OxmlElement("w:tblBorders")
        for edge, val, sz, color in (
            ("top", "single", "12", "000000"),
            ("left", "none", "0", "auto"),
            ("bottom", "single", "12", "000000"),
            ("right", "none", "0", "auto"),
            ("insideH", "single", "4", "BFBFBF"),
            ("insideV", "none", "0", "auto"),
        ):
            el = OxmlElement(f"w:{edge}")
            el.set(qn("w:val"), val)
            el.set(qn("w:sz"), sz)
            el.set(qn("w:space"), "0")
            el.set(qn("w:color"), color)
            borders.append(el)
        tblPr.append(borders)

        # header
        hdr = table.rows[0]
        trPr = hdr._tr.get_or_add_trPr()
        tblHeader = OxmlElement("w:tblHeader")
        tblHeader.set(qn("w:val"), "true")
        trPr.append(tblHeader)
        cant = OxmlElement("w:cantSplit")
        cant.set(qn("w:val"), "true")
        trPr.append(cant)
        for i, text in enumerate(headers):
            cell = hdr.cells[i]
            cell.width = Cm(widths[i])
            shade = OxmlElement("w:shd")
            shade.set(qn("w:val"), "clear")
            shade.set(qn("w:color"), "auto")
            shade.set(qn("w:fill"), header_fill)
            cell._tc.get_or_add_tcPr().append(shade)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.0
            self._runs(p, text, font, bold=True)

        for ri, row in enumerate(rows):
            cells = table.add_row().cells
            trPr = table.rows[-1]._tr.get_or_add_trPr()
            cant = OxmlElement("w:cantSplit")
            cant.set(qn("w:val"), "true")
            trPr.append(cant)
            for ci, text in enumerate(row):
                cell = cells[ci]
                cell.width = Cm(widths[ci])
                if zebra and ri % 2 == 1:
                    shade = OxmlElement("w:shd")
                    shade.set(qn("w:val"), "clear")
                    shade.set(qn("w:color"), "auto")
                    shade.set(qn("w:fill"), "F2F2F2")
                    cell._tc.get_or_add_tcPr().append(shade)
                p = cell.paragraphs[0]
                a = (align[ci] if align else ("l" if ci == 0 else "c"))
                p.alignment = {"l": WD_ALIGN_PARAGRAPH.LEFT,
                               "c": WD_ALIGN_PARAGRAPH.CENTER,
                               "r": WD_ALIGN_PARAGRAPH.RIGHT}[a]
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.0
                self._runs(p, str(text), font, bold=(bold_first and ci == 0))
        # hairline spacer: keeps a following paragraph off the table without
        # pushing a near-empty page when the table ends at the page foot
        sp = self.doc.add_paragraph()
        sp.paragraph_format.space_before = Pt(0)
        sp.paragraph_format.space_after = Pt(0)
        sp.paragraph_format.line_spacing = Pt(2)
        pPr = sp._p.get_or_add_pPr()
        rPr = OxmlElement("w:rPr")
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), "4")
        rPr.append(sz)
        pPr.append(rPr)
        return table

    def callout(self, title: str, text: str, fill: str = "EEF2FF", border: str = "C7D2FE"):
        table = self.doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        cell = table.rows[0].cells[0]
        cell.width = Cm(TEXT_WIDTH)
        tcPr = cell._tc.get_or_add_tcPr()
        shade = OxmlElement("w:shd")
        shade.set(qn("w:val"), "clear")
        shade.set(qn("w:color"), "auto")
        shade.set(qn("w:fill"), fill)
        tcPr.append(shade)
        borders = OxmlElement("w:tcBorders")
        for edge in ("top", "left", "bottom", "right"):
            el = OxmlElement(f"w:{edge}")
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "6")
            el.set(qn("w:space"), "0")
            el.set(qn("w:color"), border)
            borders.append(el)
        tcPr.append(borders)
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.line_spacing = 1.15
        self._runs(p, title, 11, bold=True, color=ACCENT)
        p2 = cell.add_paragraph()
        p2.paragraph_format.space_after = Pt(4)
        p2.paragraph_format.line_spacing = 1.15
        self._runs(p2, text, 10.5)
        sp = self.doc.add_paragraph()
        sp.paragraph_format.space_after = Pt(2)
        sp.paragraph_format.line_spacing = 1.0
