'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';

interface WorkflowCase {
  id: number;
  case_id: string;
  case_type: string;
  title_en: string;
  title_ar?: string;
  status: string;
  priority: string;
  is_overdue: boolean;
}

export default function WorkflowsPage() {
  const params = useParams();
  const locale = params?.locale as string;
  const isArabic = locale === 'ar';
  const [cases, setCases] = useState<WorkflowCase[]>([
    { id: 1, case_id: 'CASE-001', case_type: 'audit_finding', title_en: 'Remediate Password Policy Finding', title_ar: 'معالجة اكتشاف سياسة كلمات المرور', status: 'in_progress', priority: 'high', is_overdue: false },
    { id: 2, case_id: 'CASE-002', case_type: 'evidence_request', title_en: 'Request Encryption Evidence', title_ar: 'طلب دليل التشفير', status: 'pending', priority: 'medium', is_overdue: false }
  ]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-indigo-50 p-8" dir={isArabic ? 'rtl' : 'ltr'}>
      <div className="mb-8">
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl shadow-2xl p-8 text-white">
          <h1 className="text-4xl font-bold mb-2">
            {isArabic ? '⚙️ إدارة سير العمل' : '⚙️ Workflow Management'}
          </h1>
          <p className="text-purple-100 text-lg">
            {isArabic ? 'تتبع الحالات وإدارة SLA' : 'Case tracking & SLA management'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <p className="text-gray-500 text-sm">{isArabic ? 'إجمالي الحالات' : 'Total Cases'}</p>
          <p className="text-3xl font-bold text-purple-600 mt-2">{cases.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6">
          <p className="text-gray-500 text-sm">{isArabic ? 'قيد المعالجة' : 'In Progress'}</p>
          <p className="text-3xl font-bold text-blue-600 mt-2">{cases.filter(c => c.status === 'in_progress').length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6">
          <p className="text-gray-500 text-sm">{isArabic ? 'عالية الأولوية' : 'High Priority'}</p>
          <p className="text-3xl font-bold text-red-600 mt-2">{cases.filter(c => c.priority === 'high').length}</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-xl p-6">
        <h2 className="text-2xl font-bold mb-6">{isArabic ? 'سجل الحالات' : 'Case Register'}</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'المعرف' : 'Case ID'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'العنوان' : 'Title'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'النوع' : 'Type'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'الأولوية' : 'Priority'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'الحالة' : 'Status'}</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {cases.map((c) => (
                <tr key={c.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">{c.case_id}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{isArabic ? c.title_ar : c.title_en}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{c.case_type}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 inline-flex text-xs font-semibold rounded-full ${c.priority === 'high' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                      {c.priority.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 inline-flex text-xs font-semibold rounded-full ${c.status === 'in_progress' ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800'}`}>
                      {c.status.replace('_', ' ').toUpperCase()}
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
