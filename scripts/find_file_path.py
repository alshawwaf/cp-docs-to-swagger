import requests
import json

url = "https://sc1.checkpoint.com/documents/latest/APIs/data/v1.9/dynamic/content.json"
print(f"Fetching {url}...")
try:
    resp = requests.get(url, verify=False)
    data = resp.json()
    
    files_to_check = []
    
    def collect_files(obj):
        if isinstance(obj, dict):
            if 'file' in obj:
                files_to_check.append(obj['file'])
            for v in obj.values():
                collect_files(v)
        elif isinstance(obj, list):
            for item in obj:
                collect_files(item)

    collect_files(data)
    print(f"Found {len(files_to_check)} files referenced.")
    
    # Check the first few
    base_url = "https://sc1.checkpoint.com/documents/latest/APIs/data/v1.9/"
    prefixes = ["", "dynamic/", "static_content/", "static/"]
    
    for file in files_to_check[:5]:
        if not file or file.startswith('#'): continue
        print(f"Checking location for: {file}")
        for prefix in prefixes:
            url = f"{base_url}{prefix}{file}"
            try:
                resp = requests.head(url, verify=False)
                if resp.status_code == 200:
                    print(f"  FOUND at: {url}")
                    break
            except: pass
            
except Exception as e:
    print(f"Error: {e}")
