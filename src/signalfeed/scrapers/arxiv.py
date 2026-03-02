import httpx
from typing import Any
from xml.etree import ElementTree as ET

SEARCH_URL = "https://export.arxiv.org/api/query"

# Category-scoped queries: cs.CL (Computation & Language) + cs.AI only
# Format: (cat:cs.CL OR cat:cs.AI) AND all:<topic>
QUERIES = [
    "(cat:cs.CL OR cat:cs.AI) AND all:hallucination factuality grounding",
    "(cat:cs.CL OR cat:cs.AI) AND all:agent reasoning planning language model",
    "(cat:cs.CL OR cat:cs.AI) AND all:alignment instruction tuning RLHF",
    "(cat:cs.CL OR cat:cs.AI) AND all:LLM evaluation benchmark emergent",
    "(cat:cs.CL OR cat:cs.AI) AND all:context window retrieval augmented",
]
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


def fetch_arxiv(limit: int = 10) -> list[dict[str, Any]]:
    items = []
    seen = set()
    per_query = max(limit // len(QUERIES), 2)

    with httpx.Client(timeout=15) as client:
        for query in QUERIES:
            params = {
                "search_query": f"all:{query}",
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "max_results": per_query,
            }
            try:
                r = client.get(SEARCH_URL, params=params)
                r.raise_for_status()
                root = ET.fromstring(r.text)
            except Exception:
                continue

            for entry in root.findall("atom:entry", NS):
                url = entry.findtext("atom:id", namespaces=NS) or ""
                if url in seen:
                    continue
                seen.add(url)

                title = (entry.findtext("atom:title", namespaces=NS) or "").strip().replace("\n", " ")
                abstract = (entry.findtext("atom:summary", namespaces=NS) or "").strip()[:1000]
                published = entry.findtext("atom:published", namespaces=NS) or ""

                items.append({
                    "source": "arxiv",
                    "title": title,
                    "url": url,
                    "abstract": abstract,
                    "published": published,
                })

    return items[:limit]
