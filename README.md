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
    pip install -e .
    pip install -r requirements-dev.txt
    ```

Usage
-----

### Geocoding

```python
from geocodio import GeocodioClient

# Initialize the client with your API key
client = GeocodioClient("YOUR_API_KEY")

# Single forward geocode
response = client.geocode("1600 Pennsylvania Ave, Washington, DC")
print(response.results[0].formatted_address)

# Batch forward geocode
addresses = [
    "1600 Pennsylvania Ave, Washington, DC",
    "1 Infinite Loop, Cupertino, CA"
]
batch_response = client.geocode(addresses)
for result in batch_response.results:
    print(result.formatted_address)

# Single reverse geocode
rev = client.reverse("38.9002898,-76.9990361")
print(rev.results[0].formatted_address)

# Append additional fields
data = client.geocode(
    "1600 Pennsylvania Ave, Washington, DC",
    fields=["cd", "timezone"]
)
print(data.results[0].fields.timezone.name if data.results[0].fields.timezone else "No timezone data")
```

### List API

The List API allows you to manage lists of addresses or coordinates for batch processing.

```python
from geocodio import GeocodioClient

# Initialize the client with your API key
client = GeocodioClient("YOUR_API_KEY")

# Get all lists
lists = client.get_lists()
print(f"Found {len(lists.data)} lists")

# Create a new list from a file
with open("addresses.csv", "rb") as f:
    new_list = client.create_list(
        file=f,
        filename="addresses.csv",
        direction="forward"
    )
print(f"Created list: {new_list.id}")

# Get a specific list
list_details = client.get_list(new_list.id)
print(f"List status: {list_details.status}")

# Download a completed list
if list_details.status and list_details.status.get("state") == "COMPLETED":
    file_content = client.download(new_list.id, "downloaded_results.csv")
    print("List downloaded successfully")

# Delete a list
client.delete_list(new_list.id)
```

Error Handling
--------------

```python
from geocodio import GeocodioClient, AuthenticationError, InvalidRequestError

try:
    client = GeocodioClient("INVALID_API_KEY")
    response = client.geocode("1600 Pennsylvania Ave, Washington, DC")
except AuthenticationError as e:
    print(f"Authentication failed: {e}")

try:
    client = GeocodioClient("YOUR_API_KEY")
    response = client.geocode("")  # Empty address
except InvalidRequestError as e:
    print(f"Invalid request: {e}")
```

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

CI & Publishing
---------------

- CI runs unit tests and linting on every push. E2E tests run if `GEOCODIO_API_KEY` is set as a secret.
- PyPI publishing workflow supports both TestPyPI and PyPI. See `.github/workflows/publish.yml`.
- Use `test_pypi_release.py` for local packaging and dry-run upload.

### Testing GitHub Actions Workflows

The project includes tests for GitHub Actions workflows using `act` for local development:

```bash
# Test all workflows (requires act and Docker)
pytest tests/test_workflows.py

# Test specific workflow
pytest tests/test_workflows.py::test_ci_workflow
pytest tests/test_workflows.py::test_publish_workflow
```

**Prerequisites:**
- Install [act](https://github.com/nektos/act) for local GitHub Actions testing
- Docker must be running
- For publish workflow tests: Set `TEST_PYPI_API_TOKEN` environment variable

**Note:** Workflow tests are automatically skipped in CI environments.
