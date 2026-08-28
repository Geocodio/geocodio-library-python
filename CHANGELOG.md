# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.4.0] - 2026-08-28

### Added
- Public census accessors on `GeocodioFields`: `fields.census` (the requested append, most recent vintage when several are present), `fields.get_census(year)` (accepts `2023`, `"2023"` or `"census2023"`), `fields.census_years` and `fields.census_data`. The private `fields._census` dict and the dynamic `fields.census2023` attributes are unchanged.
- `GeocodingResult.match_type` and `GeocodingResult.address_lines`, both of which the API returns on every result and the model previously dropped.
- Raw response access: `GeocodingResponse.raw` / `.to_dict()` for the full untouched JSON payload, and `GeocodingResult.raw` / `.to_dict()` for a single result. Unlike `dataclasses.asdict()` these keep every key the API sent.
- Rate limit headers are parsed into a `RateLimit` model, exposed as `GeocodingResponse.rate_limit` and `Geocodio.rate_limit` (updated on every request, including ones that raise).

## [1.3.0] - 2026-08-25

### Added
- United Kingdom data append support. The `uk-westminster`, `uk-devolved`, and `uk-local` appends (and their `-next` variants) are now parsed into a typed `UKLegislativeDistrict` model, exposed via `fields.uk_westminster`, `fields.uk_devolved`, and `fields.uk_local`.

## [1.0.0] - 2026-06-05

### Changed
- **BREAKING**: Migrated to Geocodio API **v2**. The base URL version prefix changed from `v1.x` to `v2` (`https://api.geocod.io/v2/...`).
- **BREAKING**: Removed the top-level `input` object from `/geocode` and `/reverse` responses. `GeocodingResponse.input` has been removed; parsed address information now lives in `results[].address_components`.
- **BREAKING**: Renamed `AddressComponents` fields to match API v2:
  - `zip` → `postal_code`
  - `state` → `state_province`
  - Added `unit_type` (was `secondaryunit`) and `unit_number` (was `secondarynumber`)
- Structured address input now accepts `state_province` (the legacy `state` field is still accepted for compatibility).

## [0.7.0] - 2026-03-12

### Changed
- Updated default API version to v1.11

## [0.6.0] - 2026-02-24

### Changed
- Updated default API version from v1.9 to v1.10
## [0.5.1] - 2026-02-18

### Fixed
- Fixed parsing of state legislative district data (`stateleg` field). The API response key changed from `stateleg` to `state_legislative_districts` and the structure changed from a flat list to a dict with `house`/`senate` keys containing legislator info. The library now handles both formats.

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

[Unreleased]: https://github.com/Geocodio/geocodio-library-python/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/Geocodio/geocodio-library-python/compare/v1.2.0...v1.3.0
[1.0.0]: https://github.com/Geocodio/geocodio-library-python/compare/v0.7.0...v1.0.0
[0.7.0]: https://github.com/Geocodio/geocodio-library-python/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/Geocodio/geocodio-library-python/compare/v0.5.1...v0.6.0
[0.5.1]: https://github.com/Geocodio/geocodio-library-python/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/Geocodio/geocodio-library-python/compare/v0.4.0...v0.5.0
[0.2.0]: https://github.com/Geocodio/geocodio-library-python/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/Geocodio/geocodio-library-python/releases/tag/v0.1.0