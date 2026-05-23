import json
from pathlib import Path
from typing import Any, Dict, Optional
from utils import html_to_text, format_publish_time, parse_readlist_id

import httpx


def load_cookie_header(cookie_path: Path = Path("cookie.json")) -> Optional[str]:
    if not cookie_path.exists():
        return None

    raw = cookie_path.read_text(encoding="utf-8")
    data = json.loads(raw)
    cookies: Dict[str, str] = {}

    if isinstance(data, dict):
        for name, value in data.items():
            cookies[name] = str(value)
    elif isinstance(data, list):
        for item in data:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            value = item.get("value")
            domain = str(item.get("domain", ""))
            if not name or value is None:
                continue
            if "bilibili.com" not in domain and domain:
                continue
            cookies[name] = str(value)
    else:
        raise ValueError("cookie.json 必须为对象或对象数组。")

    return (
        "; ".join(f"{name}={value}" for name, value in cookies.items())
        if cookies
        else None
    )


def build_headers(
    cookie: Optional[str] = None, referer: Optional[str] = None
) -> Dict[str, str]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Origin": "https://www.bilibili.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "sec-ch-ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    if referer:
        headers["Referer"] = referer
    if cookie:
        headers["Cookie"] = cookie
    return headers


def fetch_article_list(url: str, cookie_path: Path) -> Dict[str, Any]:
    readlist_id = parse_readlist_id(url)
    cookie_header = load_cookie_header(cookie_path)
    headers = build_headers(
        cookie_header, referer=f"https://www.bilibili.com/read/readlist/rl{readlist_id}"
    )
    api_url = f"https://api.bilibili.com/x/article/list/web/articles?id={readlist_id}&web_location=333.1400"

    with httpx.Client(headers=headers, timeout=30.0) as client:
        response = client.get(api_url)
        response.raise_for_status()
        data: dict = response.json()

    if data.get("code") != 0 or not data.get("data"):
        message = data.get("message", "未知错误")
        raise RuntimeError(f"获取专栏列表失败: {message}")

    data = data["data"]
    articles = data.get("articles", [])
    author = data.get("author", {})["name"]
    title = (data.get("list") or {}).get("name") or f"readlist_{readlist_id}"

    return {
        "url": url,
        "author": author,
        "title": str(title),
        "articles": [
            {
                "id": str(item["id"]) or item["aid"] or "",
                "title": item["title"],
                "summary": item["summary"] or item["description"] or "",
                "author": author,
                "publish_time": format_publish_time(
                    item["publish_time"] or item["pubdate"] or ""
                ),
                "read_count": item["stats"]["view"]
                or item["view"]
                or item["read_count"]
                or 0,
                "url": f"https://www.bilibili.com/read/{item['id'] or item['aid']}",
            }
            for item in articles
            if "id" in item or "aid" in item
        ],
    }


def fetch_article_content(article_id: str, cookie_path: Path) -> str:
    cookie_header = load_cookie_header(cookie_path)
    headers = build_headers(cookie_header, referer="https://www.bilibili.com/")
    api_url = f"https://api.bilibili.com/x/article/view?id={article_id}"

    with httpx.Client(headers=headers, timeout=30.0) as client:
        response = client.get(api_url)
        response.raise_for_status()
        data: dict = response.json()

    if data.get("code") != 0 or not data.get("data"):
        message = data.get("message", "未知错误")
        raise RuntimeError(f"获取文章内容失败: {message}")

    article = data["data"]
    html_content = article["content"] or article["html_content"] or ""
    return html_to_text(html_content)
