import { useState, useCallback } from 'react';
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

/**
 * Custom hook for API calls with loading and error states
 * @param {string} url - API endpoint URL
 * @param {object} options - Axios options
 * @returns {object} { data, loading, error, execute, reset }
 */
export function useApi(url, options = {}) {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const execute = useCallback(async (customUrl = null, customOptions = {}) => {
        setLoading(true);
        setError(null);

        try {
            const endpoint = customUrl || url;
            const fullUrl = endpoint.startsWith('http') ? endpoint : `${API_BASE}${endpoint}`;
            const response = await axios({
                url: fullUrl,
                ...options,
                ...customOptions
            });
            setData(response.data);
            return response.data;
        } catch (err) {
            const errorMessage = err.response?.data?.detail || err.message || 'An error occurred';
            setError(errorMessage);
            throw err;
        } finally {
            setLoading(false);
        }
    }, [url, options]);

    const reset = useCallback(() => {
        setData(null);
        setError(null);
        setLoading(false);
    }, []);

    return { data, loading, error, execute, reset };
}

/**
 * Shorthand for GET requests
 */
export function useGet(url) {
    return useApi(url, { method: 'GET' });
}

/**
 * Shorthand for POST requests
 */
export function usePost(url) {
    return useApi(url, { method: 'POST' });
}

/**
 * Shorthand for PUT requests
 */
export function usePut(url) {
    return useApi(url, { method: 'PUT' });
}

/**
 * Shorthand for DELETE requests
 */
export function useDelete(url) {
    return useApi(url, { method: 'DELETE' });
}
