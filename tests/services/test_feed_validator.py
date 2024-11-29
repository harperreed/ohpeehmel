import asyncio
import aiohttp
import pytest
from unittest.mock import patch, AsyncMock
from src.services.feed_validator import FeedValidator

@pytest.mark.asyncio
async def test_valid_url():
    validator = FeedValidator()
    url = "http://example.com/feed"
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.text = AsyncMock(return_value="<rss></rss>")
        is_valid, error = await validator.validate_feed(url)
        assert is_valid
        assert error is None

@pytest.mark.asyncio
async def test_invalid_url_format():
    validator = FeedValidator()
    url = "invalid-url"
    is_valid, error = await validator.validate_feed(url)
    assert not is_valid
    assert error == "Invalid URL format"

@pytest.mark.asyncio
async def test_url_with_special_characters():
    validator = FeedValidator()
    url = "http://example.com/feed?param=value&other=äöü"
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.text = AsyncMock(return_value="<rss></rss>")
        is_valid, error = await validator.validate_feed(url)
        assert is_valid
        assert error is None

@pytest.mark.asyncio
async def test_url_with_different_protocols():
    validator = FeedValidator()
    url = "https://example.com/feed"
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.text = AsyncMock(return_value="<rss></rss>")
        is_valid, error = await validator.validate_feed(url)
        assert is_valid
        assert error is None

@pytest.mark.asyncio
async def test_valid_rss_feed():
    validator = FeedValidator()
    url = "http://example.com/rss"
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.text = AsyncMock(return_value="<rss></rss>")
        is_valid, error = await validator.validate_feed(url)
        assert is_valid
        assert error is None

@pytest.mark.asyncio
async def test_valid_atom_feed():
    validator = FeedValidator()
    url = "http://example.com/atom"
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.text = AsyncMock(return_value="<feed></feed>")
        is_valid, error = await validator.validate_feed(url)
        assert is_valid
        assert error is None

@pytest.mark.asyncio
async def test_invalid_xml_feed():
    validator = FeedValidator()
    url = "http://example.com/invalid"
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.text = AsyncMock(return_value="<rss><rss>")
        is_valid, error = await validator.validate_feed(url)
        assert not is_valid
        assert error is not None

@pytest.mark.asyncio
async def test_empty_feed():
    validator = FeedValidator()
    url = "http://example.com/empty"
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.text = AsyncMock(return_value="")
        is_valid, error = await validator.validate_feed(url)
        assert not is_valid
        assert error is not None

@pytest.mark.asyncio
async def test_malformed_feed():
    validator = FeedValidator()
    url = "http://example.com/malformed"
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.text = AsyncMock(return_value="<rss><channel><title>Test</title></channel>")
        is_valid, error = await validator.validate_feed(url)
        assert not is_valid
        assert error is not None

@pytest.mark.asyncio
async def test_timeout_scenario():
    validator = FeedValidator(timeout=0.1)
    url = "http://example.com/timeout"
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = asyncio.TimeoutError
        is_valid, error = await validator.validate_feed(url)
        assert not is_valid
        assert error is not None

@pytest.mark.asyncio
async def test_connection_error():
    validator = FeedValidator()
    url = "http://example.com/connection-error"
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = aiohttp.ClientError
        is_valid, error = await validator.validate_feed(url)
        assert not is_valid
        assert error is not None

@pytest.mark.asyncio
async def test_redirect_handling():
    validator = FeedValidator()
    url = "http://example.com/redirect"
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 301
        mock_get.return_value.__aenter__.return_value.headers = {"Location": "http://example.com/new-location"}
        is_valid, error = await validator.validate_feed(url)
        assert not is_valid
        assert error is not None

@pytest.mark.asyncio
async def test_ssl_tls_issue():
    validator = FeedValidator()
    url = "https://example.com/ssl-tls"
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = aiohttp.ClientSSLError
        is_valid, error = await validator.validate_feed(url)
        assert not is_valid
        assert error is not None

@pytest.mark.asyncio
async def test_successful_retry_after_failure():
    validator = FeedValidator()
    url = "http://example.com/retry-success"
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [aiohttp.ClientError, AsyncMock(status=200, text=AsyncMock(return_value="<rss></rss>"))]
        is_valid, error = await validator.validate_feed(url)
        assert is_valid
        assert error is None

@pytest.mark.asyncio
async def test_multiple_failures():
    validator = FeedValidator()
    url = "http://example.com/multiple-failures"
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = aiohttp.ClientError
        is_valid, error = await validator.validate_feed(url)
        assert not is_valid
        assert error is not None

@pytest.mark.asyncio
async def test_delay_timing_accuracy():
    validator = FeedValidator(retry_delay=0.5)
    url = "http://example.com/delay-timing"
    with patch("aiohttp.ClientSession.get", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = [aiohttp.ClientError, AsyncMock(status=200, text=AsyncMock(return_value="<rss></rss>"))]
        is_valid, error = await validator.validate_feed(url)
        assert is_valid
        assert error is None
