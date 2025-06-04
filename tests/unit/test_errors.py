import pytest
import httpx
from geocodio.exceptions import (
    InvalidRequestError, AuthenticationError, GeocodioServerError
)


def _add_err(httpx_mock, status_code):
    # this should actually make the request and see and error response
    # but we are mocking it here for testing purposes
    httpx_mock.add_response(
        url=httpx.URL("https://api.test/v1.8/geocode", params={"api_key": "TEST_KEY", "q": "bad input"}),
        json={"error": "boom"},
        status_code=status_code,
    )



@pytest.mark.parametrize("code,exc", [
    (422, InvalidRequestError),
    (403, AuthenticationError),
    (500, GeocodioServerError),
])
def test_error_mapping(client, httpx_mock, code, exc):
    _add_err(httpx_mock, code)
    with pytest.raises(exc):
        client.geocode("bad input")