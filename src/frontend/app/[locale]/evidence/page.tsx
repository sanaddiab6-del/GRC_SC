'use client';

import { useTranslations } from 'next-intl';
import useSWR from 'swr';
import apiClient from '@/lib/api-client';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useState } from 'react';

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export default function EvidenceListPage() {
  const params = useParams();
  const locale = params.locale as string;
  const isArabic = locale === 'ar';
  
  const [statusFilter, setStatusFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');

  const queryParams = new URLSearchParams();
  if (statusFilter) queryParams.append('status', statusFilter);
  if (typeFilter) queryParams.append('evidence_type', typeFilter);

  const { data: evidence, isLoading, error } = useSWR(
    `/api/v1/evidence?${queryParams.toString()}`,
    fetcher
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const stats = {
    total: evidence?.items?.length || 0,
    approved: evidence?.items?.filter((e: any) => e.validation_status === 'approved').length || 0,
    pending: evidence?.items?.filter((e: any) => e.validation_status === 'pending').length || 0,
    rejected: evidence?.items?.filter((e: any) => e.validation_status === 'rejected').length || 0,
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold mb-2">
                {isArabic ? '📎 إدارة الأدلة' : '📎 Evidence Management'}
              </h1>
              <p className="text-xl text-gray-600">
                {isArabic
                  ? 'عرض وإدارة جميع أدلة الامتثال'
                  : 'View and manage all compliance evidence'}
              </p>
            </div>
            <Link
              href={`/${locale}/evidence/upload`}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700"
            >
              {isArabic ? '+ تحميل أدلة جديدة' : '+ Upload Evidence'}
            </Link>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-blue-500">
            <p className="text-sm text-gray-600 mb-1">{isArabic ? 'إجمالي الأدلة' : 'Total Evidence'}</p>
            <p className="text-3xl font-bold text-blue-600">{stats.total}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-green-500">
            <p className="text-sm text-gray-600 mb-1">{isArabic ? 'معتمد' : 'Approved'}</p>
            <p className="text-3xl font-bold text-green-600">{stats.approved}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-yellow-500">
            <p className="text-sm text-gray-600 mb-1">{isArabic ? 'قيد المراجعة' : 'Pending'}</p>
            <p className="text-3xl font-bold text-yellow-600">{stats.pending}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6 border-l-4 border-red-500">
            <p className="text-sm text-gray-600 mb-1">{isArabic ? 'مرفوض' : 'Rejected'}</p>
            <p className="text-3xl font-bold text-red-600">{stats.rejected}</p>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-lg font-semibold mb-4">
            {isArabic ? 'تصفية الأدلة' : 'Filter Evidence'}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2">
                {isArabic ? 'حالة التحقق' : 'Validation Status'}
              </label>
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="">{isArabic ? 'جميع الحالات' : 'All Statuses'}</option>
                <option value="approved">{isArabic ? 'معتمد' : 'Approved'}</option>
                <option value="pending">{isArabic ? 'قيد المراجعة' : 'Pending'}</option>
                <option value="rejected">{isArabic ? 'مرفوض' : 'Rejected'}</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">
                {isArabic ? 'نوع الأدلة' : 'Evidence Type'}
              </label>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              >
                <option value="">{isArabic ? 'جميع الأنواع' : 'All Types'}</option>
                <option value="document">{isArabic ? 'وثيقة' : 'Document'}</option>
                <option value="screenshot">{isArabic ? 'لقطة شاشة' : 'Screenshot'}</option>
                <option value="log">{isArabic ? 'سجل النظام' : 'System Log'}</option>
                <option value="certificate">{isArabic ? 'شهادة' : 'Certificate'}</option>
                <option value="report">{isArabic ? 'تقرير' : 'Report'}</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => {
                  setStatusFilter('');
                  setTypeFilter('');
                }}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                {isArabic ? 'مسح التصفية' : 'Clear Filters'}
              </button>
            </div>
          </div>
        </div>

        {/* Evidence List - Skeleton for now */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-semibold mb-6">
            {isArabic ? 'قائمة الأدلة' : 'Evidence List'}
          </h2>
          
          {evidence?.items && evidence.items.length > 0 ? (
            <div className="space-y-4">
              {evidence.items.map((item: any, index: number) => (
                <div
                  key={item.id || index}
                  className="border-2 border-gray-200 rounded-lg p-6 hover:border-primary-500 hover:shadow-md transition-all"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-grow">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-2xl">📄</span>
                        <h3 className="text-lg font-bold">{item.title}</h3>
                      </div>
                      {item.description && (
                        <p className="text-gray-600 mb-3">{item.description}</p>
                      )}
                      <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                        <span>
                          <strong>{isArabic ? 'الضابط:' : 'Control:'}</strong> {item.control_id}
                        </span>
                        <span>
                          <strong>{isArabic ? 'النوع:' : 'Type:'}</strong> {item.evidence_type}
                        </span>
                        <span>
                          <strong>{isArabic ? 'التاريخ:' : 'Date:'}</strong>{' '}
                          {new Date(item.collection_date).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                    <span
                      className={`px-4 py-2 rounded-full text-sm font-semibold ${
                        item.validation_status === 'approved'
                          ? 'bg-green-100 text-green-800'
                          : item.validation_status === 'rejected'
                          ? 'bg-red-100 text-red-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}
                    >
                      {item.validation_status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-16">
              <div className="text-6xl mb-4">📂</div>
              <h3 className="text-2xl font-bold text-gray-400 mb-2">
                {isArabic ? 'لا توجد أدلة' : 'No Evidence Found'}
              </h3>
              <p className="text-gray-500 mb-6">
                {isArabic
                  ? 'ابدأ بتحميل الأدلة لإظهار الامتثال للضوابط'
                  : 'Start by uploading evidence to demonstrate compliance with controls'}
              </p>
              <Link
                href={`/${locale}/evidence/upload`}
                className="inline-block px-6 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700"
              >
                {isArabic ? '+ تحميل أدلة' : '+ Upload Evidence'}
              </Link>
            </div>
          )}
        </div>

        {/* Guidelines */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
            <span className="text-xl">💡</span>
            {isArabic ? 'إرشادات إدارة الأدلة' : 'Evidence Management Guidelines'}
          </h3>
          <ul className="text-sm text-blue-800 space-y-2">
            <li>✓ {isArabic ? 'تأكد من أن الأدلة حديثة وذات صلة بالضابط' : 'Ensure evidence is recent and relevant to the control'}</li>
            <li>✓ {isArabic ? 'قم بإزالة أي معلومات حساسة أو سرية' : 'Remove any sensitive or confidential information'}</li>
            <li>✓ {isArabic ? 'استخدم عناوين وأوصاف واضحة' : 'Use clear titles and descriptions'}</li>
            <li>✓ {isArabic ? 'حدد تواريخ انتهاء الصلاحية للأدلة الحساسة للوقت' : 'Set expiry dates for time-sensitive evidence'}</li>
            <li>✓ {isArabic ? 'قم بمراجعة الأدلة وتحديثها بانتظام' : 'Regularly review and update evidence'}</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
