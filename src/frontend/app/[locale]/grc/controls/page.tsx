"use client";

import { useState, useEffect, useMemo, useCallback } from 'react';
import Link from 'next/link';
import { useDebounce } from '@/lib/hooks';

interface Control {
  control_id: string;
  framework: string;
  title_ar: string;
  title_en: string;
  description_ar: string;
  status: string;
  priority: string;
  domain: string;
  domain_ar: string;
  implementation_guidance?: string;
  evidence_types?: string[];
}

// Move helper functions outside component to avoid recreation
const STATUS_COLORS: Record<string, string> = {
  compliant: 'bg-green-500',
  in_progress: 'bg-blue-500',
  not_started: 'bg-gray-500',
  non_compliant: 'bg-red-500'
};

const STATUS_TEXTS: Record<string, string> = {
  compliant: 'منفذ',
  in_progress: 'قيد التنفيذ',
  not_started: 'لم يبدأ',
  non_compliant: 'غير ممتثل'
};

const FRAMEWORK_COLORS: Record<string, string> = {
  'ECC': 'from-purple-600 to-purple-800',
  'CCC': 'from-blue-600 to-blue-800',
  'PDPL': 'from-green-600 to-green-800'
};

const PRIORITY_COLORS: Record<string, string> = {
  critical: 'text-red-400',
  high: 'text-orange-400',
  medium: 'text-yellow-400',
  low: 'text-green-400'
};

const getStatusColor = (status: string) => STATUS_COLORS[status] || STATUS_COLORS.not_started;
const getStatusText = (status: string) => STATUS_TEXTS[status] || status;
const getFrameworkColor = (framework: string) => FRAMEWORK_COLORS[framework] || 'from-gray-600 to-gray-800';
const getPriorityColor = (priority: string) => PRIORITY_COLORS[priority] || 'text-gray-400';

export default function ControlsManagement() {
  const [allControls, setAllControls] = useState<Control[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFramework, setSelectedFramework] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [selectedDomain, setSelectedDomain] = useState('ALL');

  // Debounce search term for better performance
  const debouncedSearchTerm = useDebounce(searchTerm, 300);

  useEffect(() => {
    loadControls();
  }, []);

  const loadControls = async () => {
    try {
      const response = await fetch('/api/v1/controls/?limit=500');
      if (response.ok) {
        const data = await response.json();
        setAllControls(data);
      }
      setLoading(false);
    } catch (error) {
      console.error('Error loading controls:', error);
      setLoading(false);
    }
  };

  // Memoize filtered controls to avoid recalculation on every render
  const filteredControls = useMemo(() => {
    let filtered = [...allControls];

    // Search filter - using debounced value
    if (debouncedSearchTerm) {
      const term = debouncedSearchTerm.toLowerCase();
      filtered = filtered.filter(c =>
        c.control_id.toLowerCase().includes(term) ||
        c.title_ar.includes(debouncedSearchTerm) ||
        c.title_en.toLowerCase().includes(term) ||
        c.description_ar.includes(debouncedSearchTerm)
      );
    }

    // Framework filter
    if (selectedFramework !== 'ALL') {
      filtered = filtered.filter(c => c.framework === selectedFramework);
    }

    // Status filter
    if (selectedStatus !== 'ALL') {
      filtered = filtered.filter(c => c.status === selectedStatus);
    }

    // Domain filter
    if (selectedDomain !== 'ALL') {
      filtered = filtered.filter(c => c.domain === selectedDomain);
    }

    return filtered;
  }, [allControls, debouncedSearchTerm, selectedFramework, selectedStatus, selectedDomain]);

  // Memoize unique domains calculation
  const uniqueDomains = useMemo(() => {
    const domains = new Set(allControls.map(c => c.domain));
    return Array.from(domains).sort();
  }, [allControls]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500 mb-4"></div>
          <p className="text-white text-xl">جاري تحميل الضوابط...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white" dir="rtl">
      {/* Header */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <Link href="/ar/grc" className="text-purple-400 hover:text-purple-300 text-sm mb-2 inline-block">
                ← العودة للرئيسية
              </Link>
              <h1 className="text-3xl font-bold text-white">إدارة الضوابط</h1>
              <p className="text-gray-400 mt-1">مكتبة شاملة للضوابط السعودية (ECC/CCC/PDPL)</p>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-purple-400">{filteredControls.length}</div>
              <div className="text-gray-400 text-sm">ضابط متاح</div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Filters */}
        <div className="bg-gray-800 rounded-xl p-6 border border-gray-700 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-300 mb-2">البحث</label>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="ابحث في الضوابط..."
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2.5 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">الإطار</label>
              <select
                value={selectedFramework}
                onChange={(e) => setSelectedFramework(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="ALL">جميع الأطر</option>
                <option value="ECC">ECC</option>
                <option value="CCC">CCC</option>
                <option value="PDPL">PDPL</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">الحالة</label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="ALL">جميع الحالات</option>
                <option value="compliant">منفذ</option>
                <option value="in_progress">قيد التنفيذ</option>
                <option value="not_started">لم يبدأ</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">المجال</label>
              <select
                value={selectedDomain}
                onChange={(e) => setSelectedDomain(e.target.value)}
                className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2.5 text-white focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="ALL">جميع المجالات</option>
                {uniqueDomains.map(domain => (
                  <option key={domain} value={domain}>{domain}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Controls Table */}
        <div className="space-y-4">
          {filteredControls.length === 0 ? (
            <div className="bg-gray-800 rounded-xl p-12 border border-gray-700 text-center">
              <h3 className="text-2xl font-bold text-gray-300 mb-2">لا توجد ضوابط</h3>
              <p className="text-gray-400">جرب تعديل معايير البحث</p>
            </div>
          ) : (
            filteredControls.map(control => (
              <div
                key={control.control_id}
                className="bg-gray-800 rounded-xl p-6 border border-gray-700 hover:border-purple-500 transition shadow-lg"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <span className="font-mono font-bold text-xl text-white">
                        {control.control_id}
                      </span>
                      <span className={`px-4 py-1.5 rounded-lg bg-gradient-to-r ${getFrameworkColor(control.framework)} font-bold text-sm`}>
                        {control.framework}
                      </span>
                      <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${getStatusColor(control.status)}`}></div>
                        <span className="text-sm text-gray-300">{getStatusText(control.status)}</span>
                      </div>
                      {control.priority && (
                        <span className={`text-sm font-medium ${getPriorityColor(control.priority)}`}>
                          {control.priority.toUpperCase()}
                        </span>
                      )}
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2">
                      {control.title_ar}
                    </h3>
                    <p className="text-gray-400 mb-3 leading-relaxed">
                      {control.description_ar}
                    </p>
                    <div className="flex items-center gap-4 text-sm text-gray-500">
                      <span>المجال: {control.domain_ar || control.domain}</span>
                      {control.evidence_types && (
                        <span>الأدلة: {control.evidence_types.length} نوع أدلة</span>
                      )}
                    </div>
                  </div>
                  <Link
                    href={`/ar/grc/controls/${control.control_id}`}
                    className="inline-flex items-center justify-center rounded-lg px-5 py-2.5 text-sm font-semibold bg-purple-600 hover:bg-purple-700 transition shadow-lg ml-4"
                  >
                    عرض التفاصيل
                  </Link>
                </div>
                {control.implementation_guidance && (
                  <div className="mt-4 p-4 bg-blue-900/30 rounded-lg border border-blue-800/50">
                    <p className="text-sm font-medium text-blue-300 mb-1">إرشادات التنفيذ:</p>
                    <p className="text-sm text-blue-200">{control.implementation_guidance}</p>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
