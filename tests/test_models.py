import pytest
from geocodio.models import (
    AddressComponents, Timezone, CongressionalDistrict,
    GeocodioFields, GeocodingResult, GeocodingResponse, Location, StateLegislativeDistrict, SchoolDistrict, CensusData, Demographics, Economics
)


def test_address_components_extras():
    # Test that extra fields are stored in extras
    data = {
        "number": "1109",
        "street": "Highland",
        "suffix": "St",
        "city": "Arlington",
        "state": "VA",
        "zip": "22201",
        "extra_field": "extra value",
        "another_extra": 123
    }

    ac = AddressComponents.from_api(data)

    assert ac.number == "1109"
    assert ac.street == "Highland"
    assert ac.suffix == "St"
    assert ac.city == "Arlington"
    assert ac.state == "VA"
    assert ac.zip == "22201"
    assert ac.get_extra("extra_field") == "extra value"
    assert ac.get_extra("another_extra") == 123
    assert ac.get_extra("nonexistent", "default") == "default"


def test_timezone_extras():
    # Test that extra fields are stored in extras
    data = {
        "name": "America/New_York",
        "utc_offset": -5,
        "observes_dst": True,
        "extra_field": "extra value"
    }

    tz = Timezone.from_api(data)

    assert tz.name == "America/New_York"
    assert tz.utc_offset == -5
    assert tz.observes_dst is True
    assert tz.get_extra("extra_field") == "extra value"
    assert tz.get_extra("nonexistent", "default") == "default"


def test_has_extras_attribute_error():
    # Test that accessing non-existent attributes raises AttributeError
    ac = AddressComponents.from_api({"number": "1109"})

    with pytest.raises(AttributeError):
        _ = ac.nonexistent_field


def test_geocoding_response_empty_results():
    # Test GeocodingResponse with empty results list
    response = GeocodingResponse(
        input={"address": "1109 N Highland St, Arlington, VA"},
        results=[]
    )

    assert len(response.results) == 0
    assert response.input["address"] == "1109 N Highland St, Arlington, VA"


def test_geocoding_result_without_fields():
    # Test GeocodingResult without optional fields
    result = GeocodingResult(
        address_components=AddressComponents.from_api({
            "number": "1109",
            "street": "Highland",
            "suffix": "St",
            "city": "Arlington",
            "state": "VA"
        }),
        formatted_address="1109 Highland St, Arlington, VA",
        location=Location(lat=38.886672, lng=-77.094735),
        accuracy=1.0,
        accuracy_type="rooftop",
        source="Arlington"
    )

    assert result.fields is None
    assert result.address_components.city == "Arlington"
    assert result.location.lat == 38.886672
    assert result.location.lng == -77.094735


def test_state_legislative_district_extras():
    # Test that extra fields are stored in extras
    data = {
        "name": "Virginia House District 8",
        "district_number": 8,
        "chamber": "house",
        "ocd_id": "ocd-division/country:us/state:va/sldl:8",
        "proportion": 1.0,
        "extra_field": "extra value"
    }

    district = StateLegislativeDistrict.from_api(data)

    assert district.name == "Virginia House District 8"
    assert district.district_number == 8
    assert district.chamber == "house"
    assert district.ocd_id == "ocd-division/country:us/state:va/sldl:8"
    assert district.proportion == 1.0
    assert district.get_extra("extra_field") == "extra value"
    assert district.get_extra("nonexistent", "default") == "default"


def test_school_district_extras():
    # Test that extra fields are stored in extras
    data = {
        "name": "Arlington Public Schools",
        "district_number": "001",
        "lea_id": "5100000",
        "nces_id": "5100000",
        "extra_field": "extra value"
    }

    district = SchoolDistrict.from_api(data)

    assert district.name == "Arlington Public Schools"
    assert district.district_number == "001"
    assert district.lea_id == "5100000"
    assert district.nces_id == "5100000"
    assert district.get_extra("extra_field") == "extra value"
    assert district.get_extra("nonexistent", "default") == "default"


def test_census_data_extras():
    # Test that extra fields are stored in extras
    data = {
        "block": "1000",
        "blockgroup": "1",
        "tract": "000100",
        "county_fips": "51013",
        "state_fips": "51",
        "msa_code": "47900",
        "csa_code": "548",
        "extra_field": "extra value"
    }

    census = CensusData.from_api(data)

    assert census.block == "1000"
    assert census.blockgroup == "1"
    assert census.tract == "000100"
    assert census.county_fips == "51013"
    assert census.state_fips == "51"
    assert census.msa_code == "47900"
    assert census.csa_code == "548"
    assert census.get_extra("extra_field") == "extra value"
    assert census.get_extra("nonexistent", "default") == "default"


def test_demographics_extras():
    # Test that extra fields are stored in extras
    data = {
        "total_population": 1000,
        "male_population": 500,
        "female_population": 500,
        "median_age": 35.5,
        "white_population": 600,
        "black_population": 200,
        "asian_population": 100,
        "hispanic_population": 100,
        "extra_field": "extra value"
    }

    demographics = Demographics.from_api(data)

    assert demographics.total_population == 1000
    assert demographics.male_population == 500
    assert demographics.female_population == 500
    assert demographics.median_age == 35.5
    assert demographics.white_population == 600
    assert demographics.black_population == 200
    assert demographics.asian_population == 100
    assert demographics.hispanic_population == 100
    assert demographics.get_extra("extra_field") == "extra value"
    assert demographics.get_extra("nonexistent", "default") == "default"


def test_economics_extras():
    # Test that extra fields are stored in extras
    data = {
        "median_household_income": 75000,
        "mean_household_income": 85000,
        "per_capita_income": 35000,
        "poverty_rate": 10.5,
        "unemployment_rate": 5.2,
        "extra_field": "extra value"
    }

    economics = Economics.from_api(data)

    assert economics.median_household_income == 75000
    assert economics.mean_household_income == 85000
    assert economics.per_capita_income == 35000
    assert economics.poverty_rate == 10.5
    assert economics.unemployment_rate == 5.2
    assert economics.get_extra("extra_field") == "extra value"
    assert economics.get_extra("nonexistent", "default") == "default"