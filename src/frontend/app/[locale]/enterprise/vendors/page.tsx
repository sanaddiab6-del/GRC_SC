'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';

interface Vendor {
  id: number;
  vendor_id: string;
  name_en: string;
  name_ar?: string;
  vendor_type?: string;
  criticality: string;
  risk_level?: string;
  status: string;
}

export default function VendorsPage() {
  const params = useParams();
  const locale = params?.locale as string;
  const isArabic = locale === 'ar';
  const [vendors, setVendors] = useState<Vendor[]>([
    { id: 1, vendor_id: 'VEND-001', name_en: 'Azure Cloud Services', name_ar: 'خدمات أزور السحابية', vendor_type: 'cloud_provider', criticality: 'high', risk_level: 'medium', status: 'active' },
    { id: 2, vendor_id: 'VEND-002', name_en: 'External Auditor Co', name_ar: 'شركة المدقق الخارجي', vendor_type: 'professional_services', criticality: 'medium', risk_level: 'low', status: 'active' }
  ]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-50 p-8" dir={isArabic ? 'rtl' : 'ltr'}>
      <div className="mb-8">
        <div className="bg-gradient-to-r from-indigo-600 to-blue-600 rounded-2xl shadow-2xl p-8 text-white">
          <h1 className="text-4xl font-bold mb-2">
            {isArabic ? '🤝 إدارة الموردين' : '🤝 Vendor Management'}
          </h1>
          <p className="text-indigo-100 text-lg">
            {isArabic ? 'تقييم مخاطر الطرف الثالث' : 'Third-party risk assessment'}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <p className="text-gray-500 text-sm">{isArabic ? 'إجمالي الموردين' : 'Total Vendors'}</p>
          <p className="text-3xl font-bold text-indigo-600 mt-2">{vendors.length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6">
          <p className="text-gray-500 text-sm">{isArabic ? 'عالية الأهمية' : 'High Criticality'}</p>
          <p className="text-3xl font-bold text-red-600 mt-2">{vendors.filter(v => v.criticality === 'high').length}</p>
        </div>
        <div className="bg-white rounded-xl shadow-lg p-6">
          <p className="text-gray-500 text-sm">{isArabic ? 'نشط' : 'Active'}</p>
          <p className="text-3xl font-bold text-green-600 mt-2">{vendors.filter(v => v.status === 'active').length}</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-xl p-6">
        <h2 className="text-2xl font-bold mb-6">{isArabic ? 'سجل الموردين' : 'Vendor Register'}</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'المعرف' : 'Vendor ID'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'الاسم' : 'Name'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'النوع' : 'Type'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'الأهمية' : 'Criticality'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'مستوى المخاطر' : 'Risk Level'}</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">{isArabic ? 'الحالة' : 'Status'}</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {vendors.map((v) => (
                <tr key={v.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">{v.vendor_id}</td>
                  <td className="px-6 py-4 text-sm text-gray-900">{isArabic ? v.name_ar : v.name_en}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{v.vendor_type}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 inline-flex text-xs font-semibold rounded-full ${v.criticality === 'high' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                      {v.criticality.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-3 py-1 inline-flex text-xs font-semibold rounded-full ${v.risk_level === 'low' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                      {(v.risk_level || 'N/A').toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-3 py-1 inline-flex text-xs font-semibold rounded-full bg-green-100 text-green-800">
                      {v.status.toUpperCase()}
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
