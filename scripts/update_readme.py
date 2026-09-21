#!/usr/bin/env python3
"""Refresh the dynamic blocks in README.md.

Blocks (delimited by <!--START:NAME--> ... <!--END:NAME--> markers):
  HEADER : IST-based greeting, banner colour/emoji, timestamp, message
  QUOTE  : random dev quote
  POSTS  : latest Dev.to articles (left untouched if the API is unreachable)
"""
import json
import random
import re
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

README = Path("README.md")
DEVTO_USER = "kavin_krishnanc_8997e443"

# (start_hour, end_hour, greeting, banner emoji, message, banner colour)
GREETINGS = [
    (1, 5, "Good Midnight 🌙", "🌙", "Burning the midnight oil? Remember to rest!", "4A5899"),
    (5, 12, "Good Morning 🌅", "🌅", "Rise and shine! Time to build something amazing.", "FFA500"),
    (12, 16, "Good Afternoon ☀️", "☀️", "Let's keep the momentum going!", "FFD700"),
    (16, 20, "Good Evening 🌆", "🌇", "Evening coding sessions hit different!", "FF6B6B"),
]
NIGHT = ("Good Night 🌙", "✨", "Time to rest and recharge for tomorrow!", "1A1A2E")

QUOTES = [
    "Code is like humor. When you have to explain it, it's bad.",
    "First, solve the problem. Then, write the code.",
    "The best error message is the one that never shows up.",
    "Clean code always looks like it was written by someone who cares.",
    "Make it work, make it right, make it fast.",
    "Talk is cheap. Show me the code.",
    "Simplicity is prerequisite for reliability.",
    "Premature optimization is the root of all evil.",
]


def pick_greeting(hour: int):
    for start, end, greeting, emoji, msg, color in GREETINGS:
        if start <= hour < end:
            return greeting, emoji, msg, color
    return NIGHT


def build_header(now: datetime) -> str:
    greeting, emoji, msg, color = pick_greeting(now.hour)
    date = now.strftime("%A, %B %d, %Y")
    time = now.strftime("%I:%M %p IST")
    return (
        '<div align="center">\n\n'
        f"# {greeting}\n\n"
        f"![Wave](https://capsule-render.vercel.app/api?type=waving&color={color}"
        f"&height=120&section=header&text={emoji}&fontSize=90&animation=twinkling)\n\n"
        f"### 🕐 Last Updated: {date} at {time}\n\n"
        f"*{msg}*\n\n"
        "</div>"
    )


def build_quote() -> str:
    return f'<div align="center">\n\n> *"{random.choice(QUOTES)}"*\n\n</div>'


def build_posts(limit: int = 5):
    url = f"https://dev.to/api/articles?username={DEVTO_USER}&per_page={limit}"
    req = urllib.request.Request(url, headers={"User-Agent": "readme-updater"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
    except Exception as exc:  # network/API failure: keep the previous block
        print(f"Dev.to fetch failed, leaving POSTS block unchanged: {exc}")
        return None
    if not data:
        return "_No posts yet, stay tuned!_"
    return "\n".join(
        f"- [{p['title']}]({p['url']}) · {p['readable_publish_date']}" for p in data
    )


def replace_block(text: str, name: str, content: str) -> str:
    pattern = re.compile(
        rf"(<!--START:{name}-->)(.*?)(<!--END:{name}-->)", re.DOTALL
    )
    if not pattern.search(text):
        print(f"Marker block {name} not found, skipping")
        return text
    return pattern.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(3)}", text)


def main() -> None:
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    text = README.read_text(encoding="utf-8")

    text = replace_block(text, "HEADER", build_header(now))
    text = replace_block(text, "QUOTE", build_quote())

    posts = build_posts()
    if posts is not None:
        text = replace_block(text, "POSTS", posts)

    README.write_text(text, encoding="utf-8")
    print(f"README updated at {now.isoformat()}")


if __name__ == "__main__":
    main()