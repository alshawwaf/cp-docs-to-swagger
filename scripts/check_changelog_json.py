import requests

base_url = "https://sc1.checkpoint.com/documents/latest/APIs/data/v1.9/"
files = ["changelog.json", "changes.json", "whatsnew.json", "new_features.json"]
prefixes = ["", "dynamic/", "static_content/", "static/"]

for file in files:
    for prefix in prefixes:
        url = f"{base_url}{prefix}{file}"
        try:
            resp = requests.head(url, verify=False)
            if resp.status_code == 200:
                print(f"FOUND: {url}")
        except: pass
