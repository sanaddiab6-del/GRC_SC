'use client';

/**
 * SICO GRC Platform - Professional Enterprise Dashboard
 * 
 * Comprehensive real-time view of organizational compliance posture, risk landscape,
 * and security operations aligned with Saudi regulatory frameworks (NCA ECC/CCC, PDPL).
 * 
 * Features:
 * - Real-time compliance scoring with trend analysis
 * - Interactive risk heat map with drill-down capabilities
 * - Security incident monitoring and SIEM integration
 * - Critical asset inventory with compliance tracking
 * - Multi-framework compliance gauges (ECC, CCC, PDPL)
 * - Control effectiveness analytics by domain
 * - PDPL data subject rights request tracking
 */

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { RiskHeatMap } from '@/components/dashboard/RiskHeatMap';
import { ComplianceGauge } from '@/components/dashboard/ComplianceGauge';
import { ComplianceTrendChart, ControlsByDomain } from '@/components/dashboard/ComplianceTrendChart';
import { SecurityIncidentFeed } from '@/components/dashboard/SecurityIncidentFeed';
import { CriticalAssetsWidget } from '@/components/dashboard/CriticalAssetsWidget';
import { DashboardKPIs } from '@/components/dashboard/DashboardKPIs';
import Link from 'next/link';

