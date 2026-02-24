'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ==================== INTERFACES ====================

interface SecurityIncident {
  incident_id: string;
  incident_number: string;
  category: string;
  severity: string;
  status: string;
  title_en: string;
  title_ar: string;
  description_en: string;
  description_ar: string;
  detected_at: string;
  reported_at: string;
  contained_at?: string;
  resolved_at?: string;
  closed_at?: string;
  affected_systems?: any[];
  affected_users_count: number;
  business_impact_en?: string;
  business_impact_ar?: string;
  financial_impact?: number;
  immediate_actions_en?: string;
  immediate_actions_ar?: string;
  containment_actions_en?: string;
  containment_actions_ar?: string;
  eradication_actions_en?: string;
  eradication_actions_ar?: string;
  recovery_actions_en?: string;
  recovery_actions_ar?: string;
  root_cause_en?: string;
  root_cause_ar?: string;
  lessons_learned_en?: string;
  lessons_learned_ar?: string;
  nca_reported: boolean;
  nca_reported_at?: string;
  reported_by: string;
  assigned_to?: string;
  incident_commander?: string;
}

interface Control {
  id: number;
  control_id: string;
  title_en: string;
  title_ar: string;
  framework: string;
}

interface IncidentStats {
  totalIncidents: number;
  openIncidents: number;
  criticalIncidents: number;
  ncaReported: number;
  avgResolutionTime: string;
}

// ==================== MAIN COMPONENT ====================

