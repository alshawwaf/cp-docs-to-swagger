"""
Simple check of content.json structure for GAiA API
"""
import requests
import json

url = "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/data/v1.8/dynamic/content.json"
headers = {"User-Agent": "Mozilla/5.0"}

print("Fetching content.json...")
resp = requests.get(url, headers=headers, timeout=10)
data = resp.json()

print(f"Top-level keys: {list(data.keys())}")

# Find commands with external-data
count = 0
examples_found = []

def search_commands(obj):
    global count, examples_found
    if isinstance(obj, dict):
        if 'commands-data' in obj:
            for cmd in obj['commands-data']:
                if isinstance(cmd, dict) and 'external-data' in cmd:
                    count += 1
                    cmd_name = cmd.get('name', {}).get('web') if isinstance(cmd.get('name'), dict) else str(cmd.get('name'))
                    files = cmd['external-data'].get('file-names', [])
                    if count <= 5:  # Show first 5
                        examples_found.append((cmd_name, files))
        
        for value in obj.values():
            search_commands(value)
    elif isinstance(obj, list):
        for item in obj:
            search_commands(item)

search_commands(data)

print(f"\nFound {count} commands with external-data references")
print("\nFirst 5 examples:")
for cmd_name, files in examples_found:
    print(f"  {cmd_name}: {files}")

# The files might be relative paths that need to be resolved differently
# Let's check if they're meant to be loaded from a different location
print("\nNote: These paths might be:")
print("1. Relative to a different base URL")
print("2. Bundled in the frontend code")
print("3. Generated dynamically by Check Point's UI")
