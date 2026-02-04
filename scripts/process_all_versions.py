import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.data_manager import get_online_versions, download_version_data, load_local_data, save_processed_spec
from app.converter import convert_checkpoint_to_openapi

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('process_all')

def process_all():
    logger.info("Starting full synchronization of all API versions...")
    
    for api_type in ['management', 'gaia']:
        logger.info(f"Checking versions for {api_type}...")
        versions = get_online_versions(api_type)
        
        if not versions:
            logger.warning(f"No versions found for {api_type}")
            continue
            
        logger.info(f"Found {len(versions)} versions: {versions}")
        
        for v in versions:
            logger.info(f"Processing {api_type} {v}...")
            
            # 1. Download Data
            if not download_version_data(api_type, v):
                logger.error(f"Failed to download data for {v}")
                continue
                
            # 2. Load Data
            data = load_local_data(api_type, v)
            if not data:
                logger.error(f"Failed to load local data for {v}")
                continue
                
            # 3. Convert (Force regeneration)
            try:
                logger.info(f"Converting {v} to OpenAPI spec...")
                # We pass None for server_url, it will use defaults. 
                # The runtime app will override this with the proxy URL anyway.
                spec = convert_checkpoint_to_openapi(api_type, None, v, data_source=data)
                
                # 4. Save
                save_processed_spec(api_type, v, spec)
                logger.info(f"Successfully processed {v}")
            except Exception as e:
                logger.error(f"Failed to convert {v}: {e}", exc_info=True)

    logger.info("Full synchronization completed.")

if __name__ == "__main__":
    process_all()
