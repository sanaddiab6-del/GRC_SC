import { useTranslations } from 'next-intl';
import Link from 'next/link';

export default function HomePage({
  params: { locale }
}: {
  params: { locale: string };
}) {
  const isArabic = locale === 'ar';

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-primary-600 to-primary-800 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-6">
            {isArabic ? 'منصة سيكو للحوكمة' : 'SICO GRC Platform'}
          </h1>
          <p className="text-xl mb-8 max-w-3xl mx-auto">
            {isArabic 
              ? 'حل شامل للحوكمة والمخاطر والامتثال للأطر التنظيمية السعودية'
              : 'Comprehensive Governance, Risk & Compliance solution for Saudi regulatory frameworks'}
          </p>
          <p className="text-lg mb-10 opacity-90">
            {isArabic
              ? 'إدارة الامتثال لأنظمة ECC و CCC و PDPL في منصة واحدة موحدة'
              : 'Manage compliance with ECC, CCC, and PDPL regulations in one unified platform'}
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              href={`/${locale}/dashboard`}
              className="px-8 py-4 bg-white text-primary-600 rounded-lg font-bold text-lg hover:bg-gray-100 transition-colors"
            >
              {isArabic ? 'الذهاب إلى لوحة القيادة' : 'Go to Dashboard'}
            </Link>
            <Link
              href={`/${locale}/controls`}
              className="px-8 py-4 bg-primary-700 text-white rounded-lg font-bold text-lg hover:bg-primary-800 transition-colors border-2 border-white"
            >
              {isArabic ? 'عرض الضوابط' : 'View Controls'}
            </Link>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="container mx-auto px-4 py-16">
        <h2 className="text-3xl font-bold text-center mb-12">
          {isArabic ? 'الميزات الرئيسية' : 'Key Features'}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <FeatureCard
            icon="CMP"
            title={isArabic ? 'لوحة الامتثال' : 'Compliance Dashboard'}
            description={isArabic 
              ? 'رؤية فورية لوضع الامتثال عبر جميع الأطر'
              : 'Real-time visibility into your compliance posture across all frameworks'}
            href={`/${locale}/dashboard`}
          />
          <FeatureCard
            icon="CTRL"
            title={isArabic ? 'إدارة الضوابط' : 'Control Management'}
            description={isArabic
              ? 'إدارة وتتبع ضوابط الامتثال مع التحقق القائم على الأدلة'
              : 'Manage and track compliance controls with evidence-based validation'}
            href={`/${locale}/controls`}
          />
          <FeatureCard
            icon="SRCH"
            title={isArabic ? 'البحث المتقدم' : 'Advanced Search'}
            description={isArabic
              ? 'البحث عبر الضوابط بدعم ثنائي اللغة للعربية والإنجليزية'
              : 'Search across controls with bilingual support for Arabic and English'}
            href={`/${locale}/search`}
          />
          <FeatureCard
            icon="EVD"
            title={isArabic ? 'إدارة الأدلة' : 'Evidence Management'}
            description={isArabic
              ? 'تحميل وتنظيم أدلة الامتثال مع التحقق التلقائي'
              : 'Upload and organize compliance evidence with automatic validation'}
            href={`/${locale}/evidence/upload`}
          />
          <FeatureCard
            icon="RPT"
            title={isArabic ? 'تقارير الامتثال' : 'Compliance Reports'}
            description={isArabic
              ? 'إنشاء التقارير التنفيذية وتصدير البيانات بتنسيقات متعددة'
              : 'Generate executive reports and export data in multiple formats'}
            href={`/${locale}/reports`}
          />
          <FeatureCard
            icon="AI"
            title={isArabic ? 'رؤى مدعومة بالذكاء الاصطناعي' : 'AI-Powered Insights'}
            description={isArabic
              ? 'احصل على توصيات ذكية باستخدام مساعد الامتثال القائم على RAG'
              : 'Get intelligent recommendations using RAG-based compliance assistant'}
            href={`/${locale}/dashboard`}
          />
        </div>
      </div>

      {/* Framework Coverage */}
      <div className="bg-gray-100 py-16">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">
            {isArabic ? 'الأطر المدعومة' : 'Supported Frameworks'}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <FrameworkCard
              title="ECC"
              fullName={isArabic ? 'الضوابط الأساسية للأمن السيبراني' : 'Essential Cybersecurity Controls'}
              authority={isArabic ? 'الهيئة الوطنية للأمن السيبراني' : 'NCA - National Cybersecurity Authority'}
              controls={isArabic ? 'أكثر من 50 ضابط' : '50+ controls'}
              color="blue"
            />
            <FrameworkCard
              title="CCC"
              fullName={isArabic ? 'ضوابط الأمن السيبراني السحابي' : 'Cloud Cybersecurity Controls'}
              authority={isArabic ? 'الهيئة الوطنية للأمن السيبراني' : 'NCA - National Cybersecurity Authority'}
              controls={isArabic ? 'أكثر من 40 ضابط' : '40+ controls'}
              color="purple"
            />
            <FrameworkCard
              title="PDPL"
              fullName={isArabic ? 'نظام حماية البيانات الشخصية' : 'Personal Data Protection Law'}
              authority={isArabic ? 'الهيئة السعودية للبيانات والذكاء الاصطناعي' : 'SDAIA - Saudi Data & AI Authority'}
              controls={isArabic ? 'أكثر من 30 ضابط' : '30+ controls'}
              color="green"
            />
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="container mx-auto px-4 py-16">
        <div className="bg-primary-600 text-white rounded-2xl p-12">
          <h2 className="text-3xl font-bold text-center mb-12">
            {isArabic ? 'إدارة شاملة للامتثال' : 'Comprehensive Compliance Management'}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div>
              <p className="text-5xl font-bold mb-2">120+</p>
              <p className="text-lg opacity-90">{isArabic ? 'إجمالي الضوابط' : 'Total Controls'}</p>
            </div>
            <div>
              <p className="text-5xl font-bold mb-2">3</p>
              <p className="text-lg opacity-90">{isArabic ? 'أطر تنظيمية' : 'Regulatory Frameworks'}</p>
            </div>
            <div>
              <p className="text-5xl font-bold mb-2">100%</p>
              <p className="text-lg opacity-90">{isArabic ? 'دعم ثنائي اللغة' : 'Bilingual Support'}</p>
            </div>
            <div>
              <p className="text-5xl font-bold mb-2">24/7</p>
              <p className="text-lg opacity-90">{isArabic ? 'مراقبة الامتثال' : 'Compliance Monitoring'}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function FeatureCard({ 
  icon, 
  title, 
  description, 
  href 
}: { 
  icon: string; 
  title: string; 
  description: string; 
  href: string;
}) {
  return (
    <Link
      href={href}
      className="block bg-white rounded-lg shadow-md p-6 hover:shadow-xl transition-shadow border border-gray-200"
    >
      <div className="text-xs font-semibold tracking-wide text-gray-500 mb-4">{icon}</div>
      <h3 className="text-xl font-bold mb-3">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </Link>
  );
}

function FrameworkCard({ 
  title, 
  fullName, 
  authority, 
  controls, 
  color 
}: { 
  title: string; 
  fullName: string; 
  authority: string; 
  controls: string; 
  color: string;
}) {
  const colorClasses: Record<string, string> = {
    blue: 'border-blue-500 bg-blue-50',
    purple: 'border-purple-500 bg-purple-50',
    green: 'border-green-500 bg-green-50',
  };

  return (
    <div className={`bg-white rounded-lg shadow-md p-6 border-l-4 ${colorClasses[color]}`}>
      <h3 className="text-2xl font-bold mb-2">{title}</h3>
      <p className="text-lg font-semibold text-gray-700 mb-3">{fullName}</p>
      <p className="text-sm text-gray-600 mb-4">{authority}</p>
      <div className="pt-4 border-t border-gray-200">
        <p className="text-primary-600 font-semibold">{controls}</p>
      </div>
    </div>
  );
}
