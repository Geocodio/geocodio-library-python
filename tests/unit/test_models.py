import pytest

from geocodio.models import (
    AddressComponents,
    CensusData,
    CongressionalDistrict,
    Demographics,
    Economics,
    Families,
    FederalRiding,
    FFIECData,
    GeocodingResponse,
    GeocodingResult,
    GeocodioFields,
    Housing,
    Location,
    RateLimit,
    SchoolDistrict,
    Social,
    StateLegislativeDistrict,
    StatisticsCanadaData,
    Timezone,
    UKLegislativeDistrict,
    ZIP4Data,
)


def test_has_extras_mixin():
    """Test the _HasExtras mixin functionality."""
    # Test with AddressComponents as an example
    data = {
        "number": "1109",
        "street": "Highland",
        "suffix": "St",
        "city": "Arlington",
        "state_province": "VA",
        "postal_code": "22201",
        "extra_field": "extra value",
        "another_extra": 123,
    }

    ac = AddressComponents.from_api(data)

    # Test get_extra with default value
    assert ac.get_extra("nonexistent", "default") == "default"

    # Test get_extra with existing value
    assert ac.get_extra("extra_field") == "extra value"
    assert ac.get_extra("another_extra") == 123

    # Test attribute access for extras
    assert ac.extra_field == "extra value"
    assert ac.another_extra == 123

    # Test attribute error for non-existent fields
    with pytest.raises(AttributeError):
        _ = ac.nonexistent_field


def test_address_components_extras():
    # Test that extra fields are stored in extras
    data = {
        "number": "1109",
        "street": "Highland",
        "suffix": "St",
        "city": "Arlington",
        "state_province": "VA",
        "postal_code": "22201",
        "extra_field": "extra value",
        "another_extra": 123,
    }

    ac = AddressComponents.from_api(data)

    assert ac.number == "1109"
    assert ac.street == "Highland"
    assert ac.suffix == "St"
    assert ac.city == "Arlington"
    assert ac.state_province == "VA"
    assert ac.postal_code == "22201"


def test_timezone_extras():
    # Test that extra fields are stored in extras
    data = {
        "name": "America/New_York",
        "utc_offset": -5,
        "observes_dst": True,
        "extra_field": "extra value",
    }

    tz = Timezone.from_api(data)

    assert tz.name == "America/New_York"
    assert tz.utc_offset == -5
    assert tz.observes_dst is True


def test_geocoding_response_empty_results():
    # Test GeocodingResponse with empty results list
    response = GeocodingResponse(results=[])

    assert len(response.results) == 0


def test_geocoding_result_without_fields():
    # Test GeocodingResult without optional fields
    result = GeocodingResult(
        address_components=AddressComponents.from_api(
            {
                "number": "1109",
                "street": "Highland",
                "suffix": "St",
                "city": "Arlington",
                "state_province": "VA",
            }
        ),
        formatted_address="1109 Highland St, Arlington, VA",
        location=Location(lat=38.886672, lng=-77.094735),
        accuracy=1.0,
        accuracy_type="rooftop",
        source="Arlington",
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
        "extra_field": "extra value",
    }

    district = StateLegislativeDistrict.from_api(data)

    assert district.name == "Virginia House District 8"
    assert district.district_number == 8
    assert district.chamber == "house"
    assert district.ocd_id == "ocd-division/country:us/state:va/sldl:8"
    assert district.proportion == 1.0


def test_school_district_extras():
    # Test that extra fields are stored in extras
    data = {
        "name": "Arlington Public Schools",
        "district_number": "001",
        "lea_id": "5100000",
        "nces_id": "5100000",
        "extra_field": "extra value",
    }

    district = SchoolDistrict.from_api(data)

    assert district.name == "Arlington Public Schools"
    assert district.district_number == "001"
    assert district.lea_id == "5100000"
    assert district.nces_id == "5100000"


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
        "extra_field": "extra value",
    }

    census = CensusData.from_api(data)

    assert census.block == "1000"
    assert census.blockgroup == "1"
    assert census.tract == "000100"
    assert census.county_fips == "51013"
    assert census.state_fips == "51"
    assert census.msa_code == "47900"
    assert census.csa_code == "548"


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
        "extra_field": "extra value",
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


def test_economics_extras():
    # Test that extra fields are stored in extras
    data = {
        "median_household_income": 75000,
        "mean_household_income": 85000,
        "per_capita_income": 35000,
        "poverty_rate": 10.5,
        "unemployment_rate": 5.2,
        "extra_field": "extra value",
    }

    economics = Economics.from_api(data)

    assert economics.median_household_income == 75000
    assert economics.mean_household_income == 85000
    assert economics.per_capita_income == 35000
    assert economics.poverty_rate == 10.5
    assert economics.unemployment_rate == 5.2


