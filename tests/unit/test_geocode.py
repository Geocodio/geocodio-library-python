import json
from pathlib import Path

import httpx2 as httpx

from geocodio.models import AddressComponents, GeocodingResponse


def sample_payload() -> dict:
    return {
        "results": [
            {
                "address_components": {
                    "number": "1109",
                    "predirectional": "N",
                    "street": "Highland",
                    "suffix": "St",
                    "formatted_street": "N Highland St",
                    "city": "Arlington",
                    "county": "Arlington County",
                    "state_province": "VA",
                    "postal_code": "22201",
                    "country": "US",
                },
                "formatted_address": "1109 N Highland St, Arlington, VA 22201",
                "location": {"lat": 38.886672, "lng": -77.094735},
                "accuracy": 1,
                "accuracy_type": "rooftop",
                "source": "Arlington",
                "fields": {
                    "timezone": {
                        "name": "America/New_York",
                        "utc_offset": -5,
                        "observes_dst": True,
                    }
                },
                "stable_address_key": "abc123stablekey",
            }
        ],
    }


def test_geocode_single(client, httpx_mock):
    # Arrange: stub the API call with a callback to inspect the request
    def response_callback(request):
        return httpx.Response(200, json=sample_payload())

    httpx_mock.add_callback(
        callback=response_callback,
        url=httpx.URL(
            "https://api.test/v2/geocode",
            params={"q": "1109 N Highland St, Arlington, VA"},
        ),
        match_headers={"Authorization": "Bearer TEST_KEY"},
    )

    # Act
    resp: GeocodingResponse = client.geocode("1109 N Highland St, Arlington, VA")

    # Assert
    assert resp.results[0].formatted_address.endswith("VA 22201")
    ac: AddressComponents = resp.results[0].address_components
    assert ac.city == "Arlington"
    assert ac.predirectional == "N"
    assert ac.street == "Highland"
    assert ac.suffix == "St"
    # timezone
    tz = resp.results[0].fields.timezone
    assert tz.name == "America/New_York"
    assert tz.observes_dst is True
    # stable address key (v2 returns this on every result)
    assert resp.results[0].stable_address_key == "abc123stablekey"


def test_geocode_batch(client, httpx_mock):
    # Arrange: stub the API call
    addresses = ["3730 N Clark St, Chicago, IL", "638 E 13th Ave, Denver, CO"]

    def batch_response_callback(request):
        assert request.method == "POST"  # Should use POST for batch
        assert json.loads(request.content) == addresses  # Check payload is a list
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "query": "3730 N Clark St, Chicago, IL",
                        "response": {
                            "results": [
                                {
                                    "address_components": {
                                        "number": "3730",
                                        "predirectional": "N",
                                        "street": "Clark",
                                        "suffix": "St",
                                        "city": "Chicago",
                                        "county": "Cook County",
                                        "state_province": "IL",
                                        "postal_code": "60613",
                                        "country": "US",
                                    },
                                    "formatted_address": "3730 N Clark St, Chicago, IL 60613",
                                    "location": {"lat": 41.94987, "lng": -87.65893},
                                    "accuracy": 1,
                                    "accuracy_type": "rooftop",
                                    "source": "Cook",
                                }
                            ]
                        },
                    },
                    {
                        "query": "638 E 13th Ave, Denver, CO",
                        "response": {
                            "results": [
                                {
                                    "address_components": {
                                        "number": "638",
                                        "predirectional": "E",
                                        "street": "13th",
                                        "suffix": "Ave",
                                        "city": "Denver",
                                        "county": "Denver County",
                                        "state_province": "CO",
                                        "postal_code": "80203",
                                        "country": "US",
                                    },
                                    "formatted_address": "638 E 13th Ave, Denver, CO 80203",
                                    "location": {"lat": 39.736792, "lng": -104.978914},
                                    "accuracy": 1,
                                    "accuracy_type": "rooftop",
                                    "source": "Denver (City of Denver Open Data Catalog CC BY 3.0)",
                                }
                            ]
                        },
                    },
                ]
            },
        )

    httpx_mock.add_callback(
        callback=batch_response_callback,
        url=httpx.URL("https://api.test/v2/geocode"),
        match_headers={"Authorization": "Bearer TEST_KEY"},
    )

    # Act
    resp = client.geocode(addresses)

    # Assert
    assert len(resp.results) == 2
    assert resp.results[0].formatted_address == "3730 N Clark St, Chicago, IL 60613"
    assert resp.results[1].formatted_address == "638 E 13th Ave, Denver, CO 80203"
    assert resp.results[0].location.lat == 41.94987
    assert resp.results[1].location.lat == 39.736792


