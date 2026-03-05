"""
Main entry point for CI: fetch → deduplicate → digest → render → write docs/index.html
Run: python -m signalfeed.generate
"""
import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from signalfeed.scrapers import fetch_arxiv, fetch_huggingface, fetch_hackernews, fetch_reddit, fetch_labs
from signalfeed.digest import digest_items
from signalfeed.render_html import render_html

SOURCES = [
    ("arxiv",       fetch_arxiv,       5),
    ("huggingface", fetch_huggingface, 5),
    ("hackernews",  fetch_hackernews,  5),
    ("reddit",      fetch_reddit,      5),
    ("labs",        fetch_labs,        6),
]

OUTPUT = Path(__file__).parents[2] / "docs" / "index.html"


def _normalize(text: str) -> set:
    """Tokenize title into a set of meaningful words for similarity comparison."""
    words = re.sub(r"[^a-z0-9\s]", "", text.lower()).split()
    stopwords = {"a", "an", "the", "of", "in", "on", "for", "to", "and", "is", "are", "with"}
    return {w for w in words if w not in stopwords and len(w) > 2}


def deduplicate(items: list[dict]) -> list[dict]:
    seen_urls = set()
    seen_titles = []
    unique = []

    for item in items:
        url = item.get("url", "").rstrip("/")
        if url in seen_urls:
            continue

        title_words = _normalize(item.get("title", ""))
        duplicate = False
        for existing_words in seen_titles:
            if not title_words or not existing_words:
                continue
            overlap = len(title_words & existing_words) / max(len(title_words), len(existing_words))
            if overlap > 0.7:
                duplicate = True
                break

        if not duplicate:
            seen_urls.add(url)
            seen_titles.append(title_words)
            unique.append(item)

    return unique


def main():
    print("SIGNAL — generating digest")

    raw = []
    for name, fn, limit in SOURCES:
        print(f"  fetching {name}...")
        try:
            items = fn(limit=limit)
            print(f"    {len(items)} items")
            raw.extend(items)
        except Exception as e:
            print(f"    failed: {e}")

    before = len(raw)
    raw = deduplicate(raw)
    print(f"  deduplicated: {before} → {len(raw)} items")

    print(f"  digesting {len(raw)} items with Groq...")
    digested = digest_items(raw)
    print(f"  {len(digested)} items digested")

    if not digested:
        print("  nothing to render — exiting")
        sys.exit(1)

    html = render_html(digested)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"  wrote {OUTPUT}")


if __name__ == "__main__":
    main()
