import listparser
import feedparser
import xml.etree.ElementTree as ET
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.progress import Progress
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.logging import RichHandler
from datetime import datetime
import hashlib
from typing import Dict, List, Set, Optional
import logging
import json
import time
import aiohttp
import asyncio
from pathlib import Path
import pickle
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor

console = Console()

@dataclass
class FeedCache:
    """Cache structure for feed data"""
    last_checked: float
    is_valid: bool
    title: str
    genre: str
    description: str
    last_content_hash: str

class LogPanel:
    """Custom log panel that maintains a list of recent log messages"""
    def __init__(self, max_lines: int = 10):
        self.logs = []
        self.max_lines = max_lines
    
    def add_log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[dim]{timestamp}[/dim] {message}")
        if len(self.logs) > self.max_lines:
            self.logs.pop(0)
    
    def __rich__(self) -> Panel:
        return Panel(
            "\n".join(self.logs),
            title="Operation Log",
            border_style="blue"
        )

class OPMLManager:
    def __init__(self, opml_file: str):
        self.opml_file = Path(opml_file)
        self.deleted_file = Path("deleted_feeds.opml")
        self.cache_file = Path("feed_cache.pkl")
        self.feeds: Dict[str, dict] = {}
        self.feed_cache: Dict[str, FeedCache] = {}
        self.genres = set(['News', 'Technology', 'Science', 'Entertainment', 'Sports', 'Dead', 'Other'])
        self.log_panel = LogPanel()
        self.setup_logging()
        self.load_cache()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[RichHandler(console=console, show_path=False)]
        )
        self.logger = logging.getLogger("opml_manager")

    def log_operation(self, message: str):
        """Log an operation to both file and panel"""
        self.logger.info(message)
        self.log_panel.add_log(message)

    def load_cache(self):
        """Load feed cache from disk"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'rb') as f:
                    self.feed_cache = pickle.load(f)
                self.log_operation(f"Loaded cache with {len(self.feed_cache)} entries")
        except Exception as e:
            self.log_operation(f"Error loading cache: {str(e)}")
            self.feed_cache = {}

    def save_cache(self):
        """Save feed cache to disk"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.feed_cache, f)
            self.log_operation("Cache saved successfully")
        except Exception as e:
            self.log_operation(f"Error saving cache: {str(e)}")

    async def check_feed_health(self, url: str) -> bool:
        """Check if a feed is accessible and valid"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        return False
                    content = await response.text()
                    feed = feedparser.parse(content)
                    return not feed.get('bozo', True)
        except:
            return False

    def get_content_hash(self, feed_data: feedparser.FeedParserDict) -> str:
        """Generate a hash of feed content to detect changes"""
        content = []
        for entry in feed_data.entries[:5]:
            content.extend([
                entry.get('title', ''),
                entry.get('link', ''),
                entry.get('description', '')
            ])
        return hashlib.md5(''.join(content).encode()).hexdigest()

    async def verify_feeds(self):
        """Verify all feeds and update their status"""
        self.log_operation("Starting feed verification...")
        
        async def verify_feed(feed_hash: str, feed_data: dict):
            url = feed_data['url']
            cache_entry = self.feed_cache.get(feed_hash)
            
            # Skip recently checked feeds
            if cache_entry and time.time() - cache_entry.last_checked < 3600:  # 1 hour
                return
            
            is_valid = await self.check_feed_health(url)
            
            if not is_valid and feed_data['genre'] != 'Dead':
                feed_data['genre'] = 'Dead'
                self.log_operation(f"Marked feed as dead: {feed_data['title']}")
            
            # Update cache
            self.feed_cache[feed_hash] = FeedCache(
                last_checked=time.time(),
                is_valid=is_valid,
                title=feed_data['title'],
                genre=feed_data['genre'],
                description=feed_data.get('description', ''),
                last_content_hash=''  # Will be updated when content is fetched
            )

        # Verify feeds concurrently
        tasks = [verify_feed(h, f) for h, f in self.feeds.items()]
        await asyncio.gather(*tasks)
        self.save_cache()

    def load_opml(self) -> None:
        """Load and parse the OPML file using listparser."""
        try:
            with open(self.opml_file) as f:
                result = listparser.parse(f.read())
            
            for feed in result.feeds:
                feed_url = feed.url
                feed_hash = hashlib.md5(feed_url.encode()).hexdigest()
                
                # Check cache for genre
                cache_entry = self.feed_cache.get(feed_hash)
                genre = cache_entry.genre if cache_entry else getattr(feed, 'category', 'Other')
                
                self.feeds[feed_hash] = {
                    'title': feed.title or '',
                    'url': feed_url,
                    'genre': genre,
                    'description': getattr(feed, 'description', '')
                }
            
            self.log_operation(f"Loaded {len(self.feeds)} feeds from OPML file")
        except Exception as e:
            self.log_operation(f"Error loading OPML file: {str(e)}")
            raise

    # ... [Previous methods remain the same: dedupe_feeds, create_opml_tree, etc.]

def create_layout() -> Layout:
    """Create the application layout"""
    layout = Layout()
    
    layout.split_column([
        Layout(name="main", ratio=3),
        Layout(name="log", ratio=1)
    ])
    
    return layout

def main():
    """Main function to run the OPML manager."""
    try:
        layout = create_layout()
        manager = OPMLManager("feeds.opml")
        
        with Live(layout, refresh_per_second=4, screen=True):
            # Load and process feeds
            manager.load_opml()
            dupes = manager.dedupe_feeds()
            
            # Verify feeds
            asyncio.run(manager.verify_feeds())
            
            while True:
                # Update layout
                layout["main"].update(display_feeds(manager.feeds))
                layout["log"].update(manager.log_panel)
                
                console.print("\n[bold cyan]Actions:[/bold cyan]")
                console.print("1. View latest articles")
                console.print("2. Change feed genre")
                console.print("3. Delete feed")
                console.print("4. Save changes")
                console.print("5. Verify feeds")
                console.print("6. Exit")
                
                choice = Prompt.ask("Choose an action", choices=['1', '2', '3', '4', '5', '6'])
                
                # ... [Previous action handling code]
                
                if choice == '5':
                    asyncio.run(manager.verify_feeds())
                
                elif choice == '6':
                    if Confirm.ask("Save changes before exiting?"):
                        manager.save_opml(manager.opml_file)
                        manager.save_cache()
                    break

    except Exception as e:
        manager.log_operation(f"Application error: {str(e)}")
        raise

if __name__ == "__main__":
    main()
