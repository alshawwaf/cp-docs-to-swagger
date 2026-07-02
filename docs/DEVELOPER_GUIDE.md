# Check Point API to OpenAPI Converter - Developer Guide

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Data Flow](#data-flow)
4. [Core Components](#core-components)
5. [Conversion Process](#conversion-process)
6. [File Structure](#file-structure)
7. [Configuration](#configuration)
8. [Extending the Tool](#extending-the-tool)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### Purpose
This tool converts Check Point **Management** and **GAiA** API documentation from their proprietary JSON format into a standard OpenAPI 3.0 specification, enabling better API exploration through Swagger UI.

### Key Features
- Fetches API documentation from Check Point's official documentation site (`sc1.checkpoint.com`)
- Supports both the Management API and the GAiA API
- Merges data from multiple JSON sources (APIs, examples, content hierarchy)
- Generates a compliant OpenAPI 3.0 specification
- Provides an interactive Swagger UI interface with a built-in `/proxy` passthrough for "Try it out"
- Discovers available versions dynamically and caches processed specs locally under `data/processed/`
- Configurable target server URL and version selection

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Check Point Documentation                 │
│  https://sc1.checkpoint.com/documents/latest/APIs/data/     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ apis.json    │  │ examples.json│  │ content.json │     │
│  │ (schemas)    │  │ (samples)    │  │ (hierarchy)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                     data_manager.py                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ fetch_data() │→ │ cache_data() │→ │ load_data()  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  app/converter/ (package)                    │
│   generator.py · schema.py · hierarchy.py · fetcher.py       │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ process_cmd()│→ │ merge_data() │→ │ generate()   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                    OpenAPI 3.0 JSON                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Paths      │  │   Schemas    │  │  Examples    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      Flask Application                       │
│                                                              │
│  ┌──────────────┐                  ┌──────────────┐        │
│  │  /openapi.json│                 │  /docs       │        │
│  │  (spec)      │─────────────────→│ (Swagger UI) │        │
│  └──────────────┘                  └──────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack
- **Backend**: Python 3.x + Flask
- **API Documentation**: Swagger UI
- **Data Format**: JSON (input and output)
- **HTTP Client**: requests library

---

## Data Flow

### 1. Data Fetching (`data_manager.py`)

The `DataManager` class handles all interactions with Check Point's documentation server and local disk cache.

**Workflow:**
1.  **Check Local Cache**: Looks for files in `data/raw/<api_type>/<version>/`.
2.  **Download if Missing**: If files don't exist, fetches them from `https://sc1.checkpoint.com/documents/latest/APIs/data/<version>`.
3.  **Load Data**: Returns the JSON objects to the converter.

**Files Managed:**
1.  `dynamic/apis.json` - Core API definitions
2.  `dynamic/examples.json` - Request/response examples
3.  `static_content/apis.json` - Static definitions
4.  `dynamic/content.json` - Documentation hierarchy

**Why Multiple Files?**
- Check Point separates concerns: schema definitions, examples, and navigation are in different files
- This mirrors their web documentation structure
- Allows for modular updates to different aspects

### 2. Data Structure Analysis

#### apis.json Structure
```json
{
  "commands": [
    {
      "name": {"web": "add-host"},
      "command": {"web": "POST https://.../web_api/add-host"},
      "description": "...",
      "request": "com.checkpoint.management...HostRequestNew",
      "response": {
        "on-success": {
          "web": {
            "status-code": "200",
            "object": {"object-name": "...HostResponse"}
          }
        }
      }
    }
  ],
  "objects": [
    {
      "name": "HostRequestNew",
      "object-name": "com.checkpoint.management...HostRequestNew",
      "fields": [...],
      "under-more-fields": [...],
      "required-fields": [...]
    }
  ]
}
```

#### examples.json Structure
```json
{
  "examples": {
    "add-host/add-host": {
      "name": "add-host",
      "web": {
        "request": {"body": "{...}"},
        "response": {"body": "{...}"}
      }
    }
  }
}
```

#### content.json Structure
```json
{
  "chapters": [
    {
      "name": "Network Objects",
      "sub-chapters": [
        {
          "name": "Host",
          "commands": ["add-host", "show-host", "set-host", "delete-host"]
        }
      ]
    }
  ]
}
```

### 3. Data Merging Process

```python
# Step 1: Index objects by name
objects_map = {obj['object-name']: obj for obj in apis_data['objects']}

# Step 2: Index examples by command name
examples_map = {}
for key, ex in examples_data['examples'].items():
    # Key format: "command/example-name" or just "command"
    # We extract the command name from the key to group multiple examples
    if '/' in key:
        cmd_name = key.split('/')[0]
    else:
        cmd_name = ex.get('name')
    
    if cmd_name:
        if cmd_name not in examples_map:
            examples_map[cmd_name] = []
        examples_map[cmd_name].append(ex)

# Step 3: Build hierarchy map for tags
hierarchy_map = traverse_content_tree(content_data)
# Result: {"add-host": ["Network Objects", "Host"]}

# Step 4: For each command, merge all related data
for command in apis_data['commands']:
    request_schema = build_from_object(command.request, objects_map)
    response_schema = build_from_object(command.response, objects_map)
    
    # Enrich schemas from examples
    enrich_from_examples(request_schema, examples_map[command.name])
    
    # Add hierarchy tags
    tags = get_tags_from_hierarchy(command.name, hierarchy_map)
```

### 4. Schema Enrichment

The tool uses a multi-source approach to build complete schemas:

**Source Priority:**
1. `fields` - Standard documented fields
2. `under-more-fields` - Additional fields (color, tags, etc.)
3. `required-fields` - Required parameters with alternatives
4. **Examples** - Fields that appear in actual API responses but aren't documented in schema

**Example Enrichment:**
```python
def enrich_schema_from_example(schema, example_body):
    """
    Finds fields in example that are missing from schema
    and adds them with inferred types
    """
    for key, value in example_body.items():
        if key not in schema['properties']:
            # Infer type from example value
            schema['properties'][key] = infer_type(value)
```

This is how the `domain` field was discovered and added - it appears in response examples but not in the schema definition.

---

## Core Components

### app/converter/ (package)

The conversion logic lives in the `app/converter/` package, not a single `converter.py` file. Its public API is re-exported from `app/converter/__init__.py`. Key modules:

| Module | Responsibility |
|--------|----------------|
| `config.py` | `API_CONFIGS` (Management + GAiA endpoints), server URLs, `VERIFY_SSL`, `SHOW_UNDOCUMENTED` |
| `fetcher.py` | `get_latest_api_version()`, `fetch_data()`, `fetch_documentation_page()`, `fetch_changes_json()` |
| `generator.py` | `convert_checkpoint_to_openapi()` — the main orchestration function |
| `schema.py` | `build_schema_from_object()`, `_process_field()` |
| `hierarchy.py` | `build_hierarchy_map()` |

#### Configuration Variables (from `config.py`)
```python
CHECKPOINT_SERVER_URL    # Target Management server for "Try it out" calls
GAIA_SERVER_URL          # Target GAiA server for "Try it out" calls
CHECKPOINT_API_VERSION   # API version to document (None -> dynamic discovery)
VERIFY_SSL               # Verify upstream TLS certs (default false)
SHOW_UNDOCUMENTED        # Include undocumented API calls (default false)
```

#### Key Functions

##### `fetch_data()` (fetcher.py)
**Purpose**: Downloads all required JSON files from Check Point documentation

**Returns**: Tuple of (apis_data, examples_data, static_data, content_data)

**Error Handling**: Raises exception if core apis.json fails; continues with empty dict for optional files

##### `build_hierarchy_map(content_data)`
**Purpose**: Traverses content.json tree to map commands to their categories

**Algorithm**:
```python
1. Recursively traverse chapters/sub-chapters
2. For each command found, record its path: ["Parent", "Child"]
3. Track top-level categories in order for tag ordering
4. Return (command_map, ordered_tags)
```

**Example Output**:
```python
command_map = {"add-host": ["Network Objects", "Host"]}
ordered_tags = [
    {"name": "Network Objects", "description": ""},
    {"name": "Session Management", "description": ""}
]
```

##### `build_schema_from_object(obj_def, objects_map)`
**Purpose**: Converts Check Point object definition to OpenAPI schema

**Process**:
```python
1. Iterate through 'fields' array
2. Iterate through 'under-more-fields' array
3. For each field:
   - Extract name and description
   - Determine type (string, integer, boolean, array)
   - Check for enums (valid-values)
   - Handle list types with element-type
4. Return OpenAPI-compliant schema object
```

##### `_process_field(field, properties, required_list)`
**Purpose**: Processes a single field definition

**Type Mapping**:
| Check Point Type | OpenAPI Type | Special Handling |
|-----------------|--------------|------------------|
| string          | string       | Check valid-values for enum |
| integer         | integer      | - |
| boolean         | boolean      | - |
| list            | array        | Extract element-type for items schema |

##### `enrich_schema_from_example(schema, example_body)`
**Purpose**: Adds fields found in examples but missing from schema

**Algorithm**:
```python
1. Check if field exists in schema
2. If not, infer type from example value:
   - isinstance(value, bool) → boolean
   - isinstance(value, int) → integer
   - isinstance(value, str) → string
   - isinstance(value, list) → array
   - isinstance(value, dict) → object (recurse)
3. Add to schema with description "Inferred from example: {field_name}"
```

##### `convert_checkpoint_to_openapi()`
**Purpose**: Main orchestration function

**Process Flow**:
```python
1. fetch_data() - Get all JSON files
2. build_hierarchy_map() - Create tag structure
3. Index objects and examples
4. Create OpenAPI base structure
5. For each command:
   a. Build request schema from object definition
   b. Build response schema from object definition
   c. Find and apply examples
   d. Enrich schemas from examples
   e. Determine tags from hierarchy
   f. Create operation object
   g. Add to paths
6. Filter tags to only include those with commands
7. Return complete OpenAPI spec
```

### app/routes.py

Routes are defined in `app/routes.py` (the Flask app itself is created in `app/__init__.py`, which also configures logging and launches the startup sync). There is no `app.py`.

#### Routes

##### `GET /`
Returns the landing page (`index.html`).

##### `GET /openapi.json`
Resolves the requested `api_type` / `api_version`, loads a pre-processed spec from `data/processed/` when available (otherwise converts on the fly), rewrites the `servers` block to point at the `/proxy` endpoint, and returns the JSON spec. Accepts `api_type`, `api_version`, and `server_url` query parameters.

##### `GET /docs`
Renders the Swagger UI page from the custom `swagger.html` template (not a `flask-swagger-ui` blueprint) with a dynamically built `api_url`.

##### `GET /docs/versions`, `GET /docs/changelog`, `GET /docs/tips`
Render the Versions, Changelog, and Tips & Best Practices pages, pulling the corresponding documentation pages from Check Point.

##### `ANY /proxy/<encoded_server>/<path:endpoint>`
A transparent proxy that forwards requests to the Check Point server. The target server is URL-safe Base64-encoded into the path.

**Why is this needed?**
1.  **CORS**: Browsers block requests to the Check Point server because it doesn't send CORS headers. The proxy adds them.
2.  **SSL**: The Check Point server often uses self-signed certificates. The proxy handles the insecure connection so the browser doesn't block it.
3.  **Session Handling**: Intercepts the login response to extract the session ID (from header or body) and ensures it's passed to the frontend.

##### `GET /proxy_example`
Lazily fetches an external request/response example JSON referenced by a spec.

##### `GET /api/versions`, `POST /api/sync`
`/api/versions` lists online versions and their local download/processed status. `/api/sync` triggers a background download-and-convert pass for an API type (the "Sync" button on the home page).

#### Server / Swagger UI configuration
The Flask server listens on **port 9482** (see `run.py`). Swagger UI is initialized client-side in `swagger.html` / `app/static/js/swagger-init.js`, with the spec URL pointing at `/openapi.json` and options such as collapsed sections and filtering enabled.

---

## Session Handling

The tool implements a robust session handling mechanism to ensure seamless authentication in Swagger UI.

### The Challenge
Check Point APIs return the session ID (`sid`) in different ways depending on the version and endpoint:
1.  **Header**: `X-chkp-sid` (standard)
2.  **Body**: JSON payload `{"sid": "..."}` (common in login responses)

Swagger UI natively expects API keys in headers, but it can't automatically extract them from a response body.

### The Solution
1.  **Proxy Extraction**: The `/proxy` endpoint inspects the upstream response.
    *   It checks for the `X-chkp-sid` header.
    *   If missing, it parses the JSON body for a `sid` field.
    *   It **always** injects the found ID into the `X-chkp-sid` response header.
2.  **Frontend Capture**: The Swagger UI (`swagger.html`) has a response interceptor that:
    *   Reads the `X-chkp-sid` header from the login response.
    *   Stores it in `localStorage`.
    *   Automatically attaches it to all subsequent requests.

---

## Conversion Process

### Detailed Conversion Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ Step 1: Fetch Data from Check Point                             │
│ ───────────────────────────────────────────────────────────────│
│ • GET apis.json (required)                                      │
│ • GET examples.json (optional, enriches schemas)                │
│ • GET static_content/apis.json (optional)                       │
│ • GET content.json (required for organization)                  │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 2: Build Indices                                            │
│ ───────────────────────────────────────────────────────────────│
│ objects_map:   {object-name → object_definition}               │
│ examples_map:  {command_name → [examples]}                     │
│ hierarchy_map: {command_name → [category_path]}                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 3: Process Each Command                                     │
│ ───────────────────────────────────────────────────────────────│
│ For command in apis_data['commands']:                          │
│   1. Extract command metadata (name, path, description)         │
│   2. Lookup request object → build_schema_from_object()        │
│   3. Lookup response object → build_schema_from_object()       │
│   4. Find examples → enrich schemas with missing fields        │
│   5. Determine tags from hierarchy                              │
│   6. Build OpenAPI operation object                             │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 4: Schema Building (per object)                            │
│ ───────────────────────────────────────────────────────────────│
│ Process 'fields':              Standard properties              │
│ Process 'under-more-fields':   Additional properties (color,    │
│                                tags, groups)                     │
│ Process 'required-fields':     Required with alternatives       │
│                                (uid OR name OR rule-number)      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 5: Example Enrichment                                       │
│ ───────────────────────────────────────────────────────────────│
│ For each example:                                               │
│   • Parse request body JSON                                     │
│   • Compare with request schema                                 │
│   • Add missing fields (e.g., 'domain' discovered here)        │
│   • Repeat for response                                         │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ Step 6: Assemble OpenAPI Document                               │
│ ───────────────────────────────────────────────────────────────│
│ {                                                               │
│   "openapi": "3.0.0",                                          │
│   "info": {...},                                                │
│   "servers": [{url: CHECKPOINT_SERVER_URL}],                   │
│   "tags": [filtered_ordered_tags],                             │
│   "paths": {                                                    │
│     "/add-host": {                                              │
│       "post": {                                                 │
│         "tags": ["Network Objects / Host"],                     │
│         "requestBody": {schema: {...}},                        │
│         "responses": {                                          │
│           "200": {schema: {...}, examples: {...}}              │
│         }                                                       │
│       }                                                         │
│     }                                                           │
│   }                                                             │
│ }                                                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Structure

### Project Layout

```
cp-docs-to-swagger/
├── run.py                 # Application entry point (Flask, port 9482)
├── app/                   # Application package
│   ├── __init__.py        # App init, logging, startup sync
│   ├── routes.py          # Route definitions
│   ├── converter/         # Conversion logic package
│   │   ├── __init__.py    # Re-exports the public converter API
│   │   ├── config.py      # API endpoints, server URLs, feature flags
│   │   ├── fetcher.py     # Data fetching + version discovery
│   │   ├── generator.py   # Core OpenAPI generation
│   │   ├── hierarchy.py   # Tag hierarchy from content.json
│   │   └── schema.py      # Object -> OpenAPI schema conversion
│   ├── data_manager.py    # Version discovery, download, and caching
│   ├── templates/         # HTML templates (index, swagger, versions,
│   │                      #   changelog, tips, navbar)
│   └── static/            # Static assets
│       ├── css/           # Custom styles
│       ├── js/            # Custom scripts (custom-search.js, ...)
│       ├── img/           # Images and icons
│       └── images/        # Additional images
├── data/                  # Data storage (gitignored)
│   ├── raw/               # Raw JSON files from Check Point
│   └── processed/         # Generated OpenAPI specs
├── docs/                  # Documentation
│   ├── DEVELOPER_GUIDE.md
│   └── LOGGING.md
├── scripts/               # Utility / diagnostic scripts
│   └── process_all_versions.py
├── tests/                 # Verification scripts
├── requirements.txt       # Python dependencies
├── .env.example           # Configuration template
├── .gitignore             # Git ignore patterns
├── Dockerfile             # Docker container definition
├── docker-compose.yml     # Compose service (publishes port 9482)
├── CONTRIBUTING.md        # Contribution guide
├── LICENSE                # License file (MIT)
└── README.md              # User documentation
```

### File Responsibilities

| File | Purpose | Key Functions |
|------|---------|---------------|
| `run.py` | Entry point | Starts the Flask server on port 9482 |
| `app/__init__.py` | App init | Configures logging, creates Flask app, starts background sync |
| `app/routes.py` | Routes | Defines endpoints (`/`, `/openapi.json`, `/docs`, `/proxy`, `/api/*`) |
| `app/converter/generator.py` | Logic | `convert_checkpoint_to_openapi()` |
| `app/data_manager.py` | Data | Version discovery, download, local spec cache |
| `app/templates/` | UI | `index.html`, `swagger.html`, `versions.html`, ... |

---

## Configuration

### Environment Variables

The tool supports configuration via environment variables:

```bash
# Server URL where Check Point Management API is hosted
CHECKPOINT_SERVER_URL=https://203.0.113.100:443/web_api

# API version to document
CHECKPOINT_API_VERSION=v2.0.1
```

### Supported API Versions

Available versions are discovered dynamically from Check Point's `versions.js`, so the exact list tracks whatever Check Point publishes. Typical ranges:

- **Management API**: v1, v1.1, v1.2, v1.3, v1.4, v1.5, v1.6, v1.6.1, v1.7, v1.7.1, v1.8, v1.8.1, v1.9, v1.9.1, v2.0, v2.0.1
- **GAiA API**: v1, v1.1, v1.2, v1.3, v1.4, v1.5, v1.6, v1.7, v1.8

If discovery fails, `config.py` falls back to `v2.0.1` (Management) / `v1.8` (GAiA).

**Version Selection Impact:**
- Changes the URL path for fetching documentation
- Different versions may have different commands/fields
- Schema structure remains consistent across versions

### Configuration Loading

Configuration lives in `app/converter/config.py`. Server URLs and the version are read from the environment, and the API version defaults to `None` to trigger dynamic discovery of the latest version:

```python
# In app/converter/config.py
CHECKPOINT_SERVER_URL = os.getenv("CHECKPOINT_SERVER_URL", API_CONFIGS['management']['default_server'])
GAIA_SERVER_URL       = os.getenv("GAIA_SERVER_URL", API_CONFIGS['gaia']['default_server'])
VERIFY_SSL            = os.getenv("VERIFY_SSL", "false").lower() == "true"
CHECKPOINT_API_VERSION = os.getenv("CHECKPOINT_API_VERSION", None)  # None -> latest
SHOW_UNDOCUMENTED     = os.getenv("SHOW_UNDOCUMENTED", "false").lower() == "true"
```

---

## Extending the Tool

### Adding New Data Sources

To incorporate additional Check Point data files:

```python
# In fetch_data()
print("Fetching new_data.json...")
new_resp = requests.get(f"{base_url}/new_data.json", headers=headers)
new_data = new_resp.json() if new_resp.status_code == 200 else {}

return apis_data, examples_data, static_data, content_data, new_data
```

### Custom Field Processing

To handle special field types:

```python
# In _process_field() (app/converter/schema.py)
if field_name == 'special_field':
    # Custom handling
    prop_schema = {
        "type": "custom",
        "format": "special"
    }
```

### Adding Custom Endpoints

```python
# In app/routes.py
@app.route('/custom-endpoint')
def custom_endpoint():
    # Your logic here
    return jsonify({"status": "ok"})
```

### Modifying Tag Organization

To change how commands are grouped:

```python
# In convert_checkpoint_to_openapi()
if cmd_name in hierarchy_map:
    category_path = hierarchy_map[cmd_name]
    
    # Option 1: Use top-level only
    tags = [category_path[0]]
    
    # Option 2: Use nested format
    tags = [" / ".join(category_path[:2])]
    
    # Option 3: Use all levels
    tags = [" > ".join(category_path)]
```

### Adding Additional OpenAPI Metadata

```python
# In convert_checkpoint_to_openapi()
openapi = {
    "openapi": "3.0.0",
    "info": {
        "title": "Check Point Management API",
        "version": CHECKPOINT_API_VERSION,
        "description": "Auto-generated OpenAPI spec",
        "contact": {  # NEW
            "name": "API Support",
            "url": "https://example.com"
        },
        "license": {  # NEW
            "name": "Apache 2.0",
            "url": "https://www.apache.org/licenses/LICENSE-2.0.html"
        }
    },
    # ...
}
```

---

## Troubleshooting

### Common Issues

#### Issue: Missing Fields in Schema

**Symptom**: Fields that appear in API responses are not documented in Swagger UI

**Cause**: Field is in examples but not in apis.json schema

**Solution**: The `enrich_schema_from_example()` function should catch this automatically. Verify:
```python
# Check if examples are being processed
print(f"Processing examples for {cmd_name}: {len(cmd_examples)}")
```

#### Issue: Commands Not Grouped Correctly

**Symptom**: All commands appear under "Check Point API" tag

**Cause**: `content.json` not fetched or hierarchy parsing failed

**Debug**:
```python
# In build_hierarchy_map()
print(f"Mapped {len(command_map)} commands to categories")
print(f"Sample: {list(command_map.items())[:5]}")
```

#### Issue: Server URL Not Applied

**Symptom**: Swagger UI shows placeholder URL

**Cause**: Environment variable not set or not loaded

**Debug**:
```python
# Run tests/verify_config.py
python tests/verify_config.py
```

#### Issue: Wrong API Version Loaded

**Symptom**: Old/missing commands

**Cause**: Incorrect API version configured

**Solution**: Check environment variable:
```bash
echo $CHECKPOINT_API_VERSION  # Linux/Mac
echo $env:CHECKPOINT_API_VERSION  # Windows PowerShell
```

### Debugging Tips

1. **Enable Verbose Logging**:
```python
# In fetch_data()
print(f"Fetching: {base_url}/dynamic/apis.json")
print(f"Response status: {apis_resp.status_code}")
print(f"Response size: {len(apis_resp.text)} bytes")
```

2. **Inspect Intermediate Data**:
```python
# After building schemas
import json
with open('debug_schema.json', 'w') as f:
    json.dump(request_schema, f, indent=2)
```

3. **Test Individual Components**:
```bash
# Test data fetching only
python -c "from app.converter.fetcher import fetch_data; data = fetch_data(); print(data.keys())"
```

4. **Check OpenAPI Spec Validity**:
Use online validators like https://apitools.dev/swagger-parser/online/

---

## Development Workflow

### Making Changes

1. **Modify Code**: Edit the relevant module under `app/converter/` or `app/routes.py`
2. **Test Locally**:
   ```bash
   python tests/verify_holistic.py  # Test conversion
   python run.py                     # Start server
   ```
3. **Verify in Browser**: Check http://localhost:9482/docs
4. **Run All Tests**:
   ```bash
   python tests/verify_config.py
   python tests/verify_types.py
   python tests/verify_tags.py
   ```

### Testing Process

```python
# tests/verify_holistic.py - Example test structure
from converter import convert_checkpoint_to_openapi

spec = convert_checkpoint_to_openapi()

# Test 1: Check specific path exists
assert '/add-host' in spec['paths']

# Test 2: Check field presence
request_schema = spec['paths']['/add-host']['post']['requestBody']['content']['application/json']['schema']
assert 'properties' in request_schema

# Test 3: Check examples
examples = spec['paths']['/add-host']['post']['responses']['200']['content']['application/json']['examples']
assert len(examples) > 0
```

### Version Control

**Important Files to Track**:
- `run.py`
- `app/` (including `routes.py`, `__init__.py`, and the `converter/` package)
- `requirements.txt`
- `app/templates/`
- `README.md`
- `docs/DEVELOPER_GUIDE.md`
- `.env.example`

**Files to Ignore** (in `.gitignore`):
- `.env` (user-specific configuration)
- `__pycache__/`
- `.venv/`

---

## Performance Considerations

### Data Fetching

- Each run fetches ~4 JSON files (total ~20-30 MB)
- Network latency: 1-3 seconds typical
- Consider caching for production use

### Memory Usage

- Full OpenAPI spec: ~3-5 MB
- In-memory processing: ~50-100 MB peak
- No persistence required (stateless)

### Optimization Opportunities

1. **Caching**:
```python
import functools
import time

@functools.lru_cache(maxsize=1)
def fetch_data_cached():
    # Cache for 5 minutes
    return fetch_data()
```

2. **Lazy Loading**:
```python
# Only fetch examples if needed
if include_examples:
    examples_data = fetch_examples()
```

3. **Parallel Fetching**:
```python
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = {
        executor.submit(fetch_url, apis_url): 'apis',
        executor.submit(fetch_url, examples_url): 'examples'
    }
    results = {name: f.result() for f, name in futures.items()}
```

---

## Appendix

### OpenAPI 3.0 Reference

Key OpenAPI concepts used in this tool:

- **Paths**: API endpoints (`/add-host`)
- **Operations**: HTTP methods (`POST`)
- **RequestBody**: Input schema
- **Responses**: Output schemas (by status code)
- **Schemas**: Data models
- **Examples**: Sample requests/responses
- **Tags**: Grouping mechanism
- **Servers**: Base URLs

### Check Point API Quirks

1. **Object Naming**: Uses Java-style package names
   ```
   com.checkpoint.management.web_api.core.handler.objects.network_objects.host.HostRequestNew
   ```

2. **Field Alternatives**: Required fields can have OR logic
   ```json
   "required-fields": [{
     "name": "uid",
     "field-alternatives": [{"name": "name"}, {"name": "rule-number"}]
   }]
   ```
   Means: (uid OR name OR rule-number) is required

3. **More Fields**: Additional fields under `under-more-fields` array

4. **Type System**: Custom types mapped to OpenAPI primitives

### Useful Commands

```bash
# Convert this Markdown to Word
pandoc DEVELOPER_GUIDE.md -o DEVELOPER_GUIDE.docx

# View OpenAPI spec
curl http://localhost:9482/openapi.json | jq .

# Count total API commands
curl http://localhost:9482/openapi.json | jq '.paths | length'

# List all tags
curl http://localhost:9482/openapi.json | jq '.tags[].name'

# Pretty-print converter output
python -c "from app.converter import convert_checkpoint_to_openapi; import json; print(json.dumps(convert_checkpoint_to_openapi(), indent=2))" > spec.json
```

---

## Conclusion

This tool bridges the gap between Check Point's proprietary documentation format and the industry-standard OpenAPI specification. Understanding the data flow and conversion process is key to maintaining and extending the tool.

For questions or contributions, refer to the project README.md for contact information.

**Last Updated**: 2026-07-02
**Version**: 1.1
