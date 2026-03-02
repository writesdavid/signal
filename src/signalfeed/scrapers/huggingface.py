import feedparser
from typing import Any

FEED_URL = "https://huggingface.co/blog/feed.xml"

KEYWORDS = {
    "llm", "language model", "agent", "hallucin", "alignment", "reasoning",
    "fine-tun", "finetun", "instruct", "rlhf", "benchmark", "eval",
    "context", "prompt", "retrieval", "rag", "drift", "emergent",
    "tokeniz", "transformer", "inference", "chain-of-thought", "grounding",
}


def fetch_huggingface(limit: int = 10) -> list[dict[str, Any]]:
    feed = feedparser.parse(FEED_URL)
    items = []

    for entry in feed.entries:
        if len(items) >= limit:
            break

        text = (entry.title + " " + entry.get("summary", "")).lower()
        if not any(kw in text for kw in KEYWORDS):
            continue

        items.append({
            "source": "huggingface",
            "title": entry.title,
            "url": entry.link,
            "abstract": entry.get("summary", "")[:1000],
            "published": entry.get("published", ""),
        })

    return items
