'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import axios from 'axios';

interface Risk {
  id: number;
  risk_id: string;
  risk_type: string;
  title_en: string;
  title_ar?: string;
  likelihood_inherent: number;
  impact_inherent: number;
  risk_score_inherent?: number;
  risk_level_inherent?: string;
  status: string;
}

export default function RiskManagementPage() {
  const params = useParams();
  const locale = params?.locale as string;
  const isArabic = locale === 'ar';
  const [risks, setRisks] = useState<Risk[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRisks();
  }, []);

  const fetchRisks = async () => {
    // TODO: Create proper API endpoint
    setLoading(false);
    // Placeholder data
    setRisks([
      { id: 1, risk_id: 'RISK-001', risk_type: 'cyber', title_en: 'Ransomware Attack', title_ar: 'هجوم برمجيات الفدية', likelihood_inherent: 4, impact_inherent: 5, risk_score_inherent: 20, risk_level_inherent: 'critical', status: 'open' },
      { id: 2, risk_id: 'RISK-002', risk_type: 'compliance', title_en: 'PDPL Non-Compliance', title_ar: 'عدم الامتثال لـ PDPL', likelihood_inherent: 3, impact_inherent: 4, risk_score_inherent: 12, risk_level_inherent: 'high', status: 'open' },
      { id: 3, risk_id: 'RISK-003', risk_type: 'operational', title_en: 'System Downtime', title_ar: 'توقف النظام', likelihood_inherent: 2, impact_inherent: 3, risk_score_inherent: 6, risk_level_inherent: 'medium', status: 'mitigated' }
    ]);
  };

  const getRiskLevelBadge = (level?: string) => {
    const classes = {
      critical: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800'
    };
    return classes[level as keyof typeof classes] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen"><p>{isArabic ? 'جاري التحميل...' : 'Loading...'}</p></div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-red-50 p-8" dir={isArabic ? 'rtl' : 'ltr'}>
      <div className="mb-8">
        <div className="bg-gradient-to-r from-orange-600 to-red-600 rounded-2xl shadow-2xl p-8 text-white">
          <h1 className="text-4xl font-bold mb-2">
            {isArabic ? '⚠️ إدارة المخاطر المؤسسية' : '⚠️ Enterprise Risk Management'}
          </h1>
          <p className="text-orange-100 text-lg">
            {isArabic ? 'تحديد وتقييم وتخفيف المخاطر التنظيمية' : 'Identify, assess, and mitigate organizational risks'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <p className="text-gray-500 text-sm">{isArabic ? 'إجمالي المخاطر' : 'Total Risks'}</p>
          <p className="text-3xl font-bold text-orange-600 mt-2">{risks.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6">
          <p className="text-gray-500 text-sm">{isArabic ? 'المخاطر الحرجة' : 'Critical Risks'}</p>
          <p className="text-3xl font-bold text-red-600 mt-2">{risks.filter(r => r.risk_level_inherent === 'critical').length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6">
          <p className="text-gray-500 text-sm">{isArabic ? 'المخاطر المفتوحة' : 'Open Risks'}</p>
          <p className="text-3xl font-bold text-orange-600 mt-2">{risks.filter(r => r.status === 'open').length}</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-xl p-6">
        <h2 className="text-2xl font-bold mb-6">{isArabic ? 'سجل المخاطر' : 'Risk Register'}</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'المعرف' : 'Risk ID'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'العنوان' : 'Title'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'النوع' : 'Type'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'الاحتمالية' : 'Likelihood'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'التأثير' : 'Impact'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'الدرجة' : 'Score'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'المستوى' : 'Level'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'الحالة' : 'Status'}</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {risks.map((risk) => (
                <tr key={risk.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">{risk.risk_id}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{isArabic ? risk.title_ar : risk.title_en}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{risk.risk_type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{risk.likelihood_inherent}/5</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{risk.impact_inherent}/5</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-red-600">{risk.risk_score_inherent}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getRiskLevelBadge(risk.risk_level_inherent)}`}>
                      {risk.risk_level_inherent?.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${risk.status === 'open' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>
                      {risk.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