def test_geocode_structured_address(client, httpx_mock):
    # Arrange: stub the API call
    structured_address = {
        "street": "1109 N Highland St",
        "city": "Arlington",
        "state_province": "VA",
    }

    def response_callback(request):
        assert request.method == "GET"
        assert request.url.params["street"] == "1109 N Highland St"
        assert request.url.params["city"] == "Arlington"
        assert request.url.params["state_province"] == "VA"
        return httpx.Response(200, json=sample_payload())

    httpx_mock.add_callback(
        callback=response_callback,
        url=httpx.URL(
            "https://api.test/v2/geocode",
            params={
                "street": "1109 N Highland St",
                "city": "Arlington",
                "state_province": "VA",
            },
        ),
        match_headers={"Authorization": "Bearer TEST_KEY"},
    )

    # Act
    resp = client.geocode(structured_address)

    # Assert
    assert len(resp.results) == 1
    assert resp.results[0].formatted_address.endswith("VA 22201")
    assert resp.results[0].address_components.city == "Arlington"
    assert resp.results[0].address_components.state_province == "VA"


def test_geocode_with_fields(client, httpx_mock):
    # Arrange: stub the API call with timezone and congressional districts
    def response_callback(request):
        assert request.method == "GET"
        assert request.url.params["fields"] == "timezone,cd"
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "address_components": {
                            "number": "1109",
                            "street": "Highland",
                            "suffix": "St",
                            "city": "Arlington",
                            "state_province": "VA",
                            "postal_code": "22201",
                        },
                        "formatted_address": "1109 Highland St, Arlington, VA 22201",
                        "location": {"lat": 38.886672, "lng": -77.094735},
                        "accuracy": 1,
                        "accuracy_type": "rooftop",
                        "source": "Arlington",
                        "fields": {
                            "timezone": {
                                "name": "America/New_York",
                                "utc_offset": -5,
                                "observes_dst": True,
                            },
                            "cd": [
                                {
                                    "name": "Virginia's 8th congressional district",
                                    "district_number": 8,
                                    "congress_number": "118",
                                }
                            ],
                        },
                    }
                ]
            },
        )

    httpx_mock.add_callback(
        callback=response_callback,
        url=httpx.URL(
            "https://api.test/v2/geocode",
            params={"q": "1109 Highland St, Arlington, VA", "fields": "timezone,cd"},
        ),
        match_headers={"Authorization": "Bearer TEST_KEY"},
    )

    # Act
    resp = client.geocode("1109 Highland St, Arlington, VA", fields=["timezone", "cd"])

    # Assert
    assert len(resp.results) == 1
    assert resp.results[0].fields.timezone.name == "America/New_York"
    assert resp.results[0].fields.timezone.utc_offset == -5
    assert resp.results[0].fields.timezone.observes_dst is True
    assert len(resp.results[0].fields.congressional_districts) == 1
    assert (
        resp.results[0].fields.congressional_districts[0].name
        == "Virginia's 8th congressional district"
    )
    assert resp.results[0].fields.congressional_districts[0].district_number == 8
    assert resp.results[0].fields.congressional_districts[0].congress_number == "118"


def test_geocode_with_limit(client, httpx_mock):
    # Arrange: stub the API call
    def response_callback(request):
        assert request.method == "GET"
        assert request.url.params["limit"] == "2"
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "address_components": {
                            "number": "1109",
                            "street": "Highland",
                            "suffix": "St",
                            "city": "Arlington",
                            "state_province": "VA",
                            "postal_code": "22201",
                        },
                        "formatted_address": "1109 Highland St, Arlington, VA 22201",
                        "location": {"lat": 38.886672, "lng": -77.094735},
                        "accuracy": 1,
                        "accuracy_type": "rooftop",
                        "source": "Arlington",
                    },
                    {
                        "address_components": {
                            "number": "1111",
                            "street": "Highland",
                            "suffix": "St",
                            "city": "Arlington",
                            "state_province": "VA",
                            "postal_code": "22201",
                        },
                        "formatted_address": "1111 Highland St, Arlington, VA 22201",
                        "location": {"lat": 38.886672, "lng": -77.094735},
                        "accuracy": 1,
                        "accuracy_type": "rooftop",
                        "source": "Arlington",
                    },
                ]
            },
        )

    httpx_mock.add_callback(
        callback=response_callback,
        url=httpx.URL(
            "https://api.test/v2/geocode",
            params={"q": "1109 Highland St, Arlington, VA", "limit": "2"},
        ),
        match_headers={"Authorization": "Bearer TEST_KEY"},
    )

    # Act
    resp = client.geocode("1109 Highland St, Arlington, VA", limit=2)

    # Assert
    assert len(resp.results) == 2
    assert resp.results[0].formatted_address == "1109 Highland St, Arlington, VA 22201"
    assert resp.results[1].formatted_address == "1111 Highland St, Arlington, VA 22201"


