from datetime import datetime, timezone
from typing import Any, Optional

IMPACT_COLOR = {
    1: "#636366",
    2: "#0a84ff",
    3: "#ffd60a",
    4: "#ff9f0a",
    5: "#ff453a",
}

IMPACT_DOT = {
    1: "●○○○○",
    2: "●●○○○",
    3: "●●●○○",
    4: "●●●●○",
    5: "●●●●●",
}

SOURCE_LABEL = {
    "arxiv":       "arXiv",
    "huggingface": "HuggingFace",
    "hackernews":  "Hacker News",
}


def _source_label(source: str) -> str:
    for key, label in SOURCE_LABEL.items():
        if key in source:
            return label
    if source.startswith("reddit/"):
        return source.replace("reddit/r/", "r/")
    return source


def _card(item: dict[str, Any], index: int) -> str:
    impact     = item.get("impact", 1)
    color      = IMPACT_COLOR.get(impact, "#636366")
    dots       = IMPACT_DOT.get(impact, "●○○○○")
    label      = item.get("impact_label", "Minor")
    source     = _source_label(item.get("source", ""))
    headline   = item.get("headline", item.get("original_title", ""))
    summary    = item.get("summary", "")
    why        = item.get("why_it_matters", "")
    url        = item.get("url", "#")
    tags       = "".join(
        f'<span class="tag">#{t}</span>' for t in item.get("tags", [])
    )

    return f"""
    <details class="card">
      <summary>
        <div class="card-summary">
          <span class="index">{index:02d}</span>
          <div class="card-main">
            <span class="headline">{headline}</span>
            <div class="card-meta">
              <span class="source">{source}</span>
              <span class="dot">·</span>
              <span class="impact-dots" style="color:{color}">{dots}</span>
              <span class="impact-label" style="color:{color}">{label}</span>
            </div>
          </div>
          <span class="chevron">›</span>
        </div>
      </summary>
      <div class="card-body">
        <p class="summary-text">{summary}</p>
        <p class="why-text">{why}</p>
        <div class="card-footer">
          <div class="tags">{tags}</div>
          <a class="read-link" href="{url}" target="_blank" rel="noopener">Read &rarr;</a>
        </div>
      </div>
    </details>"""


