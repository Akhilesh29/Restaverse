import json
import os
from datetime import datetime
from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup


DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
LATEST_FILE = os.path.join(DATA_DIR, "latest_articles.json")

_latest_cache: List[Dict[str, Any]] = []


def _ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)


def scrape_hacker_news() -> List[Dict[str, Any]]:
    """
    Simple scraper for Hacker News front page.
    This is just an example target site; you can swap it out in code or config.
    """
    url = "https://news.ycombinator.com/"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    items = soup.select("tr.athing")

    results: List[Dict[str, Any]] = []
    for item in items[:50]:
        title_link = item.select_one("span.titleline a")
        if not title_link:
            continue
        title = title_link.text.strip()
        link = title_link["href"]
        item_id = item.get("id")

        results.append(
            {
                "id": item_id,
                "title": title,
                "url": link,
                "scraped_at": datetime.utcnow().isoformat() + "Z",
            }
        )

    _store_latest(results)
    return results


def _store_latest(items: List[Dict[str, Any]]) -> None:
    global _latest_cache
    _ensure_data_dir()
    _latest_cache = items
    payload = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "count": len(items),
        "items": items,
    }
    with open(LATEST_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def get_latest() -> Dict[str, Any]:
    if _latest_cache:
        return {
            "updated_at": _latest_cache[0]["scraped_at"]
            if _latest_cache
            else None,
            "count": len(_latest_cache),
            "items": _latest_cache,
        }

    if os.path.exists(LATEST_FILE):
        with open(LATEST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return {"updated_at": None, "count": 0, "items": []}



