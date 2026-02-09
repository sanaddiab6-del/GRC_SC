'use client';

import { useTranslations } from 'next-intl';
import useSWR from 'swr';
import apiClient from '@/lib/api-client';
import Link from 'next/link';
import { useParams } from 'next/navigation';

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export default function CCCFrameworkPage() {
  const params = useParams();
  const locale = params.locale as string;
  const isArabic = locale === 'ar';

  const { data: controls, isLoading } = useSWR(
    '/api/v1/controls?framework=CCC',
    fetcher
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const domains = controls?.items?.reduce((acc: any, control: any) => {
    const domain = control.domain;
    if (!acc[domain]) {
      acc[domain] = [];
    }
    acc[domain].push(control);
    return acc;
  }, {}) || {};

  const stats = {
    total: controls?.items?.length || 0,
    compliant: controls?.items?.filter((c: any) => c.status === 'compliant').length || 0,
    inProgress: controls?.items?.filter((c: any) => c.status === 'in_progress').length || 0,
    nonCompliant: controls?.items?.filter((c: any) => c.status === 'non_compliant').length || 0,
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      {/* Header */}
      <div className="mb-8">
        <Link href={`/${locale}/frameworks`} className="text-primary-600 hover:text-primary-700 mb-4 inline-block">
          ← {isArabic ? 'العودة إلى الأطر' : 'Back to Frameworks'}
        </Link>
        <div className="bg-gradient-to-r from-purple-600 to-purple-800 text-white rounded-xl p-8 shadow-lg">
          <div className="flex items-center gap-4 mb-4">
            <div className="text-6xl">☁️</div>
            <div>
              <h1 className="text-4xl font-bold">
                {isArabic ? 'ضوابط الأمن السيبراني السحابي' : 'Cloud Cybersecurity Controls (CCC)'}
              </h1>
              <p className="text-xl mt-2 opacity-90">
                {isArabic 
                  ? 'الهيئة الوطنية للأمن السيبراني - المملكة العربية السعودية'
                  : 'National Cybersecurity Authority - Saudi Arabia'}
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-4 gap-4 mt-6">
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <p className="text-sm opacity-80">{isArabic ? 'إجمالي الضوابط' : 'Total Controls'}</p>
              <p className="text-3xl font-bold">{stats.total}</p>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <p className="text-sm opacity-80">{isArabic ? 'متوافق' : 'Compliant'}</p>
              <p className="text-3xl font-bold">{stats.compliant}</p>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <p className="text-sm opacity-80">{isArabic ? 'قيد التنفيذ' : 'In Progress'}</p>
              <p className="text-3xl font-bold">{stats.inProgress}</p>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <p className="text-sm opacity-80">{isArabic ? 'غير متوافق' : 'Non-Compliant'}</p>
              <p className="text-3xl font-bold">{stats.nonCompliant}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Framework Overview */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-2xl font-bold mb-4">
          {isArabic ? 'نظرة عامة على الإطار' : 'Framework Overview'}
        </h2>
        <div className="prose max-w-none">
          <p className="text-gray-700 leading-relaxed">
            {isArabic
              ? 'ضوابط الأمن السيبراني السحابي (CCC) هي مجموعة من الضوابط المتخصصة للحوسبة السحابية الصادرة عن الهيئة الوطنية للأمن السيبراني. تركز هذه الضوابط على حماية البيانات والخدمات السحابية.'
              : 'The Cloud Cybersecurity Controls (CCC) are specialized controls for cloud computing issued by the National Cybersecurity Authority. These controls focus on protecting cloud data and services.'}
          </p>
          <div className="bg-purple-50 border-l-4 border-purple-500 p-4 mt-4">
            <p className="font-semibold text-purple-900">
              {isArabic ? '☁️ المجالات الرئيسية:' : '☁️ Main Areas:'}
            </p>
            <ul className="list-disc list-inside mt-2 text-purple-800">
              <li>{isArabic ? 'حوكمة السحابة' : 'Cloud Governance'}</li>
              <li>{isArabic ? 'أمن البيانات السحابية' : 'Cloud Data Security'}</li>
              <li>{isArabic ? 'إدارة الهوية والوصول' : 'Identity & Access Management'}</li>
              <li>{isArabic ? 'تشفير البيانات' : 'Data Encryption'}</li>
              <li>{isArabic ? 'الامتثال والتدقيق' : 'Compliance & Auditing'}</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Controls by Domain */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">
          {isArabic ? 'الضوابط حسب المجال' : 'Controls by Domain'}
        </h2>
        
        {Object.entries(domains).map(([domain, domainControls]: [string, any]) => (
          <div key={domain} className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="bg-purple-600 text-white px-6 py-4">
              <h3 className="text-xl font-bold">{domain}</h3>
              <p className="text-sm opacity-90">{domainControls.length} {isArabic ? 'ضوابط' : 'controls'}</p>
            </div>
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              {domainControls.map((control: any) => (
                <Link
                  key={control.control_id}
                  href={`/${locale}/controls/${control.control_id}`}
                  className="block border-2 border-gray-200 rounded-lg p-4 hover:border-purple-500 hover:shadow-md transition-all"
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-mono text-sm font-bold text-purple-600">
                      {control.control_id}
                    </span>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      control.status === 'compliant'
                        ? 'bg-green-100 text-green-800'
                        : control.status === 'in_progress'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {control.status.replace('_', ' ')}
                    </span>
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-2">
                    {isArabic ? control.title_ar : control.title_en}
                  </h4>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {isArabic ? control.description_ar : control.description_en}
                  </p>
                  <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                    <span>{isArabic ? 'الأولوية:' : 'Priority:'} {control.priority}</span>
                    <span>{isArabic ? 'النضج:' : 'Maturity:'} {control.maturity_level}/5</span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Resources */}
      <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4">
          {isArabic ? 'الموارد والوثائق' : 'Resources & Documents'}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a href="https://nca.gov.sa/pages/CCC.html" target="_blank" className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50">
            <span className="text-2xl">📄</span>
            <div>
              <p className="font-semibold">{isArabic ? 'دليل الضوابط الرسمي' : 'Official Controls Guide'}</p>
              <p className="text-sm text-gray-600">NCA Website</p>
            </div>
          </a>
          <a href="#" className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50">
            <span className="text-2xl">📊</span>
            <div>
              <p className="font-semibold">{isArabic ? 'تقرير الامتثال' : 'Compliance Report'}</p>
              <p className="text-sm text-gray-600">{isArabic ? 'تنزيل PDF' : 'Download PDF'}</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
}
