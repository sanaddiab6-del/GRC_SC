/**
 * api-client.ts – Production-ready API client with automatic token management
 *
 * Features:
 * - Automatic token attachment
 * - Token refresh on 401 with retry
 * - Prevents infinite loops
 * - Graceful error handling
 * - TypeScript support
 * - Request/response interceptors
 */

import axios, {
  AxiosInstance,
  AxiosError,
  AxiosResponse,
  AxiosHeaders,
  InternalAxiosRequestConfig,
} from 'axios';
import { 
  getAccessToken, 
  refreshAccessToken, 
  clearAuthData, 
  redirectToLogin 
} from './authService';

// ── Configuration ─────────────────────────────────────────────────────────────

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const REQUEST_TIMEOUT = 30000; // 30 seconds

// ── Types ─────────────────────────────────────────────────────────────────────

interface RequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
  _skipAuth?: boolean;
}

interface ApiErrorResponse {
  detail: string | Array<{
    loc: string[];
    msg: string;
    type: string;
  }>;
}

// ── API Client Setup ──────────────────────────────────────────────────────────

/**
 * Main API client instance with interceptors
 */
export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: REQUEST_TIMEOUT,
  headers: AxiosHeaders.from({
    'Content-Type': 'application/json',
  }),
});

const ensureAxiosHeaders = (headers?: InternalAxiosRequestConfig['headers']): AxiosHeaders => {
  return headers instanceof AxiosHeaders ? headers : AxiosHeaders.from(headers || {});
};

// ── Request Interceptor ───────────────────────────────────────────────────────

/**
 * Automatically attach Authorization header if token exists
 */
