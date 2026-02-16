'use client';

/**
 * Professional Arabic Dashboard for SICO GRC Platform
 * Real-time compliance monitoring and analytics
 */

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import {
  StatsCard,
  ComplianceProgress,
  FrameworkCard,
  ControlCard,
  LoadingSpinner,
  Framework,
  Control,
  ComplianceStats
} from '@/components/ui';

export default function ProfessionalDashboard() {
  const t = useTranslations();
  const locale = 'ar'; // Arabic primary

  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<ComplianceStats | null>(null);
  const [controls, setControls] = useState<Control[]>([]);
  const [frameworks, setFrameworks] = useState<Framework[]>([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      // Fetch controls from API
      const controlsRes = await fetch('/api/v1/controls/');
      const controlsData = await controlsRes.json();
      setControls(controlsData);

      // Calculate statistics
      const totalControls = controlsData.length;
      const compliant = controlsData.filter((c: Control) => c.status === 'compliant').length;
      const inProgress = controlsData.filter((c: Control) => c.status === 'in_progress').length;
      const notStarted = controlsData.filter((c: Control) => c.status === 'not_started').length;
      const nonCompliant = controlsData.filter((c: Control) => c.status === 'non_compliant').length;
      const complianceScore = totalControls > 0 ? Math.round((compliant / totalControls) * 100) : 0;

      setStats({
        total_controls: totalControls,
        compliant,
        in_progress: inProgress,
        not_started: notStarted,
        non_compliant: nonCompliant,
        compliance_score: complianceScore
      });

      // Calculate framework-specific data
      const eccControls = controlsData.filter((c: Control) => c.framework === 'ECC');
      const cccControls = controlsData.filter((c: Control) => c.framework === 'CCC');
      const pdplControls = controlsData.filter((c: Control) => c.framework === 'PDPL');

      const calculateFrameworkScore = (controls: Control[]) => {
        if (controls.length === 0) return 0;
        const compliant = controls.filter(c => c.status === 'compliant').length;
        return Math.round((compliant / controls.length) * 100);
      };

      setFrameworks([
        {
          id: 'ECC',
          name_ar: 'الضوابط الأساسية للأمن السيبراني',
          name_en: 'Essential Cybersecurity Controls',
          authority_ar: 'الهيئة الوطنية للأمن السيبراني',
          authority_en: 'National Cybersecurity Authority',
          icon: 'ECC',
          color: 'border-blue-500',
          controls_count: eccControls.length,
          compliance_score: calculateFrameworkScore(eccControls)
        },
        {
          id: 'CCC',
          name_ar: 'ضوابط الأمن السيبراني السحابي',
          name_en: 'Cloud Cybersecurity Controls',
          authority_ar: 'الهيئة الوطنية للأمن السيبراني',
          authority_en: 'National Cybersecurity Authority',
          icon: 'CCC',
          color: 'border-purple-500',
          controls_count: cccControls.length,
          compliance_score: calculateFrameworkScore(cccControls)
        },
        {
          id: 'PDPL',
          name_ar: 'نظام حماية البيانات الشخصية',
          name_en: 'Personal Data Protection Law',
          authority_ar: 'هيئة حماية  البيانات الشخصية',
          authority_en: 'Personal Data Protection Authority',
          icon: 'PDPL',
          color: 'border-green-500',
          controls_count: pdplControls.length,
          compliance_score: calculateFrameworkScore(pdplControls)
        }
      ]);

      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Get critical controls
  const criticalControls = controls
    .filter(c => c.priority === 'critical' && c.status !== 'compliant')
    .slice(0, 6);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6" dir="rtl">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
          لوحة القيادة - الحوكمة والمخاطر والامتثال
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          نظام متكامل للامتثال للأنظمة السعودية (ECC, CCC, PDPL)
        </p>
      </div>

      {/* Key Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatsCard
          title="نسبة الامتثال الإجمالية"
          value={`${stats?.compliance_score || 0}%`}
          icon="CMP"
          color="bg-blue-500/10"
          trend={{ value: 12, isPositive: true }}
          locale={locale}
        />
        <StatsCard
          title="إجمالي الضوابط"
          value={stats?.total_controls || 0}
          icon="CTRL"
          color="bg-purple-500/10"
          locale={locale}
        />
        <StatsCard
          title="الضوابط المتوافقة"
          value={stats?.compliant || 0}
          icon="OK"
          color="bg-green-500/10"
          trend={{ value: 8, isPositive: true }}
          locale={locale}
        />
        <StatsCard
          title="يتطلب اهتمام"
          value={stats?.non_compliant || 0}
          icon="RSK"
          color="bg-red-500/10"
          trend={{ value: 5, isPositive: false }}
          locale={locale}
        />
      </div>

      {/* Compliance Progress by Status */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          توزيع حالة الضوابط
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div>
            <ComplianceProgress
              percentage={stats ? (stats.compliant / stats.total_controls) * 100 : 0}
              label={`متوافق (${stats?.compliant || 0})`}
              color="bg-green-600"
            />
          </div>
          <div>
            <ComplianceProgress
              percentage={stats ? (stats.in_progress / stats.total_controls) * 100 : 0}
              label={`قيد التنفيذ (${stats?.in_progress || 0})`}
              color="bg-blue-600"
            />
          </div>
          <div>
            <ComplianceProgress
              percentage={stats ? (stats.not_started / stats.total_controls) * 100 : 0}
              label={`لم يبدأ (${stats?.not_started || 0})`}
              color="bg-gray-600"
            />
          </div>
          <div>
            <ComplianceProgress
              percentage={stats ? (stats.non_compliant / stats.total_controls) * 100 : 0}
              label={`غير متوافق (${stats?.non_compliant || 0})`}
              color="bg-red-600"
            />
          </div>
        </div>
      </div>

      {/* Regulatory Frameworks */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            الإطار النظامي
          </h2>
          <Link 
            href="/ar/frameworks"
            className="text-blue-600 hover:text-blue-700 font-medium transition-colors"
          >
            عرض الكل ←
          </Link>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {frameworks.map((framework) => (
            <FrameworkCard
              key={framework.id}
              framework={framework}
              locale={locale}
              onClick={() => window.location.href = `/ar/frameworks/${framework.id.toLowerCase()}`}
            />
          ))}
        </div>
      </div>

      {/* Critical Controls Requiring Attention */}
      {criticalControls.length > 0 && (
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              ضوابط حرجة تتطلب اهتمام
            </h2>
            <Link 
              href="/ar/controls?priority=critical&status=non_compliant"
              className="text-red-600 hover:text-red-700 font-medium transition-colors"
            >
              عرض الكل ←
            </Link>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {criticalControls.map((control) => (
              <ControlCard
                key={control.control_id}
                control={control}
                locale={locale}
                onClick={() => window.location.href = `/ar/controls/${control.control_id}`}
              />
            ))}
          </div>
        </div>
      )}

      {/* Recent Activity Timeline */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
          النشاط الأخير
        </h2>
        <div className="space-y-4">
          <ActivityItem
            icon="OK"
            title="تم تحديث ضابط ECC-AC-3"
            description="تم تطبيق المصادقة متعددة العوامل بنجاح"
            time="منذ ساعتين"
            type="success"
          />
          <ActivityItem
            icon="REQ"
            title="طلب مراجعة جديد"
            description="ضابط PDPL-8 يتطلب مراجعة تقييم الأثر"
            time="منذ 4 ساعات"
            type="info"
          />
          <ActivityItem
            icon="ALR"
            title="تنبيه امتثال"
            description="انتهاء صلاحية شهادة التشفير في CCC-CD-1"
            time="منذ يوم واحد"
            type="warning"
          />
          <ActivityItem
            icon="REV"
            title="مراجعة دورية مجدولة"
            description="مراجعة ربع سنوية لضوابط ECC المطلوبة خلال 7 أيام"
            time="منذ يومين"
            type="info"
          />
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
        <QuickActionButton
          icon="NEW"
          label="إضافة دليل جديد"
          href="/ar/evidence/new"
          color="bg-blue-600 hover:bg-blue-700"
        />
        <QuickActionButton
          icon="RPT"
          label="إنشاء تقرير"
          href="/ar/reports/new"
          color="bg-green-600 hover:bg-green-700"
        />
        <QuickActionButton
          icon="RSK"
          label="تقييم المخاطر"
          href="/ar/risk/assessment"
          color="bg-purple-600 hover:bg-purple-700"
        />
        <QuickActionButton
          icon="AI"
          label="استشارة AI"
          href="/ar/search"
          color="bg-indigo-600 hover:bg-indigo-700"
        />
      </div>
    </div>
  );
}

//  Helper Components
const ActivityItem: React.FC<{
  icon: string;
  title: string;
  description: string;
  time: string;
  type: 'success' | 'info' | 'warning' | 'error';
}> = ({ icon, title, description, time, type }) => {
  const typeColors = {
    success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green300',
    info: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
    warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
    error: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
  };

  return (
    <div className="flex items-start gap-4 p-4 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xl ${typeColors[type]}`}>
        {icon}
      </div>
      <div className="flex-1">
        <h4 className="font-semibold text-gray-900 dark:text-white">{title}</h4>
        <p className="text-sm text-gray-600 dark:text-gray-400">{description}</p>
        <span className="text-xs text-gray-500 dark:text-gray-500">{time}</span>
      </div>
    </div>
  );
};

const QuickActionButton: React.FC<{
  icon: string;
  label: string;
  href: string;
  color: string;
}> = ({ icon, label, href, color }) => {
  return (
    <Link href={href} className={`${color} text-white rounded-lg p-4 flex items-center gap-3 transition-all hover:scale-105 shadow-md`}>
      <span className="text-2xl">{icon}</span>
      <span className="font-semibold">{label}</span>
    </Link>
  );
};
