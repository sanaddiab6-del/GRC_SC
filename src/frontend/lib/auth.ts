/**
 * auth.ts – Authentication helpers with backward compatibility
 *
 * This file maintains the original API while using the new authService
 * internally for improved reliability and security.
 */

import {
  RegisterRequest,
  parseApiError,
  FieldErrors,
} from "@/types/api";

import {
  loginUser,
  logoutUser,
  fetchCurrentUser as fetchUser,
  getStoredUser,
  storeUser,
  getAccessToken,
  getRefreshToken,
  storeTokens,
  clearAuthData,
  API_BASE,
  type User,
} from './authService';

// ── Type Exports ──────────────────────────────────────────────────────────────

export type CurrentUser = User;

export interface LoginResult {
  ok: boolean;
  error?: string;
}

// ── Re-export utilities ───────────────────────────────────────────────────────

export {
  isAuthenticated,
  hasRole,
  hasAnyRole,
  isAdmin,
  currentUserHasRole,
  currentUserIsAdmin,
  API_BASE,
} from './authService';

// ── Storage helpers ──────────────────────────────────────────────────────────

export function saveTokens(accessToken: string, refreshToken: string): void {
  storeTokens({ access_token: accessToken, refresh_token: refreshToken });
}

export { getAccessToken, getRefreshToken };

export function clearTokens(): void {
  clearAuthData();
}

export function getCachedUserInfo(): CurrentUser | null {
  return getStoredUser();
}

export function saveUserInfo(user: CurrentUser): void {
  storeUser(user);
}

export function clearUserInfo(): void {
  clearAuthData();
}

// ── Fetch wrapper with Bearer auth ───────────────────────────────────────────

export async function authFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const token = getAccessToken();
  return fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(options.headers ?? {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });
}

// ── Login ────────────────────────────────────────────────────────────────────

/**
 * POST /api/v1/auth/login (OAuth2 form-encoded).
 * On success, persists tokens and returns { ok: true }.
 */
export async function login(
  email: string,
  password: string
): Promise<LoginResult> {
  const result = await loginUser(email, password);
  return {
    ok: result.success,
    error: result.error
  };
}

// ── Register ─────────────────────────────────────────────────────────────────

export type RegisterPayload = RegisterRequest;

export interface RegisterResult {
  ok: boolean;
  userId?: string;
  error?: string;
  fieldErrors?: FieldErrors;
  status?: number;
}

/**
 * POST /api/v1/auth/register
 */
export async function register(
  payload: RegisterPayload
): Promise<RegisterResult> {
  const body: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(payload)) {
    if (v !== undefined && v !== null && v !== "") {
      body[k] = v;
    }
  }

  if (process.env.NODE_ENV !== "production") {
    console.debug("[auth] register payload →", JSON.stringify(body));
  }

  try {
    const res = await fetch(`${API_BASE}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.ok) {
      const { message, fieldErrors, status } = await parseApiError(res);
      if (process.env.NODE_ENV !== "production") {
        console.warn("[auth] register failed", { status, message, fieldErrors });
      }
      return { ok: false, error: message, fieldErrors, status };
    }

    const data = await res.json();
    if (process.env.NODE_ENV !== "production") {
      console.debug("[auth] register success, user_id =", data?.user_id);
    }
    return { ok: true, userId: data.user_id };
  } catch (err) {
    const message = "Network error – is the backend running?";
    console.error("[auth] register network error", err);
    return { ok: false, error: message, status: 0 };
  }
}

// ── Logout ───────────────────────────────────────────────────────────────────

export async function logout(): Promise<void> {
  await logoutUser();
}

// ── Current user ─────────────────────────────────────────────────────────────

export async function fetchCurrentUser(): Promise<CurrentUser | null> {
  return await fetchUser();
}

/**
 * Validate the current session against the server with detailed status.
 */
export async function validateSession(): Promise<
  | { confirmed: true;  rejected: false; user: CurrentUser }
  | { confirmed: false; rejected: true;  user?: undefined }
  | { confirmed: false; rejected: false; user?: undefined }
> {
  const token = getAccessToken();
  if (!token) return { confirmed: false, rejected: true };

  try {
    const res = await authFetch("/api/v1/auth/me");

    if (res.ok) {
      const user = await res.json() as CurrentUser;
      saveUserInfo(user);
      return { confirmed: true, rejected: false, user };
    }

    if (res.status === 401 || res.status === 403) {
      return { confirmed: false, rejected: true };
    }

    return { confirmed: false, rejected: false };
  } catch {
    return { confirmed: false, rejected: false };
  }
}
