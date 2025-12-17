"""
src/geocodio/distance.py
Distance API types and utilities for the Geocodio Python client.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union


# ──────────────────────────────────────────────────────────────────────────────
# Distance Mode Constants
# ──────────────────────────────────────────────────────────────────────────────

DISTANCE_MODE_STRAIGHTLINE = "straightline"
DISTANCE_MODE_DRIVING = "driving"
DISTANCE_MODE_HAVERSINE = "haversine"  # Alias for straightline (backward compat)

# ──────────────────────────────────────────────────────────────────────────────
# Distance Units Constants
# ──────────────────────────────────────────────────────────────────────────────

DISTANCE_UNITS_MILES = "miles"
DISTANCE_UNITS_KM = "km"

# ──────────────────────────────────────────────────────────────────────────────
# Order By Constants
# ──────────────────────────────────────────────────────────────────────────────

DISTANCE_ORDER_BY_DISTANCE = "distance"
DISTANCE_ORDER_BY_DURATION = "duration"

# ──────────────────────────────────────────────────────────────────────────────
# Sort Order Constants
# ──────────────────────────────────────────────────────────────────────────────

DISTANCE_SORT_ASC = "asc"
DISTANCE_SORT_DESC = "desc"


# ──────────────────────────────────────────────────────────────────────────────
# Coordinate Class
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True, slots=True)
class Coordinate:
    """
    Represents a geographic coordinate with optional identifier.

    Attributes:
        lat: Latitude (-90 to 90)
        lng: Longitude (-180 to 180)
        id: Optional identifier for the coordinate

    Examples:
        >>> Coordinate(38.8977, -77.0365)
        Coordinate(lat=38.8977, lng=-77.0365, id=None)

        >>> Coordinate(38.8977, -77.0365, "white_house")
        Coordinate(lat=38.8977, lng=-77.0365, id='white_house')

        >>> Coordinate.from_input("38.8977,-77.0365,white_house")
        Coordinate(lat=38.8977, lng=-77.0365, id='white_house')

        >>> Coordinate.from_input((38.8977, -77.0365))
        Coordinate(lat=38.8977, lng=-77.0365, id=None)
    """

    lat: float
    lng: float
    id: Optional[str] = None

    def __post_init__(self):
        """Validate coordinate ranges."""
        if not -90 <= self.lat <= 90:
            raise ValueError(f"Latitude must be between -90 and 90, got {self.lat}")
        if not -180 <= self.lng <= 180:
            raise ValueError(f"Longitude must be between -180 and 180, got {self.lng}")

    @classmethod
    def from_input(
        cls,
        input_value: Union[
            "Coordinate",
            str,
            Tuple[float, float],
            Tuple[float, float, str],
            List[Union[float, str]],
            Dict[str, Any],
        ],
    ) -> "Coordinate":
        """
        Create a Coordinate from various input formats.

        Supported formats:
            - Coordinate object (returned as-is)
            - String: "lat,lng" or "lat,lng,id"
            - Tuple: (lat, lng) or (lat, lng, id)
            - List: [lat, lng] or [lat, lng, id]
            - Dict: {"lat": ..., "lng": ..., "id": ...}

        Args:
            input_value: The coordinate input in any supported format.

        Returns:
            A Coordinate instance.

        Raises:
            ValueError: If the input format is invalid or values are out of range.
        """
        if isinstance(input_value, Coordinate):
            return input_value

        if isinstance(input_value, str):
            return cls._from_string(input_value)

        if isinstance(input_value, (tuple, list)):
            return cls._from_sequence(input_value)

        if isinstance(input_value, dict):
            return cls._from_dict(input_value)

        raise ValueError(
            f"Cannot convert {type(input_value).__name__} to Coordinate. "
            f"Expected string, tuple, list, dict, or Coordinate."
        )

    @classmethod
    def _from_string(cls, value: str) -> "Coordinate":
        """Parse coordinate from string format 'lat,lng' or 'lat,lng,id'."""
        parts = [p.strip() for p in value.split(",")]

        if len(parts) < 2:
            raise ValueError(
                f"Invalid coordinate string '{value}'. "
                f"Expected format: 'lat,lng' or 'lat,lng,id'"
            )

        try:
            lat = float(parts[0])
            lng = float(parts[1])
        except ValueError as e:
            raise ValueError(
                f"Invalid coordinate values in '{value}'. "
                f"Latitude and longitude must be numbers."
            ) from e

        coord_id = parts[2] if len(parts) > 2 else None
        return cls(lat=lat, lng=lng, id=coord_id)

    @classmethod
    def _from_sequence(
        cls, value: Union[Tuple, List]
    ) -> "Coordinate":
        """Parse coordinate from tuple or list: [lat, lng] or [lat, lng, id]."""
        if len(value) < 2:
            raise ValueError(
                f"Coordinate sequence must have at least 2 elements (lat, lng), "
                f"got {len(value)}"
            )

        try:
            lat = float(value[0])
            lng = float(value[1])
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Invalid coordinate values. Latitude and longitude must be numbers."
            ) from e

        coord_id = str(value[2]) if len(value) > 2 else None
        return cls(lat=lat, lng=lng, id=coord_id)

    @classmethod
    def _from_dict(cls, value: Dict[str, Any]) -> "Coordinate":
        """Parse coordinate from dict: {'lat': ..., 'lng': ..., 'id': ...}."""
        if "lat" not in value or "lng" not in value:
            raise ValueError(
                f"Coordinate dict must have 'lat' and 'lng' keys. "
                f"Got keys: {list(value.keys())}"
            )

        try:
            lat = float(value["lat"])
            lng = float(value["lng"])
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Invalid coordinate values. Latitude and longitude must be numbers."
            ) from e

        coord_id = str(value["id"]) if "id" in value and value["id"] is not None else None
        return cls(lat=lat, lng=lng, id=coord_id)

    def to_string(self) -> str:
        """
        Convert to string format for GET requests.

        Returns:
            'lat,lng' or 'lat,lng,id' if id is set.

        Examples:
            >>> Coordinate(38.8977, -77.0365).to_string()
            '38.8977,-77.0365'

            >>> Coordinate(38.8977, -77.0365, "white_house").to_string()
            '38.8977,-77.0365,white_house'
        """
        result = f"{self.lat},{self.lng}"
        if self.id:
            result += f",{self.id}"
        return result

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dict format for POST requests.

        Returns:
            {'lat': ..., 'lng': ...} or {'lat': ..., 'lng': ..., 'id': ...} if id is set.

        Examples:
            >>> Coordinate(38.8977, -77.0365).to_dict()
            {'lat': 38.8977, 'lng': -77.0365}

            >>> Coordinate(38.8977, -77.0365, "white_house").to_dict()
            {'lat': 38.8977, 'lng': -77.0365, 'id': 'white_house'}
        """
        result: Dict[str, Any] = {"lat": self.lat, "lng": self.lng}
        if self.id:
            result["id"] = self.id
        return result

    def __str__(self) -> str:
        """Return string representation for display."""
        return self.to_string()


def normalize_distance_mode(mode: str) -> str:
    """
    Normalize distance mode, mapping haversine to straightline.

    Args:
        mode: The distance mode.

    Returns:
        The normalized mode (haversine -> straightline).
    """
    if mode == DISTANCE_MODE_HAVERSINE:
        return DISTANCE_MODE_STRAIGHTLINE
    return mode


__all__ = [
    # Mode constants
    "DISTANCE_MODE_STRAIGHTLINE",
    "DISTANCE_MODE_DRIVING",
    "DISTANCE_MODE_HAVERSINE",
    # Units constants
    "DISTANCE_UNITS_MILES",
    "DISTANCE_UNITS_KM",
    # Order by constants
    "DISTANCE_ORDER_BY_DISTANCE",
    "DISTANCE_ORDER_BY_DURATION",
    # Sort constants
    "DISTANCE_SORT_ASC",
    "DISTANCE_SORT_DESC",
    # Classes
    "Coordinate",
    # Functions
    "normalize_distance_mode",
]
