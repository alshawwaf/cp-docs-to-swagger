/**
 * Index Page Logic
 * Handles loading API versions, syncing, and navigation.
 */

document.addEventListener('DOMContentLoaded', () => {
    loadVersions('management');
    loadVersions('gaia');
});

async function loadVersions(apiType) {
    const selectId = apiType === 'management' ? 'mgmtApiVersion' : 'gaiaApiVersion';
    const select = document.getElementById(selectId);
    
    if (!select) return;
    
    // Show loading state
    select.innerHTML = '<option value="">Loading versions...</option>';
    
    try {
        const response = await fetch(`/api/versions?api_type=${apiType}`);
        const versions = await response.json();
        
        select.innerHTML = '<option value="">Auto (Latest)</option>';
        
        versions.forEach(v => {
            const option = document.createElement('option');
            option.value = v.version;
            // Add checkmark if downloaded/processed
            const status = v.processed ? '✓ ' : (v.downloaded ? '⬇ ' : '');
            option.text = `${status}${v.version}`;
            select.appendChild(option);
        });
    } catch (e) {
        console.error(`Failed to load ${apiType} versions:`, e);
        select.innerHTML = '<option value="">Failed to load</option>';
    }
}

async function syncVersions(apiType) {
    const btn = document.getElementById(`sync-${apiType}`);
    const originalText = btn.innerText;
    
    btn.disabled = true;
    btn.innerText = 'Syncing...';
    
    // Open modal
    openSyncModal(apiType);
    
    try {
        const response = await fetch('/api/sync', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ api_type: apiType, force: true })
        });
        
        const result = await response.json();
        
        // Show results in modal
        displaySyncResults(result, apiType);
        
        // Reload versions after sync
        setTimeout(() => {
            loadVersions(apiType);
        }, 2000);
        
    } catch (e) {
        displaySyncError(e, apiType);
    } finally {
        btn.disabled = false;
        btn.innerText = originalText;
    }
}

function openSyncModal(apiType) {
    const modal = document.getElementById('syncModal');
    const title = document.getElementById('syncModalTitle');
    const apiName = apiType === 'management' ? 'Management' : 'GAiA';
    
    title.textContent = `Syncing ${apiName} API Versions`;
    document.getElementById('syncProgress').style.display = 'block';
    document.getElementById('syncResults').style.display = 'none';
    document.getElementById('syncCloseBtn').style.display = 'none';
    document.getElementById('syncStatus').textContent = 'Initializing sync...';
    
    modal.classList.add('show');
}

function closeSyncModal() {
    const modal = document.getElementById('syncModal');
    modal.classList.remove('show');
}

function displaySyncResults(result, apiType) {
    document.getElementById('syncProgress').style.display = 'none';
    document.getElementById('syncResults').style.display = 'block';
    document.getElementById('syncCloseBtn').style.display = 'block';
    
    const resultContent = document.getElementById('syncResultContent');
    const apiName = apiType === 'management' ? 'Management' : 'GAiA';
    
    let html = '';
    
    if (result.status === 'success' || result.message) {
        html += `
            <div class="sync-result-item success">
                <h4><span class="sync-result-icon success">✓</span> Sync Started Successfully</h4>
                <p>${result.message || `${apiName} API sync has been initiated.`}</p>
            </div>
        `;
        
        if (result.versions_synced) {
            html += `
                <div class="sync-result-item info">
                    <h4><span class="sync-result-icon info">ⓘ</span> Versions to Process</h4>
                    <p>${result.versions_synced} version(s) queued for synchronization</p>
                </div>
            `;
        }
        
        html += `
            <div class="sync-summary">
                <h3>Summary</h3>
                <div class="sync-summary-stats">
                    <div class="sync-stat">
                        <p class="sync-stat-value">${result.versions_synced || '...'}</p>
                        <p class="sync-stat-label">Versions</p>
                    </div>
                    <div class="sync-stat">
                        <p class="sync-stat-value">✓</p>
                        <p class="sync-stat-label">Status</p>
                    </div>
                </div>
                <p style="margin-top: 1rem; font-size: 0.9rem; color: var(--text-secondary);">
                    The synchronization process is running in the background. 
                    Reload the page in a few moments to see updated versions.
                </p>
            </div>
        `;
    } else {
        html += `
            <div class="sync-result-item error">
                <h4><span class="sync-result-icon error">✗</span> Sync Failed</h4>
                <p>${result.error || 'An unknown error occurred during sync.'}</p>
            </div>
        `;
    }
    
    resultContent.innerHTML = html;
}

function displaySyncError(error, apiType) {
    document.getElementById('syncProgress').style.display = 'none';
    document.getElementById('syncResults').style.display = 'block';
    document.getElementById('syncCloseBtn').style.display = 'block';
    
    const resultContent = document.getElementById('syncResultContent');
    const apiName = apiType === 'management' ? 'Management' : 'GAiA';
    
    resultContent.innerHTML = `
        <div class="sync-result-item error">
            <h4><span class="sync-result-icon error">✗</span> Sync Failed to Start</h4>
            <p>${error.message || error}</p>
        </div>
        <div class="sync-result-item info">
            <h4><span class="sync-result-icon info">ⓘ</span> Troubleshooting</h4>
            <p>Check your internet connection and server configuration. Review the application logs for more details.</p>
        </div>
    `;
}

function openAPI(apiType) {
  let serverUrl, apiVersion;
  
  if (apiType === 'management') {
    serverUrl = document.getElementById('mgmtServerUrl').value;
    apiVersion = document.getElementById('mgmtApiVersion').value;
  } else if (apiType === 'gaia') {
    serverUrl = document.getElementById('gaiaServerUrl').value;
    apiVersion = document.getElementById('gaiaApiVersion').value;
  }
  
  // Build URL with query parameters
  const params = new URLSearchParams({
    api_type: apiType
  });
  
  if (serverUrl) {
    params.append('server_url', serverUrl);
  }
  
  // Only append version if it's a valid value (not loading or empty)
  if (apiVersion && apiVersion !== 'Loading versions...' && apiVersion !== 'Failed to load') {
    params.append('api_version', apiVersion);
  }

  
  // Open Swagger UI with custom configuration
  window.location.href = `/docs?${params.toString()}`;
}
