# Branding assets (site-owned)

Files here are served from `/user/plugins/site-branding/assets/` and picked up automatically by the `site-branding` plugin:

| File | Effect |
|---|---|
| `brand.css` | Linked on every YOURLS page. |
| `logo.svg` / `logo.png` / `logo.webp` / `logo.jpg` | Replaces the YOURLS logo in the admin header (first match wins). |
| `favicon.ico` / `favicon.png` / `favicon.svg` | Adds a `<link rel="icon">` (first match wins). |

Add a logo by committing e.g. `logo.svg` here, then `uv run ym deploy prod`. No logo file means the stock YOURLS logo stays.

(This README is blocked from web access by the site `.htaccess`.)
