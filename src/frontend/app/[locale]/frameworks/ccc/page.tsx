'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useState, useEffect } from 'react';
import { apiClient } from '@/lib/api-client';

export default function CCCFrameworkPage() {
  const params = useParams();
  const locale = params.locale as string;
  const isArabic = locale === 'ar';
  const [stats, setStats] = useState({ total: 0, compliant: 0, inProgress: 0, nonCompliant: 0 });
  const [domains, setDomains] = useState<Record<string, any[]>>({});

  useEffect(() => {
    apiClient.get('/api/v1/controls/?framework=CCC&limit=500')
      .then((res) => {
        const controls: any[] = res.data?.controls ?? [];
        const grouped: Record<string, any[]> = {};
        let compliant = 0, inProgress = 0, nonCompliant = 0;
        controls.forEach((c: any) => {
          const d = c.domain || 'General';
          if (!grouped[d]) grouped[d] = [];
          grouped[d].push(c);
          if (c.status === 'compliant') compliant++;
          else if (c.status === 'in_progress') inProgress++;
          else nonCompliant++;
        });
        setDomains(grouped);
        setStats({ total: controls.length, compliant, inProgress, nonCompliant });
      })
      .catch(() => {});
  }, []);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      {/* Header */}
      <div className="mb-8">
        <Link href={`/${locale}/frameworks`} className="text-primary-600 hover:text-primary-700 mb-4 inline-block">
          ← {isArabic ? 'العودة إلى الأطر' : 'Back to Frameworks'}
        </Link>
        <div className="bg-gradient-to-r from-purple-600 to-purple-800 text-white rounded-xl p-8 shadow-lg">
          <div className="flex items-center gap-4 mb-4">
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
              {isArabic ? 'المجالات الرئيسية:' : 'Main Areas:'}
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
            <span className="text-xs font-semibold tracking-wide text-gray-500">DOC</span>
            <div>
              <p className="font-semibold">{isArabic ? 'دليل الضوابط الرسمي' : 'Official Controls Guide'}</p>
              <p className="text-sm text-gray-600">NCA Website</p>
            </div>
          </a>
          <a href="#" className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-purple-500 hover:bg-purple-50">
            <span className="text-xs font-semibold tracking-wide text-gray-500">RPT</span>
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
