"""
src/geocodio/client.py
High‑level synchronous client for the Geocodio API.
"""

from __future__ import annotations

import logging
import os
from typing import List, Union, Dict, Tuple, Optional

import httpx

from geocodio._version import __version__

# Set up logger early to capture all logs
logger = logging.getLogger("geocodio")

# flake8: noqa: F401
from geocodio.models import (
    GeocodingResponse, GeocodingResult, AddressComponents,
    Location, GeocodioFields, Timezone, CongressionalDistrict,
    CensusData, ACSSurveyData, StateLegislativeDistrict, SchoolDistrict,
    Demographics, Economics, Families, Housing, Social,
    FederalRiding, ProvincialRiding, StatisticsCanadaData, ListResponse, PaginatedResponse,
    ZIP4Data, FFIECData,
    DistanceResponse, DistanceMatrixResponse, DistanceJobResponse,
)
from geocodio.distance import (
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
    normalize_distance_mode,
)
from geocodio.exceptions import InvalidRequestError, AuthenticationError, GeocodioServerError, BadRequestError


class Geocodio:
    BASE_PATH = "/v1.9"  # keep in sync with Geocodio's current version
    DEFAULT_SINGLE_TIMEOUT = 5.0
    DEFAULT_BATCH_TIMEOUT = 1800.0  # 30 minutes
    LIST_API_TIMEOUT = 60.0
    USER_AGENT = f"geocodio-library-python/{__version__}"

    @staticmethod
    def get_status_exception_mappings() -> Dict[
        int, type[BadRequestError | InvalidRequestError | AuthenticationError | GeocodioServerError]
    ]:
        """
        Returns a list of status code to exception mappings.
        This is used to map HTTP status codes to specific exceptions.
        """
        return {
            400: BadRequestError,
            422: InvalidRequestError,
            403: AuthenticationError,
            500: GeocodioServerError,
        }

    def __init__(
        self,
        api_key: Optional[str] = None,
        hostname: str = "api.geocod.io",
        single_timeout: Optional[float] = None,
        batch_timeout: Optional[float] = None,
        list_timeout: Optional[float] = None,
        verify_ssl: bool = True,
    ):
        self.api_key: str = api_key or os.getenv("GEOCODIO_API_KEY", "")
        if not self.api_key:
            raise AuthenticationError(
                detail="No API key supplied and GEOCODIO_API_KEY is not set."
            )
        self.hostname = hostname.rstrip("/")
        self.single_timeout = single_timeout or self.DEFAULT_SINGLE_TIMEOUT
        self.batch_timeout = batch_timeout or self.DEFAULT_BATCH_TIMEOUT
        self.list_timeout = list_timeout or self.LIST_API_TIMEOUT
        self._http = httpx.Client(base_url=f"https://{self.hostname}", verify=verify_ssl)

    # ──────────────────────────────────────────────────────────────────────────
    # Public methods
    # ──────────────────────────────────────────────────────────────────────────

    def geocode(
            self,
            address: Union[
                str, Dict[str, str], List[Union[str, Dict[str, str]]], Dict[str, Union[str, Dict[str, str]]]],
            fields: Optional[List[str]] = None,
            limit: Optional[int] = None,
            country: Optional[str] = None,
            # Distance parameters
            destinations: Optional[List[Union[str, Tuple[float, float], "Coordinate"]]] = None,
            distance_mode: Optional[str] = None,
            distance_units: Optional[str] = None,
            distance_max_results: Optional[int] = None,
            distance_max_distance: Optional[float] = None,
            distance_max_duration: Optional[int] = None,
            distance_min_distance: Optional[float] = None,
            distance_min_duration: Optional[int] = None,
            distance_order_by: Optional[str] = None,
            distance_sort_order: Optional[str] = None,
    ) -> GeocodingResponse:
        params: Dict[str, Union[str, int, List[str]]] = {}
        if fields:
            params["fields"] = ",".join(fields)
        if limit:
            params["limit"] = int(limit)
        if country:
            params["country"] = country

        # Add distance parameters if destinations provided
        if destinations:
            dest_strs = [
                self._coordinate_to_string(self._normalize_coordinate(d))
                for d in destinations
            ]
            params["destinations[]"] = dest_strs
            if distance_mode:
                params["distance_mode"] = normalize_distance_mode(distance_mode)
            if distance_units:
                params["distance_units"] = distance_units
            if distance_max_results is not None:
                params["distance_max_results"] = distance_max_results
            if distance_max_distance is not None:
                params["distance_max_distance"] = distance_max_distance
            if distance_max_duration is not None:
                params["distance_max_duration"] = distance_max_duration
            if distance_min_distance is not None:
                params["distance_min_distance"] = distance_min_distance
            if distance_min_duration is not None:
                params["distance_min_duration"] = distance_min_duration
            if distance_order_by:
                params["distance_order_by"] = distance_order_by
            if distance_sort_order:
                params["distance_sort"] = distance_sort_order

        endpoint: str
        data: Union[List, Dict] | None

        # Handle different input types
        if isinstance(address, dict) and not any(isinstance(v, dict) for v in address.values()):
            # Single structured address
            endpoint = f"{self.BASE_PATH}/geocode"
            # Map our parameter names to API parameter names
            param_map = {
                "street": "street",
                "street2": "street2",
                "city": "city",
                "county": "county",
                "state": "state",
                "postal_code": "postal_code",
                "country": "country",
            }
            # Only include parameters that are present in the input
            for key, value in address.items():
                if key in param_map and value:
                    params[param_map[key]] = value
            data = None
        elif isinstance(address, list):
            # Batch addresses - send list directly
            endpoint = f"{self.BASE_PATH}/geocode"
            data = address
        elif isinstance(address, dict) and any(isinstance(v, dict) for v in address.values()):
            # Batch addresses with custom keys
            endpoint = f"{self.BASE_PATH}/geocode"
            data = {"addresses": list(address.values()), "keys": list(address.keys())}
        else:
            # Single address string
            endpoint = f"{self.BASE_PATH}/geocode"
            params["q"] = address
            data = None

        timeout = self.batch_timeout if data else self.single_timeout
        response = self._request("POST" if data else "GET", endpoint, params, json=data, timeout=timeout)
        return self._parse_geocoding_response(response.json())

    def reverse(
            self,
            coordinate: Union[str, Tuple[float, float], List[Union[str, Tuple[float, float]]]],
            fields: Optional[List[str]] = None,
            limit: Optional[int] = None,
            # Distance parameters
            destinations: Optional[List[Union[str, Tuple[float, float], "Coordinate"]]] = None,
            distance_mode: Optional[str] = None,
            distance_units: Optional[str] = None,
            distance_max_results: Optional[int] = None,
            distance_max_distance: Optional[float] = None,
            distance_max_duration: Optional[int] = None,
            distance_min_distance: Optional[float] = None,
            distance_min_duration: Optional[int] = None,
            distance_order_by: Optional[str] = None,
            distance_sort_order: Optional[str] = None,
    ) -> GeocodingResponse:
        params: Dict[str, Union[str, int, List[str]]] = {}
        if fields:
            params["fields"] = ",".join(fields)
        if limit:
            params["limit"] = int(limit)

        # Add distance parameters if destinations provided
        if destinations:
            dest_strs = [
                self._coordinate_to_string(self._normalize_coordinate(d))
                for d in destinations
            ]
            params["destinations[]"] = dest_strs
            if distance_mode:
                params["distance_mode"] = normalize_distance_mode(distance_mode)
            if distance_units:
                params["distance_units"] = distance_units
            if distance_max_results is not None:
                params["distance_max_results"] = distance_max_results
            if distance_max_distance is not None:
                params["distance_max_distance"] = distance_max_distance
            if distance_max_duration is not None:
                params["distance_max_duration"] = distance_max_duration
            if distance_min_distance is not None:
                params["distance_min_distance"] = distance_min_distance
            if distance_min_duration is not None:
                params["distance_min_duration"] = distance_min_duration
            if distance_order_by:
                params["distance_order_by"] = distance_order_by
            if distance_sort_order:
                params["distance_sort"] = distance_sort_order

        endpoint: str
        data: Union[List[str], None]

        # Batch vs single coordinate
        if isinstance(coordinate, list):
            endpoint = f"{self.BASE_PATH}/reverse"
            coords_as_strings = []
            for coord in coordinate:
                if isinstance(coord, tuple):
                    coords_as_strings.append(f"{coord[0]},{coord[1]}")
                else:
                    coords_as_strings.append(coord)
            data = coords_as_strings
        else:
            endpoint = f"{self.BASE_PATH}/reverse"
            if isinstance(coordinate, tuple):
                params["q"] = f"{coordinate[0]},{coordinate[1]}"
            else:
                params["q"] = coordinate  # "lat,lng"
            data = None

        timeout = self.batch_timeout if data else self.single_timeout
        response = self._request("POST" if data else "GET", endpoint, params, json=data, timeout=timeout)
        return self._parse_geocoding_response(response.json())

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _request(
            self,
            method: str,
            endpoint: str,
            params: Optional[dict] = None,
            json: Optional[dict] = None,
            files: Optional[dict] = None,
            timeout: Optional[float] = None,
    ) -> httpx.Response:
        logger.debug(f"Making Request: {method} {endpoint}")
        logger.debug(f"Params: {params}")
        logger.debug(f"JSON body: {json}")
        logger.debug(f"Files: {files}")

        if timeout is None:
            timeout = self.single_timeout
        
        # Set up authorization and user-agent headers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": self.USER_AGENT
        }
        
        logger.debug(f"Using timeout: {timeout}s")
        resp = self._http.request(method, endpoint, params=params, json=json, files=files, headers=headers, timeout=timeout)

        logger.debug(f"Response status code: {resp.status_code}")
        logger.debug(f"Response headers: {resp.headers}")
        logger.debug(f"Response body: {resp.content}")

        resp = self._handle_error_response(resp)

        return resp

    def _handle_error_response(self, resp) -> httpx.Response:
        if resp.status_code < 400:
            logger.debug("No error in response, returning normally.")
            return resp

        exception_mappings = self.get_status_exception_mappings()
        # dump the type and content of the exception mappings for debugging
        logger.error(f"Error response: {resp.status_code} - {resp.text}")
        if resp.status_code in exception_mappings:
            exception_class = exception_mappings[resp.status_code]
            raise exception_class(resp.text)
        else:
            raise GeocodioServerError(f"Unrecognized status code {resp.status_code}: {resp.text}")

    def _parse_geocoding_response(self, response_json: dict) -> GeocodingResponse:
        logger.debug(f"Raw response: {response_json}")

        # Handle batch response format
        if "results" in response_json and isinstance(response_json["results"], list) and response_json[
            "results"] and "response" in response_json["results"][0]:
            results = [
                GeocodingResult(
                    address_components=AddressComponents.from_api(res["response"]["results"][0]["address_components"]),
                    formatted_address=res["response"]["results"][0]["formatted_address"],
                    location=Location(**res["response"]["results"][0]["location"]),
                    accuracy=res["response"]["results"][0].get("accuracy", 0.0),
                    accuracy_type=res["response"]["results"][0].get("accuracy_type", ""),
                    source=res["response"]["results"][0].get("source", ""),
                    fields=self._parse_fields(res["response"]["results"][0].get("fields")),
                )
                for res in response_json["results"]
            ]
            return GeocodingResponse(input=response_json.get("input", {}), results=results)

        # Handle single response format
        results = [
            GeocodingResult(
                address_components=AddressComponents.from_api(res["address_components"]),
                formatted_address=res["formatted_address"],
                location=Location(**res["location"]),
                accuracy=res.get("accuracy", 0.0),
                accuracy_type=res.get("accuracy_type", ""),
                source=res.get("source", ""),
                fields=self._parse_fields(res.get("fields")),
            )
            for res in response_json.get("results", [])
        ]
        return GeocodingResponse(input=response_json.get("input", {}), results=results)

    # ──────────────────────────────────────────────────────────────────────────
    # List API methods
    # ──────────────────────────────────────────────────────────────────────────

    DIRECTION_FORWARD = "forward"
    DIRECTION_REVERSE = "reverse"

    def create_list(
            self,
            file: Optional[str] = None,
            filename: Optional[str] = None,
            direction: str = DIRECTION_FORWARD,
            format_: Optional[str] = "{{A}}",
            callback_url: Optional[str] = None,
            fields: list[str] | None = None
    ) -> ListResponse:
        """
        Create a new geocoding list.

        Args:
            file: The file content as a string. Required.
            filename: The name of the file. Defaults to "file.csv".
            direction: The direction of geocoding. Either "forward" or "reverse". Defaults to "forward".
            format_: The format string for the output. Defaults to "{{A}}".
            callback_url: Optional URL to call when processing is complete.
            fields: Optional list of fields to include in the response. Valid fields include:
                   - census2010, census2020, census2023
                   - cd, cd113-cd119 (congressional districts)
                   - stateleg, stateleg-next (state legislative districts)
                   - school (school districts)
                   - timezone
                   - acs, acs-demographics, acs-economics, acs-families, acs-housing, acs-social
                   - riding, provriding, provriding-next (Canadian data)
                   - statcan (Statistics Canada data)
                   - zip4 (ZIP+4 data)
                   - ffiec (FFIEC data, beta)

        Returns:
            A ListResponse object containing the created list information.

        Raises:
            ValueError: If file is not provided.
            InvalidRequestError: If the API request is invalid.
            AuthenticationError: If the API key is invalid.
            GeocodioServerError: If the server encounters an error.
        """
        params: Dict[str, Union[str, int]] = {}
        endpoint = f"{self.BASE_PATH}/lists"

        if not file:
            raise ValueError("File data is required to create a list.")
        filename = filename or "file.csv"
        files = {
            "file": (filename, file),
        }
        if direction:
            params["direction"] = direction
        if format_:
            params["format"] = format_
        if callback_url:
            params["callback"] = callback_url
        if fields:
            # Join fields with commas as required by the API
            params["fields"] = ",".join(fields)

        response = self._request("POST", endpoint, params, files=files, timeout=self.list_timeout)
        logger.debug(f"Response content: {response.text}")
        return self._parse_list_response(response.json(), response=response)

    def get_lists(self) -> PaginatedResponse:
        """
        Retrieve all lists.

        Returns:
            A ListResponse object containing all lists.
        """
        params: Dict[str, Union[str, int]] = {}
        endpoint = f"{self.BASE_PATH}/lists"

        response = self._request("GET", endpoint, params, timeout=self.list_timeout)
        pagination_info = response.json()

        logger.debug(f"Pagination info: {pagination_info}")

        response_lists = []
        for list_item in pagination_info.get("data", []):
            logger.debug(f"List item: {list_item}")
            response_lists.append(self._parse_list_response(list_item, response=response))

        return PaginatedResponse(
            data=response_lists,
            current_page=pagination_info.get("current_page", 1),
            from_=pagination_info.get("from", 0),
            to=pagination_info.get("to", 0),
            path=pagination_info.get("path", ""),
            per_page=pagination_info.get("per_page", 10),
            first_page_url=pagination_info.get("first_page_url"),
            next_page_url=pagination_info.get("next_page_url"),
            prev_page_url=pagination_info.get("prev_page_url")
        )

    def get_list(self, list_id: str) -> ListResponse:
        """
        Retrieve a list by ID.

        Args:
            list_id: The ID of the list to retrieve.

        Returns:
            A ListResponse object containing the retrieved list.
        """
        params: Dict[str, Union[str, int]] = {}
        endpoint = f"{self.BASE_PATH}/lists/{list_id}"

        response = self._request("GET", endpoint, params, timeout=self.list_timeout)
        return self._parse_list_response(response.json(), response=response)

    def delete_list(self, list_id: str) -> None:
        """
        Delete a list.

        Args:
            list_id: The ID of the list to delete.
        """
        params: Dict[str, Union[str, int]] = {}
        endpoint = f"{self.BASE_PATH}/lists/{list_id}"

        self._request("DELETE", endpoint, params, timeout=self.list_timeout)

    @staticmethod
    def _parse_list_response(response_json: dict, response: httpx.Response = None) -> ListResponse:
        """
        Parse a response from the List API.

        Args:
            response_json: The JSON response from the List API.

        Returns:
            A ListResponse object.
        """
        logger.debug(f"{response_json}")
        return ListResponse(
            id=response_json.get("id"),
            file=response_json.get("file"),
            status=response_json.get("status"),
            download_url=response_json.get("download_url"),
            expires_at=response_json.get("expires_at"),
            http_response=response,
        )


    def _parse_fields(self, fields_data: dict | None) -> GeocodioFields | None:
        """
        Parse fields data from API response.

        Supports both nested and flat field structures for backward compatibility:
        - Nested: census: {2010: {...}, 2020: {...}}, acs: {demographics: {...}}
        - Flat: census2010: {...}, acs-demographics: {...}
        """
        if not fields_data:
            return None

        timezone = (
            Timezone.from_api(fields_data["timezone"])
            if "timezone" in fields_data else None
        )
        congressional_districts = None
        if "cd" in fields_data:
            congressional_districts = [
                CongressionalDistrict.from_api(cd)
                for cd in fields_data["cd"]
            ]
        elif "congressional_districts" in fields_data:
            congressional_districts = [
                CongressionalDistrict.from_api(cd)
                for cd in fields_data["congressional_districts"]
            ]

        state_legislative_districts = None
        if "stateleg" in fields_data:
            state_legislative_districts = [
                StateLegislativeDistrict.from_api(district)
                for district in fields_data["stateleg"]
            ]

        state_legislative_districts_next = None
        if "stateleg-next" in fields_data:
            state_legislative_districts_next = [
                StateLegislativeDistrict.from_api(district)
                for district in fields_data["stateleg-next"]
            ]

        # School districts - support both nested dict and flat list formats
        school_districts = None

        # Check for nested dict format: school_districts: {elementary: {...}, secondary: {...}}
        if "school_districts" in fields_data:
            school_data = fields_data["school_districts"]
            if isinstance(school_data, dict):
                # Nested dict format - iterate over dict values
                school_districts = [
                    SchoolDistrict.from_api(district)
                    for district in school_data.values()
                ]
            elif isinstance(school_data, list):
                # List format (backward compatibility)
                school_districts = [
                    SchoolDistrict.from_api(district)
                    for district in school_data
                ]

        # Also check for flat list format: school: [...]
        elif "school" in fields_data:
            school_data = fields_data["school"]
            if isinstance(school_data, dict):
                # Dict format
                school_districts = [
                    SchoolDistrict.from_api(district)
                    for district in school_data.values()
                ]
            elif isinstance(school_data, list):
                # List format
                school_districts = [
                    SchoolDistrict.from_api(district)
                    for district in school_data
                ]

        # Census fields - support both nested and flat structures
        # Store in dict for dynamic access (fields.census2020, fields.census2031, etc.)
        census_data_dict = {}

        def parse_census_data(data: dict) -> dict:
            """
            Parse census data and map new field names to old field names for backward compatibility.

            API used to send: block, blockgroup, tract
            API now sends: block_code, block_group, tract_code

            We populate both so existing code using old names continues to work.
            """
            parsed = dict(data)  # Copy original data

            # Map new field names to old field names if old names not present
            if "block_code" in data and "block" not in data:
                parsed["block"] = data["block_code"]
            if "block_group" in data and "blockgroup" not in data:
                parsed["blockgroup"] = data["block_group"]
            if "tract_code" in data and "tract" not in data:
                parsed["tract"] = data["tract_code"]

            return parsed

        # Check for nested census structure: census: {2010: {...}, 2020: {...}}
        if "census" in fields_data and isinstance(fields_data["census"], dict):
            for year, census_data in fields_data["census"].items():
                field_name = f"census{year}"
                # Map new field names to old for backward compatibility
                parsed_data = parse_census_data(census_data)
                census_data_dict[field_name] = CensusData.from_api(parsed_data)

        # Also check for flat structure: census2010: {...}, census2020: {...}
        # This ensures backward compatibility if API sends both formats
        for key in fields_data:
            if key.startswith("census") and key[6:].isdigit() and key not in census_data_dict:
                # Map new field names to old for backward compatibility
                parsed_data = parse_census_data(fields_data[key])
                census_data_dict[key] = CensusData.from_api(parsed_data)

        # Parse flat ACS structure for backward compatibility
        # These will be merged with nested structure later if both exist
        demographics = (
            Demographics.from_api(fields_data["acs-demographics"])
            if "acs-demographics" in fields_data else None
        )

        economics = (
            Economics.from_api(fields_data["acs-economics"])
            if "acs-economics" in fields_data else None
        )

        families = (
            Families.from_api(fields_data["acs-families"])
            if "acs-families" in fields_data else None
        )

        housing = (
            Housing.from_api(fields_data["acs-housing"])
            if "acs-housing" in fields_data else None
        )

        social = (
            Social.from_api(fields_data["acs-social"])
            if "acs-social" in fields_data else None
        )

        # ACS fields - support both nested and flat structures
        acs_fields = {}
        acs = None

        # Check for ACS field
        if "acs" in fields_data and isinstance(fields_data["acs"], dict):
            acs_data = fields_data["acs"]

            # Check if this is nested ACS structure (contains metric keys)
            # or simple ACS structure (contains population, households, etc.)
            acs_metric_keys = {"demographics", "economics", "families", "housing", "social"}

            if any(key in acs_data for key in acs_metric_keys):
                # Nested structure: acs: {demographics: {...}, economics: {...}}
                acs_metric_map = {
                    "demographics": Demographics,
                    "economics": Economics,
                    "families": Families,
                    "housing": Housing,
                    "social": Social,
                }

                for metric, model_class in acs_metric_map.items():
                    if metric in acs_data:
                        acs_fields[metric] = model_class.from_api(acs_data[metric])
            else:
                # Simple structure: acs: {population: ..., households: ..., median_income: ...}
                acs = ACSSurveyData.from_api(acs_data)

        # Also preserve flat structure parsing for backward compatibility
        if demographics and "demographics" not in acs_fields:
            acs_fields["demographics"] = demographics
        if economics and "economics" not in acs_fields:
            acs_fields["economics"] = economics
        if families and "families" not in acs_fields:
            acs_fields["families"] = families
        if housing and "housing" not in acs_fields:
            acs_fields["housing"] = housing
        if social and "social" not in acs_fields:
            acs_fields["social"] = social

        # ZIP4 and FFIEC data
        zip4 = (
            ZIP4Data.from_api(fields_data["zip4"])
            if "zip4" in fields_data else None
        )

        ffiec = (
            FFIECData.from_api(fields_data["ffiec"])
            if "ffiec" in fields_data else None
        )

        # Canadian fields
        riding = (
            FederalRiding.from_api(fields_data["riding"])
            if "riding" in fields_data else None
        )

        provriding = (
            ProvincialRiding.from_api(fields_data["provriding"])
            if "provriding" in fields_data else None
        )

        provriding_next = (
            ProvincialRiding.from_api(fields_data["provriding-next"])
            if "provriding-next" in fields_data else None
        )

        statcan = (
            StatisticsCanadaData.from_api(fields_data["statcan"])
            if "statcan" in fields_data else None
        )

        # Collect all known field keys that were parsed
        parsed_keys = {
            "timezone", "cd", "congressional_districts",
            "stateleg", "stateleg-next",
            "school", "school_districts",  # Both school formats
            "census",  # Nested census structure
            "acs",  # Nested ACS structure
            "acs-demographics", "acs-economics", "acs-families", "acs-housing", "acs-social",
            "zip4", "ffiec",
            "riding", "provriding", "provriding-next",
            "statcan",
        }
        # Add flat census keys that were parsed (census2000, census2020, etc.)
        # All census years are now stored in _census dict for dynamic access
        parsed_keys.update(census_data_dict.keys())

        # Extras - capture any fields not explicitly handled
        # This is now mainly for truly unknown API fields (not census years)
        extras = {
            k: v for k, v in fields_data.items()
            if k not in parsed_keys
        }

        return GeocodioFields(
            timezone=timezone,
            congressional_districts=congressional_districts,
            state_legislative_districts=state_legislative_districts,
            state_legislative_districts_next=state_legislative_districts_next,
            school_districts=school_districts,
            acs=acs,
            zip4=zip4,
            ffiec=ffiec,
            riding=riding,
            provriding=provriding,
            provriding_next=provriding_next,
            statcan=statcan,
            extras=extras,
            _census=census_data_dict,  # All census years stored here
            **acs_fields,  # Dynamically include all ACS metric fields
        )

    # @TODO add a "keep_trying" parameter to download() to keep trying until the list is processed.
    def download(self, list_id: str, filename: Optional[str] = None) -> str | bytes:
        """
        This will generate/retrieve the fully geocoded list as a CSV file, and either return the content as bytes
        or save the file to disk with the provided filename.

        Args:
            list_id: The ID of the list to download.
            filename: filename to assign to the file (optional). If provided, the content will be saved to this file.

        Returns:
            The content of the file as a Bytes object, or the full file path string if filename is provided.
        Raises:
            GeocodioServerError if the list is still processing or another error occurs.
        """
        params = {}
        endpoint = f"{self.BASE_PATH}/lists/{list_id}/download"

        response: httpx.Response = self._request("GET", endpoint, params, timeout=self.list_timeout)
        if response.headers.get("content-type", "").startswith("application/json"):
            try:
                error = response.json()
                logger.error(f"Error downloading list {list_id}: {error}")
                raise GeocodioServerError(error.get("message", "Failed to download list."))
            except Exception as e:
                logger.error(f"Failed to parse error message from response: {response.text}", exc_info=True)
                raise GeocodioServerError("Failed to download list and could not parse error message.") from e
        else:
            if filename:
                # If a filename is provided, save the response content to a file of that name=
                # get the absolute path of the file
                if not os.path.isabs(filename):
                    filename = os.path.abspath(filename)
                # Ensure the directory exists
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                logger.debug(f"Saving list {list_id} to {filename}")

                # do not check if the file exists, just overwrite it
                if os.path.exists(filename):
                    logger.debug(f"File {filename} already exists; it will be overwritten.")

                try:
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    logger.info(f"List {list_id} downloaded and saved to {filename}")
                    return filename  # Return the full path of the saved file
                except IOError as e:
                    logger.error(f"Failed to save list {list_id} to {filename}: {e}", exc_info=True)
                    raise GeocodioServerError(f"Failed to save list: {e}")
            else:  # return the bytes content directly
                return response.content

    # ──────────────────────────────────────────────────────────────────────────
    # Distance API methods
    # ──────────────────────────────────────────────────────────────────────────

    def _normalize_coordinate(
        self,
        coord: Union[str, Tuple[float, float], Dict, "Coordinate"],
    ) -> "Coordinate":
        """Convert various input formats to Coordinate object."""
        return Coordinate.from_input(coord)

    def _coordinate_to_string(self, coord: "Coordinate") -> str:
        """Convert Coordinate to string for GET requests: 'lat,lng' or 'lat,lng,id'."""
        return coord.to_string()

    def _coordinate_to_dict(self, coord: "Coordinate") -> Dict:
        """Convert Coordinate to dict for POST requests."""
        return coord.to_dict()

    def distance(
        self,
        origin: Union[str, Tuple[float, float], "Coordinate"],
        destinations: List[Union[str, Tuple[float, float], "Coordinate"]],
        mode: str = DISTANCE_MODE_STRAIGHTLINE,
        units: str = DISTANCE_UNITS_MILES,
        max_results: Optional[int] = None,
        max_distance: Optional[float] = None,
        max_duration: Optional[int] = None,
        min_distance: Optional[float] = None,
        min_duration: Optional[int] = None,
        order_by: str = DISTANCE_ORDER_BY_DISTANCE,
        sort_order: str = DISTANCE_SORT_ASC,
    ) -> DistanceResponse:
        """
        Calculate distance from single origin to multiple destinations.

        Uses GET request with coordinates as query parameters.

        Args:
            origin: The origin coordinate (string, tuple, or Coordinate).
            destinations: List of destination coordinates.
            mode: Distance calculation mode ('straightline' or 'driving').
            units: Distance units ('miles' or 'kilometers').
            max_results: Maximum number of results to return.
            max_distance: Maximum distance filter.
            max_duration: Maximum duration filter (seconds, driving mode only).
            min_distance: Minimum distance filter.
            min_duration: Minimum duration filter (seconds, driving mode only).
            order_by: Sort results by 'distance' or 'duration'.
            sort_order: Sort direction ('asc' or 'desc').

        Returns:
            DistanceResponse with origin and calculated destinations.

        Example:
            >>> response = client.distance(
            ...     origin="38.8977,-77.0365,white_house",
            ...     destinations=["38.9072,-77.0369,capitol", "38.8895,-77.0353,monument"],
            ...     mode="straightline",
            ...     units="miles"
            ... )
            >>> print(response.destinations[0].distance_miles)
        """
        endpoint = f"{self.BASE_PATH}/distance"

        # Normalize and convert origin to string
        origin_coord = self._normalize_coordinate(origin)
        origin_str = self._coordinate_to_string(origin_coord)

        # Normalize and convert destinations to strings
        dest_strs = [
            self._coordinate_to_string(self._normalize_coordinate(d))
            for d in destinations
        ]

        # Build params
        params: Dict[str, Union[str, int, float, List[str]]] = {
            "origin": origin_str,
            "destinations[]": dest_strs,
            "mode": normalize_distance_mode(mode),
            "units": units,
        }

        # Add optional filter parameters
        if max_results is not None:
            params["max_results"] = max_results
        if max_distance is not None:
            params["max_distance"] = max_distance
        if max_duration is not None:
            params["max_duration"] = max_duration
        if min_distance is not None:
            params["min_distance"] = min_distance
        if min_duration is not None:
            params["min_duration"] = min_duration
        if order_by != DISTANCE_ORDER_BY_DISTANCE:
            params["order_by"] = order_by
        if sort_order != DISTANCE_SORT_ASC:
            params["sort"] = sort_order

        response = self._request("GET", endpoint, params, timeout=self.single_timeout)
        return DistanceResponse.from_api(response.json())

    def distance_matrix(
        self,
        origins: List[Union[str, Tuple[float, float], "Coordinate"]],
        destinations: List[Union[str, Tuple[float, float], "Coordinate"]],
        mode: str = DISTANCE_MODE_STRAIGHTLINE,
        units: str = DISTANCE_UNITS_MILES,
        max_results: Optional[int] = None,
        max_distance: Optional[float] = None,
        max_duration: Optional[int] = None,
        min_distance: Optional[float] = None,
        min_duration: Optional[int] = None,
        order_by: str = DISTANCE_ORDER_BY_DISTANCE,
        sort_order: str = DISTANCE_SORT_ASC,
    ) -> DistanceMatrixResponse:
        """
        Calculate distance matrix (multiple origins × destinations).

        Uses POST request with coordinates as objects in JSON body.

        Args:
            origins: List of origin coordinates.
            destinations: List of destination coordinates.
            mode: Distance calculation mode ('straightline' or 'driving').
            units: Distance units ('miles' or 'kilometers').
            max_results: Maximum number of results to return per origin.
            max_distance: Maximum distance filter.
            max_duration: Maximum duration filter (seconds, driving mode only).
            min_distance: Minimum distance filter.
            min_duration: Minimum duration filter (seconds, driving mode only).
            order_by: Sort results by 'distance' or 'duration'.
            sort_order: Sort direction ('asc' or 'desc').

        Returns:
            DistanceMatrixResponse with results for each origin.

        Example:
            >>> response = client.distance_matrix(
            ...     origins=[(38.8977, -77.0365), (38.9072, -77.0369)],
            ...     destinations=[(38.8895, -77.0353), (39.2904, -76.6122)],
            ...     mode="driving"
            ... )
            >>> print(response.results[0].destinations[0].distance_miles)
        """
        endpoint = f"{self.BASE_PATH}/distance-matrix"

        # Normalize and convert origins to dicts for POST
        origin_dicts = [
            self._coordinate_to_dict(self._normalize_coordinate(o))
            for o in origins
        ]

        # Normalize and convert destinations to dicts for POST
        dest_dicts = [
            self._coordinate_to_dict(self._normalize_coordinate(d))
            for d in destinations
        ]

        # Build request body
        body: Dict[str, Union[str, int, float, List[Dict]]] = {
            "origins": origin_dicts,
            "destinations": dest_dicts,
            "mode": normalize_distance_mode(mode),
            "units": units,
        }

        # Add optional filter parameters
        if max_results is not None:
            body["max_results"] = max_results
        if max_distance is not None:
            body["max_distance"] = max_distance
        if max_duration is not None:
            body["max_duration"] = max_duration
        if min_distance is not None:
            body["min_distance"] = min_distance
        if min_duration is not None:
            body["min_duration"] = min_duration
        if order_by != DISTANCE_ORDER_BY_DISTANCE:
            body["order_by"] = order_by
        if sort_order != DISTANCE_SORT_ASC:
            body["sort"] = sort_order

        response = self._request("POST", endpoint, json=body, timeout=self.batch_timeout)
        return DistanceMatrixResponse.from_api(response.json())

    def create_distance_matrix_job(
        self,
        name: str,
        origins: Union[List[Union[str, Tuple[float, float], "Coordinate"]], int],
        destinations: Union[List[Union[str, Tuple[float, float], "Coordinate"]], int],
        mode: str = DISTANCE_MODE_STRAIGHTLINE,
        units: str = DISTANCE_UNITS_MILES,
        callback_url: Optional[str] = None,
        max_results: Optional[int] = None,
        max_distance: Optional[float] = None,
        max_duration: Optional[int] = None,
        min_distance: Optional[float] = None,
        min_duration: Optional[int] = None,
        order_by: str = DISTANCE_ORDER_BY_DISTANCE,
        sort_order: str = DISTANCE_SORT_ASC,
    ) -> DistanceJobResponse:
        """
        Create an async distance matrix job for large calculations.

        Args:
            name: User-defined name for the job.
            origins: List of coordinates OR integer list ID.
            destinations: List of coordinates OR integer list ID.
            mode: Distance calculation mode ('straightline' or 'driving').
            units: Distance units ('miles' or 'kilometers').
            callback_url: Optional URL to call when processing completes.
            max_results: Maximum number of results to return per origin.
            max_distance: Maximum distance filter.
            max_duration: Maximum duration filter (seconds, driving mode only).
            min_distance: Minimum distance filter.
            min_duration: Minimum duration filter (seconds, driving mode only).
            order_by: Sort results by 'distance' or 'duration'.
            sort_order: Sort direction ('asc' or 'desc').

        Returns:
            DistanceJobResponse with job ID and status.

        Example:
            >>> job = client.create_distance_matrix_job(
            ...     name="My Calculation",
            ...     origins=[(38.8977, -77.0365), (38.9072, -77.0369)],
            ...     destinations=[(38.8895, -77.0353)],
            ...     mode="driving"
            ... )
            >>> print(job.id, job.status)
        """
        endpoint = f"{self.BASE_PATH}/distance-jobs"

        # Handle origins - either list of coordinates or list ID
        if isinstance(origins, int):
            origins_data = origins
        else:
            origins_data = [
                self._coordinate_to_dict(self._normalize_coordinate(o))
                for o in origins
            ]

        # Handle destinations - either list of coordinates or list ID
        if isinstance(destinations, int):
            destinations_data = destinations
        else:
            destinations_data = [
                self._coordinate_to_dict(self._normalize_coordinate(d))
                for d in destinations
            ]

        # Build request body
        body: Dict[str, Union[str, int, float, List[Dict]]] = {
            "name": name,
            "origins": origins_data,
            "destinations": destinations_data,
            "mode": normalize_distance_mode(mode),
            "units": units,
        }

        # Add optional parameters
        if callback_url:
            body["callback_url"] = callback_url
        if max_results is not None:
            body["max_results"] = max_results
        if max_distance is not None:
            body["max_distance"] = max_distance
        if max_duration is not None:
            body["max_duration"] = max_duration
        if min_distance is not None:
            body["min_distance"] = min_distance
        if min_duration is not None:
            body["min_duration"] = min_duration
        if order_by != DISTANCE_ORDER_BY_DISTANCE:
            body["order_by"] = order_by
        if sort_order != DISTANCE_SORT_ASC:
            body["sort"] = sort_order

        response = self._request("POST", endpoint, json=body, timeout=self.list_timeout)
        return DistanceJobResponse.from_api(response.json())

    def distance_matrix_job_status(self, job_id: Union[str, int]) -> DistanceJobResponse:
        """
        Get the status of a distance matrix job.

        Args:
            job_id: The job ID (integer or string).

        Returns:
            DistanceJobResponse with current status and progress.

        Example:
            >>> status = client.distance_matrix_job_status(123)
            >>> print(status.status, status.progress)
        """
        endpoint = f"{self.BASE_PATH}/distance-jobs/{job_id}"
        response = self._request("GET", endpoint, timeout=self.list_timeout)
        return DistanceJobResponse.from_api(response.json())

    def distance_matrix_jobs(self, page: int = 1) -> PaginatedResponse:
        """
        List all distance matrix jobs.

        Args:
            page: Page number for pagination.

        Returns:
            PaginatedResponse containing list of DistanceJobResponse objects.
        """
        endpoint = f"{self.BASE_PATH}/distance-jobs"
        params: Dict[str, int] = {}
        if page > 1:
            params["page"] = page

        response = self._request("GET", endpoint, params, timeout=self.list_timeout)
        pagination_info = response.json()

        job_responses = [
            DistanceJobResponse.from_api(job_data)
            for job_data in pagination_info.get("data", [])
        ]

        # Reuse PaginatedResponse but with job data
        return PaginatedResponse(
            data=job_responses,  # type: ignore
            current_page=pagination_info.get("current_page", 1),
            from_=pagination_info.get("from", 0),
            to=pagination_info.get("to", 0),
            path=pagination_info.get("path", ""),
            per_page=pagination_info.get("per_page", 10),
            first_page_url=pagination_info.get("first_page_url"),
            next_page_url=pagination_info.get("next_page_url"),
            prev_page_url=pagination_info.get("prev_page_url"),
        )

    def get_distance_matrix_job_results(
        self, job_id: Union[str, int]
    ) -> DistanceMatrixResponse:
        """
        Download and parse distance matrix job results.

        Args:
            job_id: The job ID (integer or string).

        Returns:
            DistanceMatrixResponse with all calculated distances.

        Raises:
            GeocodioServerError: If the job is not complete or failed.

        Example:
            >>> results = client.get_distance_matrix_job_results(123)
            >>> for result in results.results:
            ...     print(result.origin.id, result.destinations[0].distance_miles)
        """
        endpoint = f"{self.BASE_PATH}/distance-jobs/{job_id}/download"
        response = self._request("GET", endpoint, timeout=self.list_timeout)

        # Check if response is JSON (success) or error
        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type:
            return DistanceMatrixResponse.from_api(response.json())
        else:
            raise GeocodioServerError(
                f"Unexpected response format: {content_type}. "
                f"Job may not be complete."
            )

    def download_distance_matrix_job(
        self, job_id: Union[str, int], filename: str
    ) -> str:
        """
        Download distance matrix job results to a file.

        Args:
            job_id: The job ID (integer or string).
            filename: Path to save the results file.

        Returns:
            The absolute path to the saved file.

        Raises:
            GeocodioServerError: If the job is not complete or download fails.
        """
        endpoint = f"{self.BASE_PATH}/distance-jobs/{job_id}/download"
        response = self._request("GET", endpoint, timeout=self.list_timeout)

        # Get absolute path
        if not os.path.isabs(filename):
            filename = os.path.abspath(filename)

        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        try:
            with open(filename, "wb") as f:
                f.write(response.content)
            logger.info(f"Distance job {job_id} downloaded to {filename}")
            return filename
        except IOError as e:
            logger.error(f"Failed to save distance job {job_id} to {filename}: {e}")
            raise GeocodioServerError(f"Failed to save distance job: {e}")

    def delete_distance_matrix_job(self, job_id: Union[str, int]) -> None:
        """
        Delete a distance matrix job.

        Args:
            job_id: The job ID (integer or string).
        """
        endpoint = f"{self.BASE_PATH}/distance-jobs/{job_id}"
        self._request("DELETE", endpoint, timeout=self.list_timeout)
