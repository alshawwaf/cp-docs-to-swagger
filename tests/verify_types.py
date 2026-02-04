import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.converter import convert_checkpoint_to_openapi
import json

try:
    print("Starting conversion...")
    spec = convert_checkpoint_to_openapi()
    
    # Check add-host path
    paths = spec.get('paths', {})
    add_host_path = '/add-host'
    
    if add_host_path in paths:
        print(f"Found {add_host_path}!")
        post_op = paths[add_host_path].get('post', {})
        schema = post_op.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema', {})
        properties = schema.get('properties', {})
        
        # Check groups
        if 'groups' in properties:
            print("Checking 'groups' field...")
            groups_prop = properties['groups']
            print(f"Type: {groups_prop.get('type')}")
            if groups_prop.get('type') == 'array':
                print("SUCCESS: 'groups' is an array.")
            else:
                print(f"FAILURE: 'groups' is {groups_prop.get('type')}.")
        else:
            print("FAILURE: 'groups' field NOT found.")

        # Check color
        if 'color' in properties:
            print("Checking 'color' field...")
            color_prop = properties['color']
            if 'enum' in color_prop:
                print(f"SUCCESS: 'color' has enum values: {color_prop['enum'][:3]}...")
            else:
                print("FAILURE: 'color' does NOT have enum values.")
        else:
            print("FAILURE: 'color' field NOT found.")

    else:
        print(f"{add_host_path} not found in paths.")
        
except Exception as e:
    print(f"Conversion failed: {e}")
