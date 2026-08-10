# RKW Newsletter — RK World Category Intelligence

This repository produces the **RK World Category Intelligence** newsletter for RK World Infocom: a daily brand-news digest across the five categories the company sells on Amazon India (Beauty, Luxury Beauty, Grocery, Baby, Health & Personal Care), plus the Marketplaces and Quick Commerce channels.

## Files

| File | Purpose |
|---|---|
| `RK_World_Category_Intelligence.html` | The current issue (styled HTML, email/web ready) |
| `RK_World_Category_Intelligence.md` | Markdown version of the same issue — keep in sync with the HTML |
| `newsletter_template.html` | Reusable placeholder template (`{{ISSUE_DATE}}`, `{{BRAND_NAME}}`, …) for new issues |
| `CLAUDE.md` | This file — the generation rules |

Always update the HTML and the Markdown together; they must carry identical content.

## The news window rule (most important)

- **Only stories published within the last 2 days of the issue date may appear as news.** (The Aug 06, 2026 issue uses Aug 04–06.) State the window in the date line ("News window: …") and in the footer.
- A story with a publication date **outside** the window, or with **no verifiable date**, must never be presented as current news.
- Do not silently drop stale stories either — demote them into the bracket format below.

## Row formats

Every brand/platform row is numbered and **always carries a story with its source and date** — the page must never read as a list of "No major news today":

1. **News inside the window** (`news` in the content JSON):
   `**Brand** — <story text>. (Source Name, D Mon YYYY)`
2. **Latest story outside the window** (`recent`) — same format; the date shown tells the reader its age:
   `**Brand** — <story text>. (Source Name, date)`
3. The grey `No major news today (…)` forms still exist in the generator but are a **last resort** — only for a brand that must appear and truly has no story on record. Prefer swapping in a different brand that has one.

Rank rows: in-window stories first (by weight), then recent stories by freshness.

## Structure of an issue

1. **Header** — title and date line (issue date · news window · categories · total brands/listings). No methodology note under the date line — the user removed it; do not add it back.
2. **Executive Summary** (blue-bordered box) — only in-window stories may be summarised as news; if the cycle is quiet, say so plainly.
3. **Sections in order** — Marketplaces (Amazon & Flipkart), Beauty, Luxury Beauty, Grocery, Baby, Health & Personal Care, Quick Commerce (Blinkit, Instamart, Zepto). Each category heading carries its brand/listing counts.
4. **Per-section "Not in our portfolio" callout** (green box) — catalogue/selection analysis, not news; it is allowed to persist across issues unchanged.
5. **Footer** — "RK World Infocom | Confidential — internal use only | News items cover stories published <window> only".

## Brand selection (news-first)

- Do **not** use a fixed brand list per category. For each issue, research the whole category (any brand that sells or plausibly sells on Amazon India) and fill the top 5 rows with brands that **have news inside the window**, ranked by story weight.
- Only if fewer than 5 brands have in-window news, fill the remaining slots with the category's widest-catalogue brands as "No major news today (last major news: …)" rows.
- **Story types that count as news** (must still be published inside the window by an editorial outlet): funding, M&A, results/filings, regulatory/legal, leadership changes — and, when hard news is scarce, editorially covered product launches, ad campaigns, brand ambassadors, retail expansion and appointments (trade press like afaqs, exchange4media, ET BrandEquity, IndiaRetailing counts). Flag the softer items' source tier inline.
- Research broadly on quiet days (weekends especially): sweep D2C results trackers (Entrackr fintrackr, Inc42), trade/campaign press, exchange-filing coverage and wires before concluding a category is quiet. A "No major news today" row is a last resort, not a default.
- This keeps the issue carrying real data every day instead of a page of "No major news today".

## Style
- Sources the issues treat as trusted: Business Standard, Economic Times, Mint, Inc42, Entrackr, afaqs, ThePrint. Flag weaker ones inline (company blogs "treat as marketing", portals with commercial ties, franchise brokerages).
- Currency in ₹ Cr; growth as % YoY; keep the em-dash prose style of existing issues.
- HTML styling lives inline in `<style>` in each issue file (blue #1a56db accents, `.quiet` grey italics for no-news rows, `.gap` green callouts). Reuse it as-is from `newsletter_template.html`.

## Workflow

- Work on the designated `claude/…` branch, commit with descriptive messages, and push with `git push -u origin <branch>`.
- When the user uploads a revised issue HTML, adopt it as the repo's HTML verbatim, regenerate the Markdown to match, and note any wording it changed (e.g. window phrasing) rather than reverting it.
- Deliverables the user commonly asks for: the HTML, the Markdown, and a zip of both (plus the template). Build zips in the session scratchpad, not in the repo.
