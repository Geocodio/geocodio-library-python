"""
Tests for the GeocodioClient class
"""

import pytest
import httpx
from geocodio import GeocodioClient


@pytest.fixture
def mock_request(mocker):
    """Mock the _request method."""
    return mocker.patch('geocodio.client.GeocodioClient._request')


def test_client_initialization():
    """Test that the client can be initialized with an API key"""
    client = GeocodioClient(api_key="test-key")
    assert client.api_key == "test-key"
    assert client.hostname == "api.geocod.io"


def test_client_initialization_with_env_var(monkeypatch):
    """Test that the client can be initialized with an environment variable"""
    monkeypatch.setenv("GEOCODIO_API_KEY", "env-key")
    client = GeocodioClient()
    assert client.api_key == "env-key"


def test_client_initialization_no_key():
    """Test that the client raises an error when no API key is provided"""
    with pytest.raises(Exception):
        GeocodioClient(api_key="")


def test_geocode_with_census_data(mock_request):
    """Test geocoding with census data field."""
    mock_request.return_value = httpx.Response(200, json={
        "input": {"address_components": {"street": "1109 N Highland St", "city": "Arlington", "state": "VA"}},
        "results": [{
            "address_components": {
                "number": "1109",
                "street": "N Highland St",
                "city": "Arlington",
                "state": "VA"
            },
            "formatted_address": "1109 N Highland St, Arlington, VA",
            "location": {"lat": 38.886665, "lng": -77.094733},
            "accuracy": 1.0,
            "accuracy_type": "rooftop",
            "source": "Virginia GIS Clearinghouse",
            "fields": {
                "census2010": {
                    "block": "1000",
                    "blockgroup": "1",
                    "tract": "100100",
                    "county_fips": "51013",
                    "state_fips": "51"
                }
            }
        }]
    })

    client = GeocodioClient("fake-key")
    response = client.geocode(
        {"street": "1109 N Highland St", "city": "Arlington", "state": "VA"},
        fields=["census2010"]
    )

    assert response.results[0].fields.census2010 is not None
    assert response.results[0].fields.census2010.block == "1000"
    assert response.results[0].fields.census2010.tract == "100100"


def test_geocode_with_acs_data(mock_request):
    """Test geocoding with ACS survey data field."""
    mock_request.return_value = httpx.Response(200, json={
        "input": {"address_components": {"street": "1109 N Highland St", "city": "Arlington", "state": "VA"}},
        "results": [{
            "address_components": {
                "number": "1109",
                "street": "N Highland St",
                "city": "Arlington",
                "state": "VA"
            },
            "formatted_address": "1109 N Highland St, Arlington, VA",
            "location": {"lat": 38.886665, "lng": -77.094733},
            "accuracy": 1.0,
            "accuracy_type": "rooftop",
            "source": "Virginia GIS Clearinghouse",
            "fields": {
                "acs": {
                    "population": 1000,
                    "households": 500,
                    "median_income": 75000,
                    "median_age": 35.5
                }
            }
        }]
    })

    client = GeocodioClient("fake-key")
    response = client.geocode(
        {"street": "1109 N Highland St", "city": "Arlington", "state": "VA"},
        fields=["acs"]
    )

    assert response.results[0].fields.acs is not None
    assert response.results[0].fields.acs.population == 1000
    assert response.results[0].fields.acs.median_income == 75000


def test_geocode_batch_with_custom_keys(mock_request):
    """Test batch geocoding with custom keys."""
    mock_request.return_value = httpx.Response(200, json={
        "input": {
            "addresses": [
                "1109 N Highland St, Arlington, VA",
                "525 University Ave, Toronto, ON, Canada"
            ],
            "keys": ["address1", "address2"]
        },
        "results": [
            {
                "address_components": {
                    "number": "1109",
                    "street": "N Highland St",
                    "city": "Arlington",
                    "state": "VA"
                },
                "formatted_address": "1109 N Highland St, Arlington, VA",
                "location": {"lat": 38.886665, "lng": -77.094733},
                "accuracy": 1.0,
                "accuracy_type": "rooftop",
                "source": "Virginia GIS Clearinghouse"
            },
            {
                "address_components": {
                    "number": "525",
                    "street": "University Ave",
                    "city": "Toronto",
                    "state": "ON",
                    "country": "Canada"
                },
                "formatted_address": "525 University Ave, Toronto, ON, Canada",
                "location": {"lat": 43.662891, "lng": -79.395656},
                "accuracy": 1.0,
                "accuracy_type": "rooftop",
                "source": "Canada Post"
            }
        ]
    })

    client = GeocodioClient("fake-key")
    response = client.geocode({
        "address1": "1109 N Highland St, Arlington, VA",
        "address2": "525 University Ave, Toronto, ON, Canada"
    })

    assert len(response.results) == 2
    assert response.input["addresses"][0] == "1109 N Highland St, Arlington, VA"
    assert response.input["keys"][0] == "address1"


def test_geocode_with_congressional_districts(mock_request):
    """Test geocoding with congressional districts field."""
    mock_request.return_value = httpx.Response(200, json={
        "input": {"address_components": {"street": "1109 N Highland St", "city": "Arlington", "state": "VA"}},
        "results": [{
            "address_components": {
                "number": "1109",
                "street": "N Highland St",
                "city": "Arlington",
                "state": "VA"
            },
            "formatted_address": "1109 N Highland St, Arlington, VA",
            "location": {"lat": 38.886665, "lng": -77.094733},
            "accuracy": 1.0,
            "accuracy_type": "rooftop",
            "source": "Virginia GIS Clearinghouse",
            "fields": {
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

    client = GeocodioClient("fake-key")
    response = client.geocode(
        {"street": "1109 N Highland St", "city": "Arlington", "state": "VA"},
        fields=["cd"]
    )

    assert response.results[0].fields.congressional_districts is not None
    assert len(response.results[0].fields.congressional_districts) == 1
    assert response.results[0].fields.congressional_districts[0].name == "Virginia's 8th congressional district"
    assert response.results[0].fields.congressional_districts[0].district_number == 8
    assert response.results[0].fields.congressional_districts[0].congress_number == "118"