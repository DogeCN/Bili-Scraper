from pathlib import Path

from rich.console import Console
from rich.prompt import Prompt
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

from api import fetch_article_content

console = Console()


def display_article_list(articles: list[dict]) -> None:
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("序号", justify="right", width=6)
    table.add_column("ID", style="magenta", width=12)
    table.add_column("标题", style="white")
    table.add_column("阅读", style="yellow", width=10)
    table.add_column("发布时间", style="cyan", width=20)

    for index, item in enumerate(articles, start=1):
        table.add_row(
            str(index),
            item["id"],
            item["title"],
            str(item.get("read_count", 0)),
            str(item.get("publish_time", "")),
        )

    console.print(table)


def parse_selection_input(selection: str, max_n: int) -> list[int]:
    if not selection:
        return list(range(max_n))
    parts = [p.strip() for p in selection.split(",") if p.strip()]
    indices: set[int] = set()
    for part in parts:
        if "-" in part:
            try:
                start_str, end_str = part.split("-", 1)
                start = int(start_str) - 1
                end = int(end_str) - 1
                if start < 0:
                    start = 0
                if end >= max_n:
                    end = max_n - 1
                if start <= end:
                    indices.update(range(start, end + 1))
            except Exception:
                continue
        else:
            try:
                index = int(part) - 1
                if 0 <= index < max_n:
                    indices.add(index)
            except Exception:
                continue
    return sorted(indices)


def merge_articles_to_file(
    selected_articles: list[dict], cookie_path: Path, default_name: str
) -> None:
    file_name = Prompt.ask("请输入输出文件名", default=default_name)
    output_path = Path(file_name)
    output = []

    with Progress(
        SpinnerColumn(),
        TextColumn("{task.description}"),
        BarColumn(),
        TextColumn("{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        task = progress.add_task("正在下载文章内容…", total=len(selected_articles))
        for article in selected_articles:
            try:
                content = fetch_article_content(article["id"], cookie_path)
            except Exception as exc:
                console.print(
                    f"[yellow]跳过文章 {article['id']}，获取失败: {exc}[/yellow]"
                )
                content = ""

            output.append(content)
            output.append("\n")
            progress.advance(task)

    output_path.write_text("\n".join(output).strip() + "\n", encoding="utf-8")
    console.print(f"[green]已生成合并文件: {output_path.resolve()}[/green]")
