'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { AuthGuard } from '@/components/auth/AuthGuard';
import { fetchCurrentUser } from '@/lib/auth';

interface ReportSummary {
  overallCompliance: number;
  totalControls: number;
  compliantControls: number;
  highRisks: number;
  openIncidents: number;
  pendingAudits: number;
  criticalAssets: number;
}

function ExecutiveReportContent() {
  const params = useParams();
  const router = useRouter();
  const locale = params.locale as string;
  const isArabic = locale === 'ar';

  const [summary, setSummary] = useState<ReportSummary>({
    overallCompliance: 89,
    totalControls: 287,
    compliantControls: 256,
    highRisks: 7,
    openIncidents: 3,
    pendingAudits: 5,
    criticalAssets: 89,
  });
  const [generatedAt] = useState(new Date().toLocaleString(isArabic ? 'ar-SA' : 'en-US'));
  const [printing, setPrinting] = useState(false);

  const handlePrint = () => {
    setPrinting(true);
    setTimeout(() => {
      window.print();
      setPrinting(false);
    }, 200);
  };

  return (
    <div className="min-h-screen bg-gray-50 print:bg-white">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-900 via-blue-800 to-blue-900 text-white print:bg-blue-900">
        <div className="max-w-5xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs font-semibold tracking-widest uppercase text-blue-200 mb-1">
                SICO GRC Platform
              </div>
              <h1 className="text-3xl font-bold">
                {isArabic ? 'التقرير التنفيذي' : 'Executive Report'}
              </h1>
              <p className="mt-1 text-blue-200 text-sm">
                {isArabic ? `تاريخ التقرير: ${generatedAt}` : `Generated: ${generatedAt}`}
              </p>
            </div>
            <div className="flex gap-3 print:hidden">
              <button
                onClick={handlePrint}
                disabled={printing}
                className="bg-white/20 hover:bg-white/30 text-white px-5 py-2.5 rounded-lg font-semibold transition text-sm"
              >
                {printing ? '...' : (isArabic ? '🖨️ طباعة / تصدير PDF' : '🖨️ Print / Export PDF')}
              </button>
              <Link
                href={`/${locale}/dashboard`}
                className="bg-white/20 hover:bg-white/30 text-white px-5 py-2.5 rounded-lg font-semibold transition text-sm"
              >
                {isArabic ? '← لوحة التحكم' : '← Dashboard'}
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8 space-y-8">

        {/* Key Metrics */}
        <section>
          <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">
            {isArabic ? 'المؤشرات الرئيسية' : 'Key Performance Indicators'}
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl border shadow-sm p-5 text-center">
              <div className="text-3xl font-bold text-blue-700">{summary.overallCompliance}%</div>
              <div className="text-xs text-gray-500 mt-1 font-semibold uppercase tracking-wide">
                {isArabic ? 'الامتثال الإجمالي' : 'Overall Compliance'}
              </div>
              <div className="text-xs text-green-600 mt-1">↑ 5.2% vs last period</div>
            </div>
            <div className="bg-white rounded-xl border shadow-sm p-5 text-center">
              <div className="text-3xl font-bold text-purple-700">{summary.totalControls}</div>
              <div className="text-xs text-gray-500 mt-1 font-semibold uppercase tracking-wide">
                {isArabic ? 'إجمالي الضوابط' : 'Total Controls'}
              </div>
              <div className="text-xs text-gray-400 mt-1">{summary.compliantControls} compliant</div>
            </div>
            <div className="bg-white rounded-xl border shadow-sm p-5 text-center">
              <div className="text-3xl font-bold text-red-600">{summary.highRisks}</div>
              <div className="text-xs text-gray-500 mt-1 font-semibold uppercase tracking-wide">
                {isArabic ? 'المخاطر العالية' : 'High Risks'}
              </div>
              <div className="text-xs text-red-500 mt-1">↓ 15% vs last period</div>
            </div>
            <div className="bg-white rounded-xl border shadow-sm p-5 text-center">
              <div className="text-3xl font-bold text-orange-600">{summary.openIncidents}</div>
              <div className="text-xs text-gray-500 mt-1 font-semibold uppercase tracking-wide">
                {isArabic ? 'الحوادث المفتوحة' : 'Open Incidents'}
              </div>
              <div className="text-xs text-orange-500 mt-1">↓ 33% vs last period</div>
            </div>
          </div>
        </section>

        {/* Compliance Summary */}
        <section>
          <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">
            {isArabic ? 'ملخص الامتثال' : 'Compliance Summary'}
          </h2>
          <div className="bg-white rounded-xl border shadow-sm p-6">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-gray-600 font-medium">
                {isArabic ? 'الضوابط المستوفاة' : 'Controls Met'}
              </span>
              <span className="text-sm font-bold text-gray-800">
                {summary.compliantControls} / {summary.totalControls}
              </span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-4 overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-blue-500 to-green-500 transition-all duration-500"
                style={{ width: `${(summary.compliantControls / summary.totalControls) * 100}%` }}
              />
            </div>
            <div className="mt-4 grid grid-cols-3 gap-4 text-center text-sm">
              <div className="bg-green-50 rounded-lg p-3 border border-green-100">
                <div className="font-bold text-green-700">{summary.compliantControls}</div>
                <div className="text-green-600 text-xs mt-1">{isArabic ? 'مستوفي' : 'Compliant'}</div>
              </div>
              <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-100">
                <div className="font-bold text-yellow-700">
                  {summary.totalControls - summary.compliantControls - 12}
                </div>
                <div className="text-yellow-600 text-xs mt-1">{isArabic ? 'جزئي' : 'Partial'}</div>
              </div>
              <div className="bg-red-50 rounded-lg p-3 border border-red-100">
                <div className="font-bold text-red-700">12</div>
                <div className="text-red-600 text-xs mt-1">{isArabic ? 'غير مستوفي' : 'Non-Compliant'}</div>
              </div>
            </div>
          </div>
        </section>

        {/* Risk Overview */}
        <section>
          <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">
            {isArabic ? 'نظرة عامة على المخاطر' : 'Risk Overview'}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[
              { level: isArabic ? 'عالي' : 'High', count: summary.highRisks, color: 'red' },
              { level: isArabic ? 'متوسط' : 'Medium', count: 18, color: 'yellow' },
              { level: isArabic ? 'منخفض' : 'Low', count: 34, color: 'green' },
            ].map(({ level, count, color }) => (
              <div
                key={level}
                className={`bg-white rounded-xl border shadow-sm p-5 border-l-4 ${
                  color === 'red'
                    ? 'border-l-red-500'
                    : color === 'yellow'
                    ? 'border-l-yellow-500'
                    : 'border-l-green-500'
                }`}
              >
                <div
                  className={`text-3xl font-bold ${
                    color === 'red'
                      ? 'text-red-600'
                      : color === 'yellow'
                      ? 'text-yellow-600'
                      : 'text-green-600'
                  }`}
                >
                  {count}
                </div>
                <div className="text-sm text-gray-600 font-medium mt-1">
                  {level} {isArabic ? 'المخاطر' : 'Risk Items'}
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Audit & Incident Status */}
        <section>
          <h2 className="text-xl font-bold text-gray-800 mb-4 border-b pb-2">
            {isArabic ? 'التدقيق والحوادث' : 'Audit & Incident Status'}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white rounded-xl border shadow-sm p-6">
              <h3 className="font-semibold text-gray-800 mb-3">
                {isArabic ? 'حالة التدقيق' : 'Audit Status'}
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">{isArabic ? 'قيد التنفيذ' : 'In Progress'}</span>
                  <span className="font-semibold text-blue-600">{summary.pendingAudits}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">{isArabic ? 'مكتمل' : 'Completed'}</span>
                  <span className="font-semibold text-green-600">12</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">{isArabic ? 'مجدول' : 'Scheduled'}</span>
                  <span className="font-semibold text-gray-700">3</span>
                </div>
              </div>
            </div>
            <div className="bg-white rounded-xl border shadow-sm p-6">
              <h3 className="font-semibold text-gray-800 mb-3">
                {isArabic ? 'حالة الحوادث' : 'Incident Status'}
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">{isArabic ? 'مفتوح' : 'Open'}</span>
                  <span className="font-semibold text-red-600">{summary.openIncidents}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">{isArabic ? 'قيد المعالجة' : 'Under Investigation'}</span>
                  <span className="font-semibold text-yellow-600">2</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">{isArabic ? 'مغلق' : 'Closed'}</span>
                  <span className="font-semibold text-green-600">47</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <div className="text-center text-xs text-gray-400 border-t pt-6 print:block">
          SICO GRC Platform — {isArabic ? 'تقرير سري — للاستخدام الداخلي فقط' : 'Confidential — For Internal Use Only'} — {generatedAt}
        </div>
      </div>

      <style jsx global>{`
        @media print {
          .print\\:hidden { display: none !important; }
          .print\\:block { display: block !important; }
          .print\\:bg-white { background: white !important; }
          .print\\:bg-blue-900 { background: #1e3a5f !important; }
        }
      `}</style>
    </div>
  );
}

export default function ExecutiveReportPage() {
  return (
    <AuthGuard>
      <ExecutiveReportContent />
    </AuthGuard>
  );
}
