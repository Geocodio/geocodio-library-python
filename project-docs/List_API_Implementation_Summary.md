# List API Implementation Summary

## Overview

This document summarizes the implementation of the List API functionality in the Geocodio Python client. The List API allows users to manage lists of addresses or coordinates for batch processing.

## Changes Made

### 1. Added List API Models

Added the following data models to `src/geocodio/models.py`:

- `ListItem`: Represents an item in a list, with properties like id, query, created_at, updated_at, geocoded_at, and result.
- `GeocodioList`: Represents a list of addresses or coordinates, with properties like id, name, description, created_at, updated_at, item_count, and items.
- `ListResponse`: Represents the top-level structure returned by list API methods, with properties like lists, list, item, and items.

### 2. Implemented List API Methods

Added the following methods to the `GeocodioClient` class in `src/geocodio/client.py`:

- `create_list()`: Create a new list
- `get_lists()`: Retrieve all lists
- `get_list()`: Retrieve a list by ID
- `update_list()`: Update a list
- `delete_list()`: Delete a list
- `add_items_to_list()`: Add items to a list
- `remove_items_from_list()`: Remove items from a list
- `geocode_list()`: Geocode all items in a list

Also added helper methods for parsing the responses from the List API:
- `_parse_list_response()`: Parse a response from the List API
- `_parse_list_item()`: Parse a list item from the List API

### 3. Added Tests for List API

Created a new test file `tests/test_lists.py` with tests for all List API methods:

- `test_create_list`: Tests creating a new list
- `test_get_lists`: Tests retrieving all lists
- `test_get_list`: Tests retrieving a list by ID
- `test_update_list`: Tests updating a list
- `test_delete_list`: Tests deleting a list
- `test_add_items_to_list`: Tests adding items to a list
- `test_remove_items_from_list`: Tests removing items from a list
- `test_geocode_list`: Tests geocoding all items in a list

### 4. Updated Documentation

Updated the README.md file to include documentation for the List API functionality, with examples of how to use all the List API methods.

### 5. Created Example Script

Created an example script `examples/list_api_example.py` that demonstrates a complete workflow for using the List API, from creating a list to deleting it.

## List API Endpoints

The List API uses the following endpoints:

- `POST /v1.8/lists`: Create a new list
- `GET /v1.8/lists`: Retrieve all lists
- `GET /v1.8/lists/{list_id}`: Retrieve a specific list
- `PUT /v1.8/lists/{list_id}`: Update a list
- `DELETE /v1.8/lists/{list_id}`: Delete a list
- `POST /v1.8/lists/{list_id}/items`: Add items to a list
- `DELETE /v1.8/lists/{list_id}/items`: Remove items from a list
- `GET /v1.8/lists/{list_id}/geocode`: Geocode all items in a list

## Usage Example

```python
from geocodio import

GeocodioClient

# Initialize the client with your API key
client = GeocodioClient(
    "YOUR_API_KEY")

# Create a new list
new_list = client.create_list(
    format_="{{A}}")

# Get a specific list
list_id = new_list.list.id
list_details = client.get_list(
    list_id)

# Geocode all items in a list
geocoded_list = client.geocode_list(
    list_id=list_id,
    fields=[
        "timezone",
        "cd"]
)

# Access geocoded results
for item in geocoded_list.list.items:
    if item.result:
        print(
            f"{item.query} => {item.result.formatted_address}")
        print(
            f"Location: {item.result.location.lat}, {item.result.location.lng}")
```

## Next Steps

The List API implementation is now complete and ready for use. Users can manage lists of addresses or coordinates and geocode them in batch using the new List API methods.

For future enhancements, consider:

1. Adding pagination support for retrieving large lists
2. Implementing rate limiting for List API requests
3. Adding support for filtering and sorting lists
4. Implementing caching for frequently accessed lists