def test_families_extras():
    # Test that extra fields are stored in extras
    data = {
        "total_households": 1000,
        "family_households": 600,
        "nonfamily_households": 400,
        "married_couple_households": 400,
        "single_male_households": 100,
        "single_female_households": 100,
        "average_household_size": 2.5,
        "extra_field": "extra value",
    }

    families = Families.from_api(data)

    assert families.total_households == 1000
    assert families.family_households == 600
    assert families.nonfamily_households == 400
    assert families.married_couple_households == 400
    assert families.single_male_households == 100
    assert families.single_female_households == 100
    assert families.average_household_size == 2.5


def test_housing_extras():
    # Test that extra fields are stored in extras
    data = {
        "total_housing_units": 1000,
        "occupied_housing_units": 800,
        "vacant_housing_units": 200,
        "owner_occupied_units": 500,
        "renter_occupied_units": 300,
        "median_home_value": 350000,
        "median_rent": 1500,
        "extra_field": "extra value",
    }

    housing = Housing.from_api(data)

    assert housing.total_housing_units == 1000
    assert housing.occupied_housing_units == 800
    assert housing.vacant_housing_units == 200
    assert housing.owner_occupied_units == 500
    assert housing.renter_occupied_units == 300
    assert housing.median_home_value == 350000
    assert housing.median_rent == 1500


def test_social_extras():
    # Test that extra fields are stored in extras
    data = {
        "high_school_graduate_or_higher": 800,
        "bachelors_degree_or_higher": 400,
        "graduate_degree_or_higher": 200,
        "veterans": 100,
        "veterans_percentage": 10.5,
        "extra_field": "extra value",
    }

    social = Social.from_api(data)

    assert social.high_school_graduate_or_higher == 800
    assert social.bachelors_degree_or_higher == 400
    assert social.graduate_degree_or_higher == 200
    assert social.veterans == 100
    assert social.veterans_percentage == 10.5


def test_zip4_data():
    """Test ZIP+4 data model."""
    data = {
        "zip4": "1234",
        "delivery_point": "01",
        "carrier_route": "C001",
        "extra_field": "extra value",
    }
    zip4 = ZIP4Data.from_api(data)
    assert zip4.zip4 == "1234"
    assert zip4.delivery_point == "01"
    assert zip4.carrier_route == "C001"
    assert zip4.get_extra("extra_field") == "extra value"


def test_canadian_riding():
    """Test Canadian riding data model."""
    data = {
        "code": "35052",
        "name_english": "Toronto Centre",
        "name_french": "Toronto-Centre",
        "ocd_id": "ocd-division/country:ca/ed:35052",
        "year": 2021,
        "source": "Elections Canada",
        "extra_field": "extra value",
    }
    riding = FederalRiding.from_api(data)
    assert riding.code == "35052"
    assert riding.name_english == "Toronto Centre"
    assert riding.name_french == "Toronto-Centre"
    assert riding.ocd_id == "ocd-division/country:ca/ed:35052"
    assert riding.year == 2021
    assert riding.source == "Elections Canada"
    assert riding.get_extra("extra_field") == "extra value"


def test_uk_legislative_district():
    """Test UK legislative district data model."""
    data = {
        "district_type": "westminster_constituency",
        "gss_code": "E14001172",
        "ocd_id": "ocd-division/country:gb/part:eng/region:uki/ed:cities_of_london_and_westminster",
        "name": "Cities of London and Westminster",
        "is_upcoming_district": False,
        "source": "Office for National Statistics",
        "extra_field": "extra value",
    }
    district = UKLegislativeDistrict.from_api(data)
    assert district.district_type == "westminster_constituency"
    assert district.gss_code == "E14001172"
    assert district.name == "Cities of London and Westminster"
    assert district.is_upcoming_district is False
    assert district.source == "Office for National Statistics"
    assert district.get_extra("extra_field") == "extra value"


