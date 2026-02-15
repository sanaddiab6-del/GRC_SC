'use client';

/**
 * Professional Controls Management Page
 * Complete CRUD with filtering, sorting, and export
 */

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import {
  ControlCard,
  SearchFilterBar,
  LoadingSpinner,
  EmptyState,
  Control
} from '@/components/ui';

export default function ControlsListPage() {
  const t = useTranslations();
  const locale = 'ar';

  const [controls, setControls] = useState<Control[]>([]);
  const [filteredControls, setFilteredControls] = useState<Control[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState<any>({});
  const [sortBy, setSortBy] = useState<'priority' | 'status' | 'framework'>('priority');

  useEffect(() => {
    loadControls();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [controls, searchTerm, filters, sortBy]);

  const loadControls = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/v1/controls/');
      const data = await res.json();
      setControls(data);
      setLoading(false);
    } catch (error) {
      console.error('Error loading controls:', error);
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = [...controls];

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(c => 
        c.title_ar.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.title_en.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.control_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.description_ar.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Framework filter
    if (filters.framework && filters.framework.length > 0) {
      filtered = filtered.filter(c => filters.framework.includes(c.framework));
    }

    // Status filter
    if (filters.status && filters.status.length > 0) {
      filtered = filtered.filter(c => filters.status.includes(c.status));
    }

    // Priority filter
    if (filters.priority && filters.priority.length > 0) {
      filtered = filtered.filter(c => filters.priority.includes(c.priority));
    }

    // Sort
    const priorityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    const statusOrder = { non_compliant: 0, not_started: 1, in_progress: 2, compliant: 3 };

    if (sortBy === 'priority') {
      filtered.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
    } else if (sortBy === 'status') {
      filtered.sort((a, b) => statusOrder[a.status] - statusOrder[b.status]);
    } else if (sortBy === 'framework') {
      filtered.sort((a, b) => a.framework.localeCompare(b.framework));
    }

    setFilteredControls(filtered);
  };

  const exportToCSV = () => {
    const headers = ['Control ID', 'Framework', 'Domain', 'Title (AR)', 'Title (EN)', 'Priority', 'Status'];
    const rows = filteredControls.map(c => [
      c.control_id,
      c.framework,
      c.domain,
      c.title_ar,
      c.title_en,
      c.priority,
      c.status
    ]);

    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `sico-controls-${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            إدارة الضوابط
          </h1>
          <p className="text-gray-600 dark:text-gray-400">
            {filteredControls.length} من أصل {controls.length} ضابط
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={exportToCSV}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium flex items-center gap-2"
          >
            <span className="text-xs font-semibold tracking-wide">CSV</span>
            <span>تصدير CSV</span>
          </button>
          <Link
            href="/ar/controls/new"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center gap-2"
          >
            <span className="text-xs font-semibold tracking-wide">NEW</span>
            <span>إضافة ضابط</span>
          </Link>
        </div>
      </div>

      {/* Search and Filters */}
      <SearchFilterBar
        searchTerm={searchTerm}
        onSearchChange={setSearchTerm}
        filters={filters}
        onFilterChange={setFilters}
        locale={locale}
      />

      {/* Sort Options */}
      <div className="flex items-center gap-4 mb-6">
        <span className="text-gray-700 dark:text-gray-300 font-medium">ترتيب حسب:</span>
        <div className="flex gap-2">
          <button
            onClick={() => setSortBy('priority')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              sortBy === 'priority'
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            الأولوية
          </button>
          <button
            onClick={() => setSortBy('status')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              sortBy === 'status'
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            الحالة
          </button>
          <button
            onClick={() => setSortBy('framework')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              sortBy === 'framework'
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
            }`}
          >
            الإطار
          </button>
        </div>
      </div>

      {/* Controls Grid */}
      {filteredControls.length === 0 ? (
        <EmptyState
          title="لا توجد ضوابط"
          description="لم يتم العثور على ضوابط تطابق معايير البحث"
          icon="SRCH"
          action={{
            label: 'إعادة تعيين البحث',
            onClick: () => {
              setSearchTerm('');
              setFilters({});
            }
          }}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredControls.map((control) => (
            <ControlCard
              key={control.control_id}
              control={control}
              locale={locale}
              onClick={() => window.location.href = `/ar/controls/${control.control_id}`}
            />
          ))}
        </div>
      )}

      {/* Pagination (placeholder for future implementation) */}
      {filteredControls.length > 0 && (
        <div className="flex justify-center mt-8">
          <div className="flex items-center gap-2">
            <button className="px-4 py-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
              السابق
            </button>
            <span className="px-4 py-2 bg-blue-600 text-white rounded-lg">1</span>
            <button className="px-4 py-2 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
              التالي
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