def test_geocode_batch_with_nested_response(client, httpx_mock):
    """Test batch geocoding with the nested response structure."""
    addresses = ["3730 N Clark St, Chicago, IL", "638 E 13th Ave, Denver, CO"]

    def batch_response_callback(request):
        assert request.method == "POST"
        assert json.loads(request.content) == addresses  # Check payload is a list
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "query": "3730 N Clark St, Chicago, IL",
                        "response": {
                            "results": [
                                {
                                    "address_components": {
                                        "number": "3730",
                                        "predirectional": "N",
                                        "street": "Clark",
                                        "suffix": "St",
                                        "city": "Chicago",
                                        "county": "Cook County",
                                        "state_province": "IL",
                                        "postal_code": "60613",
                                        "country": "US",
                                    },
                                    "formatted_address": "3730 N Clark St, Chicago, IL 60613",
                                    "location": {"lat": 41.94987, "lng": -87.65893},
                                    "accuracy": 1,
                                    "accuracy_type": "rooftop",
                                    "source": "Cook",
                                }
                            ]
                        },
                    },
                    {
                        "query": "638 E 13th Ave, Denver, CO",
                        "response": {
                            "results": [
                                {
                                    "address_components": {
                                        "number": "638",
                                        "predirectional": "E",
                                        "street": "13th",
                                        "suffix": "Ave",
                                        "city": "Denver",
                                        "county": "Denver County",
                                        "state_province": "CO",
                                        "postal_code": "80203",
                                        "country": "US",
                                    },
                                    "formatted_address": "638 E 13th Ave, Denver, CO 80203",
                                    "location": {"lat": 39.736792, "lng": -104.978914},
                                    "accuracy": 1,
                                    "accuracy_type": "rooftop",
                                    "source": "Denver (City of Denver Open Data Catalog CC BY 3.0)",
                                }
                            ]
                        },
                    },
                ]
            },
        )

    httpx_mock.add_callback(
        callback=batch_response_callback,
        url=httpx.URL("https://api.test/v2/geocode"),
        match_headers={"Authorization": "Bearer TEST_KEY"},
    )

    # Act
    resp = client.geocode(addresses)

    # Assert
    assert len(resp.results) == 2
    assert resp.results[0].formatted_address == "3730 N Clark St, Chicago, IL 60613"
    assert resp.results[1].formatted_address == "638 E 13th Ave, Denver, CO 80203"
    assert resp.results[0].location.lat == 41.94987
    assert resp.results[1].location.lat == 39.736792


