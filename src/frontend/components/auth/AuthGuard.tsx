'use client';

/**
 * AuthGuard – Production-ready authentication wrapper
 *
 * Features:
 * - Hydration-safe for Next.js SSR
 * - Token validation with server check
 * - Role-based access control (RBAC)
 * - Automatic token refresh
 * - Graceful error handling
 * - Proper loading states
 */

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { 
  isAuthenticated, 
  validateSession, 
  getStoredUser, 
  hasRole,
  hasAnyRole,
  redirectToLogin,
  type User 
} from '@/lib/authService';

// ── Types ─────────────────────────────────────────────────────────────────────

interface AuthGuardProps {
  children: React.ReactNode;
  /** Required roles for access */
  requiredRoles?: string[];
  /** If true, user must have ALL specified roles (AND logic) */
  requireAllRoles?: boolean;
  /** Custom fallback component for unauthorized access */
  fallback?: React.ReactNode;
  /** Skip server validation (use cached token only) */
  skipServerValidation?: boolean;
}

type AuthState = 'loading' | 'authenticated' | 'unauthenticated' | 'unauthorized';

// ── Components ────────────────────────────────────────────────────────────────

/**
 * Loading spinner component
 */
const LoadingSpinner = ({ message }: { message?: string }) => (
  <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100">
    <div className="flex flex-col items-center gap-4">
      <div className="relative">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
        <div className="absolute inset-0 w-12 h-12 border-4 border-blue-200 rounded-full opacity-25" />
      </div>
      <div className="text-center">
        <p className="text-sm text-slate-600 font-medium">
          {message || 'Verifying authentication...'}
        </p>
        <p className="text-xs text-slate-400 mt-1">
          Please wait a moment
        </p>
      </div>
    </div>
  </div>
);

/**
 * Unauthorized access component
 */
const UnauthorizedAccess = ({ locale, requiredRoles }: { 
  locale: string; 
  requiredRoles?: string[];
}) => (
  <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 via-orange-50 to-red-50">
    <div className="max-w-md w-full p-8">
      <div className="bg-white rounded-2xl shadow-xl ring-1 ring-red-200 p-8 text-center">
        <div className="w-16 h-16 mx-auto mb-6 bg-red-100 rounded-full flex items-center justify-center">
          <svg className="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m0 0v2m0-2h2m-2 0H9m11-6V9a3 3 0 00-3-3H7a3 3 0 00-3 3v6c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2z" />
          </svg>
        </div>
        
        <h1 className="text-2xl font-bold text-slate-900 mb-3">
          {locale === 'ar' ? 'غير مخول بالوصول' : 'Access Denied'}
        </h1>
        
        <p className="text-slate-600 mb-6">
          {locale === 'ar' 
            ? 'ليس لديك الصلاحيات اللازمة للوصول إلى هذه الصفحة'
            : 'You don\'t have the required permissions to access this page'
          }
        </p>
        
        {requiredRoles && requiredRoles.length > 0 && (
          <div className="bg-slate-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-slate-600 mb-2">
              {locale === 'ar' ? 'الأدوار المطلوبة:' : 'Required roles:'}
            </p>
            <div className="flex flex-wrap gap-2 justify-center">
              {requiredRoles.map((role) => (
                <span key={role} className="px-2 py-1 bg-slate-200 text-slate-700 text-xs rounded-full">
                  {role}
                </span>
              ))}
            </div>
          </div>
        )}
        
        <div className="flex gap-3">
          <button
            onClick={() => window.history.back()}
            className="flex-1 px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition text-sm font-medium"
          >
            {locale === 'ar' ? 'رجوع' : 'Go Back'}
          </button>
          
          <a
            href={`/${locale}/dashboard`}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm font-medium text-center"
          >
            {locale === 'ar' ? 'الرئيسية' : 'Dashboard'}
          </a>
        </div>
      </div>
    </div>
  </div>
);

// ── Main AuthGuard Component ──────────────────────────────────────────────────

