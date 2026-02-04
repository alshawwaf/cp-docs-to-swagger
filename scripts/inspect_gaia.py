import requests
import json

# GAiA API Base URL (from config.py or similar)
# Assuming it's similar to Management but different base
# I'll try to discover it or use a known one. 
# In config.py, GAiA URL is likely https://sc1.checkpoint.com/documents/latest/GaiaAPIs/

base_url = "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/"
# Need to find version first
version_url = base_url + "js/versions.js"

print(f"Fetching version from {version_url}...")
try:
    resp = requests.get(version_url, verify=False)
    if resp.status_code == 200:
        import re
        match = re.search(r'var\s+default_api_version\s*=\s*"([^"]+)"', resp.text)
        if match:
            version = match.group(1)
            print(f"Version: {version}")
            
            data_url = f"{base_url}data/{version}/"
            
            # Check apis.json
            print("Fetching apis.json...")
            apis_resp = requests.get(data_url + "dynamic/apis.json", verify=False)
            apis_data = apis_resp.json()
            
            # Check content.json
            print("Fetching content.json...")
            content_resp = requests.get(data_url + "dynamic/content.json", verify=False)
            content_data = content_resp.json()
            
            # Check examples.json
            print("Fetching examples.json...")
            examples_resp = requests.get(data_url + "dynamic/examples.json", verify=False)
            if examples_resp.status_code == 200:
                print("examples.json FOUND")
                ex_data = examples_resp.json()
                print(f"Examples count: {len(ex_data.get('examples', {}))}")
            else:
                print("examples.json NOT FOUND")
                
            # Compare command names
            print("\nComparing command names...")
            api_cmds = set()
            if 'commands' in apis_data:
                for cmd in apis_data['commands']:
                    if isinstance(cmd, dict):
                        name = cmd.get('name', {}).get('web')
                        if name:
                            api_cmds.add(name)
            
            print(f"Found {len(api_cmds)} commands in apis.json")
            
            content_cmds = set()
            def find_names(obj):
                if isinstance(obj, dict):
                    if 'name' in obj:
                        name_obj = obj['name']
                        if isinstance(name_obj, dict):
                            content_cmds.add(name_obj.get('web'))
                        elif isinstance(name_obj, str):
                            content_cmds.add(name_obj)
                    for v in obj.values():
                        find_names(v)
                elif isinstance(obj, list):
                    for item in obj:
                        find_names(item)
                        
            find_names(content_data)
            print(f"Found {len(content_cmds)} commands in content.json")
            
            common = api_cmds.intersection(content_cmds)
            print(f"Common commands: {len(common)}")
            
            # Check for external data in content.json
            print("\nChecking for external examples in content.json...")
            external_refs = []
            def find_external(obj):
                if isinstance(obj, dict):
                    if 'external-data' in obj and 'file-names' in obj['external-data']:
                         if 'name' in obj:
                            name_obj = obj['name']
                            c_name = name_obj.get('web') if isinstance(name_obj, dict) else name_obj
                            external_refs.append((c_name, obj['external-data']['file-names']))
                    for v in obj.values():
                        find_external(v)
                elif isinstance(obj, list):
                    for item in obj:
                        find_external(item)
            
            find_external(content_data)
            print(f"Found {len(external_refs)} external data references")
            if len(external_refs) > 0:
                print("Sample refs:", external_refs[:5])
                
                # Fetch one example to see structure
                ex_name, ex_files = external_refs[0]
                if ex_files:
                    ex_url = data_url + "dynamic/" + ex_files[0]
                    print(f"Fetching example from {ex_url}...")
                    ex_resp = requests.get(ex_url, verify=False)
                    if ex_resp.status_code == 200:
                        print("Example content:")
                        print(json.dumps(ex_resp.json(), indent=2))
        else:
            print("Version not found in regex")
    else:
        print("Failed to fetch versions.js")
except Exception as e:
    print(f"Error: {e}")
