"""
Sends the digest to all Resend audience subscribers.
Run after generate.py — reads docs/index.html and sends via Resend.
"""
import os
import json
from datetime import datetime, timezone
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv()

RESEND_API = "https://api.resend.com"
HTML_PATH  = Path(__file__).parents[2] / "docs" / "index.html"


def get_contacts(api_key: str, audience_id: str) -> list[str]:
    r = httpx.get(
        f"{RESEND_API}/audiences/{audience_id}/contacts",
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=15,
    )
    r.raise_for_status()
    contacts = r.json().get("data", {}).get("data", [])
    return [c["email"] for c in contacts if not c.get("unsubscribed")]


def send_digest(api_key: str, emails: list[str], html: str, date: str) -> None:
    # Resend supports up to 50 recipients per call — batch if needed
    BATCH = 50
    for i in range(0, len(emails), BATCH):
        batch = emails[i : i + BATCH]
        payload = {
            "from":    "Signal <signal@writesdavid.com>",
            "to":      batch,
            "subject": f"Signal — {date}",
            "html":    html,
        }
        r = httpx.post(
            f"{RESEND_API}/emails",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type":  "application/json",
            },
            content=json.dumps(payload),
            timeout=30,
        )
        r.raise_for_status()
        print(f"  sent batch {i // BATCH + 1}: {len(batch)} emails")


def main():
    api_key     = os.environ["RESEND_API_KEY"]
    audience_id = os.environ["RESEND_AUDIENCE_ID"]
    date        = datetime.now(timezone.utc).strftime("%B %d, %Y")

    print("Signal — sending digest email")

    html = HTML_PATH.read_text(encoding="utf-8")

    print("  fetching subscribers...")
    emails = get_contacts(api_key, audience_id)
    print(f"  {len(emails)} active subscribers")

    if not emails:
        print("  no subscribers yet — skipping send")
        return

    send_digest(api_key, emails, html, date)
    print("  done")


if __name__ == "__main__":
    main()
