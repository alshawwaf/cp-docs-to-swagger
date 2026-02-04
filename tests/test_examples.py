"""
Test script to investigate the structure of Check Point's examples.json
and understand how to properly extract and map examples.
"""
import requests
import json

def test_examples_structure(api_type='gaia', api_version='v1.8'):
    """Fetch and analyze examples.json structure"""
    
    api_configs = {
        'management': 'https://sc1.checkpoint.com/documents/latest/APIs/',
        'gaia': 'https://sc1.checkpoint.com/documents/latest/GaiaAPIs/'
    }
    
    base_url = api_configs.get(api_type)
    url = f"{base_url}data/{api_version}/dynamic/examples.json"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": f"{base_url}?"
    }
    
    print(f"Fetching examples from: {url}")
    print("="*60)
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {resp.status_code}")
        print(f"Content-Type: {resp.headers.get('Content-Type')}")
        print(f"Content Length: {len(resp.content)} bytes")
        print()
        
        if resp.status_code == 200:
            data = resp.json()
            
            # Check structure
            print("Top-level keys:", list(data.keys()))
            print()
            
            if 'examples' in data:
                examples = data['examples']
                print(f"Number of examples: {len(examples)}")
                print()
                
                # Show first few example keys
                example_keys = list(examples.keys())[:5]
                print("First 5 example keys:")
                for key in example_keys:
                    print(f"  - {key}")
                print()
                
                # Look for login example
                login_examples = {k: v for k, v in examples.items() if 'login' in k.lower()}
                print(f"Found {len(login_examples)} login-related examples:")
                for key in login_examples.keys():
                    print(f"  - {key}")
                print()
                
                # Show structure of first login example
                if login_examples:
                    first_key = list(login_examples.keys())[0]
                    first_example = login_examples[first_key]
                    print(f"Structure of '{first_key}':")
                    print(json.dumps(first_example, indent=2))
                else:
                    # Show structure of any first example
                    if examples:
                        first_key = list(examples.keys())[0]
                        first_example = examples[first_key]
                        print(f"Structure of first example '{first_key}':")
                        print(json.dumps(first_example, indent=2)[:1000])
            else:
                print("No 'examples' key found in response")
                print("Response structure:")
                print(json.dumps(data, indent=2)[:500])
        else:
            print(f"Failed to fetch: {resp.status_code}")
            print(resp.text[:500])
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("Testing GAiA API examples...")
    test_examples_structure('gaia', 'v1.8')
    
    print("\n" + "="*60)
    print("\nTesting Management API examples...")
    test_examples_structure('management', 'v2.0.1')
