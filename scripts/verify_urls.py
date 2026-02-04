import requests

base_urls = [
    "https://sc1.checkpoint.com/documents/latest/APIs/data/v2.0.1/",
    "https://sc1.checkpoint.com/documents/latest/APIs/"
]
files = ["changelog.html", "tips_best_practices.html"]
prefixes = ["", "dynamic/", "static_content/", "static/"]

for base_url in base_urls:
    for file in files:
        for prefix in prefixes:
            url = f"{base_url}{prefix}{file}"
            try:
                resp = requests.head(url, verify=False)
                if resp.status_code == 200:
                    print(f"FOUND: {url}")
                # else:
                #     print(f"Checked {url}: {resp.status_code}")
            except Exception as e:
                pass