def test_statistics_canada_data():
    """Test Statistics Canada data model."""
    data = {
        "division": {"name": "Division 1"},
        "consolidated_subdivision": {"name": "Subdivision 1"},
        "subdivision": {"name": "Subdivision A"},
        "economic_region": "Region 1",
        "statistical_area": {"name": "Area 1"},
        "cma_ca": {"name": "CMA 1"},
        "tract": "0001.00",
        "population_centre": {"name": "Centre 1"},
        "dissemination_area": {"code": "12345"},
        "dissemination_block": {"code": "123456"},
        "census_year": 2021,
        "designated_place": {"name": "Place 1"},
        "extra_field": "extra value",
    }
    statcan = StatisticsCanadaData.from_api(data)
    assert statcan.division == {"name": "Division 1"}
    assert statcan.consolidated_subdivision == {"name": "Subdivision 1"}
    assert statcan.subdivision == {"name": "Subdivision A"}
    assert statcan.economic_region == "Region 1"
    assert statcan.statistical_area == {"name": "Area 1"}
    assert statcan.cma_ca == {"name": "CMA 1"}
    assert statcan.tract == "0001.00"
    assert statcan.population_centre == {"name": "Centre 1"}
    assert statcan.dissemination_area == {"code": "12345"}
    assert statcan.dissemination_block == {"code": "123456"}
    assert statcan.census_year == 2021
    assert statcan.designated_place == {"name": "Place 1"}
    assert statcan.get_extra("extra_field") == "extra value"


def test_ffiec_data():
    """Test FFIEC data model."""
    data = {"extra_field": "extra value"}
    ffiec = FFIECData.from_api(data)
    assert ffiec.get_extra("extra_field") == "extra value"


def test_census_accessors():
    """fields.census exposes the census append like every other append."""
    fields = GeocodioFields(
        _census={
            "census2020": CensusData.from_api(
                {"census_year": 2020, "full_fips": "500110960100000"}
            ),
            "census2023": CensusData.from_api(
                {"census_year": 2023, "full_fips": "500110960102004"}
            ),
        }
    )

    # The public accessor returns the most recent vintage
    assert fields.census is not None
    assert fields.census.census_year == 2023
    assert fields.census.full_fips == "500110960102004"

    # A specific vintage can be requested in any form
    assert fields.get_census(2020).census_year == 2020
    assert fields.get_census("2020").census_year == 2020
    assert fields.get_census("census2020").census_year == 2020
    assert fields.get_census(1999) is None

    # Supporting accessors
    assert fields.census_years == [2020, 2023]
    assert sorted(fields.census_data) == ["census2020", "census2023"]

    # Backward compatibility: dynamic attributes and the private dict
    assert fields.census2023.full_fips == "500110960102004"
    assert fields._census["census2023"].full_fips == "500110960102004"


def test_census_accessors_without_census_data():
    """fields.census is None when no census field was requested."""
    fields = GeocodioFields()

    assert fields.census is None
    assert fields.get_census() is None
    assert fields.get_census(2023) is None
    assert fields.census_years == []
    assert fields.census_data == {}


def test_rate_limit_from_headers():
    """Rate limit state is parsed from the X-RateLimit-* headers."""
    rate_limit = RateLimit.from_headers(
        {
            "Content-Type": "application/json",
            "X-RateLimit-Limit": "1000",
            "X-RateLimit-Remaining": "999",
            "X-RateLimit-Period": "60",
        }
    )

    assert rate_limit is not None
    assert rate_limit.limit == 1000
    assert rate_limit.remaining == 999
    assert rate_limit.period == 60
    assert rate_limit.reset is None
    assert rate_limit.headers == {
        "x-ratelimit-limit": "1000",
        "x-ratelimit-remaining": "999",
        "x-ratelimit-period": "60",
    }


def test_rate_limit_from_headers_without_rate_limit_headers():
    """No rate limit headers means no RateLimit object."""
    assert RateLimit.from_headers({"Content-Type": "application/json"}) is None
    assert RateLimit.from_headers(None) is None


def test_rate_limit_from_headers_with_unparseable_values():
    """Non-numeric header values are ignored rather than raising."""
    rate_limit = RateLimit.from_headers(
        {"X-RateLimit-Limit": "unlimited", "X-RateLimit-Remaining": "5"}
    )

    assert rate_limit is not None
    assert rate_limit.limit is None
    assert rate_limit.remaining == 5


def test_geocoding_result_raw_defaults():
    """raw defaults to an empty dict and to_dict() returns a copy."""
    result = GeocodingResult(
        address_components=AddressComponents.from_api({}),
        formatted_address="",
        location=None,
        accuracy=0.0,
        accuracy_type="",
        source="",
        raw={"formatted_address": "", "match_type": None},
    )

    assert result.to_dict() == {"formatted_address": "", "match_type": None}
    result.to_dict()["formatted_address"] = "mutated"
    assert result.raw["formatted_address"] == ""

    response = GeocodingResponse()
    assert response.raw == {}
    assert response.to_dict() == {}
    assert response.rate_limit is None
