import requests
import json

base_url = "https://sc1.checkpoint.com/documents/latest/APIs/data/v1.9/"
files = ["changes.json", "dynamic/changes.json", "static_content/changes.json"]

for f in files:
    url = base_url + f
    print(f"Checking {url}...")
    try:
        resp = requests.get(url, verify=False)
        if resp.status_code == 200:
            print(f"FOUND: {url}")
            try:
                data = resp.json()
                print("Structure keys:", list(data.keys()))
                if isinstance(data, list) and len(data) > 0:
                    print("First item keys:", list(data[0].keys()))
                    print("Sample item:", json.dumps(data[0], indent=2))
                elif isinstance(data, dict):
                    print("Keys:", list(data.keys()))
            except Exception as e:
                print(f"Failed to parse JSON: {e}")
        else:
            print(f"Status: {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")
