"""
Tests for geocoding functionality.
"""
import os
from typing import List

import pytest
from dotenv import load_dotenv

from geocodio import GeocodioClient
from geocodio.exceptions import AuthenticationError

# Load environment variables from .env file
load_dotenv()

@pytest.fixture
def client() -> GeocodioClient:
    """Create a GeocodioClient instance for testing."""
    api_key = os.getenv("GEOCODIO_API_KEY")
    if not api_key:
        pytest.skip("GEOCODIO_API_KEY environment variable not set")
    return GeocodioClient(api_key)

def test_client_requires_api_key():
    """Test that client raises AuthenticationError when no API key is provided."""
    with pytest.raises(AuthenticationError):
        GeocodioClient("")

def test_single_forward_geocode(client: GeocodioClient):
    """Test forward geocoding of a single address."""
    response = client.geocode("3730 N Clark St, Chicago, IL")

    assert response.input is not None
    assert len(response.results) > 0

    result = response.results[0]
    assert result.formatted_address == "3730 N Clark St, Chicago, IL 60613"
    assert result.accuracy > 0.9
    assert result.accuracy_type == "rooftop"
    assert result.source == "Cook"

    # Check location
    assert 41.94 < result.location.lat < 41.95
    assert -87.66 < result.location.lng < -87.65

    # Check address components
    components = result.address_components
    assert components.number == "3730"
    assert components.predirectional == "N"
    assert components.street == "Clark"
    assert components.suffix == "St"
    assert components.city == "Chicago"
    assert components.state == "IL"
    assert components.zip == "60613"

def test_batch_forward_geocode(client: GeocodioClient):
    """Test forward geocoding of multiple addresses."""
    addresses: List[str] = [
        "3730 N Clark St, Chicago, IL",
        "638 E 13th Ave, Denver, CO"
    ]
    response = client.geocode(addresses)

    assert len(response.results) == 2

    # Check first address
    chicago = response.results[0]
    assert chicago.formatted_address == "3730 N Clark St, Chicago, IL 60613"
    assert chicago.accuracy > 0.9
    assert chicago.accuracy_type == "rooftop"

    # Check second address
    denver = response.results[1]
    assert denver.formatted_address == "638 E 13th Ave, Denver, CO 80203"
    assert denver.accuracy > 0.9
    assert denver.accuracy_type == "rooftop"

def test_single_reverse_geocode(client: GeocodioClient):
    """Test reverse geocoding of coordinates."""
    response = client.reverse("38.9002898,-76.9990361")

    assert len(response.results) > 0
    result = response.results[0]

    # The exact address might vary but should be in Washington DC
    assert "Washington" in result.formatted_address
    assert "DC" in result.formatted_address
    assert result.accuracy > 0.9
    assert result.accuracy_type == "rooftop"

    # Check location is close to input coordinates
    assert 38.89 < result.location.lat < 38.91
    assert -77.00 < result.location.lng < -76.99

def test_geocode_with_fields(client: GeocodioClient):
    """Test geocoding with additional data fields."""
    response = client.geocode(
        "3730 N Clark St, Chicago, IL",
        fields=["cd", "timezone"]
    )

    assert len(response.results) > 0
    result = response.results[0]

    # Check timezone data
    assert result.fields is not None
    assert result.fields.timezone is not None
    assert result.fields.timezone.name == "America/Chicago"
    assert result.fields.timezone.utc_offset == -6
    assert result.fields.timezone.observes_dst is True

    # Congressional district data might change, but should be present
    assert result.fields.congressional_districts is not None
    district = result.fields.congressional_districts[0]
    assert district.district_number > 0
    assert "Congressional District" in district.name
    assert district.congress_number is not None