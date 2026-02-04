import sys
import os
import logging
import time
import shutil

# Add current directory to sys.path
sys.path.append(os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    from app.converter import fetch_data
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'app'))
    from app.converter import fetch_data

def verify():
    print("Starting verification of Caching and Optimization...")
    
    # Clear cache first to test fresh fetch
    cache_dir = os.path.join(os.getcwd(), 'app', 'cache')
    if os.path.exists(cache_dir):
        print(f"Clearing cache directory: {cache_dir}")
        shutil.rmtree(cache_dir)
    
    # 1. Test Fresh Fetch (Optimized)
    print("\n1. Testing Fresh Fetch (Optimized)...")
    start_time = time.time()
    apis, examples, static, content = fetch_data(api_type='gaia', api_version='v1.8')
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"Fresh fetch took {duration:.2f} seconds.")
    num_examples = len(examples.get('examples', {}))
    print(f"Fetched {num_examples} examples.")
    
    if num_examples == 0:
        print("FAILED: No examples fetched.")
        return

    # Verify example content (not externalValue)
    first_key = list(examples['examples'].keys())[0]
    first_ex = examples['examples'][first_key]
    if 'external_url' in first_ex:
         print("FAILED: Found 'external_url' in example. Revert failed?")
    elif 'web' in first_ex:
         print("SUCCESS: Example contains 'web' data (embedded).")
    else:
         print(f"WARNING: Example structure unknown: {first_ex.keys()}")

    # 2. Test Cached Fetch
    print("\n2. Testing Cached Fetch...")
    start_time = time.time()
    apis, examples, static, content = fetch_data(api_type='gaia', api_version='v1.8')
    end_time = time.time()
    duration_cached = end_time - start_time
    
    print(f"Cached fetch took {duration_cached:.2f} seconds.")
    
    if duration_cached < 1.0:
        print("SUCCESS: Cached fetch was instant.")
    else:
        print("WARNING: Cached fetch took longer than expected.")

if __name__ == "__main__":
    verify()
