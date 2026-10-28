# yourls-site-template

[Copier](https://copier.readthedocs.io) template that generates a **site repo** for a
[YOURLS](https://yourls.org) URL shortener managed by
[yourls-manager](https://github.com/RubenFixit/yourls-manager).

The generated repo holds the complete site configuration in Git: YOURLS core and plugins
vendored at locked commits, a site overlay (config shim, health endpoint, `.htaccess`,
branding), redirect tests and GitHub workflows. Secrets stay on the server.
First-class target: shared hosting (e.g. DreamHost) deployed with SSH + rsync.

## Create a site

```sh
uvx copier copy gh:RubenFixit/yourls-site-template my-site
cd my-site
```

Then follow the printed next steps (`uv sync`, `uv run ym core --version ...`,
`uv run ym sync`, create the server-local config, `uv run ym deploy prod --dry-run`, commit).

Questions asked: site name, URL, slug, GitHub owner, YOURLS version, yourls-manager tag,
deploy host/user/port/path, PHP binary (DreamHost: `/usr/local/php83/bin/php`), and whether
to include example plugins. Leaving the deploy host empty writes the prod target commented out.

## Update a site

```sh
cd my-site
uvx copier update                                   # pull template changes
uvx copier update --data manager_version=v0.2.0     # also bump the yourls-manager pin
uv lock
```

## File ownership

`copier update` 3-way-merges **template-owned** files and never touches **site-owned** ones
(`_skip_if_exists` in `copier.yml`).

| Template-owned (updated by `copier update`) | Site-owned (rendered once) |
|---|---|
| `pyproject.toml`, `.gitignore`, `.python-version`, `README.md` | `site.toml` |
| `overlay/.htaccess`, `overlay/health.php`, `overlay/user/config.php` | `tests/redirects.toml` |
| `overlay/user/plugins/site-branding/plugin.php` | `overlay/user/plugins/site-branding/assets/brand.css` |
| `server/config.example.php` | `overlay/user/plugins/site-branding/assets/README.md` and any added logo/favicon |
| `.github/workflows/*.yml`, `.github/dependabot.yml` | |

`yourls/`, `yourls.lock.json` and `uv.lock` are not rendered by the template at all; they are
written by `ym` and `uv`.

## Repository layout

- `copier.yml` - questions, validators, ownership rules.
- `template/` - the site files (`_subdirectory`); `*.jinja` files are rendered.
- `scripts/check_render.py` - sanity checks for a rendered site (used by CI).
- `.github/workflows/ci.yml` - renders the template with sample answers, checks the output,
  and verifies `copier update` is a no-op.

## Developing

```sh
uvx copier copy --defaults --vcs-ref HEAD \
  --data site_name="Example Go Links" --data site_url=https://go.example.com \
  . /tmp/demo-site
python3 scripts/check_render.py /tmp/demo-site --expect-404-plugin
```

Copier renders from git: commit before testing (or use `--vcs-ref HEAD`, which includes
uncommitted changes). Release by adding a CHANGELOG entry and tagging `vX.Y.Z`.

## License

MIT, see [LICENSE](LICENSE).
