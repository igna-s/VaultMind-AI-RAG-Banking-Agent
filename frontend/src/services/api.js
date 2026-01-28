// Dynamically select backend URL based on current hostname to ensure SameSite cookie compliance
const API_URL = window.location.hostname === '127.0.0.1'
    ? 'http://127.0.0.1:8000'
    : 'http://localhost:8000';

/**
 * Custom fetch wrapper that handles:
 * - Base URL
 * - JSON headers
 * - Auth headers (Bearer token)
 * - Credentials (cookies)
 * - Error handling (including 401)
 */
export const api = {
    get: (url, options = {}) => request(url, { ...options, method: 'GET' }),
    post: (url, body, options = {}) => request(url, { ...options, method: 'POST', body }),
    put: (url, body, options = {}) => request(url, { ...options, method: 'PUT', body }),
    delete: (url, options = {}) => request(url, { ...options, method: 'DELETE' }),
};

async function request(endpoint, options = {}) {
    // Ensure endpoint starts with / if not present
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = `${API_URL}${path}`;

    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    // 1. Handle form-data (don't set Content-Type manually if body is FormData)
    if (options.body instanceof FormData) {
        delete headers['Content-Type'];
    }
    // 2. Handle URLSearchParams (set correct content type)
    else if (options.body instanceof URLSearchParams) {
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
    }
    // 3. Stringify JSON body if needed
    else if (options.body && typeof options.body === 'object') {
        options.body = JSON.stringify(options.body);
    }

    const config = {
        ...options,
        headers,
        credentials: 'include', // Important for cookies
    };

    try {
        const response = await fetch(url, config);

        // Handle 401 Unauthorized globally
        if (response.status === 401) {
            // Dispatch a custom event or call a global logout handler if possible.
            // For now, we'll throw a specific error that AuthContext can catch.
            // Alternatively, we could clear local storage here effectively logging out the user from the frontend perspective immediately.
            localStorage.removeItem('user');
            window.dispatchEvent(new Event('auth:logout')); // Simple event bus
        }

        // Parse response
        const contentType = response.headers.get('content-type');
        let data;
        if (contentType && contentType.includes('application/json')) {
            data = await response.json();
        } else {
            data = await response.text();
        }

        if (!response.ok) {
            throw {
                status: response.status,
                message: (data && data.detail) || data || 'Request failed',
                data
            };
        }

        return data;
    } catch (error) {
        console.error('API Request Error:', error);
        throw error;
    }
}
