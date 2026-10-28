# yourls-site-template

This is the [Copier](https://copier.readthedocs.io) template that
[**yourls-manager**](https://github.com/RubenFixit/yourls-manager) (`ym`) uses to create and
update YOURLS site repos. `ym new`, `ym setup` and `ym template-update` run it for you, so you
normally never need to run Copier yourself.

**For installation, setup, adopting an existing install, deploying and updating, see the
[yourls-manager README](https://github.com/RubenFixit/yourls-manager#readme).**

```sh
uv tool install git+https://github.com/RubenFixit/yourls-manager
ym setup            # or: ym new my-site
```

The rest of this page is for people working on the template itself.

---

## Maintaining the template

### Layout

- `copier.yml`: questions, validators, ownership rules and the post-copy message.
- `template/`: the site files (`_subdirectory`). Files ending in `*.jinja` are rendered.
- `scripts/check_render.py`: sanity checks for a rendered site (used by CI).
- `.github/workflows/ci.yml`: renders the template with sample answers, checks the output,
  and verifies that `copier update` is a no-op.

### File ownership

`copier update` (run by `ym template-update`) does a 3-way merge of **template-owned** files
and never touches **site-owned** ones (`_skip_if_exists` in `copier.yml`).

| Template-owned (updated by `copier update`) | Site-owned (rendered once) |
|---|---|
| `pyproject.toml`, `.gitignore`, `.python-version`, `README.md` | `site.toml` |
| `overlay/.htaccess`, `overlay/health.php`, `overlay/user/config.php` | `tests/redirects.toml` |
| `overlay/user/plugins/site-branding/plugin.php` | `overlay/user/plugins/site-branding/assets/brand.css` |
| `server/config.example.php` | `overlay/user/plugins/site-branding/assets/README.md` and any added logo/favicon |
| `.github/workflows/*.yml`, `.github/dependabot.yml` | |

The template doesn't render `yourls/`, `yourls.lock.json`, `uv.lock` or `adopt-review/`.
`ym` and `uv` write them. `ym server-config` fills in placeholders in
`server/config.example.php` by matching `define( 'NAME', ... );` lines and the
`$yourls_user_passwords` block, so keep that format when you edit the file.

### Test-render

```sh
uvx copier copy --trust --vcs-ref HEAD --defaults \
  --data site_name="Example Go Links" --data site_url=https://go.example.com \
  . /tmp/demo-site
python3 scripts/check_render.py /tmp/demo-site --expect-404-plugin
```

Copier renders from Git. `--vcs-ref HEAD` includes uncommitted changes. To test through the
tool, run `ym new /tmp/demo-site --template . --vcs-ref HEAD`.

### Release

Add a `CHANGELOG.md` entry and tag `vX.Y.Z`. Sites pick up the new version with
`ym template-update`.

## License

MIT, see [LICENSE](LICENSE).
