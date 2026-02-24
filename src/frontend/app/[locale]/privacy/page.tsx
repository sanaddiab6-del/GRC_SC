'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import axios from 'axios';

// ===== INTERFACES =====

interface Consent {
  consent_id: string;
  user_id: string;
  consent_type: string;
  status: string;
  purpose_en: string;
  purpose_ar: string;
  given_at: string;
  withdrawn_at?: string;
  expires_at?: string;
}

interface DSARRequest {
  request_id: string;
  user_id: string;
  request_type: string;
  status: string;
  requested_at: string;
  due_date: string;
  completed_at?: string;
  description_en?: string;
  description_ar?: string;
  response_en?: string;
  response_ar?: string;
}

interface DataBreach {
  incident_id: string;
  incident_number: string;
  discovered_at: string;
  breach_type: string;
  severity: string;
  affected_records_count: number;
  status: string;
  sdaia_notified_at?: string;
  users_notified_at?: string;
  impact_description_en: string;
  impact_description_ar: string;
}

interface RetentionPolicy {
  policy_id: string;
  resource_type: string;
  retention_period_days: number;
  legal_basis_en: string;
  legal_basis_ar: string;
  auto_delete_enabled: boolean;
  created_at: string;
}

interface PrivacyStats {
  totalConsents: number;
  activeConsents: number;
  pendingDSARs: number;
  totalBreaches: number;
  criticalBreaches: number;
  retentionPolicies: number;
}

