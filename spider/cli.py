from __future__ import annotations

import asyncio
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.table import Table

from spider import __version__
from spider.utils.logger import configure_logger


console = Console()
configure_logger()


@click.group()
@click.version_option(__version__, prog_name="Hungry Spider")
def cli():
    """Hungry Spider - Modular Web Crawling and Intelligence System."""


@cli.group()
def db():
    """Database management commands."""


@db.command("init")
def db_init():
    from spider.storage.db import init_db

    init_db()
    console.print("[green]Database initialised[/green]")


@db.command("stats")
def db_stats():
    from spider.storage.repository import get_stats

    stats = get_stats()
    table = Table(title="Database Statistics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    for key, value in stats.items():
        table.add_row(key, str(value))
    console.print(table)


@cli.command("crawl")
@click.argument("url")
@click.option("--depth", "depth", default=2, show_default=True, help="Max crawl depth")
@click.option("--dynamic", "dynamic", is_flag=True, help="Use Playwright for JS-rendered sites")
@click.option("--ai/--no-ai", default=True, show_default=True, help="Enable AI extraction")
@click.option("--proxies/--no-proxies", default=False, help="Enable proxy rotation")
@click.option("--concurrency", default=4, show_default=True, help="Concurrent requests")
@click.option("--delay", default=2.0, show_default=True, help="Base delay between requests")
@click.option("--output", type=click.Choice(["db", "json", "csv", "jsonl"]), default="db")
@click.option("--job-name", default=None, help="Optional name for the crawl job")
def crawl(url, depth, dynamic, ai, proxies, concurrency, delay, output, job_name):
    """Crawl a target URL and extract data."""
    from spider.core.engine import CrawlEngine

    config = {
        "url": url,
        "depth": depth,
        "use_playwright": dynamic,
        "enable_ai": ai,
        "use_proxies": proxies,
        "concurrency": concurrency,
        "delay": delay,
        "output": output,
        "job_name": job_name or f"crawl_{Path(url).name or 'target'}",
    }
    result = asyncio.run(CrawlEngine(config).run())
    console.print(f"[green]Crawl complete[/green] job_id={result['job_id']}")
    console.print(
        f"pages_crawled={result['pages_crawled']} pages_extracted={result['pages_extracted']}"
    )
    if result.get("output"):
        console.print(f"export={result['output']}")


@cli.command("crawl-file")
@click.argument("targets_file", type=click.Path(exists=True))
@click.option("--ai/--no-ai", default=True, help="Enable AI extraction")
def crawl_file(targets_file, ai):
    """Crawl multiple targets defined in a YAML file."""
    from spider.core.engine import CrawlEngine

    with open(targets_file, encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    targets = payload.get("targets", [])
    console.print(f"Loaded {len(targets)} targets from {targets_file}")
    for target in targets:
        config = {
            "url": target["url"],
            "depth": target.get("depth", 2),
            "use_playwright": target.get("dynamic", False),
            "enable_ai": ai,
            "concurrency": target.get("concurrency", 4),
            "delay": target.get("delay", 2.0),
            "job_name": target.get("job_name"),
            "schema": target.get("schema", "generic"),
        }
        result = asyncio.run(CrawlEngine(config).run())
        console.print(
            f"[green]{target['url']}[/green] crawled={result['pages_crawled']} extracted={result['pages_extracted']}"
        )


@cli.command("export")
@click.option("--format", "format_", type=click.Choice(["json", "csv", "jsonl"]), default="json")
@click.option("--output", default="data/exports/output", help="Output file path without extension")
@click.option("--limit", default=None, type=int, help="Maximum records to export")
def export_cmd(format_, output, limit):
    """Export extracted data to JSON, CSV, or JSONL."""
    from spider.storage.exporter import export_data

    path = export_data(format=format_, output_path=output, limit=limit)
    console.print(f"[green]Exported to {path}[/green]")


@cli.command("reprocess")
@click.option("--limit", default=50, show_default=True, help="Maximum raw pages to reprocess")
def reprocess(limit):
    """Run AI extraction on previously crawled raw pages."""
    from spider.core.engine import reprocess_raw_pages

    result = asyncio.run(reprocess_raw_pages(limit=limit))
    console.print(f"[green]Reprocessed {result['processed']} pages[/green]")


if __name__ == "__main__":
    cli()
