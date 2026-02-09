'use client';

import { useTranslations } from 'next-intl';
import useSWR from 'swr';
import apiClient from '@/lib/api-client';
import Link from 'next/link';

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export default function DashboardPage() {
  const t = useTranslations('dashboard');
  const { data, error, isLoading } = useSWR('/api/v1/dashboard', fetcher);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Error loading dashboard data</p>
        </div>
      </div>
    );
  }

  const compliance = data?.compliance_summary;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">{t('title')}</h1>
          <p className="text-gray-600 mt-2">Overview of your compliance posture</p>
        </div>
        <div className="flex gap-3">
          <Link
            href="/search"
            className="px-4 py-2 bg-white border border-gray-300 rounded-lg font-semibold hover:bg-gray-50"
          >
            🔍 Search Controls
          </Link>
          <Link
            href="/reports"
            className="px-4 py-2 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700"
          >
            📊 Generate Report
          </Link>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <MetricCard
          title={t('complianceRate')}
          value={`${compliance?.compliance_rate || 0}%`}
          color="green"
          trend="+2.5%"
        />
        <MetricCard
          title={t('totalControls')}
          value={compliance?.total_controls || 0}
          color="blue"
        />
        <MetricCard
          title={t('pendingEvidence')}
          value={data?.pending_validations || 0}
          color="yellow"
          urgent={true}
        />
        <MetricCard
          title="Non-Compliant"
          value={compliance?.non_compliant || 0}
          color="red"
          urgent={compliance?.non_compliant > 0}
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <QuickAction
          icon="📎"
          title="Upload Evidence"
          description="Add supporting documentation for controls"
          href="/evidence/upload"
          color="blue"
        />
        <QuickAction
          icon="🔍"
          title="View All Controls"
          description="Browse and manage compliance controls"
          href="/controls"
          color="purple"
        />
        <QuickAction
          icon="📈"
          title="Generate Reports"
          description="Create compliance reports for stakeholders"
          href="/reports"
          color="green"
        />
      </div>

      {/* Compliance by Framework */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Compliance by Framework</h2>
        <div className="space-y-4">
          {compliance?.by_framework &&
            Object.entries(compliance.by_framework).map(([framework, stats]: [string, any]) => (
              <div key={framework}>
                <div className="flex justify-between items-center mb-2">
                  <div className="flex items-center gap-3">
                    <span className="font-medium text-lg">{framework}</span>
                    <span className="text-sm text-gray-500">
                      ({stats.compliant}/{stats.total} controls)
                    </span>
                  </div>
                  <span className="text-lg font-bold">
                    {((stats.compliant / stats.total) * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className={`h-3 rounded-full transition-all ${
                      (stats.compliant / stats.total) * 100 >= 80
                        ? 'bg-green-600'
                        : (stats.compliant / stats.total) * 100 >= 60
                        ? 'bg-yellow-600'
                        : 'bg-red-600'
                    }`}
                    style={{ width: `${(stats.compliant / stats.total) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
        </div>
      </div>

      {/* Control Posture */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Control Posture by Domain</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Domain
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Total Controls
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Avg Maturity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Compliant
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {data?.control_posture?.map((posture: any) => (
                <tr key={posture.domain}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {posture.domain}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {posture.total_controls}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {posture.maturity_average.toFixed(1)} / 5.0
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {posture.status_breakdown.compliant}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* High Priority Gaps */}
      {data?.high_priority_gaps && data.high_priority_gaps.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4 text-red-600">{t('highPriorityGaps')}</h2>
          <div className="space-y-3">
            {data.high_priority_gaps.map((gap: any) => (
              <div
                key={gap.control_id}
                className="border-l-4 border-red-500 bg-red-50 p-4 rounded"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <span className="font-mono text-sm text-red-700">{gap.control_id}</span>
                    <p className="text-gray-900 mt-1">{gap.title_en}</p>
                  </div>
                  <span className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded">
                    {gap.framework}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function MetricCard({ 
  title, 
  value, 
  color, 
  trend, 
  urgent 
}: { 
  title: string; 
  value: string | number; 
  color: string;
  trend?: string;
  urgent?: boolean;
}) {
  const colorClasses: Record<string, string> = {
    green: 'bg-green-50 border-green-200 text-green-800',
    blue: 'bg-blue-50 border-blue-200 text-blue-800',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    red: 'bg-red-50 border-red-200 text-red-800',
  };

  return (
    <div className={`rounded-lg border-2 p-6 ${colorClasses[color]} relative overflow-hidden`}>
      {urgent && (
        <div className="absolute top-2 right-2">
          <span className="inline-block w-3 h-3 bg-red-500 rounded-full animate-pulse"></span>
        </div>
      )}
      <p className="text-sm font-medium opacity-80">{title}</p>
      <p className="text-3xl font-bold mt-2">{value}</p>
      {trend && (
        <p className="text-xs mt-2 font-semibold">
          {trend.startsWith('+') ? '↑' : '↓'} {trend} from last month
        </p>
      )}
    </div>
  );
}

function QuickAction({ 
  icon, 
  title, 
  description, 
  href, 
  color 
}: { 
  icon: string; 
  title: string; 
  description: string; 
  href: string; 
  color: string;
}) {
  const colorClasses: Record<string, string> = {
    blue: 'border-blue-200 hover:border-blue-400 hover:bg-blue-50',
    purple: 'border-purple-200 hover:border-purple-400 hover:bg-purple-50',
    green: 'border-green-200 hover:border-green-400 hover:bg-green-50',
  };

  return (
    <Link
      href={href}
      className={`block bg-white border-2 ${colorClasses[color]} rounded-lg p-6 transition-all hover:shadow-lg`}
    >
      <div className="text-4xl mb-3">{icon}</div>
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </Link>
  );
}
