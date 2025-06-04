"""
End-to-end tests for the List API functionality.
These tests require a valid GEOCODIO_API_KEY environment variable.
"""

import os
import pytest
import time
from unittest.mock import patch
from geocodio import GeocodioClient
from geocodio.models import ListResponse, PaginatedResponse
from geocodio.exceptions import GeocodioServerError


@pytest.fixture
def client():
    """Create a client using the GEOCODIO_API_KEY environment variable."""
    api_key = os.getenv("GEOCODIO_API_KEY")
    if not api_key:
        pytest.skip("GEOCODIO_API_KEY environment variable not set")
    return GeocodioClient(api_key)


@pytest.fixture
def list_response(client):
    """Create a test list and clean it up after the test."""
    # Create a test list
    new_list: ListResponse = client.create_list(
        format_="{{A}}",
        file="Address\n1600 Pennsylvania Ave, Washington, DC\n1 Infinite Loop, Cupertino, CA",
        filename="test_list.csv",
    )
    return new_list


def wait_for_list_processed(client, list_id, timeout=120):
    """Wait until the list is processed or timeout (in seconds)."""
    start = time.time()
    while time.time() - start < timeout:
        list_response = client.get_list(list_id)
        list_processing_state = list_response.status.get('state')
        # @TODO: use consts for these state values.
        # @TODO: add computed property to ListResponse for processing state.
        if list_processing_state == "COMPLETED":
            print()  # Finish the dots line
            return list_response
        elif list_processing_state == "FAILED":
            print()  # Finish the dots line
            raise RuntimeError(f"List {list_id} failed to process.")
        elif list_processing_state == "PROCESSING":
            print("=>", end="", flush=True)
        time.sleep(2)
    print()
    raise TimeoutError(f"List {list_id} did not process in {timeout} seconds.")


def test_create_list(client):
    """
    Test creating a list with GeocodioClient.create_list()
    :param client: GeocodioClient instance
    """
    new_list = client.create_list(file="Zip\n20003\n20001", filename="test_list.csv")

    assert isinstance(new_list, ListResponse)


def test_get_list_status(client, list_response):
    """
    Test retrieving the status of a list with GeocodioClient.get_list_status()
    :param client: GeocodioClient instance
    :param list_response: List object created in the fixture
    """
    # Get the status of the test list
    response = client.get_list(list_response.id)

    # Verify the response
    assert isinstance(response, ListResponse)
    assert response.status is not None
    assert response.file is not None
    assert response.expires_at is not None


def test_get_lists(client, list_response):
    """
    Test retrieving all lists and ensure the test list is present.
    """
    response = client.get_lists()

    # verify we got a paginated response with at least one entry
    assert isinstance(response, PaginatedResponse)
    assert response.data, "Expected at least one list in the response"

    # check that our test list ID is in the returned list IDs
    returned_ids = [item.id for item in response.data]
    assert list_response.id in returned_ids


def test_delete_list(client, list_response):
    list_id = list_response.id

    # Delete the list
    client.delete_list(list_id)

    # Verify the list was deleted by checking that it's not in the list of lists
    all_lists = client.get_lists()

    # extract all the unique list IDs from the response
    all_list_responses = all_lists.data
    all_list_ids = {list_obj.id for list_obj in all_list_responses}

    if list_id in all_list_ids:
        raise AssertionError(f"List with ID {list_id} was not deleted successfully. It still exists in the list of lists.")
    else:
        print(f"List with ID {list_id} was deleted successfully and is no longer in the list of lists.")


def test_download_csv_to_file(client, tmp_path):
    """Test downloading a CSV and saving it to a file (E2E)."""
    new_list = client.create_list(
        format_="{{A}}",
        file="Zip\n20003\n20001",
        filename="test_list.csv",
    )
    wait_for_list_processed(client, new_list.id)
    file_path = tmp_path / "test_list.csv"
    result = client.download(list_id=new_list.id, filename=str(file_path))

    assert result == str(file_path)
    assert file_path.exists()
    content = file_path.read_text()
    assert "Zip" in content
    assert "20003" in content
    assert "20001" in content


def test_download_csv_as_bytes(client):
    """Test downloading a CSV and returning it as bytes (E2E)."""
    new_list = client.create_list(
        format_="{{A}}",
        file="Zip\n20003\n20001",
        filename="test_list.csv",
    )
    wait_for_list_processed(client, new_list.id)
    result = client.download(list_id=new_list.id)
    assert isinstance(result, bytes)
    assert b"Zip" in result
    assert b"20003" in result
    assert b"20001" in result


def test_download_list_still_processing(client):
    """Test handling a list that is still processing (E2E)."""
    new_list = client.create_list(
        format_="{{A}}",
        file="Zip\n20003\n20001",
        filename="test_list.csv",
    )
    # Immediately try to download before processing is done
    with pytest.raises(GeocodioServerError):
        client.download(list_id=new_list.id)


def test_download_error_parsing_json(client, monkeypatch):
    """Test handling an error when JSON parsing fails (E2E)."""
    fake_list_id = "nonexistent-list-id-xyz"
    orig_request = client._http.request

    def broken_json(*args, **kwargs):
        resp = orig_request(*args, **kwargs)
        resp.json = lambda: (_ for _ in ()).throw(ValueError("Invalid JSON"))
        return resp

    monkeypatch.setattr(client._http, "request", broken_json)
    with pytest.raises(GeocodioServerError):
        client.download(list_id=fake_list_id)
