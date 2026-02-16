'use client';

import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Area,
  AreaChart
} from 'recharts';

interface TrendDataPoint {
  month: string;
  compliance_score: number;
  controls_implemented: number;
  high_risks: number;
}

interface ComplianceTrendChartProps {
  data: TrendDataPoint[];
  locale?: 'ar' | 'en';
}

export const ComplianceTrendChart: React.FC<ComplianceTrendChartProps> = ({ 
  data, 
  locale = 'en' 
}) => {
  const labels = locale === 'ar'
    ? {
        title: 'اتجاه التوافق',
        compliance: 'درجة التوافق',
        controls: 'الضوابط المنفذة',
        risks: 'المخاطر العالية'
      }
    : {
        title: 'Compliance Trend',
        compliance: 'Compliance Score',
        controls: 'Controls Implemented',
        risks: 'High Risks'
      };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-900">{labels.title}</h2>
      
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorCompliance" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorControls" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="month" 
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <YAxis 
              stroke="#6b7280"
              style={{ fontSize: '12px' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1f2937', 
                border: 'none',
                borderRadius: '8px',
                color: '#fff'
              }}
            />
            <Legend />
            <Area
              type="monotone"
              dataKey="compliance_score"
              name={labels.compliance}
              stroke="#3b82f6"
              fillOpacity={1}
              fill="url(#colorCompliance)"
            />
            <Area
              type="monotone"
              dataKey="controls_implemented"
              name={labels.controls}
              stroke="#10b981"
              fillOpacity={1}
              fill="url(#colorControls)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

interface ControlsByDomainProps {
  data: Array<{
    domain: string;
    compliant: number;
    inProgress: number;
    notStarted: number;
  }>;
  locale?: 'ar' | 'en';
}

export const ControlsByDomain: React.FC<ControlsByDomainProps> = ({ data, locale = 'en' }) => {
  const labels = locale === 'ar'
    ? {
        title: 'الضوابط حسب النطاق',
        compliant: 'متوافق',
        inProgress: 'قيد التنفيذ',
        notStarted: 'لم يبدأ'
      }
    : {
        title: 'Controls by Domain',
        compliant: 'Compliant',
        inProgress: 'In Progress',
        notStarted: 'Not Started'
      };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-900">{labels.title}</h2>
      
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis 
              dataKey="domain" 
              stroke="#6b7280"
              style={{ fontSize: '11px' }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1f2937', 
                border: 'none',
                borderRadius: '8px',
                color: '#fff'
              }}
            />
            <Legend />
            <Bar 
              dataKey="compliant" 
              name={labels.compliant} 
              stackId="a" 
              fill="#10b981" 
            />
            <Bar 
              dataKey="inProgress" 
              name={labels.inProgress} 
              stackId="a" 
              fill="#3b82f6" 
            />
            <Bar 
              dataKey="notStarted" 
              name={labels.notStarted} 
              stackId="a" 
              fill="#9ca3af" 
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
