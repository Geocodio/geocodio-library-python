"""
End-to-end tests that make real API calls to Geocodio.
These tests require a valid GEOCODIO_API_KEY environment variable.
"""

import os
import pytest
from geocodio import Geocodio
from geocodio.exceptions import GeocodioError


@pytest.fixture
def client():
    """Create a client using the GEOCODIO_API_KEY environment variable."""
    api_key = os.getenv("GEOCODIO_API_KEY")
    if not api_key:
        pytest.skip("GEOCODIO_API_KEY environment variable not set")
    return Geocodio(api_key)


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


def test_integration_with_census2023(client):
    """Test real API call with census2023 field."""
    # Test address
    address = "1600 Pennsylvania Ave NW, Washington, DC"

    # Request additional fields
    response = client.geocode(
        address,
        fields=["census2023"]
    )

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify fields data
    fields = result.fields
    assert fields is not None

    # Check census2023 data
    if fields.census2023:
        assert fields.census2023.tract is not None
        assert fields.census2023.block is not None
        assert fields.census2023.county_fips is not None
        assert fields.census2023.state_fips is not None
        if fields.census2023.msa_code:
            assert isinstance(fields.census2023.msa_code, str)
        if fields.census2023.csa_code:
            assert isinstance(fields.census2023.csa_code, str)


def test_integration_with_demographics(client):
    """Test real API call with demographics field."""
    # Test address
    address = "1600 Pennsylvania Ave NW, Washington, DC"

    # Request additional fields
    response = client.geocode(
        address,
        fields=["acs-demographics"]
    )

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify fields data
    fields = result.fields
    assert fields is not None

    # Check demographics data
    if fields.demographics:
        if fields.demographics.total_population is not None:
            assert isinstance(fields.demographics.total_population, int)
        if fields.demographics.male_population is not None:
            assert isinstance(fields.demographics.male_population, int)
        if fields.demographics.female_population is not None:
            assert isinstance(fields.demographics.female_population, int)
        if fields.demographics.median_age is not None:
            assert isinstance(fields.demographics.median_age, float)
        if fields.demographics.white_population is not None:
            assert isinstance(fields.demographics.white_population, int)
        if fields.demographics.black_population is not None:
            assert isinstance(fields.demographics.black_population, int)
        if fields.demographics.asian_population is not None:
            assert isinstance(fields.demographics.asian_population, int)
        if fields.demographics.hispanic_population is not None:
            assert isinstance(fields.demographics.hispanic_population, int)


def test_integration_with_economics(client):
    """Test real API call with economics field."""
    # Test address
    address = "1600 Pennsylvania Ave NW, Washington, DC"

    # Request additional fields
    response = client.geocode(
        address,
        fields=["acs-economics"]
    )

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify fields data
    fields = result.fields
    assert fields is not None

    # Check economics data
    if fields.economics:
        if fields.economics.median_household_income is not None:
            assert isinstance(fields.economics.median_household_income, int)
        if fields.economics.mean_household_income is not None:
            assert isinstance(fields.economics.mean_household_income, int)
        if fields.economics.per_capita_income is not None:
            assert isinstance(fields.economics.per_capita_income, int)
        if fields.economics.poverty_rate is not None:
            assert isinstance(fields.economics.poverty_rate, float)
        if fields.economics.unemployment_rate is not None:
            assert isinstance(fields.economics.unemployment_rate, float)


def test_integration_with_families(client):
    """Test real API call with families field."""
    # Test address
    address = "1600 Pennsylvania Ave NW, Washington, DC"

    # Request additional fields
    response = client.geocode(
        address,
        fields=["acs-families"]
    )

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify fields data
    fields = result.fields
    assert fields is not None

    # Check families data
    if fields.families:
        if fields.families.total_households is not None:
            assert isinstance(fields.families.total_households, int)
        if fields.families.family_households is not None:
            assert isinstance(fields.families.family_households, int)
        if fields.families.nonfamily_households is not None:
            assert isinstance(fields.families.nonfamily_households, int)
        if fields.families.married_couple_households is not None:
            assert isinstance(fields.families.married_couple_households, int)
        if fields.families.single_male_households is not None:
            assert isinstance(fields.families.single_male_households, int)
        if fields.families.single_female_households is not None:
            assert isinstance(fields.families.single_female_households, int)
        if fields.families.average_household_size is not None:
            assert isinstance(fields.families.average_household_size, float)


