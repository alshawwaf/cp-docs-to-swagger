import sys
import os
import logging
import json
from urllib.parse import quote

# Add current directory to sys.path
sys.path.append(os.getcwd())

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    from app.converter import fetch_data
    from app import app
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'app'))
    from app.converter import fetch_data
    from app import app

def verify():
    print("Starting verification of Lazy Loading...")
    
    # 1. Verify fetch_data returns URLs
    print("\n1. Verifying fetch_data...")
    apis, examples, static, content = fetch_data(api_type='gaia', api_version='v1.8')
    
    external_examples = examples.get('examples', {})
    print(f"Found {len(external_examples)} examples.")
    
    if not external_examples:
        print("FAILED: No examples found.")
        return

    # Check first example
    first_key = list(external_examples.keys())[0]
    first_ex = external_examples[first_key]
    
    if 'external_url' in first_ex:
        print(f"SUCCESS: Found external_url in example: {first_ex['external_url']}")
    else:
        print(f"FAILED: 'external_url' not found in example: {first_ex}")
        return

    # 2. Verify proxy_example endpoint
    print("\n2. Verifying /proxy_example endpoint...")
    
    test_url = first_ex['external_url']
    encoded_url = quote(test_url, safe='')
    
    with app.test_client() as client:
        # Test Request Type
        print(f"Testing request type for {test_url}...")
        resp = client.get(f'/proxy_example?url={encoded_url}&type=request')
        
        if resp.status_code == 200:
            print("SUCCESS: Proxy returned 200 OK")
            try:
                data = resp.json
                print(f"Data received (type={type(data)}): {str(data)[:100]}...")
                # It should be a dict or list (JSON), not the full wrapper
                if isinstance(data, dict) and 'web' not in data:
                     print("SUCCESS: Data looks like an extracted body (not the full wrapper).")
                elif isinstance(data, dict) and 'web' in data:
                     print("WARNING: Data looks like the full wrapper. Extraction might have failed or structure is different.")
                else:
                     print("SUCCESS: Data received.")
            except:
                print("FAILED: Response is not JSON")
        else:
            print(f"FAILED: Proxy returned {resp.status_code}")
            print(resp.data)

if __name__ == "__main__":
    verify()
