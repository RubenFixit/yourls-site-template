# Changelog

All notable changes to this template. Sites pick them up with `ym template-update`.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions are git tags.

## [Unreleased]

### Changed
- Docs for yourls-manager v0.2 onboarding commands. The README now points to yourls-manager
  for all instructions and keeps only maintainer notes.
- Post-copy message is short and correct both via `ym new` and raw Copier. It points to
  `ym server-config prod` and `ym deploy prod --dry-run`.
- Generated site README uses `ym server-config`, `ym template-update` and `ym adopt`.
- `server/config.example.php` header documents `ym server-config` as the recommended install.

## [0.1.0] - 2026-10-27

### Added
- Initial template generating a YOURLS site repo for yourls-manager v0.1.0:
  `site.toml`, `pyproject.toml` (uv, git-tag pin), overlay with config shim, `health.php`,
  `.htaccess` and `site-branding` plugin, `server/config.example.php`,
  `tests/redirects.toml`, deploy / check-updates workflows and Dependabot config.
- Defaults: YOURLS 1.10.6, yourls-manager v0.1.0, Python 3.12.
