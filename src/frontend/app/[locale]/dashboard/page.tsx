'use client';

/**
 * SICO GRC Platform - Professional Enterprise Dashboard
 * Redesigned to match Risk Pilot's professional standards
 */

import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { StatCard, ChartCard, Card, TableCard } from '@/components/ui/Cards';
import { RiskHeatMap } from '@/components/dashboard/RiskHeatMap';
import { ComplianceGauge } from '@/components/dashboard/ComplianceGauge';
import { ComplianceTrendChart } from '@/components/dashboard/ComplianceTrendChart';
import { ActivityTimeline } from '@/components/dashboard/ActivityTimeline';
import { TaskWidget } from '@/components/dashboard/TaskWidget';
import Link from 'next/link';
import {
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';

export default function ProfessionalDashboard() {
  const params = useParams();
  const locale = (params?.locale as 'ar' | 'en') || 'en';
  const [lastUpdatedText, setLastUpdatedText] = useState<string | null>(null);

  useEffect(() => {
    const now = new Date();
    const formatted = locale === 'ar'
      ? `آخر تحديث: ${now.toLocaleTimeString('ar-SA')}`
      : `Last updated: ${now.toLocaleTimeString('en-US')}`;
    setLastUpdatedText(formatted);
  }, [locale]);

  // Demo Data - Professional level
  const kpiData = {
    overallCompliance: { value: 89, change: 5.2, trend: 'up' as const },
    totalControls: { value: 287, change: 12, trend: 'up' as const },
    highRisks: { value: 7, change: -15, trend: 'down' as const },
    openIncidents: { value: 3, change: -33, trend: 'down' as const },
    pendingAudits: { value: 5, change: 0, trend: 'neutral' as const },
    criticalAssets: { value: 89, change: 3, trend: 'up' as const },
  };

  const complianceFrameworks = [
    { framework: 'NCA ECC', score: 91, compliant: 156, total: 171 },
    { framework: 'NCA CCC', score: 86, compliant: 89, total: 103 },
    { framework: 'PDPL', score: 90, compliant: 45, total: 50 },
  ];

  const risks = [
    { id: 'RSK-001', title: locale === 'ar' ? 'ثغرات حرجة غير معالجة' : 'Unpatched Critical Vulnerabilities', likelihood: 4, impact: 5, status: 'open' as const },
    { id: 'RSK-002', title: locale === 'ar' ? 'ضعف في التحكم بالوصول' : 'Insufficient Access Control', likelihood: 3, impact: 5, status: 'mitigated' as const },
    { id: 'RSK-003', title: locale === 'ar' ? 'عدم تطبيق المصادقة الثنائية' : 'Lack of Multi-Factor Auth', likelihood: 4, impact: 4, status: 'open' as const },
    { id: 'RSK-004', title: locale === 'ar' ? 'تصنيف البيانات غير مكتمل' : 'Incomplete Data Classification', likelihood: 3, impact: 4, status: 'open' as const },
    { id: 'RSK-005', title: locale === 'ar' ? 'نسخ احتياطية غير مختبرة' : 'Untested Backup Procedures', likelihood: 2, impact: 5, status: 'mitigated' as const },
  ];

  const activities = [
    {
      id: '1',
      type: 'risk' as const,
      title: locale === 'ar' ? 'تم تحديد مخاطرة جديدة' : 'New Risk Identified',
      description: locale === 'ar' ? 'RSK-015: تشفير البيانات غير كافي' : 'RSK-015: Inadequate data encryption',
      user: 'Ahmed Al-Mansour',
      timestamp: new Date(Date.now() - 300000),
      metadata: { Priority: 'High', Category: 'Security' },
    },
    {
      id: '2',
      type: 'control' as const,
      title: locale === 'ar' ? 'تم تحديث الضابط' : 'Control Updated',
      description: locale === 'ar' ? 'ECC-AC-5: تحديث سياسة التحكم بالوصول' : 'ECC-AC-5: Access control policy updated',
      user: 'Sara Al-Dosari',
      timestamp: new Date(Date.now() - 3600000),
    },
    {
      id: '3',
      type: 'incident' as const,
      title: locale === 'ar' ? 'تم احتواء الحادثة INC-042' : 'Incident INC-042 Contained',
      description: locale === 'ar' ? 'محاولة دخول غير مصرح بها' : 'Unauthorized access attempt',
      user: 'Security Team',
      timestamp: new Date(Date.now() - 7200000),
    },
    {
      id: '4',
      type: 'audit' as const,
      title: locale === 'ar' ? 'اكتمل التدقيق الربعي' : 'Quarterly Audit Completed',
      description: locale === 'ar' ? 'مراجعة ضوابط PDPL - Q1 2026' : 'PDPL Controls Review - Q1 2026',
      user: 'Audit Team',
      timestamp: new Date(Date.now() - 14400000),
      metadata: { Result: '92% Compliant', Issues: '3' },
    },
  ];

  const tasks = [
    {
      id: 'TSK-001',
      title: locale === 'ar' ? 'مراجعة المخاطر الحرجة' : 'Review Critical Risks',
      description: locale === 'ar' ? 'مراجعة وتحديث تقييمات المخاطر الحرجة' : 'Review and update critical risk assessments',
      priority: 'critical' as const,
      status: 'in_progress' as const,
      assignee: 'Ahmed Al-Mansour',
      dueDate: new Date(Date.now() + 86400000),
      controlId: 'ECC-RM-1',
    },
    {
      id: 'TSK-002',
      title: locale === 'ar' ? 'تحديث أدلة الامتثال' : 'Update Compliance Evidence',
      description: locale === 'ar' ? 'رفع أدلة جديدة لضوابط CCC' : 'Upload new evidence for CCC controls',
      priority: 'high' as const,
      status: 'open' as const,
      assignee: 'Sara Al-Dosari',
      dueDate: new Date(Date.now() + 172800000),
      controlId: 'CCC-DG-3',
    },
    {
      id: 'TSK-003',
      title: locale === 'ar' ? 'تحليل الحوادث الشهرية' : 'Monthly Incident Analysis',
      priority: 'medium' as const,
      status: 'pending_review' as const,
      assignee: 'Security Team',
      dueDate: new Date(Date.now() + 259200000),
    },
    {
      id: 'TSK-004',
      title: locale === 'ar' ? 'مراجعة سياسات حماية البيانات' : 'Review Data Protection Policies',
      priority: 'high' as const,
      status: 'open' as const,
      dueDate: new Date(Date.now() + 432000000),
      riskId: 'RSK-004',
    },
  ];

  const controlStatusData = [
    { name: locale === 'ar' ? 'مطبق' : 'Compliant', value: 256, color: '#22c55e' },
    { name: locale === 'ar' ? 'قيد التنفيذ' : 'In Progress', value: 24, color: '#3b82f6' },
    { name: locale === 'ar' ? 'غير مطبق' : 'Non-Compliant', value: 7, color: '#ef4444' },
  ];

  const monthlyTrends = [
    { month: 'Aug', compliance: 78, risks: 15, incidents: 12 },
    { month: 'Sep', compliance: 81, risks: 12, incidents: 9 },
    { month: 'Oct', compliance: 83, risks: 11, incidents: 7 },
    { month: 'Nov', compliance: 85, risks: 10, incidents: 8 },
    { month: 'Dec', compliance: 87, risks: 8, incidents: 5 },
    { month: 'Jan', compliance: 88, risks: 7, incidents: 4 },
    { month: 'Feb', compliance: 89, risks: 7, incidents: 3 },
  ];

  const complianceTrendData = [
    { month: 'Aug 2024', compliance_score: 78, controls_implemented: 210, high_risks: 15 },
    { month: 'Sep 2024', compliance_score: 81, controls_implemented: 225, high_risks: 12 },
    { month: 'Oct 2024', compliance_score: 83, controls_implemented: 240, high_risks: 11 },
    { month: 'Nov 2024', compliance_score: 85, controls_implemented: 255, high_risks: 10 },
    { month: 'Dec 2024', compliance_score: 87, controls_implemented: 265, high_risks: 8 },
    { month: 'Jan 2025', compliance_score: 88, controls_implemented: 275, high_risks: 7 },
    { month: 'Feb 2025', compliance_score: 89, controls_implemented: 287, high_risks: 7 },
  ];

  const riskTable = [
    ['RSK-2024-001', locale === 'ar' ? 'هجوم فدية' : 'Ransomware', 'High', 'Open', 'CISO'],
    ['RSK-2024-004', locale === 'ar' ? 'تهديد داخلي' : 'Insider Threat', 'High', 'Open', 'CISO'],
    ['RSK-2024-007', locale === 'ar' ? 'مخالفة PDPL' : 'PDPL Violation', 'High', 'Open', 'Compliance'],
    ['RSK-2024-003', locale === 'ar' ? 'هجوم DDoS' : 'DDoS Attack', 'Medium', 'Mitigated', 'Security'],
  ];

  return (
    <div className="space-y-6 max-w-[1600px] mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-3 text-xs text-gray-500 mb-2">
            <span>{locale === 'ar' ? 'الرئيسية' : 'Home'}</span>
            <span className="text-gray-300">/</span>
            <span>{locale === 'ar' ? 'لوحة المعلومات' : 'Dashboard'}</span>
          </div>
          <h1 className="text-3xl font-semibold text-gray-900">
            {locale === 'ar' ? 'لوحة المعلومات التنفيذية' : 'Executive Dashboard'}
          </h1>
          <p className="text-sm text-gray-500">
            {lastUpdatedText ?? (locale === 'ar' ? 'آخر تحديث: --' : 'Last updated: --')}
          </p>
        </div>
        <div className="flex gap-3">
          <Link 
            href={`/${locale}/risk-assessment`}
            className="px-4 py-2 bg-white border border-gray-200 text-gray-900 rounded-md text-sm font-medium hover:bg-gray-50 transition-all"
          >
            {locale === 'ar' ? '+ مخاطرة جديدة' : '+ New Risk'}
          </Link>
          <button className="px-4 py-2 bg-gray-900 text-white rounded-md text-sm font-medium hover:bg-gray-800 transition-all">
            {locale === 'ar' ? 'تقرير تنفيذي' : 'Executive Report'}
          </button>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
        <StatCard
          title={locale === 'ar' ? 'الامتثال العام' : 'Overall Compliance'}
          value={`${kpiData.overallCompliance.value}%`}
          change={kpiData.overallCompliance.change}
          trend={kpiData.overallCompliance.trend}
          icon="C"
          color="green"
        />
        <StatCard
          title={locale === 'ar' ? 'إجمالي الضوابط' : 'Total Controls'}
          value={kpiData.totalControls.value}
          change={kpiData.totalControls.change}
          trend={kpiData.totalControls.trend}
          icon="T"
          color="blue"
          subtitle={`${256} ${locale === 'ar' ? 'مطبق' : 'compliant'}`}
        />
        <StatCard
          title={locale === 'ar' ? 'المخاطر العالية' : 'High Risks'}
          value={kpiData.highRisks.value}
          change={kpiData.highRisks.change}
          trend={kpiData.highRisks.trend}
          icon="R"
          color="orange"
        />
        <Link href={`/${locale}/incidents`}>
          <StatCard
            title={locale === 'ar' ? 'الحوادث المفتوحة' : 'Open Incidents'}
            value={kpiData.openIncidents.value}
            change={kpiData.openIncidents.change}
            trend={kpiData.openIncidents.trend}
            icon="I"
            color="red"
          />
        </Link>
        <StatCard
          title={locale === 'ar' ? 'عمليات التدقيق' : 'Pending Audits'}
          value={kpiData.pendingAudits.value}
          change={kpiData.pendingAudits.change}
          trend={kpiData.pendingAudits.trend}
          icon="A"
          color="purple"
        />
        <StatCard
          title={locale === 'ar' ? 'الأصول الحرجة' : 'Critical Assets'}
          value={kpiData.criticalAssets.value}
          change={kpiData.criticalAssets.change}
          trend={kpiData.criticalAssets.trend}
          icon="S"
          color="blue"
        />
      </div>

      {/* Compliance Frameworks + Control Status */}
      <div className="grid lg:grid-cols-4 gap-6">
        {complianceFrameworks.map((framework) => (
          <div key={framework.framework}>
            <ComplianceGauge {...framework} locale={locale} />
          </div>
        ))}
        
        {/* Control Status Distribution */}
        <ChartCard title={locale === 'ar' ? 'توزيع الضوابط' : 'Control Status'}>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={controlStatusData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {controlStatusData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
          <div className="mt-4 space-y-2">
            {controlStatusData.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                  <span className="text-gray-600">{item.name}</span>
                </div>
                <span className="font-semibold">{item.value}</span>
              </div>
            ))}
          </div>
        </ChartCard>
      </div>

      {/* Risk Heat Map + Monthly Trends */}
      <div className="grid lg:grid-cols-2 gap-6">
        <RiskHeatMap risks={risks} locale={locale} />
        
        <ChartCard 
          title={locale === 'ar' ? 'الاتجاهات الشهرية' : 'Monthly Trends'}
          subtitle={locale === 'ar' ? 'آخر 7 أشهر' : 'Last 7 months'}
        >
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={monthlyTrends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="month" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="compliance" 
                stroke="#111827" 
                strokeWidth={2}
                name={locale === 'ar' ? 'الامتثال %' : 'Compliance %'}
              />
              <Line 
                type="monotone" 
                dataKey="risks" 
                stroke="#f97316" 
                strokeWidth={2}
                name={locale === 'ar' ? 'المخاطر' : 'Risks'}
              />
              <Line 
                type="monotone" 
                dataKey="incidents" 
                stroke="#ef4444" 
                strokeWidth={2}
                name={locale === 'ar' ? 'الحوادث' : 'Incidents'}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Risk Register + Activity */}
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <TableCard
            title={locale === 'ar' ? 'أعلى المخاطر' : 'Top Risks'}
            columns={[
              locale === 'ar' ? 'المعرف' : 'ID',
              locale === 'ar' ? 'المخاطرة' : 'Risk',
              locale === 'ar' ? 'الخطورة' : 'Severity',
              locale === 'ar' ? 'الحالة' : 'Status',
              locale === 'ar' ? 'المالك' : 'Owner'
            ]}
            data={riskTable}
            actions={
              <Link href={`/${locale}/risks`} className="text-sm text-gray-600 hover:text-gray-900">
                {locale === 'ar' ? 'عرض السجل' : 'View register'}
              </Link>
            }
          />
        </div>
        <ActivityTimeline items={activities} locale={locale} />
      </div>

      {/* Tasks + Compliance Trends */}
      <div className="grid lg:grid-cols-2 gap-6">
        <TaskWidget tasks={tasks} locale={locale} />
        <ComplianceTrendChart data={complianceTrendData} locale={locale} />
      </div>

      {/* Quick Actions */}
      <div className="grid md:grid-cols-5 gap-6">
        <Link href={`/${locale}/controls`}>
          <Card hover className="p-6 cursor-pointer group">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center text-xs font-semibold text-gray-700">
                CTR
              </div>
              <div>
                <h3 className="font-semibold text-lg text-gray-900">
                  {locale === 'ar' ? 'إدارة الضوابط' : 'Control Management'}
                </h3>
                <p className="text-sm text-gray-600">
                  {locale === 'ar' ? 'مراجعة وتحديث الضوابط' : 'Review and update controls'}
                </p>
              </div>
            </div>
          </Card>
        </Link>

        <Link href={`/${locale}/incidents`}>
          <Card hover className="p-6 cursor-pointer group border-2 border-red-100 bg-red-50/30">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center text-xs font-semibold text-red-700">
                🚨
              </div>
              <div>
                <h3 className="font-semibold text-lg text-gray-900">
                  {locale === 'ar' ? 'إدارة الحوادث' : 'Incident Response'}
                </h3>
                <p className="text-sm text-gray-600">
                  {locale === 'ar' ? 'تتبع وإدارة الحوادث الأمنية' : 'Track and manage security incidents'}
                </p>
              </div>
            </div>
          </Card>
        </Link>

        <Link href={`/${locale}/ai-governance`}>
          <Card hover className="p-6 cursor-pointer group border-2 border-purple-100 bg-purple-50/30">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center text-xs font-semibold text-purple-700">
                🤖
              </div>
              <div>
                <h3 className="font-semibold text-lg text-gray-900">
                  {locale === 'ar' ? 'حوكمة الذكاء الاصطناعي' : 'AI Governance'}
                </h3>
                <p className="text-sm text-gray-600">
                  {locale === 'ar' ? 'إدارة نماذج الذكاء الاصطناعي' : 'Manage AI models and compliance'}
                </p>
              </div>
            </div>
          </Card>
        </Link>

        <Link href={`/${locale}/evidence`}>
          <Card hover className="p-6 cursor-pointer group">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center text-xs font-semibold text-gray-700">
                EVD
              </div>
              <div>
                <h3 className="font-semibold text-lg text-gray-900">
                  {locale === 'ar' ? 'إدارة الأدلة' : 'Evidence Management'}
                </h3>
                <p className="text-sm text-gray-600">
                  {locale === 'ar' ? 'رفع ومراجعة الأدلة' : 'Upload and review evidence'}
                </p>
              </div>
            </div>
          </Card>
        </Link>

        <Link href={`/${locale}/reports`}>
          <Card hover className="p-6 cursor-pointer group">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center text-xs font-semibold text-gray-700">
                RPT
              </div>
              <div>
                <h3 className="font-semibold text-lg text-gray-900">
                  {locale === 'ar' ? 'التقارير والتحليلات' : 'Reports & Analytics'}
                </h3>
                <p className="text-sm text-gray-600">
                  {locale === 'ar' ? 'عرض التقارير المفصلة' : 'View detailed reports'}
                </p>
              </div>
            </div>
          </Card>
        </Link>
      </div>
    </div>
  );
}
