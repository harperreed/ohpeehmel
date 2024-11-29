import asyncio
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress
from rich.table import Table
import logging

from utils.logger import setup_logging
from services.feed_manager import FeedManager
from ui.display import display_feeds, display_latest_articles

console = Console()


async def main():
    """Main function to run the OPML manager."""
    try:
        console.print("[bold blue]OPML Feed Manager[/bold blue]")

        # Initialize
        setup_logging()
        opml_file = Prompt.ask("Enter OPML file path", default="feeds.opml")
        manager = FeedManager(opml_file)

        # Load and validate feeds
        with console.status("[bold green]Loading and validating OPML file..."):
            valid_count, invalid_feeds = await manager.load_opml()

        # Report validation results
        if invalid_feeds:
            console.print("\n[yellow]Invalid feeds found:[/yellow]")
            table = Table(show_header=True, header_style="bold yellow")
            table.add_column("URL")
            table.add_column("Error")
            for url, error in invalid_feeds.items():
                table.add_row(url, error)
            console.print(table)
            console.print(
                f"\nInvalid feeds have been saved to '{manager.invalid_file}'"
            )
            Prompt.ask("\nPress Enter to continue")

        # Dedupe feeds
        dupes = manager.dedupe_feeds()
        if dupes:
            console.print(f"[yellow]Removed {dupes} duplicate feeds[/yellow]")

        # Process feeds
        with Progress() as progress:
            task = progress.add_task(
                "[cyan]Analyzing feeds...", total=len(manager.feeds)
            )

            for feed_hash, feed in manager.feeds.items():
                if feed.genre == "Other":
                    feed.genre = manager.genre_detector.guess_genre(feed.url)
                progress.advance(task)

        while True:
            console.clear()
            display_feeds(manager.feeds)

            console.print("\n[bold cyan]Actions:[/bold cyan]")
            console.print("1. View latest articles")
            console.print("2. Change feed genre")
            console.print("3. Delete feed")
            console.print("4. Save changes")
            console.print("5. Exit")

            choice = Prompt.ask("Choose an action", choices=["1", "2", "3", "4", "5"])

            if choice == "1":
                feed_num = int(Prompt.ask("Enter feed number")) - 1
                if 0 <= feed_num < len(manager.feeds):
                    feed_hash = list(manager.feeds.keys())[feed_num]
                    display_latest_articles(manager.feeds[feed_hash].url)
                    Prompt.ask("\nPress Enter to continue")

            elif choice == "2":
                feed_num = int(Prompt.ask("Enter feed number")) - 1
                if 0 <= feed_num < len(manager.feeds):
                    feed_hash = list(manager.feeds.keys())[feed_num]
                    console.print(
                        "\nAvailable genres:",
                        ", ".join(sorted(manager.genre_detector.genres)),
                    )
                    new_genre = Prompt.ask("Enter new genre")
                    if new_genre in manager.genre_detector.genres:
                        manager.feeds[feed_hash].genre = new_genre
                        console.print("[green]Genre updated successfully[/green]")

            elif choice == "3":
                feed_num = int(Prompt.ask("Enter feed number")) - 1
                if 0 <= feed_num < len(manager.feeds):
                    feed_hash = list(manager.feeds.keys())[feed_num]
                    if Confirm.ask(f"Delete {manager.feeds[feed_hash].title}?"):
                        manager.move_to_deleted(feed_hash)
                        console.print("[green]Feed deleted successfully[/green]")

            elif choice == "4":
                with console.status("[bold green]Saving changes..."):
                    manager.save_opml(manager.opml_file)
                console.print("[green]Changes saved successfully[/green]")
                Prompt.ask("\nPress Enter to continue")

            elif choice == "5":
                if Confirm.ask("Save changes before exiting?"):
                    manager.save_opml(manager.opml_file)
                break

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        logging.error(f"Application error: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
