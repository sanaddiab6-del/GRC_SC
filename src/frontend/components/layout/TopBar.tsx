/**
 * Professional Top Bar
 * Search, notifications, quick actions, and user menu
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { logout, fetchCurrentUser } from '@/lib/auth';

interface TopBarProps {
  locale: 'ar' | 'en';
  sidebarCollapsed?: boolean;
}

export function TopBar({ locale, sidebarCollapsed = false }: TopBarProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const [currentUser, setCurrentUser] = useState<{ email: string; full_name_en?: string | null } | null>(null);
  const t = useTranslations('shell');
  const router = useRouter();

  useEffect(() => {
    fetchCurrentUser().then((u) => {
      if (u) setCurrentUser(u);
    });
  }, []);

  const handleLogout = async () => {
    await logout();
    router.push(`/${locale}/login`);
  };

  const displayName = currentUser?.full_name_en || currentUser?.email || (locale === 'ar' ? 'المستخدم' : 'User');

  const notifications = [
    {
      id: 1,
      type: 'alert',
      title: locale === 'ar' ? 'حادثة أمنية جديدة' : 'New Security Incident',
      message: locale === 'ar' ? 'محاولة دخول غير مصرح بها' : 'Unauthorized access attempt detected',
      time: '5m ago',
      unread: true,
    },
    {
      id: 2,
      type: 'success',
      title: locale === 'ar' ? 'اكتمل التدقيق' : 'Audit Completed',
      message: locale === 'ar' ? 'تدقيق الضوابط الأساسية Q1' : 'Q1 ECC Controls Audit',
      time: '1h ago',
      unread: true,
    },
    {
      id: 3,
      type: 'warning',
      title: locale === 'ar' ? 'مهمة قادمة' : 'Task Due Soon',
      message: locale === 'ar' ? 'مراجعة المخاطر - تنتهي غداً' : 'Risk Review - Due Tomorrow',
      time: '3h ago',
      unread: false,
    },
  ];

  const unreadCount = notifications.filter(n => n.unread).length;

  return (
    <header 
      className={`
        fixed top-0 ${locale === 'ar' ? 'right-0' : 'left-0'}
        ${sidebarCollapsed ? 'w-[calc(100%-4rem)]' : 'w-[calc(100%-16rem)]'}
        bg-card/95 backdrop-blur border-b border-border z-40 transition-all duration-300
        ${locale === 'ar' ? 'mr-64' : 'ml-64'}
      `}
      style={{ 
        marginLeft: locale === 'ar' ? '0' : (sidebarCollapsed ? '4rem' : '16rem'),
        marginRight: locale === 'ar' ? (sidebarCollapsed ? '4rem' : '16rem') : '0'
      }}
    >
      <div className="flex items-center justify-between gap-6 px-6 py-3">
        <div className="flex items-center gap-3 min-w-[220px]">
          <div className="text-sm font-semibold text-foreground">{t('tenant')}</div>
          <Badge variant="outline" className="text-xs">
            {t('environment')}: {t('prod')}
          </Badge>
        </div>

        <div className="flex-1 max-w-2xl">
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={t('searchPlaceholder')}
            dir={locale === 'ar' ? 'rtl' : 'ltr'}
          />
        </div>

        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm">
            {locale === 'ar' ? 'NEW' : 'NEW'}
          </Button>

          <div className="relative">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowNotifications(!showNotifications)}
            >
              {locale === 'ar' ? 'تنبيهات' : 'Notifications'}
              {unreadCount > 0 && (
                <span className="ml-2 inline-flex h-5 w-5 items-center justify-center rounded-full bg-foreground text-[10px] font-semibold text-background">
                  {unreadCount}
                </span>
              )}
            </Button>

            {showNotifications && (
              <div className="absolute top-full right-0 mt-2 w-96 rounded-2xl border border-border bg-card shadow-sm">
                <div className="p-4 border-b border-border flex justify-between items-center">
                  <h3 className="text-sm font-semibold">
                    {locale === 'ar' ? 'الإشعارات' : 'Notifications'}
                  </h3>
                  <button className="text-xs text-muted-foreground hover:text-foreground">
                    {locale === 'ar' ? 'تمييز الكل كمقروء' : 'Mark all read'}
                  </button>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  {notifications.map((notif) => (
                    <div
                      key={notif.id}
                      className={`p-4 border-b border-border hover:bg-muted/40 cursor-pointer transition-colors ${
                        notif.unread ? 'bg-muted/30' : ''
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <span
                          className={`mt-1.5 h-2 w-2 rounded-full ${
                            notif.type === 'alert'
                              ? 'bg-destructive'
                              : notif.type === 'success'
                              ? 'bg-success'
                              : 'bg-warning'
                          }`}
                        />
                        <div className="flex-1">
                          <p className="font-medium text-sm">{notif.title}</p>
                          <p className="text-xs text-muted-foreground mt-1">{notif.message}</p>
                          <p className="text-xs text-muted-foreground mt-2">{notif.time}</p>
                        </div>
                        {notif.unread && (
                          <span className="w-2 h-2 bg-info rounded-full mt-2"></span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
                <div className="p-3 text-center border-t border-border">
                  <Link href={`/${locale}/notifications`} className="text-xs text-muted-foreground hover:text-foreground font-semibold">
                    {locale === 'ar' ? 'عرض جميع الإشعارات' : 'View All Notifications'}
                  </Link>
                </div>
              </div>
            )}
          </div>

          <Button variant="outline" size="sm" asChild>
            <Link href={`/${locale === 'ar' ? 'en' : 'ar'}`}>
              {locale === 'ar' ? 'EN' : 'AR'}
            </Link>
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                {displayName}
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>{t('userMenu')}</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="cursor-pointer"
                onClick={() => {
                  console.log('[TopBar] Profile clicked → navigating to', `/${locale}/profile`);
                  router.push(`/${locale}/profile`);
                }}
              >
                {locale === 'ar' ? 'الملف الشخصي' : 'Profile'}
              </DropdownMenuItem>
              <DropdownMenuItem
                className="cursor-pointer"
                onClick={() => {
                  console.log('[TopBar] Executive Report clicked → navigating to', `/${locale}/executive-report`);
                  router.push(`/${locale}/executive-report`);
                }}
              >
                {locale === 'ar' ? 'التقرير التنفيذي' : 'Executive Report'}
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                className="text-red-600 focus:text-red-600 cursor-pointer"
                onClick={handleLogout}
              >
                {locale === 'ar' ? 'تسجيل الخروج' : 'Log out'}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
