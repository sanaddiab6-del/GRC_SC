'use client';

import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts';

interface ComplianceGaugeProps {
  score: number; // 0-100
  framework: string;
  compliant: number;
  total: number;
  locale?: 'ar' | 'en';
}

export const ComplianceGauge: React.FC<ComplianceGaugeProps> = ({ 
  score, 
  framework, 
  compliant, 
  total,
  locale = 'en' 
}) => {
  const getScoreColor = (score: number): string => {
    if (score >= 90) return '#10b981'; // Green
    if (score >= 75) return '#3b82f6'; // Blue
    if (score >= 60) return '#f59e0b'; // Orange
    return '#ef4444'; // Red
  };

  const getScoreLabel = (score: number, locale: string): string => {
    if (locale === 'ar') {
      if (score >= 90) return 'ممتاز';
      if (score >= 75) return 'جيد';
      if (score >= 60) return 'مقبول';
      return 'يحتاج تحسين';
    }
    if (score >= 90) return 'Excellent';
    if (score >= 75) return 'Good';
    if (score >= 60) return 'Fair';
    return 'Needs Improvement';
  };

  const data = [
    { name: 'Compliant', value: score },
    { name: 'Gap', value: 100 - score }
  ];

  const COLORS = [getScoreColor(score), '#e5e7eb'];

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-gray-900">{framework}</h3>
        <span className={`px-3 py-1 rounded-full text-sm font-semibold text-white`}
          style={{ backgroundColor: getScoreColor(score) }}>
          {getScoreLabel(score, locale)}
        </span>
      </div>

      <div className="relative h-48">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              startAngle={180}
              endAngle={0}
              innerRadius={60}
              outerRadius={80}
              dataKey="value"
              stroke="none"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index]} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        
        {/* Score display in center */}
        <div className="absolute inset-0 flex items-center justify-center" style={{ marginTop: '20px' }}>
          <div className="text-center">
            <div className="text-4xl font-bold" style={{ color: getScoreColor(score) }}>
              {score}%
            </div>
            <div className="text-sm text-gray-600 mt-1">
              {compliant}/{total} {locale === 'ar' ? 'ضوابط' : 'controls'}
            </div>
          </div>
        </div>
      </div>

      {/* Progress breakdown */}
      <div className="mt-4 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">
            {locale === 'ar' ? 'متوافق' : 'Compliant'}
          </span>
          <span className="font-semibold text-green-600">{compliant}</span>
        </div>
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">
            {locale === 'ar' ? 'الفجوات' : 'Gaps'}
          </span>
          <span className="font-semibold text-red-600">{total - compliant}</span>
        </div>
      </div>
    </div>
  );
};
