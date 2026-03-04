/**
 * authService.ts – Production-ready authentication service
 *
 * Features:
 * - Secure token storage in localStorage
 * - Automatic token refresh with retry logic
 * - Hydration-safe for Next.js
 * - Comprehensive error handling
 * - Clean RBAC utilities
 * - No race conditions or infinite loops
 */

// ── Types ────────────────────────────────────────────────────────────────────

export interface User {
  user_id: string;
  email: string;
  full_name_en?: string;
  full_name_ar?: string;
  is_active: boolean;
  is_verified: boolean;
  roles: string[];
  created_at?: string;
  last_login_at?: string;
}

export interface TokenData {
  access_token: string;
  refresh_token: string;
  token_type?: string;
  expires_in?: number;
}

export interface LoginResult {
  success: boolean;
  error?: string;
  user?: User;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  isLoading: boolean;
}

// ── In-memory user cache ───────────────────────────────────────────────────

let currentUserCache: User | null = null;
let currentUserPromise: Promise<User | null> | null = null;
let currentUserCachedAt: number | null = null;
const CURRENT_USER_TTL_MS = 60 * 1000;

const debugLog = (message: string, data?: Record<string, unknown>): void => {
  if (process.env.NODE_ENV !== 'development') return;
  if (data) {
    console.log(`[auth] ${message}`, data);
    return;
  }
  console.log(`[auth] ${message}`);
};

// ── Constants ─────────────────────────────────────────────────────────────────

const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token', 
  USER_INFO: 'user_info',
  EXPIRES_AT: 'token_expires_at',
} as const;

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const REFRESH_THRESHOLD_MS = 60 * 1000; // Refresh if expires within 1 minute

// ── Utility Functions ─────────────────────────────────────────────────────────

/**
 * Safe localStorage operations that handle SSR/hydration
 */
const storage = {
  get: (key: string): string | null => {
    if (typeof window === 'undefined') return null;
    try {
      return localStorage.getItem(key);
    } catch {
      return null;
    }
  },

  set: (key: string, value: string): void => {
    if (typeof window === 'undefined') return;
    try {
      localStorage.setItem(key, value);
    } catch (error) {
      console.warn('Failed to save to localStorage:', error);
    }
  },

  remove: (key: string): void => {
    if (typeof window === 'undefined') return;
    try {
      localStorage.removeItem(key);
    } catch {
      // Ignore errors during cleanup
    }
  },

  clear: (): void => {
    if (typeof window === 'undefined') return;
    try {
      Object.values(STORAGE_KEYS).forEach(key => {
        localStorage.removeItem(key);
      });
    } catch {
      // Ignore errors during cleanup
    }
  }
};

/**
 * Check if we're running in a browser environment
 */
const isBrowser = (): boolean => typeof window !== 'undefined';

// ── Token Management ──────────────────────────────────────────────────────────

/**
 * Get access token from storage
 */
export const getAccessToken = (): string | null => {
  return storage.get(STORAGE_KEYS.ACCESS_TOKEN);
};

/**
 * Get refresh token from storage
 */
export const getRefreshToken = (): string | null => {
  return storage.get(STORAGE_KEYS.REFRESH_TOKEN);
};

/**
 * Check if user has valid authentication token
 */
export const isAuthenticated = (): boolean => {
  return !!getAccessToken();
};

/**
 * Get stored user information
 */
export const getStoredUser = (): User | null => {
  const userStr = storage.get(STORAGE_KEYS.USER_INFO);
  if (!userStr) return null;
  
  try {
    return JSON.parse(userStr) as User;
  } catch {
    return null;
  }
};

/**
 * Store authentication tokens securely
 */
export const storeTokens = (tokenData: TokenData): void => {
  storage.set(STORAGE_KEYS.ACCESS_TOKEN, tokenData.access_token);
  storage.set(STORAGE_KEYS.REFRESH_TOKEN, tokenData.refresh_token);
  
  // Calculate and store expiration time
  if (tokenData.expires_in) {
    const expiresAt = Date.now() + (tokenData.expires_in * 1000);
    storage.set(STORAGE_KEYS.EXPIRES_AT, expiresAt.toString());
  }
};

