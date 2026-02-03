// Dynamically select backend URL based on environment variables
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';


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

    const response = await fetch(url, config);

    // Handle 401 Unauthorized globally
    if (response.status === 401) {
        // Token expired or invalid
        localStorage.removeItem('user');
        window.dispatchEvent(new Event('auth:logout'));
    }

    // Handle 403 Forbidden (sometimes used for invalid session too, but distinct from unverified email)
    // BE CAREFUL: We return 403 for unverified email too. We shouldn't logout automatically then.
    // Let's rely on the specific error message or context.
    // For now, only logout on 401 which is strictly "Unauthenticated".

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
}
