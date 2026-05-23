from api import fetch_article_list
from utils import safe_filename
from rich.prompt import Prompt
from pathlib import Path
from cli import *

console.print("[red]Bilibili[/red] [green]交互式终端工具[/green]")
cookie_path = Path("cookie.json")

while True:
    url = Prompt.ask("专栏URL")
    try:
        data = fetch_article_list(url, cookie_path)
    except Exception as exc:
        console.print(f"[red]获取文章列表失败: {exc}[/red]")
        continue

    articles = data.get("articles", [])
    if not articles:
        console.print("[yellow]未找到任何文章，请检查专栏 URL 是否正确[/yellow]")
        continue

    author = data.get("author", "未知作者")
    title = data.get("title", "readlist")
    total = len(articles)
    console.print(
        f"[bold]标题: [/bold]{title}\t[bold]作者: [/bold]{author}\t[bold]文章数量: [/bold]{total}"
    )
    display_article_list(articles)

    selection = Prompt.ask("输入要合并的序号范围", default=f"1-{total}")
    indices = parse_selection_input(selection, len(articles))
    if not indices:
        console.print("[yellow]已取消[/yellow]")
    else:
        selected_articles = [articles[i] for i in indices]
        default_name = safe_filename(title)
        if not default_name.lower().endswith(".txt"):
            default_name = default_name + ".txt"
        merge_articles_to_file(selected_articles, cookie_path, default_name)

    console.print()
