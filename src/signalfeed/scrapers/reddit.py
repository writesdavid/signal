import httpx
from datetime import datetime, timezone
from typing import Any
from .utils import cutoff

SUBREDDITS = ["MachineLearning", "LocalLLaMA", "LanguageTechnology"]
HEADERS = {"User-Agent": "signal-digest/0.1 (research aggregator)"}

# Only surface posts that touch the topics we care about
KEYWORDS = {
    "hallucin", "agent", "reasoning", "alignment", "benchmark", "eval",
    "context", "prompt", "fine-tun", "finetun", "rlhf", "instruct",
    "drift", "grounding", "retrieval", "rag", "llm", "language model",
    "emergent", "tokeniz", "inference", "chain-of-thought", "cot",
}


def fetch_reddit(limit: int = 10) -> list[dict[str, Any]]:
    items = []
    seen = set()

    with httpx.Client(timeout=10, headers=HEADERS, follow_redirects=True) as client:
        for sub in SUBREDDITS:
            try:
                r = client.get(f"https://www.reddit.com/r/{sub}/hot.json?limit=10")
                r.raise_for_status()
                posts = r.json()["data"]["children"]
            except Exception:
                continue

            for post in posts:
                d = post["data"]
                if d.get("stickied") or d["url"] in seen:
                    continue

                created = d.get("created_utc", 0)
                post_dt = datetime.fromtimestamp(created, tz=timezone.utc)
                if post_dt < cutoff():
                    continue

                text = (d.get("title", "") + " " + (d.get("selftext", "") or "")).lower()
                if not any(kw in text for kw in KEYWORDS):
                    continue

                seen.add(d["url"])
                pub = datetime.fromtimestamp(created, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                items.append({
                    "source": f"reddit/r/{sub}",
                    "title": d.get("title", ""),
                    "url": d.get("url", ""),
                    "abstract": (d.get("selftext", "") or "")[:500],
                    "published": pub,
                    "score": d.get("score", 0),
                })

    items.sort(key=lambda x: x["score"], reverse=True)
    return items[:limit]
