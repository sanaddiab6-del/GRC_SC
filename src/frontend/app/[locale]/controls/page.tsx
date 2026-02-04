'use client';

import { useTranslations } from 'next-intl';
import useSWR from 'swr';
import { useState } from 'react';
import apiClient from '@/lib/api-client';

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export default function ControlsPage() {
  const t = useTranslations('controls');
  const [framework, setFramework] = useState<string>('');
  const [status, setStatus] = useState<string>('');

  const queryParams = new URLSearchParams();
  if (framework) queryParams.append('framework', framework);
  if (status) queryParams.append('status', status);

  const { data, error, isLoading } = useSWR(
    `/api/v1/controls?${queryParams.toString()}`,
    fetcher
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-4">{t('title')}</h1>

        {/* Filters */}
        <div className="flex gap-4 mb-6">
          <select
            value={framework}
            onChange={(e) => setFramework(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="">{t('all')} {t('framework')}</option>
            <option value="ECC">ECC</option>
            <option value="CCC">CCC</option>
            <option value="PDPL">PDPL</option>
          </select>

          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
          >
            <option value="">{t('all')} {t('status')}</option>
            <option value="compliant">{t('compliant')}</option>
            <option value="non_compliant">{t('nonCompliant')}</option>
            <option value="in_progress">{t('inProgress')}</option>
            <option value="not_started">{t('notStarted')}</option>
          </select>
        </div>
      </div>

      {/* Controls Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data?.items?.map((control: any) => (
          <ControlCard key={control.id} control={control} t={t} />
        ))}
      </div>

      {/* Pagination Info */}
      {data && (
        <div className="mt-8 text-center text-gray-600">
          Showing {data.items?.length || 0} of {data.total} controls
        </div>
      )}
    </div>
  );
}

function ControlCard({ control, t }: { control: any; t: any }) {
  const statusColors: Record<string, string> = {
    compliant: 'bg-green-100 text-green-800',
    non_compliant: 'bg-red-100 text-red-800',
    in_progress: 'bg-yellow-100 text-yellow-800',
    not_started: 'bg-gray-100 text-gray-800',
    not_applicable: 'bg-gray-100 text-gray-600',
  };

  const priorityColors: Record<string, string> = {
    critical: 'border-red-500',
    high: 'border-orange-500',
    medium: 'border-yellow-500',
    low: 'border-green-500',
  };

  return (
    <div
      className={`bg-white rounded-lg shadow-md p-6 border-l-4 ${
        priorityColors[control.priority] || 'border-gray-300'
      } hover:shadow-lg transition-shadow`}
    >
      <div className="flex justify-between items-start mb-3">
        <span className="font-mono text-sm text-primary-600 font-semibold">
          {control.control_id}
        </span>
        <span className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded">
          {control.framework}
        </span>
      </div>

      <h3 className="font-semibold text-lg mb-2">{control.title_en}</h3>
      <p className="text-sm text-gray-600 mb-4 line-clamp-2">{control.description_en}</p>

      <div className="flex items-center justify-between">
        <span className={`px-3 py-1 text-xs rounded-full ${statusColors[control.status]}`}>
          {control.status.replace('_', ' ')}
        </span>
        <div className="text-sm text-gray-500">
          {t('maturityLevel')}: <span className="font-semibold">{control.maturity_level}/5</span>
        </div>
      </div>

      {control.domain && (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <span className="text-xs text-gray-500">{t('domain')}: </span>
          <span className="text-xs font-medium text-gray-700">{control.domain}</span>
        </div>
      )}
    </div>
  );
}
