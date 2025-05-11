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
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. Install development dependencies:
    ```bash
    pip install -e ".[dev]"
    ```

Usage
-----

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