def render_html(items: list[dict[str, Any]], date: Optional[str] = None) -> str:
    if date is None:
        date = datetime.now(timezone.utc).strftime("%B %d, %Y")

    cards = "\n".join(_card(item, i + 1) for i, item in enumerate(items))
    count = len(items)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Signal — {date}</title>
  <meta name="description" content="AI-digested language + LLM research for engineers and practitioners." />
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

    :root {{
      --bg:          #000000;
      --bg-elevated: #1c1c1e;
      --bg-grouped:  #2c2c2e;
      --separator:   #38383a;
      --label:       #f5f5f7;
      --label-2:     #ebebf5cc;
      --label-3:     #ebebf599;
      --label-4:     #ebebf560;
      --accent:      #0a84ff;
      --font:        -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif;
      --font-mono:   'SF Mono', 'Fira Code', ui-monospace, monospace;
      --radius:      12px;
      --radius-sm:   8px;
    }}

    body {{
      background: var(--bg);
      color: var(--label);
      font-family: var(--font);
      font-size: 17px;
      line-height: 1.47;
      -webkit-font-smoothing: antialiased;
      padding: 0 1rem 4rem;
    }}

    /* ── Header ── */
    header {{
      max-width: 680px;
      margin: 0 auto;
      padding: 4rem 0 2.5rem;
    }}

    .eyebrow {{
      font-family: var(--font-mono);
      font-size: 11px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--label-3);
      margin-bottom: 0.5rem;
    }}

    h1 {{
      font-size: 34px;
      font-weight: 700;
      letter-spacing: -0.5px;
      color: var(--label);
      line-height: 1.18;
    }}

    .subtitle {{
      margin-top: 0.5rem;
      font-size: 15px;
      color: var(--label-3);
      line-height: 1.5;
    }}

    .meta-row {{
      margin-top: 1.5rem;
      display: flex;
      align-items: center;
      gap: 1rem;
      font-family: var(--font-mono);
      font-size: 12px;
      color: var(--label-4);
    }}

    .meta-row .sep {{ color: var(--separator); }}

    /* ── Feed ── */
    main {{
      max-width: 680px;
      margin: 0 auto;
    }}

    .section-label {{
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 0.02em;
      color: var(--label-3);
      text-transform: uppercase;
      padding: 0.75rem 0 0.5rem;
      border-bottom: 1px solid var(--separator);
      margin-bottom: 2px;
    }}

    /* ── Card ── */
    .card {{
      background: var(--bg-elevated);
      border-radius: var(--radius);
      margin-bottom: 2px;
      overflow: hidden;
      transition: background 0.15s ease;
    }}

    .card:first-of-type {{ border-radius: var(--radius) var(--radius) var(--radius-sm) var(--radius-sm); }}
    .card:last-of-type  {{ border-radius: var(--radius-sm) var(--radius-sm) var(--radius) var(--radius); margin-bottom: 0; }}
    .card:only-of-type  {{ border-radius: var(--radius); }}

    .card[open] {{ background: var(--bg-grouped); }}

    /* summary resets */
    .card summary {{
      list-style: none;
      cursor: pointer;
      padding: 1rem 1.25rem;
      user-select: none;
    }}
    .card summary::-webkit-details-marker {{ display: none; }}
    .card summary::marker {{ display: none; }}

    .card-summary {{
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
    }}

    .index {{
      font-family: var(--font-mono);
      font-size: 12px;
      color: var(--label-4);
      padding-top: 3px;
      min-width: 1.5rem;
      flex-shrink: 0;
    }}

    .card-main {{
      flex: 1;
      min-width: 0;
    }}

    .headline {{
      display: block;
      font-size: 15px;
      font-weight: 600;
      color: var(--label);
      line-height: 1.35;
      margin-bottom: 0.3rem;
    }}

    .card-meta {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
      flex-wrap: wrap;
    }}

    .source {{
      font-size: 12px;
      color: var(--label-3);
    }}

    .dot {{
      font-size: 10px;
      color: var(--label-4);
    }}

    .impact-dots {{
      font-size: 9px;
      letter-spacing: 0.1em;
    }}

    .impact-label {{
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.03em;
    }}

    .chevron {{
      font-size: 18px;
      color: var(--label-4);
      flex-shrink: 0;
      transition: transform 0.2s ease;
      padding-top: 0;
      line-height: 1.2;
      transform: rotate(0deg);
    }}

    .card[open] .chevron {{
      transform: rotate(90deg);
    }}

    /* ── Expanded body ── */
    .card-body {{
      padding: 0 1.25rem 1.25rem 3.25rem;
      border-top: 1px solid var(--separator);
      padding-top: 1rem;
    }}

    .summary-text {{
      font-size: 15px;
      color: var(--label-2);
      line-height: 1.6;
      margin-bottom: 0.5rem;
    }}

    .why-text {{
      font-size: 14px;
      color: var(--label-3);
      font-style: italic;
      line-height: 1.55;
      margin-bottom: 1rem;
    }}

    .card-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.75rem;
    }}

    .tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
    }}

    .tag {{
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--label-3);
      background: var(--bg);
      padding: 0.15rem 0.5rem;
      border-radius: 4px;
    }}

    .read-link {{
      font-size: 14px;
      font-weight: 500;
      color: var(--accent);
      text-decoration: none;
      white-space: nowrap;
      flex-shrink: 0;
    }}

    .read-link:hover {{ text-decoration: underline; }}

    /* ── Footer ── */
    footer {{
      max-width: 680px;
      margin: 3rem auto 0;
      padding-top: 1.5rem;
      border-top: 1px solid var(--separator);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      color: var(--label-4);
    }}

    footer a {{ color: var(--label-4); text-decoration: none; }}
    footer a:hover {{ color: var(--label-2); }}

    /* ── Subscribe ── */
    .subscribe {{
      max-width: 680px;
      margin: 0 auto 2.5rem;
      padding: 1.25rem 1.5rem;
      background: var(--bg-elevated);
      border-radius: var(--radius);
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
    }}

    .subscribe-copy {{
      font-size: 14px;
      color: var(--label-3);
      line-height: 1.4;
    }}

    .subscribe-copy strong {{
      display: block;
      font-size: 15px;
      font-weight: 600;
      color: var(--label);
      margin-bottom: 0.15rem;
    }}

    .subscribe-form {{
      display: flex;
      gap: 0.5rem;
      flex-shrink: 0;
    }}

    .subscribe-input {{
      background: var(--bg);
      border: 1px solid var(--separator);
      border-radius: var(--radius-sm);
      color: var(--label);
      font-family: var(--font);
      font-size: 14px;
      padding: 0.5rem 0.75rem;
      width: 200px;
      outline: none;
      transition: border-color 0.15s;
    }}

    .subscribe-input:focus {{ border-color: var(--accent); }}
    .subscribe-input::placeholder {{ color: var(--label-4); }}

    .subscribe-btn {{
      background: var(--accent);
      border: none;
      border-radius: var(--radius-sm);
      color: #fff;
      cursor: pointer;
      font-family: var(--font);
      font-size: 14px;
      font-weight: 600;
      padding: 0.5rem 1rem;
      white-space: nowrap;
      transition: opacity 0.15s;
    }}

    .subscribe-btn:hover {{ opacity: 0.85; }}
    .subscribe-msg {{ font-size: 13px; color: var(--label-3); display: none; }}

    /* ── Mobile ── */
    @media (max-width: 600px) {{
      h1 {{ font-size: 26px; }}
      .card-body {{ padding-left: 1.25rem; }}
      .subscribe {{ flex-direction: column; align-items: flex-start; }}
      .subscribe-form {{ width: 100%; }}
      .subscribe-input {{ flex: 1; width: auto; }}
      footer {{ flex-direction: column; gap: 0.5rem; text-align: center; }}
    }}
  </style>
