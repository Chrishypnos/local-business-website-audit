---
name: local-business-website-audit
description: Run a Hypnos AI local search and website audit for a small business - Open SEO research, branded PDF report, and client AI audit questionnaire.
---

# Local business website audit (Hypnos AI)

Use when someone gives a local business's website (often with Semrush / Open SEO screenshots) and wants to know what is ranking, what is missing locally, and a client-ready report plus questionnaire.

Deliverables, in this order:
1. A branded PDF: "<Business> - Website & Search Visibility Report" (8-11 pages), built with `scripts/build_report.py`.
2. A client questionnaire: "<Business> - AI & Growth Audit Questionnaire" (a Claude Docs artifact if available, otherwise a .docx).
3. A short chat summary of the key findings and anything the user should verify themselves.

Tone: client-facing, factual, plain English. Let the numbers make the case. Never attack the current web agency by name; state facts (spend, results, account ownership).

Requirements: the Open SEO connector (research), Python with reportlab, matplotlib and pillow (PDF). Semrush data is optional and usually comes from the user's screenshots.

## Step 1 - Understand the business
- WebFetch the homepage and contact page. Capture: business name, owner, services, address(es), phone, email, service area, licenses/certifications, reviews, CTAs, forms, chat widget, platform (wp-content/Elementor = WordPress, Wix, Squarespace, Base44, etc.), footer credit ("Designed by ..." = the agency), and whether there is a privacy policy, terms, accessibility statement, cookie notice, and SMS consent near forms.
- Don't assume the industry from the name.
- If the site is JavaScript-rendered, WebFetch returns only metadata; rely on the JS-rendered audit.
- Compare the canonical URL with the website on the Google Business Profile. A mismatch (site on one domain, Google/canonical pointing at another) is a critical finding; test whether the other domain loads.

## Step 2 - Open SEO research (one project per client)
1. `list_projects`, then `create_project` (name "<Business> (<City ST>)", domain, locationCode 2840 for the US).
2. `get_domain_overview` and `get_ranked_keywords` (limit 100; resultTypes organic, local_pack, ai_overview_reference).
3. `get_backlinks_overview` - note spam scores and link-seller domains.
4. `run_site_audit` (maxPages 50-100, runLighthouse true; renderJavaScript true if the site is a JS app or a plain crawl sees only 1 page). Poll `get_audit_status`, then `get_audit_pages`, `get_audit_issues`, `get_audit_lighthouse` (mobile).
5. Google Business Profile: `search_local_businesses` with query = business name near the city center (radius 50-60 km), then `get_business_profile` by cid. Check name formatting, primary category, reviews, photos, address (home address shown?), website link. Watch for other listings at the same address or mailbox.
6. Local SERPs: `get_local_serp_results` from the city center (zoom 12-13) for 2-3 core service terms. Record the client's rank (or "not in top 20") and the top competitors' ratings and review counts.
7. Competitor domains: `search_local_businesses` with the business category, sortBy reviews, to get domains; then `get_domain_overview` on 3-5 local independents. Exclude national franchises (SERVPRO, Paul Davis, CertaPro, Five Star, That 1 Painter, etc.) from the traffic chart because their numbers cover many locations.
8. Demand: `search_serp_locations` for the county, then `get_keyword_metrics` with locationName for ~40 service, "near me", town and cost keywords. Note volume, KD, CPC, and whether the site has a matching page.
9. Organic SERPs: `get_serp_results` for "<service> <city>" and the brand name. If the site doesn't show for its own name, say so.
- Keep credit batches under ~2,000; ask before larger runs.
- Suggest connecting Search Console (Open SEO gives a link) for real Google data.

## Step 3 - Legal and compliance check (always include)
Check for: privacy policy, terms and conditions, accessibility statement, cookie/tracking notice, SMS consent on forms, and any state-required license or registration display (e.g. NJ Home Improvement Contractor number on all advertisements, N.J.A.C. 13:45A-17.11).

Re-verify these figures with WebSearch before every report (as of Nov 2026):
- ADA website lawsuits: about 3,117 federal filings in 2025, 5,000+ including state courts; Florida had 961 federal filings (second to New York). Average out-of-court settlement about $25K-$30K.
- Example: Leaf & Blossom, Co. (Orlando flower shop) paid $7,000+ in late 2024; its site was managed by a third party.
- DOJ ADA Title III civil penalty maximum: $118,225 first violation, $236,451 subsequent (28 CFR 36.504, July 2025). DOJ only and rare; private plaintiffs get injunctions plus attorney's fees.
- TCPA: $500 per unlawful text or call, up to $1,500 if willful; Florida's FTSA adds a state claim.
- Carriers reject A2P 10DLC business texting without a public privacy policy, terms and SMS opt-in, which blocks review requests and AI follow-up texts.

