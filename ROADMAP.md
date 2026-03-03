# Signal — Roadmap

## Now — Foundation ✓
- Daily scraper across arXiv, HuggingFace, HN, Reddit
- Llama 3.3 70B digest pipeline — impact score, summary, tags
- 7-day recency filter
- GitHub Actions cron, GitHub Pages deploy
- Progressive disclosure UI, Apple HIG dark mode
- Email capture via Cloudflare Worker + Resend

---

## Next — Distribution
- [ ] Resend email delivery — send digest to subscribers daily
- [ ] Archive page — past digests browsable by date
- [ ] Auto-post digest headline to X/LinkedIn on publish
- [ ] Custom domain (`signal.writesdavid.com`)

---

## After — Quality
- [ ] Add sources: Anthropic, OpenAI, DeepMind, Meta AI blogs + Papers With Code
- [ ] Deduplication — same paper across multiple sources collapses into one card
- [ ] Scoring calibration — impact scores are too generous, needs tightening
- [ ] Tag filtering — view only `#agents` or `#hallucination` items on the page

---

## Later — Personalization
- [ ] Subscribe by tag — get only what you care about
- [ ] Digest frequency preference — daily vs weekly per subscriber
- [ ] Reader-flagged items — "this shouldn't be here" feedback loop
- [ ] Open source leaderboard — top contributors to filters and scoring

---

## Someday — Platform
- [ ] Full-text search across all past digests
- [ ] Public API — `GET /items?tag=agents&since=7d`
- [ ] Embeddable widget for other sites
- [ ] Slack/Teams integration — post digest to your team's channel

---

## What to ignore for now
- Mobile app
- Paid tier
- Recommendations engine

---

Contributions welcome. See [README](README.md) for how to get started.
