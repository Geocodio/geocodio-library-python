"""
The API reports non-fatal advisories under a `_warnings` key -- an
unrecognized field name, a superseded API version, an append that was
skipped. These tests lock in that the key is parsed onto every response
shape, so a future model refactor cannot silently drop it.

The shapes are the ones the OpenAPI specification models (see the `Warnings`
schema): top-level on single geocode/reverse, per result, per batch item,
and on the lists and distance-jobs responses.
"""

import pytest

from geocodio.exceptions import (
    AuthenticationError,
    GeocodioError,
    InvalidRequestError,
)

FIELD_WARNING = "The field congress is not recognized. Did you mean cd?"
VERSION_WARNING = (
    "There is a newer API version available, please consider upgrading to v2."
)
FIELDS_FORMAT_WARNING = (
    "The fields parameter should contain a comma-separated list of fields "
    "instead of an array"
)
FFIEC_WARNING = "ffiec field was skipped since result is not street-level"


def result(formatted_address: str, **extra) -> dict:
    return {
        "address_components": {"city": "Arlington", "country": "US"},
        "formatted_address": formatted_address,
        "location": {"lat": 38.886665, "lng": -77.094733},
        "accuracy": 1,
        "accuracy_type": "rooftop",
        "source": "Arlington",
        **extra,
    }


# ──────────────────────────────────────────────────────────────────────────────
# Geocoding responses
# ──────────────────────────────────────────────────────────────────────────────


def test_single_forward_geocode_warnings(client, httpx_mock):
    httpx_mock.add_response(
        json={
            "results": [result("1109 N Highland St, Arlington, VA 22201")],
            "_warnings": [FIELD_WARNING],
        }
    )

    response = client.geocode("1109 N Highland St, Arlington VA", fields=["congress"])

    assert response.warnings == [FIELD_WARNING]
    assert response.results[0].warnings == []


def test_single_reverse_geocode_warnings(client, httpx_mock):
    warning = (
        "Ignoring parameter zipcode as it was not expected. Did you mean postal_code?"
    )
    httpx_mock.add_response(
        json={
            "results": [result("1109 N Highland St, Arlington, VA 22201")],
            "_warnings": [warning],
        }
    )

    response = client.reverse("38.886665,-77.094733")

    assert response.warnings == [warning]


def test_per_result_warnings(client, httpx_mock):
    httpx_mock.add_response(
        json={
            "results": [
                result(
                    "Arlington, VA 22201",
                    accuracy_type="place",
                    _warnings=[FFIEC_WARNING],
                )
            ],
        }
    )

    response = client.geocode("22201", fields=["ffiec"])

    assert response.warnings == []
    assert response.results[0].warnings == [FFIEC_WARNING]


def test_batch_forward_geocode_warnings(client, httpx_mock):
    httpx_mock.add_response(
        json={
            "results": [
                {
                    "query": "1109 N Highland St, Arlington VA",
                    "response": {
                        "results": [
                            result(
                                "1109 N Highland St, Arlington, VA 22201",
                                _warnings=[FFIEC_WARNING],
                            )
                        ],
                        "_warnings": [FIELD_WARNING],
                    },
                },
                {
                    "query": "525 University Ave, Toronto, ON, Canada",
                    "response": {
                        "results": [result("525 University Ave, Toronto, ON M5G")],
                        "_warnings": [FIELD_WARNING],
                    },
                },
            ]
        }
    )

    response = client.geocode(
        [
            "1109 N Highland St, Arlington VA",
            "525 University Ave, Toronto, ON, Canada",
        ],
        fields=["congress"],
    )

    # Per query: that query's warnings, then the result's own
    assert response.results[0].warnings == [FIELD_WARNING, FFIEC_WARNING]
    assert response.results[1].warnings == [FIELD_WARNING]
    # Across the batch: each warning once
    assert response.warnings == [FIELD_WARNING]


def test_batch_reverse_geocode_warnings(client, httpx_mock):
    httpx_mock.add_response(
        json={
            "results": [
                {
                    "query": "35.9746000,-77.9658000",
                    "response": {
                        "results": [result("101 W Washington St, Nashville, NC 27856")],
                        "_warnings": [VERSION_WARNING],
                    },
                }
            ]
        }
    )

    response = client.reverse(["35.9746000,-77.9658000"])

    assert response.results[0].warnings == [VERSION_WARNING]
    assert response.warnings == [VERSION_WARNING]


def test_batch_warnings_kept_for_unmatched_query(client, httpx_mock):
    httpx_mock.add_response(
        json={
            "results": [
                {
                    "query": "not an address",
                    "response": {"results": [], "_warnings": [FIELD_WARNING]},
                },
            ]
        }
    )

    response = client.geocode(["not an address"], fields=["congress"])

    assert response.results[0].matched is False
    assert response.results[0].warnings == [FIELD_WARNING]
    assert response.warnings == [FIELD_WARNING]


def test_no_warnings_when_api_sends_none(client, httpx_mock):
    httpx_mock.add_response(
        json={"results": [result("1109 N Highland St, Arlington, VA 22201")]}
    )

    response = client.geocode("1109 N Highland St, Arlington VA")

    assert response.warnings == []
    assert response.results[0].warnings == []
    assert "_warnings" not in response.raw


