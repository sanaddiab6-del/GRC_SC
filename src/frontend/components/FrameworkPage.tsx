'use client';

import useSWR from 'swr';
import apiClient from '@/lib/api-client';
import Link from 'next/link';
import { useParams } from 'next/navigation';

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

interface FrameworkPageProps {
  frameworkCode: 'ECC' | 'CCC' | 'PDPL';
  frameworkName: {
    en: string;
    ar: string;
  };
  organizationName: {
    en: string;
    ar: string;
  };
  description: {
    en: string;
    ar: string;
  };
  gradientColors: string; // e.g., "from-blue-600 to-blue-800"
  emoji: string;
  highlightColor: string; // e.g., "blue" for bg-blue-50 and border-blue-500
}

export default function FrameworkPage({
  frameworkCode,
  frameworkName,
  organizationName,
  description,
  gradientColors,
  emoji,
  highlightColor,
}: FrameworkPageProps) {
  const params = useParams();
  const locale = params.locale as string;
  const isArabic = locale === 'ar';

  const { data: controls, isLoading } = useSWR(
    `/api/v1/controls?framework=${frameworkCode}`,
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
        <div className={`bg-gradient-to-r ${gradientColors} text-white rounded-xl p-8 shadow-lg`}>
          <div className="flex items-center gap-4 mb-4">
            <div className="text-6xl">{emoji}</div>
            <div>
              <h1 className="text-4xl font-bold">
                {isArabic ? frameworkName.ar : frameworkName.en}
              </h1>
              <p className="text-xl mt-2 opacity-90">
                {isArabic ? organizationName.ar : organizationName.en}
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
            {isArabic ? description.ar : description.en}
          </p>
          <div className={
            highlightColor === 'blue' ? 'bg-blue-50 border-l-4 border-blue-500 p-4 mt-4' :
            highlightColor === 'purple' ? 'bg-purple-50 border-l-4 border-purple-500 p-4 mt-4' :
            highlightColor === 'green' ? 'bg-green-50 border-l-4 border-green-500 p-4 mt-4' :
            'bg-gray-50 border-l-4 border-gray-500 p-4 mt-4'
          }>
            <p className={
              highlightColor === 'blue' ? 'font-semibold text-blue-900' :
              highlightColor === 'purple' ? 'font-semibold text-purple-900' :
              highlightColor === 'green' ? 'font-semibold text-green-900' :
              'font-semibold text-gray-900'
            }>
              {isArabic 
                ? `يحتوي ${frameworkName.ar} على ${stats.total} ضابط منظم عبر مجالات متعددة.`
                : `${frameworkName.en} contains ${stats.total} controls organized across multiple domains.`}
            </p>
          </div>
        </div>
      </div>

      {/* Controls by Domain */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">
          {isArabic ? 'الضوابط حسب المجال' : 'Controls by Domain'}
        </h2>
        
        {Object.entries(domains).map(([domain, domainControls]: [string, any]) => (
          <div key={domain} className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-xl font-semibold mb-4 flex items-center justify-between">
              <span>{domain}</span>
              <span className="text-sm text-gray-500 font-normal">
                {domainControls.length} {isArabic ? 'ضابط' : 'controls'}
              </span>
            </h3>
            
            <div className="space-y-3">
              {domainControls.map((control: any) => (
                <Link
                  key={control.control_id}
                  href={`/${locale}/controls/${control.control_id}`}
                  className="block border border-gray-200 rounded-lg p-4 hover:border-primary-500 hover:shadow-md transition-all"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-mono text-sm font-semibold text-primary-600">
                          {control.control_id}
                        </span>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          control.status === 'compliant' ? 'bg-green-100 text-green-800' :
                          control.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {control.status === 'compliant' ? (isArabic ? 'متوافق' : 'Compliant') :
                           control.status === 'in_progress' ? (isArabic ? 'قيد التنفيذ' : 'In Progress') :
                           (isArabic ? 'غير متوافق' : 'Non-Compliant')}
                        </span>
                      </div>
                      <h4 className="font-semibold text-gray-900">
                        {isArabic ? control.title_ar : control.title_en}
                      </h4>
                      <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                        {isArabic ? control.description_ar : control.description_en}
                      </p>
                    </div>
                    <div className="text-gray-400 ml-4">→</div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
