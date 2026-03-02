from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box
from typing import Any, Optional

console = Console()

IMPACT_COLOR = {
    1: "dim white",
    2: "cyan",
    3: "yellow",
    4: "orange1",
    5: "bold red",
}

IMPACT_BAR = {
    1: "▪︎○○○○",
    2: "▪︎▪︎○○○",
    3: "▪︎▪︎▪︎○○",
    4: "▪︎▪︎▪︎▪︎○",
    5: "▪︎▪︎▪︎▪︎▪︎",
}

SOURCE_COLOR = {
    "arxiv": "bold magenta",
    "huggingface": "bold yellow",
    "hackernews": "bold orange1",
}


def source_label(source: str) -> Text:
    color = SOURCE_COLOR.get(source.split("/")[0], "bold blue")
    return Text(source.upper(), style=color)


def render_item(item: dict[str, Any], index: int) -> Panel:
    impact = item.get("impact", 1)
    color = IMPACT_COLOR.get(impact, "white")
    bar = IMPACT_BAR.get(impact, "▪︎○○○○")
    label = item.get("impact_label", "Minor")
    tags = "  ".join(f"[dim]#{t}[/dim]" for t in item.get("tags", []))

    content = Text()
    content.append(f"{item['summary']}\n\n", style="white")
    content.append(f"{item['why_it_matters']}\n\n", style="italic dim white")
    content.append(tags)

    footer = Text()
    footer.append(f"{bar}  {label}", style=color)
    footer.append("   ")
    footer.append(item["url"], style="dim underline blue")

    full = Text()
    full.append_text(content)
    full.append("\n")
    full.append_text(footer)

    title = Text()
    title.append(f"{index:02d}  ", style="dim")
    title.append(item.get("headline", item.get("original_title", "")), style="bold white")
    title.append("  ")
    title.append_text(source_label(item["source"]))

    return Panel(
        full,
        title=title,
        title_align="left",
        border_style=color,
        padding=(1, 2),
        box=box.SIMPLE_HEAD,
    )


def render_digest(items: list[dict[str, Any]], source_filter: Optional[str] = None) -> None:
    if source_filter:
        items = [i for i in items if source_filter.lower() in i["source"].lower()]

    if not items:
        console.print("[dim]No items found.[/dim]")
        return

    console.print()
    console.rule("[bold white]S I G N A L[/bold white]  [dim]language + LLM research[/dim]")
    console.print()

    for i, item in enumerate(items, 1):
        console.print(render_item(item, i))

    console.print()
    console.rule(f"[dim]{len(items)} items[/dim]")
    console.print()
