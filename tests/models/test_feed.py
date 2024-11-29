import unittest
from datetime import datetime
from src.models.feed import Feed


class TestFeed(unittest.TestCase):
    def test_feed_instantiation(self):
        # Test basic instantiation with required fields
        feed = Feed(title="Test Feed", url="http://example.com", genre="News")
        self.assertEqual(feed.title, "Test Feed")
        self.assertEqual(feed.url, "http://example.com")
        self.assertEqual(feed.genre, "News")
        self.assertEqual(feed.description, "")
        self.assertIsNone(feed.deleted_at)

        # Test instantiation with optional fields
        feed = Feed(
            title="Test Feed",
            url="http://example.com",
            genre="News",
            description="A test feed",
            deleted_at=datetime(2023, 1, 1),
        )
        self.assertEqual(feed.description, "A test feed")
        self.assertEqual(feed.deleted_at, datetime(2023, 1, 1))

    def test_hash_property(self):
        # Test hash generation with different URL formats
        feed1 = Feed(title="Feed 1", url="http://example.com", genre="News")
        feed2 = Feed(title="Feed 2", url="https://example.com", genre="News")
        self.assertNotEqual(feed1.hash, feed2.hash)

        # Verify hash consistency for the same URL
        feed3 = Feed(title="Feed 3", url="http://example.com", genre="News")
        self.assertEqual(feed1.hash, feed3.hash)

        # Test hash generation with special characters in URL
        feed4 = Feed(title="Feed 4", url="http://example.com/!@#$%^&*()", genre="News")
        self.assertIsNotNone(feed4.hash)

    def test_default_value_handling(self):
        # Test default value handling for optional fields
        feed = Feed(title="Test Feed", url="http://example.com", genre="News")
        self.assertEqual(feed.description, "")
        self.assertIsNone(feed.deleted_at)

    def test_datetime_handling(self):
        # Test datetime handling for deleted_at field
        feed = Feed(
            title="Test Feed",
            url="http://example.com",
            genre="News",
            deleted_at=datetime(2023, 1, 1),
        )
        self.assertEqual(feed.deleted_at, datetime(2023, 1, 1))


if __name__ == "__main__":
    unittest.main()