export default function EnterpriseDashboard({ 
  params: { locale } 
}: { 
  params: { locale: 'ar' | 'en' } 
}) {
  const t = useTranslations('dashboard');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdatedText, setLastUpdatedText] = useState<string | null>(null);

  // Demo data - In production, this would come from API
  const [dashboardData, setDashboardData] = useState({
    kpis: {
      overall_compliance: 89,
      total_controls: 287,
      compliant_controls: 256,
      high_risks: 7,
      critical_assets: 89,
      open_incidents: 3,
      pending_audits: 5,
      pdpl_requests: 12
    },
    trends: {
      compliance: 5.2,
      risks: -15,
      incidents: -33
    },
    risks: [
      { id: 'RSK-001', title: 'Unpatched Critical Vulnerabilities in Production', likelihood: 4, impact: 5, status: 'open' as const },
      { id: 'RSK-002', title: 'Insufficient Access Control on Database Servers', likelihood: 3, impact: 5, status: 'mitigated' as const },
      { id: 'RSK-003', title: 'Lack of Multi-Factor Authentication', likelihood: 4, impact: 4, status: 'open' as const },
      { id: 'RSK-004', title: 'Incomplete Data Classification', likelihood: 3, impact: 4, status: 'open' as const },
      { id: 'RSK-005', title: 'Inadequate Backup Testing', likelihood: 3, impact: 4, status: 'mitigated' as const },
      { id: 'RSK-006', title: 'SIEM Log Coverage Gaps', likelihood: 2, impact: 4, status: 'open' as const },
      { id: 'RSK-007', title: 'Third-Party Vendor Assessment Overdue', likelihood: 3, impact: 3, status: 'open' as const },
      { id: 'RSK-008', title: 'Encryption Key Rotation Policy', likelihood: 2, impact: 5, status: 'accepted' as const },
      { id: 'RSK-009', title: 'Security Awareness Training Completion', likelihood: 2, impact: 3, status: 'mitigated' as const },
      { id: 'RSK-010', title: 'Network Segmentation Implementation', likelihood: 3, impact: 4, status: 'open' as const },
      { id: 'RSK-011', title: 'Incident Response Plan Testing', likelihood: 2, impact: 4, status: 'open' as const },
      { id: 'RSK-012', title: 'Data Retention Policy Compliance', likelihood: 2, impact: 3, status: 'mitigated' as const },
      { id: 'RSK-013', title: 'Mobile Device Management Gaps', likelihood: 3, impact: 3, status: 'open' as const },
      { id: 'RSK-014', title: 'Cloud Security Misconfiguration', likelihood: 4, impact: 4, status: 'open' as const },
      { id: 'RSK-015', title: 'Supply Chain Security Assessment', likelihood: 2, impact: 4, status: 'accepted' as const }
    ],
    incidents: [
      {
        id: 'INC-2024-001',
        title: 'Suspicious Login Attempts from Foreign IP Addresses',
        severity: 'high' as const,
        status: 'investigating' as const,
        affected_assets: 3,
        detected_at: new Date().toISOString(),
        related_controls: ['ECC-AC-2', 'ECC-AC-7', 'CCC-IAM-3']
      },
      {
        id: 'INC-2024-002',
        title: 'Malware Detection on Endpoint Device',
        severity: 'medium' as const,
        status: 'contained' as const,
        affected_assets: 1,
        detected_at: new Date(Date.now() - 3600000).toISOString(),
        related_controls: ['ECC-SI-3', 'ECC-SI-4']
      },
      {
        id: 'INC-2024-003',
        title: 'Unauthorized Data Access Attempt',
        severity: 'critical' as const,
        status: 'investigating' as const,
        affected_assets: 5,
        detected_at: new Date(Date.now() - 7200000).toISOString(),
        related_controls: ['ECC-AC-3', 'PDPL-15', 'CCC-DAT-2']
      },
      {
        id: 'INC-2024-004',
        title: 'DDoS Attack on Public Web Services',
        severity: 'high' as const,
        status: 'contained' as const,
        affected_assets: 8,
        detected_at: new Date(Date.now() - 14400000).toISOString(),
        related_controls: ['ECC-SC-5', 'CCC-NET-4']
      },
      {
        id: 'INC-2024-005',
        title: 'Insider Threat - Excessive Data Download',
        severity: 'high' as const,
        status: 'resolved' as const,
        affected_assets: 2,
        detected_at: new Date(Date.now() - 86400000).toISOString(),
        related_controls: ['ECC-AU-6', 'PDPL-12']
      }
    ],
    assets: [
      { id: 'AST-001', name: 'Core Banking Application Server', type: 'Server' as const, criticality: 'Critical' as const, compliance_status: 'compliant' as const, last_assessed: '2024-02-10', risk_score: 25 },
      { id: 'AST-002', name: 'Customer Database - Primary', type: 'Database' as const, criticality: 'Critical' as const, compliance_status: 'compliant' as const, last_assessed: '2024-02-09', risk_score: 30 },
      { id: 'AST-003', name: 'Payment Gateway Integration', type: 'Application' as const, criticality: 'Critical' as const, compliance_status: 'partial' as const, last_assessed: '2024-02-08', risk_score: 55 },
      { id: 'AST-004', name: 'Identity Management System', type: 'Application' as const, criticality: 'Critical' as const, compliance_status: 'compliant' as const, last_assessed: '2024-02-11', risk_score: 20 },
      { id: 'AST-005', name: 'Core Network Infrastructure', type: 'Network' as const, criticality: 'Critical' as const, compliance_status: 'non_compliant' as const, last_assessed: '2024-02-07', risk_score: 70 },
      { id: 'AST-006', name: 'SIEM Security Platform', type: 'Application' as const, criticality: 'High' as const, compliance_status: 'compliant' as const, last_assessed: '2024-02-10', risk_score: 35 },
      { id: 'AST-007', name: 'Backup Storage System', type: 'Server' as const, criticality: 'High' as const, compliance_status: 'partial' as const, last_assessed: '2024-02-06', risk_score: 45 },
      { id: 'AST-008', name: 'API Gateway', type: 'Application' as const, criticality: 'High' as const, compliance_status: 'compliant' as const, last_assessed: '2024-02-11', risk_score: 40 }
    ],
    complianceTrend: [
      { month: 'Aug 2024', compliance_score: 75, controls_implemented: 220, high_risks: 18 },
      { month: 'Sep 2024', compliance_score: 78, controls_implemented: 235, high_risks: 15 },
      { month: 'Oct 2024', compliance_score: 82, controls_implemented: 245, high_risks: 12 },
      { month: 'Nov 2024', compliance_score: 85, controls_implemented: 250, high_risks: 10 },
      { month: 'Dec 2024', compliance_score: 86, controls_implemented: 255, high_risks: 9 },
      { month: 'Jan 2025', compliance_score: 87, controls_implemented: 260, high_risks: 8 },
      { month: 'Feb 2025', compliance_score: 89, controls_implemented: 256, high_risks: 7 }
    ],
    controlsByDomain: [
      { domain: 'Access Control', compliant: 35, inProgress: 5, notStarted: 2 },
      { domain: 'Asset Management', compliant: 28, inProgress: 8, notStarted: 4 },
      { domain: 'Risk Assessment', compliant: 20, inProgress: 3, notStarted: 1 },
      { domain: 'Security Operations', compliant: 42, inProgress: 6, notStarted: 3 },
      { domain: 'Incident Response', compliant: 18, inProgress: 4, notStarted: 2 },
      { domain: 'Data Protection', compliant: 32, inProgress: 7, notStarted: 3 },
      { domain: 'Network Security', compliant: 25, inProgress: 5, notStarted: 2 },
      { domain: 'Identity Mgmt', compliant: 22, inProgress: 4, notStarted: 1 },
      { domain: 'Cryptography', compliant: 15, inProgress: 3, notStarted: 2 },
      { domain: 'Audit & Compliance', compliant: 19, inProgress: 5, notStarted: 1 }
    ],
    frameworks: {
      ecc: { score: 91, compliant: 165, total: 181 },
      ccc: { score: 86, compliant: 55, total: 64 },
      pdpl: { score: 90, compliant: 36, total: 40 }
    }
  });

  useEffect(() => {
    const now = new Date();
    setLastUpdatedText(now.toLocaleTimeString());

    // Simulate data loading
    setTimeout(() => {
      setLoading(false);
    }, 800);

    // Auto-refresh every 5 minutes
    const refreshInterval = setInterval(() => {
      handleRefresh();
    }, 300000);

    return () => clearInterval(refreshInterval);
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    // In production: await fetch('/api/v1/dashboard')
    setTimeout(() => {
      setLastUpdatedText(new Date().toLocaleTimeString());
      setRefreshing(false);
    }, 1000);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 font-semibold">
            {locale === 'ar' ? 'جاري تحميل لوحة المعلومات...' : 'Loading Dashboard...'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">
              {locale === 'ar' ? 'لوحة معلومات SICO GRC' : 'SICO GRC Dashboard'}
            </h1>
            <p className="text-gray-600 text-lg">
              {locale === 'ar' 
                ? 'مراقبة شاملة للتوافق مع اللوائح السعودية (ECC، CCC، PDPL)'
                : 'Comprehensive Saudi Regulatory Compliance Monitoring (ECC, CCC, PDPL)'}
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-sm text-gray-500">
                {locale === 'ar' ? 'آخر تحديث' : 'Last Updated'}
              </div>
              <div className="text-sm font-semibold text-gray-900">
                {lastUpdatedText ?? '--:--'}
              </div>
            </div>
            
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="px-4 py-2 bg-white border-2 border-blue-600 text-blue-600 rounded-lg 
                font-semibold hover:bg-blue-600 hover:text-white transition-all disabled:opacity-50
                flex items-center gap-2"
            >
              <span className={refreshing ? 'animate-spin' : ''}>REF</span>
              {locale === 'ar' ? 'تحديث' : 'Refresh'}
            </button>

            <Link
              href={`/${locale}/reports/generate`}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold 
                hover:bg-blue-700 transition-all shadow-lg flex items-center gap-2"
            >
              {locale === 'ar' ? 'إنشاء تقرير' : 'Generate Report'}
            </Link>
          </div>
        </div>

        {/* Quick Stats Banner */}
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-600">
          <div className="grid grid-cols-5 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">{dashboardData.kpis.overall_compliance}%</div>
              <div className="text-sm text-gray-600">
                {locale === 'ar' ? 'المستوى الإجمالي' : 'Overall Score'}
              </div>
            </div>
            <div className="text-center border-l">
              <div className="text-3xl font-bold text-green-600">{dashboardData.frameworks.ecc.score}%</div>
              <div className="text-sm text-gray-600">NCA ECC</div>
            </div>
            <div className="text-center border-l">
              <div className="text-3xl font-bold text-purple-600">{dashboardData.frameworks.ccc.score}%</div>
              <div className="text-sm text-gray-600">NCA CCC</div>
            </div>
            <div className="text-center border-l">
              <div className="text-3xl font-bold text-teal-600">{dashboardData.frameworks.pdpl.score}%</div>
              <div className="text-sm text-gray-600">PDPL</div>
            </div>
            <div className="text-center border-l">
              <div className="text-3xl font-bold text-orange-600">{dashboardData.kpis.high_risks}</div>
              <div className="text-sm text-gray-600">
                {locale === 'ar' ? 'مخاطر عالية' : 'High Risks'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="mb-8">
        <DashboardKPIs 
          data={dashboardData.kpis} 
          trends={dashboardData.trends} 
          locale={locale}
        />
      </div>

      {/* Framework Compliance Gauges */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <ComplianceGauge
          score={dashboardData.frameworks.ecc.score}
          framework="NCA ECC"
          compliant={dashboardData.frameworks.ecc.compliant}
          total={dashboardData.frameworks.ecc.total}
          locale={locale}
        />
        <ComplianceGauge
          score={dashboardData.frameworks.ccc.score}
          framework="NCA CCC"
          compliant={dashboardData.frameworks.ccc.compliant}
          total={dashboardData.frameworks.ccc.total}
          locale={locale}
        />
        <ComplianceGauge
          score={dashboardData.frameworks.pdpl.score}
          framework="PDPL"
          compliant={dashboardData.frameworks.pdpl.compliant}
          total={dashboardData.frameworks.pdpl.total}
          locale={locale}
        />
      </div>

      {/* Risk Heat Map & Security Incidents */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <RiskHeatMap risks={dashboardData.risks} locale={locale} />
        <SecurityIncidentFeed incidents={dashboardData.incidents} locale={locale} />
      </div>

      {/* Compliance Trend & Controls by Domain */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
        <ComplianceTrendChart data={dashboardData.complianceTrend} locale={locale} />
        <ControlsByDomain data={dashboardData.controlsByDomain} locale={locale} />
      </div>

      {/* Critical Assets */}
      <div className="mb-8">
        <CriticalAssetsWidget assets={dashboardData.assets} locale={locale} />
      </div>

      {/* Action Items Footer */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          href={`/${locale}/risks`}
          className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all 
            border-l-4 border-red-500 cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="text-xs font-semibold tracking-wide text-gray-500">RSK</div>
            <div className="text-red-600 font-bold text-2xl">{dashboardData.kpis.high_risks}</div>
          </div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">
            {locale === 'ar' ? 'مراجعة المخاطر العالية' : 'Review High Risks'}
          </h3>
          <p className="text-sm text-gray-600 group-hover:text-gray-900">
            {locale === 'ar' 
              ? 'معالجة المخاطر العالية المفتوحة التي تتطلب تخفيف فوري'
              : 'Address open high risks requiring immediate mitigation'}
          </p>
        </Link>

        <Link
          href={`/${locale}/evidence`}
          className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all 
            border-l-4 border-yellow-500 cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="text-xs font-semibold tracking-wide text-gray-500">EVD</div>
            <div className="text-yellow-600 font-bold text-2xl">
              {dashboardData.kpis.total_controls - dashboardData.kpis.compliant_controls}
            </div>
          </div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">
            {locale === 'ar' ? 'رفع الأدلة المفقودة' : 'Upload Missing Evidence'}
          </h3>
          <p className="text-sm text-gray-600 group-hover:text-gray-900">
            {locale === 'ar' 
              ? 'تقديم الأدلة للضوابط المعلقة لإكمال التوافق'
              : 'Provide evidence for pending controls to complete compliance'}
          </p>
        </Link>

        <Link
          href={`/${locale}/incidents`}
          className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-all 
            border-l-4 border-red-600 cursor-pointer group"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="text-xs font-semibold tracking-wide text-gray-500">INC</div>
            <div className="text-red-600 font-bold text-2xl">{dashboardData.kpis.open_incidents}</div>
          </div>
          <h3 className="text-lg font-bold text-gray-900 mb-2">
            {locale === 'ar' ? 'حل الحوادث المفتوحة' : 'Resolve Open Incidents'}
          </h3>
          <p className="text-sm text-gray-600 group-hover:text-gray-900">
            {locale === 'ar' 
              ? 'التحقيق في الحوادث الأمنية المفتوحة واحتواءها'
              : 'Investigate and contain open security incidents'}
          </p>
        </Link>
      </div>
    </div>
  );
}
