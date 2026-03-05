"""
AI lab blog scrapers — Anthropic, OpenAI, DeepMind, Meta AI
OpenAI + DeepMind have RSS. Anthropic + Meta AI are HTML scraped.
"""
import httpx
import feedparser
import re
from html.parser import HTMLParser
from typing import Any
from .utils import is_recent

HEADERS = {"User-Agent": "signal-digest/0.1 (research aggregator)"}

KEYWORDS = {
    "llm", "language model", "agent", "hallucin", "alignment", "reasoning",
    "fine-tun", "instruct", "rlhf", "benchmark", "eval", "context",
    "prompt", "retrieval", "rag", "emergent", "tokeniz", "transformer",
    "inference", "chain-of-thought", "grounding", "safety", "model",
}


def _relevant(title: str, abstract: str = "") -> bool:
    text = (title + " " + abstract).lower()
    return any(kw in text for kw in KEYWORDS)


# ── OpenAI ──────────────────────────────────────────────────────────────────

def _fetch_openai(limit: int) -> list[dict[str, Any]]:
    r = httpx.get("https://openai.com/news/rss.xml", headers=HEADERS, timeout=10)
    feed = feedparser.parse(r.text)
    items = []
    for entry in feed.entries:
        if len(items) >= limit:
            break
        pub = entry.get("published", "")
        if not is_recent(pub):
            continue
        if not _relevant(entry.title, entry.get("summary", "")):
            continue
        items.append({
            "source": "openai",
            "title": entry.title,
            "url": entry.link,
            "abstract": entry.get("summary", "")[:800],
            "published": pub,
        })
    return items


# ── DeepMind ─────────────────────────────────────────────────────────────────

def _fetch_deepmind(limit: int) -> list[dict[str, Any]]:
    r = httpx.get("https://deepmind.google/blog/rss.xml", headers=HEADERS, timeout=10)
    feed = feedparser.parse(r.text)
    items = []
    for entry in feed.entries:
        if len(items) >= limit:
            break
        pub = entry.get("published", "")
        if not is_recent(pub):
            continue
        if not _relevant(entry.title, entry.get("summary", "")):
            continue
        items.append({
            "source": "deepmind",
            "title": entry.title,
            "url": entry.link,
            "abstract": entry.get("summary", "")[:800],
            "published": pub,
        })
    return items


# ── Anthropic ────────────────────────────────────────────────────────────────

class _AnthropicParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.slugs = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrs = dict(attrs)
        href = attrs.get("href", "")
        if re.match(r"^/news/[a-z0-9\-]+$", href) and href not in self.slugs:
            self.slugs.append(href)


def _fetch_anthropic(limit: int) -> list[dict[str, Any]]:
    r = httpx.get("https://www.anthropic.com/news", headers=HEADERS, timeout=10,
                  follow_redirects=True)
    parser = _AnthropicParser()
    parser.feed(r.text)
    items = []
    for slug in parser.slugs:
        if len(items) >= limit:
            break
        url = f"https://www.anthropic.com{slug}"
        title = slug.replace("/news/", "").replace("-", " ").title()
        if not _relevant(title):
            continue
        items.append({
            "source": "anthropic",
            "title": title,
            "url": url,
            "abstract": "",
            "published": "",
        })
    return items


# ── Meta AI ──────────────────────────────────────────────────────────────────

class _MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrs = dict(attrs)
        href = attrs.get("href", "")
        if "/blog/" in href and href not in self.links and href.startswith("http"):
            self.links.append(href)


def _fetch_metaai(limit: int) -> list[dict[str, Any]]:
    r = httpx.get("https://ai.meta.com/blog/", headers=HEADERS, timeout=10,
                  follow_redirects=True)
    parser = _MetaParser()
    parser.feed(r.text)
    items = []
    for url in parser.links:
        if len(items) >= limit:
            break
        slug = url.rstrip("/").split("/")[-1]
        title = slug.replace("-", " ").title()
        if not _relevant(title):
            continue
        items.append({
            "source": "meta-ai",
            "title": title,
            "url": url,
            "abstract": "",
            "published": "",
        })
    return items


# ── Public API ───────────────────────────────────────────────────────────────

def fetch_labs(limit: int = 10) -> list[dict[str, Any]]:
    items = []
    per = max(limit // 4, 2)
    for fn in [_fetch_openai, _fetch_deepmind, _fetch_anthropic, _fetch_metaai]:
        try:
            items.extend(fn(per))
        except Exception as e:
            print(f"  labs scraper error ({fn.__name__}): {e}")
    return items[:limit]
