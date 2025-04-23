import pytest
import httpx
from geocodio.models import GeocodingResponse, Location


def test_reverse_single_coordinate(client, httpx_mock):
    # Arrange: stub the API call
    def response_callback(request):
        assert request.method == "GET"
        assert request.url.params["q"] == "38.886672,-77.094735"
        return httpx.Response(200, json={
            "results": [{
                "address_components": {
                    "number": "1109",
                    "predirectional": "N",
                    "street": "Highland",
                    "suffix": "St",
                    "formatted_street": "N Highland St",
                    "city": "Arlington",
                    "county": "Arlington County",
                    "state": "VA",
                    "zip": "22201",
                    "country": "US",
                },
                "formatted_address": "1109 N Highland St, Arlington, VA 22201",
                "location": {"lat": 38.886672, "lng": -77.094735},
                "accuracy": 1,
                "accuracy_type": "rooftop",
                "source": "Arlington"
            }]
        })

    httpx_mock.add_callback(
        callback=response_callback,
        url=httpx.URL("https://api.test/v1.7/reverse", params={"api_key": "TEST_KEY", "q": "38.886672,-77.094735"}),
    )

    # Act
    resp: GeocodingResponse = client.reverse((38.886672, -77.094735))

    # Assert
    assert len(resp.results) == 1
    assert resp.results[0].formatted_address == "1109 N Highland St, Arlington, VA 22201"
    assert resp.results[0].location.lat == 38.886672
    assert resp.results[0].location.lng == -77.094735


def test_reverse_batch_coordinates(client, httpx_mock):
    # Arrange: stub the API call
    coordinates = [
        (38.886672, -77.094735),
        (38.898719, -77.036547)
    ]

    def batch_response_callback(request):
        assert request.method == "POST"
        assert request.url.params["api_key"] == "TEST_KEY"
        return httpx.Response(200, json={
            "results": [
                {
                    "address_components": {
                        "number": "1109",
                        "predirectional": "N",
                        "street": "Highland",
                        "suffix": "St",
                        "formatted_street": "N Highland St",
                        "city": "Arlington",
                        "state": "VA",
                        "zip": "22201"
                    },
                    "formatted_address": "1109 N Highland St, Arlington, VA 22201",
                    "location": {"lat": 38.886672, "lng": -77.094735},
                    "accuracy": 1,
                    "accuracy_type": "rooftop",
                    "source": "Arlington"
                },
                {
                    "address_components": {
                        "number": "1600",
                        "street": "Pennsylvania",
                        "suffix": "Ave",
                        "postdirectional": "NW",
                        "city": "Washington",
                        "state": "DC",
                        "zip": "20500"
                    },
                    "formatted_address": "1600 Pennsylvania Ave NW, Washington, DC 20500",
                    "location": {"lat": 38.898719, "lng": -77.036547},
                    "accuracy": 1,
                    "accuracy_type": "rooftop",
                    "source": "DC"
                }
            ]
        })

    httpx_mock.add_callback(
        callback=batch_response_callback,
        url=httpx.URL("https://api.test/v1.7/reverse", params={"api_key": "TEST_KEY"}),
    )

    # Act
    resp = client.reverse(coordinates)

    # Assert
    assert len(resp.results) == 2
    assert resp.results[0].formatted_address == "1109 N Highland St, Arlington, VA 22201"
    assert resp.results[1].formatted_address == "1600 Pennsylvania Ave NW, Washington, DC 20500"


def test_reverse_with_fields(client, httpx_mock):
    # Arrange: stub the API call with timezone field
    def response_callback(request):
        assert request.method == "GET"
        assert request.url.params["fields"] == "timezone,cd"
        return httpx.Response(200, json={
            "results": [{
                "address_components": {
                    "number": "1109",
                    "street": "Highland",
                    "suffix": "St",
                    "city": "Arlington",
                    "state": "VA",
                    "zip": "22201"
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
                        "observes_dst": True
                    },
                    "cd": [
                        {
                            "name": "Virginia's 8th congressional district",
                            "district_number": 8,
                            "congress_number": "118"
                        }
                    ]
                }
            }]
        })

    httpx_mock.add_callback(
        callback=response_callback,
        url=httpx.URL("https://api.test/v1.7/reverse", params={
            "api_key": "TEST_KEY",
            "q": "38.886672,-77.094735",
            "fields": "timezone,cd"
        }),
    )

    # Act
    resp = client.reverse((38.886672, -77.094735), fields=["timezone", "cd"])

    # Assert
    assert len(resp.results) == 1
    assert resp.results[0].fields.timezone.name == "America/New_York"
    assert resp.results[0].fields.timezone.utc_offset == -5
    assert resp.results[0].fields.timezone.observes_dst is True
    assert len(resp.results[0].fields.congressional_districts) == 1
    assert resp.results[0].fields.congressional_districts[0].name == "Virginia's 8th congressional district"
    assert resp.results[0].fields.congressional_districts[0].district_number == 8
    assert resp.results[0].fields.congressional_districts[0].congress_number == "118"


def test_reverse_with_limit(client, httpx_mock):
    # Arrange: stub the API call
    def response_callback(request):
        assert request.method == "GET"
        assert request.url.params["limit"] == "2"
        return httpx.Response(200, json={
            "results": [
                {
                    "address_components": {
                        "number": "1109",
                        "street": "Highland",
                        "suffix": "St",
                        "city": "Arlington",
                        "state": "VA",
                        "zip": "22201"
                    },
                    "formatted_address": "1109 Highland St, Arlington, VA 22201",
                    "location": {"lat": 38.886672, "lng": -77.094735},
                    "accuracy": 1,
                    "accuracy_type": "rooftop",
                    "source": "Arlington"
                },
                {
                    "address_components": {
                        "number": "1111",
                        "street": "Highland",
                        "suffix": "St",
                        "city": "Arlington",
                        "state": "VA",
                        "zip": "22201"
                    },
                    "formatted_address": "1111 Highland St, Arlington, VA 22201",
                    "location": {"lat": 38.886672, "lng": -77.094735},
                    "accuracy": 1,
                    "accuracy_type": "rooftop",
                    "source": "Arlington"
                }
            ]
        })

    httpx_mock.add_callback(
        callback=response_callback,
        url=httpx.URL("https://api.test/v1.7/reverse", params={
            "api_key": "TEST_KEY",
            "q": "38.886672,-77.094735",
            "limit": "2"
        }),
    )

    # Act
    resp = client.reverse((38.886672, -77.094735), limit=2)

    # Assert
    assert len(resp.results) == 2
    assert resp.results[0].formatted_address == "1109 Highland St, Arlington, VA 22201"
    assert resp.results[1].formatted_address == "1111 Highland St, Arlington, VA 22201"


def test_reverse_invalid_coordinate(client, httpx_mock):
    # Arrange: stub the API call with error response
    httpx_mock.add_response(
        url=httpx.URL("https://api.test/v1.7/reverse", params={
            "api_key": "TEST_KEY",
            "q": "invalid,coordinate"
        }),
        json={"error": "Invalid coordinate format"},
        status_code=422
    )

    # Act & Assert
    with pytest.raises(Exception):
        client.reverse("invalid,coordinate")