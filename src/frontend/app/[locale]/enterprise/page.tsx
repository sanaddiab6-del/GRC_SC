'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import axios from 'axios';
import Link from 'next/link';

// ============================================================================
// INTERFACES
// ============================================================================

interface DashboardStats {
  organizations: number;
  risks: number;
  audit_findings: number;
  dsar_requests: number;
}

interface Organization {
  id: number;
  name_en: string;
  name_ar: string;
  org_type?: string;
  license_type?: string;
  is_active: boolean;
}

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

interface AuditFinding {
  id: number;
  finding_id: string;
  title_en: string;
  title_ar?: string;
  severity: string;
  risk_rating?: string;
  status: string;
  is_overdue: boolean;
}

interface DSARRequest {
  id: number;
  dsar_id: string;
  data_subject_name: string;
  request_date: string;
  request_type: string;
  response_deadline: string;
  status?: string;
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function EnterpriseDashboard() {
  const params = useParams();
  const locale = params?.locale as string;
  const isArabic = locale === 'ar';

  const API_BASE = 'http://localhost:8000/api/v1/enterprise';

  // State
  const [stats, setStats] = useState<DashboardStats>({ organizations: 0, risks: 0, audit_findings: 0, dsar_requests: 0 });
  const [organizations, setOrganizations] = useState<Organization[]>([]);
  const [risks, setRisks] = useState<Risk[]>([]);
  const [findings, setFindings] = useState<AuditFinding[]>([]);
  const [dsarRequests, setDsarRequests] = useState<DSARRequest[]>([]);
  const [loading, setLoading] = useState(true);

  // Fetch data on mount
  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    setLoading(true);
    try {
      // Fetch dashboard stats
      const statsRes = await axios.get(`${API_BASE}/test/dashboard`);
      setStats(statsRes.data);

      // Fetch organizations
      const orgsRes = await axios.get(`${API_BASE}/test/organizations`);
      setOrganizations(orgsRes.data.organizations || []);

      setLoading(false);
    } catch (error) {
      console.error('Error fetching enterprise data:', error);
      setLoading(false);
    }
  };

