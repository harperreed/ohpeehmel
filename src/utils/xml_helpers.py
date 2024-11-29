import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List
from models.feed import Feed


def create_opml_tree(
    feeds_by_genre: Dict[str, List[Feed]], title: str = "RSS Feeds"
) -> ET.Element:
    """Create an OPML XML tree from feeds grouped by genre."""
    root = ET.Element("opml", version="1.0")
    head = ET.SubElement(root, "head")
    ET.SubElement(head, "title").text = title
    ET.SubElement(head, "dateModified").text = datetime.now().strftime(
        "%a, %d %b %Y %H:%M:%S %z"
    )

    body = ET.SubElement(root, "body")

    for genre in sorted(feeds_by_genre.keys()):
        genre_outline = ET.SubElement(body, "outline", text=genre)

        for feed in sorted(feeds_by_genre[genre], key=lambda x: x.title):
            feed_attrs = {
                "text": feed.title,
                "title": feed.title,
                "type": "rss",
                "xmlUrl": feed.url,
                "category": genre,
                "description": feed.description,
            }
            if feed.deleted_at:
                feed_attrs["deletedAt"] = feed.deleted_at.isoformat()

            ET.SubElement(genre_outline, "outline", **feed_attrs)

    return root
