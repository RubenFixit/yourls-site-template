# yourls-site-template

This is the [Copier](https://copier.readthedocs.io) template that [**yourls-manager**](https://github.com/RubenFixit/yourls-manager) (`ym`) uses to create and update YOURLS site repos. `ym new`, `ym init` and `ym template update` run it for you, so you normally never need to run Copier yourself.

**For installation, setup, adopting an existing install, deploying and updating, see the [yourls-manager README](https://github.com/RubenFixit/yourls-manager#readme).**

```sh
uv tool install git+https://github.com/RubenFixit/yourls-manager
ym init             # or: ym new my-site
```

The rest of this page is for people working on the template itself.

---

## Maintaining the template

### Layout

- `copier.yml`: questions, validators, ownership rules and the post-copy message.
- `template/`: the site files (`_subdirectory`). Files ending in `*.jinja` are rendered.
- `scripts/check_render.py`: sanity checks for a rendered site (used by CI).
- `.github/workflows/ci.yml`: renders the template with sample answers (rsync and sftp targets; GitHub, GitLab and no CI; with and without release artifacts), checks the output, validates the CI files against GitLab's and GitHub's published schemas (`check-jsonschema`), verifies that `copier update` is a no-op, and switches `ci_provider` with `copier update --data`.

### File ownership

`copier update` (run by `ym template update`) does a 3-way merge of **template-owned** files and never touches **site-owned** ones (`_skip_if_exists` in `copier.yml`).

| Template-owned (updated by `copier update`) | Site-owned (rendered once) |
|---|---|
| `pyproject.toml`, `.gitignore`, `.python-version`, `README.md` | `site.toml` |
| `overlay/.htaccess`, `overlay/health.php`, `overlay/user/config.php` | `tests/redirects.toml` |
| `overlay/user/plugins/site-branding/plugin.php` | `overlay/user/plugins/site-branding/assets/brand.css` |
| `server/config.example.php` | `overlay/user/plugins/site-branding/assets/README.md` and any added logo/favicon |
| `.github/workflows/*.yml`, `.github/dependabot.yml` (`ci_provider = github`) | |
| `.gitlab-ci.yml` (`ci_provider = gitlab`) | |

The template doesn't render `yourls/`, `yourls.lock.json`, `uv.lock` or `adopt-review/`. `ym` and `uv` write them. `ym target config` fills in placeholders in `server/config.example.php` by matching `define( 'NAME', ... );` lines and the `$yourls_user_passwords` block, so keep that format when you edit the file.

### Test-render

```sh
uvx copier copy --trust --vcs-ref HEAD --defaults \
  --data site_name="Example Go Links" --data site_url=https://go.example.com \
  . /tmp/demo-site
python3 scripts/check_render.py /tmp/demo-site --expect-404-plugin

# an SFTP-only site (deploy_type=sftp: no php_binary question, sftp prod target)
uvx copier copy --trust --vcs-ref HEAD --defaults \
  --data site_name="Example Go Links" --data site_url=https://go.example.com \
  --data deploy_type=sftp --data deploy_host=ssh.example.com --data deploy_user=me \
  . /tmp/demo-sftp
python3 scripts/check_render.py /tmp/demo-sftp --expect-404-plugin --expect-target --expect-type sftp

# GitLab CI, publishing release artifacts, no deploy target (an artifact-only site)
uvx copier copy --trust --vcs-ref HEAD --defaults \
  --data site_name="App Backend" --data site_url=https://go.example.com \
  --data ci_provider=gitlab --data release_artifact=true \
  . /tmp/demo-gitlab
python3 scripts/check_render.py /tmp/demo-gitlab --expect-404-plugin --expect-provider gitlab --expect-artifact
```

`deploy_type` (`rsync` or `sftp`) switches the prod target in `site.toml` and the deploy instructions in the generated README. Copier validates every question's default before it prompts, so a default must always pass its own validator (and `when:`-skipped questions must still have a valid default).

**CI provider.** `ci_provider` (`github`, `gitlab`, `none`) picks the CI files. They live at their real paths, `template/.github/` and `template/.gitlab-ci.yml.jinja`, and `_exclude` in `copier.yml` leaves out the ones the answers don't use (patterns there match the rendered path, without `.jinja`), so Copier never writes the unused files and `copier update --data ci_provider=...` (`ym template update --data ...`) removes the old ones. Keep the jobs of both providers equivalent: `deploy` (release tags, only `ci = true` targets), `check-updates` and, with `release_artifact`, `publish` (`ym artifact build`, then a GitHub release or GitLab's Generic Package Registry + release). `release_artifact` also writes `[artifact]` to `site.toml`, active or commented out.

Copier renders from Git. `--vcs-ref HEAD` includes uncommitted changes. To test through the tool, run `ym new /tmp/demo-site --template . --vcs-ref HEAD`.

### Release

Add a `CHANGELOG.md` entry and tag `vX.Y.Z`. Sites pick up the new version with `ym template update`.

## License

MIT, see [LICENSE](LICENSE).
