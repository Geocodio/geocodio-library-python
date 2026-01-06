"""
Unit tests for the Distance API implementation.
"""

import json
import pytest
import httpx

from geocodio import (
    Geocodio,
    Coordinate,
    DISTANCE_MODE_STRAIGHTLINE,
    DISTANCE_MODE_DRIVING,
    DISTANCE_MODE_HAVERSINE,
    DISTANCE_UNITS_MILES,
    DISTANCE_UNITS_KM,
    DISTANCE_ORDER_BY_DISTANCE,
    DISTANCE_ORDER_BY_DURATION,
    DISTANCE_SORT_ASC,
    DISTANCE_SORT_DESC,
    DistanceResponse,
    DistanceMatrixResponse,
    DistanceJobResponse,
)


# ──────────────────────────────────────────────────────────────────────────────
# Coordinate Class Tests
# ──────────────────────────────────────────────────────────────────────────────


class TestCoordinate:
    """Tests for the Coordinate class."""

    def test_create_basic(self):
        """Test basic coordinate creation."""
        coord = Coordinate(38.8977, -77.0365)
        assert coord.lat == 38.8977
        assert coord.lng == -77.0365
        assert coord.id is None

    def test_create_with_id(self):
        """Test coordinate creation with id."""
        coord = Coordinate(38.8977, -77.0365, "white_house")
        assert coord.lat == 38.8977
        assert coord.lng == -77.0365
        assert coord.id == "white_house"

    def test_validation_lat_too_high(self):
        """Test latitude validation - too high."""
        with pytest.raises(ValueError, match="Latitude must be between"):
            Coordinate(91.0, -77.0365)

    def test_validation_lat_too_low(self):
        """Test latitude validation - too low."""
        with pytest.raises(ValueError, match="Latitude must be between"):
            Coordinate(-91.0, -77.0365)

    def test_validation_lng_too_high(self):
        """Test longitude validation - too high."""
        with pytest.raises(ValueError, match="Longitude must be between"):
            Coordinate(38.8977, 181.0)

    def test_validation_lng_too_low(self):
        """Test longitude validation - too low."""
        with pytest.raises(ValueError, match="Longitude must be between"):
            Coordinate(38.8977, -181.0)

    def test_from_string_basic(self):
        """Test creating coordinate from string 'lat,lng'."""
        coord = Coordinate.from_input("38.8977,-77.0365")
        assert coord.lat == 38.8977
        assert coord.lng == -77.0365
        assert coord.id is None

    def test_from_string_with_id(self):
        """Test creating coordinate from string 'lat,lng,id'."""
        coord = Coordinate.from_input("38.8977,-77.0365,white_house")
        assert coord.lat == 38.8977
        assert coord.lng == -77.0365
        assert coord.id == "white_house"

    def test_from_string_with_spaces(self):
        """Test creating coordinate from string with spaces."""
        coord = Coordinate.from_input(" 38.8977 , -77.0365 , white_house ")
        assert coord.lat == 38.8977
        assert coord.lng == -77.0365
        assert coord.id == "white_house"

    def test_from_tuple(self):
        """Test creating coordinate from tuple (lat, lng)."""
        coord = Coordinate.from_input((38.8977, -77.0365))
        assert coord.lat == 38.8977
        assert coord.lng == -77.0365
        assert coord.id is None

    def test_from_tuple_with_id(self):
        """Test creating coordinate from tuple (lat, lng, id)."""
        coord = Coordinate.from_input((38.8977, -77.0365, "white_house"))
        assert coord.lat == 38.8977
        assert coord.lng == -77.0365
        assert coord.id == "white_house"

    def test_from_list(self):
        """Test creating coordinate from list [lat, lng]."""
        coord = Coordinate.from_input([38.8977, -77.0365])
        assert coord.lat == 38.8977
        assert coord.lng == -77.0365

    def test_from_dict(self):
        """Test creating coordinate from dict."""
        coord = Coordinate.from_input({"lat": 38.8977, "lng": -77.0365})
        assert coord.lat == 38.8977
        assert coord.lng == -77.0365
        assert coord.id is None

    def test_from_dict_with_id(self):
        """Test creating coordinate from dict with id."""
        coord = Coordinate.from_input({"lat": 38.8977, "lng": -77.0365, "id": "white_house"})
        assert coord.lat == 38.8977
        assert coord.lng == -77.0365
        assert coord.id == "white_house"

    def test_from_coordinate(self):
        """Test creating coordinate from another Coordinate object."""
        original = Coordinate(38.8977, -77.0365, "white_house")
        coord = Coordinate.from_input(original)
        assert coord is original

    def test_to_string_basic(self):
        """Test converting coordinate to string."""
        coord = Coordinate(38.8977, -77.0365)
        assert coord.to_string() == "38.8977,-77.0365"

    def test_to_string_with_id(self):
        """Test converting coordinate with id to string."""
        coord = Coordinate(38.8977, -77.0365, "white_house")
        assert coord.to_string() == "38.8977,-77.0365,white_house"

    def test_to_dict_basic(self):
        """Test converting coordinate to dict."""
        coord = Coordinate(38.8977, -77.0365)
        assert coord.to_dict() == {"lat": 38.8977, "lng": -77.0365}

    def test_to_dict_with_id(self):
        """Test converting coordinate with id to dict."""
        coord = Coordinate(38.8977, -77.0365, "white_house")
        assert coord.to_dict() == {"lat": 38.8977, "lng": -77.0365, "id": "white_house"}

    def test_str(self):
        """Test string representation."""
        coord = Coordinate(38.8977, -77.0365, "white_house")
        assert str(coord) == "38.8977,-77.0365,white_house"


