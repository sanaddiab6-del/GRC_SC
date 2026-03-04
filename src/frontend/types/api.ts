/**
 * api.ts – Shared API contract types.
 *
 * This file is the SINGLE SOURCE OF TRUTH for all request/response shapes
 * exchanged with the FastAPI backend.
 *
 * KEEP IN SYNC WITH: src/backend/auth/schemas.py
 * When a backend Pydantic schema changes, update the corresponding
 * interface here so TypeScript catches mismatches at compile-time.
 */

// ── Register / User ──────────────────────────────────────────────────────────

/**
 * Matches backend `UserCreate` (auth/schemas.py).
 *
 * Password rules (NCA ECC-IS-3 / PDPL Art. 29):
 *   - Min 12 characters
 *   - At least 1 uppercase letter  [A-Z]
 *   - At least 1 lowercase letter  [a-z]
 *   - At least 1 digit             [0-9]
 *   - At least 1 special character [!@#$%^&*(),.?":{}|<>]
 */
export interface RegisterRequest {
  email: string;
  password: string;
  full_name_en?: string;
  full_name_ar?: string;
  organization_name?: string;
}

/**
 * Matches backend `UserResponse` (auth/schemas.py).
 */
export interface UserResponse {
  user_id: string;
  email: string;
  full_name_en?: string | null;
  full_name_ar?: string | null;
  is_active: boolean;
  is_verified: boolean;
  last_login_at?: string | null;
  created_at: string;
  roles: string[];
}

// ── Auth tokens ───────────────────────────────────────────────────────────────

/**
 * Matches backend `TokenResponse` (auth/schemas.py).
 */
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

// ── Error shapes ──────────────────────────────────────────────────────────────

/**
 * A single entry in FastAPI's 422 Unprocessable Entity detail array.
 * Example: { loc: ["body", "password"], msg: "Value error, ...", type: "value_error" }
 */
export interface PydanticValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}

/**
 * The JSON body FastAPI returns for 4xx errors.
 * - 400 / 409: `detail` is a plain string.
 * - 422:        `detail` is a `PydanticValidationError[]`.
 */
export interface ApiErrorBody {
  detail: string | PydanticValidationError[];
}

/**
 * Map of field name → error message, used for inline field-level errors.
 * The special key `"_form"` holds a non-field (whole-form) error.
 */
export type FieldErrors = Record<string, string>;

// ── Error utilities ───────────────────────────────────────────────────────────

/**
 * Convert a raw `ApiErrorBody` to a plain human-readable string.
 *
 * - String detail  → returned as-is.
 * - Array detail   → each item formatted as "fieldName: message", joined by "; ".
 */
export function formatApiError(
  body: ApiErrorBody | null | undefined
): string {
  if (!body) return "Unknown error";
  const { detail } = body;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((e) => {
        // loc is e.g. ["body", "password"] — strip the top-level "body" key
        const path = e.loc
          .filter((p) => p !== "body" && p !== "query" && p !== "header")
          .join(".");
        return path ? `${path}: ${e.msg}` : e.msg;
      })
      .join("; ");
  }
  return "Unexpected error format";
}

/**
 * Convert a `PydanticValidationError[]` to a `FieldErrors` map so the
 * register/login form can highlight the exact field that failed.
 *
 * Example input:
 *   [{ loc: ["body","password"], msg: "Password must contain...", type: "value_error" }]
 * Example output:
 *   { password: "Password must contain..." }
 */
export function validationErrorsToFieldMap(
  errors: PydanticValidationError[]
): FieldErrors {
  const map: FieldErrors = {};
  for (const err of errors) {
    // The last string segment in loc is the field name
    const fieldCandidates = err.loc.filter(
      (p): p is string =>
        typeof p === "string" &&
        p !== "body" &&
        p !== "query" &&
        p !== "header"
    );
    const field = fieldCandidates.at(-1) ?? "_form";
    // Keep first error per field
    if (!map[field]) {
      map[field] = err.msg.replace(/^Value error, /i, "");
    }
  }
  return map;
}

/**
 * Awaits a `fetch` Response that is NOT ok, parses the body, and returns
 * a structured result with both a human string and optional field map.
 */
export async function parseApiError(res: Response): Promise<{
  message: string;
  fieldErrors: FieldErrors;
  status: number;
}> {
  const body: ApiErrorBody = await res
    .json()
    .catch(() => ({ detail: `HTTP ${res.status}` }));

  const fieldErrors: FieldErrors = {};
  let message: string;

  if (typeof body.detail === "string") {
    message = body.detail;
  } else if (Array.isArray(body.detail)) {
    message = formatApiError(body);
    Object.assign(fieldErrors, validationErrorsToFieldMap(body.detail));
  } else {
    message = `HTTP ${res.status}`;
  }

  return { message, fieldErrors, status: res.status };
}
