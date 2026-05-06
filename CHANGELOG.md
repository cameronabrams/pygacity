# Changelog

All notable changes to pygacity will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.10.2] - 2026-03-13

### Added

- Ability to generate short-answer-only exams.

## [0.10.1] - 2026-03-13

### Added

- `latexmkrc`-based build support via `SimpleAssignment_latexmkrc.yaml` example.
- Short exam example (`ShortExam.yaml`).

## [0.10.0] - 2026-03-13

### Added

- Updated example images for documentation.

## [0.9.0] - 2026-03-12

### Changed

- Upgraded to use `latexmk` and `xelatex` by default, with pythontex integration via `latexmkrc`.
- Added support for multiple pythontex workflow modes, including an "explicit" mode that runs pythontex as a separate step from latexmk.

## [0.8.0] - 2026-03-11

### Changed

- Updated preamble handling to allow for more flexible formatting.
- More transparent question numbering in the LaTeX output.

## [0.7.0] - 2026-02-22

### Added

- `distribute` subcommand for building and distributing PDF exams on a per-student basis.

## [0.6.0] - 2025-12-28

### Changed

- Enhanced pythontex integration.

## [0.5.0] - 2025-12-26

### Added

- `singlet` subcommand.

## [0.4.1] - 2025-12-26

### Fixed

- Seed handling in question selection (`pick.py`).
- Example YAML and LaTeX files updated for compatibility.

## [0.4.0] - 2025-12-26

### Added

- Usage examples.

## [0.3.0] - 2025-12-26

### Added

- Multiple-choice, short answer, and fill-in-the-blank question types.
- `combine` and `build` subcommands.

## [0.1.0] - 2025-02-27

- Initial release of pygacity.