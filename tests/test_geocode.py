import json
from pathlib import Path
from geocodio.models import GeocodingResponse, AddressComponents
import httpx


def sample_payload() -> dict:
    return {
        "input": {
            "address_components": {
                "number": "1109",
                "predirectional": "N",
                "street": "Highland",
                "suffix": "St",
                "formatted_street": "N Highland St",
                "city": "Arlington",
                "state": "VA",
                "country": "US",
            },
            "formatted_address": "1109 N Highland St, Arlington, VA",
        },
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
                    "state": "VA",
                    "zip": "22201",
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
            }
        ],
    }


def test_geocode_single(client, httpx_mock):
    # Arrange: stub the API call with a callback to inspect the request
    def response_callback(request):
        print("\nActual request:", request.url)
        print("Actual request headers:", dict(request.headers))
        return httpx.Response(200, json=sample_payload())

    httpx_mock.add_callback(
        callback=response_callback,
        url=httpx.URL("https://api.test/v1.7/geocode", params={"api_key": "TEST_KEY", "q": "1109 N Highland St, Arlington, VA"}),
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


def test_geocode_batch(client, httpx_mock):
    # Arrange: stub the API call
    addresses = [
        "1109 N Highland St, Arlington, VA",
        "1600 Pennsylvania Ave NW, Washington, DC"
    ]

    def batch_response_callback(request):
        assert request.method == "POST"  # Should use POST for batch
        assert json.loads(request.content) == {"addresses": addresses}  # Check payload
        return httpx.Response(200, json={
            "results": [
                sample_payload()["results"][0],  # First address
                {  # Second address
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
        url=httpx.URL("https://api.test/v1.7/geocode", params={"api_key": "TEST_KEY"}),
    )

    # Act
    resp = client.geocode(addresses)

    # Assert
    assert len(resp.results) == 2
    assert resp.results[0].formatted_address.endswith("VA 22201")
    assert resp.results[1].formatted_address.endswith("DC 20500")
    assert resp.results[1].location.lat == 38.898719