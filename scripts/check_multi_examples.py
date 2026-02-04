import requests
import json

base_url = "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/"
version_url = base_url + "js/versions.js"

try:
    resp = requests.get(version_url, verify=False)
    if resp.status_code == 200:
        import re
        match = re.search(r'var\s+default_api_version\s*=\s*"([^"]+)"', resp.text)
        if match:
            version = match.group(1)
            data_url = f"{base_url}data/{version}/"
            content_resp = requests.get(data_url + "dynamic/content.json", verify=False)
            content_data = content_resp.json()
            
            multi_file_refs = []
            def find_multi(obj):
                if isinstance(obj, dict):
                    if 'external-data' in obj and 'file-names' in obj['external-data']:
                         files = obj['external-data']['file-names']
                         if len(files) > 1:
                             if 'name' in obj:
                                name_obj = obj['name']
                                c_name = name_obj.get('web') if isinstance(name_obj, dict) else name_obj
                                multi_file_refs.append((c_name, len(files)))
                    for v in obj.values():
                        find_multi(v)
                elif isinstance(obj, list):
                    for item in obj:
                        find_multi(item)
            
            find_multi(content_data)
            print(f"Found {len(multi_file_refs)} commands with multiple examples")
            for name, count in multi_file_refs:
                print(f"  {name}: {count} examples")
                
except Exception as e:
    print(f"Error: {e}")
