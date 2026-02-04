import time
import logging
import sys
import os

# Add current directory to sys.path
sys.path.append(os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

try:
    from app.converter import fetch_data
except ImportError:
    # If running from inside app/ or similar, adjust
    sys.path.append(os.path.join(os.getcwd(), 'app'))
    from app.converter import fetch_data

def verify():
    print("Starting verification of GAiA API data fetching...")
    start_time = time.time()
    
    try:
        # Fetch GAiA data (which triggers the external example fetching)
        # We need to mock get_latest_api_version or just pass a version if we want to be safe, 
        # but fetch_data handles it.
        # However, get_latest_api_version might fail if network is weird, but let's try.
        # We'll pass 'gaia' as api_type.
        
        apis, examples, static, content = fetch_data(api_type='gaia', api_version='v1.8')
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\nSuccess! Data fetched in {duration:.2f} seconds.")
        print(f"Number of examples fetched: {len(examples.get('examples', {}))}")
        
        if duration > 60:
            print("WARNING: It still took over 60 seconds. Optimization might not be effective enough.")
        else:
            print("Performance looks good (under 60s).")
            
    except Exception as e:
        print(f"Error during verification: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify()
