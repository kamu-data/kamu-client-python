# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!--
Recommendation: for ease of reading, use the following order:
- Added
- Changed
- Fixed
-->

## [0.7.0] - 2025-02-25
### Added
- Support V6 layout of Kamu workspaces

## [0.6.1] - 2024-12-30
### Added
- Ability to specify engine version via an environment variable

## [0.6.0] - 2024-12-26
### Added
- Basic and token-based authentication support

## [0.5.1] - 2024-12-24
### Fixed
- Handle `file://` URL as current working directory
- Fix subprocess error not showing correct log file paths

## [0.5.0] - 2024-12-24
### Added
- Added support for `file://` URLs to automatically run a `kamu sql server` sub-process and serve data from a local workspace

## [0.4.3] - 2024-12-23
### Added
- New `utils.df_to_geojson` function

## [0.4.2] - 2024-12-23
### Changed
- Improved readme

## [0.4.1] - 2024-12-23
### Fixed
- Corrected links in readme

## [0.4.0] - 2024-12-23
### Added
- Jupyter extension auto-registers the `autovizwidget` to visualize Pandas dataframes

## [0.3.0] - 2024-12-23
### Added
- Jupyter extension that provides a convenience `%%sql` cell magic

## [0.2.0] - 2024-12-18
### Added
- Spark engine support via Livy HTTP gateway (not for production)
- Hidden different connection implementations behind `KamuConnection` interface
- `KamuConnection.query(sql)` helper method

## [0.1.2] - 2024-12-16
### Added
- Keeping a CHANGELOG
- Initial wrapper around ADBC connection
