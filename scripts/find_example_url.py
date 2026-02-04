"""
Brute force search for GAiA API example files
"""
import requests
import sys

def check_url(url):
    try:
        resp = requests.head(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        print(f"[{resp.status_code}] {url}")
        return resp.status_code == 200
    except Exception as e:
        print(f"[ERR] {url}: {e}")
        return False

base_urls = [
    "https://sc1.checkpoint.com/documents/latest/GaiaAPIs",
    "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/data",
    "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/data/v1.8",
    "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/v1.8",
    "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/docs",
    "https://sc1.checkpoint.com/documents/latest/GaiaAPIs/assets",
]

# The path from content.json is "examples//login//login_1/example.json"
# We'll try various cleanups of this path
paths = [
    "examples/login/login_1/example.json",
    "examples//login//login_1/example.json",
    "dynamic/examples/login/login_1/example.json",
    "static_content/examples/login/login_1/example.json",
    "data/v1.8/examples/login/login_1/example.json",
]

print("Starting brute force search for example files...")
found = False
for base in base_urls:
    for path in paths:
        url = f"{base}/{path}"
        if check_url(url):
            print(f"\n!!! FOUND IT !!!\n{url}")
            found = True
            break
    if found: break

if not found:
    print("\nStill couldn't find the example files.")