def test_geocode_batch_with_fields(client, httpx_mock):
    """Test batch geocoding with additional fields."""
    addresses = ["3730 N Clark St, Chicago, IL", "638 E 13th Ave, Denver, CO"]

    def batch_response_callback(request):
        assert request.method == "POST"
        assert request.url.params["fields"] == "timezone,cd"
        assert json.loads(request.content) == addresses  # Check payload is a list
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "query": "3730 N Clark St, Chicago, IL",
                        "response": {
                            "results": [
                                {
                                    "address_components": {
                                        "number": "3730",
                                        "predirectional": "N",
                                        "street": "Clark",
                                        "suffix": "St",
                                        "city": "Chicago",
                                        "county": "Cook County",
                                        "state_province": "IL",
                                        "postal_code": "60613",
                                        "country": "US",
                                    },
                                    "formatted_address": "3730 N Clark St, Chicago, IL 60613",
                                    "location": {"lat": 41.94987, "lng": -87.65893},
                                    "accuracy": 1,
                                    "accuracy_type": "rooftop",
                                    "source": "Cook",
                                    "fields": {
                                        "timezone": {
                                            "name": "America/Chicago",
                                            "utc_offset": -6,
                                            "observes_dst": True,
                                        },
                                        "cd": [
                                            {
                                                "name": "Congressional District 5",
                                                "district_number": 5,
                                                "congress_number": "119th",
                                            }
                                        ],
                                    },
                                }
                            ]
                        },
                    },
                    {
                        "query": "638 E 13th Ave, Denver, CO",
                        "response": {
                            "results": [
                                {
                                    "address_components": {
                                        "number": "638",
                                        "predirectional": "E",
                                        "street": "13th",
                                        "suffix": "Ave",
                                        "city": "Denver",
                                        "county": "Denver County",
                                        "state_province": "CO",
                                        "postal_code": "80203",
                                        "country": "US",
                                    },
                                    "formatted_address": "638 E 13th Ave, Denver, CO 80203",
                                    "location": {"lat": 39.736792, "lng": -104.978914},
                                    "accuracy": 1,
                                    "accuracy_type": "rooftop",
                                    "source": "Denver (City of Denver Open Data Catalog CC BY 3.0)",
                                    "fields": {
                                        "timezone": {
                                            "name": "America/Denver",
                                            "utc_offset": -7,
                                            "observes_dst": True,
                                        },
                                        "cd": [
                                            {
                                                "name": "Congressional District 1",
                                                "district_number": 1,
                                                "congress_number": "119th",
                                            }
                                        ],
                                    },
                                }
                            ]
                        },
                    },
                ]
            },
        )

    httpx_mock.add_callback(
        callback=batch_response_callback,
        url=httpx.URL("https://api.test/v2/geocode", params={"fields": "timezone,cd"}),
        match_headers={"Authorization": "Bearer TEST_KEY"},
    )

    # Act
    resp = client.geocode(addresses, fields=["timezone", "cd"])

    # Assert
    assert len(resp.results) == 2

    # Check first address (Chicago)
    assert resp.results[0].formatted_address == "3730 N Clark St, Chicago, IL 60613"
    assert resp.results[0].fields.timezone.name == "America/Chicago"
    assert resp.results[0].fields.timezone.utc_offset == -6
    assert resp.results[0].fields.congressional_districts[0].district_number == 5

    # Check second address (Denver)
    assert resp.results[1].formatted_address == "638 E 13th Ave, Denver, CO 80203"
    assert resp.results[1].fields.timezone.name == "America/Denver"
    assert resp.results[1].fields.timezone.utc_offset == -7
    assert resp.results[1].fields.congressional_districts[0].district_number == 1


def test_geocode_with_census_fields(client, httpx_mock):
    """Test geocoding with census field appends including all census years."""

    # Arrange: stub the API call with multiple census years
    def response_callback(request):
        assert request.method == "GET"
        assert (
            request.url.params["fields"]
            == "census2010,census2020,census2023,census2024"
        )
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "address_components": {
                            "number": "1640",
                            "street": "Main",
                            "suffix": "St",
                            "city": "Sheldon",
                            "state_province": "VT",
                            "postal_code": "05483",
                            "country": "US",
                        },
                        "formatted_address": "1640 Main St, Sheldon, VT 05483",
                        "location": {"lat": 44.895469, "lng": -72.953264},
                        "accuracy": 1,
                        "accuracy_type": "rooftop",
                        "source": "Vermont",
                        "fields": {
                            "census2010": {
                                "tract": "960100",
                                "block": "2001",
                                "blockgroup": "2",
                                "county_fips": "50011",
                                "state_fips": "50",
                            },
                            "census2020": {
                                "tract": "960100",
                                "block": "2002",
                                "blockgroup": "2",
                                "county_fips": "50011",
                                "state_fips": "50",
                            },
                            "census2023": {
                                "tract": "960100",
                                "block": "2003",
                                "blockgroup": "2",
                                "county_fips": "50011",
                                "state_fips": "50",
                            },
                            "census2024": {
                                "tract": "960100",
                                "block": "2004",
                                "blockgroup": "2",
                                "county_fips": "50011",
                                "state_fips": "50",
                            },
                        },
                    }
                ]
            },
        )

    httpx_mock.add_callback(
        callback=response_callback,
        url=httpx.URL(
            "https://api.test/v2/geocode",
            params={
                "street": "1640 Main St",
                "city": "Sheldon",
                "state": "VT",
                "postal_code": "05483",
                "fields": "census2010,census2020,census2023,census2024",
            },
        ),
        match_headers={"Authorization": "Bearer TEST_KEY"},
    )

    # Act
    resp = client.geocode(
        {
            "city": "Sheldon",
            "state": "VT",
            "street": "1640 Main St",
            "postal_code": "05483",
        },
        fields=["census2010", "census2020", "census2023", "census2024"],
    )

    # Assert
    assert len(resp.results) == 1
    result = resp.results[0]
    assert result.formatted_address == "1640 Main St, Sheldon, VT 05483"

    # Check that all census fields are present and parsed correctly
    assert result.fields.census2010 is not None
    assert result.fields.census2010.tract == "960100"
    assert result.fields.census2010.block == "2001"
    assert result.fields.census2010.county_fips == "50011"

    assert result.fields.census2020 is not None
    assert result.fields.census2020.tract == "960100"
    assert result.fields.census2020.block == "2002"

    assert result.fields.census2023 is not None
    assert result.fields.census2023.tract == "960100"
    assert result.fields.census2023.block == "2003"

    # This will fail until we fix the parsing logic
    assert result.fields.census2024 is not None
    assert result.fields.census2024.tract == "960100"
    assert result.fields.census2024.block == "2004"


