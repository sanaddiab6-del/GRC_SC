"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';

interface Stats {
  totalControls: number;
  implementedControls: number;
  frameworks: {
    ECC: { total: number; implemented: number };
    CCC: { total: number; implemented: number };
    PDPL: { total: number; implemented: number };
  };
  overallCompliance: number;
}

export default function ComprehensiveDashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/controls/?limit=1000');
      const controls = await response.json();
      
      const eccControls = controls.filter((c: any) => c.framework === 'ECC');
      const cccControls = controls.filter((c: any) => c.framework === 'CCC');
      const pdplControls = controls.filter((c: any) => c.framework === 'PDPL');
      
      const implemented = controls.filter((c: any) => c.status === 'implemented').length;
      
      setStats({
        totalControls: controls.length,
        implementedControls: implemented,
        frameworks: {
          ECC: {
            total: eccControls.length,
            implemented: eccControls.filter((c: any) => c.status === 'implemented').length
          },
          CCC: {
            total: cccControls.length,
            implemented: cccControls.filter((c: any) => c.status === 'implemented').length
          },
          PDPL: {
            total: pdplControls.length,
            implemented: pdplControls.filter((c: any) => c.status === 'implemented').length
          }
        },
        overallCompliance: (implemented / controls.length) * 100
      });
      
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">جاري تحميل لوحة التحكم...</p>
        </div>
      </div>
    );
  }

  const deliverables = [
    {
      id: 1,
      phase: "A",
      nameAr: "مكتبة الضوابط السعودية",
      nameEn: "Saudi Control Library",
      description: `${stats?.totalControls || 0} ضابط تشغيلي (ECC/CCC/PDPL)`,
      status: "مكتمل",
      statusColor: "green",
      link: "/ar/control-library",
      icon: "LIB"
    },
    {
      id: 2,
      phase: "A",
      nameAr: "الخط القاعدي الموحد ECC↔CCC",
      nameEn: "ECC↔CCC Unified Baseline",
      description: "إزال ة التكرار بين الأطر التنظيمية",
      status: "مكتمل",
      statusColor: "green",
      link: "/ar/unified-baseline",
      icon: "MAP"
    },
    {
      id: 3,
      phase: "A",
      nameAr: "مجموعة ضوابط PDPL التشغيلية",
      nameEn: "PDPL Operational Control Set",
      description: "سجلات الخصوصية والضوابط",
      status: "مكتمل",
      statusColor: "green",
      link: "/ar/pdpl-controls",
      icon: "PDPL"
    },
    {
      id: 4,
      phase: "A",
      nameAr: "فهرس الأدلة الرئيسي",
      nameEn: "Evidence Master Catalog",
      description: "قوالب أدلة جاهزة للتدقيق",
      status: "مكتمل",
      statusColor: "green",
      link: "/ar/evidence-catalog",
      icon: "EVD"
    },
    {
      id: 5,
      phase: "A",
      nameAr: "مكتبة إجراءات اختبار التدقيق",
      nameEn: "Audit Test Procedures",
      description: "إجراءات اخت بار لجميع الضوابط",
      status: "مكتمل",
      statusColor: "green",
      link: "/ar/audit-procedures",
      icon: "AUD"
    },
    {
      id: 6,
      phase: "B",
      nameAr: "حزم SICO",
      nameEn: "SICO Packs",
      description: "حزم امتثال مسبقة التجهيز",
      status: "متاح",
      statusColor: "blue",
      link: "/ar/sico-packs",
      icon: "PKG"
    },
    {
      id: 7,
      phase: "B",
      nameAr: "مجموعة التقارير التنفيذية",
      nameEn: "Executive Reporting Kit",
      description: "لوحات تحكم تنفيذية جاهزة للاستخدام",
      status: "متاح",
      statusColor: "blue",
      link: "/ar/executive-reports",
      icon: "RPT"
    },
    {
      id: 8,
      phase: "B",
      nameAr: "جسر SOC ↔ GRC",
      nameEn: "SOC ↔ GRC Bridge",
      description: "أتمتة ربط الحوادث بالامتثال",
      status: "متاح",
      statusColor: "blue",
      link: "/ar/soc-grc-bridge",
      icon: "SOC"
    },
    {
      id: 9,
      phase: "C",
      nameAr: "قاعدة المعرفة ثنائية اللغة + RAG",
      nameEn: "Bilingual Knowledge Base + RAG",
      description: "إجابات AI مدعومة بالاستشهادات",
      status: "متاح",
      statusColor: "blue",
      link: "/ar/ai-assistant",
      icon: "AI"
    },
    {
      id: 10,
      phase: "C",
      nameAr: "محرك قاموس العملاء",
      nameEn: "Client Dictionary Engine",
      description: "مصطلحات ثنائية اللغة خاصة بالعميل",
      status: "متاح",
      statusColor: "blue",
      link: "/ar/client-dictionary",
      icon: "DICT"
    },
    {
      id: 11,
      phase: "C",
      nameAr: "محولات BERT لكل عميل",
      nameEn: "Per-Client BERT Adapters",
      description: "نماذج NLP مخصصة (بريميوم)",
      status: "بريميوم",
      statusColor: "purple",
      link: "/ar/bert-adapters",
      icon: "NLP"
    },
    {
      id: 12,
      phase: "D",
      nameAr: "دليل مصنع التسليم",
      nameEn: "Delivery Factory Playbook",
      description: "منهجية تسليم قابلة للتكرار",
      status: "متاح",
      statusColor: "blue",
      link: "/ar/delivery-playbook",
      icon: "OPS"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-blue-600">
                منصة SICO GRC
              </h1>
              <p className="mt-2 text-lg text-gray-600">
                منصة الامتثال التنظيمي السعودي (ECC/CCC/PDPL)
              </p>
            </div>
            <div className="flex gap-3">
              <Link
                href="/ar/control-library"
                className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 transition font-medium shadow-lg"
              >
                مكتبة الضوابط
              </Link>
              <Link
                href="/ar/executive-reports"
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition font-medium shadow-lg"
              >
                التقارير التنفيذية
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 rtl">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-gradient-to-br from-purple-500 to-purple-600 p-6 rounded-xl shadow-lg text-white">
            <div className="text-4xl font-bold mb-2">{stats?.totalControls || 0}</div>
            <div className="text-purple-100">إجمالي الضوابط</div>
          </div>
          <div className="bg-gradient-to-br from-green-500 to-green-600 p-6 rounded-xl shadow-lg text-white">
            <div className="text-4xl font-bold mb-2">{stats?.implementedControls || 0}</div>
            <div className="text-green-100">ضوابط منفذة</div>
          </div>
          <div className="bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-xl shadow-lg text-white">
            <div className="text-4xl font-bold mb-2">{stats?.overallCompliance.toFixed(0) || 0}%</div>
            <div className="text-blue-100">نسبة الامتثال</div>
          </div>
          <div className="bg-gradient-to-br from-orange-500 to-orange-600 p-6 rounded-xl shadow-lg text-white">
            <div className="text-4xl font-bold mb-2">12</div>
            <div className="text-orange-100">التسليمات الرئيسية</div>
          </div>
        </div>

        {/* Framework Status */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {stats && Object.entries(stats.frameworks).map(([framework, data]) => (
            <div key={framework} className="bg-white p-6 rounded-xl shadow-lg border">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-2xl font-bold text-gray-900">{framework}</h3>
                <span className="text-3xl font-bold text-purple-600">
                  {((data.implemented / data.total) * 100).toFixed(0)}%
                </span>
              </div>
              <div className="mb-3">
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">التقدم</span>
                  <span className="font-medium">{data.implemented} / {data.total}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-purple-500 to-blue-500 h-3 rounded-full transition-all"
                    style={{ width: `${(data.implemented / data.total) * 100}%` }}
                  ></div>
                </div>
              </div>
              <Link
                href={`/ar/frameworks/${framework.toLowerCase()}`}
                className="text-purple-600 hover:text-purple-700 font-medium text-sm"
              >
                عرض التفاصيل ←
              </Link>
            </div>
          ))}
        </div>

        {/* 12 Deliverables */}
        <div className="bg-white p-6 rounded-xl shadow-lg border mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            التسليمات الرئيسية الـ 12
          </h2>
          
          {/* Phase A */}
          <div className="mb-8">
            <h3 className="text-xl font-bold text-purple-600 mb-4 flex items-center gap-2">
              <span className="bg-purple-100 px-3 py-1 rounded-full text-sm">المرحلة A</span>
              الإعداد التنظيمي (التسليمات 1-5)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {deliverables.filter(d => d.phase === "A").map(deliverable => (
                <Link
                  key={deliverable.id}
                  href={deliverable.link}
                  className="block bg-gradient-to-br from-gray-50 to-white p-6 rounded-lg border-2 border-gray-200 hover:border-purple-400 transition hover:shadow-lg"
                >
                  <div className="flex items-start gap-3 mb-3">
                    <span className="text-xs font-semibold tracking-wide text-gray-500">{deliverable.icon}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          deliverable.statusColor === 'green' ? 'bg-green-100 text-green-800' :
                          deliverable.statusColor === 'blue' ? 'bg-blue-100 text-blue-800' :
                          'bg-purple-100 text-purple-800'
                        }`}>
                          {deliverable.status}
                        </span>
                      </div>
                      <h4 className="font-bold text-gray-900 mb-1">
                        {deliverable.nameAr}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {deliverable.description}
                      </p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Phase B */}
          <div className="mb-8">
            <h3 className="text-xl font-bold text-blue-600 mb-4 flex items-center gap-2">
              <span className="bg-blue-100 px-3 py-1 rounded-full text-sm">المرحلة B</span>
              الميزة التنافسية (التسليمات 6-8)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {deliverables.filter(d => d.phase === "B").map(deliverable => (
                <Link
                  key={deliverable.id}
                  href={deliverable.link}
                  className="block bg-gradient-to-br from-blue-50 to-white p-6 rounded-lg border-2 border-gray-200 hover:border-blue-400 transition hover:shadow-lg"
                >
                  <div className="flex items-start gap-3 mb-3">
                    <span className="text-xs font-semibold tracking-wide text-gray-500">{deliverable.icon}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          deliverable.statusColor === 'green' ? 'bg-green-100 text-green-800' :
                          deliverable.statusColor === 'blue' ? 'bg-blue-100 text-blue-800' :
                          'bg-purple-100 text-purple-800'
                        }`}>
                          {deliverable.status}
                        </span>
                      </div>
                      <h4 className="font-bold text-gray-900 mb-1">
                        {deliverable.nameAr}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {deliverable.description}
                      </p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Phase C */}
          <div className="mb-8">
            <h3 className="text-xl font-bold text-green-600 mb-4 flex items-center gap-2">
              <span className="bg-green-100 px-3 py-1 rounded-full text-sm">المرحلة C</span>
              الأتمتة المدعومة بالذكاء الاصطناعي (التسليمات 9-11)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {deliverables.filter(d => d.phase === "C").map(deliverable => (
                <Link
                  key={deliverable.id}
                  href={deliverable.link}
                  className="block bg-gradient-to-br from-green-50 to-white p-6 rounded-lg border-2 border-gray-200 hover:border-green-400 transition hover:shadow-lg"
                >
                  <div className="flex items-start gap-3 mb-3">
                    <span className="text-xs font-semibold tracking-wide text-gray-500">{deliverable.icon}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          deliverable.statusColor === 'green' ? 'bg-green-100 text-green-800' :
                          deliverable.statusColor === 'blue' ? 'bg-blue-100 text-blue-800' :
                          'bg-purple-100 text-purple-800'
                        }`}>
                          {deliverable.status}
                        </span>
                      </div>
                      <h4 className="font-bold text-gray-900 mb-1">
                        {deliverable.nameAr}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {deliverable.description}
                      </p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Phase D */}
          <div>
            <h3 className="text-xl font-bold text-orange-600 mb-4 flex items-center gap-2">
              <span className="bg-orange-100 px-3 py-1 rounded-full text-sm">المرحلة D</span>
              التميز التشغيلي (التسليم 12)
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {deliverables.filter(d => d.phase === "D").map(deliverable => (
                <Link
                  key={deliverable.id}
                  href={deliverable.link}
                  className= "block bg-gradient-to-br from-orange-50 to-white p-6 rounded-lg border-2 border-gray-200 hover:border-orange-400 transition hover:shadow-lg"
                >
                  <div className="flex items-start gap-3 mb-3">
                    <span className="text-xs font-semibold tracking-wide text-gray-500">{deliverable.icon}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          deliverable.statusColor === 'green' ? 'bg-green-100 text-green-800' :
                          deliverable.statusColor === 'blue' ? 'bg-blue-100 text-blue-800' :
                          'bg-purple-100 text-purple-800'
                        }`}>
                          {deliverable.status}
                        </span>
                      </div>
                      <h4 className="font-bold text-gray-900 mb-1">
                        {deliverable.nameAr}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {deliverable.description}
                      </p>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            href="/ar/control-library"
            className="bg-white p-6 rounded-xl shadow-lg border hover:shadow-xl transition text-center"
          >
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-3">LIB</div>
            <div className="font-bold text-gray-900 mb-2">مكتبة الضوابط</div>
            <div className="text-sm text-gray-600">{stats?.totalControls || 0} ضابط تشغيلي</div>
          </Link>
          <Link
            href="/ar/evidence-catalog"
            className="bg-white p-6 rounded-xl shadow-lg border hover:shadow-xl transition text-center"
          >
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-3">EVD</div>
            <div className="font-bold text-gray-900 mb-2">فهرس الأدلة</div>
            <div className="text-sm text-gray-600">قوالب جاهزة للتدقيق</div>
          </Link>
          <Link
            href="/ar/ai-assistant"
            className="bg-white p-6 rounded-xl shadow-lg border hover:shadow-xl transition text-center"
          >
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-3">AI</div>
            <div className="font-bold text-gray-900 mb-2">مساعد AI</div>
            <div className="text-sm text-gray-600">استشارات ذكية ثنائية اللغة</div>
          </Link>
          <Link
            href="/ar/executive-reports"
            className="bg-white p-6 rounded-xl shadow-lg border hover:shadow-xl transition text-center"
          >
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-3">RPT</div>
            <div className="font-bold text-gray-900 mb-2">التقارير التنفيذية</div>
            <div className="text-sm text-gray-600">لوحات تحكم شاملة</div>
          </Link>
        </div>
      </div>
    </div>
  );
}
