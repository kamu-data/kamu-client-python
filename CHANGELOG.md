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

## [0.2.0] - 2024-12-18
### Added
- Spark engine support via Livy HTTP gateway (not for production)
- Hidden different connection implementations behind `KamuConnection` interface
- `KamuConnection.query(sql)` helper method

## [0.1.2] - 2024-12-16
### Added
- Keeping a CHANGELOG
- Initial wrapper around ADBC connection
