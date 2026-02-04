from flask import jsonify, render_template, request, Response
from app import app, logger, CHECKPOINT_SERVER_URL, CHECKPOINT_API_VERSION
from .converter import convert_checkpoint_to_openapi, API_CONFIGS, GAIA_SERVER_URL

import requests

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/docs')
def swagger_ui():
    """Render Swagger UI with dynamic configuration"""
    api_type = request.args.get('api_type', 'management')
    server_url = request.args.get('server_url', '')
    api_version = request.args.get('api_version', '')
    # Build the API URL for OpenAPI spec - always point to localhost for the JSON
    from urllib.parse import quote
    params = []
    if api_type:
        params.append(f'api_type={quote(api_type)}')
    if server_url:
        params.append(f'server_url={quote(server_url)}')
    if api_version:
        params.append(f'api_version={quote(api_version)}')
    
    api_url = '/openapi.json' + ('?' + '&'.join(params) if params else '')
    
    return render_template('swagger.html', api_url=api_url, api_type=api_type, server_url=server_url, api_version=api_version)

@app.route('/docs/versions')
def docs_versions():
    """Render Versions page"""
    from .converter.fetcher import fetch_documentation_page
    api_type = request.args.get('api_type', 'management')
    server_url = request.args.get('server_url', '')
    api_version = request.args.get('api_version', '')
    
    content = fetch_documentation_page(api_type, api_version, 'api_versions.html')
    
    return render_template('versions.html', 
                         api_type=api_type, 
                         server_url=server_url, 
                         api_version=api_version,
                         content=content)

@app.route('/docs/changelog')
def docs_changelog():
    """Render Changelog page"""
    from .converter.fetcher import fetch_documentation_page, fetch_changes_json
    api_type = request.args.get('api_type', 'management')
    server_url = request.args.get('server_url', '')
    api_version = request.args.get('api_version', '')
    
    content = fetch_documentation_page(api_type, api_version, 'changelog.html')
    changes_data = fetch_changes_json(api_type, api_version)
    
    return render_template('changelog.html', 
                         api_type=api_type, 
                         server_url=server_url, 
                         api_version=api_version,
                         content=content,
                         changes_data=changes_data)

@app.route('/docs/tips')
def docs_tips():
    """Render Tips & Best Practices page"""
    from .converter.fetcher import fetch_documentation_page
    api_type = request.args.get('api_type', 'management')
    server_url = request.args.get('server_url', '')
    api_version = request.args.get('api_version', '')
    
    content = fetch_documentation_page(api_type, api_version, 'tips_best_practices.html')
    
    return render_template('tips.html', 
                         api_type=api_type, 
                         server_url=server_url, 
                         api_version=api_version,
                         content=content)

