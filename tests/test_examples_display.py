"""
Test script to verify that examples are properly displayed in the OpenAPI spec
"""
import requests
import json

def test_management_api_examples():
    """Test that Management API has examples in the OpenAPI spec"""
    print("Testing Management API Examples...")
    print("="*60)
    
    # Fetch OpenAPI spec
    url = "http://localhost:5000/openapi.json?api_type=management"
    resp = requests.get(url)
    
    if resp.status_code != 200:
        print(f"❌ Failed to fetch OpenAPI spec: {resp.status_code}")
        return False
    
    spec = resp.json()
    
    # Check if login endpoint exists
    if '/login' not in spec.get('paths', {}):
        print("❌ Login endpoint not found in spec")
        return False
    
    login_endpoint = spec['paths']['/login']
    
    # Check if POST method exists
    if 'post' not in login_endpoint:
        print("❌ POST method not found for login endpoint")
        return False
    
    login_post = login_endpoint['post']
    
    # Check if requestBody exists
    if 'requestBody' not in login_post:
        print("❌ No requestBody found for login endpoint")
        return False
    
    request_body = login_post['requestBody']
    
    # Check if examples exist
    if 'content' not in request_body:
        print("❌ No content in requestBody")
        return False
    
    if 'application/json' not in request_body['content']:
        print("❌ No application/json in requestBody content")
        return False
    
    json_content = request_body['content']['application/json']
    
    if 'examples' not in json_content:
        print("❌ No examples found in requestBody")
        print("\nAvailable keys:", list(json_content.keys()))
        if 'schema' in json_content:
            print("\nSchema properties:", list(json_content['schema'].get('properties', {}).keys()))
        return False
    
    examples = json_content['examples']
    print(f"✅ Found {len(examples)} example(s) for login endpoint")
    
    # Display the examples
    for example_name, example_data in examples.items():
        print(f"\n{example_name}:")
        print(json.dumps(example_data.get('value', {}), indent=2))
    
    # Verify the example is simple (should have user and password, not all fields)
    first_example = list(examples.values())[0]
    example_value = first_example.get('value', {})
    
    if 'user' in example_value and 'password' in example_value:
        print("\n✅ Example has user and password fields")
        
        # Check if it's a simple example (not showing all optional fields)
        if len(example_value) <= 4:  # user, password, and maybe 1-2 other fields
            print(f"✅ Example is concise ({len(example_value)} fields)")
        else:
            print(f"⚠️  Example has many fields ({len(example_value)}), might be too verbose")
    else:
        print("❌ Example missing user or password fields")
        return False
    
    return True

def test_gaia_api_no_crash():
    """Test that GAiA API doesn't crash when examples.json is missing"""
    print("\n\nTesting GAiA API (should handle missing examples gracefully)...")
    print("="*60)
    
    # Fetch OpenAPI spec for GAiA
    url = "http://localhost:5000/openapi.json?api_type=gaia&server_url=https://203.0.113.100:443/gaia_api"
    resp = requests.get(url)
    
    if resp.status_code != 200:
        print(f"❌ Failed to fetch GAiA OpenAPI spec: {resp.status_code}")
        print(resp.text[:500])
        return False
    
    spec = resp.json()
    print(f"✅ GAiA API spec loaded successfully")
    print(f"   Found {len(spec.get('paths', {}))} endpoints")
    
    # Check if login endpoint exists
    if '/login' in spec.get('paths', {}):
        login_endpoint = spec['paths']['/login']
        if 'post' in login_endpoint:
            login_post = login_endpoint['post']
            has_examples = 'examples' in login_post.get('requestBody', {}).get('content', {}).get('application/json', {})
            if has_examples:
                print("   ℹ️  Login endpoint has examples (unexpected for GAiA)")
            else:
                print("   ✅ Login endpoint has no examples (expected for GAiA)")
    
    return True

if __name__ == "__main__":
    print("OpenAPI Examples Verification Test")
    print("="*60)
    print()
    
    success = True
    
    # Test Management API
    if not test_management_api_examples():
        success = False
    
    # Test GAiA API
    if not test_gaia_api_no_crash():
        success = False
    
    print("\n" + "="*60)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    
    exit(0 if success else 1)