  // ============================================================================
  // RENDER
  // ============================================================================

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
          <p className="mt-4 text-gray-600 text-lg">{isArabic ? 'جاري التحميل...' : 'Loading...'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-8" dir={isArabic ? 'rtl' : 'ltr'}>
      {/* Header */}
      <div className="mb-8">
        <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl shadow-2xl p-8 text-white">
          <h1 className="text-4xl font-bold mb-2">
            {isArabic ? '🏢 لوحة التحكم المؤسسية' : '🏢 Enterprise GRC Dashboard'}
          </h1>
          <p className="text-purple-100 text-lg">
            {isArabic 
              ? 'إدارة الحوكمة والمخاطر والامتثال على مستوى المؤسسة'
              : 'Governance, Risk & Compliance Management at Enterprise Scale'}
          </p>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {/* Organizations */}
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">
                {isArabic ? 'المؤسسات' : 'Organizations'}
              </p>
              <p className="text-3xl font-bold text-blue-600 mt-2">{stats.organizations}</p>
            </div>
            <div className="bg-blue-100 rounded-full p-4">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
          </div>
        </div>

        {/* Risks */}
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-orange-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">
                {isArabic ? 'المخاطر النشطة' : 'Active Risks'}
              </p>
              <p className="text-3xl font-bold text-orange-600 mt-2">{stats.risks}</p>
            </div>
            <div className="bg-orange-100 rounded-full p-4">
              <svg className="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Audit Findings */}
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-red-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">
                {isArabic ? 'نتائج التدقيق' : 'Audit Findings'}
              </p>
              <p className="text-3xl font-bold text-red-600 mt-2">{stats.audit_findings}</p>
            </div>
            <div className="bg-red-100 rounded-full p-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
          </div>
        </div>

        {/* DSAR Requests (PDPL) */}
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">
                {isArabic ? 'طلبات حقوق البيانات' : 'DSAR Requests'}
              </p>
              <p className="text-3xl font-bold text-green-600 mt-2">{stats.dsar_requests}</p>
            </div>
            <div className="bg-green-100 rounded-full p-4">
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Links */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Link href={`/${locale}/enterprise/risks`} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition transform hover:-translate-y-1">
          <div className="flex items-center gap-4">
            <div className="bg-orange-100 rounded-lg p-3">
              <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h3 className="font-bold text-lg">{isArabic ? 'إدارة المخاطر' : 'Risk Management'}</h3>
              <p className="text-gray-500 text-sm">{isArabic ? 'سجل المخاطر وتقييم التهديدات' : 'Risk register & threat assessment'}</p>
            </div>
          </div>
        </Link>

        <Link href={`/${locale}/enterprise/audits`} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition transform hover:-translate-y-1">
          <div className="flex items-center gap-4">
            <div className="bg-red-100 rounded-lg p-3">
              <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <div>
              <h3 className="font-bold text-lg">{isArabic ? 'إدارة التدقيق' : 'Audit Management'}</h3>
              <p className="text-gray-500 text-sm">{isArabic ? 'برامج التدقيق والنتائج' : 'Audit programs & findings'}</p>
            </div>
          </div>
        </Link>

        <Link href={`/${locale}/enterprise/pdpl`} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition transform hover:-translate-y-1">
          <div className="flex items-center gap-4">
            <div className="bg-green-100 rounded-lg p-3">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <div>
              <h3 className="font-bold text-lg">{isArabic ? 'عمليات PDPL' : 'PDPL Operations'}</h3>
              <p className="text-gray-500 text-sm">{isArabic ? 'سجل المعالجة وطلبات حقوق البيانات' : 'RoPA & data subject rights'}</p>
            </div>
          </div>
        </Link>

        <Link href={`/${locale}/enterprise/workflows`} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition transform hover:-translate-y-1">
          <div className="flex items-center gap-4">
            <div className="bg-purple-100 rounded-lg p-3">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <div>
              <h3 className="font-bold text-lg">{isArabic ? 'سير العمل' : 'Workflows'}</h3>
              <p className="text-gray-500 text-sm">{isArabic ? 'إدارة الحالات وتتبع SLA' : 'Case management & SLA tracking'}</p>
            </div>
          </div>
        </Link>

        <Link href={`/${locale}/enterprise/vendors`} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition transform hover:-translate-y-1">
          <div className="flex items-center gap-4">
            <div className="bg-indigo-100 rounded-lg p-3">
              <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            </div>
            <div>
              <h3 className="font-bold text-lg">{isArabic ? 'إدارة الموردين' : 'Vendor Management'}</h3>
              <p className="text-gray-500 text-sm">{isArabic ? 'تقييم مخاطر الطرف الثالث' : 'Third-party risk assessment'}</p>
            </div>
          </div>
        </Link>

        <Link href={`/${locale}/enterprise/reports`} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-2xl transition transform hover:-translate-y-1">
          <div className="flex items-center gap-4">
            <div className="bg-cyan-100 rounded-lg p-3">
              <svg className="w-6 h-8 text-cyan-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div>
              <h3 className="font-bold text-lg">{isArabic ? 'التقارير التنفيذية' : 'Executive Reports'}</h3>
              <p className="text-gray-500 text-sm">{isArabic ? 'لوحات معلومات ومقاييس KPI/KRI' : 'Dashboards & KPI/KRI metrics'}</p>
            </div>
          </div>
        </Link>
      </div>

      {/* Organizations Table */}
      <div className="bg-white rounded-xl shadow-xl p-6">
        <h2 className="text-2xl font-bold mb-6 text-gray-800">
          {isArabic ? 'المؤسسات المسجلة' : 'Registered Organizations'}
        </h2>
        
        {organizations.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">{isArabic ? 'لا توجد مؤسسات' : 'No organizations found'}</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {isArabic ? 'الاسم' : 'Name'}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {isArabic ? 'النوع' : 'Type'}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {isArabic ? 'الترخيص' : 'License'}
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    {isArabic ? 'الحالة' : 'Status'}
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {organizations.map((org) => (
                  <tr key={org.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {isArabic ? org.name_ar : org.name_en}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">{org.org_type || '-'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">{org.license_type || '-'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        org.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {isArabic ? (org.is_active ? 'نشط' : 'غير نشط') : (org.is_active ? 'Active' : 'Inactive')}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