def test_geocode_with_stateleg_fields(client, httpx_mock):
    """Test geocoding with state legislative district fields.

    The API returns state_legislative_districts as a dict with house/senate keys,
    each containing a list of district objects with legislator info.
    """

    def response_callback(request):
        assert request.url.params["fields"] == "stateleg"
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "address_components": {
                            "number": "600",
                            "street": "Santa Ray",
                            "suffix": "Ave",
                            "city": "Oakland",
                            "state_province": "CA",
                            "postal_code": "94610",
                            "country": "US",
                        },
                        "formatted_address": "600 Santa Ray Ave, Oakland, CA 94610",
                        "location": {"lat": 37.811943, "lng": -122.240213},
                        "accuracy": 1,
                        "accuracy_type": "rooftop",
                        "source": "Alameda",
                        "fields": {
                            "state_legislative_districts": {
                                "house": [
                                    {
                                        "name": "Assembly District 18",
                                        "district_number": "18",
                                        "ocd_id": "ocd-division/country:us/state:ca/sldl:18",
                                        "is_upcoming_state_legislative_district": False,
                                        "proportion": 1,
                                        "current_legislators": [
                                            {
                                                "type": "representative",
                                                "bio": {
                                                    "last_name": "Bonta",
                                                    "first_name": "Mia",
                                                    "party": "Democrat",
                                                },
                                            }
                                        ],
                                    }
                                ],
                                "senate": [
                                    {
                                        "name": "Senate District 7",
                                        "district_number": "7",
                                        "ocd_id": "ocd-division/country:us/state:ca/sldu:7",
                                        "is_upcoming_state_legislative_district": False,
                                        "proportion": 1,
                                        "current_legislators": [
                                            {
                                                "type": "senator",
                                                "bio": {
                                                    "last_name": "Arreguin",
                                                    "first_name": "Jesse",
                                                    "party": "Democrat",
                                                },
                                            }
                                        ],
                                    }
                                ],
                            }
                        },
                    }
                ]
            },
        )

    httpx_mock.add_callback(
        callback=response_callback,
        url=httpx.URL(
            "https://api.test/v2/geocode",
            params={"q": "600 Santa Ray Ave, Oakland CA 94610", "fields": "stateleg"},
        ),
        match_headers={"Authorization": "Bearer TEST_KEY"},
    )

    # Act
    resp = client.geocode("600 Santa Ray Ave, Oakland CA 94610", fields=["stateleg"])

    # Assert - state legislative districts should be parsed, not None
    fields = resp.results[0].fields
    assert fields.state_legislative_districts is not None
    assert len(fields.state_legislative_districts) == 2

    # Check house district
    house = [d for d in fields.state_legislative_districts if d.chamber == "house"]
    assert len(house) == 1
    assert house[0].name == "Assembly District 18"
    assert house[0].district_number == "18"
    assert house[0].ocd_id == "ocd-division/country:us/state:ca/sldl:18"
    assert house[0].proportion == 1

    # Check senate district
    senate = [d for d in fields.state_legislative_districts if d.chamber == "senate"]
    assert len(senate) == 1
    assert senate[0].name == "Senate District 7"
    assert senate[0].district_number == "7"
    assert senate[0].ocd_id == "ocd-division/country:us/state:ca/sldu:7"

    # Check that legislator info is accessible via extras
    legislators = house[0].get_extra("current_legislators", [])
    assert len(legislators) == 1
    assert legislators[0]["bio"]["last_name"] == "Bonta"

    # Ensure state_legislative_districts didn't leak into extras
    assert "state_legislative_districts" not in fields.extras


