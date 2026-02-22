'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';

interface DSARRequest {
  id: number;
  dsar_id: string;
  data_subject_name: string;
  request_date: string;
  request_type: string;
  response_deadline: string;
  status: string;
}

export default function PDPLOperationsPage() {
  const params = useParams();
  const locale = params?.locate as string;
  const isArabic = locale === 'ar';
  const [dsarRequests, setDsarRequests] = useState<DSARRequest[]>([]);

  useEffect(() => {
    // Placeholder data
    setDsarRequests([
      { id: 1, dsar_id: 'DSAR-001', data_subject_name: 'Ahmed Ali', request_date: '2024-02-01', request_type: 'access', response_deadline: '2024-03-02', status: 'in_progress' },
      { id: 2, dsar_id: 'DSAR-002', data_subject_name: 'Sara Mohamed', request_date: '2024-02-15', request_type: 'erasure', response_deadline: '2024-03-17', status: 'pending' }
    ]);
  }, []);

  const getStatusBadge = (status: string) => {
    const classes = {
      pending: 'bg-yellow-100 text-yellow-800',
      in_progress: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800'
    };
    return classes[status as keyof typeof classes] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-teal-50 p-8" dir={isArabic ? 'rtl' : 'ltr'}>
      <div className="mb-8">
        <div className="bg-gradient-to-r from-green-600 to-teal-600 rounded-2xl shadow-2xl p-8 text-white">
          <h1 className="text-4xl font-bold mb-2">
            {isArabic ? '🔒 عمليات حماية البيانات (PDPL)' : '🔒 PDPL Operations'}
          </h1>
          <p className="text-green-100 text-lg">
            {isArabic ? 'إدارة طلبات حقوق أصحاب البيانات والامتثال لـ PDPL' : 'Manage data subject rights requests & PDPL compliance'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <p className="text-gray-500 text-sm">{isArabic ? 'إجمالي الطلبات' : 'Total Requests'}</p>
          <p className="text-3xl font-bold text-green-600 mt-2">{dsarRequests.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6">
          <p className="text-gray-500 text-sm">{isArabic ? 'قيد المعالجة' : 'In Progress'}</p>
          <p className="text-3xl font-bold text-blue-600 mt-2">{dsarRequests.filter(d => d.status === 'in_progress').length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6">
          <p className="text-gray-500 text-sm">{isArabic ? 'معلقة' : 'Pending'}</p>
          <p className="text-3xl font-bold text-yellow-600 mt-2">{dsarRequests.filter(d => d.status === 'pending').length}</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-xl p-6 mb-6">
        <h2 className="text-2xl font-bold mb-6">{isArabic ? 'طلبات حقوق البيانات (DSAR)' : 'Data Subject Access Requests (DSAR)'}</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'المعرف' : 'Request ID'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'الاسم' : 'Name'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'النوع' : 'Type'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'تاريخ الطلب' : 'Request Date'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'الموعد النهائي' : 'Deadline'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'الحالة' : 'Status'}</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {dsarRequests.map((req) => (
                <tr key={req.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">{req.dsar_id}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{req.data_subject_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{req.request_type}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{req.request_date}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{req.response_deadline}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadge(req.status)}`}>
                      {req.status.replace('_', ' ').toUpperCase()}
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
