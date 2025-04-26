"""
src/geocodio/models.py
Dataclass representations of Geocodio API responses and related objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict, TypeVar, Type, ClassVar

T = TypeVar('T', bound='_HasExtras')

class ApiModelMixin:
    """Mixin to provide additional functionality for API response models."""

    @classmethod
    def from_api(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create an instance from API response data.

        Known fields are extracted and passed to the constructor.
        Unknown fields are stored in the extras dictionary.
        """
        known = {f.name for f in cls.__dataclass_fields__.values()}
        core = {k: v for k, v in data.items() if k in known}
        extra = {k: v for k, v in data.items() if k not in known}
        return cls(**core, extras=extra)


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
class AddressComponents(_HasExtras, ApiModelMixin):
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


@dataclass(frozen=True)
class Timezone(_HasExtras, ApiModelMixin):
    name: str
    utc_offset: int
    observes_dst: Optional[bool] = None   # new key documented by Geocodio
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class CongressionalDistrict(_HasExtras, ApiModelMixin):
    name: str
    district_number: int
    congress_number: str
    ocd_id: Optional[str] = None
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class StateLegislativeDistrict(_HasExtras, ApiModelMixin):
    """
    State legislative district information.
    """
    name: str
    district_number: int
    chamber: str  # 'house' or 'senate'
    ocd_id: Optional[str] = None
    proportion: Optional[float] = None  # Proportion of overlap with the address
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class CensusData(_HasExtras, ApiModelMixin):
    """
    Census data for a location.
    """
    block: Optional[str] = None
    blockgroup: Optional[str] = None
    tract: Optional[str] = None
    county_fips: Optional[str] = None
    state_fips: Optional[str] = None
    msa_code: Optional[str] = None  # Metropolitan Statistical Area
    csa_code: Optional[str] = None  # Combined Statistical Area
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class ACSSurveyData(_HasExtras, ApiModelMixin):
    """
    American Community Survey data for a location.
    """
    population: Optional[int] = None
    households: Optional[int] = None
    median_income: Optional[int] = None
    median_age: Optional[float] = None
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class SchoolDistrict(_HasExtras, ApiModelMixin):
    """
    School district information.
    """
    name: str
    district_number: Optional[str] = None
    lea_id: Optional[str] = None  # Local Education Agency ID
    nces_id: Optional[str] = None  # National Center for Education Statistics ID
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class Demographics(_HasExtras, ApiModelMixin):
    """
    American Community Survey demographics data.
    """
    total_population: Optional[int] = None
    male_population: Optional[int] = None
    female_population: Optional[int] = None
    median_age: Optional[float] = None
    white_population: Optional[int] = None
    black_population: Optional[int] = None
    asian_population: Optional[int] = None
    hispanic_population: Optional[int] = None
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class Economics(_HasExtras, ApiModelMixin):
    """
    American Community Survey economics data.
    """
    median_household_income: Optional[int] = None
    mean_household_income: Optional[int] = None
    per_capita_income: Optional[int] = None
    poverty_rate: Optional[float] = None
    unemployment_rate: Optional[float] = None
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class GeocodioFields:
    """
    Container for optional 'fields' returned by the Geocodio API.
    Add new attributes as additional data‑append endpoints become useful.
    """
    timezone: Optional[Timezone] = None
    congressional_districts: Optional[List[CongressionalDistrict]] = None
    state_legislative_districts: Optional[List[StateLegislativeDistrict]] = None
    state_legislative_districts_next: Optional[List[StateLegislativeDistrict]] = None
    school_districts: Optional[List[SchoolDistrict]] = None
    census2010: Optional[CensusData] = None
    census2020: Optional[CensusData] = None
    census2023: Optional[CensusData] = None
    acs: Optional[ACSSurveyData] = None
    demographics: Optional[Demographics] = None
    economics: Optional[Economics] = None


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