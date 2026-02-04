import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.converter import convert_checkpoint_to_openapi
import json

try:
    print("Starting holistic conversion...")
    spec = convert_checkpoint_to_openapi()
    
    # Check add-host path
    paths = spec.get('paths', {})
    add_host_path = '/add-host'
    
    if add_host_path in paths:
        print(f"Found {add_host_path}!")
        post_op = paths[add_host_path].get('post', {})
        
        # Check Request Schema
        req_schema = post_op.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema', {})
        req_props = req_schema.get('properties', {})
        if 'domain' in req_props:
            print("SUCCESS: 'domain' field found in REQUEST properties!")
            print(json.dumps(req_props['domain'], indent=2))
        else:
            print("FAILURE: 'domain' field NOT found in REQUEST properties.")

        # Check Response Schema
        res_schema = post_op.get('responses', {}).get('200', {}).get('content', {}).get('application/json', {}).get('schema', {})
        res_props = res_schema.get('properties', {})
        
        if 'domain' in res_props:
            print("SUCCESS: 'domain' field found in RESPONSE properties!")
            print(json.dumps(res_props['domain'], indent=2))
        else:
            print("FAILURE: 'domain' field NOT found in RESPONSE properties.")
            
        # Check Request Examples
        req_examples = post_op.get('requestBody', {}).get('content', {}).get('application/json', {}).get('examples', {})
        if req_examples:
            print(f"Found {len(req_examples)} request examples.")
            print(json.dumps(list(req_examples.keys()), indent=2))
        else:
            print("No request examples found.")

    else:
        print(f"{add_host_path} not found in paths.")
        
except Exception as e:
    print(f"Conversion failed: {e}")
