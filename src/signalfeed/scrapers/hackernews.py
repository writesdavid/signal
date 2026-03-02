import httpx
from typing import Any

ALGOLIA_URL = "https://hn.algolia.com/api/v1/search"
QUERIES = [
    "hallucination language model",
    "LLM agent reasoning",
    "AI alignment",
    "model evaluation benchmark",
    "prompt context window",
]


def fetch_hackernews(limit: int = 10) -> list[dict[str, Any]]:
    items = []
    seen = set()

    with httpx.Client(timeout=10) as client:
        for query in QUERIES:
            params = {
                "query": query,
                "tags": "story",
                "numericFilters": "points>50",
                "hitsPerPage": 5,
            }
            try:
                r = client.get(ALGOLIA_URL, params=params)
                r.raise_for_status()
                hits = r.json().get("hits", [])
            except Exception:
                continue

            for hit in hits:
                url = hit.get("url") or f"https://news.ycombinator.com/item?id={hit['objectID']}"
                if url in seen:
                    continue
                seen.add(url)

                items.append({
                    "source": "hackernews",
                    "title": hit.get("title", ""),
                    "url": url,
                    "abstract": hit.get("story_text", "")[:500] if hit.get("story_text") else "",
                    "published": hit.get("created_at", ""),
                    "points": hit.get("points", 0),
                })

    items.sort(key=lambda x: x["points"], reverse=True)
    return items[:limit]
