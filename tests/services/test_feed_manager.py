import pytest
from unittest.mock import patch, mock_open
from pathlib import Path
from src.services.feed_manager import FeedManager
from src.models.feed import Feed


@pytest.fixture
def valid_opml_content():
    return """<?xml version="1.0" encoding="UTF-8"?>
    <opml version="1.0">
        <head>
            <title>Test OPML</title>
        </head>
        <body>
            <outline text="Technology" title="Technology">
                <outline text="TechCrunch" title="TechCrunch" type="rss" xmlUrl="http://feeds.feedburner.com/TechCrunch/" />
            </outline>
        </body>
    </opml>"""


@pytest.fixture
def invalid_opml_content():
    return """<?xml version="1.0" encoding="UTF-8"?>
    <opml version="1.0">
        <head>
            <title>Test OPML</title>
        </head>
        <body>
            <outline text="Technology" title="Technology">
                <outline text="InvalidFeed" title="InvalidFeed" type="rss" xmlUrl="http://invalid.url/" />
            </outline>
        </body>
    </opml>"""


@pytest.fixture
def feed_manager():
    return FeedManager("feeds.opml")


def test_load_valid_opml(feed_manager, valid_opml_content):
    with patch("builtins.open", mock_open(read_data=valid_opml_content)):
        valid_count, invalid_feeds = feed_manager.load_opml()
        assert valid_count == 1
        assert len(invalid_feeds) == 0


def test_load_invalid_opml(feed_manager, invalid_opml_content):
    with patch("builtins.open", mock_open(read_data=invalid_opml_content)):
        with patch(
            "src.services.feed_validator.FeedValidator.validate_feeds",
            return_value={"http://invalid.url/": (False, "Invalid feed")},
        ):
            valid_count, invalid_feeds = feed_manager.load_opml()
            assert valid_count == 0
            assert len(invalid_feeds) == 1
            assert "http://invalid.url/" in invalid_feeds


def test_save_opml(feed_manager, valid_opml_content):
    with patch("builtins.open", mock_open(read_data=valid_opml_content)):
        feed_manager.load_opml()
        with patch("builtins.open", mock_open()) as mocked_file:
            feed_manager.save_opml(Path("feeds.opml"))
            mocked_file.assert_called_once_with(
                Path("feeds.opml"), "w", encoding="utf-8"
            )


def test_add_remove_update_feed(feed_manager, valid_opml_content):
    with patch("builtins.open", mock_open(read_data=valid_opml_content)):
        feed_manager.load_opml()
        new_feed = Feed(title="New Feed", url="http://newfeed.com", genre="News")
        feed_manager.feeds[new_feed.hash] = new_feed
        assert len(feed_manager.feeds) == 2

        del feed_manager.feeds[new_feed.hash]
        assert len(feed_manager.feeds) == 1

        feed_manager.feeds[new_feed.hash] = new_feed
        feed_manager.feeds[new_feed.hash].title = "Updated Feed"
        assert feed_manager.feeds[new_feed.hash].title == "Updated Feed"


def test_move_to_deleted(feed_manager, valid_opml_content):
    with patch("builtins.open", mock_open(read_data=valid_opml_content)):
        feed_manager.load_opml()
        feed_hash = list(feed_manager.feeds.keys())[0]
        feed_manager.move_to_deleted(feed_hash)
        assert len(feed_manager.feeds) == 0
        with open(feed_manager.deleted_file) as f:
            content = f.read()
            assert "TechCrunch" in content
            assert "deletedAt" in content