export function AuthGuard({ 
  children, 
  requiredRoles = [], 
  requireAllRoles = false,
  fallback,
  skipServerValidation = false 
}: AuthGuardProps) {
  const router = useRouter();
  const params = useParams();
  const locale = (params?.locale as string) || 'en';
  
  const [authState, setAuthState] = useState<AuthState>('loading');
  const [user, setUser] = useState<User | null>(null);

  // ── Authorization Check ───────────────────────────────────────────────────

  const checkAuthorization = (user: User | null): boolean => {
    if (!user || requiredRoles.length === 0) {
      return true; // No role requirements
    }

    if (requireAllRoles) {
      // User must have ALL specified roles
      return requiredRoles.every(role => hasRole(user, role));
    } else {
      // User must have ANY of the specified roles
      return hasAnyRole(user, requiredRoles);
    }
  };

  // ── Authentication Effect ─────────────────────────────────────────────────

  useEffect(() => {
    let isMounted = true;

    const checkAuth = async () => {
      try {
        // Phase 1: Check if user has token
        if (!isAuthenticated()) {
          if (isMounted) {
            setAuthState('unauthenticated');
            redirectToLogin(locale);
          }
          return;
        }

        // Phase 2: Get cached user data
        const cachedUser = getStoredUser();
        if (cachedUser) {
          setUser(cachedUser);
          
          // Check authorization with cached data
          if (!checkAuthorization(cachedUser)) {
            if (isMounted) {
              setAuthState('unauthorized');
            }
            return;
          }
          
          // If skipping server validation, we're done
          if (skipServerValidation) {
            if (isMounted) {
              setAuthState('authenticated');
            }
            return;
          }
        }

        // Phase 3: Validate with server (unless skipped)
        if (!skipServerValidation) {
          const validation = await validateSession();
          
          if (!isMounted) return;

          if (!validation.valid) {
            setAuthState('unauthenticated');
            redirectToLogin(locale);
            return;
          }

          if (validation.user) {
            setUser(validation.user);
            
            // Re-check authorization with fresh data
            if (!checkAuthorization(validation.user)) {
              setAuthState('unauthorized');
              return;
            }
          }
        }

        // All checks passed
        if (isMounted) {
          setAuthState('authenticated');
        }

      } catch (error) {
        console.error('AuthGuard: Authentication check failed:', error);
        
        if (isMounted) {
          // On error, check if we have cached user data to fall back on
          const cachedUser = getStoredUser();
          if (cachedUser && checkAuthorization(cachedUser)) {
            setAuthState('authenticated');
            setUser(cachedUser);
          } else {
            setAuthState('unauthenticated');
            redirectToLogin(locale);
          }
        }
      }
    };

    checkAuth();

    // Cleanup function
    return () => {
      isMounted = false;
    };
  // }, [locale, requiredRoles, requireAllRoles, skipServerValidation, router]);
  }, [locale, requireAllRoles, skipServerValidation]);

  // ── Render Logic ──────────────────────────────────────────────────────────

  switch (authState) {
    case 'loading':
      return <LoadingSpinner message="Checking authentication..." />;
      
    case 'unauthenticated':
      return <LoadingSpinner message="Redirecting to login..." />;
      
    case 'unauthorized':
      return fallback || (
        <UnauthorizedAccess 
          locale={locale} 
          requiredRoles={requiredRoles} 
        />
      );
      
    case 'authenticated':
      return <>{children}</>;
      
    default:
      return <LoadingSpinner message="Loading..." />;
  }
}

// ── Specialized AuthGuard Variants ────────────────────────────────────────────

/**
 * Admin-only AuthGuard
 */
export function AdminGuard({ children, ...props }: Omit<AuthGuardProps, 'requiredRoles'>) {
  return (
    <AuthGuard requiredRoles={['Admin', 'super_admin']} {...props}>
      {children}
    </AuthGuard>
  );
}

/**
 * Role-based AuthGuard with multiple roles (OR logic)
 */
export function RoleGuard({ 
  roles, 
  children, 
  ...props 
}: Omit<AuthGuardProps, 'requiredRoles'> & { roles: string[] }) {
  return (
    <AuthGuard requiredRoles={roles} requireAllRoles={false} {...props}>
      {children}
    </AuthGuard>
  );
}

/**
 * Multi-role AuthGuard requiring ALL roles (AND logic)
 */
export function MultiRoleGuard({ 
  roles, 
  children, 
  ...props 
}: Omit<AuthGuardProps, 'requiredRoles' | 'requireAllRoles'> & { roles: string[] }) {
  return (
    <AuthGuard requiredRoles={roles} requireAllRoles={true} {...props}>
      {children}
    </AuthGuard>
  );
}

// Export default AuthGuard
export default AuthGuard;
