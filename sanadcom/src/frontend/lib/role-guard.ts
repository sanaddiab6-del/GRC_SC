import React, { useMemo } from 'react';
import { jwtDecode } from 'jwt-decode';

// Permission matrix: maps actions to allowed roles
export const PERMISSION_MATRIX: Record<string, string[]> = {
  'approve_evidence': ['Admin', 'ComplianceOfficer', 'Auditor'],
  'edit_control': ['Admin', 'ComplianceOfficer'],
  'delete_control': ['Admin'],
  'view_reports': ['Admin', 'ComplianceOfficer', 'Auditor', 'Analyst', 'Viewer'],
  'generate_report': ['Admin', 'ComplianceOfficer', 'Auditor', 'Analyst'],
  'manage_users': ['Admin'],
  'approve_risk': ['Admin', 'ComplianceOfficer'],
  'close_incident': ['Admin', 'ComplianceOfficer', 'Auditor'],
  // ...add more actions as needed
};

// JWT payload type (minimal)
interface JWTPayload {
  roles?: string[];
  permissions?: string[];
  [key: string]: any;
}

// Get JWT from localStorage (or cookie if needed)
function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

// Decode JWT and extract roles/permissions
function getUserPermissions(): { roles: string[]; permissions: string[] } {
  const token = getToken();
  if (!token) return { roles: [], permissions: [] };
  try {
    const decoded = jwtDecode<JWTPayload>(token);
    return {
      roles: decoded.roles || [],
      permissions: decoded.permissions || [],
    };
  } catch {
    return { roles: [], permissions: [] };
  }
}

// React hook: usePermission(action)
export function usePermission(action: string): boolean {
  return useMemo(() => {
    const { roles, permissions } = getUserPermissions();
    // Explicit permission in JWT
    if (permissions.includes(action)) return true;
    // Role-based permission
    const allowedRoles = PERMISSION_MATRIX[action] || [];
    return roles.some(role => allowedRoles.includes(role));
  }, [action]);
}
