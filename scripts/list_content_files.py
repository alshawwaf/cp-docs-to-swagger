import json

try:
    # Try utf-16 first since that's what PowerShell output
    try:
        with open('content_dump.json', 'r', encoding='utf-16') as f:
            data = json.load(f)
    except:
        with open('content_dump.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
    files = set()
    def collect_files(obj):
        if isinstance(obj, dict):
            if 'file' in obj:
                files.add(obj['file'])
            for v in obj.values():
                collect_files(v)
        elif isinstance(obj, list):
            for item in obj:
                collect_files(item)

    collect_files(data)
    
    print("Files found in content.json:")
    for file in sorted(files):
        print(file)
        
except Exception as e:
    print(f"Error: {e}")