export default function PrivacyDashboardPage() {
  const params = useParams();
  const locale = params.locale as string;
  const isArabic = locale === 'ar';

  // ===== STATE =====
  const [selectedTab, setSelectedTab] = useState<'consent' | 'dsar' | 'breach' | 'retention'>('consent');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Data states
  const [consents, setConsents] = useState<Consent[]>([]);
  const [dsarRequests, setDsarRequests] = useState<DSARRequest[]>([]);
  const [breaches, setBreaches] = useState<DataBreach[]>([]);
  const [retentionPolicies, setRetentionPolicies] = useState<RetentionPolicy[]>([]);
  const [stats, setStats] = useState<PrivacyStats>({
    totalConsents: 0,
    activeConsents: 0,
    pendingDSARs: 0,
    totalBreaches: 0,
    criticalBreaches: 0,
    retentionPolicies: 0,
  });

  // Modal states
  const [showConsentModal, setShowConsentModal] = useState(false);
  const [showDSARModal, setShowDSARModal] = useState(false);
  const [showBreachModal, setShowBreachModal] = useState(false);
  const [showRetentionModal, setShowRetentionModal] = useState(false);
  const [showDSARUpdateModal, setShowDSARUpdateModal] = useState(false);
  const [selectedDSAR, setSelectedDSAR] = useState<DSARRequest | null>(null);

  // Form states
  const [newConsent, setNewConsent] = useState({
    consent_type: 'DATA_PROCESSING',
    purpose_en: '',
    purpose_ar: '',
    legal_basis_en: '',
    legal_basis_ar: '',
    consent_text_en: '',
    consent_text_ar: '',
    expires_at: '',
  });

  const [newDSAR, setNewDSAR] = useState({
    request_type: 'ACCESS',
    description_en: '',
    description_ar: '',
    verification_method: 'email',
  });

  const [newBreach, setNewBreach] = useState({
    discovered_at: new Date().toISOString().split('T')[0],
    breach_type: 'unauthorized_access',
    severity: 'medium',
    affected_records_count: 0,
    affected_data_types: [] as string[],
    impact_description_en: '',
    impact_description_ar: '',
    containment_actions_en: '',
    containment_actions_ar: '',
  });

  const [newRetentionPolicy, setNewRetentionPolicy] = useState({
    resource_type: 'users',
    retention_period_days: 365,
    legal_basis_en: '',
    legal_basis_ar: '',
    auto_delete_enabled: true,
    deletion_method: 'soft_delete',
  });

  const [dsarUpdate, setDsarUpdate] = useState({
    status: 'PENDING',
    processor_notes: '',
    response_en: '',
    response_ar: '',
    rejection_reason_en: '',
    rejection_reason_ar: '',
  });

  // ===== API FUNCTIONS =====

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return { Authorization: `Bearer ${token}` };
  };

  const API_BASE = 'http://localhost:8000/api/v1';

  // Fetch all data
  const fetchAllData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const headers = getAuthHeaders();

      // Fetch consents
      const consentsRes = await axios.get(`${API_BASE}/privacy/consent`, { headers });
      setConsents(consentsRes.data);

      // Fetch DSARs
      const dsarRes = await axios.get(`${API_BASE}/privacy/dsar`, { headers });
      setDsarRequests(dsarRes.data);

      // Fetch breaches (admin only)
      let breachData: DataBreach[] = [];
      try {
        const breachRes = await axios.get(`${API_BASE}/privacy/breach`, { headers });
        breachData = breachRes.data;
        setBreaches(breachData);
      } catch (err: any) {
        if (err.response?.status !== 403) {
          console.error('Failed to fetch breaches:', err);
        }
      }

      // Fetch retention policies
      const retentionRes = await axios.get(`${API_BASE}/privacy/retention`, { headers });
      setRetentionPolicies(retentionRes.data);

      // Calculate stats
      const activeConsents = consentsRes.data.filter((c: Consent) => c.status === 'ACTIVE').length;
      const pendingDSARs = dsarRes.data.filter((d: DSARRequest) => d.status === 'PENDING').length;
      const criticalBreaches = breachData.filter((b: DataBreach) => b.severity === 'critical').length;

      setStats({
        totalConsents: consentsRes.data.length,
        activeConsents,
        pendingDSARs,
        totalBreaches: breachData.length,
        criticalBreaches,
        retentionPolicies: retentionRes.data.length,
      });
    } catch (error: any) {
      console.error('Failed to fetch data:', error);
      setError(error.response?.data?.detail || error.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // ===== CONSENT HANDLERS =====

  const handleCreateConsent = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const headers = getAuthHeaders();
      const payload = {
        ...newConsent,
        expires_at: newConsent.expires_at ? new Date(newConsent.expires_at).toISOString() : null,
      };
      
      await axios.post(`${API_BASE}/privacy/consent`, payload, { headers });
      await fetchAllData();
      setShowConsentModal(false);
      setNewConsent({
        consent_type: 'DATA_PROCESSING',
        purpose_en: '',
        purpose_ar: '',
        legal_basis_en: '',
        legal_basis_ar: '',
        consent_text_en: '',
        consent_text_ar: '',
        expires_at: '',
      });
      alert(isArabic ? 'تم حفظ الموافقة بنجاح' : 'Consent saved successfully');
    } catch (error: any) {
      alert(
        isArabic
          ? `فشل في حفظ الموافقة: ${error.response?.data?.detail || error.message}`
          : `Failed to save consent: ${error.response?.data?.detail || error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

  const handleWithdrawConsent = async (consentId: string) => {
    if (!confirm(isArabic ? 'هل أنت متأكد من سحب هذه الموافقة؟' : 'Are you sure you want to withdraw this consent?')) {
      return;
    }

    setLoading(true);
    try {
      const headers = getAuthHeaders();
      await axios.post(`${API_BASE}/privacy/consent/${consentId}/withdraw`, {}, { headers });
      await fetchAllData();
      alert(isArabic ? 'تم سحب الموافقة بنجاح' : 'Consent withdrawn successfully');
    } catch (error: any) {
      alert(
        isArabic
          ? `فشل في سحب الموافقة: ${error.response?.data?.detail || error.message}`
          : `Failed to withdraw consent: ${error.response?.data?.detail || error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

  // ===== DSAR HANDLERS =====

  const handleCreateDSAR = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const headers = getAuthHeaders();
      await axios.post(`${API_BASE}/privacy/dsar`, newDSAR, { headers });
      await fetchAllData();
      setShowDSARModal(false);
      setNewDSAR({
        request_type: 'ACCESS',
        description_en: '',
        description_ar: '',
        verification_method: 'email',
      });
      alert(isArabic ? 'تم إنشاء طلب DSAR بنجاح' : 'DSAR request created successfully');
    } catch (error: any) {
      alert(
        isArabic
          ? `فشل في إنشاء طلب DSAR: ${error.response?.data?.detail || error.message}`
          : `Failed to create DSAR: ${error.response?.data?.detail || error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateDSAR = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDSAR) return;

    setLoading(true);
    try {
      const headers = getAuthHeaders();
      await axios.patch(
        `${API_BASE}/privacy/dsar/${selectedDSAR.request_id}`,
        dsarUpdate,
        { headers }
      );
      await fetchAllData();
      setShowDSARUpdateModal(false);
      setSelectedDSAR(null);
      setDsarUpdate({
        status: 'PENDING',
        processor_notes: '',
        response_en: '',
        response_ar: '',
        rejection_reason_en: '',
        rejection_reason_ar: '',
      });
      alert(isArabic ? 'تم تحديث طلب DSAR بنجاح' : 'DSAR request updated successfully');
    } catch (error: any) {
      alert(
        isArabic
          ? `فشل في تحديث طلب DSAR: ${error.response?.data?.detail || error.message}`
          : `Failed to update DSAR: ${error.response?.data?.detail || error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

  const handleOpenDSARUpdateModal = (dsar: DSARRequest) => {
    setSelectedDSAR(dsar);
    setDsarUpdate({
      status: dsar.status,
      processor_notes: '',
      response_en: dsar.response_en || '',
      response_ar: dsar.response_ar || '',
      rejection_reason_en: '',
      rejection_reason_ar: '',
    });
    setShowDSARUpdateModal(true);
  };

  // ===== BREACH HANDLERS =====

  const handleCreateBreach = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const headers = getAuthHeaders();
      const payload = {
        ...newBreach,
        discovered_at: new Date(newBreach.discovered_at).toISOString(),
      };
      await axios.post(`${API_BASE}/privacy/breach`, payload, { headers });
      await fetchAllData();
      setShowBreachModal(false);
      setNewBreach({
        discovered_at: new Date().toISOString().split('T')[0],
        breach_type: 'unauthorized_access',
        severity: 'medium',
        affected_records_count: 0,
        affected_data_types: [],
        impact_description_en: '',
        impact_description_ar: '',
        containment_actions_en: '',
        containment_actions_ar: '',
      });
      alert(isArabic ? 'تم الإبلاغ عن الخرق بنجاح' : 'Breach reported successfully');
    } catch (error: any) {
      alert(
        isArabic
          ? `فشل في الإبلاغ عن الخرق: ${error.response?.data?.detail || error.message}`
          : `Failed to report breach: ${error.response?.data?.detail || error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

  // ===== RETENTION POLICY HANDLERS =====

  const handleCreateRetentionPolicy = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const headers = getAuthHeaders();
      await axios.post(`${API_BASE}/privacy/retention`, newRetentionPolicy, { headers });
      await fetchAllData();
      setShowRetentionModal(false);
      setNewRetentionPolicy({
        resource_type: 'users',
        retention_period_days: 365,
        legal_basis_en: '',
        legal_basis_ar: '',
        auto_delete_enabled: true,
        deletion_method: 'soft_delete',
      });
      alert(isArabic ? 'تم إنشاء سياسة الاحتفاظ بنجاح' : 'Retention policy created successfully');
    } catch (error: any) {
      alert(
        isArabic
          ? `فشل في إنشاء سياسة الاحتفاظ: ${error.response?.data?.detail || error.message}`
          : `Failed to create retention policy: ${error.response?.data?.detail || error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

  // ===== UTILITY FUNCTIONS =====

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString(isArabic ? 'ar-SA' : 'en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getStatusBadgeClass = (status: string) => {
    const statusMap: { [key: string]: string } = {
      ACTIVE: 'bg-green-100 text-green-800',
      WITHDRAWN: 'bg-red-100 text-red-800',
      EXPIRED: 'bg-gray-100 text-gray-800',
      PENDING: 'bg-yellow-100 text-yellow-800',
      IN_PROGRESS: 'bg-blue-100 text-blue-800',
      COMPLETED: 'bg-green-100 text-green-800',
      REJECTED: 'bg-red-100 text-red-800',
      INVESTIGATING: 'bg-orange-100 text-orange-800',
      CONTAINED: 'bg-blue-100 text-blue-800',
      CLOSED: 'bg-gray-100 text-gray-800',
    };
    return statusMap[status] || 'bg-gray-100 text-gray-800';
  };

  const getSeverityBadgeClass = (severity: string) => {
    const severityMap: { [key: string]: string } = {
      low: 'bg-blue-100 text-blue-800',
      medium: 'bg-yellow-100 text-yellow-800',
      high: 'bg-orange-100 text-orange-800',
      critical: 'bg-red-100 text-red-800',
    };
    return severityMap[severity] || 'bg-gray-100 text-gray-800';
  };

  // ===== RENDER =====

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-gray-100 to-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-900 via-indigo-900 to-purple-900 text-white">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold">
                {isArabic ? '🔒 حماية البيانات الشخصية' : '🔒 Privacy & Data Protection'}
              </h1>
              <p className="mt-2 text-gray-200">
                {isArabic
                  ? 'إدارة الموافقات، طلبات DSAR، خروقات البيانات وسياسات الاحتفاظ - الامتثال لنظام حماية البيانات الشخصية'
                  : 'Manage consents, DSAR requests, data breaches, and retention policies - PDPL Compliance'}
              </p>
            </div>
            <Link
              href={`/${locale}/dashboard`}
              className="bg-white/20 hover:bg-white/30 text-white px-6 py-3 rounded-lg transition font-semibold"
            >
              {isArabic ? '← العودة للوحة التحكم' : '← Back to Dashboard'}
            </Link>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-6 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg border p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">CONSENTS</div>
            <div className="text-3xl font-bold text-green-600 mb-1">{stats.totalConsents}</div>
            <div className="text-sm text-gray-600">{isArabic ? 'إجمالي الموافقات' : 'Total Consents'}</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg border p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">ACTIVE</div>
            <div className="text-3xl font-bold text-blue-600 mb-1">{stats.activeConsents}</div>
            <div className="text-sm text-gray-600">{isArabic ? 'الموافقات النشطة' : 'Active Consents'}</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg border p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">DSAR</div>
            <div className="text-3xl font-bold text-purple-600 mb-1">{stats.pendingDSARs}</div>
            <div className="text-sm text-gray-600">{isArabic ? 'طلبات DSAR المعلقة' : 'Pending DSARs'}</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg border p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">BREACHES</div>
            <div className="text-3xl font-bold text-orange-600 mb-1">{stats.totalBreaches}</div>
            <div className="text-sm text-gray-600">{isArabic ? 'إجمالي الخروقات' : 'Total Breaches'}</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg border p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">CRITICAL</div>
            <div className="text-3xl font-bold text-red-600 mb-1">{stats.criticalBreaches}</div>
            <div className="text-sm text-gray-600">{isArabic ? 'الخروقات الحرجة' : 'Critical Breaches'}</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg border p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">POLICIES</div>
            <div className="text-3xl font-bold text-teal-600 mb-1">{stats.retentionPolicies}</div>
            <div className="text-sm text-gray-600">{isArabic ? 'سياسات الاحتفاظ' : 'Retention Policies'}</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-lg border overflow-hidden">
          <div className="border-b">
            <div className="flex overflow-x-auto">
              <button
                onClick={() => setSelectedTab('consent')}
                className={`px-6 py-4 font-semibold transition whitespace-nowrap ${
                  selectedTab === 'consent'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                }`}
              >
                {isArabic ? '✅ إدارة الموافقات' : '✅ Consent Management'}
              </button>
              <button
                onClick={() => setSelectedTab('dsar')}
                className={`px-6 py-4 font-semibold transition whitespace-nowrap relative ${
                  selectedTab === 'dsar'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                }`}
              >
                {isArabic ? '📋 طلبات DSAR' : '📋 DSAR Requests'}
                {stats.pendingDSARs > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-600 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
                    {stats.pendingDSARs}
                  </span>
                )}
              </button>
              <button
                onClick={() => setSelectedTab('breach')}
                className={`px-6 py-4 font-semibold transition whitespace-nowrap ${
                  selectedTab === 'breach'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                }`}
              >
                {isArabic ? '🚨 إشعارات الخروقات' : '🚨 Breach Notifications'}
              </button>
              <button
                onClick={() => setSelectedTab('retention')}
                className={`px-6 py-4 font-semibold transition whitespace-nowrap ${
                  selectedTab === 'retention'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                }`}
              >
                {isArabic ? '⏱️ سياسات الاحتفاظ' : '⏱️ Retention Policies'}
              </button>
            </div>
          </div>

          <div className="p-8">
            {/* ===== CONSENT TAB ===== */}
            {selectedTab === 'consent' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {isArabic ? 'إدارة الموافقات' : 'Consent Management'}
                  </h2>
                  <button
                    onClick={() => setShowConsentModal(true)}
                    className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition shadow"
                  >
                    + {isArabic ? 'إضافة موافقة' : 'Add Consent'}
                  </button>
                </div>

                {consents.length === 0 ? (
                  <div className="text-center py-12 bg-gray-50 rounded-lg border">
                    <div className="text-6xl mb-4">✅</div>
                    <p className="text-gray-600 text-lg">
                      {isArabic ? 'لا توجد موافقات مسجلة' : 'No consents recorded'}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {consents.map((consent) => (
                      <div
                        key={consent.consent_id}
                        className="bg-gray-50 rounded-lg p-6 border hover:shadow-md transition"
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-xl font-bold text-gray-900">
                                {isArabic ? consent.purpose_ar : consent.purpose_en}
                              </h3>
                              <span
                                className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadgeClass(
                                  consent.status
                                )}`}
                              >
                                {consent.status}
                              </span>
                              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
                                {consent.consent_type}
                              </span>
                            </div>
                            <p className="text-gray-600 text-sm mb-2">
                              {isArabic ? '📅 تاريخ الموافقة:' : '📅 Given:'} {formatDate(consent.given_at)}
                            </p>
                            {consent.expires_at && (
                              <p className="text-gray-600 text-sm mb-2">
                                {isArabic ? '⏰ تنتهي في:' : '⏰ Expires:'} {formatDate(consent.expires_at)}
                              </p>
                            )}
                            {consent.withdrawn_at && (
                              <p className="text-red-600 text-sm mb-2">
                                {isArabic ? '🚫 تم السحب في:' : '🚫 Withdrawn:'} {formatDate(consent.withdrawn_at)}
                              </p>
                            )}
                          </div>
                          {consent.status === 'ACTIVE' && (
                            <button
                              onClick={() => handleWithdrawConsent(consent.consent_id)}
                              disabled={loading}
                              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-semibold transition shadow disabled:opacity-50"
                            >
                              {isArabic ? 'سحب الموافقة' : 'Withdraw Consent'}
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* ===== DSAR TAB ===== */}
            {selectedTab === 'dsar' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {isArabic ? 'طلبات الوصول إلى البيانات (DSAR)' : 'Data Subject Access Requests (DSAR)'}
                  </h2>
                  <button
                    onClick={() => setShowDSARModal(true)}
                    className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition shadow"
                  >
                    + {isArabic ? 'إنشاء طلب DSAR' : 'Create DSAR Request'}
                  </button>
                </div>

                {dsarRequests.length === 0 ? (
                  <div className="text-center py-12 bg-gray-50 rounded-lg border">
                    <div className="text-6xl mb-4">📋</div>
                    <p className="text-gray-600 text-lg">
                      {isArabic ? 'لا توجد طلبات DSAR' : 'No DSAR requests'}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {dsarRequests.map((dsar) => (
                      <div
                        key={dsar.request_id}
                        className="bg-gray-50 rounded-lg p-6 border hover:shadow-md transition"
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-xl font-bold text-gray-900">
                                {dsar.request_type} Request
                              </h3>
                              <span
                                className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadgeClass(
                                  dsar.status
                                )}`}
                              >
                                {dsar.status}
                              </span>
                            </div>
                            <p className="text-gray-600 text-sm mb-2">
                              {isArabic ? '📅 تاريخ الطلب:' : '📅 Requested:'} {formatDate(dsar.requested_at)}
                            </p>
                            <p className="text-gray-600 text-sm mb-2">
                              {isArabic ? '⏰ موعد الاستحقاق:' : '⏰ Due Date:'} {formatDate(dsar.due_date)}
                            </p>
                            {dsar.completed_at && (
                              <p className="text-green-600 text-sm mb-2">
                                {isArabic ? '✅ تم الإكمال في:' : '✅ Completed:'} {formatDate(dsar.completed_at)}
                              </p>
                            )}
                            {(dsar.description_en || dsar.description_ar) && (
                              <p className="text-gray-700 mt-2">
                                <span className="font-semibold">{isArabic ? 'الوصف:' : 'Description:'}</span>{' '}
                                {isArabic ? dsar.description_ar : dsar.description_en}
                              </p>
                            )}
                            {dsar.response_en && (
                              <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                                <p className="font-semibold text-blue-900 mb-1">
                                  {isArabic ? 'الرد:' : 'Response:'}
                                </p>
                                <p className="text-gray-700">
                                  {isArabic ? dsar.response_ar : dsar.response_en}
                                </p>
                              </div>
                            )}
                          </div>
                          {(dsar.status === 'PENDING' || dsar.status === 'IN_PROGRESS') && (
                            <button
                              onClick={() => handleOpenDSARUpdateModal(dsar)}
                              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-semibold transition shadow ml-4"
                            >
                              {isArabic ? 'تحديث الحالة' : 'Update Status'}
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* ===== BREACH TAB ===== */}
            {selectedTab === 'breach' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {isArabic ? 'إشعارات خروقات البيانات' : 'Data Breach Notifications'}
                  </h2>
                  <button
                    onClick={() => setShowBreachModal(true)}
                    className="bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-semibold transition shadow"
                  >
                    + {isArabic ? 'الإبلاغ عن خرق' : 'Report Breach'}
                  </button>
                </div>

                {breaches.length === 0 ? (
                  <div className="text-center py-12 bg-gray-50 rounded-lg border">
                    <div className="text-6xl mb-4">🚨</div>
                    <p className="text-gray-600 text-lg">
                      {isArabic ? 'لا توجد خروقات مبلغ عنها' : 'No breaches reported'}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {breaches.map((breach) => (
                      <div
                        key={breach.incident_id}
                        className="bg-gray-50 rounded-lg p-6 border hover:shadow-md transition"
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-xl font-bold text-gray-900">{breach.incident_number}</h3>
                              <span
                                className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadgeClass(
                                  breach.status
                                )}`}
                              >
                                {breach.status}
                              </span>
                              <span
                                className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${getSeverityBadgeClass(
                                  breach.severity
                                )}`}
                              >
                                {breach.severity.toUpperCase()}
                              </span>
                            </div>
                            <p className="text-gray-600 text-sm mb-2">
                              {isArabic ? '🔍 نوع الخرق:' : '🔍 Breach Type:'} {breach.breach_type}
                            </p>
                            <p className="text-gray-600 text-sm mb-2">
                              {isArabic ? '📅 تاريخ الاكتشاف:' : '📅 Discovered:'}{' '}
                              {formatDate(breach.discovered_at)}
                            </p>
                            <p className="text-gray-600 text-sm mb-2">
                              {isArabic ? '👥 السجلات المتأثرة:' : '👥 Affected Records:'}{' '}
                              {breach.affected_records_count.toLocaleString()}
                            </p>
                            {breach.sdaia_notified_at && (
                              <p className="text-green-600 text-sm mb-2">
                                {isArabic ? '✅ تم إشعار SDAIA في:' : '✅ SDAIA Notified:'}{' '}
                                {formatDate(breach.sdaia_notified_at)}
                              </p>
                            )}
                            <div className="mt-3 p-3 bg-red-50 rounded-lg">
                              <p className="font-semibold text-red-900 mb-1">
                                {isArabic ? 'وصف التأثير:' : 'Impact Description:'}
                              </p>
                              <p className="text-gray-700">
                                {isArabic ? breach.impact_description_ar : breach.impact_description_en}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* ===== RETENTION TAB ===== */}
            {selectedTab === 'retention' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {isArabic ? 'سياسات الاحتفاظ بالبيانات' : 'Data Retention Policies'}
                  </h2>
                  <button
                    onClick={() => setShowRetentionModal(true)}
                    className="bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition shadow"
                  >
                    + {isArabic ? 'إضافة سياسة' : 'Add Policy'}
                  </button>
                </div>

                {retentionPolicies.length === 0 ? (
                  <div className="text-center py-12 bg-gray-50 rounded-lg border">
                    <div className="text-6xl mb-4">⏱️</div>
                    <p className="text-gray-600 text-lg">
                      {isArabic ? 'لا توجد سياسات احتفاظ محددة' : 'No retention policies defined'}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {retentionPolicies.map((policy) => (
                      <div
                        key={policy.policy_id}
                        className="bg-gray-50 rounded-lg p-6 border hover:shadow-md transition"
                      >
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-xl font-bold text-gray-900 capitalize">
                                {policy.resource_type}
                              </h3>
                              <span
                                className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                                  policy.auto_delete_enabled
                                    ? 'bg-green-100 text-green-800'
                                    : 'bg-gray-100 text-gray-800'
                                }`}
                              >
                                {policy.auto_delete_enabled
                                  ? isArabic
                                    ? '🔄 الحذف التلقائي مفعل'
                                    : '🔄 Auto-delete enabled'
                                  : isArabic
                                  ? '⏸️ الحذف التلقائي معطل'
                                  : '⏸️ Auto-delete disabled'}
                              </span>
                            </div>
                            <p className="text-gray-600 text-sm mb-2">
                              {isArabic ? '⏱️ فترة الاحتفاظ:' : '⏱️ Retention Period:'}{' '}
                              {policy.retention_period_days} {isArabic ? 'يوم' : 'days'} (
                              {(policy.retention_period_days / 365).toFixed(1)}{' '}
                              {isArabic ? 'سنة' : 'years'})
                            </p>
                            <p className="text-gray-600 text-sm mb-2">
                              {isArabic ? '📅 تاريخ الإنشاء:' : '📅 Created:'} {formatDate(policy.created_at)}
                            </p>
                            <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                              <p className="font-semibold text-blue-900 mb-1">
                                {isArabic ? 'الأساس القانوني:' : 'Legal Basis:'}
                              </p>
                              <p className="text-gray-700">
                                {isArabic ? policy.legal_basis_ar : policy.legal_basis_en}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* ===== MODALS ===== */}

      {/* Consent Modal */}
      {showConsentModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h3 className="text-2xl font-bold text-gray-900">
                {isArabic ? 'إضافة موافقة جديدة' : 'Add New Consent'}
              </h3>
            </div>
            <form onSubmit={handleCreateConsent} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  {isArabic ? 'نوع الموافقة' : 'Consent Type'}
                </label>
                <select
                  value={newConsent.consent_type}
                  onChange={(e) => setNewConsent({ ...newConsent, consent_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  required
                >
                  <option value="DATA_PROCESSING">Data Processing</option>
                  <option value="MARKETING">Marketing</option>
                  <option value="PROFILING">Profiling</option>
                  <option value="THIRD_PARTY_SHARING">Third Party Sharing</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'الغرض (بالإنجليزية)' : 'Purpose (English)'}
                  </label>
                  <input
                    type="text"
                    value={newConsent.purpose_en}
                    onChange={(e) => setNewConsent({ ...newConsent, purpose_en: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'الغرض (بالعربية)' : 'Purpose (Arabic)'}
                  </label>
                  <input
                    type="text"
                    value={newConsent.purpose_ar}
                    onChange={(e) => setNewConsent({ ...newConsent, purpose_ar: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'الأساس القانوني (بالإنجليزية)' : 'Legal Basis (English)'}
                  </label>
                  <input
                    type="text"
                    value={newConsent.legal_basis_en}
                    onChange={(e) => setNewConsent({ ...newConsent, legal_basis_en: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'الأساس القانوني (بالعربية)' : 'Legal Basis (Arabic)'}
                  </label>
                  <input
                    type="text"
                    value={newConsent.legal_basis_ar}
                    onChange={(e) => setNewConsent({ ...newConsent, legal_basis_ar: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  {isArabic ? 'تاريخ الانتهاء (اختياري)' : 'Expiry Date (Optional)'}
                </label>
                <input
                  type="date"
                  value={newConsent.expires_at}
                  onChange={(e) => setNewConsent({ ...newConsent, expires_at: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                />
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition shadow disabled:opacity-50"
                >
                  {loading ? (isArabic ? 'جاري الحفظ...' : 'Saving...') : isArabic ? 'حفظ' : 'Save'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowConsentModal(false)}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-3 rounded-lg font-semibold transition"
                >
                  {isArabic ? 'إلغاء' : 'Cancel'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* DSAR Modal */}
      {showDSARModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h3 className="text-2xl font-bold text-gray-900">
                {isArabic ? 'إنشاء طلب DSAR جديد' : 'Create New DSAR Request'}
              </h3>
            </div>
            <form onSubmit={handleCreateDSAR} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  {isArabic ? 'نوع الطلب' : 'Request Type'}
                </label>
                <select
                  value={newDSAR.request_type}
                  onChange={(e) => setNewDSAR({ ...newDSAR, request_type: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  required
                >
                  <option value="ACCESS">Access - View my data</option>
                  <option value="RECTIFICATION">Rectification - Correct my data</option>
                  <option value="ERASURE">Erasure - Delete my data</option>
                  <option value="PORTABILITY">Portability - Export my data</option>
                  <option value="OBJECTION">Objection - Stop processing</option>
                  <option value="RESTRICTION">Restriction - Limit processing</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'الوصف (بالإنجليزية)' : 'Description (English)'}
                  </label>
                  <textarea
                    value={newDSAR.description_en}
                    onChange={(e) => setNewDSAR({ ...newDSAR, description_en: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    rows={4}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'الوصف (بالعربية)' : 'Description (Arabic)'}
                  </label>
                  <textarea
                    value={newDSAR.description_ar}
                    onChange={(e) => setNewDSAR({ ...newDSAR, description_ar: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    rows={4}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  {isArabic ? 'طريقة التحقق' : 'Verification Method'}
                </label>
                <select
                  value={newDSAR.verification_method}
                  onChange={(e) => setNewDSAR({ ...newDSAR, verification_method: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  required
                >
                  <option value="email">Email</option>
                  <option value="phone">Phone</option>
                  <option value="id_document">ID Document</option>
                </select>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition shadow disabled:opacity-50"
                >
                  {loading ? (isArabic ? 'جاري الإنشاء...' : 'Creating...') : isArabic ? 'إنشاء' : 'Create'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowDSARModal(false)}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-3 rounded-lg font-semibold transition"
                >
                  {isArabic ? 'إلغاء' : 'Cancel'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* DSAR Update Modal */}
      {showDSARUpdateModal && selectedDSAR && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h3 className="text-2xl font-bold text-gray-900">
                {isArabic ? 'تحديث طلب DSAR' : 'Update DSAR Request'}
              </h3>
            </div>
            <form onSubmit={handleUpdateDSAR} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  {isArabic ? 'الحالة' : 'Status'}
                </label>
                <select
                  value={dsarUpdate.status}
                  onChange={(e) => setDsarUpdate({ ...dsarUpdate, status: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  required
                >
                  <option value="PENDING">Pending</option>
                  <option value="IN_PROGRESS">In Progress</option>
                  <option value="COMPLETED">Completed</option>
                  <option value="REJECTED">Rejected</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'الرد (بالإنجليزية)' : 'Response (English)'}
                  </label>
                  <textarea
                    value={dsarUpdate.response_en}
                    onChange={(e) => setDsarUpdate({ ...dsarUpdate, response_en: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    rows={4}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'الرد (بالعربية)' : 'Response (Arabic)'}
                  </label>
                  <textarea
                    value={dsarUpdate.response_ar}
                    onChange={(e) => setDsarUpdate({ ...dsarUpdate, response_ar: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    rows={4}
                  />
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition shadow disabled:opacity-50"
                >
                  {loading ? (isArabic ? 'جاري التحديث...' : 'Updating...') : isArabic ? 'تحديث' : 'Update'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowDSARUpdateModal(false);
                    setSelectedDSAR(null);
                  }}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-3 rounded-lg font-semibold transition"
                >
                  {isArabic ? 'إلغاء' : 'Cancel'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Breach Modal */}
      {showBreachModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h3 className="text-2xl font-bold text-gray-900">
                {isArabic ? 'الإبلاغ عن خرق بيانات' : 'Report Data Breach'}
              </h3>
              <p className="text-sm text-red-600 mt-1">
                {isArabic
                  ? '⚠️ يجب إشعار SDAIA خلال 72 ساعة للخروقات عالية الخطورة'
                  : '⚠️ SDAIA must be notified within 72 hours for high-severity breaches'}
              </p>
            </div>
            <form onSubmit={handleCreateBreach} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'تاريخ الاكتشاف' : 'Discovery Date'}
                  </label>
                  <input
                    type="date"
                    value={newBreach.discovered_at}
                    onChange={(e) => setNewBreach({ ...newBreach, discovered_at: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'نوع الخرق' : 'Breach Type'}
                  </label>
                  <select
                    value={newBreach.breach_type}
                    onChange={(e) => setNewBreach({ ...newBreach, breach_type: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                    required
                  >
                    <option value="unauthorized_access">Unauthorized Access</option>
                    <option value="data_loss">Data Loss</option>
                    <option value="ransomware">Ransomware</option>
                    <option value="phishing">Phishing</option>
                    <option value="insider_threat">Insider Threat</option>
                    <option value="misconfiguration">Misconfiguration</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'مستوى الخطورة' : 'Severity Level'}
                  </label>
                  <select
                    value={newBreach.severity}
                    onChange={(e) => setNewBreach({ ...newBreach, severity: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                    required
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'عدد السجلات المتأثرة' : 'Affected Records Count'}
                  </label>
                  <input
                    type="number"
                    value={newBreach.affected_records_count}
                    onChange={(e) =>
                      setNewBreach({ ...newBreach, affected_records_count: parseInt(e.target.value) })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                    required
                    min="0"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'وصف التأثير (بالإنجليزية)' : 'Impact Description (English)'}
                  </label>
                  <textarea
                    value={newBreach.impact_description_en}
                    onChange={(e) => setNewBreach({ ...newBreach, impact_description_en: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                    rows={4}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'وصف التأثير (بالعربية)' : 'Impact Description (Arabic)'}
                  </label>
                  <textarea
                    value={newBreach.impact_description_ar}
                    onChange={(e) => setNewBreach({ ...newBreach, impact_description_ar: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                    rows={4}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'إجراءات الاحتواء (بالإنجليزية)' : 'Containment Actions (English)'}
                  </label>
                  <textarea
                    value={newBreach.containment_actions_en}
                    onChange={(e) => setNewBreach({ ...newBreach, containment_actions_en: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                    rows={3}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'إجراءات الاحتواء (بالعربية)' : 'Containment Actions (Arabic)'}
                  </label>
                  <textarea
                    value={newBreach.containment_actions_ar}
                    onChange={(e) => setNewBreach({ ...newBreach, containment_actions_ar: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                    rows={3}
                  />
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-semibold transition shadow disabled:opacity-50"
                >
                  {loading ? (isArabic ? 'جاري الإبلاغ...' : 'Reporting...') : isArabic ? 'إبلاغ' : 'Report Breach'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowBreachModal(false)}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-3 rounded-lg font-semibold transition"
                >
                  {isArabic ? 'إلغاء' : 'Cancel'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Retention Policy Modal */}
      {showRetentionModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h3 className="text-2xl font-bold text-gray-900">
                {isArabic ? 'إنشاء سياسة احتفاظ جديدة' : 'Create New Retention Policy'}
              </h3>
            </div>
            <form onSubmit={handleCreateRetentionPolicy} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'نوع المورد' : 'Resource Type'}
                  </label>
                  <select
                    value={newRetentionPolicy.resource_type}
                    onChange={(e) =>
                      setNewRetentionPolicy({ ...newRetentionPolicy, resource_type: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    required
                  >
                    <option value="users">Users</option>
                    <option value="controls">Controls</option>
                    <option value="evidence">Evidence</option>
                    <option value="reports">Reports</option>
                    <option value="audit_logs">Audit Logs</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'فترة الاحتفاظ (أيام)' : 'Retention Period (Days)'}
                  </label>
                  <input
                    type="number"
                    value={newRetentionPolicy.retention_period_days}
                    onChange={(e) =>
                      setNewRetentionPolicy({
                        ...newRetentionPolicy,
                        retention_period_days: parseInt(e.target.value),
                      })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    required
                    min="1"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {(newRetentionPolicy.retention_period_days / 365).toFixed(1)}{' '}
                    {isArabic ? 'سنة' : 'years'}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'الأساس القانوني (بالإنجليزية)' : 'Legal Basis (English)'}
                  </label>
                  <textarea
                    value={newRetentionPolicy.legal_basis_en}
                    onChange={(e) =>
                      setNewRetentionPolicy({ ...newRetentionPolicy, legal_basis_en: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    rows={3}
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? 'الأساس القانوني (بالعربية)' : 'Legal Basis (Arabic)'}
                  </label>
                  <textarea
                    value={newRetentionPolicy.legal_basis_ar}
                    onChange={(e) =>
                      setNewRetentionPolicy({ ...newRetentionPolicy, legal_basis_ar: e.target.value })
                    }
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    rows={3}
                    required
                  />
                </div>
              </div>

              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={newRetentionPolicy.auto_delete_enabled}
                    onChange={(e) =>
                      setNewRetentionPolicy({ ...newRetentionPolicy, auto_delete_enabled: e.target.checked })
                    }
                    className="w-5 h-5 text-purple-600 rounded"
                  />
                  <span className="ml-3 text-gray-700 font-semibold">
                    {isArabic ? 'تفعيل الحذف التلقائي' : 'Enable Auto-Delete'}
                  </span>
                </label>
                <p className="text-xs text-gray-500 mt-1 ml-8">
                  {isArabic
                    ? 'سيتم حذف البيانات تلقائيًا بعد انتهاء فترة الاحتفاظ'
                    : 'Data will be automatically deleted after retention period expires'}
                </p>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-6 py-3 rounded-lg font-semibold transition shadow disabled:opacity-50"
                >
                  {loading ? (isArabic ? 'جاري الإنشاء...' : 'Creating...') : isArabic ? 'إنشاء' : 'Create Policy'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowRetentionModal(false)}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 px-6 py-3 rounded-lg font-semibold transition"
                >
                  {isArabic ? 'إلغاء' : 'Cancel'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