# ──────────────────────────────────────────────────────────────────────────────
# Distance Method Tests
# ──────────────────────────────────────────────────────────────────────────────


def sample_distance_response():
    """Sample response for distance endpoint."""
    return {
        "origin": {
            "query": "38.8977,-77.0365,white_house",
            "location": [38.8977, -77.0365],
            "id": "white_house"
        },
        "mode": "straightline",
        "destinations": [
            {
                "query": "38.9072,-77.0369,capitol",
                "location": [38.9072, -77.0369],
                "id": "capitol",
                "distance_miles": 0.7,
                "distance_km": 1.1
            },
            {
                "query": "38.8895,-77.0353,monument",
                "location": [38.8895, -77.0353],
                "id": "monument",
                "distance_miles": 0.6,
                "distance_km": 0.9
            }
        ]
    }


def sample_distance_driving_response():
    """Sample response for distance endpoint with driving mode."""
    return {
        "origin": {
            "query": "38.8977,-77.0365",
            "location": [38.8977, -77.0365]
        },
        "mode": "driving",
        "destinations": [
            {
                "query": "38.9072,-77.0369",
                "location": [38.9072, -77.0369],
                "distance_miles": 1.2,
                "distance_km": 1.9,
                "duration_seconds": 294
            }
        ]
    }


