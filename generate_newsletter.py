#!/usr/bin/env python3
"""Generate the RK World Category Intelligence newsletter (HTML + Markdown).

Usage:
    python3 generate_newsletter.py content_2026-08-07.json

Reads the edition content from the JSON file given on the command line
(defaults to the newest content_*.json next to this script) and writes

    RK_World_Category_Intelligence_<issue-date>.html
    RK_World_Category_Intelligence_<issue-date>.md

into the same directory as the content file.

Rules enforced:
- News window: only rows of type "news" whose date falls within the last
  `window_days` days of the issue date are accepted; anything else must be a
  bracket row ("no_news" with a last-major-news headline, or "no_prior").
- Row formats:
    news     -> Brand -- <story>. (Source, D Mon YYYY)  [must be in-window]
    recent   -> Brand -- <story>. (Source, date)  [brand's latest story, any date]
    no_news  -> Brand -- No major news today (last major news: <headline>).  [last resort]
    no_prior -> Brand -- No major news today (no prior story found).  [last resort]

Inline markup accepted in text fields:
    **bold**            -> bold brand/keyword
    [label](https://u)  -> hyperlink (HTML adds a trailing arrow)
"""

import html
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

# ======================================================================
# RENDERING
# ======================================================================

MONTHS = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}

STYLE = """\
  body { margin:0; padding:22px 16px; background:#f0f2f5;
         font-family:"Segoe UI",Arial,Helvetica,sans-serif; font-size:14px; line-height:1.5; }
  .wrap { max-width:820px; margin:0 auto; background:#fff; padding:28px 32px 24px 32px;
          border-radius:5px; box-shadow:0 1px 8px rgba(0,0,0,.08); }
  h1 { font-size:24px; font-weight:bold; color:#1a56db; margin:0 0 3px 0; }
  .date { color:#8a90a0; font-size:12.5px; margin-bottom:5px; }
  hr.top { border:none; border-top:2px solid #1a56db; margin:0 0 18px 0; }
  h2 { font-size:17px; font-weight:bold; color:#1a56db; margin:22px 0 9px 0;
       padding-bottom:5px; border-bottom:1px solid #e3e6ec; }
  h2 .cnt { font-weight:normal; color:#9aa0ae; font-size:12px; }
  .sub { font-weight:bold; color:#000; }
  .txt { color:#5a6173; }
  .exec { background:#f6f8fc; border-left:3px solid #1a56db; padding:12px 16px; margin-bottom:6px; }
  .exec .eh { font-size:15px; font-weight:bold; color:#000; margin-bottom:9px; }
  .exec .row { margin-bottom:8px; }
  .exec .row:last-child { margin-bottom:0; }
  .row { margin-bottom:7px; }
  .n { color:#000; font-weight:bold; margin-right:5px; }
  .src { color:#a0a6b4; font-size:11.5px; }
  .quiet { color:#8a90a0; font-size:12.5px; font-style:italic; }
  a { color:#1a56db; text-decoration:none; }
  a:hover { text-decoration:underline; }
  .gap { background:#f3faf6; border-left:3px solid #0f766e; padding:9px 14px; margin-top:9px; }
  .gap .gh { font-weight:bold; color:#000; font-size:13px; }
  .gap .txt { font-size:13px; }
  .sign { text-align:center; color:#a0a6b4; font-size:11.5px; margin-top:20px;
          padding-top:14px; border-top:1px solid #e3e6ec; }
"""

LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")


def parse_iso(s):
    y, m, d = (int(p) for p in s.split("-"))
    return date(y, m, d)


def parse_pub_date(s):
    m = re.match(r"^(\d{1,2})\s+([A-Za-z]{3})\w*\s+(\d{4})$", s.strip())
    if not m:
        raise ValueError(f"Unparseable publication date: {s!r}")
    return date(int(m.group(3)), MONTHS[m.group(2)[:3].title()], int(m.group(1)))


def fmt_long(d):
    return d.strftime("%B %d, %Y")


def fmt_window(start, end):
    if (start.month, start.year) == (end.month, end.year):
        return f"{start.strftime('%B')} {start.day:02d}–{end.day:02d}, {end.year}"
    return f"{fmt_long(start)} – {fmt_long(end)}"


def _bold_html(text):
    return BOLD_RE.sub(r'<span class="sub">\1</span>', text)


def inline_html(text, arrow_links=False):
    out, pos = [], 0
    for m in LINK_RE.finditer(text):
        out.append(_bold_html(html.escape(text[pos:m.start()], quote=False)))
        label = _bold_html(html.escape(m.group(1), quote=False))
        arrow = " →" if arrow_links else ""
        out.append(f'<a href="{html.escape(m.group(2))}">{label}{arrow}</a>')
        pos = m.end()
    out.append(_bold_html(html.escape(text[pos:], quote=False)))
    return "".join(out)


def check_window(row, start, end):
    if row["type"] == "recent":
        if not row.get("date"):
            raise SystemExit(f"Row {row['brand']!r} of type 'recent' needs a date.")
        return
    if row["type"] != "news":
        return
    pub = parse_pub_date(row["date"])
    if not (start <= pub <= end):
        raise SystemExit(
            f"WINDOW VIOLATION: {row['brand']!r} news dated {row['date']} is outside "
            f"{start} .. {end}. Demote it to a 'no_news' bracket row.")


