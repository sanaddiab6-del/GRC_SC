import '../globals.css';
import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { AppShell } from '@/components/layout/AppShell';

export default async function LocaleLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  const messages = await getMessages();

  if (!['en', 'ar'].includes(locale)) {
    notFound();
  }

  const localeTyped = locale as 'ar' | 'en';

  return (
    <html lang={locale} dir={locale === 'ar' ? 'rtl' : 'ltr'}>
      <body 
        className="min-h-screen bg-[#f7f8fa] text-foreground antialiased"
        style={{ fontFamily: locale === 'ar' ? "'Cairo', sans-serif" : "'Plus Jakarta Sans', sans-serif" }}
      >
        <NextIntlClientProvider messages={messages} locale={locale}>
          <AppShell locale={localeTyped}>
            {children}
          </AppShell>
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