class TestDistance:
    """Tests for the distance() method."""

    def test_distance_basic(self, client, httpx_mock):
        """Test basic distance calculation."""
        def response_callback(request):
            assert request.method == "GET"
            assert "/v1.9/distance" in str(request.url)
            return httpx.Response(200, json=sample_distance_response())

        httpx_mock.add_callback(callback=response_callback)

        response = client.distance(
            origin="38.8977,-77.0365,white_house",
            destinations=["38.9072,-77.0369,capitol", "38.8895,-77.0353,monument"]
        )

        assert isinstance(response, DistanceResponse)
        assert response.origin.id == "white_house"
        assert response.mode == "straightline"
        assert len(response.destinations) == 2
        assert response.destinations[0].id == "capitol"
        assert response.destinations[0].distance_miles == 0.7

    def test_distance_with_coordinate_objects(self, client, httpx_mock):
        """Test distance with Coordinate objects."""
        httpx_mock.add_callback(
            callback=lambda request: httpx.Response(200, json=sample_distance_response())
        )

        origin = Coordinate(38.8977, -77.0365, "white_house")
        destinations = [
            Coordinate(38.9072, -77.0369, "capitol"),
            Coordinate(38.8895, -77.0353, "monument")
        ]

        response = client.distance(origin=origin, destinations=destinations)

        assert isinstance(response, DistanceResponse)
        assert len(response.destinations) == 2

    def test_distance_with_tuples(self, client, httpx_mock):
        """Test distance with tuple coordinates."""
        httpx_mock.add_callback(
            callback=lambda request: httpx.Response(200, json=sample_distance_response())
        )

        response = client.distance(
            origin=(38.8977, -77.0365),
            destinations=[(38.9072, -77.0369), (38.8895, -77.0353)]
        )

        assert isinstance(response, DistanceResponse)

    def test_distance_driving_mode(self, client, httpx_mock):
        """Test distance with driving mode returns duration."""
        def response_callback(request):
            assert "mode=driving" in str(request.url)
            return httpx.Response(200, json=sample_distance_driving_response())

        httpx_mock.add_callback(callback=response_callback)

        response = client.distance(
            origin="38.8977,-77.0365",
            destinations=["38.9072,-77.0369"],
            mode=DISTANCE_MODE_DRIVING
        )

        assert response.mode == "driving"
        assert response.destinations[0].duration_seconds == 294

    def test_distance_haversine_mapped_to_straightline(self, client, httpx_mock):
        """Test that haversine mode is mapped to straightline."""
        def response_callback(request):
            assert "mode=straightline" in str(request.url)
            return httpx.Response(200, json=sample_distance_response())

        httpx_mock.add_callback(callback=response_callback)

        client.distance(
            origin="38.8977,-77.0365",
            destinations=["38.9072,-77.0369"],
            mode=DISTANCE_MODE_HAVERSINE
        )

    def test_distance_with_filters(self, client, httpx_mock):
        """Test distance with filter parameters."""
        def response_callback(request):
            url_str = str(request.url)
            assert "max_results=5" in url_str
            assert "max_distance=10" in url_str  # Changed from 10.0 due to URL encoding
            return httpx.Response(200, json=sample_distance_response())

        httpx_mock.add_callback(callback=response_callback)

        client.distance(
            origin="38.8977,-77.0365",
            destinations=["38.9072,-77.0369"],
            max_results=5,
            max_distance=10.0
        )

    def test_distance_with_sorting(self, client, httpx_mock):
        """Test distance with sorting parameters."""
        def response_callback(request):
            url_str = str(request.url)
            assert "order_by=duration" in url_str
            assert "sort=desc" in url_str
            return httpx.Response(200, json=sample_distance_response())

        httpx_mock.add_callback(callback=response_callback)

        client.distance(
            origin="38.8977,-77.0365",
            destinations=["38.9072,-77.0369"],
            order_by=DISTANCE_ORDER_BY_DURATION,
            sort_order=DISTANCE_SORT_DESC
        )


# ──────────────────────────────────────────────────────────────────────────────
# Distance Matrix Method Tests
# ──────────────────────────────────────────────────────────────────────────────


def sample_distance_matrix_response():
    """Sample response for distance-matrix endpoint."""
    return {
        "mode": "straightline",
        "results": [
            {
                "origin": {
                    "query": "38.8977,-77.0365",
                    "location": [38.8977, -77.0365],
                    "id": "origin1"
                },
                "destinations": [
                    {
                        "query": "38.8895,-77.0353",
                        "location": [38.8895, -77.0353],
                        "id": "dest1",
                        "distance_miles": 1.5,
                        "distance_km": 2.5
                    }
                ]
            },
            {
                "origin": {
                    "query": "38.9072,-77.0369",
                    "location": [38.9072, -77.0369],
                    "id": "origin2"
                },
                "destinations": [
                    {
                        "query": "38.8895,-77.0353",
                        "location": [38.8895, -77.0353],
                        "id": "dest1",
                        "distance_miles": 1.3,
                        "distance_km": 2.1
                    }
                ]
            }
        ]
    }