def test_geocode_with_uk_fields(client, httpx_mock):
    """Test geocoding a UK address with the UK legislative district appends.

    The API returns uk_westminster / uk_local as lists of district objects.
    """

    def response_callback(request):
        assert request.url.params["fields"] == "uk-westminster,uk-local"
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "address_components": {
                            "number": "10",
                            "street": "Downing",
                            "suffix": "St",
                            "city": "London",
                            "nation": "England",
                            "postal_code": "SW1A 2AA",
                            "country": "GB",
                        },
                        "formatted_address": "10 Downing St, London SW1A 2AA",
                        "location": {"lat": 51.503541, "lng": -0.12767},
                        "accuracy": 1,
                        "accuracy_type": "rooftop",
                        "source": "Contains OS data © Crown copyright.",
                        "fields": {
                            "uk_westminster": [
                                {
                                    "district_type": "westminster_constituency",
                                    "gss_code": "E14001172",
                                    "ocd_id": "ocd-division/country:gb/part:eng/region:uki/ed:cities_of_london_and_westminster",
                                    "name": "Cities of London and Westminster",
                                    "is_upcoming_district": False,
                                    "source": "Office for National Statistics",
                                }
                            ],
                            "uk_local": [
                                {
                                    "district_type": "ward",
                                    "gss_code": "E05013806",
                                    "ocd_id": "ocd-division/country:gb/part:eng/ward:e05013806",
                                    "name": "St James's",
                                    "is_upcoming_district": False,
                                    "source": "Office for National Statistics",
                                }
                            ],
                        },
                    }
                ]
            },
        )

    httpx_mock.add_callback(
        callback=response_callback,
        url=httpx.URL(
            "https://api.test/v2/geocode",
            params={
                "q": "10 Downing St, London, United Kingdom",
                "fields": "uk-westminster,uk-local",
            },
        ),
        match_headers={"Authorization": "Bearer TEST_KEY"},
    )

    # Act
    resp = client.geocode(
        "10 Downing St, London, United Kingdom",
        fields=["uk-westminster", "uk-local"],
    )

    # Assert - UK appends should be parsed into typed models, not None
    fields = resp.results[0].fields
    assert fields.uk_westminster is not None
    assert len(fields.uk_westminster) == 1
    assert fields.uk_westminster[0].name == "Cities of London and Westminster"
    assert fields.uk_westminster[0].district_type == "westminster_constituency"

    assert fields.uk_local is not None
    assert fields.uk_local[0].district_type == "ward"
    assert fields.uk_local[0].name == "St James's"

    # UK devolved was not requested for this address, so it stays None
    assert fields.uk_devolved is None

    # Ensure UK fields didn't leak into extras
    assert "uk_westminster" not in fields.extras
    assert "uk_local" not in fields.extras


def test_geocode_batch_with_unmatched_address(client, httpx_mock):
    """Batch responses can include queries with no results (e.g. an address
    the API could not match). Those entries must not raise IndexError, and the
    result list stays aligned with the submitted addresses so callers can tell
    which query failed."""
    addresses = ["3730 N Clark St, Chicago, IL", "qwertyuiop asdfghjkl zxcvbnm"]

    def batch_response_callback(request):
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "query": "3730 N Clark St, Chicago, IL",
                        "response": {
                            "results": [
                                {
                                    "address_components": {
                                        "number": "3730",
                                        "predirectional": "N",
                                        "street": "Clark",
                                        "suffix": "St",
                                        "city": "Chicago",
                                        "county": "Cook County",
                                        "state_province": "IL",
                                        "postal_code": "60613",
                                        "country": "US",
                                    },
                                    "formatted_address": "3730 N Clark St, Chicago, IL 60613",
                                    "location": {"lat": 41.94987, "lng": -87.65893},
                                    "accuracy": 1,
                                    "accuracy_type": "rooftop",
                                    "source": "Cook",
                                }
                            ]
                        },
                    },
                    {
                        "query": "qwertyuiop asdfghjkl zxcvbnm",
                        "response": {
                            "error": "Could not geocode address. No matches found.",
                            "results": [],
                        },
                    },
                ]
            },
        )

    httpx_mock.add_callback(
        callback=batch_response_callback,
        url=httpx.URL("https://api.test/v2/geocode"),
        match_headers={"Authorization": "Bearer TEST_KEY"},
    )

    resp = client.geocode(addresses)

    # One entry per submitted address, in order.
    assert len(resp.results) == 2

    matched, unmatched = resp.results
    assert matched.matched is True
    assert matched.query == "3730 N Clark St, Chicago, IL"
    assert matched.formatted_address == "3730 N Clark St, Chicago, IL 60613"
    assert matched.location.lat == 41.94987

    # Unmatched query is preserved with no coordinates.
    assert unmatched.matched is False
    assert unmatched.location is None
    assert unmatched.query == "qwertyuiop asdfghjkl zxcvbnm"
    assert unmatched.formatted_address == ""


