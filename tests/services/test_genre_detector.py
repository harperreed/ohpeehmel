import unittest
from unittest.mock import patch
from src.services.genre_detector import GenreDetector


class TestGenreDetector(unittest.TestCase):
    def setUp(self):
        self.detector = GenreDetector()

    @patch("src.services.genre_detector.feedparser.parse")
    def test_predefined_genre_keywords(self, mock_parse):
        mock_parse.return_value.entries = [
            {"title": "Tech News", "description": "Latest in AI and programming"},
            {"title": "Science Daily", "description": "New discovery in physics"},
        ]
        genre = self.detector.guess_genre("http://example.com/feed")
        self.assertEqual(genre, "Technology")

    @patch("src.services.genre_detector.feedparser.parse")
    def test_multiple_matching_keywords(self, mock_parse):
        mock_parse.return_value.entries = [
            {"title": "Tech and Science", "description": "AI and space research"}
        ]
        genre = self.detector.guess_genre("http://example.com/feed")
        self.assertEqual(genre, "Technology")

    @patch("src.services.genre_detector.feedparser.parse")
    def test_no_matching_keywords(self, mock_parse):
        mock_parse.return_value.entries = [
            {"title": "Cooking Tips", "description": "Best recipes for the season"}
        ]
        genre = self.detector.guess_genre("http://example.com/feed")
        self.assertEqual(genre, "Other")

    @patch("src.services.genre_detector.feedparser.parse")
    def test_case_sensitivity(self, mock_parse):
        mock_parse.return_value.entries = [
            {"title": "TECH NEWS", "description": "LATEST IN AI AND PROGRAMMING"}
        ]
        genre = self.detector.guess_genre("http://example.com/feed")
        self.assertEqual(genre, "Technology")

    @patch("src.services.genre_detector.feedparser.parse")
    def test_valid_feed_content(self, mock_parse):
        mock_parse.return_value.entries = [
            {"title": "Tech News", "description": "Latest in AI and programming"}
        ]
        genre = self.detector.guess_genre("http://example.com/feed")
        self.assertEqual(genre, "Technology")

    @patch("src.services.genre_detector.feedparser.parse")
    def test_empty_feed_content(self, mock_parse):
        mock_parse.return_value.entries = []
        genre = self.detector.guess_genre("http://example.com/feed")
        self.assertEqual(genre, "Other")

    @patch("src.services.genre_detector.feedparser.parse")
    def test_malformed_feed_content(self, mock_parse):
        mock_parse.return_value.entries = None
        genre = self.detector.guess_genre("http://example.com/feed")
        self.assertEqual(genre, "Other")

    @patch("src.services.genre_detector.feedparser.parse")
    def test_network_error(self, mock_parse):
        mock_parse.side_effect = Exception("Network error")
        genre = self.detector.guess_genre("http://example.com/feed")
        self.assertEqual(genre, "Other")

    @patch("src.services.genre_detector.feedparser.parse")
    def test_parse_error(self, mock_parse):
        mock_parse.return_value.bozo = True
        mock_parse.return_value.bozo_exception = Exception("Parse error")
        genre = self.detector.guess_genre("http://example.com/feed")
        self.assertEqual(genre, "Other")

    @patch("src.services.genre_detector.feedparser.parse")
    def test_invalid_content(self, mock_parse):
        mock_parse.return_value.entries = [
            {"title": "Invalid Content", "description": "This is not a valid feed"}
        ]
        genre = self.detector.guess_genre("http://example.com/feed")
        self.assertEqual(genre, "Other")


if __name__ == "__main__":
    unittest.main()
