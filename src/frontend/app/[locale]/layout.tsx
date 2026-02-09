import { NextIntlClientProvider } from 'next-intl';
import { getMessages, getTranslations } from 'next-intl/server';
import { notFound } from 'next/navigation';
import Link from 'next/link';

export default async function LocaleLayout({
  children,
  params: { locale }
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  const messages = await getMessages();
  const t = await getTranslations('nav');

  if (!['en', 'ar'].includes(locale)) {
    notFound();
  }

  const navItems = [
    { href: '/dashboard', icon: '📊', label: t('dashboard') },
    { href: '/frameworks', icon: '🛡️', label: t('frameworks') },
    { href: '/controls', icon: '📋', label: t('controls') },
    { href: '/search', icon: '🔍', label: t('search') },
    { href: '/evidence', icon: '📎', label: t('evidence') },
    { href: '/reports', icon: '📈', label: t('reports') },
  ];

  return (
    <html lang={locale} dir={locale === 'ar' ? 'rtl' : 'ltr'}>
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=Inter:wght@400;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="bg-gray-50" style={{ fontFamily: locale === 'ar' ? "'Cairo', sans-serif" : "'Inter', sans-serif" }}>
        <NextIntlClientProvider messages={messages} locale={locale}>
          <nav className="bg-primary-600 text-white shadow-lg">
            <div className="container mx-auto px-4 py-3">
              <div className="flex justify-between items-center">
                <Link href={`/${locale}`} className="text-2xl font-bold hover:text-gray-200">
                  🛡️ {locale === 'ar' ? 'سيكو للحوكمة' : 'SICO GRC'}
                </Link>
                <div className="flex gap-6 items-center">
                  {navItems.map((item) => (
                    <Link 
                      key={item.href}
                      href={`/${locale}${item.href}`} 
                      className="hover:text-gray-200 font-medium transition-colors whitespace-nowrap"
                    >
                      {item.icon} {item.label}
                    </Link>
                  ))}
                  <Link 
                    href={`/${locale === 'ar' ? 'en' : 'ar'}`} 
                    className="px-4 py-2 bg-white text-primary-600 rounded-lg hover:bg-gray-100 font-semibold transition-colors"
                  >
                    {locale === 'ar' ? 'English' : 'العربية'}
                  </Link>
                </div>
              </div>
            </div>
          </nav>
          <main className="min-h-screen">
            {children}
          </main>
          <footer className="bg-gray-800 text-white py-6 mt-12">
            <div className="container mx-auto px-4 text-center">
              <p className="text-sm">
                {locale === 'ar' 
                  ? 'منصة سيكو للحوكمة - نظام إدارة الامتثال السعودي' 
                  : 'SICO GRC Platform - Saudi Compliance Management System'}
              </p>
              <p className="text-xs text-gray-400 mt-2">
                {locale === 'ar' 
                  ? 'الضوابط الأساسية • ضوابط الحوسبة السحابية • نظام حماية البيانات' 
                  : 'ECC • CCC • PDPL Frameworks'}
              </p>
            </div>
          </footer>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
