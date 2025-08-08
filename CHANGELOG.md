# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Fixed

### Changed

### Deprecated

### Removed

### Security

## Release Process

When ready to release:
1. Update the version in `pyproject.toml`
2. Move all "Unreleased" items to a new version section with date
3. Commit with message: `chore: prepare release vX.Y.Z`
4. Tag the release: `git tag vX.Y.Z`
5. Push tags: `git push --tags`
6. GitHub Actions will automatically publish to PyPI

[Unreleased]: https://github.com/Geocodio/geocodio-library-python/compare/main...HEAD