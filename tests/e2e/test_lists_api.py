"""
End-to-end tests for the List API functionality.
These tests require a valid GEOCODIO_API_KEY environment variable.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
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


def test_create_list(client):
    """
    Test creating a list with GeocodioClient.create_list()
    :param client: GeocodioClient instance
    """
    # generate CSV rows with addresses. super simple example:   -F "file"=$'Zip\n20003\n20001
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


@pytest.fixture
def client():
    return GeocodioClient(api_key="test_api_key")

@patch("httpx.Client.request")
def test_download_csv_to_file(mock_request, client, tmp_path):
    """Test downloading a CSV and saving it to a file."""
    mock_response = MagicMock()
    mock_response.headers = {"content-type": "text/csv"}
    mock_response.content = b"address,city,state,zip\n123 Main St,Anytown,NY,12345"
    mock_request.return_value = mock_response

    file_path = tmp_path / "test_list.csv"
    result = client.download(list_id="12345", filename=str(file_path))

    assert result == str(file_path)
    assert file_path.exists()
    assert file_path.read_text() == "address,city,state,zip\n123 Main St,Anytown,NY,12345"

@patch("httpx.Client.request")
def test_download_csv_as_bytes(mock_request, client):
    """Test downloading a CSV and returning it as bytes."""
    mock_response = MagicMock()
    mock_response.headers = {"content-type": "text/csv"}
    mock_response.content = b"address,city,state,zip\n123 Main St,Anytown,NY,12345"
    mock_request.return_value = mock_response

    result = client.download(list_id="12345")

    assert result == b"address,city,state,zip\n123 Main St,Anytown,NY,12345"

@patch("httpx.Client.request")
def test_download_list_still_processing(mock_request, client):
    """Test handling a list that is still processing."""
    mock_response = MagicMock()
    mock_response.headers = {"content-type": "application/json"}
    mock_response.json.return_value = {"message": "List is still processing", "success": False}
    mock_request.return_value = mock_response

    with pytest.raises(GeocodioServerError, match="List is still processing"):
        client.download(list_id="12345")

@patch("httpx.Client.request")
def test_download_error_parsing_json(mock_request, client):
    """Test handling an error when JSON parsing fails."""
    mock_response = MagicMock()
    mock_response.headers = {"content-type": "application/json"}
    mock_response.json.side_effect = ValueError("Invalid JSON")
    mock_request.return_value = mock_response

    with pytest.raises(GeocodioServerError, match="Failed to download list and could not parse error message"):
        client.download(list_id="12345")