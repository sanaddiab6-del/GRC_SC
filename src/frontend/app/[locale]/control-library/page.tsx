"use client";

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';

// Types
interface Control {
  control_id: string;
  framework: 'ECC' | 'CCC' | 'PDPL';
  title_en: string;
  title_ar: string;
  description_en: string;
  description_ar: string;
  domain: string;
  domain_ar: string;
  status: string;
  priority: string;
  implementation_guidance: string;
  evidence_types: string[];
}

interface FrameworkStats {
  total: number;
  implemented: number;
  inProgress: number;
  notStarted: number;
}

export default function ControlLibraryPage() {
  const t = useTranslations();
  const [controls, setControls] = useState<Control[]>([]);
  const [filteredControls, setFilteredControls] = useState<Control[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFramework, setSelectedFramework] = useState<string>('ALL');
  const [selectedDomain, setSelectedDomain] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [frameworkStats, setFrameworkStats] = useState<Record<string, FrameworkStats>>({});

  useEffect(() => {
    fetchControls();
  }, []);

  useEffect(() => {
    filterControls();
  }, [controls, selectedFramework, selectedDomain, searchQuery]);

  const fetchControls = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/controls/?limit=1000');
      const data = await response.json();
      setControls(data);
      calculateStats(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching controls:', error);
      setLoading(false);
    }
  };

  const calculateStats = (controlsData: Control[]) => {
    const stats: Record<string, FrameworkStats> = {};
    
    ['ECC', 'CCC', 'PDPL'].forEach(framework => {
      const frameworkControls = controlsData.filter(c => c.framework === framework);
      stats[framework] = {
        total: frameworkControls.length,
        implemented: frameworkControls.filter(c => c.status === 'implemented').length,
        inProgress: frameworkControls.filter(c => c.status === 'in_progress').length,
        notStarted: frameworkControls.filter(c => c.status === 'not_started').length,
      };
    });
    
    setFrameworkStats(stats);
  };

  const filterControls = () => {
    let filtered = [...controls];
    
    if (selectedFramework !== 'ALL') {
      filtered = filtered.filter(c => c.framework === selectedFramework);
    }
    
    if (selectedDomain !== 'ALL') {
      filtered = filtered.filter(c => c.domain === selectedDomain);
    }
    
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(c =>
        c.control_id.toLowerCase().includes(query) ||
        c.title_en.toLowerCase().includes(query) ||
        c.title_ar.includes(query) ||
        c.description_en.toLowerCase().includes(query) ||
        c.description_ar.includes(query)
      );
    }
    
    setFilteredControls(filtered);
  };

  const getUniqueDomains = () => {
    const domains = new Set(controls.map(c => c.domain));
    return Array.from(domains).sort();
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-300';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'implemented': return 'bg-green-100 text-green-800';
      case 'in_progress': return 'bg-blue-100 text-blue-800';
      case 'not_started': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getFrameworkColor = (framework: string) => {
    switch (framework) {
      case 'ECC': return 'bg-purple-100 text-purple-800 border-purple-300';
      case 'CCC': return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'PDPL': return 'bg-green-100 text-green-800 border-green-300';
      default: return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">جاري تحميل المكتبة...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 rtl">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                مكتبة الضوابط السعودية
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                مكتبة شاملة لضوابط الأمن السيبراني السعودية (ECC/CCC/PDPL)
              </p>
            </div>
            <Link
              href="/ar/dashboard"
              className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition"
            >
              لوحة التحكم
            </Link>
          </div>
        </div>
      </div>

      {/* Framework Stats */}
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {['ECC', 'CCC', 'PDPL'].map(framework => (
            <div key={framework} className="bg-white p-6 rounded-lg shadow-sm border">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-gray-900">{framework}</h3>
                <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getFrameworkColor(framework)}`}>
                  {frameworkStats[framework]?.total || 0} ضابط
                </span>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">منفذ</span>
                  <span className="font-medium text-green-600">
                    {frameworkStats[framework]?.implemented || 0}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">قيد التنفيذ</span>
                  <span className="font-medium text-blue-600">
                    {frameworkStats[framework]?.inProgress || 0}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">لم يبدأ</span>
                  <span className="font-medium text-gray-600">
                    {frameworkStats[framework]?.notStarted || 0}
                  </span>
                </div>
              </div>
              {frameworkStats[framework] && (
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-600 h-2 rounded-full transition-all"
                      style={{
                        width: `${(frameworkStats[framework].implemented / frameworkStats[framework].total) * 100}%`
                      }}
                    ></div>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    {Math.round((frameworkStats[framework].implemented / frameworkStats[framework].total) * 100)}% نسبة التنفيذ
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Filters */}
        <div className="bg-white p-6 rounded-lg shadow-sm border mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                البحث
              </label>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="ابحث عن ضابط..."
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                الإطار
              </label>
              <select
                value={selectedFramework}
                onChange={(e) => setSelectedFramework(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="ALL">جميع الأطر</option>
                <option value="ECC">ECC - الضوابط الأساسية</option>
                <option value="CCC">CCC - ضوابط السحابة</option>
                <option value="PDPL">PDPL - حماية البيانات</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                المجال
              </label>
              <select
                value={selectedDomain}
                onChange={(e) => setSelectedDomain(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-purple-500"
              >
                <option value="ALL">جميع المجالات</option>
                {getUniqueDomains().map(domain => (
                  <option key={domain} value={domain}>{domain}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                النتائج
              </label>
              <div className="px-4 py-2 bg-gray-100 rounded-lg">
                <span className="font-bold text-purple-600">{filteredControls.length}</span>
                <span className="text-gray-600"> ضابط</span>
              </div>
            </div>
          </div>
        </div>

        {/* Controls List */}
        <div className="space-y-4">
          {filteredControls.map(control => (
            <div
              key={control.control_id}
              className="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition"
            >
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="font-mono font-bold text-lg text-gray-900">
                      {control.control_id}
                    </span>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getFrameworkColor(control.framework)}`}>
                      {control.framework}
                    </span>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getPriorityColor(control.priority)}`}>
                      {control.priority}
                    </span>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(control.status)}`}>
                      {control.status === 'implemented' ? 'منفذ' : control.status === 'in_progress' ? 'قيد التنفيذ' : 'لم يبدأ'}
                    </span>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {control.title_ar}
                  </h3>
                  <p className="text-gray-600 mb-3">
                    {control.description_ar}
                  </p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>📁 {control.domain_ar}</span>
                    <span>📋 {control.evidence_types?.length || 0} نوع أدلة</span>
                  </div>
                </div>
                <Link
                  href={`/ar/controls/${control.control_id}`}
                  className="bg-purple-50 text-purple-600 px-4 py-2 rounded-lg hover:bg-purple-100 transition"
                >
                  عرض التفاصيل ←
                </Link>
              </div>
              {control.implementation_guidance && (
                <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm font-medium text-blue-900 mb-1">
                    إرشادات التنفيذ:
                  </p>
                  <p className="text-sm text-blue-800">
                    {control.implementation_guidance}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>

        {filteredControls.length === 0 && (
          <div className="text-center py-12 bg-white rounded-lg border">
            <p className="text-gray-500 text-lg">لا توجد ضوابط تطابق معايير البحث</p>
          </div>
        )}
      </div>
    </div>
  );
}
