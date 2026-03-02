"""
Main entry point for CI: fetch → digest → render → write docs/index.html
Run: python -m signalfeed.generate
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from signalfeed.scrapers import fetch_arxiv, fetch_huggingface, fetch_hackernews, fetch_reddit
from signalfeed.digest import digest_items
from signalfeed.render_html import render_html

SOURCES = [
    ("arxiv",      fetch_arxiv,      5),
    ("huggingface", fetch_huggingface, 5),
    ("hackernews", fetch_hackernews,  5),
    ("reddit",     fetch_reddit,      5),
]

OUTPUT = Path(__file__).parents[2] / "docs" / "index.html"


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
