/**
 * Activity Timeline Component
 * Shows recent activity, audit trails, and system events
 */

'use client';

import React from 'react';
import { Card } from '../ui/Cards';

interface TimelineItem {
  id: string;
  type: 'risk' | 'control' | 'incident' | 'audit' | 'user' | 'system';
  title: string;
  description: string;
  user?: string;
  timestamp: Date;
  metadata?: any;
}

interface ActivityTimelineProps {
  items: TimelineItem[];
  locale: 'ar' | 'en';
}

export function ActivityTimeline({ items, locale }: ActivityTimelineProps) {
  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = Math.floor((now.getTime() - date.getTime()) / 1000);
    
    if (diff < 60) return locale === 'ar' ? 'منذ لحظات' : 'Just now';
    if (diff < 3600) return `${Math.floor(diff / 60)}${locale === 'ar' ? 'د' : 'm'}`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}${locale === 'ar' ? 'س' : 'h'}`;
    return `${Math.floor(diff / 86400)}${locale === 'ar' ? 'ي' : 'd'}`;
  };

  const getIcon = (type: string) => {
    const icons = {
      risk: 'R',
      control: 'C',
      incident: 'I',
      audit: 'A',
      user: 'U',
      system: 'S',
    };
    return icons[type as keyof typeof icons] || '.';
  };

  const getColor = (type: string) => {
    const colors = {
      risk: 'bg-orange-500',
      control: 'bg-green-500',
      incident: 'bg-red-500',
      audit: 'bg-blue-500',
      user: 'bg-purple-500',
      system: 'bg-gray-500',
    };
    return colors[type as keyof typeof colors] || 'bg-gray-500';
  };

  return (
    <Card>
      <h3 className="text-lg font-bold text-gray-900 mb-6">
        {locale === 'ar' ? 'النشاط الأخير' : 'Recent Activity'}
      </h3>
      
      <div className="space-y-6">
        {items.map((item, index) => (
          <div key={item.id} className="flex gap-4">
            {/* Timeline Line */}
            <div className="flex flex-col items-center">
              <div className={`w-9 h-9 rounded-full ${getColor(item.type)} flex items-center justify-center text-white shadow-sm`}>
                <span className="text-xs font-semibold">{getIcon(item.type)}</span>
              </div>
              {index < items.length - 1 && (
                <div className="w-px h-full bg-gray-200 mt-2"></div>
              )}
            </div>

            {/* Content */}
            <div className="flex-1 pb-6">
              <div className="flex items-start justify-between mb-1">
                <h4 className="font-semibold text-gray-900">{item.title}</h4>
                <span className="text-xs text-gray-500">{formatTime(item.timestamp)}</span>
              </div>
              <p className="text-sm text-gray-600 mb-2">{item.description}</p>
              {item.user && (
                <p className="text-xs text-gray-500">
                  {locale === 'ar' ? 'بواسطة' : 'by'} <span className="font-medium">{item.user}</span>
                </p>
              )}
              {item.metadata && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {Object.entries(item.metadata).map(([key, value]) => (
                    <span key={key} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-md">
                      {key}: <span className="font-semibold">{String(value)}</span>
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {items.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          <p className="text-sm">{locale === 'ar' ? 'لا توجد أنشطة حديثة' : 'No recent activity'}</p>
        </div>
      )}
    </Card>
  );
}
