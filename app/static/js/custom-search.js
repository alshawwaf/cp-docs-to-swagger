/**
 * Custom Search Implementation for Swagger UI
 * Bypasses the slow internal filter by searching the spec directly and jumping to anchors.
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log('Custom Search: Initializing...');
    const searchInput = document.getElementById('custom-search-input');
    const resultsContainer = document.getElementById('custom-search-results');
    
    if (!searchInput || !resultsContainer) {
        console.error('Custom Search: Elements not found');
        return;
    }

    let searchIndex = [];
    let isIndexed = false;
    let isIndexing = false;

    // Build index from Swagger spec
    async function buildIndex() {
        if (isIndexed || isIndexing) return;
        isIndexing = true;
        console.log('Custom Search: Building index...');
        
        try {
            let spec = null;
            
            // Try to get from Swagger UI first (Safe access)
            try {
                if (window.ui && typeof window.ui.spec === 'function') {
                    const specObj = window.ui.spec();
                    if (specObj && specObj.selectors && specObj.selectors.specJson) {
                        const jsonFn = specObj.selectors.specJson;
                        if (typeof jsonFn === 'function' && typeof jsonFn().toJS === 'function') {
                            const uiSpec = jsonFn().toJS();
                            if (uiSpec && uiSpec.paths) {
                                console.log('Custom Search: Got spec from Swagger UI');
                                spec = uiSpec;
                            }
                        }
                    }
                }
            } catch (uiError) {
                console.warn('Custom Search: Failed to get spec from UI, trying fallback', uiError);
            }
            
            // Fallback: Fetch from URL if UI not ready or empty
            if (!spec && window.api_url) {
                console.log('Custom Search: Fetching spec from URL:', window.api_url);
                try {
                    const resp = await fetch(window.api_url);
                    if (resp.ok) {
                        spec = await resp.json();
                        console.log('Custom Search: Fetched spec from URL successfully');
                    } else {
                        console.error('Custom Search: Failed to fetch spec from URL', resp.status);
                    }
                } catch (fetchError) {
                    console.error('Custom Search: Fetch error', fetchError);
                }
            }

            if (!spec || !spec.paths) {
                console.log('Custom Search: Spec not ready yet');
                isIndexing = false;
                return;
            }

            searchIndex = [];
            
            Object.entries(spec.paths).forEach(([path, methods]) => {
                Object.entries(methods).forEach(([method, op]) => {
                    if (method === 'parameters') return;
                    
                    searchIndex.push({
                        path: path,
                        method: method,
                        summary: op.summary || '',
                        description: op.description || '',
                        operationId: op.operationId || '',
                        tags: op.tags || [],
                        // Construct anchor: #/Tag/operationId
                        anchor: `/${op.tags ? op.tags[0] : 'default'}/${op.operationId}`
                    });
                });
            });
            
            console.log(`Custom Search: Indexed ${searchIndex.length} operations.`);
            isIndexed = true;
            searchInput.placeholder = `Search ${searchIndex.length} operations...`;
        } catch (e) {
            console.error('Custom Search: Indexing failed', e);
        } finally {
            isIndexing = false;
        }
    }

    // Debounce function
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Search function with Ranking
    function performSearch(query) {
        if (!isIndexed) {
            buildIndex();
            if (!isIndexed) return; 
        }
        
        if (!query) {
            resultsContainer.classList.remove('show');
            resultsContainer.style.display = 'none';
            return;
        }

        const lowerQuery = query.toLowerCase().trim();
        if (lowerQuery.length < 2) return; // Wait for at least 2 chars

        // Scoring Algorithm
        const results = searchIndex.map(item => {
            let score = 0;
            const summary = item.summary.toLowerCase();
            const opId = item.operationId.toLowerCase();
            const path = item.path.toLowerCase();
            const tags = item.tags.map(t => t.toLowerCase());

            // 1. Exact Match (Highest Priority)
            if (summary === lowerQuery) score += 100;
            if (opId === lowerQuery) score += 90;

            // 2. Starts With (High Priority)
            if (summary.startsWith(lowerQuery)) score += 50;
            if (opId.startsWith(lowerQuery)) score += 45;

            // 3. Contains (Medium Priority)
            if (summary.includes(lowerQuery)) score += 30;
            if (opId.includes(lowerQuery)) score += 25;
            
            // 4. Path & Tags (Lower Priority)
            if (path.includes(lowerQuery)) score += 15;
            if (tags.some(t => t.includes(lowerQuery))) score += 10;

            // 5. Description (Lowest)
            if (item.description && item.description.toLowerCase().includes(lowerQuery)) score += 5;

            return { ...item, score };
        })
        .filter(item => item.score > 0)
        .sort((a, b) => b.score - a.score) // Sort by score descending
        .slice(0, 15); // Top 15 results

        displayResults(results);
    }

    function displayResults(results) {
        resultsContainer.innerHTML = '';
        
        if (results.length === 0) {
            const noResult = document.createElement('div');
            noResult.className = 'search-result-item empty';
            noResult.textContent = 'No matching operations found.';
            resultsContainer.appendChild(noResult);
        } else {
            results.forEach(item => {
                const div = document.createElement('div');
                div.className = 'search-result-item';
                
                // Method Badge Color
                const method = item.method.toLowerCase();
                
                div.innerHTML = `
                    <div class="result-header">
                        <span class="method-badge method-${method}">${method}</span>
                        <span class="result-summary">${highlightMatch(item.summary || item.operationId)}</span>
                    </div>
                    <div class="result-meta">
                        <span class="result-path">${item.path}</span>
                        ${item.tags && item.tags.length ? `<span class="result-tag">${item.tags[0]}</span>` : ''}
                    </div>
                `;
                
                div.addEventListener('click', () => {
                    navigateToOperation(item);
                });
                
                resultsContainer.appendChild(div);
            });
        }
        
        resultsContainer.classList.add('show');
        resultsContainer.style.display = 'block';
    }

    function highlightMatch(text) {
        // Simple highlight logic (optional, can be expanded)
        return text; 
    }

    function navigateToOperation(item) {
        console.log('Custom Search: Navigating to', item.operationId);
        
        // Clear search
        resultsContainer.classList.remove('show');
        resultsContainer.style.display = 'none';
        searchInput.value = '';

        if (window.ui) {
            const tag = item.tags[0];
            const opId = item.operationId;
            
            try {
                // 1. Try Swagger UI's internal API to expand
                // This works if the tag/opId match exactly what Swagger expects
                window.ui.layoutActions.show(["operations", tag, opId], true);
            } catch (e) {
                console.warn("Custom Search: layoutActions.show failed", e);
            }

            // 2. DOM-based Fallback: Find, Scroll, and Click
            setTimeout(() => {
                // A. Expand Parent Tag first
                expandTag(tag);

                // B. Expand Operation
                setTimeout(() => {
                    const element = findOperationElement(tag, opId);
                    
                    if (element) {
                        // Scroll to element with offset for fixed header
                        // We use a timeout to ensure layout is stable after expansion
                        setTimeout(() => {
                            const headerOffset = 120; // Height of fixed header + padding
                            const elementPosition = element.getBoundingClientRect().top;
                            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
                      
                            window.scrollTo({
                                 top: offsetPosition,
                                 behavior: "smooth"
                            });
                        }, 50);
                        
                        // Flash effect
                        element.style.transition = 'background 0.5s';
                        const originalBg = element.style.background;
                        element.style.background = 'rgba(236, 72, 153, 0.1)';
                        setTimeout(() => {
                            element.style.background = originalBg;
                        }, 1000);

                        // Force Expand if not already open
                        // Check if it has the 'is-open' class
                        if (!element.classList.contains('is-open')) {
                            console.log('Custom Search: Element not open, clicking summary to expand');
                            const summary = element.querySelector('.opblock-summary');
                            if (summary) {
                                summary.click();
                            }
                        }
                    } else {
                        console.warn('Custom Search: Element not found for scrolling/expanding');
                    }
                }, 100); // Wait for tag expansion
            }, 100);
        }
    }

    function expandTag(tag) {
        // Swagger UI Tag ID format: operations-tag-{tag}
        const escape = (s) => s.replace(/\s+/g, '_').replace(/\//g, '_');
        const tagId = `operations-tag-${escape(tag)}`;
        const tagHeader = document.getElementById(tagId);
        
        if (tagHeader) {
            // Check if the next sibling (the content) is visible or if the header indicates closed state
            // Usually Swagger UI puts 'is-open' on the parent section or similar.
            // But clicking the header toggles it.
            // Let's check the data-is-open attribute or class on the header or its parent.
            
            // In standard Swagger UI, the header is inside a div that might have is-open.
            // Or we can look for the SVG icon direction.
            
            // Safer approach: Check if the section is collapsed.
            // The tag header is usually an h4 or div.
            // The content is in a sibling div.
            
            // Let's try to find the parent span/div that holds the tag section
            const tagSection = tagHeader.closest('.opblock-tag-section');
            if (tagSection && !tagSection.classList.contains('is-open')) {
                console.log('Custom Search: Tag section closed, clicking to expand:', tag);
                tagHeader.click();
            }
        } else {
            // Fallback: Try to find by text content if ID fails
            const headers = document.querySelectorAll('.opblock-tag');
            for (let h of headers) {
                if (h.textContent.trim().includes(tag) || h.id.includes(escape(tag))) {
                     const tagSection = h.closest('.opblock-tag-section');
                     if (tagSection && !tagSection.classList.contains('is-open')) {
                         h.click();
                     }
                     break;
                }
            }
        }
    }

    function findOperationElement(tag, opId) {
        // Strategy 1: Construct ID (Swagger UI standard)
        // operations-{tag}-{opId}
        // Swagger UI escapes spaces to _, etc.
        const escape = (s) => s.replace(/\s+/g, '_').replace(/\//g, '_'); // Basic escape
        const id1 = `operations-${escape(tag)}-${opId}`;
        let el = document.getElementById(id1);
        if (el) return el;

        // Strategy 2: Search by partial ID match on opId
        // Since operationId is usually unique, we can look for an element 
        // whose ID ends with -{opId}
        // The ID is on the div with class 'opblock'
        const opBlocks = document.querySelectorAll('.opblock');
        for (let op of opBlocks) {
            // Check if ID ends with the opId (preceded by -)
            if (op.id && op.id.endsWith(`-${opId}`)) {
                return op;
            }
        }
        
        // Strategy 3: Search by data attributes or content if needed (Last resort)
        // Not implemented to avoid performance hit, Strategy 2 is usually sufficient
        
        return null;
    }

    // Event Listeners
    searchInput.addEventListener('input', debounce((e) => {
        performSearch(e.target.value);
    }, 300));

    // Close on click outside
    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !resultsContainer.contains(e.target)) {
            resultsContainer.classList.remove('show');
            resultsContainer.style.display = 'none';
        }
    });
    
    // Build index loop
    // Check every 2 seconds until indexed
    const indexInterval = setInterval(() => {
        if (isIndexed) {
            clearInterval(indexInterval);
        } else {
            buildIndex();
        }
    }, 2000);
});