Always say "not legal advice; have a licensed attorney review final policies", and be honest that the main risk is lawsuits and settlements, not government fines.

Include anything the user tests by hand: an unanswered website chat goes in a red callout with the 2007 MIT/InsideSales study (contact within 5 minutes vs 30 gives 100x the odds of reaching and 21x the odds of qualifying; say "qualify", not "close"). A low-resolution logo goes in the website section with the user's screenshot.

## Step 4 - Build the PDF
1. Copy `examples/example-config.json` to the working folder and fill it with the real findings. Block types: `lead`, `paragraph`, `heading`, `bullets`, `small`, `spacer`, `kpis` (3x2 big red numbers), `table` (columns, rows, widths as fractions, optional highlight_row), `bar_chart` (rows `[label, value, is_client]`; client bar blue, others grey; optional note, source, width), `callout` (red or blue box), `image` (screenshots), `plan` (30/60/90 phases), `targets`, `contact`, `page_break`.
2. Set `brand.logo` to the absolute path of `assets/hypnos-logo.png` in this skill folder (or another logo).
3. Run: `python3 <skill-folder>/scripts/build_report.py config.json "<Business>-Website-Report.pdf"`.

Section order (each starts on a new page):
- "What your website does today": lead, KPI grid (visitors/month, ranking keywords, Maps position, Google reviews, Authority Score, AI mentions), "The good news" (3 honest positives).
- 1. Website traffic: client vs 3-5 local competitors bar chart; cost per visitor if the monthly marketing spend is known; what a visitor is worth (CPCs); red callouts for critical issues.
- 2. What the site ranks for / what people search for: ranked keywords (flag ones that belong to other companies) and a demand table (term, searches, difficulty, CPC, page on site?).
- 3. Google Maps and reviews: review-count chart, Maps rank table with the client row highlighted, Business Profile fixes.
- 4. AI search visibility and 5. Backlinks and trust (Semrush vs Open SEO, good links, links to review, address/phone conflicts, credentials to show off).
- 6. Website health check: audit summary, issues table, other findings.
- 7. Legal and compliance risk: status table (Missing in red), real examples table, the fix, sources line.
- 8. What we recommend: 30/60/90 plan, 90-day targets, contact block.
- Appendix: the user's Semrush and Open SEO screenshots.

Quality check before sending: render pages with `pdftoppm` and look at every page. If a section spills a line or two onto a new page, tighten text, merge minor table rows or shrink a chart (`width`). Never leave a near-empty page. Keep long competitor names short so chart labels aren't clipped.

## Step 5 - Questionnaire
Byline, a short intro ("Please type your answers in the right-hand column, or we can go through it on a 30-minute call"), then tables with columns #, Question, Your answer. Adapt to the industry:
1. Business basics and goals: legal name, years in business, licenses/registration and insurance, services, most profitable jobs, average job value, capacity, towns, revenue goal, seasonality.
2. Website, web addresses and Google profile: who built it and holds the logins, domain ownership, which address is real, Google profile access, home vs office address, directory listings, Search Console/Analytics. Turn every audit red flag into a neutral question.
3. Leads, estimates and follow-up: lead sources (%), volume and close rate, who answers calls, after-hours, form response speed, estimate process, follow-up, paid lead sites.
4. Jobs, tools and reviews: CRM/scheduling/invoicing, team size, review requests, past-customer list size, referrals, time drains.
5. Marketing, compliance and AI readiness: current spend and what it covers, past SEO/link vendors, agency contract, texting today, comfort with an AI voice agent and automated texts, no-go topics for automation, budget, what a 90-day win looks like.

End with: "Next step: once we have your answers, we'll come back with a prioritized plan and pricing within 3 business days. Questions: Chris, (201) 800-4647 - support@hypnos-ai.com - hypnos-ai.com".

## Step 6 - Wrap-up message
A few bullets on the headline findings, what the user should verify by hand (anything the tools couldn't reach, form widgets, chat tests), the Open SEO Search Console link, and the file names. If the client's current agency fee is known, add the pitch angle: cost per visitor, and a rebuild-included retainer with every account owned by the client.
