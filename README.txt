RK World Category Intelligence — code files (August 07, 2026)

1. RK_World_Category_Intelligence_2026-08-07.html — the newsletter (open in any browser / paste into email)
2. RK_World_Category_Intelligence_2026-08-07.md   — Markdown twin
3. generate_newsletter.py                         — Python generator for both formats
4. content_2026-08-07.json                        — edition content (input to the generator)

Regenerate the newsletter with:
  python generate_newsletter.py content_2026-08-07.json

The generator enforces the news-window rule: a row of type "news" must be
dated within the last 2 days of the issue date or the build fails; older
stories belong in "no_news" bracket rows (last major news: <headline>).
