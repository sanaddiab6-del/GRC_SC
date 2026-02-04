import { useTranslations } from 'next-intl';
import Link from 'next/link';

export default function HomePage({
  params: { locale }
}: {
  params: { locale: string };
}) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center space-y-6">
        <h1 className="text-4xl font-bold">
          {locale === 'ar' ? 'منصة سيكو للحوكمة' : 'SICO GRC Platform'}
        </h1>
        <p className="text-xl text-gray-600">
          {locale === 'ar' 
            ? 'محرك الامتثال التنظيمي السعودي - الضوابط الأساسية، ضوابط الحوسبة السحابية، نظام حماية البيانات'
            : 'Saudi Regulatory Compliance Engine - ECC, CCC, PDPL'}
        </p>
        <div className="flex gap-4 justify-center mt-8">
          <Link 
            href={`/${locale}/controls`}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            {locale === 'ar' ? 'عرض الضوابط' : 'View Controls'}
          </Link>
          <Link 
            href={`/${locale}/dashboard`}
            className="px-6 py-3 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300"
          >
            {locale === 'ar' ? 'لوحة القيادة' : 'Dashboard'}
          </Link>
        </div>
      </div>
    </main>
  );
}
