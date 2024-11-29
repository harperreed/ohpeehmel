import aiohttp
import asyncio
import feedparser
import logging
from typing import Tuple, Optional, Dict
from aiohttp import ClientTimeout
from urllib.parse import urlparse

class FeedValidator:
    def __init__(self, timeout: int = 10, retry_delay: float = 1.0):
        """Initialize the feed validator.
        
        Args:
            timeout (int): Maximum time in seconds to wait for a feed response
            retry_delay (float): Delay in seconds between validation attempts
        """
        self.timeout = ClientTimeout(total=timeout)
        self.retry_delay = retry_delay
        self.headers = {
            'User-Agent': 'OhPeehMel/1.0 (https://github.com/yourusername/ohpeehmel; feed-validator) Python-Feedparser/6.0.11'
        }
    
    async def validate_feed(self, url: str) -> Tuple[bool, Optional[str]]:
        """Validate if a URL points to a valid RSS/Atom feed with two attempts.
        
        Args:
            url (str): The URL to validate
            
        Returns:
            Tuple[bool, Optional[str]]: A tuple containing:
                - Boolean indicating if the URL is a valid feed
                - Error message if validation failed, None otherwise
        """
        # Basic URL validation
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                return False, "Invalid URL format"
        except Exception as e:
            return False, f"URL parsing error: {str(e)}"

        # Two validation attempts
        for attempt in range(2):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout, headers=self.headers) as session:
                    async with session.get(url, allow_redirects=True) as response:
                        if response.status != 200:
                            if attempt == 0:  # Only log first attempt failures
                                logging.warning(f"First attempt failed for {url}: HTTP {response.status}")
                            if attempt < 1:  # Only delay if we're going to retry
                                await asyncio.sleep(self.retry_delay)
                            continue  # Try second attempt
                        
                        # Read the content
                        content = await response.text()
                        
                        # Parse with feedparser
                        feed = feedparser.parse(content)
                        
                        # Check if it's a valid feed
                        if feed.bozo:  # feedparser sets bozo on parse errors
                            if attempt == 0:
                                logging.warning(f"First attempt parse error for {url}: {str(feed.bozo_exception)}")
                            if attempt < 1:
                                await asyncio.sleep(self.retry_delay)
                            continue  # Try second attempt
                        
                        # Verify feed has basic required elements
                        if not hasattr(feed, 'entries') or not hasattr(feed, 'feed'):
                            if attempt < 1:
                                await asyncio.sleep(self.retry_delay)
                            continue  # Try second attempt
                        
                        # Feed is valid
                        return True, None
                    
            except asyncio.TimeoutError:
                if attempt == 0:
                    logging.warning(f"First attempt timeout for {url}")
                if attempt < 1:
                    await asyncio.sleep(self.retry_delay)
                continue  # Try second attempt
            except aiohttp.ClientError as e:
                if attempt == 0:
                    logging.warning(f"First attempt connection error for {url}: {str(e)}")
                if attempt < 1:
                    await asyncio.sleep(self.retry_delay)
                continue  # Try second attempt
            except Exception as e:
                logging.error(f"Unexpected error validating feed {url} (attempt {attempt + 1}): {str(e)}")
                if attempt < 1:
                    await asyncio.sleep(self.retry_delay)
                continue  # Try second attempt

        # If we get here, both attempts failed
        return False, f"Feed validation failed after 2 attempts"

    async def validate_feeds(self, urls: list[str]) -> dict[str, Tuple[bool, Optional[str]]]:
        """Validate multiple feeds concurrently.
        
        Args:
            urls (list[str]): List of URLs to validate
            
        Returns:
            dict[str, Tuple[bool, Optional[str]]]: Dictionary mapping URLs to their validation results
        """
        tasks = [self.validate_feed(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return dict(zip(urls, results))
