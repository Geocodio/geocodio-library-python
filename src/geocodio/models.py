"""
src/geocodio/models.py
Dataclass representations of Geocodio API responses and related objects.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict, TypeVar, Type

import httpx

T = TypeVar("T", bound="ExtrasMixin")


class ExtrasMixin:
    """Mixin to provide additional functionality for API response models."""

    extras: Dict[str, Any]

    def get_extra(self, key: str, default=None):
        return self.extras.get(key, default)

    def __getattr__(self, item):
        try:
            return self.extras[item]
        except KeyError as exc:
            raise AttributeError(item) from exc


class ApiModelMixin(ExtrasMixin):
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


@dataclass(slots=True, frozen=True)
class Location:
    lat: float
    lng: float


@dataclass(frozen=True)
class AddressComponents(ApiModelMixin):
    # core / always-present
    number: Optional[str] = None
    predirectional: Optional[str] = None  # e.g. "N"
    street: Optional[str] = None
    suffix: Optional[str] = None  # e.g. "St"
    postdirectional: Optional[str] = None
    formatted_street: Optional[str] = None  # full street line

    city: Optional[str] = None
    county: Optional[str] = None
    state: Optional[str] = None
    zip: Optional[str] = None  # Geocodio returns "zip"
    postal_code: Optional[str] = None  # alias for completeness
    country: Optional[str] = None

    # catch‑all for anything Geocodio adds later
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(frozen=True)
class Timezone(ApiModelMixin):
    name: str
    utc_offset: int
    observes_dst: Optional[bool] = None  # new key documented by Geocodio
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class CongressionalDistrict(ApiModelMixin):
    name: str
    district_number: int
    congress_number: str
    ocd_id: Optional[str] = None
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class StateLegislativeDistrict(ApiModelMixin):
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
class CensusData(ApiModelMixin):
    """
    Census data for a location.

    Supports both legacy field names (block, blockgroup, tract) and
    current API field names (block_code, block_group, tract_code).
    """

    # Current API field names
    census_year: Optional[int] = None
    block_code: Optional[str] = None
    block_group: Optional[str] = None
    tract_code: Optional[str] = None
    full_fips: Optional[str] = None
    county_fips: Optional[str] = None
    state_fips: Optional[str] = None
    place: Optional[Dict[str, Any]] = None
    metro_micro_statistical_area: Optional[Dict[str, Any]] = None
    combined_statistical_area: Optional[Dict[str, Any]] = None
    metropolitan_division: Optional[Dict[str, Any]] = None
    county_subdivision: Optional[Dict[str, Any]] = None
    source: Optional[str] = None

    # Legacy field names (for backward compatibility)
    block: Optional[str] = None
    blockgroup: Optional[str] = None
    tract: Optional[str] = None
    msa_code: Optional[str] = None  # Metropolitan Statistical Area
    csa_code: Optional[str] = None  # Combined Statistical Area

    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class ACSSurveyData(ApiModelMixin):
    """
    American Community Survey data for a location.
    """

    population: Optional[int] = None
    households: Optional[int] = None
    median_income: Optional[int] = None
    median_age: Optional[float] = None
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class SchoolDistrict(ApiModelMixin):
    """
    School district information.

    Supports both legacy and current API field names for backward compatibility.
    """

    name: str
    district_number: Optional[str] = None
    lea_id: Optional[str] = None  # Local Education Agency ID (legacy)
    lea_code: Optional[str] = None  # Local Education Agency Code (current)
    nces_id: Optional[str] = None  # National Center for Education Statistics ID
    grade_low: Optional[str] = None  # Lowest grade served
    grade_high: Optional[str] = None  # Highest grade served
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class Demographics(ApiModelMixin):
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
class Economics(ApiModelMixin):
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
class Families(ApiModelMixin):
    """
    American Community Survey families data.
    """

    total_households: Optional[int] = None
    family_households: Optional[int] = None
    nonfamily_households: Optional[int] = None
    married_couple_households: Optional[int] = None
    single_male_households: Optional[int] = None
    single_female_households: Optional[int] = None
    average_household_size: Optional[float] = None
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class Housing(ApiModelMixin):
    """
    American Community Survey housing data.
    """

    total_housing_units: Optional[int] = None
    occupied_housing_units: Optional[int] = None
    vacant_housing_units: Optional[int] = None
    owner_occupied_units: Optional[int] = None
    renter_occupied_units: Optional[int] = None
    median_home_value: Optional[int] = None
    median_rent: Optional[int] = None
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class Social(ApiModelMixin):
    """
    American Community Survey social data.
    """

    high_school_graduate_or_higher: Optional[int] = None
    bachelors_degree_or_higher: Optional[int] = None
    graduate_degree_or_higher: Optional[int] = None
    veterans: Optional[int] = None
    veterans_percentage: Optional[float] = None
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class ZIP4Data(ApiModelMixin):
    """USPS ZIP+4 code and delivery information."""

    record_type: Optional[Dict[str, Any]] = None
    residential: Optional[bool] = None
    carrier_route: Optional[Dict[str, Any]] = None
    plus4: Optional[List[str]] = None
    zip9: Optional[List[str]] = None
    facility_code: Optional[Dict[str, Any]] = None
    city_delivery: Optional[bool] = None
    valid_delivery_area: Optional[bool] = None
    exact_match: Optional[bool] = None
    building_or_firm_name: Optional[str] = None
    government_building: Optional[bool] = None
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class FederalRiding(ApiModelMixin):
    """Canadian federal electoral district information."""

    code: str
    name_english: str
    name_french: str
    ocd_id: str
    year: int
    source: str
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class ProvincialRiding(ApiModelMixin):
    """Canadian provincial electoral district information."""

    name_english: str
    name_french: str
    ocd_id: str
    is_upcoming_district: bool
    source: str
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class StatisticsCanadaData(ApiModelMixin):
    """Canadian statistical boundaries from Statistics Canada."""

    division: Dict[str, Any]
    consolidated_subdivision: Dict[str, Any]
    subdivision: Dict[str, Any]
    economic_region: str
    statistical_area: Dict[str, Any]
    cma_ca: Dict[str, Any]
    tract: str
    population_centre: Dict[str, Any]
    dissemination_area: Dict[str, Any]
    dissemination_block: Dict[str, Any]
    census_year: int
    designated_place: Optional[Dict[str, Any]] = None
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(slots=True, frozen=True)
class FFIECData(ApiModelMixin):
    """FFIEC CRA/HMDA Data (Beta)."""

    collection_year: Optional[int] = None
    msa_md_code: Optional[str] = None
    fips_state_code: Optional[str] = None
    fips_county_code: Optional[str] = None
    census_tract: Optional[str] = None
    principal_city: Optional[bool] = None
    small_county: Optional[Dict[str, Any]] = None
    split_tract: Optional[Dict[str, Any]] = None
    demographic_data: Optional[Dict[str, Any]] = None
    urban_rural_flag: Optional[Dict[str, Any]] = None
    msa_md_median_family_income: Optional[int] = None
    msa_md_median_household_income: Optional[int] = None
    tract_median_family_income_percentage: Optional[float] = None
    ffiec_estimated_msa_md_median_family_income: Optional[int] = None
    income_indicator: Optional[str] = None
    cra_poverty_criteria: Optional[bool] = None
    cra_unemployment_criteria: Optional[bool] = None
    cra_distressed_criteria: Optional[bool] = None
    cra_remote_rural_low_density_criteria: Optional[bool] = None
    previous_year_cra_distressed_criteria: Optional[bool] = None
    previous_year_cra_underserved_criterion: Optional[bool] = None
    meets_current_previous_criteria: Optional[bool] = None
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)


@dataclass(frozen=True)
class GeocodioFields:
    """
    Container for optional 'fields' returned by the Geocodio API.

    Census years are handled dynamically - access any year with fields.census2020,
    fields.census2025, etc. without needing to predefine every year.

    Note: slots removed to support dynamic field passing via **kwargs
    """

    timezone: Optional[Timezone] = None
    congressional_districts: Optional[List[CongressionalDistrict]] = None
    state_legislative_districts: Optional[List[StateLegislativeDistrict]] = None
    state_legislative_districts_next: Optional[List[StateLegislativeDistrict]] = None
    school_districts: Optional[List[SchoolDistrict]] = None

    # ACS data
    acs: Optional[ACSSurveyData] = None
    demographics: Optional[Demographics] = None
    economics: Optional[Economics] = None
    families: Optional[Families] = None
    housing: Optional[Housing] = None
    social: Optional[Social] = None

    # New fields
    zip4: Optional[ZIP4Data] = None
    ffiec: Optional[FFIECData] = None

    # Canadian fields
    riding: Optional[FederalRiding] = None
    provriding: Optional[ProvincialRiding] = None
    provriding_next: Optional[ProvincialRiding] = None
    statcan: Optional[StatisticsCanadaData] = None

    # Catch-all for any future or unknown fields from the API
    extras: Dict[str, Any] = field(default_factory=dict, repr=False)

    # Internal storage for census data (all years dynamically accessible)
    _census: Dict[str, CensusData] = field(default_factory=dict, repr=False)

    def __getattr__(self, name: str):
        """
        Dynamic attribute access for census years (census2020, census2025, etc.).

        This allows accessing census data for any year without hardcoding fields:
        - fields.census2020 → CensusData for 2020
        - fields.census2031 → CensusData for 2031 (future-proof)
        """
        # Handle censusXXXX attributes dynamically
        if name.startswith("census") and len(name) > 6 and name[6:].isdigit():
            return self._census.get(name)

        # Fall back to extras for any other unknown attributes
        if name in self.extras:
            return self.extras[name]

        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")


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


@dataclass(slots=True, frozen=True)
class ListProcessingState:
    """
    Constants for list processing states returned by the Geocodio API.
    """
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PROCESSING = "PROCESSING"


@dataclass(slots=True, frozen=True)
class ListResponse:
    """
    status, download_url, expires_at are not always present.
    """

    id: str
    file: Dict[str, Any]
    status: Optional[Dict[str, Any]] = None
    download_url: Optional[str] = None
    expires_at: Optional[str] = None
    http_response: Optional[httpx.Response] = None


@dataclass(slots=True, frozen=True)
class PaginatedResponse():
    """
    Base class for paginated responses.
    """

    current_page: int
    data: List[ListResponse]
    from_: int
    to: int
    path: str
    per_page: int
    first_page_url: str
    next_page_url: Optional[str] = None
    prev_page_url: Optional[str] = None
