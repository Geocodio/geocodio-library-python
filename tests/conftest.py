"""
Test configuration and fixtures
"""

import pytest
from geocodio import GeocodioClient


@pytest.fixture
def client():
    """Create a GeocodioClient instance with test configuration"""
    return GeocodioClient(api_key="TEST_KEY", hostname="api.test")