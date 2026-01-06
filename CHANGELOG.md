# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.0] - 2026-01-06

### Added
- **Distance API support** with new methods for calculating distances between coordinates:
  - `distance()` - Calculate distances from a single origin to multiple destinations
  - `distance_matrix()` - Calculate distances from multiple origins to multiple destinations
  - Support for `straightline` (haversine) and `driving` distance modes
  - Support for `miles` and `km` units
  - Optional sorting by distance or duration
- New `Coordinate` class for representing geographic coordinates with optional IDs
- Distance parameters for `geocode()` and `reverse()` methods to calculate distances inline
- Comprehensive type definitions: `DistanceResponse`, `DistanceMatrixResponse`, `DistanceOrigin`, `DistanceDestination`
- Distance mode constants: `DISTANCE_MODE_STRAIGHTLINE`, `DISTANCE_MODE_DRIVING`
- Distance unit constants: `DISTANCE_UNITS_MILES`, `DISTANCE_UNITS_KM`

## [0.2.0] - 2025-08-08

### Changed
- **BREAKING**: Renamed main client class from `GeocodioClient` to `Geocodio` for simplicity and consistency with other SDKs
  - Migration: Change imports from `from geocodio import GeocodioClient` to `from geocodio import Geocodio`
  - Migration: Update instantiation from `client = GeocodioClient(...)` to `client = Geocodio(...)`

## [0.1.0] - 2025-08-08

### Added
- Initial release of the official Python client for the Geocodio API
- Forward geocoding for single addresses and batch operations (up to 10,000 addresses)
- Reverse geocoding for single coordinates and batch operations
- List API support for managing large batch jobs
- Field appending capabilities (census data, timezone, congressional districts, etc.)
- Comprehensive error handling with structured exception hierarchy
- Full test coverage with unit and end-to-end tests
- Support for Geocodio Enterprise API via hostname parameter
- Modern async-capable HTTP client using httpx
- Type hints and dataclass models for better IDE support
- GitHub Actions CI/CD pipeline for automated testing and publishing

## Release Process

When ready to release:
1. Update the version in `pyproject.toml`
2. Move all "Unreleased" items to a new version section with date
3. Commit with message: `chore: prepare release vX.Y.Z`
4. Tag the release: `git tag vX.Y.Z`
5. Push tags: `git push --tags`
6. GitHub Actions will automatically publish to PyPI

[Unreleased]: https://github.com/Geocodio/geocodio-library-python/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/Geocodio/geocodio-library-python/compare/v0.4.0...v0.5.0
[0.2.0]: https://github.com/Geocodio/geocodio-library-python/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Geocodio/geocodio-library-python/releases/tag/v0.1.0