def test_integration_with_housing(client):
    """Test real API call with housing field."""
    # Test address
    address = "1600 Pennsylvania Ave NW, Washington, DC"

    # Request additional fields
    response = client.geocode(
        address,
        fields=["acs-housing"]
    )

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify fields data
    fields = result.fields
    assert fields is not None

    # Check housing data
    if fields.housing:
        if fields.housing.total_housing_units is not None:
            assert isinstance(fields.housing.total_housing_units, int)
        if fields.housing.occupied_housing_units is not None:
            assert isinstance(fields.housing.occupied_housing_units, int)
        if fields.housing.vacant_housing_units is not None:
            assert isinstance(fields.housing.vacant_housing_units, int)
        if fields.housing.owner_occupied_units is not None:
            assert isinstance(fields.housing.owner_occupied_units, int)
        if fields.housing.renter_occupied_units is not None:
            assert isinstance(fields.housing.renter_occupied_units, int)
        if fields.housing.median_home_value is not None:
            assert isinstance(fields.housing.median_home_value, int)
        if fields.housing.median_rent is not None:
            assert isinstance(fields.housing.median_rent, int)


def test_integration_with_zip4(client):
    """Test real API call with ZIP+4 field."""
    # Test address
    address = "1600 Pennsylvania Ave NW, Washington, DC"

    # Request additional fields
    response = client.geocode(
        address,
        fields=["zip4"]
    )

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify fields data
    fields = result.fields
    assert fields is not None

    # Check ZIP+4 data
    if fields.zip4:
        assert fields.zip4.zip4 is not None
        assert fields.zip4.delivery_point is not None
        assert fields.zip4.carrier_route is not None


def test_integration_with_ffiec(client):
    """Test real API call with FFIEC field (Beta)."""
    # Test address
    address = "1600 Pennsylvania Ave NW, Washington, DC"

    # Request additional fields
    response = client.geocode(
        address,
        fields=["ffiec"]
    )

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify fields data
    fields = result.fields
    assert fields is not None

    # Check FFIEC data (Beta feature, so we just verify it exists)
    if fields.ffiec:
        assert isinstance(fields.ffiec.extras, dict)


