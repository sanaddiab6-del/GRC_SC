'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';

interface AuditFinding {
  id: number;
  finding_id: string;
  title_en: string;
  title_ar?: string;
  severity: string;
  status: string;
  is_overdue: boolean;
}

export default function AuditFindingsPage() {
  const params = useParams();
  const locale = params?.locale as string;
  const isArabic = locale === 'ar';
  const [findings, setFindings] = useState<AuditFinding[]>([]);

  useEffect(() => {
    // Placeholder data
    setFindings([
      { id: 1, finding_id: 'FIND-001', title_en: 'Weak Password Policy', title_ar: 'سياسة كلمات المرور الضعيفة', severity: 'high', status: 'open', is_overdue: true },
      { id: 2, finding_id: 'FIND-002', title_en: 'Missing Encryption', title_ar: 'التشفير المفقود', severity: 'critical', status: 'open', is_overdue: false }
    ]);
  }, []);

  const getSeverityBadge = (severity: string) => {
    const classes = {
      critical: 'bg-red-100 text-red-800',
      high: 'bg-orange-100 text-orange-800',
      medium: 'bg-yellow-100 text-yellow-800',
      low: 'bg-green-100 text-green-800'
    };
    return classes[severity as keyof typeof classes] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-pink-50 p-8" dir={isArabic ? 'rtl' : 'ltr'}>
      <div className="mb-8">
        <div className="bg-gradient-to-r from-red-600 to-pink-600 rounded-2xl shadow-2xl p-8 text-white">
          <h1 className="text-4xl font-bold mb-2">
            {isArabic ? '🔍 إدارة نتائج التدقيق' : '🔍 Audit Findings Management'}
          </h1>
          <p className="text-red-100 text-lg">
            {isArabic ? 'تتبع ومعالجة نتائج التدقيق' : 'Track and remediate audit findings'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <p className="text-gray-500 text-sm">{isArabic ? 'إجمالي النتائج' : 'Total Findings'}</p>
          <p className="text-3xl font-bold text-red-600 mt-2">{findings.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6">
          <p className="text-gray-500 text-sm">{isArabic ? 'النتائج الحرجة' : 'Critical Findings'}</p>
          <p className="text-3xl font-bold text-red-600 mt-2">{findings.filter(f => f.severity === 'critical').length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6">
          <p className="text-gray-500 text-sm">{isArabic ? 'النتائج المتأخرة' : 'Overdue Findings'}</p>
          <p className="text-3xl font-bold text-orange-600 mt-2">{findings.filter(f => f.is_overdue).length}</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-xl p-6">
        <h2 className="text-2xl font-bold mb-6">{isArabic ? 'سجل النتائج' : 'Findings Register'}</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'المعرف' : 'Finding ID'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'العنوان' : 'Title'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'الخطورة' : 'Severity'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'الحالة' : 'Status'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'متأخر' : 'Overdue'}</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {findings.map((finding) => (
                <tr key={finding.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">{finding.finding_id}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{isArabic ? finding.title_ar : finding.title_en}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getSeverityBadge(finding.severity)}`}>
                      {finding.severity.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">
                      {finding.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {finding.is_overdue && <span className="text-red-600 font-bold">{isArabic ? '⚠️ نعم' : '⚠️ Yes'}</span>}
                    {!finding.is_overdue && <span className="text-green-600">{isArabic ? '✓ لا' : '✓ No'}</span>}
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
