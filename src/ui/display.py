from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime
import feedparser
from typing import Dict
import time
from models.feed import Feed

console = Console()

def display_feeds(feeds: Dict[str, Feed]) -> None:
    """Display feeds in a rich table."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim")
    table.add_column("Title")
    table.add_column("Genre")
    table.add_column("URL", style="dim")

    for idx, (_, feed) in enumerate(feeds.items(), 1):
        table.add_row(
            str(idx),
            feed.title,
            feed.genre,
            feed.url
        )

    console.print(table)

def display_latest_articles(feed_url: str) -> None:
    """Display the latest articles from a feed."""
    with console.status("[bold green]Fetching latest articles..."):
        feed = feedparser.parse(feed_url)
    
    table = Table(show_header=True, header_style="bold green")
    table.add_column("Date")
    table.add_column("Title")
    
    for entry in feed.entries[:5]:
        # Get the time struct from either published or updated date
        time_struct = entry.get('published_parsed') or entry.get('updated_parsed')
        
        if time_struct:
            # Convert time_struct to Unix timestamp then to datetime
            timestamp = time.mktime(time_struct)
            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        else:
            date = 'Unknown'
        
        table.add_row(date, entry.get('title', 'No title'))
    
    console.print(Panel(table, title="Latest Articles", border_style="green"))