/**
 * Store user information
 */
export const storeUser = (user: User): void => {
  storage.set(STORAGE_KEYS.USER_INFO, JSON.stringify(user));
};

/**
 * Check if token needs refresh (within threshold)
 */
export const shouldRefreshToken = (): boolean => {
  const expiresAtStr = storage.get(STORAGE_KEYS.EXPIRES_AT);
  if (!expiresAtStr) return false;
  
  try {
    const expiresAt = parseInt(expiresAtStr);
    return Date.now() >= (expiresAt - REFRESH_THRESHOLD_MS);
  } catch {
    return false;
  }
};

/**
 * Clear all authentication data
 */
export const clearAuthData = (): void => {
  storage.clear();
  currentUserCache = null;
  currentUserPromise = null;
  currentUserCachedAt = null;
};

/**
 * Clear in-memory current user cache.
 */
export const clearUserCache = (): void => {
  currentUserCache = null;
  currentUserPromise = null;
  currentUserCachedAt = null;
};

// ── API Functions ─────────────────────────────────────────────────────────────

/**
 * Refresh access token using refresh token
 */
export const refreshAccessToken = async (): Promise<TokenData | null> => {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return null;

  try {
    const response = await fetch(`${API_BASE}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      // Refresh token is invalid/expired
      clearAuthData();
      return null;
    }

    const tokenData = await response.json() as TokenData;
    storeTokens(tokenData);
    return tokenData;
  } catch (error) {
    console.error('Token refresh failed:', error);
    clearAuthData();
    return null;
  }
};

/**
 * Login user with email and password
 */
export const loginUser = async (email: string, password: string): Promise<LoginResult> => {
  try {
    // Clear any existing auth data
    clearAuthData();
    
    const formData = new URLSearchParams();
    formData.append('username', email); // OAuth2 uses 'username' field
    formData.append('password', password);

    const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      return {
        success: false,
        error: errorData?.detail || 'Login failed'
      };
    }

    const tokenData = await response.json() as TokenData;
    
    // Store tokens
    storeTokens(tokenData);

    // Fetch and store user information
    try {
      const user = await fetchCurrentUser();
      if (user) {
        return { success: true, user };
      }
    } catch (error) {
      console.warn('Failed to fetch user info after login:', error);
    }

    return { success: true };
  } catch (error) {
    console.error('Login error:', error);
    return {
      success: false,
      error: 'Network error. Please check your connection.'
    };
  }
};

/**
 * Fetch current user information from API
 */
export const fetchCurrentUser = async (): Promise<User | null> => {
  if (currentUserCache && currentUserCachedAt) {
    const ageMs = Date.now() - currentUserCachedAt;
    if (ageMs < CURRENT_USER_TTL_MS) {
      debugLog('cache hit', { ageMs });
      return currentUserCache;
    }
    debugLog('cache expired', { ageMs });
    currentUserCache = null;
    currentUserCachedAt = null;
  }

  if (currentUserCache) {
    debugLog('cache hit', { ageMs: 0 });
    return currentUserCache;
  }

  if (currentUserPromise) {
    debugLog('in-flight request reuse');
    return currentUserPromise;
  }

  debugLog('cache miss');

  const token = getAccessToken();
  if (!token) return null;

  const fetchOnce = async (accessToken: string, allowRefresh: boolean): Promise<User | null> => {
    try {
      debugLog('request /api/v1/auth/me');
      const response = await fetch(`${API_BASE}/api/v1/auth/me`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (response.status === 401 && allowRefresh) {
        debugLog('refresh token flow');
        const refreshed = await refreshAccessToken();
        if (!refreshed) {
          clearAuthData();
          return null;
        }
        return fetchOnce(refreshed.access_token, false);
      }

      if (!response.ok) {
        return null;
      }

      const user = await response.json() as User;
      currentUserCache = user;
      currentUserCachedAt = Date.now();
      storeUser(user);
      return user;
    } catch (error) {
      console.error('Failed to fetch current user:', error);
      return null;
    }
  };

  currentUserPromise = fetchOnce(token, true).finally(() => {
    currentUserPromise = null;
  });

  return currentUserPromise;
};

/**
 * Force refresh the current user from the server.
 */
export const refreshCurrentUser = async (): Promise<User | null> => {
  clearUserCache();
  return fetchCurrentUser();
};

/**
 * Logout user and clear all data
 */
export const logoutUser = async (): Promise<void> => {
  const token = getAccessToken();
  
  // Clear local data first
  clearAuthData();

  // Notify server (best effort)
  if (token) {
    try {
      await fetch(`${API_BASE}/api/v1/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
    } catch {
      // Ignore network errors during logout
    }
  }
};