def test_warnings_remain_on_raw_payload(client, httpx_mock):
    httpx_mock.add_response(
        json={
            "results": [result("1109 N Highland St, Arlington, VA 22201")],
            "_warnings": [FIELD_WARNING],
        }
    )

    response = client.geocode("1109 N Highland St, Arlington VA", fields=["congress"])

    assert response.raw["_warnings"] == [FIELD_WARNING]


# ──────────────────────────────────────────────────────────────────────────────
# Lists responses
# ──────────────────────────────────────────────────────────────────────────────


def test_create_list_warnings(client, httpx_mock):
    warning = (
        "The following field was not recognized and has been skipped: "
        "congressional_district"
    )
    httpx_mock.add_response(
        json={
            "id": 42,
            "file": {"filename": "inline.csv"},
            "status": {"state": "PROCESSING"},
            "_warnings": [warning],
        }
    )

    response = client.create_list(
        file="address\n1109 N Highland St, Arlington VA",
        filename="inline.csv",
        fields=["congressional_district"],
    )

    assert response.warnings == [warning]


def test_get_list_warnings(client, httpx_mock):
    httpx_mock.add_response(
        json={
            "id": 42,
            "file": {"filename": "inline.csv"},
            "status": {"state": "COMPLETED"},
            "_warnings": [FIELDS_FORMAT_WARNING],
        }
    )

    assert client.get_list("42").warnings == [FIELDS_FORMAT_WARNING]


def test_get_lists_warnings(client, httpx_mock):
    httpx_mock.add_response(
        json={
            "current_page": 1,
            "data": [],
            "from": 0,
            "to": 0,
            "path": "/v2/lists",
            "per_page": 15,
            "first_page_url": "/v2/lists?page=1",
            "_warnings": [FIELDS_FORMAT_WARNING],
        }
    )

    assert client.get_lists().warnings == [FIELDS_FORMAT_WARNING]


# ──────────────────────────────────────────────────────────────────────────────
# Distance matrix job responses
# ──────────────────────────────────────────────────────────────────────────────


def test_create_distance_matrix_job_warnings(client, httpx_mock):
    httpx_mock.add_response(
        json={
            "id": 123,
            "identifier": "dmj_abc123",
            "status": "ENQUEUED",
            "name": "Store coverage",
            "created_at": "2026-09-25T12:00:00.000000Z",
            "origins_count": 1,
            "destinations_count": 1,
            "total_calculations": 1,
            "_warnings": [VERSION_WARNING],
        }
    )

    response = client.create_distance_matrix_job(
        name="Store coverage",
        origins=[(38.886665, -77.094733)],
        destinations=[(38.897675, -77.036547)],
    )

    assert response.warnings == [VERSION_WARNING]


def test_distance_matrix_job_status_warnings(client, httpx_mock):
    # Warnings sit beside the nested "data" key, not inside it
    httpx_mock.add_response(
        json={
            "data": {"id": 123, "identifier": "dmj_abc123", "status": "COMPLETED"},
            "_warnings": [FIELDS_FORMAT_WARNING],
        }
    )

    response = client.distance_matrix_job_status("dmj_abc123")

    assert response.status == "COMPLETED"
    assert response.warnings == [FIELDS_FORMAT_WARNING]


def test_distance_matrix_jobs_warnings(client, httpx_mock):
    httpx_mock.add_response(
        json={
            "current_page": 1,
            "data": [],
            "from": 0,
            "to": 0,
            "path": "/v2/distance-jobs",
            "per_page": 10,
            "first_page_url": "/v2/distance-jobs?page=1",
            "_warnings": [FIELDS_FORMAT_WARNING],
        }
    )

    assert client.distance_matrix_jobs().warnings == [FIELDS_FORMAT_WARNING]


# ──────────────────────────────────────────────────────────────────────────────
# Error responses
# ──────────────────────────────────────────────────────────────────────────────


def test_error_response_warnings(client, httpx_mock):
    httpx_mock.add_response(
        status_code=422,
        json={
            "error": "Could not geocode address. Postal code or city required.",
            "_warnings": [FIELD_WARNING],
        },
    )

    with pytest.raises(InvalidRequestError) as exc_info:
        client.geocode("1109 N Highland St", fields=["congress"])

    assert exc_info.value.warnings == [FIELD_WARNING]
    assert exc_info.value.detail.warnings == [FIELD_WARNING]


def test_error_response_without_warnings(client, httpx_mock):
    httpx_mock.add_response(status_code=403, json={"error": "Invalid API key"})

    with pytest.raises(AuthenticationError) as exc_info:
        client.geocode("1109 N Highland St, Arlington VA")

    assert exc_info.value.warnings == []


def test_non_json_error_response_has_no_warnings(client, httpx_mock):
    httpx_mock.add_response(status_code=502, text="<html>Bad Gateway</html>")

    with pytest.raises(GeocodioError) as exc_info:
        client.geocode("1109 N Highland St, Arlington VA")

    assert exc_info.value.warnings == []


def test_error_constructed_directly_has_no_warnings():
    assert GeocodioError("boom").warnings == []
    assert GeocodioError("boom", warnings=[FIELD_WARNING]).warnings == [FIELD_WARNING]
