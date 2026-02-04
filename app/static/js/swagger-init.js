/**
 * Swagger UI Initialization Logic
 */

window.onload = function() {
    // Storage for session ID
    let sessionId = localStorage.getItem('chkp-session-id') || null;
    
    // Toggle Logic (handled by theme.js now, but we need to handle the specific swagger CSS disable/enable if needed)
    // Actually, with the new CSS variables approach, we don't need to disable the swagger CSS file anymore.
    // We just override the variables.
    
    // Initialize Swagger UI
    window.ui = SwaggerUIBundle({
      url: window.api_url, // Passed from template
      dom_id: '#swagger-ui',
      deepLinking: true,
      presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIStandalonePreset
      ],
      plugins: [
        SwaggerUIBundle.plugins.DownloadUrl
      ],
      layout: "StandaloneLayout",
      docExpansion: "none",
      validatorUrl: "none",
      filter: false,
      defaultModelsExpandDepth: -1,
      defaultModelExpandDepth: 1,
      syntaxHighlight: false,
      displayOperationId: false,
      displayRequestDuration: true,
      persistAuthorization: true,
      tryItOutEnabled: true,
      // Disable tag sorting to respect the order in the spec (Check Point order)
      tagsSorter: null,
      operationsSorter: "alpha",
      // Prefer showing examples over schema-generated values
      defaultModelRendering: 'example',
      showExtensions: true,
      
      // Request interceptor - always attach the stored session ID (if any)
      requestInterceptor: (request) => {
        const storedSessionId = localStorage.getItem('chkp-session-id');
        
        if (storedSessionId) {
          request.headers['X-chkp-sid'] = storedSessionId;
        }
        return request;
      },

      // Response interceptor - capture the session ID from the login response
      responseInterceptor: (response) => {
        // Detect the login response (the proxy endpoint ends with /login)
        if (response.url && response.url.includes('/login')) {
          // The proxy forwards the original header; check both capitalisations
          const sid = response.headers['X-chkp-sid'] || response.headers['x-chkp-sid'];
          
          if (sid) {
            // Persist the session ID for future requests
            localStorage.setItem('chkp-session-id', sid);
            
            // Optionally pre-authorize an API key (keeps the UI "locked")
            if (window.ui && typeof window.ui.preauthorizeApiKey === 'function') {
              window.ui.preauthorizeApiKey('sessionId', sid);
            }
            
            console.log('Login successful - session ID captured.');
          }
        }
        
        // Handle possible session expiration (401/403)
        if (response.status === 401 || response.status === 403) {
          localStorage.removeItem('chkp-session-id');
        }
        
        return response;
      },
      onComplete: function() {
         // Ensure the title is correct if we are in custom mode
         
         // Add class to all category tags for consistent styling
         setTimeout(() => {
           const tags = document.querySelectorAll('.opblock-tag');
           tags.forEach(tag => {
             tag.classList.add('tag-category');
           });
         }, 50);
      }
    });
    
    // If we have a stored session, automatically preauthorize
    if (sessionId) {
      console.log('Found stored session ID, preauthorizing...');
      setTimeout(() => {
        window.ui.preauthorizeApiKey('sessionId', sessionId);
        console.log('✓ Preauthorized with stored sessionId');
      }, 1000);
    }
  };
