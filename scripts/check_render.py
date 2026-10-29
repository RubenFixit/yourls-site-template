"""Sanity-check a site rendered from this template.

Usage: python scripts/check_render.py <rendered-site-dir> [--expect-404-plugin]
       [--expect-target] [--expect-type rsync|sftp] [--expect-ci]
       [--expect-provider github|gitlab|none] [--expect-artifact]

Stdlib only. Checks expected files, TOML parsing and site.toml shape, leftover Jinja
markers (outside GitHub Actions ${{ }} expressions), and `php -l` when php is available.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

EXPECTED = [
    ".copier-answers.yml",
    ".gitignore",
    ".python-version",
    "pyproject.toml",
    "site.toml",
    "README.md",
    "overlay/.htaccess",
    "overlay/health.php",
    "overlay/user/config.php",
    "overlay/user/plugins/site-branding/plugin.php",
    "overlay/user/plugins/site-branding/assets/brand.css",
    "server/config.example.php",
    "tests/redirects.toml",
]
# CI files per ci_provider; the other providers' files must not be rendered.
CI_FILES = {
    "github": [
        ".github/workflows/deploy.yml",
        ".github/workflows/check-updates.yml",
        ".github/dependabot.yml",
    ],
    "gitlab": [".gitlab-ci.yml"],
    "none": [],
}
GITHUB_PUBLISH = ".github/workflows/publish.yml"
SITE_KEYS = {"site", "core", "plugins", "build", "deploy", "release", "artifact"}
TARGET_KEYS = {
    "type", "host", "user", "port", "path", "php", "config_file",
    "backup_dir", "protect", "backup_keep", "url", "state_dir", "accept", "ci",
}
# Keys that only rsync targets use (ym warns about them on sftp targets).
RSYNC_ONLY_KEYS = {"php", "backup_dir", "backup_keep"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("site", type=Path)
    ap.add_argument("--expect-404-plugin", action="store_true")
    ap.add_argument("--expect-target", action="store_true")
    ap.add_argument("--expect-type", choices=["rsync", "sftp"], default="rsync")
    ap.add_argument("--expect-ci", action="store_true", help="prod must have ci = true")
    ap.add_argument("--expect-provider", choices=sorted(CI_FILES), default="github")
    ap.add_argument(
        "--expect-artifact", action="store_true", help="[artifact] enabled + a publish job"
    )
    args = ap.parse_args()
    root: Path = args.site
    errors: list[str] = []

    expected = EXPECTED + CI_FILES[args.expect_provider]
    if args.expect_artifact and args.expect_provider == "github":
        expected.append(GITHUB_PUBLISH)
    for rel in expected:
        if not (root / rel).is_file():
            errors.append(f"missing file: {rel}")
    unexpected = {f for files in CI_FILES.values() for f in files} | {GITHUB_PUBLISH}
    for rel in sorted(unexpected - set(expected)):
        if (root / rel).exists():
            errors.append(f"unexpected file for ci_provider={args.expect_provider}: {rel}")
    if args.expect_provider != "github" and (root / ".github").exists():
        errors.append(".github/ rendered although ci_provider is not github")
    gitlab_ci = root / ".gitlab-ci.yml"
    if gitlab_ci.is_file():
        publishes = "ym artifact build" in gitlab_ci.read_text("utf-8")
        if publishes is not args.expect_artifact:
            errors.append(f".gitlab-ci.yml: publish job present = {publishes}, expected {args.expect_artifact}")
    for bad in ("dist", "yourls"):
        if (root / bad).exists():
            errors.append(f"unexpected path rendered: {bad}")
    if any(root.rglob("*.jinja")):
        errors.append("rendered output contains *.jinja files")

    tomls = {}
    for path in sorted(root.rglob("*.toml")):
        try:
            tomls[path.relative_to(root).as_posix()] = tomllib.loads(path.read_text("utf-8"))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"TOML parse error in {path}: {exc}")

    site = tomls.get("site.toml")
    if site is not None:
        unknown = set(site) - SITE_KEYS
        if unknown:
            errors.append(f"site.toml: unknown top-level keys {sorted(unknown)}")
        s = site.get("site", {})
        if not re.fullmatch(r"[a-z0-9-]+", s.get("slug", "")):
            errors.append("site.toml: [site].slug invalid")
        if not s.get("url", "").startswith("https://") or s["url"].endswith("/"):
            errors.append("site.toml: [site].url invalid")
        if not re.fullmatch(r"\d+\.\d+(\.\d+)?", site.get("core", {}).get("version", "")):
            errors.append("site.toml: [core].version invalid")
        artifact = site.get("artifact")
        if args.expect_artifact:
            if not (artifact and artifact.get("enabled") is True):
                errors.append("site.toml: [artifact] enabled = true expected")
            elif not set(artifact.get("formats", [])) <= {"tar.gz", "zip"}:
                errors.append("site.toml: [artifact].formats invalid")
        elif artifact is not None:
            errors.append("site.toml: [artifact] should be commented out")
        else:
            text = (root / "site.toml").read_text("utf-8")
            block = re.search(r"^# \[artifact\]\n(?:^# .*\n?)+", text, re.M)
            try:
                art = tomllib.loads(re.sub(r"^# ", "", block[0], flags=re.M))["artifact"]
                if art.get("enabled") is not True:
                    errors.append("site.toml: commented-out [artifact] should enable it")
            except (TypeError, tomllib.TOMLDecodeError, KeyError) as exc:
                errors.append(f"site.toml: commented-out [artifact] missing or invalid: {exc}")
        names = [p.get("name") for p in site.get("plugins", [])]
        if "site-branding" not in names:
            errors.append("site.toml: site-branding plugin missing")
        if args.expect_404_plugin and "404-if-not-found" not in names:
            errors.append("site.toml: 404-if-not-found plugin expected")
        targets = site.get("deploy", {}).get("targets", {})
        if args.expect_target:
            prod = targets.get("prod")
            if not prod:
                errors.append("site.toml: [deploy.targets.prod] expected")
            else:
                if set(prod) - TARGET_KEYS:
                    errors.append(f"site.toml: unknown target keys {sorted(set(prod) - TARGET_KEYS)}")
                if prod.get("ci", False) is not args.expect_ci:
                    errors.append(f"site.toml: prod ci = {prod.get('ci', False)}, expected {args.expect_ci}")
                if prod.get("type") != args.expect_type or not prod.get("host"):
                    errors.append(f"site.toml: prod target must be {args.expect_type} with a host")
                if args.expect_type == "sftp" and set(prod) & RSYNC_ONLY_KEYS:
                    errors.append(
                        f"site.toml: sftp target has rsync-only keys {sorted(set(prod) & RSYNC_ONLY_KEYS)}"
                    )
        elif targets:
            errors.append("site.toml: prod target should be commented out when no host given")
        else:
            # the commented-out target must become valid TOML of the expected type when
            # uncommented
            text = (root / "site.toml").read_text("utf-8")
            block = re.search(r"^# \[deploy\.targets\.prod\]\n(?:^# .*\n?)+", text, re.M)
            if not block:
                errors.append("site.toml: commented-out [deploy.targets.prod] missing")
            else:
                uncommented = re.sub(r"^# ", "", block[0], flags=re.M)
                try:
                    prod = tomllib.loads(uncommented)["deploy"]["targets"]["prod"]
                    if prod.get("type") != args.expect_type:
                        errors.append(
                            f"site.toml: commented-out prod target is not {args.expect_type}"
                        )
                except (tomllib.TOMLDecodeError, KeyError) as exc:
                    errors.append(f"site.toml: commented-out prod target is invalid: {exc}")

    redirects = tomls.get("tests/redirects.toml")
    if redirects is not None:
        for i, case in enumerate(redirects.get("case", [])):
            if "path" not in case or "status" not in case:
                errors.append(f"tests/redirects.toml: case {i} needs path and status")

    pyproject = tomls.get("pyproject.toml", {})
    src = pyproject.get("tool", {}).get("uv", {}).get("sources", {}).get("yourls-manager", {})
    if not (src.get("git") and src.get("tag")):
        errors.append("pyproject.toml: [tool.uv.sources] yourls-manager git+tag missing")
    if pyproject.get("tool", {}).get("uv", {}).get("package") is not False:
        errors.append("pyproject.toml: [tool.uv] package = false missing")

    marker = re.compile(r"\{%|%\}|\{\{|\}\}|\{#|#\}")
    for path in sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts):
        text = path.read_text("utf-8", errors="replace")
        for lineno, line in enumerate(text.splitlines(), 1):
            stripped = re.sub(r"\$\{\{.*?\}\}", "", line)
            if marker.search(stripped):
                errors.append(f"leftover template marker: {path.relative_to(root)}:{lineno}: {line.strip()}")

    php = shutil.which("php")
    if php:
        for path in sorted(root.rglob("*.php")):
            res = subprocess.run([php, "-l", str(path)], capture_output=True, text=True)
            if res.returncode != 0:
                errors.append(f"php -l failed for {path}: {res.stdout}{res.stderr}")
    else:
        print("note: php not found; skipped php -l")

    for err in errors:
        print(f"ERROR: {err}")
    print(f"{'FAILED' if errors else 'OK'}: {root} ({len(errors)} problem(s))")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
