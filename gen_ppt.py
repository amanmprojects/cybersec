"""
Generate the Mini-Project PPT: Phishing Susceptibility Study.
Design system + native charts + real screenshots of the app.

RUN:  uv run --with python-pptx python gen_ppt.py
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_LABEL_POSITION

HERE = os.path.dirname(os.path.abspath(__file__))
SHOTS = os.path.join(HERE, "assets", "shots")
OUT = os.path.join(HERE, "Phishing_Susceptibility_PPT.pptx")

# ----------------------------------------------------------------- palette
INK    = RGBColor(0x0D, 0x14, 0x24)
INK2   = RGBColor(0x47, 0x55, 0x69)
MUTED  = RGBColor(0x94, 0xA3, 0xB8)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
BG     = RGBColor(0xFF, 0xFF, 0xFF)
SURF   = RGBColor(0xF8, 0xFA, 0xFC)
LINE   = RGBColor(0xE2, 0xE8, 0xF0)
BRAND  = RGBColor(0x4F, 0x46, 0xE5)
BRANDD = RGBColor(0x31, 0x2E, 0x81)
BRANDS = RGBColor(0xEE, 0xF0, 0xFF)
OK     = RGBColor(0x05, 0x96, 0x69)
OKS    = RGBColor(0xE7, 0xF7, 0xF1)
WARN   = RGBColor(0xD9, 0x77, 0x06)
WARNS  = RGBColor(0xFD, 0xF3, 0xE4)
BAD    = RGBColor(0xDC, 0x26, 0x26)
BADS   = RGBColor(0xFD, 0xEC, 0xEC)
NAVY   = RGBColor(0x0D, 0x14, 0x24)
NAVY2  = RGBColor(0x1A, 0x24, 0x3D)
NAVY3  = RGBColor(0x27, 0x33, 0x52)

W, H = 13.333, 7.5
M = 0.72                      # page margin
CW = W - 2 * M                # content width

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
BLANK = prs.slide_layouts[6]

# ----------------------------------------------------------------- helpers
def slide(dark=False):
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = NAVY if dark else BG
    return s

def rect(s, x, y, w, h, fill=None, line=None, lw=1.0, shape=MSO_SHAPE.RECTANGLE, radius=None):
    sp = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    sp.shadow.inherit = False
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid(); sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line; sp.line.width = Pt(lw)
    if radius is not None and shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        sp.adjustments[0] = radius
    sp.text_frame.text = ""
    return sp

def card(s, x, y, w, h, fill=SURF, line=LINE):
    return rect(s, x, y, w, h, fill=fill, line=line, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.045)

def tb(s, x, y, w, h, anchor=MSO_ANCHOR.TOP):
    t = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = t.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    return tf

def para(tf, text, size=14, bold=False, color=INK2, align=PP_ALIGN.LEFT,
         space_before=0, space_after=0, first=False, line_spacing=1.24, font="Segoe UI"):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    p.space_after = Pt(space_after)
    p.line_spacing = line_spacing
    r = p.add_run(); r.text = text
    r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color; r.font.name = font
    return p

def eyebrow(s, text, y=0.52, color=BRAND):
    rect(s, M, y + 0.045, 0.19, 0.055, fill=color)
    tf = tb(s, M + 0.3, y - 0.03, 8.0, 0.3)
    para(tf, text.upper(), size=10.5, bold=True, color=color, first=True)
    tf.paragraphs[0].runs[0].font.name = "Segoe UI"
    # letter-spacing via XML
    from pptx.oxml.ns import qn
    for r in tf.paragraphs[0].runs:
        r.font._rPr.set("spc", "140")

def heading(s, text, sub=None, y=0.88):
    tf = tb(s, M, y, CW, 0.62)
    para(tf, text, size=30, bold=True, color=INK, first=True, line_spacing=1.06)
    if sub:
        tf2 = tb(s, M, y + 0.62, CW * 0.86, 0.42)
        para(tf2, sub, size=13.5, color=INK2, first=True, line_spacing=1.3)

def footer(s, n, label="Phishing Susceptibility Study  ·  Group No. 2  ·  Cyber Security Mini Project"):
    rect(s, M, 6.93, CW, 0.012, fill=LINE)
    tf = tb(s, M, 7.03, CW - 0.6, 0.28)
    para(tf, label, size=9, color=MUTED, first=True)
    tf2 = tb(s, W - M - 0.6, 7.03, 0.6, 0.28)
    para(tf2, str(n), size=9, bold=True, color=MUTED, align=PP_ALIGN.RIGHT, first=True)

def chip(s, x, y, w, text, fg, bg, size=9.5, h=0.28):
    rect(s, x, y, w, h, fill=bg, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
    tf = tb(s, x, y + 0.045, w, h, anchor=MSO_ANCHOR.TOP)
    para(tf, text, size=size, bold=True, color=fg, align=PP_ALIGN.CENTER, first=True)

def icon_badge(s, x, y, d, glyph, fg, bg, size=15):
    rect(s, x, y, d, d, fill=bg, shape=MSO_SHAPE.OVAL)
    tf = tb(s, x, y + d * 0.24, d, d)
    para(tf, glyph, size=size, bold=True, color=fg, align=PP_ALIGN.CENTER, first=True)

def numbered_card(s, x, y, w, h, n, title, body, accent=BRAND):
    card(s, x, y, w, h)
    icon_badge(s, x + 0.28, y + 0.28, 0.42, str(n), accent, BRANDS, size=13)
    tf = tb(s, x + 0.85, y + 0.3, w - 1.15, 0.4)
    para(tf, title, size=14.5, bold=True, color=INK, first=True)
    tf2 = tb(s, x + 0.3, y + 0.9, w - 0.6, h - 1.06)
    para(tf2, body, size=11, color=INK2, first=True, line_spacing=1.32)

def stat(s, x, y, w, h, value, label, sub, accent, soft):
    card(s, x, y, w, h, fill=WHITE)
    rect(s, x, y + 0.16, 0.055, h - 0.32, fill=accent)
    tf = tb(s, x + 0.32, y + 0.24, w - 0.5, 0.3)
    para(tf, label.upper(), size=9, bold=True, color=MUTED, first=True)
    tf2 = tb(s, x + 0.32, y + 0.54, w - 0.5, 0.56)
    para(tf2, value, size=30, bold=True, color=accent, first=True, line_spacing=1.0)
    tf3 = tb(s, x + 0.32, y + 1.12, w - 0.5, 0.4)
    para(tf3, sub, size=10.5, color=INK2, first=True, line_spacing=1.25)

def screenshot(s, path, x, y, w, max_h, caption=None):
    """Screenshot in a framed browser window. The image is centre/top-cropped so it
    always fits the given slot (w x max_h) without distorting or overflowing."""
    from PIL import Image
    ch = 0.40 if caption else 0.0
    inner_w = w - 0.18
    img = Image.open(path).convert("RGB")
    iw, ih = img.size
    if max_h:
        want = inner_w / max(1e-6, (max_h - 0.42 - ch))
        if iw / ih > want:                       # too wide -> trim sides
            nw = int(ih * want)
            img = img.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
        else:                                    # too tall -> keep the top
            img = img.crop((0, 0, iw, max(1, int(iw / want))))
    iw, ih = img.size
    inner_h = inner_w * ih / iw
    frame_h = 0.42 + inner_h + ch
    rect(s, x, y, w, frame_h, fill=WHITE, line=LINE, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.03)
    rect(s, x, y, w, 0.34, fill=NAVY, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.16)
    rect(s, x, y + 0.2, w, 0.14, fill=NAVY)
    for i, c in enumerate([RGBColor(0xFF, 0x5F, 0x57), RGBColor(0xFE, 0xBC, 0x2E), RGBColor(0x28, 0xC8, 0x40)]):
        rect(s, x + 0.16 + i * 0.19, y + 0.115, 0.11, 0.11, fill=c, shape=MSO_SHAPE.OVAL)
    rect(s, x + 0.72, y + 0.075, w * 0.42, 0.19, fill=NAVY3, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
    tf = tb(s, x + 0.72, y + 0.095, w * 0.42, 0.2)
    para(tf, "127.0.0.1:8000", size=7.5, color=RGBColor(0x8B, 0x98, 0xB0), align=PP_ALIGN.CENTER, first=True)
    tmp = os.path.join("/tmp", "phishshot_%d.png" % abs(hash((path, w, round(max_h or 0)))))
    img.save(tmp)
    s.shapes.add_picture(tmp, Inches(x + 0.09), Inches(y + 0.42),
                         width=Inches(inner_w), height=Inches(inner_h))
    if caption:
        tf2 = tb(s, x + 0.06, y + frame_h - 0.34, w - 0.12, 0.28)
        para(tf2, caption, size=8.5, color=MUTED, align=PP_ALIGN.CENTER, first=True)
    return y + frame_h

_N = [1]   # slide 1 (title) is not numbered
def footer(s, label="Phishing Susceptibility Study  ·  Group No. 2  ·  Cyber Security Mini Project"):
    _N[0] += 1
    n = _N[0]
    rect(s, M, 6.93, CW, 0.012, fill=LINE)
    tf = tb(s, M, 7.03, CW - 0.6, 0.28)
    para(tf, label, size=9, color=MUTED, first=True)
    tf2 = tb(s, W - M - 0.6, 7.03, 0.6, 0.28)
    para(tf2, str(n), size=9, bold=True, color=MUTED, align=PP_ALIGN.RIGHT, first=True)

# ============================================================== 1 · TITLE
s = slide(dark=True)
rect(s, 0, 0, W, 0.09, fill=BRAND)
rect(s, 8.4, -1.1, 6.6, 6.6, fill=NAVY2, shape=MSO_SHAPE.OVAL)
rect(s, 10.9, 2.5, 4.6, 4.6, fill=NAVY3, shape=MSO_SHAPE.OVAL)
rect(s, 0, 6.0, W, 1.5, fill=NAVY2)

rect(s, M, 1.06, 0.62, 0.62, fill=BRAND, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.28)
tf = tb(s, M, 1.19, 0.62, 0.4)
para(tf, "\U0001F3A3", size=19, align=PP_ALIGN.CENTER, first=True)
tf = tb(s, M + 0.82, 1.13, 6.0, 0.5)
para(tf, "PhishStudy", size=17, bold=True, color=WHITE, first=True)
tf = tb(s, M, 1.22, 6.0, 0.4)

tf = tb(s, M, 2.05, 9.6, 0.4)
para(tf, "MINI PROJECT  ·  CYBER SECURITY", size=11.5, bold=True, color=RGBColor(0xA5, 0xB4, 0xFC), first=True)
for r in tf.paragraphs[0].runs:
    r.font._rPr.set("spc", "200")

tf = tb(s, M, 2.52, 10.4, 1.9)
para(tf, "Phishing Susceptibility Study", size=48, bold=True, color=WHITE, first=True, line_spacing=1.02)
tf = tb(s, M, 3.62, 9.4, 1.0)
para(tf, "A simulated phishing campaign to measure and improve employee awareness",
     size=18, color=RGBColor(0xB6, 0xC2, 0xD9), first=True, line_spacing=1.3)

rect(s, M, 4.42, 3.2, 0.03, fill=BRAND)
tf = tb(s, M, 4.68, 9.6, 0.4)
para(tf, "Measure it.  Train it.  Report it.", size=14, bold=True, color=WHITE, first=True)

# feature chips
feats = [("Safe local simulation", RGBColor(0x6E, 0xF0, 0xC0), RGBColor(0x0B, 0x2E, 0x22)),
         ("Zero installation", RGBColor(0xC7, 0xD2, 0xFE), RGBColor(0x1E, 0x1B, 0x4B)),
         ("Tracks click → submit → report", RGBColor(0xFE, 0xE9, 0x9B), RGBColor(0x3B, 0x2C, 0x05))]
cx = M
for label, fg, bgc in feats:
    wch = 0.30 + len(label) * 0.083
    chip(s, cx, 5.28, wch, label, fg, bgc, size=10, h=0.34)
    cx += wch + 0.14

tf = tb(s, M, 6.28, 8.6, 0.9)
para(tf, "GROUP NO. 2", size=10.5, bold=True, color=RGBColor(0xA5, 0xB4, 0xFC), first=True)
para(tf, "Shetty Vikyath Vishwanath   ·   Mehtar Aman Yasin   ·   Singh Yash Anil   ·   Singh Abhishek Shailesh",
     size=12.5, color=WHITE, space_before=5)
tf = tb(s, M, 6.98, 11.0, 0.3)
para(tf, "8 October 2026   ·   Demonstration:  python3 app.py  →  http://127.0.0.1:8000",
     size=10, color=RGBColor(0x7C, 0x8A, 0xA3), first=True)

# ============================================================== 2 · PROBLEM
s = slide()
eyebrow(s, "The problem")
heading(s, "Why phishing, and why study it?",
        "Phishing is the cheapest way for an attacker to get a valid password — so it remains the #1 entry point.")

sw = (CW - 3 * 0.26) / 4
stat(s, M + (sw + 0.26) * 0, 2.15, sw, 1.62, "~90%", "of breaches", "begin with a phishing or stolen-credential incident", BAD, BADS)
stat(s, M + (sw + 0.26) * 1, 2.15, sw, 1.62, "1 in 3", "employees", "click a simulated phishing link in testing", WARN, WARNS)
stat(s, M + (sw + 0.26) * 2, 2.15, sw, 1.62, "1 click", "= full access", "an attacker reuses that password everywhere", BRAND, BRANDS)
stat(s, M + (sw + 0.26) * 3, 2.15, sw, 1.62, "0 tech", "fixes this", "awareness is the only control that always works", OK, OKS)

card(s, M, 4.06, CW * 0.485, 2.42)
icon_badge(s, M + 0.32, 4.32, 0.46, "\U0001F575", INK, RGBColor(0xE7, 0xEC, 0xF4), size=15)
tf = tb(s, M + 0.94, 4.36, CW * 0.4, 0.4)
para(tf, "Why we cannot just send real phish", size=15.5, bold=True, color=INK, first=True)
tf = tb(s, M + 0.32, 4.98, CW * 0.485 - 0.64, 1.4)
para(tf, "Sending real phishing to real people is dangerous, unethical and usually illegal without written "
         "consent. It can expose genuine credentials, damage trust and breach privacy law.",
     size=12, color=INK2, first=True, line_spacing=1.36)
para(tf, "So we built a controlled simulation instead: realistic attacks, fictional employees, zero real risk.",
     size=12, color=INK, bold=True, space_before=8, line_spacing=1.36)

card(s, M + CW * 0.515, 4.06, CW * 0.485, 2.42, fill=BRANDS, line=RGBColor(0xD5, 0xD8, 0xFB))
icon_badge(s, M + CW * 0.515 + 0.32, 4.32, 0.46, "\U0001F4A1", BRANDD, RGBColor(0xD5, 0xD8, 0xFB), size=15)
tf = tb(s, M + CW * 0.515 + 0.94, 4.36, CW * 0.4, 0.4)
para(tf, "What a simulation gives us", size=15.5, bold=True, color=INK, first=True)
items = ["A measurable baseline instead of guesswork",
         "Repeatable, safe and free of legal risk",
         "Immediate, blame-free training feedback",
         "Proof that training actually reduces risk"]
tf = tb(s, M + CW * 0.515 + 0.32, 4.98, CW * 0.485 - 0.64, 1.5)
for i, t in enumerate(items):
    para(tf, "✓   " + t, size=12, color=INK2, first=(i == 0), space_before=0 if i == 0 else 6, line_spacing=1.3)
footer(s)

# ============================================================== 3 · OBJECTIVES
s = slide()
eyebrow(s, "Objectives")
heading(s, "What our project set out to do",
        "Four measurable goals — each one visible in the application during the demo.")

cw2 = (CW - 0.34) / 2
ch2 = 1.76
objs = [("Simulate realistic phishing",
         "Three templates at increasing difficulty: IT password expiry (Easy), HR festival bonus (Medium) and a Microsoft 365 sign-in alert (Hard). None of them leave the app.", BRAND),
        ("Measure susceptibility",
         "Track the whole funnel per employee: sent → opened → clicked → submitted credentials → reported. Split by department and by template.", WARN),
        ("Show risk in plain language",
         "Every campaign produces a submission rate, a reporting rate and a plain-English insight, so a non-technical manager can act on it.", OK),
        ("Train immediately, then verify",
         "Falling for the phish opens instant red-flag coaching; reporting one reinforces the habit. A five-question quiz scores whether training stuck.", BAD)]
for i, (t, b, acc) in enumerate(objs):
    x = M + (cw2 + 0.34) * (i % 2)
    y = 2.12 + (ch2 + 0.26) * (i // 2)
    numbered_card(s, x, y, cw2, ch2, i + 1, t, b, accent=acc)

card(s, M, 6.02, CW, 0.8, fill=WHITE)
tf = tb(s, M + 0.36, 6.2, CW - 0.72, 0.46, anchor=MSO_ANCHOR.MIDDLE)
para(tf, "Success = fewer people submit credentials, and more people report the mail.",
     size=14.5, bold=True, color=INK, align=PP_ALIGN.CENTER, first=True)
footer(s)

# ============================================================== 4 · RED FLAGS
s = slide()
eyebrow(s, "What the app teaches", color=BAD)
heading(s, "Five red flags in every simulated email",
        "Students learn to spot these before clicking anything. Hover, read the domain, then act.")

flags = [("\U0001F4E7", "Sender domain lies",
          "The domain is outside the organisation — or deliberately misspelled.", BAD, BADS),
         ("⏱", "Manufactured urgency",
          "A deadline or a threat exists purely to stop you thinking.", WARN, WARNS),
         ("\U0001F381", "Too good to be true",
          "An unearned prize or reward is the most classic lure of all.", BRAND, BRANDS),
         ("\U0001F517", "Link ≠ text",
          "The button label and the real destination are not the same place.", OK, OKS),
         ("\U0001F510", "Wants your secrets",
          "No real IT team or vendor asks for a password or OTP by email.", BAD, BADS)]
cw5 = (CW - 4 * 0.2) / 5
for i, (g, t, b, acc, soft) in enumerate(flags):
    x = M + (cw5 + 0.2) * i
    card(s, x, 2.14, cw5, 2.42)
    icon_badge(s, x + 0.3, 2.42, 0.5, g, acc, soft, size=15)
    tf = tb(s, x + 0.3, 3.06, cw5 - 0.6, 0.62)
    para(tf, t, size=12.5, bold=True, color=INK, first=True, line_spacing=1.15)
    tf = tb(s, x + 0.3, 3.72, cw5 - 0.6, 0.78)
    para(tf, b, size=10, color=INK2, first=True, line_spacing=1.3)

# live example strip
card(s, M, 4.74, CW, 1.94, fill=WHITE)
tf = tb(s, M + 0.36, 4.96, 5.4, 0.34)
para(tf, "LIVE EXAMPLE FROM THE APP", size=9.5, bold=True, color=BAD, first=True)
for r in tf.paragraphs[0].runs:
    r.font._rPr.set("spc", "140")
tf = tb(s, M + 0.36, 5.28, 6.2, 0.4)
para(tf, "no-reply@micorsoft-secure-auth.com", size=17, bold=True, color=BAD, first=True, font="Consolas")
tf = tb(s, M + 0.36, 5.72, 6.2, 0.78)
para(tf, "Reads like Microsoft. Attacks the eye, not the mind — people see the logo and the word "
         "“Microsoft” and stop reading the domain carefully.",
     size=11.5, color=INK2, first=True, line_spacing=1.32)
rect(s, M + 6.95, 5.0, 0.028, 1.42, fill=LINE)
tf = tb(s, M + 7.3, 4.98, CW - 7.7, 1.56)
para(tf, "The correct response", size=13.5, bold=True, color=INK, first=True)
for i, t in enumerate(["Read the domain letter by letter",
                       "Hover the link and read the real URL",
                       "Open the official site yourself",
                       "Report it — never silently delete it"]):
    para(tf, "→   " + t, size=11, color=INK2, space_before=6 if i else 8, line_spacing=1.26)
footer(s)

# ============================================================== 5 · SOLUTION
s = slide()
eyebrow(s, "Our solution")
heading(s, "PhishStudy — what we actually built",
        "One Python file, zero dependencies. It runs offline on any laptop, which is why it demos in seconds.")

feats2 = [("Admin console", "Launch a campaign from a template, add employees, watch KPIs move live.", BRAND),
          ("Fake employee inbox", "Phishing and genuine mail mixed, so staff must discriminate.", WARN),
          ("Fake login page", "A realistic SSO screen that records the credential submission.", BAD),
          ("Instant training", "Red-flag coaching on failure, praise on reporting, scored quiz.", OK)]
LEFT_W = CW * 0.435
cwf = (LEFT_W - 0.22) / 2
for i, (t, b, acc) in enumerate(feats2):
    x = M + (cwf + 0.22) * (i % 2)
    y = 2.14 + (1.34 + 0.2) * (i // 2)
    card(s, x, y, cwf, 1.34)
    rect(s, x, y + 0.14, 0.05, 1.06, fill=acc)
    tf = tb(s, x + 0.28, y + 0.24, cwf - 0.52, 0.32)
    para(tf, t, size=13, bold=True, color=INK, first=True)
    tf = tb(s, x + 0.28, y + 0.6, cwf - 0.52, 0.68)
    para(tf, b, size=10, color=INK2, first=True, line_spacing=1.28)

card(s, M, 5.06, LEFT_W, 1.42, fill=NAVY, line=None)
tf = tb(s, M + 0.34, 5.24, LEFT_W - 0.68, 1.1)
para(tf, "BUILT WITH", size=9, bold=True, color=RGBColor(0xA5, 0xB4, 0xFC), first=True)
para(tf, "Python 3 standard library only — http.server + sqlite3. No pip install, no internet, no database server.",
     size=11.5, color=WHITE, space_before=6, line_spacing=1.3)
para(tf, "python3 app.py  →  http://127.0.0.1:8000", size=10.5, bold=True,
     color=RGBColor(0xA5, 0xB4, 0xFC), space_before=7, font="Consolas")

screenshot(s, os.path.join(SHOTS, "dashboard.png"), M + LEFT_W + 0.3, 2.14,
           CW - LEFT_W - 0.3, 4.72,
           caption="Admin console — campaign funnel, outcome breakdown, per-department and per-employee results")
footer(s)

# ============================== 6 · WHAT THE EMPLOYEE SEES
s = slide()
eyebrow(s, "Inside the simulation")
heading(s, "What the employee actually sees",
        "Three real screens from the demo. Every one of them is recorded, and none of them can reach a real inbox.")

shots = [("mail.png", "1  ·  THE BAIT", "A realistic mail with a fake sender domain and a deadline. The open itself is logged.", BRAND),
         ("landing.png", "2  ·  THE TRAP", "A convincing SSO page on localhost. The click and any submitted field are logged.", BAD),
         ("educate.png", "3  ·  THE LESSON", "Instant coaching names each red flag they missed, then sends them to the quiz.", OK)]
cws = (CW - 2 * 0.26) / 3
for i, (f, lbl, desc, acc) in enumerate(shots):
    x = M + (cws + 0.26) * i
    chip(s, x, 2.08, 1.9, lbl, acc, RGBColor(0xF1, 0xF4, 0xF9), size=9)
    screenshot(s, os.path.join(SHOTS, f), x, 2.5, cws, 3.32)
    tf = tb(s, x, 6.04, cws, 0.72)
    para(tf, desc, size=11, color=INK2, first=True, line_spacing=1.3)
footer(s)

# ============================================================== 7 · WORKFLOW
s = slide()
eyebrow(s, "How it works")
heading(s, "The end-to-end workflow",
        "This is exactly the path we will click through during the live demonstration.")

steps = [("Launch", "Admin picks a template and sends it to every employee", BRAND),
         ("Receive", "Each employee gets a tracked mail in their fake inbox", WARN),
         ("React", "They open, click, submit or report — every step timestamped", BAD),
         ("Measure", "Dashboard recomputes rates and flags the highest-risk group", OK),
         ("Train", "Instant coaching, then a quiz whose score proves it worked", BRAND)]
cws = (CW - 4 * 0.16) / 5
for i, (t, b, acc) in enumerate(steps):
    x = M + (cws + 0.16) * i
    sh = rect(s, x, 2.2, cws, 0.62, fill=acc, shape=MSO_SHAPE.CHEVRON)
    tf = sh.text_frame
    tf.margin_left = tf.margin_right = 0
    tf.word_wrap = True
    para(tf, t.upper(), size=12, bold=True, color=WHITE, align=PP_ALIGN.CENTER, first=True)
    tf = tb(s, x + 0.12, 3.02, cws - 0.3, 1.1)
    para(tf, b, size=11.5, color=INK2, first=True, line_spacing=1.32)

card(s, M, 4.3, CW, 2.3, fill=WHITE)
tf = tb(s, M + 0.4, 4.5, 4.2, 0.34)
para(tf, "THE DEMONSTRATION SCRIPT", size=9.5, bold=True, color=BRAND, first=True)
for r in tf.paragraphs[0].runs:
    r.font._rPr.set("spc", "140")
demos = ["Open the Employee Inbox and choose any employee identity",
         "Open the phishing mail and follow the link",
         "Type any fake credentials on the login page",
         "Read the instant red-flag coaching screen",
         "Return to the dashboard — the rates have moved",
         "Report a second mail, then take the quiz"]
tf = tb(s, M + 0.4, 4.88, CW * 0.52, 1.6)
for i, t in enumerate(demos):
    p = para(tf, f"{i+1}.   {t}", size=11, color=INK2, first=(i == 0), space_before=0 if i == 0 else 5, line_spacing=1.26)
rect(s, M + CW * 0.585, 4.58, 0.028, 1.76, fill=LINE)
tf = tb(s, M + CW * 0.625, 4.56, CW * 0.33, 1.8)
para(tf, "Total demo time: 2 minutes", size=15, bold=True, color=INK, first=True)
para(tf, "Undergraduate project, no external network access, no real credentials and no real email "
         "delivery required — so it runs on any classroom laptop.",
     size=11.5, color=INK2, space_before=9, line_spacing=1.34)
footer(s)

# ============================================================== 7 · METRICS
s = slide()
eyebrow(s, "Methodology")
heading(s, "How we measure susceptibility",
        "Four rates, one funnel. The submission rate is the number that actually matters to a security team.")

metrics = [("Open rate", "opened ÷ sent", "Was the subject line or sender name convincing enough?", BRAND),
           ("Click rate", "clicked ÷ sent", "Did the lure and the call-to-action work?", WARN),
           ("Submission rate", "submitted ÷ sent", "KEY METRIC — the account would be fully compromised", BAD),
           ("Reporting rate", "reported ÷ sent", "Resilience — did they alert IT instead of acting?", OK)]
for i, (t, formula, b, acc) in enumerate(metrics):
    cwm = (CW - 3 * 0.24) / 4
    x = M + (cwm + 0.24) * i
    card(s, x, 2.14, cwm, 1.56)
    rect(s, x, 2.14, cwm, 0.06, fill=acc, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.5)
    tf = tb(s, x + 0.28, 2.36, cwm - 0.56, 0.3)
    para(tf, t, size=14, bold=True, color=INK, first=True)
    tf = tb(s, x + 0.28, 2.68, cwm - 0.56, 0.28)
    para(tf, formula, size=11, bold=True, color=acc, first=True, font="Consolas")
    tf = tb(s, x + 0.28, 3.02, cwm - 0.56, 0.6)
    para(tf, b, size=10.5, color=INK2, first=True, line_spacing=1.3)

# funnel chart
card(s, M, 3.94, CW * 0.62, 2.52, fill=WHITE)
tf = tb(s, M + 0.36, 4.16, 5.0, 0.3)
para(tf, "CAMPAIGN FUNNEL — BATCH A (8 EMPLOYEES)", size=9.5, bold=True, color=MUTED, first=True)
cd = CategoryChartData()
cd.categories = ["Phished", "Clicked", "Opened", "Sent"]
cd.add_series("Employees", (2, 4, 7, 8))
gf = s.shapes.add_chart(XL_CHART_TYPE.BAR_CLUSTERED, Inches(M + 0.2), Inches(4.46),
                        Inches(CW * 0.62 - 0.5), Inches(1.86), cd)
ch = gf.chart
ch.has_legend = False
ch.has_title = False
pl = ch.plots[0]
pl.gap_width = 58
pl.has_data_labels = True
dl = pl.data_labels
dl.font.size = Pt(11); dl.font.bold = True; dl.font.color.rgb = INK
dl.position = XL_LABEL_POSITION.OUTSIDE_END
ser = pl.series[0]
ser.format.fill.solid(); ser.format.fill.fore_color.rgb = BRAND
for idx, col in enumerate([BAD, WARN, RGBColor(0x25, 0x63, 0xEB), BRAND]):
    pt = ser.points[idx]
    pt.format.fill.solid(); pt.format.fill.fore_color.rgb = col
    pt.format.line.fill.background()
ca = ch.category_axis
ca.has_major_gridlines = False
ca.tick_labels.font.size = Pt(11); ca.tick_labels.font.color.rgb = INK2
ca.format.line.color.rgb = LINE
va = ch.value_axis
va.has_major_gridlines = False
va.visible = False
va.format.line.fill.background()

card(s, M + CW * 0.645, 3.94, CW * 0.355, 2.58, fill=BRANDS, line=RGBColor(0xD5, 0xD8, 0xFB))
tf = tb(s, M + CW * 0.645 + 0.34, 4.16, CW * 0.355 - 0.68, 2.2)
para(tf, "Reading the funnel", size=14.5, bold=True, color=INK, first=True)
para(tf, "Each step measures a different human decision. The gap between “Clicked” and “Phished” is where "
         "training pays off — the employee was curious but still stopped.",
     size=11, color=INK2, space_before=8, line_spacing=1.3)
para(tf, "The gap between “Clicked” and “Reported” is the culture problem: people engage with phish "
         "instead of warning the IT team.",
     size=11, color=INK2, space_before=8, line_spacing=1.3)
footer(s)

# ============================================================== 8 · RESULTS
s = slide()
eyebrow(s, "Results")
heading(s, "What the seeded campaign found",
        "16 targets across two templates. Replace these figures with your live run during the demonstration.")

card(s, M, 2.14, CW * 0.575, 3.02, fill=WHITE)
tf = tb(s, M + 0.36, 2.36, 5.6, 0.3)
para(tf, "OUTCOMES ACROSS ALL CAMPAIGNS", size=9.5, bold=True, color=MUTED, first=True)
cd = CategoryChartData()
cd.categories = ["Sent", "Opened", "Clicked", "Phished", "Reported"]
cd.add_series("Employees", (16, 13, 5, 3, 1))
gf = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(M + 0.24), Inches(2.66),
                        Inches(CW * 0.575 - 0.58), Inches(2.34), cd)
ch = gf.chart
ch.has_legend = False; ch.has_title = False
pl = ch.plots[0]; pl.gap_width = 62
pl.has_data_labels = True
dl = pl.data_labels
dl.font.size = Pt(11); dl.font.bold = True; dl.font.color.rgb = INK
dl.position = XL_LABEL_POSITION.OUTSIDE_END
ser = pl.series[0]
ser.format.line.fill.background()
for idx, col in enumerate([BRAND, RGBColor(0x25, 0x63, 0xEB), WARN, BAD, OK]):
    pt = ser.points[idx]
    pt.format.fill.solid(); pt.format.fill.fore_color.rgb = col
ca = ch.category_axis; ca.has_major_gridlines = False
ca.tick_labels.font.size = Pt(10.5); ca.tick_labels.font.color.rgb = INK2
ca.format.line.color.rgb = LINE
va = ch.value_axis; va.has_major_gridlines = False; va.visible = False
va.format.line.fill.background()

findings = [("18.8%", "submitted credentials", "3 of 16 targets handed over a username and password — "
             "in a real incident that is 3 compromised accounts.", BAD, BADS),
            ("31.2%", "clicked the link", "Curiosity beat caution. The HR bonus lure performed best on "
             "Finance and Sales.", WARN, WARNS),
            ("6.2%", "reported the mail", "Only one employee alerted IT. This is the weakest number in "
             "the whole study.", OK, OKS)]
for i, (v, lbl, b, acc, soft) in enumerate(findings):
    y = 2.14 + i * 1.1
    card(s, M + CW * 0.6, y, CW * 0.4, 0.98, fill=soft, line=None)
    tf = tb(s, M + CW * 0.6 + 0.3, y + 0.15, 1.5, 0.5)
    para(tf, v, size=22, bold=True, color=acc, first=True, line_spacing=1.0)
    tf = tb(s, M + CW * 0.6 + 1.78, y + 0.14, CW * 0.4 - 2.1, 0.3)
    para(tf, lbl, size=11.5, bold=True, color=INK, first=True)
    tf = tb(s, M + CW * 0.6 + 1.78, y + 0.4, CW * 0.4 - 2.1, 0.54)
    para(tf, b, size=9.5, color=INK2, first=True, line_spacing=1.26)

card(s, M, 5.56, CW, 1.1, fill=WHITE)
rect(s, M, 5.72, 0.055, 0.78, fill=BRAND)
tf = tb(s, M + 0.34, 5.76, CW - 0.7, 0.8)
para(tf, "Conclusion from the data", size=12.5, bold=True, color=INK, first=True)
para(tf, "Awareness alone did not prevent credential submission, but reporting behaviour is measurably "
         "improvable — which is exactly what the second campaign and the quiz are designed to test.",
     size=11.5, color=INK2, space_before=5, line_spacing=1.3)
footer(s)

# ============================================================== 9 · ETHICS
s = slide()
eyebrow(s, "Ethics & limits", color=OK)
heading(s, "Safe by design, not safe by accident",
        "A phishing tool is only acceptable in an educational setting under strict constraints.")

rules = [("Written consent", "Participants are told it is a study before it starts, and results are never "
          "used for punishment or appraisal.", OK, OKS),
         ("Fictional data only", "Every employee, mailbox and campaign is invented. No real names, no real "
          "addresses, no real passwords are ever stored.", BRAND, BRANDS),
         ("No real delivery", "The 'malicious' email and login page exist only inside this app on localhost. "
          "Nothing is sent to anybody.", WARN, WARNS),
         ("Immediate debrief", "Anyone who falls for the simulation is shown the red flags straight away, and "
          "the red-flag panel is available inside every email.", BAD, BADS)]
cwe = (CW - 3 * 0.24) / 4
for i, (t, b, acc, soft) in enumerate(rules):
    x = M + (cwe + 0.24) * i
    card(s, x, 2.14, cwe, 2.1)
    icon_badge(s, x + 0.3, 2.42, 0.5, "\U0001F6E1", acc, soft, size=15)
    tf = tb(s, x + 0.3, 3.06, cwe - 0.6, 0.34)
    para(tf, t, size=13.5, bold=True, color=INK, first=True)
    tf = tb(s, x + 0.3, 3.44, cwe - 0.6, 0.72)
    para(tf, b, size=10, color=INK2, first=True, line_spacing=1.3)

card(s, M, 4.42, CW * 0.615, 2.12, fill=NAVY, line=None)
tf = tb(s, M + 0.42, 4.66, CW * 0.615 - 0.84, 1.7)
para(tf, "Limitations we acknowledge", size=13.5, bold=True, color=WHITE, first=True)
for i, t in enumerate(["A self-selected group of 8 fictional employees is not a statistically valid workforce sample",
                       "No real email headers, SPF/DKIM failures or malicious attachments are modelled yet",
                       "Only email phishing — no SMS, QR-code or voice-call (smishing / vishing) variants"]):
    para(tf, "•   " + t, size=11.5, color=RGBColor(0xB6, 0xC2, 0xD9), space_before=9 if i == 0 else 6, line_spacing=1.3)

card(s, M + CW * 0.64, 4.42, CW * 0.36, 2.12, fill=BADS, line=RGBColor(0xF7, 0xC9, 0xC9))
tf = tb(s, M + CW * 0.64 + 0.36, 4.66, CW * 0.36 - 0.72, 1.8)
para(tf, "If this were deployed for real", size=13.5, bold=True, color=RGBColor(0xB1, 0x1D, 0x1D), first=True)
para(tf, "It would require written authorisation from management, a privacy-impact assessment, "
         "guaranteed non-punitive reporting, and a debrief session for every participant.",
     size=11.5, color=RGBColor(0x7F, 0x1D, 0x1D), space_before=9, line_spacing=1.34)
footer(s)

# ============================================================== 10 · CLOSING
s = slide(dark=True)
rect(s, 0, 0, W, 0.09, fill=BRAND)
rect(s, 10.4, 4.1, 5.4, 5.4, fill=NAVY2, shape=MSO_SHAPE.OVAL)
eyebrow(s, "Conclusion", color=RGBColor(0xA5, 0xB4, 0xFC))
tf = tb(s, M, 1.06, 9.4, 1.1)
para(tf, "Measure it. Train it. Repeat it.", size=40, bold=True, color=WHITE, first=True, line_spacing=1.05)
tf = tb(s, M, 1.96, 8.6, 0.8)
para(tf, "Our study showed that even careful employees fall for a convincing phish — but every report "
         "and every correct quiz answer moves the number.",
     size=15, color=RGBColor(0xB6, 0xC2, 0xD9), first=True, line_spacing=1.34)

take = [("18.8%", "phished", "Baseline measured on 16 targets", BAD),
        ("6.2%", "reported", "The number training must raise", WARN),
        ("5", "red flags", "Taught, quizzed and reinforced", OK)]
cwt = (CW - 2 * 0.24) / 3
for i, (v, lbl, b, acc) in enumerate(take):
    x = M + (cwt + 0.24) * i
    rect(s, x, 3.06, cwt, 1.46, fill=NAVY2, line=NAVY3, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.06)
    tf = tb(s, x + 0.34, 3.26, cwt - 0.68, 0.55)
    para(tf, v, size=27, bold=True, color=acc, first=True, line_spacing=1.0)
    tf = tb(s, x + 0.34, 3.82, cwt - 0.68, 0.28)
    para(tf, lbl.upper(), size=10.5, bold=True, color=WHITE, first=True)
    tf = tb(s, x + 0.34, 4.12, cwt - 0.68, 0.3)
    para(tf, b, size=10, color=RGBColor(0x8B, 0x98, 0xB0), first=True)

tf = tb(s, M, 4.86, 10.4, 0.9)
para(tf, "Next steps", size=11, bold=True, color=RGBColor(0xA5, 0xB4, 0xFC), first=True)
para(tf, "Repeat the campaign after training to prove the submission rate drops  ·  add SMS and QR-code "
         "phishing variants  ·  track MFA adoption as a second metric",
     size=11.5, color=RGBColor(0xB6, 0xC2, 0xD9), space_before=6, line_spacing=1.3)

rect(s, M, 6.06, CW, 0.02, fill=NAVY3)
tf = tb(s, M, 6.28, 8.6, 0.9)
para(tf, "Live demo:  python3 app.py  →  http://127.0.0.1:8000", size=14, bold=True,
     color=RGBColor(0xA5, 0xB4, 0xFC), first=True)
para(tf, "Thank you — questions welcome", size=12, color=RGBColor(0x7C, 0x8A, 0xA3), space_before=4)
tf = tb(s, W - M - 4.0, 6.34, 4.0, 0.6)
para(tf, "GROUP NO. 2", size=11, bold=True, color=WHITE, align=PP_ALIGN.RIGHT, first=True)
para(tf, "Cyber Security Mini Project", size=10, color=RGBColor(0x7C, 0x8A, 0xA3),
     align=PP_ALIGN.RIGHT, space_before=3)

prs.save(OUT)
print("saved", OUT, "slides:", len(prs.slides.__iter__.__self__._sldIdLst))