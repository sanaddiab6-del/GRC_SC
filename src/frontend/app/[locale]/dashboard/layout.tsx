'use client';

/**
 * Dashboard layout – every route inside /[locale]/dashboard/* is protected.
 * Unauthenticated users are redirected to /[locale]/login.
 */

import { AuthGuard } from '@/components/auth/AuthGuard';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <AuthGuard>{children}</AuthGuard>;
}
