import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.converter import convert_checkpoint_to_openapi
import json

try:
    print("Starting conversion with hierarchy...")
    spec = convert_checkpoint_to_openapi()
    
    # Check add-host path
    paths = spec.get('paths', {})
    add_host_path = '/add-host'
    
    if add_host_path in paths:
        print(f"Found {add_host_path}!")
        post_op = paths[add_host_path].get('post', {})
        tags = post_op.get('tags', [])
        print(f"Tags for add-host: {tags}")
        
        if any("Network Objects" in t for t in tags):
            print("SUCCESS: 'Network Objects' found in tags.")
        else:
            print("FAILURE: 'Network Objects' NOT found in tags.")
            
    # Check another one
    login_path = '/login'
    if login_path in paths:
        print(f"Found {login_path}!")
        tags = paths[login_path].get('post', {}).get('tags', [])
        print(f"Tags for login: {tags}")

except Exception as e:
    print(f"Conversion failed: {e}")
