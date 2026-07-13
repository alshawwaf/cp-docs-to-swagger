# Docs to Swagger

Convert Check Point **Management** and **GAiA** API documentation into a browsable, interactive OpenAPI 3.0 / Swagger UI.

Part of the [Dev Hub](https://github.com/alshawwaf/dev-hub) ecosystem — deploy the whole suite with [ubuntu-dokploy-ai](https://github.com/alshawwaf/ubuntu-dokploy-ai).

## Overview

Check Point publishes its Management and GAiA API references as a proprietary set of JSON files rather than a machine-readable API spec. This app fetches those files from Check Point's public documentation site, converts them into a standard OpenAPI 3.0 specification, caches the result locally, and serves it through a customized Swagger UI. The result is a searchable, versioned reference where every command can be tried against a live server through a built-in proxy.

A small Flask backend handles fetching, conversion, caching, and the "Try it out" proxy; the frontend is Swagger UI with custom search, theming, and navigation on top.

## Features

- **Two APIs, one UI** — browse the Management API (`/web_api`) and the GAiA API (`/gaia_api`) from a single landing page.
- **Automatic conversion** — Check Point's `apis.json` / `examples.json` / `content.json` are merged and converted to OpenAPI 3.0, with request/response schemas, examples, and a tag hierarchy built from the docs' own chapter structure.
- **Version management** — versions are discovered dynamically from Check Point; sync and cache any version, or pin one via configuration.
- **Offline after first sync** — processed specs are cached under `data/processed/` and served without re-fetching. A background sync warms the cache on startup.
- **Interactive "Try it out"** — the generated spec points at a local `/proxy` passthrough that forwards requests to your Check Point server, handling CORS, self-signed certificates, and the `X-chkp-sid` session header automatically.
- **Enhanced search** — client-side indexing for instant results, ranking that favors exact and operation-name matches, and deep-linking that expands nested tags on selection.
- **Docs pages** — Versions, Changelog, and Tips & Best Practices are pulled straight from Check Point for the selected API/version.
- **Dark mode** — flash-free theme switching (dark by default).

## Screenshots

<!-- Add screenshots of the landing page and Swagger UI here. -->

## Quick start

### Docker (recommended)

```bash
git clone https://github.com/alshawwaf/cp-docs-to-swagger.git
cd cp-docs-to-swagger

# Optional: seed configuration (see Configuration below)
cp .env.example .env

docker compose up -d
```

The container runs `python run.py` and publishes port **9482**; `data/` and `logs/` are mounted as volumes so the cache and logs persist across restarts. Then open <http://localhost:9482>.

### Local development

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Browse to <http://localhost:9482>. On first run the app kicks off a background sync of the Management and GAiA versions, so the cache warms up on its own. You can also trigger a full download/convert for an API type with the **Sync** button on the landing page.

## Deployment

In the Dev Hub ecosystem this app is deployed automatically by [ubuntu-dokploy-ai](https://github.com/alshawwaf/ubuntu-dokploy-ai) as the **Docs to Swagger** service at `swagger.<domain>` (Docker + Dokploy + Traefik, TLS via Let's Encrypt or a Cloudflare Tunnel), and is embedded in the Dev Hub launcher. Dokploy builds the included `docker-compose.yml` directly, so no application changes are needed to deploy.

## Configuration

Copy `.env.example` to `.env` and adjust as needed. All settings are optional — the app runs with sensible defaults.

| Variable | Default | Description |
| --- | --- | --- |
| `CHECKPOINT_SERVER_URL` | Management placeholder | Target Management server used by the Swagger **Try it out** proxy (e.g. `https://<mgmt-ip>/web_api`). |
| `GAIA_SERVER_URL` | GAiA placeholder | Target GAiA server used by **Try it out** (e.g. `https://<gaia-ip>/gaia_api`). |
| `CHECKPOINT_API_VERSION` | _empty_ | Pin a specific API version. Leave empty to auto-discover the latest. |
| `VERIFY_SSL` | `false` | Verify TLS certificates when calling Check Point servers and the docs site. `false` allows self-signed certs. |
| `SHOW_UNDOCUMENTED` | `false` | Include commands flagged `"documented": false` in the generated spec. |
| `LOG_LEVEL` | `INFO` | Python logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

> [!NOTE]
> `CHECKPOINT_SERVER_URL` and `GAIA_SERVER_URL` only affect the interactive **Try it out** feature — they are the servers your API calls are proxied to. The API *documentation* itself is always fetched from Check Point's public documentation servers, regardless of these values.

## How it works

1. **Discover** — available versions are read from Check Point's `versions.js`; the latest is resolved from `default_api_version`.
2. **Download** — per version, the raw `apis.json`, `examples.json`, `static_content/apis.json`, and `content.json` are fetched from `sc1.checkpoint.com` into `data/raw/`.
3. **Convert** — `app/converter/` turns the raw data into OpenAPI 3.0: paths and operations from `commands`, request/response schemas from object definitions, examples parsed from the web/CLI bodies (including CLI-string-to-JSON parsing for GAiA), and a tag hierarchy plus Redoc `x-tag-groups` built from the docs' chapter tree.
4. **Cache** — the generated spec is written to `data/processed/<api_type>/<version>/openapi.json`.
5. **Serve** — Swagger UI loads `/openapi.json`, whose `servers` block is rewritten to a local `/proxy/<base64-server>` passthrough so "Try it out" works without CORS or SSL headaches.

### Key routes

| Route | Purpose |
| --- | --- |
| `/` | Landing page (API selection, version, sync). |
| `/docs` | Swagger UI for the selected API/version. |
| `/docs/versions`, `/docs/changelog`, `/docs/tips` | Docs pages pulled from Check Point. |
| `/openapi.json` | Generated OpenAPI spec (from cache or on the fly). |
| `/api/versions` | JSON list of versions with download/processed status. |
| `/api/sync` | `POST` — download + convert all versions for an API type in the background. |
| `/proxy/<server>/<endpoint>` | Passthrough used by "Try it out". |

## Tech stack

- **Backend**: Python 3.9 · Flask · `requests` · `flask-swagger-ui`
- **Frontend**: Swagger UI 5.9.0 · vanilla JavaScript · custom CSS with CSS-variable theming
- **Packaging**: Docker (`python:3.9-slim`) + docker compose

## Project structure

```
cp-docs-to-swagger/
├── app/
│   ├── converter/        # OpenAPI conversion package
│   │   ├── config.py     #   API endpoints, server URLs, feature flags
│   │   ├── fetcher.py    #   data fetching + version discovery
│   │   ├── generator.py  #   OpenAPI 3.0 generation (convert_checkpoint_to_openapi)
│   │   ├── hierarchy.py  #   tag hierarchy from content.json
│   │   └── schema.py     #   OpenAPI schemas from Check Point object defs
│   ├── static/           # CSS, JS (theme, search, swagger init), images
│   ├── templates/        # index, swagger, versions, changelog, tips, navbar
│   ├── __init__.py       # Flask app init, logging, startup sync
│   ├── routes.py         # routes incl. the /proxy passthrough
│   └── data_manager.py   # version discovery, download, local caching
├── data/                 # local cache (gitignored): raw/ + processed/
├── docs/                 # DEVELOPER_GUIDE.md, LOGGING.md
├── scripts/              # diagnostic / batch-processing utilities
├── tests/                # verification scripts
├── run.py                # entry point (Flask, port 9482)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

## Development

- Entry point is `run.py`, which serves the Flask app on `0.0.0.0:9482`.
- Conversion logic lives entirely in `app/converter/` — start with `generator.py`.
- `scripts/process_all_versions.py` batch-downloads and converts every version.
- The `tests/` and `scripts/` directories hold standalone verification/diagnostic scripts (run them directly with Python).
- See [CONTRIBUTING.md](CONTRIBUTING.md) before opening a PR.

## Documentation

- [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) — architecture and conversion internals.
- [LOGGING.md](docs/LOGGING.md) — logging configuration.

## License

Released under the [MIT License](LICENSE).
