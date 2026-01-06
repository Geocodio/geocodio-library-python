"""
End-to-end tests for the Distance API.

These tests require a valid GEOCODIO_API_KEY environment variable.
They make real API calls to the Geocodio service.
"""

import os
import pytest
from geocodio import (
    Geocodio,
    Coordinate,
    DISTANCE_MODE_STRAIGHTLINE,
    DISTANCE_MODE_DRIVING,
    DISTANCE_UNITS_MILES,
    DISTANCE_UNITS_KM,
    DistanceResponse,
    DistanceMatrixResponse,
)


# Skip all tests if no API key is available
pytestmark = pytest.mark.skipif(
    not os.getenv("GEOCODIO_API_KEY"),
    reason="GEOCODIO_API_KEY environment variable not set"
)


@pytest.fixture
def client():
    """Create a Geocodio client with real API key."""
    api_key = os.getenv("GEOCODIO_API_KEY")
    return Geocodio(api_key=api_key)


# ──────────────────────────────────────────────────────────────────────────────
# Distance Method E2E Tests
# ──────────────────────────────────────────────────────────────────────────────


class TestDistanceE2E:
    """End-to-end tests for distance() method."""

    def test_distance_basic(self, client):
        """Test basic distance calculation with real API."""
        response = client.distance(
            origin="38.8977,-77.0365",  # White House
            destinations=[
                "38.8895,-77.0353",  # Washington Monument
                "38.9072,-77.0369"   # Capitol Building
            ],
            mode=DISTANCE_MODE_STRAIGHTLINE,
            units=DISTANCE_UNITS_MILES
        )

        assert isinstance(response, DistanceResponse)
        assert response.mode == "straightline"
        assert len(response.destinations) == 2

        # Check distances are reasonable (should be < 2 miles)
        for dest in response.destinations:
            assert dest.distance_miles > 0
            assert dest.distance_miles < 2
            assert dest.distance_km > 0

    def test_distance_with_ids(self, client):
        """Test distance with coordinate IDs."""
        response = client.distance(
            origin=Coordinate(38.8977, -77.0365, "white_house"),
            destinations=[
                Coordinate(38.8895, -77.0353, "monument"),
                Coordinate(38.9072, -77.0369, "capitol")
            ]
        )

        assert isinstance(response, DistanceResponse)
        assert response.destinations[0].id == "monument"
        assert response.destinations[1].id == "capitol"

    def test_distance_driving_mode(self, client):
        """Test distance with driving mode returns duration."""
        response = client.distance(
            origin="38.8977,-77.0365",
            destinations=["38.8895,-77.0353"],
            mode=DISTANCE_MODE_DRIVING
        )

        assert response.mode == "driving"
        # Driving mode should include duration
        for dest in response.destinations:
            assert dest.duration_seconds is not None
            assert dest.duration_seconds > 0

    def test_distance_kilometers(self, client):
        """Test distance in kilometers."""
        response = client.distance(
            origin="38.8977,-77.0365",
            destinations=["38.8895,-77.0353"],
            units=DISTANCE_UNITS_KM
        )

        assert isinstance(response, DistanceResponse)
        # Both miles and km should be in response
        assert response.destinations[0].distance_miles > 0
        assert response.destinations[0].distance_km > 0


# ──────────────────────────────────────────────────────────────────────────────
# Distance Matrix E2E Tests
# ──────────────────────────────────────────────────────────────────────────────


class TestDistanceMatrixE2E:
    """End-to-end tests for distance_matrix() method."""

    def test_distance_matrix_basic(self, client):
        """Test basic distance matrix calculation."""
        response = client.distance_matrix(
            origins=[
                (38.8977, -77.0365),  # White House
                (38.9072, -77.0369)   # Capitol
            ],
            destinations=[
                (38.8895, -77.0353),  # Washington Monument
                (38.8816, -77.0364)   # Jefferson Memorial
            ]
        )

        assert isinstance(response, DistanceMatrixResponse)
        assert len(response.results) == 2  # Two origins

        for result in response.results:
            assert len(result.destinations) == 2  # Two destinations per origin
            for dest in result.destinations:
                assert dest.distance_miles > 0
                assert dest.distance_km > 0

    def test_distance_matrix_with_ids(self, client):
        """Test distance matrix preserves IDs."""
        response = client.distance_matrix(
            origins=[
                Coordinate(38.8977, -77.0365, "origin1"),
                Coordinate(38.9072, -77.0369, "origin2")
            ],
            destinations=[
                Coordinate(38.8895, -77.0353, "dest1")
            ]
        )

        assert isinstance(response, DistanceMatrixResponse)
        # Check IDs are preserved
        assert response.results[0].origin.id == "origin1"
        assert response.results[1].origin.id == "origin2"


# ──────────────────────────────────────────────────────────────────────────────
# Geocode with Distance E2E Tests
# ──────────────────────────────────────────────────────────────────────────────


class TestGeocodeWithDistanceE2E:
    """End-to-end tests for geocode() with distance parameters."""

    def test_geocode_with_destinations(self, client):
        """Test geocode with distance to destinations."""
        response = client.geocode(
            "1600 Pennsylvania Ave NW, Washington DC",
            destinations=["38.8895,-77.0353"]  # Washington Monument
        )

        assert len(response.results) >= 1
        # Note: The response structure for geocode+distance may vary
        # This test mainly verifies the request is accepted

    def test_reverse_with_destinations(self, client):
        """Test reverse geocode with distance to destinations."""
        response = client.reverse(
            (38.8977, -77.0365),  # White House coordinates
            destinations=["38.8895,-77.0353"]  # Washington Monument
        )

        assert len(response.results) >= 1


# ──────────────────────────────────────────────────────────────────────────────
# Coordinate Class E2E Tests
# ──────────────────────────────────────────────────────────────────────────────


class TestCoordinateE2E:
    """End-to-end tests verifying Coordinate class works with real API."""

    def test_all_coordinate_formats(self, client):
        """Test that all coordinate formats work with the API."""
        # String format
        response1 = client.distance(
            origin="38.8977,-77.0365",
            destinations=["38.8895,-77.0353"]
        )
        assert isinstance(response1, DistanceResponse)

        # Tuple format
        response2 = client.distance(
            origin=(38.8977, -77.0365),
            destinations=[(38.8895, -77.0353)]
        )
        assert isinstance(response2, DistanceResponse)

        # Coordinate object format
        response3 = client.distance(
            origin=Coordinate(38.8977, -77.0365),
            destinations=[Coordinate(38.8895, -77.0353)]
        )
        assert isinstance(response3, DistanceResponse)

        # Mixed formats
        response4 = client.distance(
            origin=Coordinate(38.8977, -77.0365, "white_house"),
            destinations=[
                "38.8895,-77.0353,monument",
                (38.9072, -77.0369)
            ]
        )
        assert isinstance(response4, DistanceResponse)

        # All responses should have similar distances (within tolerance)
        dist1 = response1.destinations[0].distance_miles
        dist2 = response2.destinations[0].distance_miles
        dist3 = response3.destinations[0].distance_miles

        assert abs(dist1 - dist2) < 0.01
        assert abs(dist2 - dist3) < 0.01
