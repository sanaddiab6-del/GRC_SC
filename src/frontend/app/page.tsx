import { useTranslations } from 'next-intl';
import Link from 'next/link';

export default function HomePage() {
  const t = useTranslations('home');

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center space-y-6">
        <h1 className="text-4xl font-bold">
          {t('title')}
        </h1>
        <p className="text-xl text-gray-600">
          {t('subtitle')}
        </p>
        <div className="flex gap-4 justify-center mt-8">
          <Link 
            href="/controls" 
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            {t('viewControls')}
          </Link>
          <Link 
            href="/reports" 
            className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
          >
            {t('viewReports')}
          </Link>
        </div>
      </div>
    </main>
  );
}
