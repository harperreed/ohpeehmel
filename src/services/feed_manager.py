import listparser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
import logging
from xml.dom import minidom
import xml.etree.ElementTree as ET

from src.models.feed import Feed
from src.utils.xml_helpers import create_opml_tree
from src.services.genre_detector import GenreDetector
from src.services.feed_validator import FeedValidator



class FeedManager:
    def __init__(self, opml_file: str):
        self.opml_file = Path(opml_file)
        self.deleted_file = Path("deleted_feeds.opml")
        self.invalid_file = Path("invalid_feeds.opml")
        self.feeds: Dict[str, Feed] = {}
        self.genre_detector = GenreDetector()
        self.feed_validator = FeedValidator(timeout=10)

    async def load_opml(self) -> Tuple[int, Dict[str, str]]:
        """Load and parse the OPML file using listparser.

        Returns:
            Tuple[int, Dict[str, str]]: Number of feeds loaded and dict of invalid feeds with errors
        """
        try:
            with open(self.opml_file) as f:
                result = listparser.parse(f.read())

            # First pass: Create Feed objects
            feeds_to_validate = []
            feed_map = {}  # Map URLs to Feed objects

            for feed_data in result.feeds:
                feed = Feed(
                    title=feed_data.title or "",
                    url=feed_data.url,
                    genre=getattr(feed_data, "category", "Other"),
                    description=getattr(feed_data, "description", ""),
                )
                feeds_to_validate.append(feed_data.url)
                feed_map[feed_data.url] = feed

            # Validate all feeds concurrently
            validation_results = await self.feed_validator.validate_feeds(
                feeds_to_validate
            )

            # Process results
            invalid_feeds = {}
            for url, (is_valid, error_msg) in validation_results.items():
                if is_valid:
                    feed = feed_map[url]
                    self.feeds[feed.hash] = feed
                else:
                    invalid_feeds[url] = error_msg or "Unknown error"

            # Save invalid feeds to separate file
            if invalid_feeds:
                # Group invalid feeds by their original category
                invalid_feeds_by_genre: Dict[str, List[Feed]] = {}
                for url, error in invalid_feeds.items():
                    feed = feed_map[url]
                    if feed.genre not in invalid_feeds_by_genre:
                        invalid_feeds_by_genre[feed.genre] = []

                    # Create a copy of the feed with error in description
                    invalid_feed = Feed(
                        title=feed.title,
                        url=url,
                        genre=feed.genre,  # Preserve original genre
                        description=f"{feed.description}\nValidation Error: {error}",
                    )
                    invalid_feeds_by_genre[feed.genre].append(invalid_feed)
                await self._save_invalid_feeds(invalid_feeds_by_genre)

            logging.info(f"Loaded {len(self.feeds)} valid feeds from OPML file")
            logging.warning(f"Found {len(invalid_feeds)} invalid feeds")

            return len(self.feeds), invalid_feeds

        except Exception as e:
            logging.error(f"Error loading OPML file: {str(e)}")
            raise

    async def _save_invalid_feeds(self, invalid_feeds_by_genre: List[Feed]) -> None:
        """Save invalid feeds to a separate OPML file."""
        root = create_opml_tree(
            invalid_feeds_by_genre,
            title="Invalid RSS Feeds - Grouped by Original Category",
        )
        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

        with open(self.invalid_file, "w", encoding="utf-8") as f:
            f.write(xmlstr)

        logging.info(
            f"Saved {len(invalid_feeds_by_genre)} invalid feeds to {self.invalid_file}"
        )

    def dedupe_feeds(self) -> int:
        """Remove duplicate feeds based on URL."""
        seen_urls = set()
        duplicate_hashes = set()

        for feed_hash, feed in list(self.feeds.items()):
            if feed.url in seen_urls:
                duplicate_hashes.add(feed_hash)
            else:
                seen_urls.add(feed.url)

        for hash_to_remove in duplicate_hashes:
            del self.feeds[hash_to_remove]

        logging.info(f"Removed {len(duplicate_hashes)} duplicate feeds")
        return len(duplicate_hashes)

    def save_opml(self, filename: Path) -> None:
        """Save feeds to an OPML file."""
        genre_feeds: Dict[str, List[Feed]] = {}
        for feed in self.feeds.values():
            if feed.genre not in genre_feeds:
                genre_feeds[feed.genre] = []
            genre_feeds[feed.genre].append(feed)

        root = create_opml_tree(genre_feeds)
        xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(xmlstr)

        logging.info(f"Saved OPML file to {filename}")

    def move_to_deleted(self, feed_hash: str) -> None:
        """Move a feed to the deleted feeds file."""
        try:
            # Load existing deleted feeds
            deleted_feeds: List[Feed] = []
            if self.deleted_file.exists():
                with open(self.deleted_file) as f:
                    result = listparser.parse(f.read())
                for feed_data in result.feeds:
                    feed = Feed(
                        title=feed_data.title,
                        url=feed_data.url,
                        genre=getattr(feed_data, "category", "Other"),
                        description=getattr(feed_data, "description", ""),
                        deleted_at=datetime.fromisoformat(
                            getattr(feed_data, "deletedAt", datetime.now().isoformat())
                        ),
                    )
                    deleted_feeds.append(feed)

            # Add the feed to deleted feeds
            feed = self.feeds[feed_hash]
            feed.deleted_at = datetime.now()
            deleted_feeds.append(feed)

            # Save deleted feeds file
            genre_feeds = {}
            for feed in deleted_feeds:
                if feed.genre not in genre_feeds:
                    genre_feeds[feed.genre] = []
                genre_feeds[feed.genre].append(feed)

            root = create_opml_tree(genre_feeds, title="Deleted RSS Feeds")
            xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

            with open(self.deleted_file, "w", encoding="utf-8") as f:
                f.write(xmlstr)

            # Remove from active feeds
            del self.feeds[feed_hash]
            logging.info(f"Moved feed {feed.title} to deleted feeds")

        except Exception as e:
            logging.error(f"Error moving feed to deleted: {str(e)}")
            raise
