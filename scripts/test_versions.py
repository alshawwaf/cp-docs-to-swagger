from app.data_manager import get_online_versions
import logging

# Configure logging to see output
logging.basicConfig(level=logging.INFO)

print("Fetching Management versions...")
versions = get_online_versions('management')
print(f"Found {len(versions)} versions: {versions}")

print("\nFetching GAiA versions...")
gaia_versions = get_online_versions('gaia')
print(f"Found {len(gaia_versions)} versions: {gaia_versions}")
