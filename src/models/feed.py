from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Feed:
    title: str
    url: str
    genre: str
    description: str = ''
    deleted_at: Optional[datetime] = None

    @property
    def hash(self) -> str:
        """Generate a unique hash for the feed based on its URL."""
        import hashlib
        return hashlib.md5(self.url.encode()).hexdigest()
