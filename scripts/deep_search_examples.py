"""
Deep search for GAiA API login examples in all possible locations
"""
import requests
import json
import re

def deep_search_for_examples():
    """Search for the exact example values shown on Check Point's website"""
    
    base_url = "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/data/v1.8"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/?"
    }
    
    # The example we're looking for
    target_user = "admin"
    target_password = "secret"
    
    print("Searching for the exact example from Check Point's website:")
    print(f'  "user": "{target_user}"')
    print(f'  "password": "{target_password}"')
    print("="*60)
    
    # Check all possible JSON files
    files_to_check = [
        "dynamic/apis.json",
        "dynamic/content.json",
        "static_content/content.json",
        "static_content/examples.json",
    ]
    
    for file_path in files_to_check:
        url = f"{base_url}/{file_path}"
        print(f"\nChecking: {file_path}")
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                content = resp.text
                
                # Search for the exact string pattern
                if '"admin"' in content and '"secret"' in content:
                    print(f"  ✓ Found 'admin' and 'secret' in {file_path}!")
                    
                    # Try to find the context
                    data = resp.json()
                    
                    # Search recursively for login examples
                    def search_dict(obj, path=""):
                        if isinstance(obj, dict):
                            for key, value in obj.items():
                                new_path = f"{path}.{key}" if path else key
                                
                                # Check if this looks like a login example
                                if isinstance(value, dict):
                                    if 'user' in value and 'password' in value:
                                        if value.get('user') == 'admin' or value.get('password') == 'secret':
                                            print(f"\n  Found at path: {new_path}")
                                            print(f"  Content: {json.dumps(value, indent=4)}")
                                            return True
                                
                                if search_dict(value, new_path):
                                    return True
                        elif isinstance(obj, list):
                            for i, item in enumerate(obj):
                                if search_dict(item, f"{path}[{i}]"):
                                    return True
                        return False
                    
                    search_dict(data)
                else:
                    print(f"  ✗ No matching example found")
            elif resp.status_code == 404:
                print(f"  ✗ 404 Not Found")
            else:
                print(f"  ✗ HTTP {resp.status_code}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    # Also try to fetch the HTML page directly to see how they load it
    print("\n" + "="*60)
    print("Checking the HTML page source...")
    print("="*60)
    
    try:
        html_url = "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/"
        resp = requests.get(html_url, headers=headers, timeout=10)
        if resp.status_code == 200:
            html_content = resp.text
            
            # Search for JavaScript that might load examples
            if 'examples' in html_content.lower():
                # Find script tags or data attributes
                script_matches = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
                print(f"\nFound {len(script_matches)} script tags")
                
                for i, script in enumerate(script_matches[:5]):  # Check first 5 scripts
                    if 'example' in script.lower() or 'login' in script.lower():
                        print(f"\nScript {i+1} contains 'example' or 'login':")
                        print(script[:500])
    except Exception as e:
        print(f"Error fetching HTML: {e}")

if __name__ == "__main__":
    deep_search_for_examples()
