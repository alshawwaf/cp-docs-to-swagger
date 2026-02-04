"""
Fetch GAiA API external example files
"""
import requests
import json

base_url = "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/data/v1.8"
headers = {"User-Agent": "Mozilla/5.0"}

# Try different path formats
example_paths = [
    "examples/login/login_1/example.json",
    "examples//login//login_1/example.json",  # With double slashes as shown in content.json
    "static_content/examples/login/login_1/example.json",
]

print("Trying to fetch login example...")
print("="*60)

for path in example_paths:
    url = f"{base_url}/{path}"
    print(f"\nTrying: {url}")
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {resp.status_code}")
        
        if resp.status_code == 200:
            print("✓ SUCCESS! Found the example file!")
            print("\nContent:")
            data = resp.json()
            print(json.dumps(data, indent=2))
            break
        elif resp.status_code == 404:
            print("✗ 404 Not Found")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print("\n" + "="*60)
    print("Could not find example files in any expected location")
    print("The path format in content.json might need adjustment")
