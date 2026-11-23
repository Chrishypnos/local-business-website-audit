# Local Business Website Audit — a Claude skill by Hypnos AI

Point Claude at any local business website and get back:

1. **A branded PDF report** — "Website & Search Visibility Report": Google traffic vs. local competitors, what the site ranks for, Google Maps position and review gap, AI search visibility (ChatGPT, Gemini, Google AI Overviews), backlink quality, a technical health check, legal and compliance risks (privacy policy, terms, ADA accessibility, SMS consent) with real fine examples, and a 30/60/90-day plan.
2. **A client questionnaire** — "AI & Growth Audit Questionnaire" that turns every red flag into a question for the owner.
3. **A short summary** of headline findings and what to verify by hand.

**See a sample:** [Example Plumbing Co. report (PDF)](examples/sample-report-plumbing.pdf) — a fictional plumbing company with illustrative data.

Built by [Chris Fotomaras](https://hypnos-ai.com) at **Hypnos AI** as part of a build-in-public series of small-business automations.

## What you need

- [Claude](https://claude.ai) with skills enabled (or Claude Code)
- The **Open SEO** connector (for rankings, Maps, backlinks, site audit and keyword data)
- Optional: Semrush screenshots for Authority Score and AI visibility
- Python 3 with `reportlab`, `matplotlib`, `pillow` (Claude's workspace already has them)

## Install

**Claude (web / desktop):** download this repo as a ZIP (Code → Download ZIP), then go to **Customize → Skills → Upload** and upload the ZIP.

**Claude Code:** clone into your skills folder:

```bash
git clone https://github.com/Chrishypnos/local-business-website-audit ~/.claude/skills/local-business-website-audit
```

## Use

> Run a local business website audit for **examplebusiness.com**. Here are my Semrush screenshots.

Claude researches the site, builds the PDF and the questionnaire, and tells you what to check yourself.

## Build a report by hand

```bash
python3 scripts/build_report.py examples/plumbing-config.json my-report.pdf
```

- `examples/plumbing-config.json` — a full 8-section report (the one behind the sample PDF).
- `examples/example-config.json` — a shorter template showing every block type (KPI grid, bar charts, tables, callouts, 30/60/90 plan, contact block).

Both use fictional businesses. Set `"report_label"` to change the small line above the business name on the cover.

## Make it yours

The report is branded for Hypnos AI. To use your own brand, change the `brand` block in the config (name, logo, website, email, phone, contact name) and replace `assets/hypnos-logo.png`.

## Repo layout

```
SKILL.md                    the instructions Claude follows
scripts/build_report.py     JSON config -> branded PDF
examples/plumbing-config.json      full sample config
examples/sample-report-plumbing.pdf
examples/example-config.json       short template
assets/hypnos-logo.png
```

## Disclaimer

The legal section is general information, not legal advice. Have a licensed attorney review any policy before publishing it. Re-check fine and lawsuit figures before each report.

## Contact

Hypnos AI · [hypnos-ai.com](https://hypnos-ai.com) · support@hypnos-ai.com · (201) 800-4647

MIT License
