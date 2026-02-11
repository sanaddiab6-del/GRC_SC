import { NextIntlClientProvider } from 'next-intl';
import { getMessages } from 'next-intl/server';
import { notFound } from 'next/navigation';
import { Sidebar } from '@/components/layout/Sidebar';
import { TopBar } from '@/components/layout/TopBar';

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

  const localeTyped = locale as 'ar' | 'en';

  return (
    <div
      lang={locale}
      dir={locale === 'ar' ? 'rtl' : 'ltr'}
      className="bg-[#f7f8fa] min-h-screen"
      style={{ fontFamily: locale === 'ar' ? "'Cairo', sans-serif" : "'Plus Jakarta Sans', sans-serif" }}
    >
      <NextIntlClientProvider messages={messages} locale={locale}>
        {/* Modern Sidebar Navigation */}
        <Sidebar locale={localeTyped} />
        
        {/* Top Bar with Search and Actions */}
        <TopBar locale={localeTyped} />
        
        {/* Main Content Area */}
        <main 
          className={`
            min-h-screen pt-20 transition-all duration-300
            ${locale === 'ar' ? 'mr-64' : 'ml-64'}
          `}
        >
          <div className="p-8">
            {children}
          </div>
        </main>
      </NextIntlClientProvider>
    </div>
  );
}
