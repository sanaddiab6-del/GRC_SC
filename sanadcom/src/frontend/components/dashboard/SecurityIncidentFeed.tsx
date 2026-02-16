'use client';

import React from 'react';
import { format } from 'date-fns';
import { ar } from 'date-fns/locale';

interface Incident {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'investigating' | 'contained' | 'resolved';
  affected_assets: number;
  detected_at: string;
  related_controls: string[];
}

interface SecurityIncidentFeedProps {
  incidents: Incident[];
  locale?: 'ar' | 'en';
}

export const SecurityIncidentFeed: React.FC<SecurityIncidentFeedProps> = ({ 
  incidents, 
  locale = 'en' 
}) => {
  const labels = locale === 'ar'
    ? {
        title: 'الحوادث الأمنية الأخيرة',
        severity: 'الخطورة',
        status: 'الحالة',
        assets: 'الأصول المتأثرة',
        controls: 'الضوابط ذات الصلة',
        viewAll: 'عرض الكل',
        critical: 'حرج',
        high: 'عالي',
        medium: 'متوسط',
        low: 'منخفض',
        open: 'مفتوح',
        investigating: 'تحت التحقيق',
        contained: 'محتوى',
        resolved: 'محلول'
      }
    : {
        title: 'Recent Security Incidents',
        severity: 'Severity',
        status: 'Status',
        assets: 'Affected Assets',
        controls: 'Related Controls',
        viewAll: 'View All',
        critical: 'Critical',
        high: 'High',
        medium: 'Medium',
        low: 'Low',
        open: 'Open',
        investigating: 'Investigating',
        contained: 'Contained',
        resolved: 'Resolved'
      };

  const severityConfig = {
    critical: { color: 'bg-red-100 text-red-800 border-red-300', label: labels.critical },
    high: { color: 'bg-orange-100 text-orange-800 border-orange-300', label: labels.high },
    medium: { color: 'bg-yellow-100 text-yellow-800 border-yellow-300', label: labels.medium },
    low: { color: 'bg-green-100 text-green-800 border-green-300', label: labels.low }
  };

  const statusConfig = {
    open: { color: 'bg-red-50 text-red-700', label: labels.open },
    investigating: { color: 'bg-blue-50 text-blue-700', label: labels.investigating },
    contained: { color: 'bg-yellow-50 text-yellow-700', label: labels.contained },
    resolved: { color: 'bg-green-50 text-green-700', label: labels.resolved }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">{labels.title}</h2>
        <button className="text-sm text-blue-600 hover:text-blue-800 font-semibold">
          {labels.viewAll} →
        </button>
      </div>

      <div className="space-y-4">
        {incidents.slice(0, 5).map((incident) => {
          const severityStyle = severityConfig[incident.severity];
          const statusStyle = statusConfig[incident.status];
          
          return (
            <div 
              key={incident.id}
              className="border-l-4 border-gray-200 hover:border-blue-500 bg-gray-50 hover:bg-blue-50 
                p-4 rounded-r-lg transition-all cursor-pointer"
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`px-2 py-1 rounded text-xs font-bold border ${severityStyle.color}`}>
                      {severityStyle.label}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${statusStyle.color}`}>
                      {statusStyle.label}
                    </span>
                  </div>
                  <h3 className="font-semibold text-gray-900 mb-1">{incident.title}</h3>
                  <div className="flex items-center gap-4 text-sm text-gray-600">
                    <span>
                      {format(new Date(incident.detected_at), 'PPp', { 
                        locale: locale === 'ar' ? ar : undefined 
                      })}
                    </span>
                    <span>
                      {incident.affected_assets} {labels.assets}
                    </span>
                  </div>
                </div>
              </div>
              
              {incident.related_controls.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <div className="text-xs text-gray-600 mb-1">{labels.controls}:</div>
                  <div className="flex flex-wrap gap-1">
                    {incident.related_controls.map((control) => (
                      <span 
                        key={control}
                        className="px-2 py-1 bg-white border border-gray-300 rounded text-xs font-mono"
                      >
                        {control}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Summary statistics */}
      <div className="mt-6 pt-6 border-t grid grid-cols-4 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600">
            {incidents.filter(i => i.severity === 'critical' && i.status !== 'resolved').length}
          </div>
          <div className="text-xs text-gray-600">{labels.critical}</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-orange-600">
            {incidents.filter(i => i.severity === 'high' && i.status !== 'resolved').length}
          </div>
          <div className="text-xs text-gray-600">{labels.high}</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">
            {incidents.filter(i => i.status === 'investigating').length}
          </div>
          <div className="text-xs text-gray-600">{labels.investigating}</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">
            {incidents.filter(i => i.status === 'resolved').length}
          </div>
          <div className="text-xs text-gray-600">{labels.resolved}</div>
        </div>
      </div>
    </div>
  );
};
