"""
Search for loginRequest object and its example values in GAiA API
"""
import requests
import json

def find_login_request_object():
    """Find the loginRequest object definition and look for examples"""
    
    base_url = "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/data/v1.8"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/?"
    }
    
    url = f"{base_url}/dynamic/apis.json"
    resp = requests.get(url, headers=headers, timeout=10)
    data = resp.json()
    
    # Find loginRequest object
    print("Searching for loginRequest object...")
    print("="*60)
    
    if 'objects' in data:
        for obj in data['objects']:
            obj_name = obj.get('object-name') or obj.get('name')
            if obj_name and 'login' in obj_name.lower():
                print(f"\nFound object: {obj_name}")
                print(json.dumps(obj, indent=2)[:3000])
                print("\n" + "="*60)
    
    # Also check if there are any example fields in the objects
    print("\n\nSearching for 'example' or 'default' values in objects...")
    print("="*60)
    
    json_str = json.dumps(data)
    if '"example"' in json_str or '"default"' in json_str or '"sample"' in json_str:
        print("✓ Found 'example', 'default', or 'sample' fields in the data!")
        
        # Find specific instances
        if 'objects' in data:
            for obj in data['objects']:
                obj_str = json.dumps(obj)
                if '"example"' in obj_str or '"default"' in obj_str:
                    obj_name = obj.get('object-name') or obj.get('name')
                    print(f"\nObject with examples: {obj_name}")
                    print(json.dumps(obj, indent=2)[:2000])
                    break
    else:
        print("✗ No 'example', 'default', or 'sample' fields found")
        print("\nThis means GAiA API truly has no examples in any of the JSON files.")
        print("The examples shown on Check Point's website are likely hardcoded in their UI.")

if __name__ == "__main__":
    find_login_request_object()
