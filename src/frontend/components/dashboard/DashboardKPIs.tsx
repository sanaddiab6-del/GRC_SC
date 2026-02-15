'use client';

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface DashboardKPIsProps {
  data: {
    overall_compliance: number;
    total_controls: number;
    compliant_controls: number;
    high_risks: number;
    critical_assets: number;
    open_incidents: number;
    pending_audits: number;
    pdpl_requests: number;
  };
  trends: {
    compliance: number; // % change
    risks: number;
    incidents: number;
  };
  locale?: 'ar' | 'en';
}

export const DashboardKPIs: React.FC<DashboardKPIsProps> = ({ data, trends, locale = 'en' }) => {
  const labels = locale === 'ar'
    ? {
        overallCompliance: 'التوافق الإجمالي',
        totalControls: 'إجمالي الضوابط',
        highRisks: 'مخاطر عالية',
        criticalAssets: 'أصول حرجة',
        openIncidents: 'حوادث مفتوحة',
        pendingAudits: 'عمليات تدقيق معلقة',
        pdplRequests: 'طلبات PDPL',
        thisMonth: 'هذا الشهر'
      }
    : {
        overallCompliance: 'Overall Compliance',
        totalControls: 'Total Controls',
        highRisks: 'High Risks',
        criticalAssets: 'Critical Assets',
        openIncidents: 'Open Incidents',
        pendingAudits: 'Pending Audits',
        pdplRequests: 'PDPL Requests',
        thisMonth: 'This Month'
      };

  const KPICard = ({ 
    title, 
    value, 
    icon, 
    trend, 
    color,
    urgent = false
  }: { 
    title: string; 
    value: number | string; 
    icon: string; 
    trend?: number;
    color: string;
    urgent?: boolean;
  }) => {
    const getTrendIcon = () => {
      if (!trend) return null;
      if (trend > 0) return '↑';
      if (trend < 0) return '↓';
      return '→';
    };

    const getTrendColor = () => {
      if (!trend) return '';
      // For compliance, positive is good
      if (title === labels.overallCompliance && trend > 0) return 'text-green-600';
      if (title === labels.overallCompliance && trend < 0) return 'text-red-600';
      // For risks/incidents, negative is good
      if ((title === labels.highRisks || title === labels.openIncidents) && trend < 0) return 'text-green-600';
      if ((title === labels.highRisks || title === labels.openIncidents) && trend > 0) return 'text-red-600';
      return 'text-gray-600';
    };

    return (
      <div className={`relative bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow border-l-4 ${color}`}>
        {urgent && (
          <div className="absolute top-2 right-2 flex items-center gap-1">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
            </span>
          </div>
        )}
        
        <div className="flex items-start justify-between mb-4">
          <div className={`w-14 h-14 rounded-lg bg-gradient-to-br ${color.replace('border', 'from')} to-gray-100 
            flex items-center justify-center text-3xl shadow-md`}>
            {icon}
          </div>
          {trend !== undefined && (
            <div className={`flex items-center gap-1 font-bold text-sm ${getTrendColor()}`}>
              <span className="text-lg">{getTrendIcon()}</span>
              <span>{Math.abs(trend)}%</span>
            </div>
          )}
        </div>

        <h3 className="text-gray-600 text-sm font-medium mb-2">{title}</h3>
        <div className="flex items-end justify-between">
          <p className="text-4xl font-bold text-gray-900">{value}</p>
          {trend !== undefined && (
            <span className="text-xs text-gray-500">{labels.thisMonth}</span>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <KPICard
        title={labels.overallCompliance}
        value={`${data.overall_compliance}%`}
        icon="CMP"
        trend={trends.compliance}
        color="border-blue-500"
      />
      
      <KPICard
        title={labels.totalControls}
        value={`${data.compliant_controls}/${data.total_controls}`}
        icon="CTRL"
        color="border-green-500"
      />
      
      <KPICard
        title={labels.highRisks}
        value={data.high_risks}
        icon="RSK"
        trend={trends.risks}
        color="border-orange-500"
        urgent={data.high_risks > 10}
      />
      
      <KPICard
        title={labels.openIncidents}
        value={data.open_incidents}
        icon="INC"
        trend={trends.incidents}
        color="border-red-500"
        urgent={data.open_incidents > 0}
      />
      
      <KPICard
        title={labels.criticalAssets}
        value={data.critical_assets}
        icon="AST"
        color="border-purple-500"
      />
      
      <KPICard
        title={labels.pendingAudits}
        value={data.pending_audits}
        icon="AUD"
        color="border-indigo-500"
      />
      
      <KPICard
        title={labels.pdplRequests}
        value={data.pdpl_requests}
        icon="PDPL"
        color="border-teal-500"
      />

      {/* Control Status Distribution - Small Pie Chart */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-gray-900 font-semibold mb-4">
          {locale === 'ar' ? 'توزيع الضوابط' : 'Control Distribution'}
        </h3>
        <ResponsiveContainer width="100%" height={120}>
          <PieChart>
            <Pie
              data={[
                { name: locale === 'ar' ? 'متوافق' : 'Compliant', value: data.compliant_controls },
                { name: locale === 'ar' ? 'غير متوافق' : 'Non-Compliant', value: data.total_controls - data.compliant_controls }
              ]}
              cx="50%"
              cy="50%"
              innerRadius={30}
              outerRadius={50}
              paddingAngle={5}
              dataKey="value"
            >
              <Cell fill="#10b981" />
              <Cell fill="#ef4444" />
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
