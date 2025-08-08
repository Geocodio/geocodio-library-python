"""
Tests for the Geocodio class
"""

import pytest
import httpx
from geocodio import Geocodio
from geocodio.exceptions import AuthenticationError


@pytest.fixture
def mock_request(mocker):
    """Mock the _request method."""
    return mocker.patch('geocodio.client.Geocodio._request')


def test_client_initialization():
    """Test that the client can be initialized with an API key"""
    client = Geocodio(api_key="test-key")
    assert client.api_key == "test-key"
    assert client.hostname == "api.geocod.io"


def test_client_initialization_with_env_var(monkeypatch):
    """Test that the client can be initialized with an environment variable"""
    monkeypatch.setenv("GEOCODIO_API_KEY", "env-key")
    client = Geocodio()
    assert client.api_key == "env-key"


def test_client_initialization_no_key(monkeypatch):
    """Test that the client raises an error when no API key is provided"""
    # Ensure environment variable is not set
    monkeypatch.delenv("GEOCODIO_API_KEY", raising=False)
    with pytest.raises(AuthenticationError, match="No API key supplied and GEOCODIO_API_KEY is not set"):
        Geocodio()


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

    client = Geocodio("fake-key")
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

    client = Geocodio("fake-key")
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

    client = Geocodio("fake-key")
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

    client = Geocodio("fake-key")
    response = client.geocode(
        {"street": "1109 N Highland St", "city": "Arlington", "state": "VA"},
        fields=["cd"]
    )

    assert response.results[0].fields.congressional_districts is not None
    assert len(response.results[0].fields.congressional_districts) == 1
    assert response.results[0].fields.congressional_districts[0].name == "Virginia's 8th congressional district"
    assert response.results[0].fields.congressional_districts[0].district_number == 8
    assert response.results[0].fields.congressional_districts[0].congress_number == "118"


def test_user_agent_header_in_request(mocker):
    """Test that the User-Agent header is included in all requests."""
    from geocodio import __version__
    
    # Mock the httpx.Client.request method to capture headers
    mock_httpx_request = mocker.patch('httpx.Client.request')
    mock_httpx_request.return_value = httpx.Response(200, json={
        "input": {"address_components": {"q": "1109 N Highland St, Arlington, VA"}},
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
            "source": "Virginia GIS Clearinghouse"
        }]
    })
    
    client = Geocodio("test-api-key")
    client.geocode("1109 N Highland St, Arlington, VA")
    
    # Verify request was made with correct headers
    mock_httpx_request.assert_called_once()
    call_args = mock_httpx_request.call_args
    headers = call_args.kwargs.get('headers', {})
    
    assert 'User-Agent' in headers
    assert headers['User-Agent'] == f"geocodio-library-python/{__version__}"
    assert 'Authorization' in headers
    assert headers['Authorization'] == "Bearer test-api-key"


def test_user_agent_header_format():
    """Test that the User-Agent header has the correct format."""
    from geocodio import __version__
    
    client = Geocodio("test-api-key")
    expected_user_agent = f"geocodio-library-python/{__version__}"
    assert client.USER_AGENT == expected_user_agent


def test_user_agent_header_in_batch_request(mocker):
    """Test that the User-Agent header is included in batch requests."""
    from geocodio import __version__
    
    # Mock the httpx.Client.request method
    mock_httpx_request = mocker.patch('httpx.Client.request')
    mock_httpx_request.return_value = httpx.Response(200, json={
        "results": []
    })
    
    client = Geocodio("test-api-key")
    client.geocode(["Address 1", "Address 2"])
    
    # Verify headers in batch request
    mock_httpx_request.assert_called_once()
    call_args = mock_httpx_request.call_args
    headers = call_args.kwargs.get('headers', {})
    
    assert headers['User-Agent'] == f"geocodio-library-python/{__version__}"


def test_user_agent_header_in_reverse_geocode(mocker):
    """Test that the User-Agent header is included in reverse geocoding requests."""
    from geocodio import __version__
    
    # Mock the httpx.Client.request method
    mock_httpx_request = mocker.patch('httpx.Client.request')
    mock_httpx_request.return_value = httpx.Response(200, json={
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
            "source": "Virginia GIS Clearinghouse"
        }]
    })
    
    client = Geocodio("test-api-key")
    client.reverse("38.886665,-77.094733")
    
    # Verify headers in reverse geocode request
    mock_httpx_request.assert_called_once()
    call_args = mock_httpx_request.call_args
    headers = call_args.kwargs.get('headers', {})
    
    assert headers['User-Agent'] == f"geocodio-library-python/{__version__}"


def test_user_agent_header_in_list_api(mocker):
    """Test that the User-Agent header is included in List API requests."""
    from geocodio import __version__
    
    # Mock the httpx.Client.request method
    mock_httpx_request = mocker.patch('httpx.Client.request')
    mock_httpx_request.return_value = httpx.Response(200, json={
        "data": [],
        "current_page": 1,
        "from": 0,
        "to": 0,
        "path": "",
        "per_page": 10
    })
    
    client = Geocodio("test-api-key")
    client.get_lists()
    
    # Verify headers in list API request
    mock_httpx_request.assert_called_once()
    call_args = mock_httpx_request.call_args
    headers = call_args.kwargs.get('headers', {})
    
    assert headers['User-Agent'] == f"geocodio-library-python/{__version__}"