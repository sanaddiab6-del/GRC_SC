import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';

export default async function LocaleLayout({
  children,
  params: { locale }
}: {
  children: React.ReactNode;
  params: { locale: string };
}) {
  const messages = await getMessages();

  if (!['en', 'ar'].includes(locale)) {
    notFound();
  }

  return (
    <html lang={locale} dir={locale === 'ar' ? 'rtl' : 'ltr'}>
      <body>
        <NextIntlClientProvider messages={messages} locale={locale}>
          <nav className="bg-primary-600 text-white p-4 shadow-lg">
            <div className="container mx-auto flex justify-between items-center">
              <h1 className="text-xl font-bold">SICO GRC</h1>
              <div className="flex gap-6">
                <a href={`/${locale}/dashboard`} className="hover:underline">
                  Dashboard
                </a>
                <a href={`/${locale}/controls`} className="hover:underline">
                  Controls
                </a>
                <a href={`/${locale}`} className="px-3 py-1 bg-white text-primary-600 rounded">
                  {locale === 'ar' ? 'EN' : 'AR'}
                </a>
              </div>
            </div>
          </nav>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
