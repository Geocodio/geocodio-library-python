import pytest
from geocodio.models import (
    AddressComponents, Timezone, CongressionalDistrict,
    GeocodioFields, GeocodingResult, GeocodingResponse, Location
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
    assert ac.extras["extra_field"] == "extra value"
    assert ac.extras["another_extra"] == 123
    assert ac.get_extra("extra_field") == "extra value"
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
    assert tz.extras["extra_field"] == "extra value"
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