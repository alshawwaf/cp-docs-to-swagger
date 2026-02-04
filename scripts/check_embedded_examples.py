"""
Check if examples are embedded in content.json commands-data
"""
import requests
import json

url = "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/data/v1.8/dynamic/content.json"
headers = {"User-Agent": "Mozilla/5.0"}

print("Fetching content.json and looking for embedded examples...")
resp = requests.get(url, headers=headers, timeout=10)
data = resp.json()

# Find the login command and see its full structure
def find_login_command(obj, depth=0):
    if depth > 30:
        return None
    
    if isinstance(obj, dict):
        # Check if this is a command with name 'login'
        if 'name' in obj:
            name = obj['name']
            if isinstance(name, dict) and name.get('web') == 'login':
                return obj
            elif name == 'login':
                return obj
        
        # Recurse through dict values
        for value in obj.values():
            result = find_login_command(value, depth + 1)
            if result:
                return result
    
    elif isinstance(obj, list):
        for item in obj:
            result = find_login_command(item, depth + 1)
            if result:
                return result
    
    return None

login_cmd = find_login_command(data)

if login_cmd:
    print("✓ Found login command in content.json!")
    print("\nFull structure:")
    print(json.dumps(login_cmd, indent=2)[:3000])
    
    # Check if there's example data embedded
    if 'example' in json.dumps(login_cmd).lower():
        print("\n✓ Found 'example' in the login command data!")
else:
    print("✗ Could not find login command")

# Also check the first command with external-data to see its full structure
print("\n" + "="*60)
print("Checking structure of first command with external-data...")
print("="*60)

def find_first_external_data_command(obj, depth=0):
    if depth > 30:
        return None
    
    if isinstance(obj, dict):
        if 'external-data' in obj and 'name' in obj:
            return obj
        
        for value in obj.values():
            result = find_first_external_data_command(value, depth + 1)
            if result:
                return result
    
    elif isinstance(obj, list):
        for item in obj:
            result = find_first_external_data_command(item, depth + 1)
            if result:
                return result
    
    return None

first_cmd = find_first_external_data_command(data)
if first_cmd:
    print("\nFirst command with external-data:")
    print(json.dumps(first_cmd, indent=2)[:2000])
