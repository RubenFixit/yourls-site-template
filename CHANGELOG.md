# Changelog

All notable changes to this template. Sites pick them up with `ym template-update`.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions are git tags.

## [Unreleased]

## [0.4.0] - 2026-10-28

### Changed
- New sites pin yourls-manager `v0.5.0`.
- Site README: a Plugins section with `ym plugin search/add/list/enable/disable/remove`
  (adding by hand still documented), what removing a plugin does on deploy (sftp:
  deactivate it in the admin first), `ym doctor` in the day-to-day commands, `ym update
  --commit` for routine updates, and `ym plugin apply prod` instead of `ym plugins prod`.

## [0.3.0] - 2026-10-28

### Added
- Release flow: prod gets `accept = "release"`; commented `staging` target (`accept = "any"`)
  and `[release] push_markers` in site.toml. The deploy workflow deploys final release tags
  to prod and `-rc.<n>` tags to staging (skipped without a staging target).

### Changed
- Site README documents `ym release` and the tag scheme `v<yourls>-<rev>[-rc.<n>]`, replacing
  the `vYYYY.MM.DD` advice. New sites pin yourls-manager `v0.4.0`.

### Added
- `deploy_type` question: `rsync` (default) or `sftp`, for hosts that only offer SFTP
  (needs yourls-manager v0.3.0). An sftp site gets a `type = "sftp"` prod target in
  `site.toml` (with `state_dir` documented instead of `php` / `backup_dir` / `backup_keep`)
  and a README that explains the browser steps (install/upgrade page, plugin activation)
  and that SFTP deploys don't back up the database.
- `scripts/check_render.py --expect-type rsync|sftp`; it also checks that a commented-out
  prod target is valid TOML of that type. CI renders two sftp variants.

### Changed
- `php_binary` is only asked for rsync targets.
- New sites pin yourls-manager `v0.3.0` by default.
- `site.toml` comments describe both target types and point to `ym server-config prod`.

## [0.1.1] - 2026-10-28

### Fixed
- Setting a deploy host crashed the interactive prompt (`Validation error for question
  'deploy_user'`): the empty default for `deploy_user` failed its own validator. The question
  now has no default and is asked whenever a deploy host is given. CI checks this.

### Changed
- New sites pin yourls-manager `v0.2.0` by default.
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
