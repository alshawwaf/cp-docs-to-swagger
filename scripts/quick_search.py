"""
Search for the specific example value in GAiA API JSON files
"""
import requests
import json

# Download the apis.json file
url = "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/data/v1.8/dynamic/apis.json"
headers = {"User-Agent": "Mozilla/5.0"}

print("Downloading GAiA API data...")
resp = requests.get(url, headers=headers, timeout=30)
data = resp.json()

# Search for the specific IP
search_value = "44.4.44.0"
print(f"\nSearching for '{search_value}'...")

# Convert to string and search
json_str = json.dumps(data)
if search_value in json_str:
    print(f"✓ Found '{search_value}' in the data!")
    
    # Find the context
    idx = json_str.find(search_value)
    context_start = max(0, idx - 500)
    context_end = min(len(json_str), idx + 500)
    
    print("\nContext around the match:")
    print(json_str[context_start:context_end])
else:
    print(f"✗ '{search_value}' not found in apis.json")
    
    # Try searching for "admin" and "secret" for login
    if '"admin"' in json_str and '"secret"' in json_str:
        print("\n✓ But found 'admin' and 'secret'!")
        admin_idx = json_str.find('"admin"')
        print(f"\nContext around 'admin':")
        print(json_str[max(0, admin_idx-300):admin_idx+300])
    else:
        print("\n✗ 'admin' and 'secret' also not found")
        print("\nThis confirms: GAiA API examples are NOT in the JSON files")
        print("They must be hardcoded in Check Point's frontend UI")
