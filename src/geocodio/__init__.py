"""
Geocodio Python Client
A Python client for the Geocodio API.
"""

from ._version import __version__
from .client import GeocodioClient

__all__ = ["GeocodioClient", "__version__"]
