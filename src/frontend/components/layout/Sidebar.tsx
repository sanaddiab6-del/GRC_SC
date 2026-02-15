/**
 * Professional Sidebar Navigation
 * Collapsible sidebar with icon support, active states, and user profile
 */

'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/button';

interface SidebarProps {
  locale: 'ar' | 'en';
}

interface NavItem {
  href: string;
  label: string;
  badge?: number;
  submenu?: NavItem[];
}

export function Sidebar({ locale }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const pathname = usePathname();
  const t = useTranslations('nav');

  const navItems: NavItem[] = [
    {
      href: '/dashboard',
      label: t('dashboard'),
    },
    {
      href: '/frameworks',
      label: t('frameworks'),
      submenu: [
        { href: '/frameworks/ecc', label: t('ecc') },
        { href: '/frameworks/ccc', label: t('ccc') },
        { href: '/frameworks/pdpl', label: t('pdpl') },
      ],
    },
    {
      href: '/control-library',
      label: t('unifiedLibrary'),
    },
    {
      href: '/risk-assessment',
      label: t('assessments'),
    },
    {
      href: '/controls',
      label: t('controls'),
    },
    {
      href: '/evidence',
      label: t('evidence'),
    },
    {
      href: '/findings',
      label: t('findings'),
    },
    {
      href: '/risks',
      label: t('risk'),
    },
    {
      href: '/reports',
      label: t('reports'),
    },
    {
      href: '/soc-grc-bridge',
      label: t('socBridge'),
    },
    {
      href: '/admin',
      label: t('admin'),
    },
  ];

  const isActive = (href: string) => pathname?.includes(href);

  return (
    <aside 
      className={`
        fixed ${locale === 'ar' ? 'right-0' : 'left-0'} top-0 h-screen
        bg-card text-foreground transition-all duration-300 z-50
        ${locale === 'ar' ? 'border-l' : 'border-r'} border-border
        ${collapsed ? 'w-16' : 'w-64'}
      `}
    >
      {/* Logo & Collapse Toggle */}
      <div className="flex items-center justify-between p-5 border-b border-border">
        {!collapsed && (
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-foreground rounded-xl flex items-center justify-center text-background text-sm font-semibold">
              SG
            </div>
            <div>
              <h2 className="font-semibold text-lg">
                {locale === 'ar' ? 'سيكو' : 'SICO'}
              </h2>
              <p className="text-xs text-muted-foreground">
                {locale === 'ar' ? 'منصة الحوكمة' : 'GRC Platform'}
              </p>
            </div>
          </div>
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setCollapsed(!collapsed)}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          <span className="text-sm text-muted-foreground">{collapsed ? '>' : (locale === 'ar' ? '>' : '<')}</span>
        </Button>
      </div>

      {/* Navigation Items */}
      <nav className="p-3 space-y-1 overflow-y-auto h-[calc(100vh-176px)]">
        {navItems.map((item) => (
          <div key={item.href}>
            <Link
              href={`/${locale}${item.href}`}
              className={`
                flex items-center gap-3 px-3 py-2 rounded-lg
                transition-all duration-200 group relative text-sm
                ${isActive(item.href)
                  ? 'bg-muted text-foreground'
                  : 'hover:bg-muted/60 text-muted-foreground hover:text-foreground'
                }
              `}
            >
              {!collapsed && (
                <>
                  <span className="flex-1 font-medium">{item.label}</span>
                  {item.badge && (
                    <span className="px-2 py-0.5 bg-foreground text-background text-xs rounded-full font-semibold">
                      {item.badge}
                    </span>
                  )}
                </>
              )}
              {collapsed && item.badge && (
                <span className="absolute top-2 right-2 w-2 h-2 bg-foreground rounded-full"></span>
              )}
            </Link>
            
            {/* Submenu */}
            {item.submenu && !collapsed && isActive(item.href) && (
              <div className="ml-6 mt-2 space-y-1">
                {item.submenu.map((subitem) => (
                  <Link
                    key={subitem.href}
                    href={`/${locale}${subitem.href}`}
                    className="flex items-center gap-2 px-3 py-2 text-sm rounded-lg hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
                  >
                    <span>{subitem.label}</span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>

      {/* User Profile */}
      <div className={`absolute bottom-0 ${locale === 'ar' ? 'right-0' : 'left-0'} w-full p-4 border-t border-border bg-card`}>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-foreground rounded-full flex items-center justify-center font-semibold text-background">
            A
          </div>
          {!collapsed && (
            <div className="flex-1">
              <p className="font-medium text-sm text-foreground">
                {locale === 'ar' ? 'مدير الامتثال' : 'Admin User'}
              </p>
              <p className="text-xs text-muted-foreground">
                {locale === 'ar' ? 'متصل' : 'Online'}
              </p>
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
