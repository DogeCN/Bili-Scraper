import datetime
import html
import re


def parse_readlist_id(url: str) -> str:
    m = re.search(r"rl(\d+)", url.strip(), re.IGNORECASE)
    return m.group(1)


def html_to_text(html_content: str) -> str:
    if not html_content:
        return ""

    text = html_content
    text = re.sub(
        r"<(script|style|noscript)[^>]*>[\s\S]*?<\/\1>", "", text, flags=re.IGNORECASE
    )
    text = re.sub(r"<img[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<video[^>]*>[\s\S]*?<\/video>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<iframe[^>]*>[\s\S]*?<\/iframe>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<figure[^>]*>[\s\S]*?<\/figure>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<figcaption[^>]*>.*?<\/figcaption>", "", text, flags=re.IGNORECASE)

    text = re.sub(r"<br\s*\/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<li[^>]*>", "\n• ", text, flags=re.IGNORECASE)
    text = re.sub(r"<\/li>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<\/h[1-6]>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<h[1-6][^>]*>", "\n\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<p[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<\/p>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<div[^>]*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<\/div>", "\n", text, flags=re.IGNORECASE)

    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)

    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]
    return "\n\n".join(lines).strip()


def format_publish_time(value: int | str) -> str:
    if isinstance(value, int):
        try:
            return datetime.datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return str(value)
    if isinstance(value, str) and value.isdigit():
        try:
            return datetime.datetime.fromtimestamp(int(value)).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except Exception:
            return value
    return str(value)


def safe_filename(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[\\/:*?\"<>|]+", "_", name)
    if not name:
        return "output"
    return name
