'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { useParams } from 'next/navigation';

export default function FrameworksPage() {
  const params = useParams();
  const locale = params.locale as string;
  const isArabic = locale === 'ar';

  const frameworks = [
    {
      id: 'ecc',
      title: isArabic ? 'الضوابط الأساسية للأمن السيبراني' : 'Essential Cybersecurity Controls',
      titleShort: 'ECC',
      authority: isArabic ? 'الهيئة الوطنية للأمن السيبراني' : 'National Cybersecurity Authority',
      description: isArabic 
        ? 'مجموعة الضوابط الأمنية الإلزامية لحماية البنية التحتية الحيوية والأصول الرقمية'
        : 'Mandatory security controls to protect critical infrastructure and digital assets',
      color: 'blue',
      icon: '🛡️',
      controls: '50+',
    },
    {
      id: 'ccc',
      title: isArabic ? 'ضوابط الأمن السيبراني السحابي' : 'Cloud Cybersecurity Controls',
      titleShort: 'CCC',
      authority: isArabic ? 'الهيئة الوطنية للأمن السيبراني' : 'National Cybersecurity Authority',
      description: isArabic
        ? 'ضوابط متخصصة لحماية البيانات والخدمات السحابية'
        : 'Specialized controls for cloud data and services protection',
      color: 'purple',
      icon: '☁️',
      controls: '40+',
    },
    {
      id: 'pdpl',
      title: isArabic ? 'نظام حماية البيانات الشخصية' : 'Personal Data Protection Law',
      titleShort: 'PDPL',
      authority: isArabic ? 'الهيئة السعودية للبيانات والذكاء الاصطناعي' : 'Saudi Data & AI Authority',
      description: isArabic
        ? 'الإطار التنظيمي لحماية خصوصية الأفراد وتنظيم معالجة البيانات الشخصية'
        : 'Regulatory framework for protecting privacy and regulating personal data processing',
      color: 'green',
      icon: '🔒',
      controls: '30+',
    },
  ];

  const colorClasses: Record<string, any> = {
    blue: {
      border: 'border-blue-500',
      bg: 'bg-blue-50',
      text: 'text-blue-600',
      hover: 'hover:border-blue-600 hover:shadow-blue-200',
    },
    purple: {
      border: 'border-purple-500',
      bg: 'bg-purple-50',
      text: 'text-purple-600',
      hover: 'hover:border-purple-600 hover:shadow-purple-200',
    },
    green: {
      border: 'border-green-500',
      bg: 'bg-green-50',
      text: 'text-green-600',
      hover: 'hover:border-green-600 hover:shadow-green-200',
    },
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4">
            {isArabic ? 'الأطر التنظيمية' : 'Regulatory Frameworks'}
          </h1>
          <p className="text-xl text-gray-600">
            {isArabic
              ? 'استكشف الأطر التنظيمية السعودية للأمن السيبراني وحماية البيانات'
              : 'Explore Saudi regulatory frameworks for cybersecurity and data protection'}
          </p>
        </div>

        {/* Framework Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {frameworks.map((framework) => (
            <Link
              key={framework.id}
              href={`/${locale}/frameworks/${framework.id}`}
              className={`block bg-white rounded-xl shadow-lg overflow-hidden border-l-8 ${colorClasses[framework.color].border} ${colorClasses[framework.color].hover} hover:shadow-xl transition-all`}
            >
              <div className={`${colorClasses[framework.color].bg} p-6`}>
                <div className="flex items-center gap-3 mb-3">
                  <span className="text-5xl">{framework.icon}</span>
                  <div>
                    <h2 className={`text-3xl font-bold ${colorClasses[framework.color].text}`}>
                      {framework.titleShort}
                    </h2>
                  </div>
                </div>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-bold mb-3">{framework.title}</h3>
                <p className="text-sm text-gray-600 mb-4">{framework.authority}</p>
                <p className="text-gray-700 mb-4">{framework.description}</p>
                <div className="flex justify-between items-center pt-4 border-t">
                  <div>
                    <p className="text-sm text-gray-500">{isArabic ? 'الضوابط' : 'Controls'}</p>
                    <p className={`text-2xl font-bold ${colorClasses[framework.color].text}`}>
                      {framework.controls}
                    </p>
                  </div>
                  <div className={`px-4 py-2 ${colorClasses[framework.color].bg} ${colorClasses[framework.color].text} rounded-lg font-semibold`}>
                    {isArabic ? 'عرض →' : 'View →'}
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* Compliance Overview */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold mb-6">
            {isArabic ? 'نظرة عامة على الامتثال' : 'Compliance Overview'}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 bg-blue-50 rounded-lg">
              <p className="text-5xl font-bold text-blue-600 mb-2">100%</p>
              <p className="text-gray-700">{isArabic ? 'ECC متوافق' : 'ECC Compliant'}</p>
            </div>
            <div className="text-center p-6 bg-purple-50 rounded-lg">
              <p className="text-5xl font-bold text-purple-600 mb-2">100%</p>
              <p className="text-gray-700">{isArabic ? 'CCC متوافق' : 'CCC Compliant'}</p>
            </div>
            <div className="text-center p-6 bg-red-50 rounded-lg">
              <p className="text-5xl font-bold text-red-600 mb-2">0%</p>
              <p className="text-gray-700">{isArabic ? 'PDPL متوافق' : 'PDPL Compliant'}</p>
            </div>
          </div>
        </div>

        {/* Quick Links */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold mb-6">
            {isArabic ? 'روابط سريعة' : 'Quick Links'}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <a href="https://nca.gov.sa" target="_blank" className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50">
              <span className="text-3xl">🌐</span>
              <div>
                <p className="font-semibold">{isArabic ? 'الهيئة الوطنية للأمن السيبراني' : 'NCA Website'}</p>
                <p className="text-sm text-gray-600">nca.gov.sa</p>
              </div>
            </a>
            <a href="https://sdaia.gov.sa" target="_blank" className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50">
              <span className="text-3xl">🌐</span>
              <div>
                <p className="font-semibold">{isArabic ? 'الهيئة السعودية للبيانات والذكاء الاصطناعي' : 'SDAIA Website'}</p>
                <p className="text-sm text-gray-600">sdaia.gov.sa</p>
              </div>
            </a>
            <Link href={`/${locale}/controls`} className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50">
              <span className="text-3xl">📋</span>
              <div>
                <p className="font-semibold">{isArabic ? 'جميع الضوابط' : 'All Controls'}</p>
                <p className="text-sm text-gray-600">{isArabic ? 'عرض جميع ضوابط الامتثال' : 'View all compliance controls'}</p>
              </div>
            </Link>
            <Link href={`/${locale}/reports`} className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50">
              <span className="text-3xl">📊</span>
              <div>
                <p className="font-semibold">{isArabic ? 'تقارير الامتثال' : 'Compliance Reports'}</p>
                <p className="text-sm text-gray-600">{isArabic ? 'إنشاء وتنزيل التقارير' : 'Generate and download reports'}</p>
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
