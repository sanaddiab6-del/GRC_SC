'use client';

import { useTranslations } from 'next-intl';
import { useState } from 'react';
import useSWR from 'swr';
import apiClient from '@/lib/api-client';

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export default function ReportsPage() {
  const t = useTranslations('reports');
  const [selectedReport, setSelectedReport] = useState<string>('compliance');
  const [framework, setFramework] = useState<string>('');
  const [dateRange, setDateRange] = useState({
    start: new Date(new Date().setMonth(new Date().getMonth() - 1)).toISOString().split('T')[0],
    end: new Date().toISOString().split('T')[0],
  });
  const [generating, setGenerating] = useState(false);

  const { data: dashboardData } = useSWR('/api/v1/dashboard', fetcher);

  const reportTypes = [
    {
      id: 'compliance',
      name: 'Compliance Status Report',
      description: 'Comprehensive overview of compliance across all frameworks',
      icon: 'COMP',
    },
    {
      id: 'gaps',
      name: 'Gap Analysis Report',
      description: 'Identify non-compliant controls and remediation actions',
      icon: 'GAP',
    },
    {
      id: 'executive',
      name: 'Executive Summary',
      description: 'High-level summary for leadership and stakeholders',
      icon: 'EXEC',
    },
    {
      id: 'evidence',
      name: 'Evidence Coverage Report',
      description: 'Evidence collection status and missing documentation',
      icon: 'EVD',
    },
    {
      id: 'audit',
      name: 'Audit Trail Report',
      description: 'Complete audit log of all system activities',
      icon: 'AUD',
    },
  ];

  const handleGenerateReport = async () => {
    setGenerating(true);
    try {
      // Example: Download report from backend as blob (PDF/Excel/JSON)
      // Only this request should use responseType: 'blob'
      // Uncomment and adapt when backend endpoint is ready:
      // const response = await apiClient.get(`/api/v1/reports/${selectedReport}`, {
      //   params: { framework, start: dateRange.start, end: dateRange.end },
      //   responseType: 'blob',
      // });
      // const blob = new Blob([response.data], { type: response.headers['content-type'] });
      // const url = URL.createObjectURL(blob);
      // const a = document.createElement('a');
      // a.href = url;
      // a.download = `${selectedReport}-report.${getFileExtension(response.headers['content-type'])}`;
      // document.body.appendChild(a);
      // a.click();
      // document.body.removeChild(a);
      // URL.revokeObjectURL(url);

      // Simulate report generation (JSON download)
      const reportData = {
        type: selectedReport,
        framework,
        dateRange,
        generatedAt: new Date().toISOString(),
        data: dashboardData,
      };
      const blob = new Blob([JSON.stringify(reportData, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedReport}-report-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      alert('Report generated successfully!');
    } catch (error) {
      alert('Failed to generate report');
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Compliance Reports</h1>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Report Types */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-lg font-semibold mb-4">Report Types</h2>
              <div className="space-y-2">
                {reportTypes.map((report) => (
                  <button
                    key={report.id}
                    onClick={() => setSelectedReport(report.id)}
                    className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                      selectedReport === report.id
                        ? 'border-primary-600 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-xs font-semibold tracking-wide text-gray-500">{report.icon}</span>
                      <div>
                        <p className="font-semibold">{report.name}</p>
                        <p className="text-sm text-gray-600 mt-1">{report.description}</p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Report Configuration */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h2 className="text-lg font-semibold mb-6">Report Configuration</h2>

              <div className="space-y-6">
                {/* Framework Filter */}
                <div>
                  <label className="block text-sm font-semibold mb-2">Framework (Optional)</label>
                  <select
                    value={framework}
                    onChange={(e) => setFramework(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                  >
                    <option value="">All Frameworks</option>
                    <option value="ECC">ECC - Essential Cybersecurity Controls</option>
                    <option value="CCC">CCC - Cloud Cybersecurity Controls</option>
                    <option value="PDPL">PDPL - Personal Data Protection Law</option>
                  </select>
                </div>

                {/* Date Range */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold mb-2">Start Date</label>
                    <input
                      type="date"
                      value={dateRange.start}
                      onChange={(e) =>
                        setDateRange({ ...dateRange, start: e.target.value })
                      }
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold mb-2">End Date</label>
                    <input
                      type="date"
                      value={dateRange.end}
                      onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                    />
                  </div>
                </div>

                {/* Export Format */}
                <div>
                  <label className="block text-sm font-semibold mb-2">Export Format</label>
                  <div className="grid grid-cols-3 gap-3">
                    {['PDF', 'Excel', 'JSON'].map((format) => (
                      <button
                        key={format}
                        className="px-4 py-2 border-2 border-gray-300 rounded-lg font-semibold hover:border-primary-600 hover:bg-primary-50"
                      >
                        {format}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Generate Button */}
                <button
                  onClick={handleGenerateReport}
                  disabled={generating}
                  className="w-full bg-gray-900 text-white px-6 py-3 rounded-md font-semibold hover:bg-gray-800 disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  {generating ? 'Generating Report...' : 'Generate & Download Report'}
                </button>
              </div>
            </div>

            {/* Report Preview */}
            {dashboardData && (
              <div className="bg-white rounded-lg shadow-lg p-6">
                <h2 className="text-lg font-semibold mb-4">Preview - Current Compliance Status</h2>

                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <p className="text-3xl font-bold text-green-600">
                      {dashboardData.compliance_summary?.compliance_rate || 0}%
                    </p>
                    <p className="text-sm text-gray-600 mt-1">Overall Compliance</p>
                  </div>
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <p className="text-3xl font-bold text-blue-600">
                      {dashboardData.compliance_summary?.compliant || 0}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">Compliant Controls</p>
                  </div>
                  <div className="text-center p-4 bg-red-50 rounded-lg">
                    <p className="text-3xl font-bold text-red-600">
                      {dashboardData.compliance_summary?.non_compliant || 0}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">Non-Compliant</p>
                  </div>
                </div>

                {/* Framework Breakdown */}
                <div className="space-y-3">
                  <h3 className="font-semibold text-sm text-gray-600">By Framework:</h3>
                  {dashboardData.compliance_summary?.by_framework &&
                    Object.entries(dashboardData.compliance_summary.by_framework).map(
                      ([fw, stats]: [string, any]) => (
                        <div key={fw} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                          <span className="font-medium">{fw}</span>
                          <span className="text-sm text-gray-600">
                            {stats.compliant}/{stats.total} controls (
                            {((stats.compliant / stats.total) * 100).toFixed(1)}%)
                          </span>
                        </div>
                      )
                    )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Recent Reports */}
        <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Reports</h2>
          <div className="text-center text-gray-500 py-8">
            <p>No recent reports. Generate your first report above.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
