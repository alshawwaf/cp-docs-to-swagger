# Check Point API Documentation Viewer

A modern web application for viewing and interacting with Check Point Management and GAiA API documentation through an enhanced Swagger UI interface.

## Features

### Core Functionality
- **Offline Capability**: Automatically downloads and caches API specifications locally
- **Multi-API Support**: View both Management and GAiA APIs in a unified interface
- **Version Management**: Browse and sync multiple API versions
- **Dark Mode**: Full dark mode support with instant theme switching (no flash)

### Enhanced Search
- **Instant Results**: Client-side indexing for zero-latency searches
- **Smart Ranking**: Prioritizes exact matches and operation names
- **Deep Navigation**: Automatically expands nested tags and operations upon selection
- **Professional UI**: Method badges (GET, POST, etc.) and clear hierarchy

### Documentation Pages
- **API Documentation**: Interactive Swagger UI for API exploration
- **Changelog**: View what's new in each API version
- **Versions**: Browse available API versions and their status
- **Tips & Best Practices**: Check Point's tips/best-practices page for the selected API
- **Responsive Design**: Optimized for various screen sizes

### Performance Optimizations
- Lazy loading for large specifications
- Optimized syntax highlighting
- Correctly nested tags (e.g., "Network Objects / Host")
- Local caching to reduce network requests

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/alshawwaf/cp-docs-to-swagger.git
   cd cp-docs-to-swagger
   ```

2. Create a virtual environment (recommended):

   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Application

1. Start the Flask server:

   ```bash
   python run.py
   ```

2. Open your browser and navigate to:

   ```
   http://localhost:9482
   ```

### First Run

- The application will automatically attempt to download the latest API versions
- Select your desired API type (Management or GAiA) from the landing page
- Choose the API version you want to explore
- The app will fetch and cache the documentation locally

### Syncing API Versions

Use the "Sync" button on the home page to download and process all available versions for an API type. The application also kicks off a background sync of Management and GAiA versions on startup, so the cache warms up automatically on first run.

### Running with Docker

A `Dockerfile` and `docker-compose.yml` are included. The container runs `python run.py` and publishes port `9482`; the `data/` and `logs/` directories are mounted as volumes so the cache and logs persist across restarts.

```bash
# Optional: create a .env from the template first (see Configuration)
cp .env.example .env

docker compose up -d
```

Then browse to `http://localhost:9482`.

### Deployment

In the lab, this app is deployed as the **Docs-to-Swagger** service (`swagger.<domain>`) on the shared bare-metal Ubuntu + Dokploy host (Traefik ingress + Let's Encrypt), and is surfaced from the AI DevHub launcher. Dokploy builds the included `docker-compose.yml` directly, so no application changes are needed to deploy.

## Architecture

### Backend
- **Framework**: Flask (Python)
- **Data Management**: Automated fetching, caching, and version management
- **Conversion Engine**: Converts Check Point's proprietary JSON format to OpenAPI 3.0

### Frontend
- **UI Framework**: Swagger UI 5.9.0
- **Styling**: Custom CSS with CSS variables for theming
- **Scripting**: Vanilla JavaScript for search, theme management, and interactions

### Data Flow
1. Raw JSON documentation fetched from Check Point's official sources
2. Converted to standard OpenAPI 3.0 format
3. Cached locally for offline access
4. Served through customized Swagger UI

## Project Structure

```
cp-docs-to-swagger/
├── app/
│   ├── converter/           # OpenAPI conversion package
│   │   ├── __init__.py      # Re-exports the public converter API
│   │   ├── config.py        # API endpoints, server URLs, feature flags
│   │   ├── fetcher.py       # Data fetching + version discovery from Check Point
│   │   ├── generator.py     # OpenAPI 3.0 spec generation (convert_checkpoint_to_openapi)
│   │   ├── hierarchy.py     # Builds tag hierarchy from content.json
│   │   └── schema.py        # Builds OpenAPI schemas from Check Point object defs
│   ├── static/
│   │   ├── css/             # Stylesheets (variables.css, layout.css,
│   │   │                    #   swagger-overrides.css, search.css, modal.css, ...)
│   │   ├── js/              # JavaScript (theme.js, custom-search.js,
│   │   │                    #   swagger-init.js, index.js)
│   │   ├── img/             # Images and icons
│   │   └── images/          # Additional images
│   ├── templates/           # HTML templates
│   │   ├── index.html       # Landing page
│   │   ├── swagger.html     # API documentation viewer
│   │   ├── versions.html    # Version browser
│   │   ├── changelog.html   # Changelog viewer
│   │   ├── tips.html        # Tips & Best Practices page
│   │   └── navbar.html      # Navigation component
│   ├── __init__.py          # Flask app init, logging, startup sync
│   ├── routes.py            # Application routes (incl. the /proxy passthrough)
│   └── data_manager.py      # Version discovery, download, and local caching
├── data/                    # Local cache (gitignored)
│   ├── raw/                 # Raw JSON from Check Point
│   └── processed/           # Generated OpenAPI specs
├── docs/                    # Documentation
│   ├── DEVELOPER_GUIDE.md
│   └── LOGGING.md
├── logs/                    # Application logs (gitignored)
├── scripts/                 # Utility / diagnostic scripts
│   └── process_all_versions.py
├── tests/                   # Verification scripts
├── run.py                   # Application entry point (Flask, port 9482)
├── requirements.txt         # Python dependencies (flask, requests, flask-swagger-ui)
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Compose service (publishes port 9482)
├── .env.example             # Environment variable template
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## Configuration

See `.env.example` for available configuration options. Key settings include:

- Server URLs for Management and GAiA APIs (used for the "Try it out" interactive feature)
- API version preferences
- Logging levels

> [!NOTE]
> The `CHECKPOINT_SERVER_URL` and `GAIA_SERVER_URL` variables are only used for the interactive "Try it out" feature in the Swagger UI. The application automatically fetches the latest API documentation definitions from Check Point's official online servers.


## Documentation

For detailed developer documentation, see:
- [DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md) - Architecture and development guide
- [LOGGING.md](docs/LOGGING.md) - Logging configuration