def row_html(row, number):
    n = f'<span class="n">{number}.</span>'
    brand = html.escape(row["brand"], quote=False)
    if row["type"] in ("news", "recent"):
        src = f'{html.escape(row["source"], quote=False)}, {row["date"]}'
        if row.get("source_note"):
            src += " — " + html.escape(row["source_note"], quote=False)
        body = inline_html(row["text"], arrow_links=True)
        return (f'  <div class="row">{n}<span class="sub">{brand}</span> '
                f'<span class="txt">— {body} <span class="src">{src}</span></span></div>')
    if row["type"] == "no_news":
        quiet = f'No major news today (last major news: {inline_html(row["last"], arrow_links=True)})'
    else:
        quiet = "No major news today (no prior story found)"
    return (f'  <div class="row">{n}<span class="sub">{brand}</span> '
            f'<span class="txt">— <span class="quiet">{quiet}</span>.</span></div>')


def row_md(row, number):
    if row["type"] in ("news", "recent"):
        src = f"{row['source']}, {row['date']}"
        if row.get("source_note"):
            src += " — " + row["source_note"]
        return f"{number}. **{row['brand']}** — {row['text']} *({src})*"
    if row["type"] == "no_news":
        return f"{number}. **{row['brand']}** — *No major news today (last major news: {row['last']})*."
    return f"{number}. **{row['brand']}** — *No major news today (no prior story found)*."


def build(data):
    issue_date = parse_iso(data["issue_date"])
    start = issue_date - timedelta(days=data["window_days"])
    end = issue_date
    window = fmt_window(start, end)
    cats = " · ".join(data["categories"])
    totals = data["totals"]

    for section in data["sections"]:
        for row in section["rows"]:
            check_window(row, start, end)

    h = ["<!DOCTYPE html>", '<html lang="en">', "<head>", '<meta charset="UTF-8">',
         f"<title>RK World Category Intelligence — {fmt_long(issue_date)}</title>",
         f"<style>\n{STYLE}</style>", "</head>", "<body>", '<div class="wrap">\n',
         "  <h1>RK World Category Intelligence</h1>",
         f'  <div class="date">{fmt_long(issue_date)} &nbsp;&middot;&nbsp; '
         f'News window: {window} &nbsp;&middot;&nbsp; {cats} &nbsp;&middot;&nbsp; '
         f'{totals["brands"]} brands &middot; {totals["listings"]} listings on Amazon India</div>',
         '  <hr class="top">\n',
         '  <div class="exec">', '    <div class="eh">Executive Summary</div>']
    for para in data["executive_summary"]:
        h.append(f'    <div class="row"><span class="txt">{inline_html(para)}</span></div>')
    h.append("  </div>\n")
    for section in data["sections"]:
        name = html.escape(section["name"], quote=False)
        cnt = html.escape(section["count_note"], quote=False)
        h.append(f'  <h2>{name} <span class="cnt">— {cnt}</span></h2>')
        for i, row in enumerate(section["rows"], 1):
            h.append(row_html(row, i))
        if section.get("gap"):
            gh = html.escape(section["gap"]["heading"], quote=False)
            h.append(f'  <div class="gap"><span class="gh">{gh}</span> '
                     f'<span class="txt">{inline_html(section["gap"]["text"])}</span></div>')
        h.append("")
    h += [f'  <div class="sign">RK World Infocom &nbsp;|&nbsp; Confidential — '
          f'internal use only &nbsp;|&nbsp; News items cover stories published {window} only</div>\n',
          "</div>", "</body>", "</html>"]
    html_out = "\n".join(h) + "\n"

    m = ["# RK World Category Intelligence\n",
         f"**{fmt_long(issue_date)}** · News window: {window} · {cats} · "
         f"{totals['brands']} brands · {totals['listings']} listings on Amazon India\n",
         "---\n", "## Executive Summary\n"]
    for para in data["executive_summary"]:
        m.append(para + "\n")
    for section in data["sections"]:
        m.append(f"## {section['name']} *({section['count_note']})*\n")
        for i, row in enumerate(section["rows"], 1):
            m.append(row_md(row, i))
        m.append("")
        if section.get("gap"):
            m.append(f"> **{section['gap']['heading']}** {section['gap']['text']}\n")
    m += ["---\n",
          f"*RK World Infocom | Confidential — internal use only | "
          f"News items cover stories published {window} only*"]
    md_out = "\n".join(m) + "\n"

    return html_out, md_out


def main():
    if len(sys.argv) > 1:
        content_path = Path(sys.argv[1])
    else:
        candidates = sorted(Path(__file__).parent.glob("content_*.json"))
        if not candidates:
            raise SystemExit("No content_*.json found. Usage: python3 generate_newsletter.py <content.json>")
        content_path = candidates[-1]
    data = json.loads(content_path.read_text(encoding="utf-8"))
    html_out, md_out = build(data)
    stem = f"RK_World_Category_Intelligence_{data['issue_date']}"
    out_dir = content_path.parent
    (out_dir / f"{stem}.html").write_text(html_out, encoding="utf-8")
    (out_dir / f"{stem}.md").write_text(md_out, encoding="utf-8")
    print(f"Wrote {out_dir / (stem + '.html')}")
    print(f"Wrote {out_dir / (stem + '.md')}")


if __name__ == "__main__":
    main()
