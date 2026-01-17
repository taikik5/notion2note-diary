"""
Notion API module for fetching and updating articles.
"""

import os
from datetime import datetime

import httpx


NOTION_API_BASE = "https://api.notion.com/v1"


def get_notion_headers() -> dict:
    """Get headers for Notion API requests."""
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        raise ValueError("NOTION_TOKEN environment variable is not set")
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }


def fetch_ready_articles(database_id: str) -> list[dict]:
    """
    Fetch articles with Status = 'Ready' from the Notion database.

    Returns:
        List of article records with id, title, memo_content, and date.
    """
    articles = []
    has_more = True
    start_cursor = None
    headers = get_notion_headers()

    while has_more:
        payload = {
            "filter": {
                "property": "Status",
                "status": {
                    "equals": "Ready"
                }
            }
        }

        if start_cursor:
            payload["start_cursor"] = start_cursor

        response = httpx.post(
            f"{NOTION_API_BASE}/databases/{database_id}/query",
            headers=headers,
            json=payload,
            timeout=30.0,
        )
        if response.status_code != 200:
            print(f"Error response: {response.text}")
        response.raise_for_status()
        data = response.json()

        for page in data.get("results", []):
            article = {
                "id": page["id"],
                "title": _extract_title(page),
                "memo_content": _extract_memo_content(page),
                "date": _extract_date(page),
            }
            articles.append(article)

        has_more = data.get("has_more", False)
        start_cursor = data.get("next_cursor")

    return articles


def _extract_title(page: dict) -> str:
    """Extract title from page properties."""
    title_prop = page.get("properties", {}).get("タイトル", {})
    title_list = title_prop.get("title", [])
    if title_list:
        return title_list[0].get("plain_text", "")
    return ""


def _extract_memo_content(page: dict) -> str:
    """Extract memo content from page properties."""
    memo_prop = page.get("properties", {}).get("メモ内容", {})
    rich_text_list = memo_prop.get("rich_text", [])
    if rich_text_list:
        return "".join([rt.get("plain_text", "") for rt in rich_text_list])
    return ""


def _extract_date(page: dict) -> str:
    """
    Extract date from page properties.
    If empty, return today's date in YYYY.MM.DD format.
    """
    date_prop = page.get("properties", {}).get("日付", {})
    date_obj = date_prop.get("date")
    if date_obj and date_obj.get("start"):
        date_str = date_obj["start"]
        # Convert YYYY-MM-DD to YYYY.MM.DD
        return date_str.replace("-", ".")
    # Default to today
    return datetime.now().strftime("%Y.%m.%d")


def mark_as_done(page_id: str) -> None:
    """Update the Status property to 'Done' for the specified page."""
    headers = get_notion_headers()
    payload = {
        "properties": {
            "Status": {
                "status": {
                    "name": "Done"
                }
            }
        }
    }
    response = httpx.patch(
        f"{NOTION_API_BASE}/pages/{page_id}",
        headers=headers,
        json=payload,
        timeout=30.0,
    )
    response.raise_for_status()


if __name__ == "__main__":
    # Test execution
    from dotenv import load_dotenv
    load_dotenv()

    database_id = os.environ.get("NOTION_DATABASE_ID", "")
    articles = fetch_ready_articles(database_id)
    print(f"Found {len(articles)} ready articles:")
    for article in articles:
        print(f"  - {article['title']} ({article['date']})")
