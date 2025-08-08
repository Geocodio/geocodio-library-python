"""
Tests for geocoding functionality.
"""
import os
from typing import List

import pytest
from dotenv import load_dotenv

from geocodio import Geocodio
from geocodio.exceptions import AuthenticationError

# Load environment variables from .env file
load_dotenv()

@pytest.fixture
def client() -> Geocodio:
    """Create a Geocodio instance for testing."""
    api_key = os.getenv("GEOCODIO_API_KEY")
    if not api_key:
        pytest.skip("GEOCODIO_API_KEY environment variable not set")
    return Geocodio(api_key)

def test_client_requires_api_key():
    """Test that client raises AuthenticationError when no API key is provided."""
    # Temporarily unset the environment variable
    original_key = os.environ.get("GEOCODIO_API_KEY")
    if original_key:
        del os.environ["GEOCODIO_API_KEY"]

    try:
        with pytest.raises(AuthenticationError):
            Geocodio("")
    finally:
        # Restore the environment variable
        if original_key:
            os.environ["GEOCODIO_API_KEY"] = original_key

def test_single_forward_geocode(client: Geocodio):
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

def test_batch_forward_geocode(client: Geocodio):
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

def test_single_reverse_geocode(client: Geocodio):
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

def test_geocode_with_fields(client: Geocodio):
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
    assert result.fields.timezone.extras["abbreviation"] == "CST"
    assert result.fields.timezone.extras["source"] == "© OpenStreetMap contributors"

    # Check congressional district data
    assert result.fields.congressional_districts is not None
    district = result.fields.congressional_districts[0]
    assert district.name == "Congressional District 5"
    assert district.district_number == 5
    assert district.ocd_id == "ocd-division/country:us/state:il/cd:5"
    assert district.congress_number == "119th"
    assert district.congress_years == "2025-2027"
    assert district.proportion == 1
    assert len(district.current_legislators) > 0