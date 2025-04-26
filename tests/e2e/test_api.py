"""
End-to-end tests that make real API calls to Geocodio.
These tests require a valid GEOCODIO_API_KEY environment variable.
"""

import os
import pytest
from geocodio import GeocodioClient
from geocodio.exceptions import GeocodioError


@pytest.fixture
def client():
    """Create a client using the GEOCODIO_API_KEY environment variable."""
    api_key = os.getenv("GEOCODIO_API_KEY")
    if not api_key:
        pytest.skip("GEOCODIO_API_KEY environment variable not set")
    return GeocodioClient(api_key)


def test_integration_geocode(client):
    """Test real geocoding API call."""
    # Test address
    address = "1109 N Highland St, Arlington, VA"

    # Make the API call
    response = client.geocode(address)

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify core fields
    assert result.formatted_address is not None
    assert result.location is not None
    assert isinstance(result.location.lat, float)
    assert isinstance(result.location.lng, float)
    assert isinstance(result.accuracy, (float, int))  # API returns accuracy as int
    assert result.accuracy_type is not None
    assert result.source is not None

    # Verify address components
    components = result.address_components
    assert components.number == "1109"
    assert "Highland" in components.street
    assert components.city == "Arlington"
    assert components.state == "VA"
    assert components.zip is not None


def test_integration_reverse(client):
    """Test real reverse geocoding API call."""
    # Test coordinates (White House)
    lat, lng = 38.897699, -77.036547

    # Make the API call
    response = client.reverse((lat, lng))

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify core fields
    assert result.formatted_address is not None
    assert result.location is not None
    assert isinstance(result.location.lat, float)
    assert isinstance(result.location.lng, float)
    assert isinstance(result.accuracy, (float, int))  # API returns accuracy as int
    assert result.accuracy_type is not None
    assert result.source is not None

    # Verify address components
    components = result.address_components
    assert components.number is not None
    assert components.street is not None
    assert components.city is not None
    assert components.state is not None
    assert components.zip is not None


def test_integration_with_fields(client):
    """Test real API call with additional data fields."""
    # Test address
    address = "1600 Pennsylvania Ave NW, Washington, DC"

    # Request additional fields
    response = client.geocode(
        address,
        fields=["timezone", "cd", "census2020", "acs"]
    )

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify fields data
    fields = result.fields
    assert fields is not None

    # Check timezone (this seems to be consistently available)
    assert fields.timezone is not None
    assert fields.timezone.name is not None
    assert isinstance(fields.timezone.utc_offset, int)
    assert isinstance(fields.timezone.observes_dst, bool)

    # Note: Some fields might be None depending on data availability
    # We'll just verify the types when they are present
    if fields.congressional_districts:
        cd = fields.congressional_districts[0]
        assert cd.name is not None
        assert isinstance(cd.district_number, int)
        assert cd.congress_number is not None

    if fields.census2020:
        assert fields.census2020.tract is not None
        assert fields.census2020.block is not None
        assert fields.census2020.county_fips is not None
        assert fields.census2020.state_fips is not None

    if fields.acs:
        if fields.acs.population is not None:
            assert isinstance(fields.acs.population, int)
        if fields.acs.households is not None:
            assert isinstance(fields.acs.households, int)
        if fields.acs.median_income is not None:
            assert isinstance(fields.acs.median_income, int)
        if fields.acs.median_age is not None:
            assert isinstance(fields.acs.median_age, float)


def test_integration_batch_geocode(client):
    """Test real batch geocoding API call."""
    # Test addresses
    addresses = [
        "3730 N Clark St, Chicago, IL",
        "638 E 13th Ave, Denver, CO"
    ]

    # Make the API call
    response = client.geocode(addresses)

    # Verify response structure
    assert response is not None
    assert len(response.results) == 2

    # Check first address (Chicago)
    chicago = response.results[0]
    assert chicago.formatted_address == "3730 N Clark St, Chicago, IL 60613"
    assert chicago.accuracy > 0.9
    assert chicago.accuracy_type == "rooftop"
    assert chicago.source == "Cook"

    # Verify Chicago address components
    components = chicago.address_components
    assert components.number == "3730"
    assert components.predirectional == "N"
    assert components.street == "Clark"
    assert components.suffix == "St"
    assert components.city == "Chicago"
    assert components.state == "IL"
    assert components.zip == "60613"

    # Check second address (Denver)
    denver = response.results[1]
    assert denver.formatted_address == "638 E 13th Ave, Denver, CO 80203"
    assert denver.accuracy > 0.9
    assert denver.accuracy_type == "rooftop"
    assert "Denver" in denver.source

    # Verify Denver address components
    components = denver.address_components
    assert components.number == "638"
    assert components.predirectional == "E"
    assert components.street == "13th"
    assert components.suffix == "Ave"
    assert components.city == "Denver"
    assert components.state == "CO"
    assert components.zip == "80203"


def test_integration_with_state_legislative_districts(client):
    """Test real API call with state legislative district fields."""
    # Test address
    address = "1600 Pennsylvania Ave NW, Washington, DC"

    # Request additional fields
    response = client.geocode(
        address,
        fields=["stateleg", "stateleg-next"]
    )

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify fields data
    fields = result.fields
    assert fields is not None

    # Check state legislative districts
    if fields.state_legislative_districts:
        district = fields.state_legislative_districts[0]
        assert district.name is not None
        assert isinstance(district.district_number, int)
        assert district.chamber in ["house", "senate"]
        if district.ocd_id:
            assert isinstance(district.ocd_id, str)
        if district.proportion:
            assert isinstance(district.proportion, float)

    # Check upcoming state legislative districts
    if fields.state_legislative_districts_next:
        district = fields.state_legislative_districts_next[0]
        assert district.name is not None
        assert isinstance(district.district_number, int)
        assert district.chamber in ["house", "senate"]
        if district.ocd_id:
            assert isinstance(district.ocd_id, str)
        if district.proportion:
            assert isinstance(district.proportion, float)


def test_integration_with_school_districts(client):
    """Test real API call with school district fields."""
    # Test address
    address = "1600 Pennsylvania Ave NW, Washington, DC"

    # Request additional fields
    response = client.geocode(
        address,
        fields=["school"]
    )

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify fields data
    fields = result.fields
    assert fields is not None

    # Check school districts
    if fields.school_districts:
        district = fields.school_districts[0]
        assert district.name is not None
        if district.district_number:
            assert isinstance(district.district_number, str)
        if district.lea_id:
            assert isinstance(district.lea_id, str)
        if district.nces_id:
            assert isinstance(district.nces_id, str)