class TestDistanceMatrix:
    """Tests for the distance_matrix() method."""

    def test_distance_matrix_basic(self, client, httpx_mock):
        """Test basic distance matrix calculation."""
        def response_callback(request):
            assert request.method == "POST"
            body = json.loads(request.content)
            assert "origins" in body
            assert "destinations" in body
            assert body["mode"] == "straightline"
            return httpx.Response(200, json=sample_distance_matrix_response())

        httpx_mock.add_callback(callback=response_callback)

        response = client.distance_matrix(
            origins=[
                (38.8977, -77.0365, "origin1"),
                (38.9072, -77.0369, "origin2")
            ],
            destinations=[
                (38.8895, -77.0353, "dest1")
            ]
        )

        assert isinstance(response, DistanceMatrixResponse)
        assert response.mode == "straightline"
        assert len(response.results) == 2
        assert response.results[0].origin.id == "origin1"
        assert response.results[0].destinations[0].distance_miles == 1.5

    def test_distance_matrix_uses_object_format(self, client, httpx_mock):
        """Test that distance_matrix uses object format in POST body."""
        def response_callback(request):
            body = json.loads(request.content)
            # Origins and destinations should be dicts, not strings
            assert isinstance(body["origins"][0], dict)
            assert "lat" in body["origins"][0]
            assert "lng" in body["origins"][0]
            return httpx.Response(200, json=sample_distance_matrix_response())

        httpx_mock.add_callback(callback=response_callback)

        client.distance_matrix(
            origins=["38.8977,-77.0365,origin1"],
            destinations=["38.8895,-77.0353,dest1"]
        )

    def test_distance_matrix_preserves_ids(self, client, httpx_mock):
        """Test that IDs are preserved in request."""
        def response_callback(request):
            body = json.loads(request.content)
            assert body["origins"][0]["id"] == "origin1"
            assert body["destinations"][0]["id"] == "dest1"
            return httpx.Response(200, json=sample_distance_matrix_response())

        httpx_mock.add_callback(callback=response_callback)

        client.distance_matrix(
            origins=[Coordinate(38.8977, -77.0365, "origin1")],
            destinations=[Coordinate(38.8895, -77.0353, "dest1")]
        )


# ──────────────────────────────────────────────────────────────────────────────
# Distance Job Method Tests
# ──────────────────────────────────────────────────────────────────────────────


def sample_job_create_response():
    """Sample response for creating a distance job."""
    return {
        "id": 123,
        "identifier": "abc123def456",
        "status": "ENQUEUED",
        "name": "My Job",
        "created_at": "2025-01-15T12:00:00.000000Z",
        "origins_count": 2,
        "destinations_count": 2,
        "total_calculations": 4
    }


def sample_job_status_response():
    """Sample response for job status."""
    return {
        "data": {
            "id": 123,
            "identifier": "abc123def456",
            "name": "My Job",
            "status": "COMPLETED",
            "progress": 100,
            "download_url": "https://api.geocod.io/v1.9/distance-jobs/123/download",
            "total_calculations": 4,
            "calculations_completed": 4,
            "origins_count": 2,
            "destinations_count": 2,
            "created_at": "2025-01-15T12:00:00.000000Z"
        }
    }


def sample_jobs_list_response():
    """Sample response for listing jobs."""
    return {
        "data": [
            {
                "id": 123,
                "identifier": "abc123",
                "status": "COMPLETED",
                "name": "Job 1",
                "created_at": "2025-01-15T12:00:00.000000Z",
                "origins_count": 2,
                "destinations_count": 2,
                "total_calculations": 4
            },
            {
                "id": 124,
                "identifier": "def456",
                "status": "PROCESSING",
                "name": "Job 2",
                "created_at": "2025-01-15T13:00:00.000000Z",
                "origins_count": 3,
                "destinations_count": 3,
                "total_calculations": 9
            }
        ],
        "current_page": 1,
        "from": 1,
        "to": 2,
        "path": "/v1.9/distance-jobs",
        "per_page": 10
    }


