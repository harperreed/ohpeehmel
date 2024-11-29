import feedparser
import logging
from typing import Set

class GenreDetector:
    def __init__(self):
        self.genres: Set[str] = {'News', 'Technology', 'Science', 'Entertainment', 'Sports', 'Other'}
        self.genre_keywords = {
            'Technology': ['tech', 'programming', 'software', 'hardware', 'ai', 'code'],
            'Science': ['science', 'research', 'study', 'discovery', 'space', 'physics'],
            'News': ['news', 'politics', 'world', 'breaking', 'report'],
            'Entertainment': ['movie', 'music', 'celebrity', 'entertainment', 'film'],
            'Sports': ['sports', 'game', 'player', 'team', 'score', 'match']
        }

    def guess_genre(self, feed_url: str) -> str:
        """Attempt to guess the genre of a feed based on its content."""
        try:
            feed = feedparser.parse(feed_url)
            
            text = ' '.join([
                entry.get('title', '') + ' ' + entry.get('description', '')
                for entry in feed.entries[:5]
            ]).lower()
            
            genre_scores = {genre: 0 for genre in self.genre_keywords}
            for genre, keywords in self.genre_keywords.items():
                genre_scores[genre] = sum(1 for keyword in keywords if keyword in text)
            
            max_score = max(genre_scores.values())
            if max_score > 0:
                return max(genre_scores.items(), key=lambda x: x[1])[0]
            return 'Other'
            
        except Exception as e:
            logging.warning(f"Error guessing genre for {feed_url}: {str(e)}")
            return 'Other'