def test_geocode_batch_exposes_stable_address_key(client, httpx_mock):
    """stable_address_key is parsed from the nested batch response format."""
    addresses = ["1109 N Highland St, Arlington, VA"]

    def batch_response_callback(request):
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "query": "1109 N Highland St, Arlington, VA",
                        "response": {
                            "results": [
                                {
                                    "address_components": {
                                        "number": "1109",
                                        "street": "Highland",
                                        "suffix": "St",
                                        "city": "Arlington",
                                        "state_province": "VA",
                                        "postal_code": "22201",
                                        "country": "US",
                                    },
                                    "formatted_address": "1109 N Highland St, Arlington, VA 22201",
                                    "location": {"lat": 38.886672, "lng": -77.094735},
                                    "accuracy": 1,
                                    "accuracy_type": "rooftop",
                                    "source": "Arlington",
                                    "stable_address_key": "arlington-stable-key",
                                }
                            ]
                        },
                    },
                ]
            },
        )

    httpx_mock.add_callback(
        callback=batch_response_callback,
        url=httpx.URL("https://api.test/v2/geocode"),
        match_headers={"Authorization": "Bearer TEST_KEY"},
    )

    resp = client.geocode(addresses)

    assert resp.results[0].stable_address_key == "arlington-stable-key"


def test_geocode_stable_address_key_absent_is_none(client, httpx_mock):
    """stable_address_key defaults to None when the API omits it."""

    def response_callback(request):
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "address_components": {
                            "number": "1109",
                            "street": "Highland",
                            "suffix": "St",
                            "city": "Arlington",
                            "state_province": "VA",
                            "postal_code": "22201",
                            "country": "US",
                        },
                        "formatted_address": "1109 N Highland St, Arlington, VA 22201",
                        "location": {"lat": 38.886672, "lng": -77.094735},
                        "accuracy": 1,
                        "accuracy_type": "rooftop",
                        "source": "Arlington",
                    }
                ],
            },
        )

    httpx_mock.add_callback(
        callback=response_callback,
        url=httpx.URL(
            "https://api.test/v2/geocode",
            params={"q": "1109 N Highland St, Arlington, VA"},
        ),
        match_headers={"Authorization": "Bearer TEST_KEY"},
    )

    resp = client.geocode("1109 N Highland St, Arlington, VA")

    assert resp.results[0].stable_address_key is None


def test_geocode_nested_census_public_accessor(client, httpx_mock):
    """The nested census structure is reachable via the public accessor."""

    def response_callback(request):
        assert request.url.params["fields"] == "census2023"
        return httpx.Response(
            200,
            json={
                "results": [
                    {
                        "address_components": {
                            "number": "1109",
                            "predirectional": "N",
                            "street": "Highland",
                            "suffix": "St",
                            "city": "Arlington",
                            "state_province": "VA",
                            "postal_code": "22201",
                            "country": "US",
                        },
                        "formatted_address": "1109 N Highland St, Arlington, VA 22201",
                        "location": {"lat": 38.886672, "lng": -77.094735},
                        "accuracy": 1,
                        "accuracy_type": "rooftop",
                        "source": "Arlington",
                        "fields": {
                            "census": {
                                "2023": {
                                    "census_year": 2023,
                                    "state_fips": "51",
                                    "county_fips": "51013",
                                    "tract_code": "101801",
                                    "block_code": "2004",
                                    "block_group": "2",
                                    "full_fips": "510131018012004",
                                    "source": "US Census Bureau",
                                }
                            }
                        },
                    }
                ]
            },
        )

    httpx_mock.add_callback(
        callback=response_callback,
        url=httpx.URL(
            "https://api.test/v2/geocode",
            params={
                "q": "1109 N Highland St, Arlington, VA",
                "fields": "census2023",
            },
        ),
        match_headers={"Authorization": "Bearer TEST_KEY"},
    )

    resp = client.geocode("1109 N Highland St, Arlington, VA", fields=["census2023"])
    fields = resp.results[0].fields

    # New public accessor
    assert fields.census is not None
    assert fields.census.full_fips == "510131018012004"
    assert fields.census.census_year == 2023
    assert fields.get_census(2023).full_fips == "510131018012004"
    assert fields.census_years == [2023]

    # Legacy field name mapping still applies through the accessor
    assert fields.census.tract == "101801"
    assert fields.census.block == "2004"

    # Backward compatibility
    assert fields.census2023.full_fips == "510131018012004"
    assert fields._census["census2023"].full_fips == "510131018012004"


