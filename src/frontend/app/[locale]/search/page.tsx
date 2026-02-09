'use client';

import { useTranslations } from 'next-intl';
import { useState } from 'react';
import useSWR from 'swr';
import apiClient from '@/lib/api-client';
import Link from 'next/link';

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export default function SearchPage() {
  const t = useTranslations('search');
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState({
    framework: '',
    status: '',
    priority: '',
    domain: '',
  });
  const [searchPerformed, setSearchPerformed] = useState(false);

  // Build query string
  const queryParams = new URLSearchParams();
  if (filters.framework) queryParams.append('framework', filters.framework);
  if (filters.status) queryParams.append('status', filters.status);
  if (filters.priority) queryParams.append('priority', filters.priority);
  if (filters.domain) queryParams.append('domain', filters.domain);

  const { data: controls, isLoading } = useSWR(
    searchPerformed ? `/api/v1/controls?${queryParams.toString()}` : null,
    fetcher
  );

  const handleSearch = () => {
    setSearchPerformed(true);
  };

  const filteredControls = controls?.items?.filter((control: any) => {
    if (!query) return true;
    const searchLower = query.toLowerCase();
    return (
      control.control_id.toLowerCase().includes(searchLower) ||
      control.title_en?.toLowerCase().includes(searchLower) ||
      control.title_ar?.includes(query) ||
      control.description_en?.toLowerCase().includes(searchLower) ||
      control.description_ar?.includes(query)
    );
  });

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Advanced Search</h1>

        {/* Search Bar */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex gap-4">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="Search by control ID, title, or description (supports Arabic and English)..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 text-lg"
            />
            <button
              onClick={handleSearch}
              className="px-8 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700"
            >
              🔍 Search
            </button>
          </div>
        </div>

        {/* Advanced Filters */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <details className="cursor-pointer">
            <summary className="font-semibold text-lg mb-4">Advanced Filters</summary>
            <div className="grid grid-cols-4 gap-4 mt-4">
              <div>
                <label className="block text-sm font-semibold mb-2">Framework</label>
                <select
                  value={filters.framework}
                  onChange={(e) => setFilters({ ...filters, framework: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">All Frameworks</option>
                  <option value="ECC">ECC</option>
                  <option value="CCC">CCC</option>
                  <option value="PDPL">PDPL</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Status</label>
                <select
                  value={filters.status}
                  onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">All Statuses</option>
                  <option value="compliant">Compliant</option>
                  <option value="non_compliant">Non-Compliant</option>
                  <option value="in_progress">In Progress</option>
                  <option value="not_started">Not Started</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Priority</label>
                <select
                  value={filters.priority}
                  onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                >
                  <option value="">All Priorities</option>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold mb-2">Domain</label>
                <input
                  type="text"
                  value={filters.domain}
                  onChange={(e) => setFilters({ ...filters, domain: e.target.value })}
                  placeholder="e.g., Governance"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                />
              </div>
            </div>

            <button
              onClick={() => {
                setFilters({ framework: '', status: '', priority: '', domain: '' });
                setQuery('');
              }}
              className="mt-4 text-sm text-primary-600 hover:text-primary-700 font-semibold"
            >
              Clear all filters
            </button>
          </details>
        </div>

        {/* Results */}
        {isLoading && (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        )}

        {searchPerformed && !isLoading && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold">
                Search Results ({filteredControls?.length || 0})
              </h2>
              {filteredControls && filteredControls.length > 0 && (
                <button className="text-sm text-primary-600 hover:text-primary-700 font-semibold">
                  Export Results
                </button>
              )}
            </div>

            {filteredControls && filteredControls.length > 0 ? (
              <div className="space-y-4">
                {filteredControls.map((control: any) => (
                  <SearchResultCard key={control.control_id} control={control} query={query} />
                ))}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                <svg
                  className="w-16 h-16 mx-auto mb-4 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                <p className="text-lg font-semibold">No results found</p>
                <p className="text-sm mt-2">Try adjusting your search criteria or filters</p>
              </div>
            )}
          </div>
        )}

        {!searchPerformed && (
          <div className="bg-white rounded-lg shadow-lg p-12 text-center">
            <svg
              className="w-20 h-20 mx-auto mb-4 text-gray-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <h2 className="text-2xl font-bold text-gray-400 mb-2">Start Your Search</h2>
            <p className="text-gray-500">
              Enter keywords or use advanced filters to search across all controls
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

function SearchResultCard({ control, query }: { control: any; query: string }) {
  const statusColors: Record<string, string> = {
    compliant: 'bg-green-100 text-green-800',
    non_compliant: 'bg-red-100 text-red-800',
    in_progress: 'bg-yellow-100 text-yellow-800',
    not_started: 'bg-gray-100 text-gray-800',
  };

  const highlightText = (text: string) => {
    if (!query || !text) return text;
    const regex = new RegExp(`(${query})`, 'gi');
    return text.split(regex).map((part, i) =>
      regex.test(part) ? (
        <mark key={i} className="bg-yellow-200 font-semibold">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  return (
    <Link
      href={`/controls/${control.control_id}`}
      className="block border rounded-lg p-6 hover:shadow-lg transition-shadow"
    >
      <div className="flex justify-between items-start mb-3">
        <div>
          <span className="text-sm font-semibold text-primary-600">{control.control_id}</span>
          <h3 className="text-xl font-bold mt-1">{highlightText(control.title_en)}</h3>
          {control.title_ar && (
            <p className="text-gray-600 mt-1" dir="rtl">
              {highlightText(control.title_ar)}
            </p>
          )}
        </div>
        <span
          className={`px-3 py-1 rounded-full text-sm font-semibold ${
            statusColors[control.status]
          }`}
        >
          {control.status?.replace('_', ' ').toUpperCase()}
        </span>
      </div>

      <p className="text-gray-600 line-clamp-2 mb-3">{highlightText(control.description_en)}</p>

      <div className="flex gap-4 text-sm text-gray-500">
        <span className="font-medium">
          {control.framework} • {control.domain}
        </span>
        <span className="px-2 py-1 bg-gray-100 rounded">{control.priority} priority</span>
      </div>
    </Link>
  );
}
