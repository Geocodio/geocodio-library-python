"""
Test configuration and fixtures
"""

import logging
import os

import pytest
import httpx2 as httpx
from dotenv import load_dotenv

from geocodio import Geocodio


class _HttpxMock:
    """Simple compatibility replacement for pytest-httpx's httpx_mock fixture."""

    def __init__(self):
        self._callbacks = []

    def add_callback(self, callback=None, **kwargs):
        if callback is None:
            raise ValueError("callback is required")
        self._callbacks.append(callback)

    def add_response(
        self,
        *,
        url=None,
        match_headers=None,
        status_code=200,
        headers=None,
        content=None,
        json=None,
        text=None,
    ):
        self._callbacks.append(
            lambda request: httpx.Response(
                status_code,
                headers=headers,
                content=content,
                json=json,
                text=text,
            )
        )

    def _assert_options(self):
        assert not self._callbacks, (
            "The following responses are mocked but not requested: "
            f"{self._callbacks}"
        )


@pytest.fixture
def httpx_mock(monkeypatch):
    """Patch httpx2 transport methods to satisfy the tests' httpx_mock API."""
    mock = _HttpxMock()
    real_handle_request = httpx.HTTPTransport.handle_request

    def mocked_handle_request(transport, request):
        if not mock._callbacks:
            return real_handle_request(transport, request)
        callback = mock._callbacks.pop(0)
        return callback(request)

    monkeypatch.setattr(httpx.HTTPTransport, "handle_request", mocked_handle_request)

    real_handle_async_request = httpx.AsyncHTTPTransport.handle_async_request

    async def mocked_handle_async_request(transport, request):
        if not mock._callbacks:
            return await real_handle_async_request(transport, request)
        callback = mock._callbacks.pop(0)
        return callback(request)

    monkeypatch.setattr(
        httpx.AsyncHTTPTransport,
        "handle_async_request",
        mocked_handle_async_request,
    )

    yield mock
    mock._assert_options()

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture
def client(request):
    """Create a Geocodio instance with test configuration"""
    # Use TEST_KEY for all tests except e2e tests
    if "e2e" in request.node.fspath.strpath:
        logger.debug("Running e2e tests - using API key from environment")
        api_key = os.getenv("GEOCODIO_API_KEY")
        if not api_key:
            logger.warning("GEOCODIO_API_KEY not set - skipping e2e test")
            pytest.skip("GEOCODIO_API_KEY environment variable not set")
        return Geocodio(api_key=api_key)
    else:
        logger.debug("Running unit tests - using TEST_KEY with api.test hostname")
        return Geocodio(api_key="TEST_KEY", hostname="api.test")
