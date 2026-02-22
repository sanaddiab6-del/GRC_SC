'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

interface SecurityIncident {
  id: string;
  timestamp: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  title: string;
  source: string;
  mappedControl: string;
  status: 'pending' | 'mapped' | 'resolved';
  description: string;
}

export default function SOCGRCBridgePage() {
  const params = useParams();
  const locale = params.locale as string;
  const isArabic = locale === 'ar';

  const [incidents, setIncidents] = useState<SecurityIncident[]>([]);
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  useEffect(() => {
    // Mock SOC incidents that map to GRC controls
    setIncidents([
      {
        id: 'INC-2026-001',
        timestamp: '2026-02-22 14:30',
        severity: 'critical',
        title: 'Multiple Failed Login Attempts Detected',
        source: 'SIEM - Azure AD',
        mappedControl: 'ECC-1-1 (Access Control)',
        status: 'mapped',
        description: 'Detected 50+ failed login attempts from IP 192.168.1.100 targeting admin accounts',
      },
      {
        id: 'INC-2026-002',
        timestamp: '2026-02-22 13:15',
        severity: 'high',
        title: 'Unauthorized Data Access Attempt',
        source: 'SIEM - Database Logs',
        mappedControl: 'PDPL-12 (Data Protection)',
        status: 'mapped',
        description: 'User attempted to access PII data without proper authorization',
      },
      {
        id: 'INC-2026-003',
        timestamp: '2026-02-22 12:00',
        severity: 'medium',
        title: 'Suspicious Outbound Traffic',
        source: 'SIEM - Firewall',
        mappedControl: 'CCC-2-3 (Network Security)',
        status: 'pending',
        description: 'Unusual data transfer detected to external IP address',
      },
      {
        id: 'INC-2026-004',
        timestamp: '2026-02-22 10:45',
        severity: 'low',
        title: 'Patch Management Alert',
        source: 'Vulnerability Scanner',
        mappedControl: 'ECC-1-5 (Vulnerability Management)',
        status: 'resolved',
        description: 'Critical security patch available for Windows Server 2019',
      },
    ]);
  }, []);

  const filteredIncidents = incidents.filter(incident => {
    if (filterSeverity !== 'all' && incident.severity !== filterSeverity) return false;
    if (filterStatus !== 'all' && incident.status !== filterStatus) return false;
    return true;
  });

  const severityColors = {
    critical: 'bg-red-100 text-red-800 border-red-600',
    high: 'bg-orange-100 text-orange-800 border-orange-600',
    medium: 'bg-yellow-100 text-yellow-800 border-yellow-600',
    low: 'bg-blue-100 text-blue-800 border-blue-600',
  };

  const statusColors = {
    pending: 'bg-yellow-100 text-yellow-800',
    mapped: 'bg-blue-100 text-blue-800',
    resolved: 'bg-green-100 text-green-800',
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-gray-100 to-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-900 via-blue-900 to-indigo-900 text-white">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold">
                {isArabic ? 'جسر SOC ↔ GRC' : 'SOC ↔ GRC Bridge'}
              </h1>
              <p className="mt-2 text-gray-200">
                {isArabic 
                  ? 'ربط تلقائي بين حوادث مركز العمليات الأمنية وضوابط الامتثال'
                  : 'Automated mapping between Security Operations Center incidents and compliance controls'
                }
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
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg border-l-4 border-red-600 p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">CRITICAL</div>
            <div className="text-3xl font-bold text-red-600 mb-1">
              {incidents.filter(i => i.severity === 'critical').length}
            </div>
            <div className="text-sm text-gray-600">{isArabic ? 'حوادث حرجة' : 'Critical Incidents'}</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg border-l-4 border-orange-600 p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">HIGH</div>
            <div className="text-3xl font-bold text-orange-600 mb-1">
              {incidents.filter(i => i.severity === 'high').length}
            </div>
            <div className="text-sm text-gray-600">{isArabic ? 'حوادث عالية' : 'High Priority'}</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg border-l-4 border-blue-600 p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">MAPPED</div>
            <div className="text-3xl font-bold text-blue-600 mb-1">
              {incidents.filter(i => i.status === 'mapped').length}
            </div>
            <div className="text-sm text-gray-600">{isArabic ? 'مُربوطة بضوابط' : 'Mapped to Controls'}</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg border-l-4 border-green-600 p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">RESOLVED</div>
            <div className="text-3xl font-bold text-green-600 mb-1">
              {incidents.filter(i => i.status === 'resolved').length}
            </div>
            <div className="text-sm text-gray-600">{isArabic ? 'تم الحل' : 'Resolved'}</div>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-lg border p-6 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {isArabic ? 'الخطورة' : 'Severity'}
              </label>
              <select
                value={filterSeverity}
                onChange={(e) => setFilterSeverity(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">{isArabic ? 'الكل' : 'All'}</option>
                <option value="critical">{isArabic ? 'حرج' : 'Critical'}</option>
                <option value="high">{isArabic ? 'عالي' : 'High'}</option>
                <option value="medium">{isArabic ? 'متوسط' : 'Medium'}</option>
                <option value="low">{isArabic ? 'منخفض' : 'Low'}</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {isArabic ? 'الحالة' : 'Status'}
              </label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="all">{isArabic ? 'الكل' : 'All'}</option>
                <option value="pending">{isArabic ? 'معلق' : 'Pending'}</option>
                <option value="mapped">{isArabic ? 'مُربوط' : 'Mapped'}</option>
                <option value="resolved">{isArabic ? 'محلول' : 'Resolved'}</option>
              </select>
            </div>
            <div className="ml-auto">
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2.5 rounded-lg font-semibold transition shadow">
                {isArabic ? '🔄 مزامنة مع SIEM' : '🔄 Sync with SIEM'}
              </button>
            </div>
          </div>
        </div>

        {/* Integration Info */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6 mb-6">
          <div className="flex items-start gap-4">
            <div className="text-4xl">🔗</div>
            <div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">
                {isArabic ? 'التكامل مع مركز العمليات الأمنية (SOC)' : 'Security Operations Center (SOC) Integration'}
              </h3>
              <p className="text-gray-700 mb-3">
                {isArabic
                  ? 'يقوم النظام تلقائياً بربط الحوادث الأمنية من SIEM، جدران الحماية، وأنظمة منع التسلل مع ضوابط الامتثال ذات الصلة (ECC/CCC/PDPL).'
                  : 'System automatically maps security incidents from SIEM, firewalls, and intrusion prevention systems to relevant compliance controls (ECC/CCC/PDPL).'}
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-white rounded-full text-xs font-semibold text-gray-700 border">
                  ✓ Azure Sentinel
                </span>
                <span className="px-3 py-1 bg-white rounded-full text-xs font-semibold text-gray-700 border">
                  ✓ Splunk
                </span>
                <span className="px-3 py-1 bg-white rounded-full text-xs font-semibold text-gray-700 border">
                  ✓ Palo Alto Networks
                </span>
                <span className="px-3 py-1 bg-white rounded-full text-xs font-semibold text-gray-700 border">
                  ✓ Fortinet
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Incidents Table */}
        <div className="bg-white rounded-xl shadow-lg border overflow-hidden">
          <div className="px-6 py-4 border-b bg-gray-50">
            <h2 className="text-xl font-bold text-gray-900">
              {isArabic ? 'الحوادث الأمنية' : 'Security Incidents'}
              <span className="ml-2 text-gray-500 font-normal text-sm">
                ({filteredIncidents.length} {isArabic ? 'حادثة' : 'incidents'})
              </span>
            </h2>
          </div>

          <div className="divide-y">
            {filteredIncidents.length === 0 ? (
              <div className="p-12 text-center text-gray-500">
                <div className="text-6xl mb-4">🔍</div>
                <p className="text-lg font-semibold">{isArabic ? 'لا توجد حوادث' : 'No incidents found'}</p>
                <p className="text-sm mt-2">{isArabic ? 'جرب تغيير الفلاتر' : 'Try adjusting the filters'}</p>
              </div>
            ) : (
              filteredIncidents.map((incident) => (
                <div key={incident.id} className="p-6 hover:bg-gray-50 transition">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-bold text-gray-900">{incident.title}</h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase ${severityColors[incident.severity]}`}>
                          {incident.severity}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${statusColors[incident.status]}`}>
                          {incident.status}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-3">{incident.description}</p>
                      <div className="flex flex-wrap gap-4 text-sm">
                        <span className="text-gray-600">
                          <span className="font-semibold">{isArabic ? 'المعرّف:' : 'ID:'}</span> {incident.id}
                        </span>
                        <span className="text-gray-600">
                          <span className="font-semibold">{isArabic ? 'المصدر:' : 'Source:'}</span> {incident.source}
                        </span>
                        <span className="text-gray-600">
                          <span className="font-semibold">{isArabic ? 'الوقت:' : 'Time:'}</span> {incident.timestamp}
                        </span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between bg-blue-50 rounded-lg p-4 border border-blue-200">
                    <div>
                      <p className="text-xs text-gray-600 mb-1">
                        {isArabic ? '🔗 مُربوط بالضابط:' : '🔗 Mapped to Control:'}
                      </p>
                      <p className="font-semibold text-gray-900">{incident.mappedControl}</p>
                    </div>
                    <div className="flex gap-2">
                      <Link
                        href={`/${locale}/controls`}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition"
                      >
                        {isArabic ? 'عرض الضابط' : 'View Control'}
                      </Link>
                      <button className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-semibold transition">
                        {isArabic ? 'رفع دليل' : 'Upload Evidence'}
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Mapping Statistics */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl shadow-lg border p-6">
            <h3 className="font-semibold text-lg text-gray-900 mb-4">
              {isArabic ? 'الضوابط الأكثر تأثراً' : 'Most Affected Controls'}
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-700">ECC-1-1 (Access Control)</span>
                <span className="font-bold text-red-600">3</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-700">PDPL-12 (Data Protection)</span>
                <span className="font-bold text-orange-600">2</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-700">CCC-2-3 (Network Security)</span>
                <span className="font-bold text-yellow-600">1</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg border p-6">
            <h3 className="font-semibold text-lg text-gray-900 mb-4">
              {isArabic ? 'مصادر الحوادث' : 'Incident Sources'}
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-700">Azure Sentinel SIEM</span>
                <span className="font-bold text-blue-600">45%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-700">Firewall Logs</span>
                <span className="font-bold text-purple-600">30%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-700">IDS/IPS</span>
                <span className="font-bold text-green-600">25%</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg border p-6">
            <h3 className="font-semibold text-lg text-gray-900 mb-4">
              {isArabic ? 'متوسط وقت الاستجابة' : 'Average Response Time'}
            </h3>
            <div className="text-center py-4">
              <div className="text-4xl font-bold text-green-600 mb-2">15 {isArabic ? 'دقيقة' : 'min'}</div>
              <p className="text-sm text-gray-600">{isArabic ? 'من الاكتشاف إلى الربط' : 'From detection to mapping'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
