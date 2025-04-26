"""
src/geocodio/client.py
High‑level synchronous client for the Geocodio API.
"""

from __future__ import annotations

import os
from typing import List, Union, Dict, Tuple, Optional

import httpx

from .models import (
    GeocodingResponse, GeocodingResult, AddressComponents,
    Location, GeocodioFields, Timezone, CongressionalDistrict,
    CensusData, ACSSurveyData, StateLegislativeDistrict, SchoolDistrict,
    Demographics, Economics, Families
)
from .exceptions import InvalidRequestError, AuthenticationError, GeocodioServerError


class GeocodioClient:
    BASE_PATH = "/v1.7"  # keep in sync with Geocodio's current version

    def __init__(self, api_key: Optional[str] = None, hostname: str = "api.geocod.io"):
        self.api_key: str = api_key or os.getenv("GEOCODIO_API_KEY", "")
        if not self.api_key:
            raise AuthenticationError(
                detail="No API key supplied and GEOCODIO_API_KEY is not set."
            )
        self.hostname = hostname.rstrip("/")
        self._http = httpx.Client(base_url=f"https://{self.hostname}")

    # ──────────────────────────────────────────────────────────────────────────
    # Public methods
    # ──────────────────────────────────────────────────────────────────────────

    def geocode(
        self,
        address: Union[str, Dict[str, str], List[Union[str, Dict[str, str]]], Dict[str, Union[str, Dict[str, str]]]],
        fields: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> GeocodingResponse:
        params: Dict[str, Union[str, int]] = {"api_key": self.api_key}
        if fields:
            params["fields"] = ",".join(fields)
        if limit:
            params["limit"] = int(limit)

        endpoint: str
        data: Union[List, Dict] | None

        # Handle different input types
        if isinstance(address, dict) and not any(isinstance(v, dict) for v in address.values()):
            # Single structured address
            endpoint = f"{self.BASE_PATH}/geocode"
            params.update(address)
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

        response = self._request("POST" if data else "GET", endpoint, params, json=data)
        return self._parse_geocoding_response(response.json())

    def reverse(
        self,
        coordinate: Union[str, Tuple[float, float], List[Union[str, Tuple[float, float]]]],
        fields: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> GeocodingResponse:
        params: Dict[str, Union[str, int]] = {"api_key": self.api_key}
        if fields:
            params["fields"] = ",".join(fields)
        if limit:
            params["limit"] = int(limit)

        endpoint: str
        data: Dict[str, list] | None

        # Batch vs single coordinate
        if isinstance(coordinate, list):
            endpoint = f"{self.BASE_PATH}/reverse"
            data = {"coordinates": coordinate}
        else:
            endpoint = f"{self.BASE_PATH}/reverse"
            if isinstance(coordinate, tuple):
                params["q"] = f"{coordinate[0]},{coordinate[1]}"
            else:
                params["q"] = coordinate  # "lat,lng"
            data = None

        response = self._request("POST" if data else "GET", endpoint, params, json=data)
        return self._parse_geocoding_response(response.json())

    # ──────────────────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────────────────

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict,
        json: Optional[dict] = None,
    ) -> httpx.Response:
        print(f"\nRequest: {method} {endpoint}")
        print(f"Params: {params}")
        print(f"JSON body: {json}")
        resp = self._http.request(method, endpoint, params=params, json=json, timeout=30)
        if resp.status_code == 422:
            raise InvalidRequestError(resp.text)
        if resp.status_code == 403:
            raise AuthenticationError(resp.text)
        if 500 <= resp.status_code <= 599:
            raise GeocodioServerError(resp.text)
        resp.raise_for_status()
        return resp

    # ──────────────────────────────────────────────────────────────────────────

    def _parse_geocoding_response(self, response_json: dict) -> GeocodingResponse:
        print("Raw response:", response_json)  # Debug logging

        # Handle batch response format
        if "results" in response_json and isinstance(response_json["results"], list) and response_json["results"] and "response" in response_json["results"][0]:
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

    def _parse_fields(self, fields_data: dict | None) -> GeocodioFields | None:
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

        school_districts = None
        if "school" in fields_data:
            school_districts = [
                SchoolDistrict.from_api(district)
                for district in fields_data["school"]
            ]

        census2010 = (
            CensusData.from_api(fields_data["census2010"])
            if "census2010" in fields_data else None
        )

        census2020 = (
            CensusData.from_api(fields_data["census2020"])
            if "census2020" in fields_data else None
        )

        census2023 = (
            CensusData.from_api(fields_data["census2023"])
            if "census2023" in fields_data else None
        )

        acs = (
            ACSSurveyData.from_api(fields_data["acs"])
            if "acs" in fields_data else None
        )

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

        return GeocodioFields(
            timezone=timezone,
            congressional_districts=congressional_districts,
            state_legislative_districts=state_legislative_districts,
            state_legislative_districts_next=state_legislative_districts_next,
            school_districts=school_districts,
            census2010=census2010,
            census2020=census2020,
            census2023=census2023,
            acs=acs,
            demographics=demographics,
            economics=economics,
            families=families,
        )