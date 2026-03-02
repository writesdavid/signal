import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .scrapers import fetch_arxiv, fetch_huggingface, fetch_hackernews, fetch_reddit
from .digest import digest_items
from .display import render_digest

console = Console()


def gather_items(sources: tuple[str, ...], limit: int) -> list[dict]:
    per_source = max(limit // len(sources), 3)
    items = []

    fetchers = {
        "arxiv": fetch_arxiv,
        "huggingface": fetch_huggingface,
        "hackernews": fetch_hackernews,
        "reddit": fetch_reddit,
    }

    active = {k: v for k, v in fetchers.items() if k in sources}

    with Progress(
        SpinnerColumn(),
        TextColumn("[dim]{task.description}[/dim]"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Pulling research...", total=None)

        for name, fn in active.items():
            progress.update(task, description=f"Fetching {name}...")
            try:
                items.extend(fn(limit=per_source))
            except Exception as e:
                console.print(f"[dim red]  {name}: {e}[/dim red]")

        progress.update(task, description="Processing with Claude...")
        digested = digest_items(items)

    return digested


@click.group()
def cli():
    """SIGNAL — AI-digested language + LLM research."""
    pass


@cli.command()
@click.option("--limit", "-n", default=20, help="Max items to fetch and digest.")
@click.option("--source", "-s", multiple=True,
              type=click.Choice(["arxiv", "huggingface", "hackernews", "reddit"]),
              default=["arxiv", "huggingface", "hackernews", "reddit"],
              help="Sources to pull from.")
@click.option("--filter", "-f", "source_filter", default=None, help="Filter displayed items by source.")
def pull(limit, source, source_filter):
    """Pull and digest the latest research."""
    items = gather_items(source, limit)
    render_digest(items, source_filter)


@cli.command()
@click.option("--limit", "-n", default=30, help="Max items to fetch.")
def today(limit):
    """Show today's top research, all sources."""
    items = gather_items(("arxiv", "huggingface", "hackernews", "reddit"), limit)
    render_digest(items)


@cli.command()
@click.option("--limit", "-n", default=10, help="Number of top items to show.")
def top(limit):
    """Show only the highest-impact items."""
    items = gather_items(("arxiv", "huggingface", "hackernews", "reddit"), 30)
    top_items = [i for i in items if i.get("impact", 0) >= 4][:limit]
    render_digest(top_items)
