"""
End-to-end tests for batch reverse geocoding functionality.
"""

import pytest
from geocodio import GeocodioClient


def test_batch_reverse_geocoding(client):
    """Test batch reverse geocoding against real API."""
    # Arrange
    coordinates = [
        (38.886665, -77.094733),  # Arlington, VA
        (38.897676, -77.036530),  # White House
        (37.331669, -122.030090)  # Apple Park
    ]
    
    # Act
    response = client.reverse(coordinates)
    
    # Assert
    assert response is not None
    assert len(response.results) == 3
    
    # Check first result (Arlington, VA)
    arlington = response.results[0]
    assert "Arlington" in arlington.formatted_address
    assert "VA" in arlington.formatted_address
    assert arlington.location.lat == pytest.approx(38.886672, abs=0.001)
    assert arlington.location.lng == pytest.approx(-77.094735, abs=0.001)
    
    # Check second result (White House)
    white_house = response.results[1]
    assert "Pennsylvania" in white_house.formatted_address
    assert "Washington" in white_house.formatted_address or "DC" in white_house.formatted_address
    
    # Check third result (Apple Park)
    apple_park = response.results[2]
    assert "Cupertino" in apple_park.formatted_address or "CA" in apple_park.formatted_address


def test_batch_reverse_with_strings(client):
    """Test batch reverse geocoding with string coordinates."""
    # Arrange
    coordinates = [
        "38.886665,-77.094733",  # Arlington, VA
        "38.897676,-77.036530"   # White House
    ]
    
    # Act
    response = client.reverse(coordinates)
    
    # Assert
    assert response is not None
    assert len(response.results) == 2
    assert "Arlington" in response.results[0].formatted_address
    assert "Pennsylvania" in response.results[1].formatted_address or "Washington" in response.results[1].formatted_address


def test_batch_reverse_with_fields(client):
    """Test batch reverse geocoding with additional fields."""
    # Arrange
    coordinates = [
        (38.886665, -77.094733),  # Arlington, VA
        (38.897676, -77.036530)   # White House
    ]
    
    # Act
    response = client.reverse(coordinates, fields=["timezone", "cd"])
    
    # Assert
    assert response is not None
    assert len(response.results) == 2
    
    # Check that fields are populated
    for result in response.results:
        assert result.fields is not None
        if result.fields.timezone:
            assert result.fields.timezone.name is not None
        if result.fields.congressional_districts:
            assert len(result.fields.congressional_districts) > 0


def test_empty_batch_reverse(client):
    """Test batch reverse geocoding with empty list."""
    # Arrange
    coordinates = []
    
    # Act & Assert
    with pytest.raises(Exception):
        client.reverse(coordinates)


def test_mixed_batch_reverse_formats(client):
    """Test batch reverse geocoding with mixed coordinate formats."""
    # Note: The API expects consistent format, so this tests error handling
    # Arrange
    coordinates = [
        (38.886665, -77.094733),  # Tuple format
        "38.897676,-77.036530"     # String format
    ]
    
    # Act
    # The library should handle converting these to a consistent format
    response = client.reverse(coordinates)
    
    # Assert
    assert response is not None
    assert len(response.results) == 2