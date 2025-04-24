"""
src/geocodio/models.py
Dataclass representations of Geocodio API responses and related objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict


# ──────────────────────────────────────────────────────────────────────────────
# Primitive value objects
# ──────────────────────────────────────────────────────────────────────────────

class _HasExtras:
    extras: Dict[str, Any]

    def get_extra(self, key: str, default=None):
        return self.extras.get(key, default)

    def __getattr__(self, item):
        try:
            return self.extras[item]
        except KeyError as exc:
            raise AttributeError(item) from exc


@dataclass(slots=True, frozen=True)
class Location:
    lat: float
    lng: float


@dataclass(frozen=True)
class AddressComponents(_HasExtras):
    # core / always-present
    number:           Optional[str] = None
    predirectional:   Optional[str] = None   # e.g. "N"
    street:           Optional[str] = None
    suffix:           Optional[str] = None   # e.g. "St"
    postdirectional:  Optional[str] = None
    formatted_street: Optional[str] = None   # full street line

    city:        Optional[str] = None
    county:      Optional[str] = None
    state:       Optional[str] = None
    zip:         Optional[str] = None        # Geocodio returns "zip"
    postal_code: Optional[str] = None        # alias for completeness
    country:     Optional[str] = None

    # catch‑all for anything Geocodio adds later
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "AddressComponents":
        """Ignore unknown keys by stashing them in `extras`."""
        known = {f.name for f in cls.__dataclass_fields__.values()}
        core  = {k: v for k, v in data.items() if k in known}
        extra = {k: v for k, v in data.items() if k not in known}
        return cls(**core, extras=extra)


@dataclass(frozen=True)
class Timezone(_HasExtras):
    name: str
    utc_offset: int
    observes_dst: Optional[bool] = None   # new key documented by Geocodio
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "Timezone":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        core  = {k: v for k, v in data.items() if k in known}
        extra = {k: v for k, v in data.items() if k not in known}
        return cls(**core, extras=extra)


@dataclass(slots=True, frozen=True)
class CongressionalDistrict(_HasExtras):
    name: str
    district_number: int
    congress_number: str
    ocd_id: Optional[str] = None
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "CongressionalDistrict":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        core  = {k: v for k, v in data.items() if k in known}
        extra = {k: v for k, v in data.items() if k not in known}
        return cls(**core, extras=extra)


# ──────────────────────────────────────────────────────────────────────────────
# Composite field container
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(slots=True, frozen=True)
class CensusData(_HasExtras):
    """
    Census data for a location.
    """
    block: Optional[str] = None
    blockgroup: Optional[str] = None
    tract: Optional[str] = None
    county_fips: Optional[str] = None
    state_fips: Optional[str] = None
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "CensusData":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        core  = {k: v for k, v in data.items() if k in known}
        extra = {k: v for k, v in data.items() if k not in known}
        return cls(**core, extras=extra)


@dataclass(slots=True, frozen=True)
class ACSSurveyData(_HasExtras):
    """
    American Community Survey data for a location.
    """
    population: Optional[int] = None
    households: Optional[int] = None
    median_income: Optional[int] = None
    median_age: Optional[float] = None
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> "ACSSurveyData":
        known = {f.name for f in cls.__dataclass_fields__.values()}
        core  = {k: v for k, v in data.items() if k in known}
        extra = {k: v for k, v in data.items() if k not in known}
        return cls(**core, extras=extra)


@dataclass(slots=True, frozen=True)
class GeocodioFields:
    """
    Container for optional 'fields' returned by the Geocodio API.
    Add new attributes as additional data‑append endpoints become useful.
    """
    timezone: Optional[Timezone] = None
    congressional_districts: Optional[List[CongressionalDistrict]] = None
    census2010: Optional[CensusData] = None
    census2020: Optional[CensusData] = None
    acs: Optional[ACSSurveyData] = None


# ──────────────────────────────────────────────────────────────────────────────
# Main result objects
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(slots=True, frozen=True)
class GeocodingResult:
    address_components: AddressComponents
    formatted_address: str
    location: Location
    accuracy: float
    accuracy_type: str
    source: str
    fields: Optional[GeocodioFields] = None


@dataclass(slots=True, frozen=True)
class GeocodingResponse:
    """
    Top‑level structure returned by client.geocode() / client.reverse().
    """
    input: Dict[str, Optional[str]]
    results: List[GeocodingResult] = field(default_factory=list)