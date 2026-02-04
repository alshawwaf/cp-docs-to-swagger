"""
Script to investigate where GAiA API examples are stored in Check Point's JSON files
"""
import requests
import json

def investigate_gaia_examples():
    """Fetch and analyze all GAiA API JSON files to find where examples are stored"""
    
    base_url = "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/data/v1.8"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/?"
    }
    
    files_to_check = [
        "dynamic/apis.json",
        "dynamic/examples.json",  # We know this is 404
        "dynamic/content.json",
        "static_content/apis.json",
    ]
    
    for file_path in files_to_check:
        url = f"{base_url}/{file_path}"
        print(f"\n{'='*60}")
        print(f"Checking: {file_path}")
        print(f"URL: {url}")
        print('='*60)
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            print(f"Status: {resp.status_code}")
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"Size: {len(resp.content)} bytes")
                print(f"Top-level keys: {list(data.keys())}")
                
                # Search for login-related content
                json_str = json.dumps(data)
                
                # Search for "user" and "password" together (likely login example)
                if '"user"' in json_str and '"password"' in json_str:
                    print("\n✓ Found 'user' and 'password' fields in this file!")
                    
                    # Try to find the login command
                    if 'commands' in data:
                        commands = data['commands']
                        if isinstance(commands, list):
                            for cmd in commands:
                                if isinstance(cmd, dict):
                                    name = cmd.get('name', {})
                                    if isinstance(name, dict):
                                        cmd_name = name.get('web')
                                    else:
                                        cmd_name = name
                                    
                                    if cmd_name == 'login':
                                        print(f"\nFound login command!")
                                        print(json.dumps(cmd, indent=2)[:2000])
                                        break
                    
                    # Check for examples in different structures
                    if 'examples' in data:
                        print(f"\nFound 'examples' key with {len(data['examples'])} items")
                        # Look for login examples
                        for key, value in list(data['examples'].items())[:5]:
                            if 'login' in key.lower():
                                print(f"\nLogin example key: {key}")
                                print(json.dumps(value, indent=2)[:1000])
                
                # Check if there's example data embedded in commands
                if 'commands' in data:
                    print(f"\nFound {len(data.get('commands', []))} commands")
                    # Check first few commands for example structure
                    commands = data['commands']
                    if isinstance(commands, list) and len(commands) > 0:
                        first_cmd = commands[0]
                        print(f"\nStructure of first command:")
                        print(f"Keys: {list(first_cmd.keys()) if isinstance(first_cmd, dict) else 'Not a dict'}")
                        
            elif resp.status_code == 404:
                print("✗ File not found (404)")
            else:
                print(f"✗ HTTP {resp.status_code}")
                
        except Exception as e:
            print(f"✗ Error: {e}")

if __name__ == "__main__":
    investigate_gaia_examples()
