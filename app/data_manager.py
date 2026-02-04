import os
import json
import requests
import re
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger('checkpoint_api')

DATA_DIR = os.path.join(os.getcwd(), 'data')
RAW_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')

API_CONFIGS = {
    'management': {
        'name': 'Management API',
        'base_url': 'https://sc1.checkpoint.com/documents/latest/APIs/',
        'versions_url': 'https://sc1.checkpoint.com/documents/latest/APIs/js/versions.js',
    },
    'gaia': {
        'name': 'GAiA API',
        'base_url': 'https://sc1.checkpoint.com/documents/latest/GaiaAPIs/',
        'versions_url': 'https://sc1.checkpoint.com/documents/latest/GaiaAPIs/js/versions.js',
    }
}

def ensure_dirs():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)

def get_online_versions(api_type='management'):
    """Fetch available versions from the online versions.js file."""
    config = API_CONFIGS.get(api_type)
    if not config:
        return []

    try:
        logger.info(f"Fetching versions for {api_type} from {config['versions_url']}")
        response = requests.get(config['versions_url'], timeout=10)
        response.raise_for_status()
        
        # Parse JS array: var versions = [ ... ];
        # We'll use regex to extract the JSON-like array
        # The content might be spread across lines, so we need DOTALL
        # The variable name might be 'versions' or 'default_api_version' (wait, that's different)
        # In versions.js, it is: var versions = [ ... ];
        
        # Try a more robust regex that captures everything between [ and ];
        match = re.search(r'var\s+versions\s*=\s*(\[.*?\]);', response.text, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            # Clean up potential JS comments or trailing commas if any (though standard JSON doesn't allow them)
            # The curl output showed standard JSON format inside the array.
            
            try:
                versions = json.loads(json_str)
                return [v['key'] for v in versions]
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode failed: {e}. Trying regex fallback.")
                # Fallback: simple regex for "key": "v..."
                return re.findall(r'"key":\s*"([^"]+)"', json_str)
        else:
            logger.warning("Regex match failed for versions array")
            # Fallback: just search for "key": "v..." in the whole text
            return re.findall(r'"key":\s*"([^"]+)"', response.text)
    except Exception as e:
        logger.error(f"Failed to fetch versions for {api_type}: {e}")
        return []
    return []

def is_version_downloaded(api_type, version):
    """Check if raw data for a version exists locally."""
    version_dir = os.path.join(RAW_DIR, api_type, version)
    # Check for minimal required files
    return os.path.exists(os.path.join(version_dir, 'apis.json'))

def is_version_processed(api_type, version):
    """Check if processed OpenAPI spec exists locally."""
    return os.path.exists(os.path.join(PROCESSED_DIR, api_type, version, 'openapi.json'))

def download_version_data(api_type, version):
    """Download all necessary data files for a specific version."""
    config = API_CONFIGS.get(api_type)
    if not config:
        return False

    base_url = f"{config['base_url']}data/{version}"
    target_dir = os.path.join(RAW_DIR, api_type, version)
    os.makedirs(target_dir, exist_ok=True)

    files_to_fetch = [
        ('dynamic/apis.json', 'apis.json'),
        ('dynamic/examples.json', 'examples.json'),
        ('static_content/apis.json', 'static_apis.json'),
        ('dynamic/content.json', 'content.json')
    ]

    success = True
    
    def fetch_file(url_path, local_name):
        url = f"{base_url}/{url_path}"
        local_path = os.path.join(target_dir, local_name)
        
        try:
            logger.info(f"Downloading {url}...")
            from .converter.config import VERIFY_SSL
            resp = requests.get(url, timeout=30, verify=VERIFY_SSL)
            if resp.status_code == 200:
                with open(local_path, 'w', encoding='utf-8') as f:
                    f.write(resp.text)
                return True
            else:
                logger.warning(f"Failed to download {url}: {resp.status_code}")
                # Some files might be missing (e.g. static_content), that's okay-ish
                if local_name == 'apis.json': # Critical file
                    return False
                return True # Non-critical
        except Exception as e:
            logger.error(f"Error downloading {url}: {e}")
            if local_name == 'apis.json':
                return False
            return True

    # Fetch main files
    for url_path, local_name in files_to_fetch:
        if not fetch_file(url_path, local_name):
            success = False
            break
    
    if success:
        logger.info(f"Successfully downloaded raw data for {api_type} {version}")
    
    return success

def load_local_data(api_type, version):
    """Load raw data from local storage."""
    version_dir = os.path.join(RAW_DIR, api_type, version)
    data = {}
    
    try:
        with open(os.path.join(version_dir, 'apis.json'), 'r', encoding='utf-8') as f:
            data['apis'] = json.load(f)
    except FileNotFoundError:
        return None

    try:
        with open(os.path.join(version_dir, 'examples.json'), 'r', encoding='utf-8') as f:
            data['examples'] = json.load(f)
    except FileNotFoundError:
        data['examples'] = {}

    try:
        with open(os.path.join(version_dir, 'static_apis.json'), 'r', encoding='utf-8') as f:
            data['static'] = json.load(f)
    except FileNotFoundError:
        data['static'] = {}

    try:
        with open(os.path.join(version_dir, 'content.json'), 'r', encoding='utf-8') as f:
            data['content'] = json.load(f)
    except FileNotFoundError:
        data['content'] = {}
        
    return data

def save_processed_spec(api_type, version, spec):
    """Save the converted OpenAPI spec."""
    target_dir = os.path.join(PROCESSED_DIR, api_type, version)
    os.makedirs(target_dir, exist_ok=True)
    
    with open(os.path.join(target_dir, 'openapi.json'), 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2)
    
    logger.info(f"Saved processed spec for {api_type} {version}")

def get_local_spec(api_type, version):
    """Get the processed OpenAPI spec from local storage."""
    path = os.path.join(PROCESSED_DIR, api_type, version, 'openapi.json')
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None