/**
 * Validate current session with server
 */
export const validateSession = async (): Promise<{
  valid: boolean;
  user?: User;
  needsRefresh?: boolean;
}> => {
  const token = getAccessToken();
  if (!token) {
    return { valid: false };
  }

  // Check if token needs refresh
  if (shouldRefreshToken()) {
    const refreshed = await refreshAccessToken();
    if (!refreshed) {
      return { valid: false };
    }
    return { valid: true, needsRefresh: true };
  }

  // Validate with server
  try {
    const user = await fetchCurrentUser();
    return { 
      valid: !!user, 
      user: user || undefined 
    };
  } catch {
    return { valid: false };
  }
};

// ── RBAC Utilities ────────────────────────────────────────────────────────────

/**
 * Check if user has specific role
 */
export const hasRole = (user: User | null, role: string): boolean => {
  return user?.roles?.includes(role) || false;
};

/**
 * Check if user has any of the specified roles
 */
export const hasAnyRole = (user: User | null, roles: string[]): boolean => {
  if (!user?.roles) return false;
  return roles.some(role => user.roles.includes(role));
};

/**
 * Check if user has admin privileges
 */
export const isAdmin = (user: User | null): boolean => {
  return hasAnyRole(user, ['Admin', 'admin', 'super_admin']);
};

/**
 * Check if current stored user has specific role (without API call)
 */
export const currentUserHasRole = (role: string): boolean => {
  if (!isBrowser()) return false;
  const user = getStoredUser();
  return hasRole(user, role);
};

/**
 * Check if current stored user is admin (without API call)
 */
export const currentUserIsAdmin = (): boolean => {
  if (!isBrowser()) return false;
  const user = getStoredUser();
  return isAdmin(user);
};

// ── Auth State Hook ───────────────────────────────────────────────────────────

/**
 * Get current authentication state
 */
export const getAuthState = (): AuthState => {
  if (!isBrowser()) {
    return {
      isAuthenticated: false,
      user: null,
      token: null,
      isLoading: true,
    };
  }

  const token = getAccessToken();
  const user = getStoredUser();

  return {
    isAuthenticated: !!token,
    user,
    token,
    isLoading: false,
  };
};

// ── Navigation Helpers ────────────────────────────────────────────────────────

/**
 * Get locale-aware redirect URLs
 */
export const getRedirectUrls = (locale: string = 'en') => ({
  login: `/${locale}/login`,
  dashboard: `/${locale}/dashboard`,
  unauthorized: `/${locale}/unauthorized`,
});

/**
 * Redirect to login with proper locale
 */
export const redirectToLogin = (locale: string = 'en'): void => {
  if (!isBrowser()) return;
  
  const { login } = getRedirectUrls(locale);
  window.location.href = login;
};

/**
 * Redirect to dashboard with proper locale  
 */
export const redirectToDashboard = (locale: string = 'en'): void => {
  if (!isBrowser()) return;
  
  const { dashboard } = getRedirectUrls(locale);
  window.location.href = dashboard;
};

// ── Development Utilities ─────────────────────────────────────────────────────

/**
 * Debug current auth state (development only)
 */
export const debugAuthState = (): void => {
  if (process.env.NODE_ENV !== 'development') return;
  
  console.group('🔐 Auth Debug State');
  console.log('Is Authenticated:', isAuthenticated());
  console.log('Access Token:', getAccessToken() ? '✅ Present' : '❌ Missing');
  console.log('Refresh Token:', getRefreshToken() ? '✅ Present' : '❌ Missing');
  console.log('Stored User:', getStoredUser());
  console.log('Needs Refresh:', shouldRefreshToken());
  console.groupEnd();
};