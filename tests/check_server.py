import requests

try:
    print("Checking /openapi.json...")
    resp = requests.get("http://localhost:5000/openapi.json")
    print(f"Status: {resp.status_code}")
    if resp.status_code != 200:
        print(f"Error: {resp.text}")
    else:
        print("Success! JSON length:", len(resp.text))
        
except Exception as e:
    print(f"Connection failed: {e}")
