# geocodio

The official Python client for the Geocodio API.

Features
--------

- Forward geocoding of single addresses or in batches (up to 10,000 lookups).
- Reverse geocoding of coordinates (single or batch).
- Append additional data fields (e.g. congressional districts, timezone, census data).
- Automatic parsing of address components.
- Simple exception handling for authentication, data, and server errors.

Installation
------------

Install via pip:

    pip install geocodio

Development Installation
-----------------------

1. Clone the repository:
    ```bash
    git clone https://github.com/geocodio/geocodio-library-python.git
    cd geocodio-library-python
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m .venv venv
    source .venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install development dependencies:
    ```bash
    pip install .
    pip install .[dev]
    pip install -r pyproject.toml
    ```

Usage
-----

### Geocoding

```python
from geocodio import GeocodioClient

# Initialize the client with your API key
client = GeocodioClient("YOUR_API_KEY")

# Single forward geocode
response = client.geocode("123 Anywhere St, Chicago, IL")
print(response)

# Batch forward geocode
addresses = [
    "123 Anywhere St, Chicago, IL",
    "456 Oak St, Los Angeles, CA"
]
batch_response = client.geocode(addresses)
print(batch_response)

# Single reverse geocode
rev = client.reverse("38.9002898,-76.9990361")
print(rev)

# Append additional fields
data = client.geocode(
    "123 Anywhere St, Chicago, IL",
    fields=["cd", "timezone"]
)
print(data)
```

### List API

The List API allows you to manage lists of addresses or coordinates for batch processing.

```python
from geocodio import GeocodioClient

# Initialize the client with your API key
client = GeocodioClient("YOUR_API_KEY")

# Create a new list
new_list = client.create_list(
    name="My Addresses",
    description="A list of addresses to geocode",
    items=[
        "1600 Pennsylvania Ave, Washington, DC",
        "1 Infinite Loop, Cupertino, CA"
    ]
)
print(new_list)

# Get all lists
lists = client.get_lists()
print(lists)

# Get a specific list
list_id = new_list.list.id
list_details = client.get_list(list_id)
print(list_details)

# Update a list
updated_list = client.update_list(
    list_id=list_id,
    name="Updated List Name",
    description="Updated description"
)
print(updated_list)

# Add items to a list
added_items = client.add_items_to_list(
    list_id=list_id,
    items=[
        "123 Anywhere St, Chicago, IL",
        "456 Oak St, Los Angeles, CA"
    ]
)
print(added_items)

# Geocode all items in a list
geocoded_list = client.geocode_list(
    list_id=list_id,
    fields=["timezone", "cd"]
)
print(geocoded_list)

# Remove items from a list
item_ids = [item.id for item in added_items.items]
client.remove_items_from_list(
    list_id=list_id,
    item_ids=item_ids
)

# Delete a list
client.delete_list(list_id)
```

Error Handling
--------------

- `GeocodioAuthError` is raised for authentication failures (HTTP 403).
- `GeocodioDataError` is raised for invalid requests (HTTP 422).
- `GeocodioServerError` is raised for server-side errors (HTTP 5xx).

Documentation
-------------

Full documentation is available at <https://www.geocod.io/docs/?python>.

Contributing
------------

Contributions are welcome! Please open issues and pull requests on GitHub.

Issues: <https://github.com/geocodio/geocodio-library-python/issues>

License
-------

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
