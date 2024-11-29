import unittest
from unittest.mock import patch, MagicMock
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from datetime import datetime
import feedparser
from src.ui.display import display_feeds, display_latest_articles
from src.models.feed import Feed

class TestDisplay(unittest.TestCase):

    @patch('src.ui.display.console')
    def test_display_feeds(self, mock_console):
        feeds = {
            'hash1': Feed(title='Feed 1', url='http://example.com/feed1', genre='Technology'),
            'hash2': Feed(title='Feed 2', url='http://example.com/feed2', genre='Science'),
            'hash3': Feed(title='Feed 3', url='http://example.com/feed3', genre='News')
        }
        display_feeds(feeds)
        
        # Check if the console.print method was called with a Table
        self.assertTrue(mock_console.print.called)
        printed_table = mock_console.print.call_args[0][0]
        self.assertIsInstance(printed_table, Table)
        
        # Check table content
        self.assertEqual(len(printed_table.rows), 3)
        self.assertEqual(printed_table.rows[0].cells[1], 'Feed 1')
        self.assertEqual(printed_table.rows[1].cells[1], 'Feed 2')
        self.assertEqual(printed_table.rows[2].cells[1], 'Feed 3')

    @patch('src.ui.display.console')
    @patch('src.ui.display.feedparser.parse')
    def test_display_latest_articles(self, mock_parse, mock_console):
        mock_parse.return_value = MagicMock(entries=[
            {'title': 'Article 1', 'published_parsed': datetime(2023, 1, 1).timetuple()},
            {'title': 'Article 2', 'published_parsed': datetime(2023, 1, 2).timetuple()},
            {'title': 'Article 3', 'published_parsed': datetime(2023, 1, 3).timetuple()},
        ])
        
        display_latest_articles('http://example.com/feed')
        
        # Check if the console.print method was called with a Panel
        self.assertTrue(mock_console.print.called)
        printed_panel = mock_console.print.call_args[0][0]
        self.assertIsInstance(printed_panel, Panel)
        
        # Check panel content
        printed_table = printed_panel.renderable
        self.assertIsInstance(printed_table, Table)
        self.assertEqual(len(printed_table.rows), 3)
        self.assertEqual(printed_table.rows[0].cells[1], 'Article 1')
        self.assertEqual(printed_table.rows[1].cells[1], 'Article 2')
        self.assertEqual(printed_table.rows[2].cells[1], 'Article 3')

    @patch('src.ui.display.console')
    def test_display_feeds_special_characters(self, mock_console):
        feeds = {
            'hash1': Feed(title='Feed & 1', url='http://example.com/feed1', genre='Technology'),
            'hash2': Feed(title='Feed < 2', url='http://example.com/feed2', genre='Science'),
            'hash3': Feed(title='Feed > 3', url='http://example.com/feed3', genre='News')
        }
        display_feeds(feeds)
        
        # Check if the console.print method was called with a Table
        self.assertTrue(mock_console.print.called)
        printed_table = mock_console.print.call_args[0][0]
        self.assertIsInstance(printed_table, Table)
        
        # Check table content for special characters
        self.assertEqual(printed_table.rows[0].cells[1], 'Feed & 1')
        self.assertEqual(printed_table.rows[1].cells[1], 'Feed < 2')
        self.assertEqual(printed_table.rows[2].cells[1], 'Feed > 3')

    @patch('src.ui.display.console')
    def test_display_feeds_long_text_truncation(self, mock_console):
        long_title = 'Feed ' + 'A' * 100
        feeds = {
            'hash1': Feed(title=long_title, url='http://example.com/feed1', genre='Technology')
        }
        display_feeds(feeds)
        
        # Check if the console.print method was called with a Table
        self.assertTrue(mock_console.print.called)
        printed_table = mock_console.print.call_args[0][0]
        self.assertIsInstance(printed_table, Table)
        
        # Check table content for long text truncation
        self.assertTrue(len(printed_table.rows[0].cells[1]) < len(long_title))

if __name__ == '__main__':
    unittest.main()