def test_integration_with_canadian_fields(client):
    """Test real API call with Canadian fields."""
    # Test forward geocoding with Canadian address using q parameter
    address = "301 Front Street West, Toronto, ON M5V 2T6, Canada"
    response = client.geocode(
        address,
        fields=["provriding"]  # Test with just provriding first
    )

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify fields data
    fields = result.fields
    assert fields is not None

    # Check provriding (Provincial Electoral District)
    if fields.provriding:
        assert fields.provriding.name_english is not None
        assert fields.provriding.name_french is not None
        assert fields.provriding.ocd_id is not None
        assert isinstance(fields.provriding.is_upcoming_district, bool)
        assert fields.provriding.source is not None

    # Test forward geocoding with structured address parameters
    structured_address = {
        "street": "301 Front Street West",
        "city": "Toronto",
        "state": "ON",
        "postal_code": "M5V 2T6",
        "country": "Canada"
    }
    response = client.geocode(
        structured_address,
        fields=["provriding"]
    )

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify fields data
    fields = result.fields
    assert fields is not None

    # Check provriding (Provincial Electoral District)
    if fields.provriding:
        assert fields.provriding.name_english is not None
        assert fields.provriding.name_french is not None
        assert fields.provriding.ocd_id is not None
        assert isinstance(fields.provriding.is_upcoming_district, bool)
        assert fields.provriding.source is not None

    # Test reverse geocoding with Canadian coordinates (CN Tower coordinates)
    response = client.reverse(
        (43.6426, -79.3871),
        fields=["provriding"]
    )

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify fields data
    fields = result.fields
    assert fields is not None

    # Check provriding (Provincial Electoral District)
    if fields.provriding:
        assert fields.provriding.name_english is not None
        assert fields.provriding.name_french is not None
        assert fields.provriding.ocd_id is not None
        assert isinstance(fields.provriding.is_upcoming_district, bool)
        assert fields.provriding.source is not None

    # Now test with all Canadian fields using country parameter
    response = client.geocode(
        "301 Front Street West, Toronto, ON M5V 2T6",
        fields=["riding", "provriding", "provriding-next", "statcan"],
        country="CA"  # Use country parameter instead of including in address
    )

    # Verify fields data for all Canadian fields
    fields = response.results[0].fields
    assert fields is not None

    # Check riding (Federal Electoral District)
    if fields.riding:
        assert fields.riding.code is not None
        assert fields.riding.name_english is not None
        assert fields.riding.name_french is not None
        assert fields.riding.ocd_id is not None
        assert isinstance(fields.riding.year, int)
        assert fields.riding.source is not None

    # Check provriding (Provincial Electoral District)
    if fields.provriding:
        assert fields.provriding.name_english is not None
        assert fields.provriding.name_french is not None
        assert fields.provriding.ocd_id is not None
        assert isinstance(fields.provriding.is_upcoming_district, bool)
        assert fields.provriding.source is not None

    # Check provriding-next (Upcoming Provincial Districts)
    if fields.provriding_next:
        assert fields.provriding_next.name_english is not None
        assert fields.provriding_next.name_french is not None
        assert fields.provriding_next.ocd_id is not None
        assert isinstance(fields.provriding_next.is_upcoming_district, bool)
        assert fields.provriding_next.source is not None

    # Check Statistics Canada data
    if fields.statcan:
        assert fields.statcan.division is not None
        assert fields.statcan.consolidated_subdivision is not None
        assert fields.statcan.subdivision is not None
        assert fields.statcan.economic_region is not None
        assert fields.statcan.statistical_area is not None
        assert fields.statcan.cma_ca is not None
        assert fields.statcan.tract is not None
        assert fields.statcan.population_centre is not None
        assert fields.statcan.dissemination_area is not None
        assert fields.statcan.dissemination_block is not None
        assert isinstance(fields.statcan.census_year, int)


def test_integration_with_census_years(client):
    """Test real API call with various census years."""
    # Test address
    address = "1600 Pennsylvania Ave NW, Washington, DC"

    # Request additional fields for various census years
    response = client.geocode(
        address,
        fields=["census2000", "census2010", "census2020", "census2023"]
    )

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify fields data
    fields = result.fields
    assert fields is not None

    # Check census data for each year
    for year in [2000, 2010, 2020, 2023]:
        census_data = getattr(fields, f"census{year}")
        if census_data:
            assert census_data.tract is not None
            assert census_data.block is not None
            assert census_data.county_fips is not None
            assert census_data.state_fips is not None


def test_integration_with_congressional_district_variants(client):
    """Test real API call with specific congressional district variants."""
    # Test address
    address = "1600 Pennsylvania Ave NW, Washington, DC"

    # Request additional fields for various congress numbers
    response = client.geocode(
        address,
        fields=["cd113", "cd114", "cd115", "cd116", "cd117", "cd118", "cd119"]
    )

    # Verify response structure
    assert response is not None
    assert len(response.results) > 0
    result = response.results[0]

    # Verify fields data
    fields = result.fields
    assert fields is not None

    # Check congressional districts
    if fields.congressional_districts:
        for district in fields.congressional_districts:
            assert district.name is not None
            assert isinstance(district.district_number, int)
            assert district.congress_number is not None
            if district.ocd_id:
                assert isinstance(district.ocd_id, str)