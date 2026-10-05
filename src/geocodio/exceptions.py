"""
src/geocodio/exceptions.py
Structured exception hierarchy for the Geocodio Python client.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Union

# ──────────────────────────────────────────────────────────────────────────────
# Data container
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class GeocodioErrorDetail:
    """
    A typed record returned by Geocodio on errors.
    """

    message: str
    code: Optional[int] = None  # e.g. HTTP status or internal
    errors: Optional[List[str]] = None  # field‑specific validation messages
    warnings: List[str] = field(default_factory=list)  # from ``_warnings``


# ──────────────────────────────────────────────────────────────────────────────
# Base + specific exceptions
# ──────────────────────────────────────────────────────────────────────────────


class GeocodioError(Exception):
    """Root of the library’s exception hierarchy."""

    def __init__(
        self,
        detail: Union[str, GeocodioErrorDetail],
        warnings: Optional[List[str]] = None,
    ):
        if isinstance(detail, str):
            self.detail = GeocodioErrorDetail(
                message=detail, warnings=list(warnings or [])
            )
        else:
            self.detail = detail
        super().__init__(self.detail.message)

    @property
    def warnings(self) -> List[str]:
        """
        Non-fatal advisories the API returned alongside the error.

        The API appends a ``_warnings`` key to error responses just as it does
        to successful ones, e.g. to point out a misspelled field name in a
        request that failed for an unrelated reason.
        """
        return self.detail.warnings

    def __str__(self) -> str:  # prettier default printing
        return self.detail.message


class BadRequestError(GeocodioError):
    """400 Bad Request – invalid input / validation failure."""


class InvalidRequestError(GeocodioError):
    """422 Unprocessable Entity – invalid input / validation failure."""


class AuthenticationError(GeocodioError):
    """401/403 – missing or incorrect API key, or insufficient permissions."""


class GeocodioServerError(GeocodioError):
    """5xx – Geocodio internal error."""


class DefaultHTTPError(GeocodioError):
    """Other HTTP error – 4xx or 5xx, but not one of the above."""


__all__ = [
    "GeocodioErrorDetail",
    "GeocodioError",
    "BadRequestError",
    "InvalidRequestError",
    "AuthenticationError",
    "GeocodioServerError",
    "DefaultHTTPError",
]
