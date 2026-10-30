# Project Report

The report is delivered as a formatted document, not as Markdown:

- **`Phishing_Susceptibility_Study_Report.docx`** — the final report (86 pages, A4)
- **`Phishing_Susceptibility_Study_Report.pdf`** — the same document, paginated
- **`TEMP_REPORT_FOR_REVIEW.docx` / `.pdf`** — identical copies, for review convenience

It is generated from the two supplied templates
(`Chapterwise_BE honor Project-report-format_2026-27_part 1.docx` and `... part 2.docx`) with
**WordCraft**, the Word-compatible engine:

```bash
uv run --with python-docx python docs/wc_build.py
```

The document contains the cover page, declaration, abstract, index, list of figures, list of
tables, ten chapters, appendices A–C, the plagiarism record, the literature cited and the
acknowledgements.

Source modules live in `docs/`:

| File | Purpose |
|------|---------|
| `wc_build.py` | The build: page setup, front matter, headers/footers, two-pass pagination, PDF export |
| `wc_builder.py` | Turns the report API into WordCraft commands (styles, native tables, images, captions) |
| `wc_back.py` | Appendices A–C, the plagiarism record, the literature cited, the acknowledgements |
| `report_ch1_3.py`, `report_ch4_6.py`, `report_ch7_10.py` | The chapters: prose, tables and figures |
| `refs.py` | The reference database (IEEE style) |
| `results.json` | The analytics snapshot every number in the report comes from |
| `make_figures.py`, `make_charts.py` | Regenerate the diagrams and the result charts |

The figures and charts are generated from `docs/results.json`, which is exported from the seeded
database with `python3 app.py export docs/results.json`.