class TestDistanceJobs:
    """Tests for distance job methods."""

    def test_create_job_with_coordinates(self, client, httpx_mock):
        """Test creating a distance job with coordinate lists."""
        def response_callback(request):
            assert request.method == "POST"
            body = json.loads(request.content)
            assert body["name"] == "My Job"
            assert isinstance(body["origins"], list)
            assert isinstance(body["destinations"], list)
            return httpx.Response(200, json=sample_job_create_response())

        httpx_mock.add_callback(callback=response_callback)

        response = client.create_distance_matrix_job(
            name="My Job",
            origins=[(38.8977, -77.0365), (38.9072, -77.0369)],
            destinations=[(38.8895, -77.0353), (39.2904, -76.6122)]
        )

        assert isinstance(response, DistanceJobResponse)
        assert response.id == 123
        assert response.status == "ENQUEUED"
        assert response.total_calculations == 4

    def test_create_job_with_list_ids(self, client, httpx_mock):
        """Test creating a distance job with list IDs."""
        def response_callback(request):
            body = json.loads(request.content)
            assert body["origins"] == 12345
            assert body["destinations"] == 67890
            return httpx.Response(200, json=sample_job_create_response())

        httpx_mock.add_callback(callback=response_callback)

        client.create_distance_matrix_job(
            name="My Job",
            origins=12345,
            destinations=67890
        )

    def test_create_job_with_callback_url(self, client, httpx_mock):
        """Test creating a job with callback URL."""
        def response_callback(request):
            body = json.loads(request.content)
            assert body["callback_url"] == "https://example.com/webhook"
            return httpx.Response(200, json=sample_job_create_response())

        httpx_mock.add_callback(callback=response_callback)

        client.create_distance_matrix_job(
            name="My Job",
            origins=[(38.8977, -77.0365)],
            destinations=[(38.8895, -77.0353)],
            callback_url="https://example.com/webhook"
        )

    def test_job_status(self, client, httpx_mock):
        """Test getting job status."""
        httpx_mock.add_callback(
            callback=lambda request: httpx.Response(200, json=sample_job_status_response())
        )

        response = client.distance_matrix_job_status(123)

        assert response.id == 123
        assert response.status == "COMPLETED"
        assert response.progress == 100

    def test_list_jobs(self, client, httpx_mock):
        """Test listing jobs."""
        httpx_mock.add_callback(
            callback=lambda request: httpx.Response(200, json=sample_jobs_list_response())
        )

        response = client.distance_matrix_jobs()

        assert response.current_page == 1
        assert len(response.data) == 2

    def test_get_job_results(self, client, httpx_mock):
        """Test downloading job results."""
        httpx_mock.add_callback(
            callback=lambda request: httpx.Response(
                200,
                json=sample_distance_matrix_response(),
                headers={"content-type": "application/json"}
            )
        )

        response = client.get_distance_matrix_job_results(123)

        assert isinstance(response, DistanceMatrixResponse)
        assert len(response.results) == 2

    def test_delete_job(self, client, httpx_mock):
        """Test deleting a job."""
        def response_callback(request):
            assert request.method == "DELETE"
            return httpx.Response(204)

        httpx_mock.add_callback(callback=response_callback)

        # Should not raise
        client.delete_distance_matrix_job(123)


# ──────────────────────────────────────────────────────────────────────────────
# Geocode with Distance Tests
# ──────────────────────────────────────────────────────────────────────────────


def sample_geocode_with_distance_response():
    """Sample geocode response with distance data."""
    return {
        "results": [{
            "address_components": {
                "number": "1600",
                "street": "Pennsylvania",
                "suffix": "Ave",
                "city": "Washington",
                "state": "DC",
                "zip": "20500"
            },
            "formatted_address": "1600 Pennsylvania Ave NW, Washington, DC 20500",
            "location": {"lat": 38.8977, "lng": -77.0365},
            "accuracy": 1,
            "accuracy_type": "rooftop",
            "source": "DC",
            "destinations": [
                {
                    "query": "38.9072,-77.0369",
                    "location": [38.9072, -77.0369],
                    "distance_miles": 0.7,
                    "distance_km": 1.1
                }
            ]
        }]
    }


