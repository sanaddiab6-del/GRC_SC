"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface ControlData {
  control_id: string;
  framework: string;
  title_ar: string;
  title_en: string;
  description_ar: string;
  status: string;
  priority: string;
  domain: string;
  domain_ar: string;
}

interface DashboardStats {
  total_controls: number;
  by_framework: {
    ECC: number;
    CCC: number;
    PDPL: number;
  };
  by_status: {
    compliant: number;
    in_progress: number;
    not_started: number;
  };
  compliance_score: number;
}

export default function GRCPlatform() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentControls, setRecentControls] = useState<ControlData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/v1/controls/?limit=100');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const controls: ControlData[] = await response.json();
      
      // Calculate stats
      const dashboardStats: DashboardStats = {
        total_controls: controls.length,
        by_framework: {
          ECC: controls.filter(c => c.framework === 'ECC').length,
          CCC: controls.filter(c => c.framework === 'CCC').length,
          PDPL: controls.filter(c => c.framework === 'PDPL').length,
        },
        by_status: {
          compliant: controls.filter(c => c.status === 'compliant').length,
          in_progress: controls.filter(c => c.status === 'in_progress').length,
          not_started: controls.filter(c => c.status === 'not_started').length,
        },
        compliance_score: Math.round((controls.filter(c => c.status === 'compliant').length / controls.length) * 100)
      };
      
      setStats(dashboardStats);
      setRecentControls(controls.slice(0, 10));
      setLoading(false);
    } catch (err) {
      console.error('Error loading dashboard:', err);
      setError(err instanceof Error ? err.message : 'Failed to load data');
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      compliant: 'bg-green-500',
      in_progress: 'bg-blue-500',
      not_started: 'bg-gray-400',
      non_compliant: 'bg-red-500'
    };
    return styles[status] || styles.not_started;
  };

  const getFrameworkColor = (framework: string) => {
    const colors: Record<string, string> = {
      'ECC': 'from-purple-600 to-purple-800',
      'CCC': 'from-blue-600 to-blue-800',
      'PDPL': 'from-green-600 to-green-800'
    };
    return colors[framework] || 'from-gray-600 to-gray-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500 mb-4"></div>
          <p className="text-white text-xl">جاري تحميل منصة GRC...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="bg-red-900 border border-red-700 rounded-lg p-8 max-w-lg">
          <h2 className="text-2xl font-bold text-red-200 mb-4">خطأ في التحميل</h2>
          <p className="text-red-300 mb-4">{error}</p>
          <button
            onClick={loadDashboardData}
            className="bg-red-700 hover:bg-red-600 text-white px-6 py-2 rounded-lg transition"
          >
            إعادة المحاولة
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white" dir="rtl">
      {/* Header */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-white">منصة SICO GRC</h1>
              <p className="text-gray-400 mt-1">إدارة الامتثال التنظيمي السعودي</p>
            </div>
            <div className="flex gap-3">
              <Link
                href="/ar/grc/controls"
                className="bg-purple-600 hover:bg-purple-700 px-5 py-2.5 rounded-lg font-medium transition shadow-lg"
              >
                إدارة الضوابط
              </Link>
              <Link
                href="/ar/grc/reports"
                className="bg-gray-700 hover:bg-gray-600 px-5 py-2.5 rounded-lg font-medium transition"
              >
                التقارير
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-xl p-6 shadow-2xl">
            <div className="text-purple-200 mb-2">إجمالي الضوابط</div>
            <div className="text-5xl font-bold mb-2">{stats?.total_controls || 0}</div>
            <div className="text-purple-300 text-sm">ضابط تشغيلي</div>
          </div>

          <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-xl p-6 shadow-2xl">
            <div className="text-green-200 mb-2">نسبة الامتثال</div>
            <div className="text-5xl font-bold mb-2">{stats?.compliance_score || 0}%</div>
            <div className="text-green-300 text-sm">{stats?.by_status.compliant || 0} ضابط منفذ</div>
          </div>

          <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-xl p-6 shadow-2xl">
            <div className="text-blue-200 mb-2">قيد التنفيذ</div>
            <div className="text-5xl font-bold mb-2">{stats?.by_status.in_progress || 0}</div>
            <div className="text-blue-300 text-sm">ضوابط نشطة</div>
          </div>

          <div className="bg-gradient-to-br from-orange-600 to-orange-800 rounded-xl p-6 shadow-2xl">
            <div className="text-orange-200 mb-2">لم يبدأ</div>
            <div className="text-5xl font-bold mb-2">{stats?.by_status.not_started || 0}</div>
            <div className="text-orange-300 text-sm">ضوابط معلقة</div>
          </div>
        </div>

        {/* Framework Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {stats && Object.entries(stats.by_framework).map(([framework, count]) => {
            const percentage = Math.round((count / stats.total_controls) * 100);
            return (
              <div key={framework} className="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-xl">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-2xl font-bold">{framework}</h3>
                  <span className={`px-4 py-2 rounded-lg bg-gradient-to-r ${getFrameworkColor(framework)} font-bold text-lg`}>
                    {count}
                  </span>
                </div>
                <div className="mb-3">
                  <div className="flex justify-between text-sm text-gray-400 mb-2">
                    <span>التقدم</span>
                    <span>{percentage}%</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full bg-gradient-to-r ${getFrameworkColor(framework)} transition-all duration-500`}
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>
                <Link
                  href={`/ar/grc/frameworks/${framework.toLowerCase()}`}
                  className="text-purple-400 hover:text-purple-300 text-sm font-medium transition"
                >
                  عرض التفاصيل ←
                </Link>
              </div>
            );
          })}
        </div>

        {/* Recent Controls */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 shadow-xl">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">الضوابط الحديثة</h2>
            <Link
              href="/ar/grc/controls"
              className="text-purple-400 hover:text-purple-300 font-medium transition"
            >
              عرض الكل ←
            </Link>
          </div>
          <div className="space-y-3">
            {recentControls.map(control => (
              <div
                key={control.control_id}
                className="bg-gray-750 rounded-lg p-4 border border-gray-700 hover:border-purple-500 transition"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="font-mono font-bold text-white">{control.control_id}</span>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium bg-gradient-to-r ${getFrameworkColor(control.framework)}`}>
                        {control.framework}
                      </span>
                      <div className={`w-3 h-3 rounded-full ${getStatusBadge(control.status)}`}></div>
                    </div>
                    <h3 className="font-bold text-white mb-1">{control.title_ar}</h3>
                    <p className="text-gray-400 text-sm">{control.domain_ar}</p>
                  </div>
                  <Link
                    href={`/ar/grc/controls/${control.control_id}`}
                    className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-lg text-sm font-medium transition"
                  >
                    عرض
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-8">
          <Link href="/ar/grc/controls" className="bg-gray-800 hover:bg-gray-750 rounded-xl p-6 border border-gray-700 text-center transition shadow-lg">
            <div className="text-xs font-semibold tracking-wide text-gray-400 mb-3">LIB</div>
            <div className="font-bold text-lg">مكتبة الضوابط</div>
            <div className="text-gray-400 text-sm mt-1">{stats?.total_controls || 0} ضابط</div>
          </Link>
          <Link href="/ar/grc/evidence" className="bg-gray-800 hover:bg-gray-750 rounded-xl p-6 border border-gray-700 text-center transition shadow-lg">
            <div className="text-xs font-semibold tracking-wide text-gray-400 mb-3">EVD</div>
            <div className="font-bold text-lg">الأدلة</div>
            <div className="text-gray-400 text-sm mt-1">إدارة الأدلة</div>
          </Link>
          <Link href="/ar/grc/reports" className="bg-gray-800 hover:bg-gray-750 rounded-xl p-6 border border-gray-700 text-center transition shadow-lg">
            <div className="text-xs font-semibold tracking-wide text-gray-400 mb-3">RPT</div>
            <div className="font-bold text-lg">التقارير</div>
            <div className="text-gray-400 text-sm mt-1">تقارير تنفيذية</div>
          </Link>
          <Link href="/ar/grc/ai" className="bg-gray-800 hover:bg-gray-750 rounded-xl p-6 border border-gray-700 text-center transition shadow-lg">
            <div className="text-xs font-semibold tracking-wide text-gray-400 mb-3">AI</div>
            <div className="font-bold text-lg">مساعد AI</div>
            <div className="text-gray-400 text-sm mt-1">استشارات ذكية</div>
          </Link>
        </div>
      </div>
    </div>
  );
}
