#!/usr/bin/env python3
"""Build a branded "Website & Search Visibility Report" PDF from a JSON config.

Usage:
    python3 build_report.py config.json output.pdf

See examples/example-config.json for every supported block type.
Requires: reportlab, matplotlib, pillow.
"""
import json
import os
import sys
import tempfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle)

# ---------- fonts (Carlito if available, else Helvetica) ----------
FONT_DIR_CANDIDATES = ["/usr/share/fonts/truetype/crosextra/", os.path.join(os.path.dirname(__file__), "../assets/fonts/")]
BASE, BOLD, ITAL = "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"
MPL_FONT = None
for d in FONT_DIR_CANDIDATES:
    reg = os.path.join(d, "Carlito-Regular.ttf")
    if os.path.exists(reg):
        pdfmetrics.registerFont(TTFont("Carlito", reg))
        pdfmetrics.registerFont(TTFont("Carlito-Bold", os.path.join(d, "Carlito-Bold.ttf")))
        pdfmetrics.registerFont(TTFont("Carlito-Italic", os.path.join(d, "Carlito-Italic.ttf")))
        registerFontFamily("Carlito", normal="Carlito", bold="Carlito-Bold", italic="Carlito-Italic")
        BASE, BOLD, ITAL = "Carlito", "Carlito-Bold", "Carlito-Italic"
        for f in ["Carlito-Regular.ttf", "Carlito-Bold.ttf"]:
            fm.fontManager.addfont(os.path.join(d, f))
        MPL_FONT = "Carlito"
        break
if MPL_FONT:
    plt.rcParams["font.family"] = MPL_FONT

INK = colors.HexColor("#1A1A1A")
MUTED = colors.HexColor("#6B6B6B")
ACCENT = colors.HexColor("#1F6FD1")
RED = colors.HexColor("#C0392B")
LINE = colors.HexColor("#DADAD4")
SOFT = colors.HexColor("#F4F4F0")
NAVY = colors.HexColor("#0F1F33")

SS = {
    "h1": ParagraphStyle("h1", fontName=BOLD, fontSize=22, leading=26, textColor=INK, spaceAfter=6),
    "h2": ParagraphStyle("h2", fontName=BOLD, fontSize=16, leading=20, textColor=INK, spaceBefore=8, spaceAfter=6),
    "lead": ParagraphStyle("lead", fontName=BASE, fontSize=12.5, leading=17, textColor=INK, spaceAfter=8),
    "body": ParagraphStyle("body", fontName=BASE, fontSize=11, leading=15, textColor=INK, spaceAfter=6),
    "small": ParagraphStyle("small", fontName=BASE, fontSize=9, leading=12, textColor=MUTED),
    "cell": ParagraphStyle("cell", fontName=BASE, fontSize=10, leading=13, textColor=INK),
    "cellb": ParagraphStyle("cellb", fontName=BOLD, fontSize=10, leading=13, textColor=INK),
    "hdr": ParagraphStyle("hdr", fontName=BOLD, fontSize=9.5, leading=12, textColor=MUTED),
    "bul": ParagraphStyle("bul", fontName=BASE, fontSize=11, leading=15, textColor=INK, leftIndent=14,
                          bulletIndent=2, spaceAfter=3),
    "kpi": ParagraphStyle("kpi", fontName=BOLD, fontSize=26, leading=28, textColor=RED, alignment=TA_LEFT),
    "kpil": ParagraphStyle("kpil", fontName=BASE, fontSize=10, leading=12.5, textColor=INK),
}
W = letter[0] - 1.5 * inch
TMP = tempfile.mkdtemp(prefix="lbwa_")


def P(t, s="body"):
    return Paragraph(t, SS[s])


def bullets(items):
    return [Paragraph(i, SS["bul"], bulletText="•") for i in items]


def img(path, width=W):
    w, h = PILImage.open(path).size
    return Image(path, width=width, height=width * h / w)


def table(columns, rows, widths=None, highlight=None):
    data = [[P(c, "hdr") for c in columns]]
    for i, r in enumerate(rows, 1):
        st = "cellb" if highlight == i else "cell"
        data.append([P(str(c), st) for c in r])
    if widths:
        widths = [W * f for f in widths]
    t = Table(data, colWidths=widths, repeatRows=1)
    style = [("LINEBELOW", (0, 0), (-1, 0), 0.8, INK), ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINE),
             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 5),
             ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 4)]
    if highlight:
        style.append(("BACKGROUND", (0, highlight), (-1, highlight), colors.HexColor("#EAF2FC")))
    t.setStyle(TableStyle(style))
    return t


