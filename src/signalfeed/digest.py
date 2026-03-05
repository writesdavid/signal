import json
import os
import re
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are the editorial intelligence behind SIGNAL — a research digest for engineers and AI practitioners who care deeply about language: how models use it, generate it, and are shaped by it.

Your readers are smart, time-poor, and allergic to hype. They want signal, not noise.

For each research item, return a JSON object with exactly these fields:
- headline: A sharp, editorial rewrite of the title (max 10 words). Not clickbait. Not academic. Clear.
- summary: 2 sentences. What it is, what it found. Plain language.
- impact: Integer 1-5. Be conservative. Most items are 1 or 2. Use this scale strictly:
    1 = Minor: routine release, incremental update, narrow finding
    2 = Noteworthy: useful advance, worth reading, limited broad impact
    3 = Significant: clear step forward, changes how practitioners think about a problem
    4 = Major: important finding that will influence the field for months
    5 = Field-shifting: rare paradigm change — use fewer than 5% of the time
- impact_label: One of: "Minor" | "Noteworthy" | "Significant" | "Major" | "Field-shifting"
- why_it_matters: 1 sentence. Specifically why this matters for code, language models, or content at scale.
- tags: Array of 1-3 strings from: ["prompting", "evals", "code-gen", "tokenization", "fine-tuning", "reasoning", "multimodal", "safety", "efficiency", "agents", "rag", "language-design"]

Respond with only valid JSON. No markdown fences, no explanation."""


def _call_groq(user_content: str) -> dict:
    headers = {
        "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": 512,
        "temperature": 0.3,
    }
    r = httpx.post(GROQ_URL, json=payload, headers=headers, timeout=30)
    r.raise_for_status()
    raw = r.json()["choices"][0]["message"]["content"].strip()
    # Strip markdown fences if model wraps anyway
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def digest_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []

    for item in items:
        user_content = f"""Source: {item['source']}
Title: {item['title']}
URL: {item['url']}
Abstract: {item.get('abstract', '(none)')}"""

        try:
            parsed = _call_groq(user_content)
            parsed["url"] = item["url"]
            parsed["source"] = item["source"]
            parsed["original_title"] = item["title"]
            results.append(parsed)
        except Exception as e:
            print(f"  skipped: {item['title'][:50]} — {e}")
            continue

    results.sort(key=lambda x: x.get("impact", 0), reverse=True)
    return results