class TestGeocodeWithDistance:
    """Tests for geocode() with distance parameters."""

    def test_geocode_with_destinations(self, client, httpx_mock):
        """Test geocode with destination parameter."""
        def response_callback(request):
            url_str = str(request.url)
            assert "/v1.9/geocode" in url_str
            assert "destinations%5B%5D" in url_str or "destinations[]" in url_str.replace("%5B", "[").replace("%5D", "]")
            return httpx.Response(200, json=sample_geocode_with_distance_response())

        httpx_mock.add_callback(callback=response_callback)

        response = client.geocode(
            "1600 Pennsylvania Ave NW, Washington DC",
            destinations=["38.9072,-77.0369"]
        )

        assert len(response.results) == 1

    def test_geocode_with_distance_mode(self, client, httpx_mock):
        """Test geocode with distance mode parameter."""
        def response_callback(request):
            url_str = str(request.url)
            assert "/v1.9/geocode" in url_str
            assert "distance_mode=driving" in url_str
            return httpx.Response(200, json=sample_geocode_with_distance_response())

        httpx_mock.add_callback(callback=response_callback)

        client.geocode(
            "1600 Pennsylvania Ave NW, Washington DC",
            destinations=["38.9072,-77.0369"],
            distance_mode=DISTANCE_MODE_DRIVING
        )

    def test_geocode_with_distance_units(self, client, httpx_mock):
        """Test geocode with distance units parameter."""
        def response_callback(request):
            url_str = str(request.url)
            assert "/v1.9/geocode" in url_str
            assert "distance_units=km" in url_str
            return httpx.Response(200, json=sample_geocode_with_distance_response())

        httpx_mock.add_callback(callback=response_callback)

        client.geocode(
            "1600 Pennsylvania Ave NW, Washington DC",
            destinations=["38.9072,-77.0369"],
            distance_units=DISTANCE_UNITS_KM
        )


# ──────────────────────────────────────────────────────────────────────────────
# Reverse with Distance Tests
# ──────────────────────────────────────────────────────────────────────────────


class TestReverseWithDistance:
    """Tests for reverse() with distance parameters."""

    def test_reverse_with_destinations(self, client, httpx_mock):
        """Test reverse geocode with destination parameter."""
        def response_callback(request):
            url_str = str(request.url)
            assert "/v1.9/reverse" in url_str
            assert "destinations%5B%5D" in url_str or "destinations[]" in url_str.replace("%5B", "[").replace("%5D", "]")
            return httpx.Response(200, json=sample_geocode_with_distance_response())

        httpx_mock.add_callback(callback=response_callback)

        response = client.reverse(
            "38.8977,-77.0365",
            destinations=["38.9072,-77.0369"]
        )

        assert len(response.results) == 1

    def test_reverse_with_distance_mode(self, client, httpx_mock):
        """Test reverse geocode with distance mode parameter."""
        def response_callback(request):
            url_str = str(request.url)
            assert "/v1.9/reverse" in url_str
            assert "distance_mode=straightline" in url_str
            return httpx.Response(200, json=sample_geocode_with_distance_response())

        httpx_mock.add_callback(callback=response_callback)

        client.reverse(
            (38.8977, -77.0365),
            destinations=[(38.9072, -77.0369)],
            distance_mode=DISTANCE_MODE_STRAIGHTLINE
        )


# ──────────────────────────────────────────────────────────────────────────────
# Constants Tests
# ──────────────────────────────────────────────────────────────────────────────


class TestConstants:
    """Tests for distance constants."""

    def test_mode_constants(self):
        """Test distance mode constants."""
        assert DISTANCE_MODE_STRAIGHTLINE == "straightline"
        assert DISTANCE_MODE_DRIVING == "driving"
        assert DISTANCE_MODE_HAVERSINE == "haversine"

    def test_units_constants(self):
        """Test distance units constants."""
        assert DISTANCE_UNITS_MILES == "miles"
        assert DISTANCE_UNITS_KM == "km"

    def test_order_by_constants(self):
        """Test order by constants."""
        assert DISTANCE_ORDER_BY_DISTANCE == "distance"
        assert DISTANCE_ORDER_BY_DURATION == "duration"

    def test_sort_constants(self):
        """Test sort constants."""
        assert DISTANCE_SORT_ASC == "asc"
        assert DISTANCE_SORT_DESC == "desc"