def kpi_grid(items):
    cells = [[P(str(v), "kpi"), Spacer(1, 4), P(label, "kpil")] for v, label in items]
    rows = [cells[i:i + 3] for i in range(0, len(cells), 3)]
    while len(rows[-1]) < 3:
        rows[-1].append("")
    t = Table(rows, colWidths=[W / 3] * 3)
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), SOFT), ("LINEAFTER", (0, 0), (-2, -1), 6, colors.white),
                           ("LINEBELOW", (0, 0), (-1, -2), 6, colors.white), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("TOPPADDING", (0, 0), (-1, -1), 12), ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                           ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 10)]))
    return t


def callout(title, paragraphs, tone="red"):
    fill, edge, tc = ("#FDF1EF", RED, "#C0392B") if tone == "red" else ("#EAF2FC", ACCENT, "#1F6FD1")
    rows = [[P(f"<font color='{tc}'><b>{title}</b></font>", "h2")]] + [[P(p, "body")] for p in paragraphs]
    t = Table(rows, colWidths=[W])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(fill)), ("LINEBEFORE", (0, 0), (0, -1), 4, edge),
                           ("LEFTPADDING", (0, 0), (-1, -1), 14), ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                           ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                           ("TOPPADDING", (0, 0), (-1, 0), 10), ("BOTTOMPADDING", (0, -1), (-1, -1), 10)]))
    return KeepTogether([t])


_chart_n = [0]