def test_geocode_exposes_match_type_address_lines_and_raw(client, httpx_mock):
    """match_type, address_lines and the raw payload survive parsing."""
    payload = {
        "results": [
            {
                "stable_address_key": "gcod_abc123",
                "address_components": {
                    "number": "1109",
                    "predirectional": "N",
                    "street": "Highland",
                    "suffix": "St",
                    "city": "Arlington",
                    "state_province": "VA",
                    "postal_code": "22201",
                    "country": "US",
                },
                "address_lines": [
                    "1109 N Highland St",
                    "",
                    "Arlington, VA 22201",
                ],
                "formatted_address": "1109 N Highland St, Arlington, VA 22201",
                "location": {"lat": 38.886672, "lng": -77.094735},
                "accuracy": 1,
                "accuracy_type": "rooftop",
                "match_type": "building_centroid",
                "source": "Arlington",
                "some_future_key": {"not": "modelled"},
            }
        ]
    }

    httpx_mock.add_callback(
        callback=lambda request: httpx.Response(
            200,
            json=payload,
            headers={
                "X-RateLimit-Limit": "1000",
                "X-RateLimit-Remaining": "998",
                "X-RateLimit-Period": "60",
            },
        ),
        url=httpx.URL(
            "https://api.test/v2/geocode",
            params={"q": "1109 N Highland St, Arlington, VA"},
        ),
        match_headers={"Authorization": "Bearer TEST_KEY"},
    )

    resp = client.geocode("1109 N Highland St, Arlington, VA")
    result = resp.results[0]

    assert result.match_type == "building_centroid"
    assert result.address_lines == [
        "1109 N Highland St",
        "",
        "Arlington, VA 22201",
    ]

    # Raw payloads keep everything, including keys the models do not map
    assert resp.raw == payload
    assert resp.to_dict() == payload
    assert result.raw == payload["results"][0]
    assert result.to_dict()["some_future_key"] == {"not": "modelled"}

    # Rate limit headers are exposed on the response and the client
    assert resp.rate_limit is not None
    assert resp.rate_limit.limit == 1000
    assert resp.rate_limit.remaining == 998
    assert resp.rate_limit.period == 60
    assert client.rate_limit == resp.rate_limit


def test_geocode_batch_exposes_match_type_and_raw(client, httpx_mock):
    """Batch results carry match_type, address_lines and their raw payload."""
    payload = {
        "results": [
            {
                "query": "1109 N Highland St, Arlington VA",
                "response": {
                    "results": [
                        {
                            "address_components": {
                                "number": "1109",
                                "street": "Highland",
                                "suffix": "St",
                                "city": "Arlington",
                                "state_province": "VA",
                                "postal_code": "22201",
                                "country": "US",
                            },
                            "address_lines": [
                                "1109 N Highland St",
                                "",
                                "Arlington, VA 22201",
                            ],
                            "formatted_address": (
                                "1109 N Highland St, Arlington, VA 22201"
                            ),
                            "location": {"lat": 38.886672, "lng": -77.094735},
                            "accuracy": 1,
                            "accuracy_type": "rooftop",
                            "match_type": "building_centroid",
                            "source": "Arlington",
                        }
                    ]
                },
            },
            {
                "query": "zzzzzz nowhere",
                "response": {"results": []},
            },
        ]
    }

    httpx_mock.add_callback(
        callback=lambda request: httpx.Response(200, json=payload),
        url=httpx.URL("https://api.test/v2/geocode"),
        method="POST",
        match_headers={"Authorization": "Bearer TEST_KEY"},
    )

    resp = client.geocode(["1109 N Highland St, Arlington VA", "zzzzzz nowhere"])

    matched, unmatched = resp.results
    assert matched.match_type == "building_centroid"
    assert matched.address_lines[0] == "1109 N Highland St"
    assert matched.raw == payload["results"][0]["response"]["results"][0]

    # Unmatched queries keep their slot; the full payload stays on the response
    assert unmatched.matched is False
    assert unmatched.match_type is None
    assert unmatched.address_lines is None
    assert unmatched.raw == {}
    assert resp.raw == payload
