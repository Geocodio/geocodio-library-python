import pytest
from geocodio.exceptions import (
    GeocodioErrorDetail,
    GeocodioError,
    InvalidRequestError,
    AuthenticationError,
    GeocodioServerError,
)


def test_error_detail_with_code_and_errors():
    detail = GeocodioErrorDetail(
        message="Invalid input",
        code=422,
        errors=["Field 'address' is required"]
    )
    assert detail.message == "Invalid input"
    assert detail.code == 422
    assert detail.errors == ["Field 'address' is required"]


def test_error_with_string_detail():
    error = GeocodioError("Simple error message")
    assert str(error) == "Simple error message"
    assert error.detail.message == "Simple error message"
    assert error.detail.code is None
    assert error.detail.errors is None


def test_error_with_error_detail():
    detail = GeocodioErrorDetail(
        message="Complex error",
        code=500,
        errors=["Database error", "Network timeout"]
    )
    error = GeocodioError(detail)
    assert str(error) == "Complex error"
    assert error.detail.code == 500
    assert error.detail.errors == ["Database error", "Network timeout"]


def test_specific_errors():
    # Test that specific error classes maintain the error detail structure
    invalid_req = InvalidRequestError("Invalid request")
    assert str(invalid_req) == "Invalid request"
    assert invalid_req.detail.message == "Invalid request"

    auth_error = AuthenticationError("Invalid API key")
    assert str(auth_error) == "Invalid API key"
    assert auth_error.detail.message == "Invalid API key"

    server_error = GeocodioServerError("Internal server error")
    assert str(server_error) == "Internal server error"
    assert server_error.detail.message == "Internal server error"