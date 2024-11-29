import unittest
import xml.etree.ElementTree as ET
from datetime import datetime
from src.utils.xml_helpers import create_opml_tree
from src.models.feed import Feed

class TestXMLHelpers(unittest.TestCase):

    def setUp(self):
        self.feeds_by_genre = {
            "Technology": [
                Feed(title="TechCrunch", url="http://techcrunch.com/feed", genre="Technology", description="Tech news"),
                Feed(title="Wired", url="http://wired.com/feed", genre="Technology", description="Wired news")
            ],
            "Science": [
                Feed(title="ScienceDaily", url="http://sciencedaily.com/feed", genre="Science", description="Science news")
            ]
        }

    def test_create_opml_tree_valid_feed_data(self):
        root = create_opml_tree(self.feeds_by_genre, title="Valid Feeds")
        self.assertEqual(root.tag, "opml")
        self.assertEqual(root.attrib["version"], "1.0")
        self.assertEqual(root.find("head/title").text, "Valid Feeds")
        self.assertEqual(len(root.find("body").findall("outline")), 2)

    def test_create_opml_tree_empty_feed_lists(self):
        root = create_opml_tree({}, title="Empty Feeds")
        self.assertEqual(root.tag, "opml")
        self.assertEqual(root.attrib["version"], "1.0")
        self.assertEqual(root.find("head/title").text, "Empty Feeds")
        self.assertEqual(len(root.find("body").findall("outline")), 0)

    def test_create_opml_tree_special_characters_in_feed_data(self):
        feeds_with_special_chars = {
            "Technology": [
                Feed(title="Tech & Crunch", url="http://techcrunch.com/feed", genre="Technology", description="Tech & news")
            ]
        }
        root = create_opml_tree(feeds_with_special_chars, title="Special Characters")
        self.assertEqual(root.tag, "opml")
        self.assertEqual(root.attrib["version"], "1.0")
        self.assertEqual(root.find("head/title").text, "Special Characters")
        self.assertEqual(len(root.find("body").findall("outline")), 1)
        self.assertEqual(root.find("body/outline/outline").attrib["text"], "Tech & Crunch")

    def test_create_opml_tree_multiple_genres(self):
        root = create_opml_tree(self.feeds_by_genre, title="Multiple Genres")
        self.assertEqual(root.tag, "opml")
        self.assertEqual(root.attrib["version"], "1.0")
        self.assertEqual(root.find("head/title").text, "Multiple Genres")
        self.assertEqual(len(root.find("body").findall("outline")), 2)

    def test_create_opml_tree_nested_structure_accuracy(self):
        root = create_opml_tree(self.feeds_by_genre, title="Nested Structure")
        self.assertEqual(root.tag, "opml")
        self.assertEqual(root.attrib["version"], "1.0")
        self.assertEqual(root.find("head/title").text, "Nested Structure")
        self.assertEqual(len(root.find("body").findall("outline")), 2)
        tech_outline = root.find("body/outline[@text='Technology']")
        self.assertIsNotNone(tech_outline)
        self.assertEqual(len(tech_outline.findall("outline")), 2)

if __name__ == "__main__":
    unittest.main()
