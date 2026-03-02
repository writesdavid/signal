# Signal

A free daily digest of language and LLM research. Hallucinations, agents, drift, alignment — the research that explains why models behave the way they do.

**→ [writesdavid.github.io/signal](https://writesdavid.github.io/signal)**

---

## What it does

Every weekday morning, Signal:

1. Pulls recent papers and posts from arXiv (cs.CL + cs.AI), HuggingFace, Hacker News, and Reddit
2. Drops anything older than 7 days
3. Runs each item through Llama 3.3 70B on Groq — impact score (1–5), plain-English summary, why it matters for language at scale
4. Generates a styled static page and commits it to GitHub Pages

Free. No account needed. No inference costs to you.

---

## Under the hood

```
src/signalfeed/
├── scrapers/        # arXiv, HuggingFace, HN, Reddit + recency filter
├── digest.py        # Groq/Llama processing pipeline
├── render_html.py   # Static HTML generator
├── generate.py      # CI entry point
└── email_send.py    # Resend email delivery (optional)
```

Stack: Python · Groq (Llama 3.3 70B) · GitHub Actions · GitHub Pages

---

## Run it locally

```bash
git clone https://github.com/writesdavid/signal.git
cd signal

python3 -m venv .venv && source .venv/bin/activate
pip install httpx feedparser python-dotenv

echo "GROQ_API_KEY=your_key_here" > .env  # console.groq.com — free

cd src && python -m signalfeed.generate
open ../docs/index.html
```

---

## Make it better

Tighter filters, smarter scoring, new sources, email delivery — all welcome.

```bash
git checkout -b your-feature
# make your changes
git push origin your-feature
# open a pull request
```

Good places to start:
- `src/signalfeed/scrapers/` — add a source or tighten keyword filters
- `src/signalfeed/digest.py` — improve the prompt or scoring logic
- `src/signalfeed/render_html.py` — improve the design

---

Built by [writesdavid](https://github.com/writesdavid) while learning to build in public.