</head>
<body>
  <header>
    <p class="eyebrow">Signal</p>
    <h1>Language + LLM<br>Research</h1>
    <p class="subtitle">AI-digested highlights for engineers and practitioners<br>who care about language.</p>
    <div class="meta-row">
      <span>{date}</span>
      <span class="sep">·</span>
      <span>{count} items</span>
      <span class="sep">·</span>
      <span>arXiv · HuggingFace · HN · Reddit</span>
    </div>
  </header>

  <div class="subscribe">
    <div class="subscribe-copy">
      <strong>Get it in your inbox</strong>
      Weekday mornings. No noise.
    </div>
    <div>
      <form class="subscribe-form" onsubmit="handleSubscribe(event)">
        <input class="subscribe-input" type="email" placeholder="you@example.com" required />
        <button class="subscribe-btn" type="submit">Subscribe</button>
      </form>
      <p class="subscribe-msg" id="sub-msg"></p>
    </div>
  </div>

  <main>
    <p class="section-label">Today's digest</p>
    {cards}
  </main>

  <footer>
    <span>By <a href="https://github.com/writesdavid" target="_blank">writesdavid</a></span>
    <span><a href="https://github.com/writesdavid/signal" target="_blank">View source</a></span>
  </footer>

  <script>
    async function handleSubscribe(e) {{
      e.preventDefault();
      const form = e.target;
      const email = form.querySelector('input').value;
      const btn = form.querySelector('button');
      const msg = document.getElementById('sub-msg');
      btn.disabled = true;
      btn.textContent = '...';
      try {{
        const res = await fetch('https://signal-subscribe.davehamiltonj.workers.dev', {{
          method: 'POST',
          headers: {{'Content-Type': 'application/json'}},
          body: JSON.stringify({{ email }}),
        }});
        if (res.ok) {{
          form.style.display = 'none';
          msg.style.display = 'block';
          msg.textContent = "You're in. First issue hits tomorrow morning.";
        }} else {{
          throw new Error();
        }}
      }} catch {{
        btn.disabled = false;
        btn.textContent = 'Subscribe';
        msg.style.display = 'block';
        msg.textContent = 'Something went wrong. Try again.';
      }}
    }}
  </script>
</body>
</html>"""
