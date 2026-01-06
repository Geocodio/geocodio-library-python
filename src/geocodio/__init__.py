"""
Geocodio Python Client
A Python client for the Geocodio API.
"""

from ._version import __version__
from .client import Geocodio

# Distance API exports
from .distance import (
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
)
from .models import (
    DistanceResponse,
    DistanceMatrixResponse,
    DistanceDestination,
    DistanceOrigin,
    DistanceJobResponse,
    DistanceMatrixResult,
)

__all__ = [
    "Geocodio",
    "__version__",
    # Distance types
    "Coordinate",
    "DistanceResponse",
    "DistanceMatrixResponse",
    "DistanceDestination",
    "DistanceOrigin",
    "DistanceJobResponse",
    "DistanceMatrixResult",
    # Distance mode constants
    "DISTANCE_MODE_STRAIGHTLINE",
    "DISTANCE_MODE_DRIVING",
    "DISTANCE_MODE_HAVERSINE",
    # Distance unit constants
    "DISTANCE_UNITS_MILES",
    "DISTANCE_UNITS_KM",
    # Distance order by constants
    "DISTANCE_ORDER_BY_DISTANCE",
    "DISTANCE_ORDER_BY_DURATION",
    # Distance sort constants
    "DISTANCE_SORT_ASC",
    "DISTANCE_SORT_DESC",
]
