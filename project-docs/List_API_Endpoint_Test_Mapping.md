# List API Endpoint to Test Mapping

This document maps the Geocodio List API endpoints to the client methods and test methods in the Python client.

## Mapping Table

| API Endpoint | HTTP Method | Client Method | Test Method | Description |
|--------------|-------------|---------------|-------------|-------------|
| `/v1.8/lists` | POST | `create_list()` | `test_create_list()` | Create a new list |
| `/v1.8/lists` | GET | `get_lists()` | `test_get_lists()` | Retrieve all lists |
| `/v1.8/lists/{list_id}` | GET | `get_list()` | `test_get_list()` | Retrieve a specific list |
| `/v1.8/lists/{list_id}` | PUT | `update_list()` | `test_update_list()` | Update a list |
| `/v1.8/lists/{list_id}` | DELETE | `delete_list()` | `test_delete_list()` | Delete a list |
| `/v1.8/lists/{list_id}/items` | POST | `add_items_to_list()` | `test_add_items_to_list()` | Add items to a list |
| `/v1.8/lists/{list_id}/items` | DELETE | `remove_items_from_list()` | `test_remove_items_from_list()` | Remove items from a list |
| `/v1.8/lists/{list_id}/geocode` | GET | `geocode_list()` | `test_geocode_list()` | Geocode all items in a list |

## Test Coverage

All List API endpoints are covered by end-to-end tests in the `tests/e2e/test_lists_api.py` file. These tests make real API calls to the Geocodio API and verify the responses.

The tests use a `client` fixture that creates a `GeocodioClient` instance using the API key from the environment variable, and a `test_list` fixture that creates a test list for use in the tests and cleans it up afterward.

## Test Implementation Details

Each test follows a similar pattern:
1. Call the client method with appropriate parameters
2. Verify the response structure and content
3. Clean up any created resources

For example, the `test_create_list()` method:
1. Calls `client.create_list()` with a name and description
2. Verifies that the response contains a list with the correct name and description
3. Cleans up by deleting the created list

This ensures that the tests are isolated and don't leave test data in the API.