export default function IncidentResponsePage() {
  const params = useParams();
  const locale = params.locale as string;
  const isArabic = locale === 'ar';

  // State management
  const [incidents, setIncidents] = useState<SecurityIncident[]>([]);
  const [controls, setControls] = useState<Control[]>([]);
  const [stats, setStats] = useState<IncidentStats>({
    totalIncidents: 0,
    openIncidents: 0,
    criticalIncidents: 0,
    ncaReported: 0,
    avgResolutionTime: '0h'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filter state
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showUpdateModal, setShowUpdateModal] = useState(false);
  const [showTimelineModal, setShowTimelineModal] = useState(false);
  const [showLinkControlModal, setShowLinkControlModal] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState<SecurityIncident | null>(null);

  // Form state - Create Incident
  const [newIncident, setNewIncident] = useState({
    category: 'UNAUTHORIZED_ACCESS',
    severity: 'MEDIUM',
    title_en: '',
    title_ar: '',
    description_en: '',
    description_ar: '',
    detected_at: '',
    affected_users_count: 0,
    immediate_actions_en: '',
    immediate_actions_ar: ''
  });

  // Form state - Update Incident
  const [updateData, setUpdateData] = useState({
    status: '',
    severity: '',
    business_impact_en: '',
    business_impact_ar: '',
    financial_impact: 0,
    containment_actions_en: '',
    containment_actions_ar: '',
    eradication_actions_en: '',
    eradication_actions_ar: '',
    recovery_actions_en: '',
    recovery_actions_ar: '',
    root_cause_en: '',
    root_cause_ar: '',
    lessons_learned_en: '',
    lessons_learned_ar: ''
  });

  // Form state - Link Control
  const [selectedControlId, setSelectedControlId] = useState<string>('');

  // ==================== HELPER FUNCTIONS ====================

  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return { Authorization: `Bearer ${token}` };
  };

  const formatDate = (dateString: string) => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return isArabic
      ? date.toLocaleDateString('ar-SA', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' })
      : date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  const getStatusBadgeClass = (status: string) => {
    const statusMap: { [key: string]: string } = {
      'new': 'bg-blue-100 text-blue-800',
      'investigating': 'bg-yellow-100 text-yellow-800',
      'contained': 'bg-orange-100 text-orange-800',
      'eradicated': 'bg-purple-100 text-purple-800',
      'recovered': 'bg-green-100 text-green-800',
      'closed': 'bg-gray-100 text-gray-800'
    };
    return statusMap[status.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  const getSeverityBadgeClass = (severity: string) => {
    const severityMap: { [key: string]: string } = {
      'low': 'bg-green-100 text-green-800',
      'medium': 'bg-yellow-100 text-yellow-800',
      'high': 'bg-orange-100 text-orange-800',
      'critical': 'bg-red-100 text-red-800'
    };
    return severityMap[severity.toLowerCase()] || 'bg-gray-100 text-gray-800';
  };

  const getStatusLabel = (status: string) => {
    const labels: { [key: string]: { en: string; ar: string } } = {
      'new': { en: 'New', ar: 'جديد' },
      'investigating': { en: 'Investigating', ar: 'قيد التحقيق' },
      'contained': { en: 'Contained', ar: 'محتوى' },
      'eradicated': { en: 'Eradicated', ar: 'مستأصل' },
      'recovered': { en: 'Recovered', ar: 'متعافى' },
      'closed': { en: 'Closed', ar: 'مغلق' }
    };
    return isArabic ? labels[status.toLowerCase()]?.ar : labels[status.toLowerCase()]?.en;
  };

  const getSeverityLabel = (severity: string) => {
    const labels: { [key: string]: { en: string; ar: string } } = {
      'low': { en: 'Low', ar: 'منخفض' },
      'medium': { en: 'Medium', ar: 'متوسط' },
      'high': { en: 'High', ar: 'عالي' },
      'critical': { en: 'Critical', ar: 'حرج' }
    };
    return isArabic ? labels[severity.toLowerCase()]?.ar : labels[severity.toLowerCase()]?.en;
  };

  const getCategoryLabel = (category: string) => {
    const labels: { [key: string]: { en: string; ar: string } } = {
      'UNAUTHORIZED_ACCESS': { en: 'Unauthorized Access', ar: 'وصول غير مصرح به' },
      'MALWARE': { en: 'Malware', ar: 'برمجيات خبيثة' },
      'PHISHING': { en: 'Phishing', ar: 'تصيد احتيالي' },
      'DOS_DDOS': { en: 'DoS/DDoS', ar: 'حرمان من الخدمة' },
      'DATA_BREACH': { en: 'Data Breach', ar: 'اختراق البيانات' },
      'INSIDER_THREAT': { en: 'Insider Threat', ar: 'تهديد داخلي' },
      'POLICY_VIOLATION': { en: 'Policy Violation', ar: 'انتهاك السياسة' },
      'SYSTEM_FAILURE': { en: 'System Failure', ar: 'فشل النظام' },
      'OTHER': { en: 'Other', ar: 'أخرى' }
    };
    return isArabic ? labels[category]?.ar : labels[category]?.en;
  };

  // ==================== DATA FETCHING ====================

  const fetchAllData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const headers = getAuthHeaders();

      // Fetch incidents
      const incidentsRes = await axios.get(`${API_BASE}/incidents`, { headers });
      setIncidents(incidentsRes.data);

      // Fetch controls for linking
      const controlsRes = await axios.get(`${API_BASE}/controls?limit=1000`, { headers });
      setControls(controlsRes.data.controls || []);

      // Calculate statistics
      const totalIncidents = incidentsRes.data.length;
      const openIncidents = incidentsRes.data.filter((i: SecurityIncident) => 
        ['new', 'investigating', 'contained'].includes(i.status.toLowerCase())
      ).length;
      const criticalIncidents = incidentsRes.data.filter((i: SecurityIncident) => 
        i.severity.toLowerCase() === 'critical'
      ).length;
      const ncaReported = incidentsRes.data.filter((i: SecurityIncident) => 
        i.nca_reported
      ).length;

      // Calculate average resolution time
      const resolvedIncidents = incidentsRes.data.filter((i: SecurityIncident) => i.resolved_at);
      const avgTime = resolvedIncidents.length > 0
        ? resolvedIncidents.reduce((sum: number, i: SecurityIncident) => {
            const detected = new Date(i.detected_at).getTime();
            const resolved = new Date(i.resolved_at!).getTime();
            return sum + (resolved - detected);
          }, 0) / resolvedIncidents.length
        : 0;
      const avgHours = Math.round(avgTime / (1000 * 60 * 60));

      setStats({
        totalIncidents,
        openIncidents,
        criticalIncidents,
        ncaReported,
        avgResolutionTime: `${avgHours}h`
      });
    } catch (error: any) {
      setError(error.response?.data?.detail || error.message);
      console.error('Failed to fetch incident data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // ==================== HANDLERS ====================

  const handleCreateIncident = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const headers = getAuthHeaders();
      await axios.post(`${API_BASE}/incidents`, newIncident, { headers });
      
      alert(isArabic ? 'تم إنشاء الحادث بنجاح' : 'Incident created successfully');
      setShowCreateModal(false);
      setNewIncident({
        category: 'UNAUTHORIZED_ACCESS',
        severity: 'MEDIUM',
        title_en: '',
        title_ar: '',
        description_en: '',
        description_ar: '',
        detected_at: '',
        affected_users_count: 0,
        immediate_actions_en: '',
        immediate_actions_ar: ''
      });
      await fetchAllData();
    } catch (error: any) {
      alert(isArabic
        ? `فشل إنشاء الحادث: ${error.response?.data?.detail || error.message}`
        : `Failed to create incident: ${error.response?.data?.detail || error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateIncident = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedIncident) return;

    setLoading(true);
    try {
      const headers = getAuthHeaders();
      // Only send non-empty fields
      const payload = Object.fromEntries(
        Object.entries(updateData).filter(([_, v]) => v !== '' && v !== 0)
      );

      await axios.patch(`${API_BASE}/incidents/${selectedIncident.incident_id}`, payload, { headers });
      
      alert(isArabic ? 'تم تحديث الحادث بنجاح' : 'Incident updated successfully');
      setShowUpdateModal(false);
      setSelectedIncident(null);
      await fetchAllData();
    } catch (error: any) {
      alert(isArabic
        ? `فشل تحديث الحادث: ${error.response?.data?.detail || error.message}`
        : `Failed to update incident: ${error.response?.data?.detail || error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReportToNCA = async (incident: SecurityIncident) => {
    if (!confirm(isArabic
      ? 'هل أنت متأكد من الإبلاغ عن هذا الحادث للهيئة الوطنية للأمن السيبراني؟'
      : 'Are you sure you want to report this incident to NCA?'
    )) {
      return;
    }

    setLoading(true);
    try {
      const headers = getAuthHeaders();
      const response = await axios.post(`${API_BASE}/incidents/${incident.incident_id}/report-nca`, {}, { headers });
      
      alert(isArabic ? response.data.message_ar : response.data.message_en);
      await fetchAllData();
    } catch (error: any) {
      alert(isArabic
        ? `فشل الإبلاغ إلى الهيئة: ${error.response?.data?.detail || error.message}`
        : `Failed to report to NCA: ${error.response?.data?.detail || error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

  const openUpdateModal = (incident: SecurityIncident) => {
    setSelectedIncident(incident);
    setUpdateData({
      status: incident.status,
      severity: incident.severity,
      business_impact_en: incident.business_impact_en || '',
      business_impact_ar: incident.business_impact_ar || '',
      financial_impact: incident.financial_impact || 0,
      containment_actions_en: incident.containment_actions_en || '',
      containment_actions_ar: incident.containment_actions_ar || '',
      eradication_actions_en: incident.eradication_actions_en || '',
      eradication_actions_ar: incident.eradication_actions_ar || '',
      recovery_actions_en: incident.recovery_actions_en || '',
      recovery_actions_ar: incident.recovery_actions_ar || '',
      root_cause_en: incident.root_cause_en || '',
      root_cause_ar: incident.root_cause_ar || '',
      lessons_learned_en: incident.lessons_learned_en || '',
      lessons_learned_ar: incident.lessons_learned_ar || ''
    });
    setShowUpdateModal(true);
  };

  const openTimelineModal = (incident: SecurityIncident) => {
    setSelectedIncident(incident);
    setShowTimelineModal(true);
  };

  const openLinkControlModal = (incident: SecurityIncident) => {
    setSelectedIncident(incident);
    setSelectedControlId('');
    setShowLinkControlModal(true);
  };

  // Filter incidents
  const filteredIncidents = incidents.filter(incident => {
    const statusMatch = filterStatus === 'all' || incident.status.toLowerCase() === filterStatus.toLowerCase();
    const severityMatch = filterSeverity === 'all' || incident.severity.toLowerCase() === filterSeverity.toLowerCase();
    return statusMatch && severityMatch;
  });

  // ==================== RENDER ====================

  return (
    <div className={`min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6 ${isArabic ? 'rtl' : 'ltr'}`}>
      {/* Header */}
      <div className="max-w-7xl mx-auto">
        <div className="bg-gradient-to-r from-red-600 to-orange-600 rounded-xl shadow-lg p-8 mb-6 text-white">
          <h1 className="text-4xl font-bold mb-2">
            {isArabic ? '🚨 إدارة الحوادث الأمنية' : '🚨 Incident Response Management'}
          </h1>
          <p className="text-red-100 text-lg">
            {isArabic
              ? 'إدارة وتتبع الحوادث الأمنية - متطلبات الهيئة الوطنية للأمن السيبراني (ECC-IS-5)'
              : 'Security incident management and tracking - NCA ECC-IS-5 compliance'}
          </p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm mb-1">
              {isArabic ? 'إجمالي الحوادث' : 'Total Incidents'}
            </div>
            <div className="text-3xl font-bold text-gray-900">{stats.totalIncidents}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm mb-1">
              {isArabic ? 'الحوادث المفتوحة' : 'Open Incidents'}
            </div>
            <div className="text-3xl font-bold text-blue-600">{stats.openIncidents}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm mb-1">
              {isArabic ? 'حوادث حرجة' : 'Critical Incidents'}
            </div>
            <div className="text-3xl font-bold text-red-600">{stats.criticalIncidents}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm mb-1">
              {isArabic ? 'تم الإبلاغ للهيئة' : 'NCA Reported'}
            </div>
            <div className="text-3xl font-bold text-purple-600">{stats.ncaReported}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm mb-1">
              {isArabic ? 'متوسط وقت الحل' : 'Avg Resolution'}
            </div>
            <div className="text-3xl font-bold text-green-600">{stats.avgResolutionTime}</div>
          </div>
        </div>

        {/* Filters and Create Button */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {isArabic ? 'الحالة' : 'Status'}
              </label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
              >
                <option value="all">{isArabic ? 'الكل' : 'All'}</option>
                <option value="new">{isArabic ? 'جديد' : 'New'}</option>
                <option value="investigating">{isArabic ? 'قيد التحقيق' : 'Investigating'}</option>
                <option value="contained">{isArabic ? 'محتوى' : 'Contained'}</option>
                <option value="eradicated">{isArabic ? 'مستأصل' : 'Eradicated'}</option>
                <option value="recovered">{isArabic ? 'متعافى' : 'Recovered'}</option>
                <option value="closed">{isArabic ? 'مغلق' : 'Closed'}</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {isArabic ? 'الخطورة' : 'Severity'}
              </label>
              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
              >
                <option value="all">{isArabic ? 'الكل' : 'All'}</option>
                <option value="low">{isArabic ? 'منخفض' : 'Low'}</option>
                <option value="medium">{isArabic ? 'متوسط' : 'Medium'}</option>
                <option value="high">{isArabic ? 'عالي' : 'High'}</option>
                <option value="critical">{isArabic ? 'حرج' : 'Critical'}</option>
              </select>
            </div>

            <div className={`${isArabic ? 'mr-auto' : 'ml-auto'}`}>
              <button
                onClick={() => setShowCreateModal(true)}
                className="px-6 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition shadow-md"
              >
                {isArabic ? '➕ إنشاء حادث جديد' : '➕ Create New Incident'}
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Incidents List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            {isArabic ? '📋 قائمة الحوادث الأمنية' : '📋 Security Incidents'}
          </h2>

          {loading && incidents.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              {isArabic ? 'جاري التحميل...' : 'Loading...'}
            </div>
          ) : filteredIncidents.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              {isArabic ? 'لا توجد حوادث' : 'No incidents found'}
            </div>
          ) : (
            <div className="space-y-4">
              {filteredIncidents.map((incident) => (
                <div
                  key={incident.incident_id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-bold text-gray-900">
                          {incident.incident_number}
                        </h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getSeverityBadgeClass(incident.severity)}`}>
                          {getSeverityLabel(incident.severity)}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadgeClass(incident.status)}`}>
                          {getStatusLabel(incident.status)}
                        </span>
                        {incident.nca_reported && (
                          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-800">
                            {isArabic ? '✓ تم الإبلاغ للهيئة' : '✓ NCA Reported'}
                          </span>
                        )}
                      </div>
                      <p className="text-gray-900 font-semibold mb-1">
                        {isArabic ? incident.title_ar : incident.title_en}
                      </p>
                      <p className="text-gray-600 text-sm mb-2">
                        {isArabic ? incident.description_ar : incident.description_en}
                      </p>
                      <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                        <span>
                          {isArabic ? 'الفئة:' : 'Category:'} {getCategoryLabel(incident.category)}
                        </span>
                        <span>
                          {isArabic ? 'تاريخ الاكتشاف:' : 'Detected:'} {formatDate(incident.detected_at)}
                        </span>
                        <span>
                          {isArabic ? 'المستخدمون المتأثرون:' : 'Affected Users:'} {incident.affected_users_count}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-wrap gap-2 pt-3 border-t border-gray-200">
                    <button
                      onClick={() => openUpdateModal(incident)}
                      className="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition"
                    >
                      {isArabic ? '✏️ تحديث' : '✏️ Update'}
                    </button>
                    <button
                      onClick={() => openTimelineModal(incident)}
                      className="px-4 py-2 bg-green-600 text-white text-sm font-semibold rounded-lg hover:bg-green-700 transition"
                    >
                      {isArabic ? '🕐 المخطط الزمني' : '🕐 Timeline'}
                    </button>
                    <button
                      onClick={() => openLinkControlModal(incident)}
                      className="px-4 py-2 bg-purple-600 text-white text-sm font-semibold rounded-lg hover:bg-purple-700 transition"
                    >
                      {isArabic ? '🔗 ربط بضابط' : '🔗 Link Control'}
                    </button>
                    {!incident.nca_reported && (incident.severity === 'high' || incident.severity === 'critical') && (
                      <button
                        onClick={() => handleReportToNCA(incident)}
                        disabled={loading}
                        className="px-4 py-2 bg-red-600 text-white text-sm font-semibold rounded-lg hover:bg-red-700 transition disabled:bg-gray-400"
                      >
                        {isArabic ? '📢 الإبلاغ للهيئة' : '📢 Report to NCA'}
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ==================== CREATE INCIDENT MODAL ==================== */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white p-6 border-b z-10">
              <h3 className="text-2xl font-bold text-gray-900">
                {isArabic ? 'إنشاء حادث أمني جديد' : 'Create New Security Incident'}
              </h3>
            </div>
            <form onSubmit={handleCreateIncident} className="p-6 space-y-4">
              {/* Category and Severity */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isArabic ? 'الفئة *' : 'Category *'}
                  </label>
                  <select
                    value={newIncident.category}
                    onChange={(e) => setNewIncident({ ...newIncident, category: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                    required
                  >
                    <option value="UNAUTHORIZED_ACCESS">{getCategoryLabel('UNAUTHORIZED_ACCESS')}</option>
                    <option value="MALWARE">{getCategoryLabel('MALWARE')}</option>
                    <option value="PHISHING">{getCategoryLabel('PHISHING')}</option>
                    <option value="DOS_DDOS">{getCategoryLabel('DOS_DDOS')}</option>
                    <option value="DATA_BREACH">{getCategoryLabel('DATA_BREACH')}</option>
                    <option value="INSIDER_THREAT">{getCategoryLabel('INSIDER_THREAT')}</option>
                    <option value="POLICY_VIOLATION">{getCategoryLabel('POLICY_VIOLATION')}</option>
                    <option value="SYSTEM_FAILURE">{getCategoryLabel('SYSTEM_FAILURE')}</option>
                    <option value="OTHER">{getCategoryLabel('OTHER')}</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isArabic ? 'الخطورة *' : 'Severity *'}
                  </label>
                  <select
                    value={newIncident.severity}
                    onChange={(e) => setNewIncident({ ...newIncident, severity: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                    required
                  >
                    <option value="LOW">{getSeverityLabel('low')}</option>
                    <option value="MEDIUM">{getSeverityLabel('medium')}</option>
                    <option value="HIGH">{getSeverityLabel('high')}</option>
                    <option value="CRITICAL">{getSeverityLabel('critical')}</option>
                  </select>
                </div>
              </div>

              {/* Title EN */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'العنوان (إنجليزي) *' : 'Title (English) *'}
                </label>
                <input
                  type="text"
                  value={newIncident.title_en}
                  onChange={(e) => setNewIncident({ ...newIncident, title_en: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                  required
                  minLength={5}
                  maxLength={255}
                />
              </div>

              {/* Title AR */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'العنوان (عربي) *' : 'Title (Arabic) *'}
                </label>
                <input
                  type="text"
                  value={newIncident.title_ar}
                  onChange={(e) => setNewIncident({ ...newIncident, title_ar: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                  dir="rtl"
                  required
                  minLength={5}
                  maxLength={255}
                />
              </div>

              {/* Description EN */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'الوصف (إنجليزي) *' : 'Description (English) *'}
                </label>
                <textarea
                  value={newIncident.description_en}
                  onChange={(e) => setNewIncident({ ...newIncident, description_en: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                  rows={3}
                  required
                  minLength={10}
                />
              </div>

              {/* Description AR */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'الوصف (عربي) *' : 'Description (Arabic) *'}
                </label>
                <textarea
                  value={newIncident.description_ar}
                  onChange={(e) => setNewIncident({ ...newIncident, description_ar: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                  rows={3}
                  dir="rtl"
                  required
                  minLength={10}
                />
              </div>

              {/* Detected At */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'تاريخ ووقت الاكتشاف *' : 'Detected Date & Time *'}
                </label>
                <input
                  type="datetime-local"
                  value={newIncident.detected_at}
                  onChange={(e) => setNewIncident({ ...newIncident, detected_at: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                  required
                />
              </div>

              {/* Affected Users Count */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'عدد المستخدمين المتأثرين' : 'Affected Users Count'}
                </label>
                <input
                  type="number"
                  value={newIncident.affected_users_count}
                  onChange={(e) => setNewIncident({ ...newIncident, affected_users_count: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                  min={0}
                />
              </div>

              {/* Immediate Actions EN */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'الإجراءات الفورية (إنجليزي)' : 'Immediate Actions (English)'}
                </label>
                <textarea
                  value={newIncident.immediate_actions_en}
                  onChange={(e) => setNewIncident({ ...newIncident, immediate_actions_en: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                  rows={2}
                />
              </div>

              {/* Immediate Actions AR */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'الإجراءات الفورية (عربي)' : 'Immediate Actions (Arabic)'}
                </label>
                <textarea
                  value={newIncident.immediate_actions_ar}
                  onChange={(e) => setNewIncident({ ...newIncident, immediate_actions_ar: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500"
                  rows={2}
                  dir="rtl"
                />
              </div>

              {/* Buttons */}
              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-6 py-3 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition disabled:bg-gray-400"
                >
                  {loading ? (isArabic ? 'جاري الحفظ...' : 'Saving...') : (isArabic ? 'حفظ' : 'Save')}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-800 font-semibold rounded-lg hover:bg-gray-300 transition"
                >
                  {isArabic ? 'إلغاء' : 'Cancel'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ==================== UPDATE INCIDENT MODAL ==================== */}
      {showUpdateModal && selectedIncident && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white p-6 border-b z-10">
              <h3 className="text-2xl font-bold text-gray-900">
                {isArabic ? `تحديث الحادث: ${selectedIncident.incident_number}` : `Update Incident: ${selectedIncident.incident_number}`}
              </h3>
            </div>
            <form onSubmit={handleUpdateIncident} className="p-6 space-y-4">
              {/* Status and Severity */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isArabic ? 'الحالة' : 'Status'}
                  </label>
                  <select
                    value={updateData.status}
                    onChange={(e) => setUpdateData({ ...updateData, status: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="new">{getStatusLabel('new')}</option>
                    <option value="investigating">{getStatusLabel('investigating')}</option>
                    <option value="contained">{getStatusLabel('contained')}</option>
                    <option value="eradicated">{getStatusLabel('eradicated')}</option>
                    <option value="recovered">{getStatusLabel('recovered')}</option>
                    <option value="closed">{getStatusLabel('closed')}</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isArabic ? 'الخطورة' : 'Severity'}
                  </label>
                  <select
                    value={updateData.severity}
                    onChange={(e) => setUpdateData({ ...updateData, severity: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="low">{getSeverityLabel('low')}</option>
                    <option value="medium">{getSeverityLabel('medium')}</option>
                    <option value="high">{getSeverityLabel('high')}</option>
                    <option value="critical">{getSeverityLabel('critical')}</option>
                  </select>
                </div>
              </div>

              {/* Business Impact */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'الأثر على الأعمال (إنجليزي)' : 'Business Impact (English)'}
                </label>
                <textarea
                  value={updateData.business_impact_en}
                  onChange={(e) => setUpdateData({ ...updateData, business_impact_en: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={2}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'الأثر على الأعمال (عربي)' : 'Business Impact (Arabic)'}
                </label>
                <textarea
                  value={updateData.business_impact_ar}
                  onChange={(e) => setUpdateData({ ...updateData, business_impact_ar: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={2}
                  dir="rtl"
                />
              </div>

              {/* Financial Impact */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'الأثر المالي (ريال سعودي)' : 'Financial Impact (SAR)'}
                </label>
                <input
                  type="number"
                  value={updateData.financial_impact}
                  onChange={(e) => setUpdateData({ ...updateData, financial_impact: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  min={0}
                />
              </div>

              {/* Containment Actions */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'إجراءات الاحتواء (إنجليزي)' : 'Containment Actions (English)'}
                </label>
                <textarea
                  value={updateData.containment_actions_en}
                  onChange={(e) => setUpdateData({ ...updateData, containment_actions_en: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={2}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'إجراءات الاحتواء (عربي)' : 'Containment Actions (Arabic)'}
                </label>
                <textarea
                  value={updateData.containment_actions_ar}
                  onChange={(e) => setUpdateData({ ...updateData, containment_actions_ar: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={2}
                  dir="rtl"
                />
              </div>

              {/* Root Cause */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'السبب الجذري (إنجليزي)' : 'Root Cause (English)'}
                </label>
                <textarea
                  value={updateData.root_cause_en}
                  onChange={(e) => setUpdateData({ ...updateData, root_cause_en: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={2}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'السبب الجذري (عربي)' : 'Root Cause (Arabic)'}
                </label>
                <textarea
                  value={updateData.root_cause_ar}
                  onChange={(e) => setUpdateData({ ...updateData, root_cause_ar: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={2}
                  dir="rtl"
                />
              </div>

              {/* Lessons Learned */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'الدروس المستفادة (إنجليزي)' : 'Lessons Learned (English)'}
                </label>
                <textarea
                  value={updateData.lessons_learned_en}
                  onChange={(e) => setUpdateData({ ...updateData, lessons_learned_en: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={2}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'الدروس المستفادة (عربي)' : 'Lessons Learned (Arabic)'}
                </label>
                <textarea
                  value={updateData.lessons_learned_ar}
                  onChange={(e) => setUpdateData({ ...updateData, lessons_learned_ar: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={2}
                  dir="rtl"
                />
              </div>

              {/* Buttons */}
              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400"
                >
                  {loading ? (isArabic ? 'جاري التحديث...' : 'Updating...') : (isArabic ? 'تحديث' : 'Update')}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowUpdateModal(false);
                    setSelectedIncident(null);
                  }}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-800 font-semibold rounded-lg hover:bg-gray-300 transition"
                >
                  {isArabic ? 'إلغاء' : 'Cancel'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ==================== TIMELINE MODAL ==================== */}
      {showTimelineModal && selectedIncident && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white p-6 border-b z-10">
              <h3 className="text-2xl font-bold text-gray-900">
                {isArabic ? `المخطط الزمني: ${selectedIncident.incident_number}` : `Timeline: ${selectedIncident.incident_number}`}
              </h3>
            </div>
            <div className="p-6">
              {/* Timeline */}
              <div className="space-y-4">
                {/* Detected */}
                <div className="flex items-start gap-4">
                  <div className="w-32 text-sm font-semibold text-gray-600 flex-shrink-0">
                    {isArabic ? 'تم الاكتشاف' : 'Detected'}
                  </div>
                  <div className="flex-1">
                    <div className="text-gray-900">{formatDate(selectedIncident.detected_at)}</div>
                  </div>
                  <div className="w-3 h-3 rounded-full bg-blue-500 flex-shrink-0 mt-1" />
                </div>

                {/* Reported */}
                <div className="flex items-start gap-4">
                  <div className="w-32 text-sm font-semibold text-gray-600 flex-shrink-0">
                    {isArabic ? 'تم الإبلاغ' : 'Reported'}
                  </div>
                  <div className="flex-1">
                    <div className="text-gray-900">{formatDate(selectedIncident.reported_at)}</div>
                  </div>
                  <div className="w-3 h-3 rounded-full bg-green-500 flex-shrink-0 mt-1" />
                </div>

                {/* Contained */}
                {selectedIncident.contained_at && (
                  <div className="flex items-start gap-4">
                    <div className="w-32 text-sm font-semibold text-gray-600 flex-shrink-0">
                      {isArabic ? 'تم الاحتواء' : 'Contained'}
                    </div>
                    <div className="flex-1">
                      <div className="text-gray-900">{formatDate(selectedIncident.contained_at)}</div>
                    </div>
                    <div className="w-3 h-3 rounded-full bg-orange-500 flex-shrink-0 mt-1" />
                  </div>
                )}

                {/* Resolved */}
                {selectedIncident.resolved_at && (
                  <div className="flex items-start gap-4">
                    <div className="w-32 text-sm font-semibold text-gray-600 flex-shrink-0">
                      {isArabic ? 'تم الحل' : 'Resolved'}
                    </div>
                    <div className="flex-1">
                      <div className="text-gray-900">{formatDate(selectedIncident.resolved_at)}</div>
                    </div>
                    <div className="w-3 h-3 rounded-full bg-purple-500 flex-shrink-0 mt-1" />
                  </div>
                )}

                {/* Closed */}
                {selectedIncident.closed_at && (
                  <div className="flex items-start gap-4">
                    <div className="w-32 text-sm font-semibold text-gray-600 flex-shrink-0">
                      {isArabic ? 'تم الإغلاق' : 'Closed'}
                    </div>
                    <div className="flex-1">
                      <div className="text-gray-900">{formatDate(selectedIncident.closed_at)}</div>
                    </div>
                    <div className="w-3 h-3 rounded-full bg-gray-500 flex-shrink-0 mt-1" />
                  </div>
                )}

                {/* NCA Reported */}
                {selectedIncident.nca_reported_at && (
                  <div className="flex items-start gap-4">
                    <div className="w-32 text-sm font-semibold text-gray-600 flex-shrink-0">
                      {isArabic ? 'تم الإبلاغ للهيئة' : 'NCA Reported'}
                    </div>
                    <div className="flex-1">
                      <div className="text-gray-900">{formatDate(selectedIncident.nca_reported_at)}</div>
                    </div>
                    <div className="w-3 h-3 rounded-full bg-red-500 flex-shrink-0 mt-1" />
                  </div>
                )}
              </div>

              {/* Close Button */}
              <div className="pt-6">
                <button
                  onClick={() => {
                    setShowTimelineModal(false);
                    setSelectedIncident(null);
                  }}
                  className="w-full px-6 py-3 bg-gray-200 text-gray-800 font-semibold rounded-lg hover:bg-gray-300 transition"
                >
                  {isArabic ? 'إغلاق' : 'Close'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ==================== LINK CONTROL MODAL ==================== */}
      {showLinkControlModal && selectedIncident && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white p-6 border-b z-10">
              <h3 className="text-2xl font-bold text-gray-900">
                {isArabic ? `ربط الحادث بضابط: ${selectedIncident.incident_number}` : `Link Incident to Control: ${selectedIncident.incident_number}`}
              </h3>
            </div>
            <div className="p-6">
              <p className="text-gray-600 mb-4">
                {isArabic
                  ? 'اربط هذا الحادث بضابط أمن لتتبع الامتثال وتحسين الضوابط.'
                  : 'Link this incident to a security control for compliance tracking and control improvements.'}
              </p>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {isArabic ? 'اختر الضابط' : 'Select Control'}
                </label>
                <select
                  value={selectedControlId}
                  onChange={(e) => setSelectedControlId(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 mb-4"
                >
                  <option value="">{isArabic ? 'اختر ضابط...' : 'Select a control...'}</option>
                  {controls.map((control) => (
                    <option key={control.id} value={control.control_id}>
                      {control.control_id} - {isArabic ? control.title_ar : control.title_en}
                    </option>
                  ))}
                </select>
              </div>

              {/* Note: This is UI-only for now, backend integration would require adding control_id to incident model */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <p className="text-sm text-blue-800">
                  {isArabic
                    ? '💡 ملاحظة: ميزة ربط الضوابط قيد التطوير. ستتم إضافة ربط البيانات الكامل قريباً.'
                    : '💡 Note: Control linking feature is under development. Full data integration coming soon.'}
                </p>
              </div>

              {/* Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    if (selectedControlId) {
                      alert(isArabic
                        ? `تم ربط الحادث بالضابط ${selectedControlId}`
                        : `Incident linked to control ${selectedControlId}`
                      );
                      setShowLinkControlModal(false);
                      setSelectedIncident(null);
                    }
                  }}
                  disabled={!selectedControlId}
                  className="flex-1 px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition disabled:bg-gray-400"
                >
                  {isArabic ? 'ربط' : 'Link'}
                </button>
                <button
                  onClick={() => {
                    setShowLinkControlModal(false);
                    setSelectedIncident(null);
                  }}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-800 font-semibold rounded-lg hover:bg-gray-300 transition"
                >
                  {isArabic ? 'إلغاء' : 'Cancel'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
