from flask import Flask
import os
import logging
from logging.handlers import RotatingFileHandler
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration defaults
CHECKPOINT_SERVER_URL = os.getenv('CHECKPOINT_SERVER_URL', 'https://203.0.113.100:443/web_api')
GAIA_SERVER_URL = os.getenv('GAIA_SERVER_URL', 'https://203.0.113.100:443/gaia_api')
# Default to None to trigger dynamic discovery
CHECKPOINT_API_VERSION = os.getenv('CHECKPOINT_API_VERSION', None)
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

def setup_logging():
    """Configure logging to output to both console and file"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Set log level from environment variable
    log_level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Create file handler with rotation (max 10MB, keep 5 backup files)
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    
    # Create app-specific logger
    app_logger = logging.getLogger('checkpoint_api')
    app_logger.setLevel(log_level)
    
    return app_logger

# Initialize logging
logger = setup_logging()
logger.info(f"Application starting with log level: {LOG_LEVEL}")

app = Flask(__name__)

# Import routes after app is created to avoid circular imports
from app import routes

# Trigger background sync on startup
def startup_sync():
    import requests
    import time
    import threading
    
    def sync():
        # Wait for server to start
        time.sleep(5)
        try:
            logger.info("Triggering startup sync...")
            # We can call the internal function directly or hit the endpoint
            # Hitting endpoint is safer to avoid context issues, but requires URL
            # Let's call the internal logic via data_manager directly
            from app.data_manager import get_online_versions, download_version_data, load_local_data, save_processed_spec, is_version_processed
            from app.converter import convert_checkpoint_to_openapi
            
            for api_type in ['management', 'gaia']:
                versions = get_online_versions(api_type)
                for v in versions:
                    if not is_version_processed(api_type, v):
                        logger.info(f"Startup sync: Processing {api_type} {v}...")
                        if download_version_data(api_type, v):
                            data = load_local_data(api_type, v)
                            if data:
                                try:
                                    spec = convert_checkpoint_to_openapi(api_type, None, v, data_source=data)
                                    save_processed_spec(api_type, v, spec)
                                except Exception as e:
                                    logger.error(f"Failed to convert {v}: {e}")
        except Exception as e:
            logger.error(f"Startup sync failed: {e}")

    thread = threading.Thread(target=sync)
    thread.daemon = True
    thread.start()

startup_sync()
