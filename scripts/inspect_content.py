import requests
import json

url = "https://sc1.checkpoint.com/documents/latest/APIs/data/v1.9/dynamic/content.json"
print(f"Fetching {url}...")
try:
    resp = requests.get(url, verify=False)
    data = resp.json()
    
    for i, chapter in enumerate(data.get('chapters', [])):
        name = chapter.get('name', '')
        print(f"Chapter {i}: {name}")
        if "Tips" in name or "Changelog" in name or "Version" in name:
            print(json.dumps(chapter, indent=2))
            
except Exception as e:
    print(f"Error: {e}")
