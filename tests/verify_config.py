import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.converter import CHECKPOINT_SERVER_URL, CHECKPOINT_API_VERSION

print("=== Check Point API Converter Configuration ===")
print(f"Server URL: {CHECKPOINT_SERVER_URL}")
print(f"API Version: {CHECKPOINT_API_VERSION}")
print()

# Check if using defaults
if CHECKPOINT_SERVER_URL == "https://<mgmt-server>:<port>/web_api":
    print("⚠️  Using DEFAULT server URL (placeholder)")
else:
    print("✓ Using CUSTOM server URL from environment variable")

if CHECKPOINT_API_VERSION == "v2.0.1":
    print("✓ Using DEFAULT API version (v2.0.1)")
else:
    print(f"✓ Using CUSTOM API version from environment variable")

print("\nTo configure:")
print("1. Copy .env.example to .env")
print("2. Edit .env with your settings")
print("3. Restart the application")
print("\nExample:")
print("  CHECKPOINT_SERVER_URL=https://203.0.113.100:443/web_api")
print("  CHECKPOINT_API_VERSION=v2.0.1")
