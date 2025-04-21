"""
Tests for the GeocodioClient class
"""

import pytest
from geocodio import GeocodioClient


def test_client_initialization():
    """Test that the client can be initialized with an API key"""
    client = GeocodioClient(api_key="test-key")
    assert client.api_key == "test-key"
    assert client.hostname == "api.geocod.io"


def test_client_initialization_with_env_var(monkeypatch):
    """Test that the client can be initialized with an environment variable"""
    monkeypatch.setenv("GEOCODIO_API_KEY", "env-key")
    client = GeocodioClient()
    assert client.api_key == "env-key"


def test_client_initialization_no_key():
    """Test that the client raises an error when no API key is provided"""
    with pytest.raises(Exception):
        GeocodioClient(api_key="")