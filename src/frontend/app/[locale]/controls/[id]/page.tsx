'use client';

import { useTranslations } from 'next-intl';
import useSWR from 'swr';
import { useState } from 'react';
import apiClient from '@/lib/api-client';
import Link from 'next/link';
import { useParams } from 'next/navigation';

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export default function ControlDetailPage() {
  const params = useParams();
  const controlId = params.id as string;
  const t = useTranslations('controlDetail');
  const [activeTab, setActiveTab] = useState<'overview' | 'evidence' | 'history'>('overview');

  const { data: control, error, isLoading } = useSWR(
    `/api/v1/controls/${controlId}`,
    fetcher
  );

  const { data: evidenceList } = useSWR(
    activeTab === 'evidence' ? `/api/v1/evidence?control_id=${controlId}` : null,
    fetcher
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error || !control) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">Error loading control details</p>
        </div>
      </div>
    );
  }

  const statusColors: Record<string, string> = {
    compliant: 'bg-green-100 text-green-800',
    non_compliant: 'bg-red-100 text-red-800',
    in_progress: 'bg-yellow-100 text-yellow-800',
    not_started: 'bg-gray-100 text-gray-800',
    not_applicable: 'bg-gray-100 text-gray-600',
  };

  const priorityColors: Record<string, string> = {
    critical: 'bg-red-100 text-red-800',
    high: 'bg-orange-100 text-orange-800',
    medium: 'bg-yellow-100 text-yellow-800',
    low: 'bg-green-100 text-green-800',
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      {/* Header */}
      <div className="mb-6">
        <Link
          href="/controls"
          className="text-primary-600 hover:text-primary-700 flex items-center gap-2 mb-4"
        >
          ← Back to Controls
        </Link>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex justify-between items-start mb-4">
            <div>
              <span className="text-sm font-semibold text-gray-500">{control.control_id}</span>
              <h1 className="text-3xl font-bold mt-1">{control.title_en}</h1>
              {control.title_ar && (
                <p className="text-xl text-gray-600 mt-2" dir="rtl">{control.title_ar}</p>
              )}
            </div>
            <div className="flex gap-3">
              <span className={`px-4 py-2 rounded-full font-semibold ${statusColors[control.status]}`}>
                {control.status?.replace('_', ' ').toUpperCase()}
              </span>
              <span className={`px-4 py-2 rounded-full font-semibold ${priorityColors[control.priority]}`}>
                {control.priority?.toUpperCase()} PRIORITY
              </span>
            </div>
          </div>

          <div className="grid grid-cols-4 gap-4 mt-6 pt-6 border-t">
            <div>
              <p className="text-sm text-gray-500">Framework</p>
              <p className="font-semibold text-lg">{control.framework}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Domain</p>
              <p className="font-semibold text-lg">{control.domain}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Maturity Level</p>
              <p className="font-semibold text-lg">{control.maturity_level || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-500">Last Updated</p>
              <p className="font-semibold text-lg">
                {new Date(control.updated_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="border-b border-gray-200">
          <nav className="flex">
            <button
              onClick={() => setActiveTab('overview')}
              className={`px-6 py-4 font-semibold ${
                activeTab === 'overview'
                  ? 'border-b-2 border-primary-600 text-primary-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('evidence')}
              className={`px-6 py-4 font-semibold ${
                activeTab === 'evidence'
                  ? 'border-b-2 border-primary-600 text-primary-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Evidence ({evidenceList?.items?.length || 0})
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`px-6 py-4 font-semibold ${
                activeTab === 'history'
                  ? 'border-b-2 border-primary-600 text-primary-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              History
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <OverviewTab control={control} />
          )}
          {activeTab === 'evidence' && (
            <EvidenceTab controlId={controlId} evidenceList={evidenceList} />
          )}
          {activeTab === 'history' && (
            <HistoryTab control={control} />
          )}
        </div>
      </div>
    </div>
  );
}

function OverviewTab({ control }: { control: any }) {
  return (
    <div className="space-y-6">
      {/* Description */}
      <div>
        <h3 className="text-lg font-semibold mb-3">Description</h3>
        <p className="text-gray-700 leading-relaxed">{control.description_en}</p>
        {control.description_ar && (
          <p className="text-gray-700 leading-relaxed mt-3" dir="rtl">
            {control.description_ar}
          </p>
        )}
      </div>

      {/* Implementation Guidance */}
      {control.implementation_guidance && (
        <div>
          <h3 className="text-lg font-semibold mb-3">Implementation Guidance</h3>
          <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
            <p className="text-gray-700">{control.implementation_guidance}</p>
          </div>
        </div>
      )}

      {/* Related Controls */}
      {control.related_controls && control.related_controls.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-3">Related Controls</h3>
          <div className="flex flex-wrap gap-2">
            {control.related_controls.map((relatedId: string) => (
              <Link
                key={relatedId}
                href={`/controls/${relatedId}`}
                className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium text-sm"
              >
                {relatedId}
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Testing Procedure */}
      {control.testing_procedure && (
        <div>
          <h3 className="text-lg font-semibold mb-3">Testing Procedure</h3>
          <ol className="list-decimal list-inside space-y-2 text-gray-700">
            {control.testing_procedure.split('\n').map((step: string, idx: number) => (
              <li key={idx}>{step}</li>
            ))}
          </ol>
        </div>
      )}

      {/* Metadata */}
      <div className="grid grid-cols-2 gap-4 pt-6 border-t">
        <div>
          <p className="text-sm text-gray-500">Created At</p>
          <p className="font-medium">
            {new Date(control.created_at).toLocaleString()}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Last Updated</p>
          <p className="font-medium">
            {new Date(control.updated_at).toLocaleString()}
          </p>
        </div>
      </div>
    </div>
  );
}

function EvidenceTab({ controlId, evidenceList }: { controlId: string; evidenceList: any }) {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold">Evidence Documents</h3>
        <Link
          href={`/evidence/upload?control_id=${controlId}`}
          className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-semibold"
        >
          + Upload Evidence
        </Link>
      </div>

      {evidenceList?.items?.length > 0 ? (
        <div className="space-y-3">
          {evidenceList.items.map((evidence: any) => (
            <div
              key={evidence.id}
              className="border rounded-lg p-4 hover:shadow-md transition-shadow"
            >
              <div className="flex justify-between items-start">
                <div>
                  <h4 className="font-semibold text-lg">{evidence.title}</h4>
                  {evidence.description && (
                    <p className="text-gray-600 mt-1">{evidence.description}</p>
                  )}
                  <div className="flex gap-4 mt-3 text-sm text-gray-500">
                    <span>Type: {evidence.evidence_type}</span>
                    <span>
                      Collected: {new Date(evidence.collection_date).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    evidence.validation_status === 'approved'
                      ? 'bg-green-100 text-green-800'
                      : evidence.validation_status === 'rejected'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {evidence.validation_status}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12 text-gray-500">
          <p className="text-lg mb-2">No evidence uploaded yet</p>
          <p className="text-sm">Upload evidence to demonstrate compliance with this control</p>
        </div>
      )}
    </div>
  );
}

function HistoryTab({ control }: { control: any }) {
  // Mock history data - would come from audit log API endpoint
  const history = [
    {
      date: control.updated_at,
      action: 'Status updated',
      user: 'System',
      details: `Status changed to ${control.status}`,
    },
    {
      date: control.created_at,
      action: 'Control created',
      user: 'System',
      details: 'Control added to framework',
    },
  ];

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold mb-4">Audit Trail</h3>
      <div className="space-y-4">
        {history.map((entry, idx) => (
          <div key={idx} className="flex gap-4 border-l-2 border-gray-300 pl-4 pb-4">
            <div className="flex-shrink-0 w-24 text-sm text-gray-500">
              {new Date(entry.date).toLocaleDateString()}
            </div>
            <div className="flex-grow">
              <p className="font-semibold">{entry.action}</p>
              <p className="text-sm text-gray-600 mt-1">{entry.details}</p>
              <p className="text-xs text-gray-400 mt-1">By {entry.user}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