apiClient.interceptors.request.use(
  (config: RequestConfig) => {
    // Skip auth header for certain endpoints (login, register, etc.)
    if (config._skipAuth) {
      return config;
    }

    const token = getAccessToken();
    const headers = ensureAxiosHeaders(config.headers);
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    // Add request ID for debugging
    if (process.env.NODE_ENV === 'development') {
      headers.set('X-Request-ID', `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
    }

    config.headers = headers;

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ── Response Interceptor ──────────────────────────────────────────────────────

/**
 * Handle token refresh and retry logic
 */
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // Successful responses pass through unchanged
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as RequestConfig;

    // Only handle 401 errors for authenticated requests
    if (error.response?.status === 401 && originalRequest && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Attempt to refresh the token
        const newTokenData = await refreshAccessToken();
        
        if (newTokenData) {
          // Update the authorization header with new token
          const headers = ensureAxiosHeaders(originalRequest.headers);
          headers.set('Authorization', `Bearer ${newTokenData.access_token}`);
          originalRequest.headers = headers;
          
          // Retry the original request
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError);
      }

      // If refresh failed, clear auth data and redirect to login
      clearAuthData();
      
      // Get locale from current URL or default to 'en'
      const locale = getCurrentLocale();
      redirectToLogin(locale);
      
      return Promise.reject(error);
    }

    // Handle other errors
    return Promise.reject(enhanceError(error));
  }
);

// ── Utility Functions ─────────────────────────────────────────────────────────

/**
 * Get current locale from URL
 */
const getCurrentLocale = (): string => {
  if (typeof window === 'undefined') return 'en';
  
  const path = window.location.pathname;
  const segments = path.split('/').filter(Boolean);
  
  // Check if first segment is a locale
  if (segments.length > 0 && ['en', 'ar'].includes(segments[0])) {
    return segments[0];
  }
  
  return 'en';
};

/**
 * Enhance error with additional context
 */
const enhanceError = (error: AxiosError): AxiosError => {
  if (error.response) {
    // Server responded with error status
    const data = error.response.data as ApiErrorResponse;
    
    if (data?.detail) {
      if (typeof data.detail === 'string') {
        error.message = data.detail;
      } else if (Array.isArray(data.detail)) {
        // Handle Pydantic validation errors
        const messages = data.detail.map(err => 
          `${err.loc.join('.')}: ${err.msg}`
        );
        error.message = messages.join(', ');
      }
    }
  } else if (error.request) {
    // Network error
    error.message = 'Network error. Please check your connection.';
  }

  return error;
};

// ── Specialized Client Functions ──────────────────────────────────────────────

/**
 * Make authenticated API request
 */
export const authFetch = async <T = any>(
  url: string, 
  config?: Partial<RequestConfig>
): Promise<AxiosResponse<T>> => {
  return apiClient({
    url,
    ...config,
  });
};

/**
 * Make unauthenticated API request (skips auth header)
 */
export const publicFetch = async <T = any>(
  url: string,
  config?: Partial<RequestConfig>
): Promise<AxiosResponse<T>> => {
  return apiClient({
    url,
    ...config,
    _skipAuth: true,
  });
};

/**
 * GET request helper
 */
export const get = async <T = any>(
  url: string,
  config?: Partial<RequestConfig>
): Promise<AxiosResponse<T>> => {
  return authFetch<T>(url, { ...config, method: 'GET' });
};

/**
 * POST request helper
 */
export const post = async <T = any>(
  url: string,
  data?: any,
  config?: Partial<RequestConfig>
): Promise<AxiosResponse<T>> => {
  return authFetch<T>(url, { ...config, method: 'POST', data });
};

/**
 * PUT request helper
 */
export const put = async <T = any>(
  url: string,
  data?: any,
  config?: Partial<RequestConfig>
): Promise<AxiosResponse<T>> => {
  return authFetch<T>(url, { ...config, method: 'PUT', data });
};

/**
 * PATCH request helper
 */
export const patch = async <T = any>(
  url: string,
  data?: any,
  config?: Partial<RequestConfig>
): Promise<AxiosResponse<T>> => {
  return authFetch<T>(url, { ...config, method: 'PATCH', data });
};

/**
 * DELETE request helper
 */
export const del = async <T = any>(
  url: string,
  config?: Partial<RequestConfig>
): Promise<AxiosResponse<T>> => {
  return authFetch<T>(url, { ...config, method: 'DELETE' });
};

// ── File Upload Helper ────────────────────────────────────────────────────────

/**
 * Upload file with progress tracking
 */
export const uploadFile = async (
  url: string,
  file: File,
  onProgress?: (progress: number) => void,
  additionalData?: Record<string, any>
): Promise<AxiosResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  // Add additional form data if provided
  if (additionalData) {
    Object.entries(additionalData).forEach(([key, value]) => {
      formData.append(key, typeof value === 'string' ? value : JSON.stringify(value));
    });
  }
  
  return authFetch(url, {
    method: 'POST',
    data: formData,
    headers: AxiosHeaders.from({
      'Content-Type': 'multipart/form-data',
    }),
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(progress);
      }
    },
  });
};

// ── Error Handler Hook ────────────────────────────────────────────────────────

/**
 * Extract user-friendly error message from API error
 */
export const getErrorMessage = (error: any): string => {
  if (error?.response?.data?.detail) {
    const detail = error.response.data.detail;
    
    if (typeof detail === 'string') {
      return detail;
    }
    
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map(err => err.msg).join(', ');
    }
  }
  
  if (error?.message) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
};

/**
 * Check if error is due to network issues
 */
export const isNetworkError = (error: any): boolean => {
  return !error?.response && !!error?.request;
};

/**
 * Check if error is due to authentication issues
 */
export const isAuthError = (error: any): boolean => {
  return error?.response?.status === 401 || error?.response?.status === 403;
};

// ── Development Helpers ───────────────────────────────────────────────────────

/**
 * Log API request/response in development
 */
if (process.env.NODE_ENV === 'development') {
  apiClient.interceptors.request.use((config) => {
    console.log(`📤 API Request: ${config.method?.toUpperCase()} ${config.url}`, {
      headers: config.headers,
      data: config.data,
    });
    return config;
  });

  apiClient.interceptors.response.use(
    (response) => {
      console.log(`📥 API Response: ${response.status} ${response.config.url}`, {
        data: response.data,
      });
      return response;
    },
    (error) => {
      console.error(`❌ API Error: ${error.config?.url}`, {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
      });
      return Promise.reject(error);
    }
  );
}

export default apiClient;