@app.route('/proxy/<encoded_server>/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy_request(encoded_server, endpoint):
    """Proxy requests to the Check Point server to handle CORS and SSL issues"""
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = Response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Expose-Headers'] = 'X-chkp-sid'
        return response
    
    # Decode the target server from the path
    import base64
    try:
        # URL-safe Base64 decode
        target_server_bytes = base64.urlsafe_b64decode(encoded_server)
        target_server = target_server_bytes.decode('utf-8')
        
        # Enforce HTTPS if no scheme is provided
        if not target_server.startswith('http://') and not target_server.startswith('https://'):
            target_server = f"https://{target_server}"
        
        # If HTTP is provided, upgrade to HTTPS as requested by user
        if target_server.startswith('http://'):
            target_server = target_server.replace('http://', 'https://', 1)
            
    except Exception as e:
        logger.error(f"Failed to decode server URL: {e}")
        return jsonify({"error": "Invalid server URL encoding"}), 400
    
    # Build the full URL
    target_url = f"{target_server}/{endpoint}"
    
    logger.info("="*60)
    logger.info(f"Proxying request to: {target_url}")
    logger.info(f"Method: {request.method}")
    
    # Forward the request
    try:
        # Suppress InsecureRequestWarning
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Get request data
        data = request.get_data()
        headers = {key: value for key, value in request.headers if key.lower() not in ['host', 'connection']}
        
        # Explicitly ensure X-chkp-sid is passed if present
        if 'X-chkp-sid' in headers or 'x-chkp-sid' in headers:
            sid = headers.get('X-chkp-sid') or headers.get('x-chkp-sid')
            headers['X-chkp-sid'] = sid
            logger.info(f"Found session ID in request headers: {sid}")
        
        # Make the request with SSL verification
        from .converter.config import VERIFY_SSL
        resp = requests.request(
            method=request.method,
            url=target_url,
            headers=headers,
            data=data,
            verify=VERIFY_SSL,
            timeout=30
        )
        
        logger.info(f"Response status: {resp.status_code}")
        
        # Create response with CORS headers
        response = Response(resp.content, status=resp.status_code)
        response.headers['Content-Type'] = resp.headers.get('Content-Type', 'application/json')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = '*'
        response.headers['Access-Control-Expose-Headers'] = 'X-chkp-sid, x-chkp-sid'
        
        # Forward session ID header if present (handle case-insensitive search)
        # requests headers are case-insensitive, but we want to be explicit about what we send back
        sid = resp.headers.get('X-chkp-sid') or resp.headers.get('x-chkp-sid')
        
        # If not in headers, try to extract from JSON body (common in Check Point API login response)
        if not sid:
            try:
                # We can safely read content since we already accessed it for the response
                json_data = resp.json()
                if isinstance(json_data, dict) and 'sid' in json_data:
                    sid = json_data['sid']
                    logger.info(f"Found session ID in response body: {sid}")
            except Exception:
                # Not JSON or parsing failed, ignore
                pass

        if sid:
            response.headers['X-chkp-sid'] = sid
            logger.info(f"Forwarding session ID: {sid}")
            
        return response
    except Exception as e:
        logger.error(f"Proxy error: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/proxy_example')
def proxy_example():
    """Proxy for lazy-loading external examples"""
    url = request.args.get('url')
    example_type = request.args.get('type', 'request') # 'request' or 'response'
    
    if not url:
        return jsonify({"error": "Missing url parameter"}), 400
    
    # Decode URL if needed
    from urllib.parse import unquote
    url = unquote(url)
    
    logger.info(f"Fetching external example ({example_type}) from: {url}")
    
    try:
        # Fetch the example
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        
        data = resp.json()
        
        # Extract the specific body based on type
        result = {}
        if 'web' in data:
            web_data = data['web']
            if example_type == 'request' and 'request' in web_data and 'body' in web_data['request']:
                body_str = web_data['request']['body']
                try:
                    result = json.loads(body_str)
                except:
                    result = body_str # Return as string if not JSON
            elif example_type == 'response' and 'response' in web_data and 'body' in web_data['response']:
                body_str = web_data['response']['body']
                try:
                    result = json.loads(body_str)
                except:
                    result = body_str
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error fetching example from {url}: {e}")
        return jsonify({"error": f"Failed to fetch example: {str(e)}"}), 500

@app.route('/openapi.json')
def get_openapi_spec():
    logger.info("Request received for /openapi.json")
    
    # Get configuration from query parameters or environment variables
    api_type = request.args.get('api_type', 'management')
    server_url = request.args.get('server_url', '')
    api_version = request.args.get('api_version', CHECKPOINT_API_VERSION)
    
    # Validate api_version - ignore if it looks like a placeholder or error message
    if api_version and (api_version.lower().startswith('loading') or '...' in api_version or 'failed' in api_version.lower()):
        logger.warning(f"Received invalid api_version: '{api_version}', ignoring.")
        api_version = None
    
    # Default server URL based on API type
    if not server_url:
        if api_type == 'gaia':
            server_url = GAIA_SERVER_URL
        else:
            server_url = CHECKPOINT_SERVER_URL
    
    logger.info(f"Using API type: {api_type}")
    logger.info(f"Using server URL: {server_url}")
    logger.info(f"Using API version: {api_version}")
    
    try:
        # Check if we have a processed spec locally
        from .data_manager import get_local_spec, is_version_processed
        from .converter import get_latest_api_version
        
        # If no version specified, find the latest one
        if not api_version:
            api_version = get_latest_api_version(api_type)
            logger.info(f"Resolved latest API version to: {api_version}")
        
        spec = None
        if api_version and is_version_processed(api_type, api_version):
            logger.info(f"Loading pre-processed spec for {api_type} {api_version}")
            spec = get_local_spec(api_type, api_version)
        
        if not spec:
            logger.info("Generating spec on-the-fly (fallback)")
            spec = convert_checkpoint_to_openapi(api_type, server_url, api_version)
        
        # Modify the spec to use the proxy endpoint instead of direct server URL
        api_name = API_CONFIGS.get(api_type, {}).get('name', 'Check Point API')
        
        # Base64 encode the server_url to safely pass it in the path
        import base64
        encoded_server_url = base64.urlsafe_b64encode(server_url.encode('utf-8')).decode('utf-8')
        
        # Override servers block
        proxy_base = request.host_url.rstrip('/')
        spec['servers'] = [
            {
                "url": f"{proxy_base}/proxy/{encoded_server_url}",
                "description": f"Proxy to {api_name} Server ({server_url})"
            }
        ]
        
        logger.info(f"Proxy URL configured: {proxy_base}/proxy/{encoded_server_url}")
        logger.info("Spec generated successfully.")
        return jsonify(spec)
    except Exception as e:
        logger.error(f"Error generating spec: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500



@app.route('/api/versions')
def list_versions():
    """List available versions (online and local status)"""
    from .data_manager import get_online_versions, is_version_downloaded, is_version_processed
    
    api_type = request.args.get('api_type', 'management')
    online_versions = get_online_versions(api_type)
    
    results = []
    for v in online_versions:
        results.append({
            "version": v,
            "downloaded": is_version_downloaded(api_type, v),
            "processed": is_version_processed(api_type, v)
        })
        
    return jsonify(results)

@app.route('/api/sync', methods=['POST'])
def sync_versions():
    """Trigger download and conversion of all versions"""
    from .data_manager import get_online_versions, download_version_data, load_local_data, save_processed_spec, is_version_processed
    
    api_type = request.json.get('api_type', 'management')
    force = request.json.get('force', False)
    
    def background_sync(api_type, force):
        logger.info(f"Starting background sync for {api_type}")
        versions = get_online_versions(api_type)
        
        for v in versions:
            if not force and is_version_processed(api_type, v):
                logger.info(f"Skipping {v} (already processed)")
                continue
                
            logger.info(f"Processing version {v}...")
            if download_version_data(api_type, v):
                data = load_local_data(api_type, v)
                if data:
                    try:
                        # Convert without server_url (will be injected at runtime)
                        spec = convert_checkpoint_to_openapi(api_type, None, v, data_source=data)
                        save_processed_spec(api_type, v, spec)
                    except Exception as e:
                        logger.error(f"Failed to convert {v}: {e}")
            
        logger.info("Sync completed")

    # Run in background thread
    import threading
    thread = threading.Thread(target=background_sync, args=(api_type, force))
    thread.start()
    
    return jsonify({"status": "started", "message": "Sync started in background"})