def bar_chart(title, subtitle, rows, unit, note=None):
    """rows: [[label, value, is_client], ...] top to bottom. Client bar is blue, others grey."""
    grey, accent, text, muted = "#C4C6BC", "#1F6FD1", "#1A1A1A", "#6B6B6B"
    rows = rows[::-1]
    n = len(rows)
    H = 0.6 * n + 1.6 + (0.4 if note else 0)
    fig, ax = plt.subplots(figsize=(8, H), dpi=200)
    mx = max(r[1] for r in rows) or 1
    for i, (lab, v, c) in enumerate(rows):
        w = max(v, mx * 0.005)
        ax.barh(i, w, height=0.62, color=accent if c else grey)
        txt = f"{v:,} {unit}" if c else f"{v:,}"
        ax.text(w + mx * 0.012, i, txt.replace("$", "\\$"), va="center", fontsize=12,
                color=accent if c else text, fontweight="bold" if c else "normal")
    ax.set_yticks(range(n))
    ax.set_yticklabels([r[0] for r in rows], fontsize=12)
    for tick, r in zip(ax.get_yticklabels(), rows):
        tick.set_color(text if r[2] else muted)
        if r[2]:
            tick.set_fontweight("bold")
    ax.set_xlim(0, mx * 1.25)
    ax.set_ylim(-0.6, n - 0.4)
    ax.xaxis.set_visible(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.tick_params(left=False)
    fig.text(0.02, 1 - 0.18 / H, title.replace("$", "\\$"), fontsize=17, fontweight="bold", color=text, va="top")
    fig.text(0.02, 1 - 0.55 / H, subtitle.replace("$", "\\$"), fontsize=11.5, color=muted, va="top")
    if note:
        fig.text(0.30, 0.18 / H, note.replace("$", "\\$"), fontsize=11.5, color=muted)
    fig.subplots_adjust(left=0.30, right=0.97, top=1 - 0.95 / H, bottom=(0.55 if note else 0.15) / H)
    _chart_n[0] += 1
    path = os.path.join(TMP, f"chart{_chart_n[0]}.png")
    fig.savefig(path)
    plt.close(fig)
    return path


def resolve(path, base):
    return path if os.path.isabs(path) else os.path.normpath(os.path.join(base, path))


def build(cfg, out, base):
    biz, brand = cfg["business"], cfg["brand"]
    logo = resolve(brand["logo"], base)
    date = cfg.get("date", "")
    footer_left = f"{biz['name']} — Website Report · {cfg.get('short_date', date)}"
    footer_right = f"{brand['name']} · {brand['website']} · {brand['email']}"
    lw_px, lh_px = PILImage.open(logo).size

    def on_page(c, doc):
        c.saveState()
        c.setFont(BASE, 8.5)
        c.setFillColor(MUTED)
        c.drawString(0.75 * inch, 0.5 * inch, footer_left)
        c.drawRightString(letter[0] - 0.75 * inch, 0.5 * inch, f"{footer_right} · Page {doc.page}")
        c.restoreState()

    def on_cover(c, doc):
        c.saveState()
        c.setFillColor(NAVY)
        c.rect(0, letter[1] - 3.1 * inch, letter[0], 3.1 * inch, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont(BASE, 11)
        c.drawString(0.75 * inch, letter[1] - 0.9 * inch, cfg.get("report_label", "WEBSITE & SEARCH VISIBILITY REPORT"))
        c.setFont(BOLD, 32)
        c.drawString(0.75 * inch, letter[1] - 1.55 * inch, biz["name"])
        c.setFont(BASE, 14)
        c.drawString(0.75 * inch, letter[1] - 1.95 * inch, f"{biz['domain']}  ·  {biz['location']}")
        c.setFont(BASE, 11)
        c.setFillColor(colors.HexColor("#B8C4D4"))
        c.drawString(0.75 * inch, letter[1] - 2.55 * inch, f"Prepared by {brand['name']} for {cfg.get('prepared_for', biz['name'])}  ·  {date}")
        lw = 1.55 * inch
        lh = lw * lh_px / lw_px
        x = letter[0] - 0.75 * inch - lw - 0.4 * inch
        y = letter[1] - 0.45 * inch - lh - 0.4 * inch
        c.setFillColor(colors.white)
        c.roundRect(x, y, lw + 0.4 * inch, lh + 0.4 * inch, 8, stroke=0, fill=1)
        c.drawImage(logo, x + 0.2 * inch, y + 0.2 * inch, lw, lh, mask="auto")
        c.setFillColor(colors.HexColor("#B8C4D4"))
        c.setFont(BASE, 10)
        c.drawRightString(letter[0] - 0.75 * inch, letter[1] - 2.55 * inch, f"{brand['website']}  ·  {brand['email']}")
        c.restoreState()
        on_page(c, doc)

    doc = BaseDocTemplate(out, pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                          topMargin=0.75 * inch, bottomMargin=0.8 * inch,
                          title=f"{biz['name']} — Website & Search Visibility Report", author=brand["name"])
    doc.addPageTemplates([
        PageTemplate("cover", [Frame(0.75 * inch, 0.8 * inch, W, letter[1] - 4.2 * inch, id="c")], onPage=on_cover),
        PageTemplate("normal", [Frame(0.75 * inch, 0.8 * inch, W, letter[1] - 1.55 * inch, id="n")], onPage=on_page)])

    def contact_block():
        t = Table([[Image(logo, width=1.1 * inch, height=1.1 * inch * lh_px / lw_px),
                    [P("<b>Questions? Let's talk.</b>", "body"),
                     P(f"{brand['contact_name']}, {brand['name']}<br/>{brand['phone']} · "
                       f"<link href='mailto:{brand['email']}' color='#1F6FD1'>{brand['email']}</link> · "
                       f"<link href='https://{brand['website']}' color='#1F6FD1'>{brand['website']}</link>", "body")]]],
                  colWidths=[1.4 * inch, W - 1.4 * inch])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEABOVE", (0, 0), (-1, 0), 0.5, LINE),
                               ("TOPPADDING", (0, 0), (-1, -1), 12)]))
        return KeepTogether([t])

    def render_block(b):
        t = b["type"]
        if t == "paragraph":
            return [P(b["text"], "body")]
        if t == "lead":
            return [P(b["text"], "lead")]
        if t == "small":
            return [P(b["text"], "small")]
        if t == "heading":
            return [P(b["text"], "h2")]
        if t == "bullets":
            return bullets(b["items"])
        if t == "spacer":
            return [Spacer(1, b.get("height", 10))]
        if t == "table":
            return [table(b["columns"], b["rows"], b.get("widths"), b.get("highlight_row"))]
        if t == "kpis":
            return [kpi_grid(b["items"])]
        if t == "bar_chart":
            path = bar_chart(b["title"], b["subtitle"], b["rows"], b.get("unit", ""), b.get("note"))
            out = [img(path, W * b.get("width", 1.0))]
            if b.get("source"):
                out.append(P(b["source"], "small"))
            return out
        if t == "callout":
            return [callout(b["title"], b["paragraphs"], b.get("tone", "red"))]
        if t == "image":
            return [img(resolve(b["path"], base), W * b.get("width", 1.0))]
        if t == "targets":
            tt = Table([[P(f"<b>{b.get('label', '90-day targets')}</b>", "cellb"), P(b["text"], "cell")]],
                       colWidths=[1.4 * inch, W - 1.4 * inch])
            tt.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EAF2FC")),
                                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 10),
                                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10), ("LEFTPADDING", (0, 0), (-1, -1), 10)]))
            return [tt]
        if t == "plan":
            out = []
            for phase in b["phases"]:
                out.append(KeepTogether([P(phase["title"], "h2")] + bullets(phase["items"])))
            return out
        if t == "contact":
            return [contact_block()]
        if t == "page_break":
            return [PageBreak()]
        raise ValueError(f"Unknown block type: {t}")

    story = [NextPageTemplate("normal"), Spacer(1, 4)]
    for i, sec in enumerate(cfg["sections"]):
        if i > 0:
            story.append(PageBreak())
        story.append(P(sec["title"], "h1"))
        if sec.get("lead"):
            story.append(P(sec["lead"], "lead"))
        for b in sec.get("blocks", []):
            story += render_block(b)
    doc.build(story)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    cfg_path = sys.argv[1]
    with open(cfg_path) as f:
        cfg = json.load(f)
    build(cfg, sys.argv[2], os.path.dirname(os.path.abspath(cfg_path)))
    print(f"Built {sys.argv[2]}")
