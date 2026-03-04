'use client';

/**
 * AppShell – renders the Sidebar + TopBar only for non-auth routes.
 *
 * Auth routes (/login, /register) get a clean full-screen layout.
 * All other routes get the full dashboard shell.
 */

import { usePathname } from 'next/navigation';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';

const AUTH_ROUTE_SEGMENTS = ['/login', '/register'];

interface AppShellProps {
  children: React.ReactNode;
  locale: 'ar' | 'en';
}

export function AppShell({ children, locale }: AppShellProps) {
  const pathname = usePathname();

  const isAuthRoute = AUTH_ROUTE_SEGMENTS.some((seg) =>
    pathname.endsWith(seg)
  );

  if (isAuthRoute) {
    // Clean layout – no sidebar, no topbar
    return <>{children}</>;
  }

  return (
    <>
      <Sidebar locale={locale} />
      <TopBar locale={locale} />
      <main
        className={`
          min-h-screen pt-20 transition-all duration-300
          ${locale === 'ar' ? 'mr-64' : 'ml-64'}
        `}
      >
        <div className="p-8">{children}</div>
      </main>
    </>
  );
}
