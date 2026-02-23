import FrameworkPage from '@/components/FrameworkPage';

export default function PDPLFrameworkPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      {/* Header */}
      <div className="mb-8">
        <Link href={`/${locale}/frameworks`} className="text-primary-600 hover:text-primary-700 mb-4 inline-block">
          ← {isArabic ? 'العودة إلى الأطر' : 'Back to Frameworks'}
        </Link>
        <div className="bg-gradient-to-r from-green-600 to-green-800 text-white rounded-xl p-8 shadow-lg">
          <div className="flex items-center gap-4 mb-4">
            <div>
              <h1 className="text-4xl font-bold">
                {isArabic ? 'نظام حماية البيانات الشخصية' : 'Personal Data Protection Law (PDPL)'}
              </h1>
              <p className="text-xl mt-2 opacity-90">
                {isArabic 
                  ? 'الهيئة السعودية للبيانات والذكاء الاصطناعي (سدايا)'
                  : 'Saudi Data & AI Authority (SDAIA)'}
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-4 gap-4 mt-6">
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <p className="text-sm opacity-80">{isArabic ? 'إجمالي الضوابط' : 'Total Controls'}</p>
              <p className="text-3xl font-bold">{stats.total}</p>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <p className="text-sm opacity-80">{isArabic ? 'متوافق' : 'Compliant'}</p>
              <p className="text-3xl font-bold">{stats.compliant}</p>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <p className="text-sm opacity-80">{isArabic ? 'قيد التنفيذ' : 'In Progress'}</p>
              <p className="text-3xl font-bold">{stats.inProgress}</p>
            </div>
            <div className="bg-white bg-opacity-20 rounded-lg p-4">
              <p className="text-sm opacity-80">{isArabic ? 'غير متوافق' : 'Non-Compliant'}</p>
              <p className="text-3xl font-bold">{stats.nonCompliant}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Framework Overview */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <h2 className="text-2xl font-bold mb-4">
          {isArabic ? 'نظرة عامة على النظام' : 'Framework Overview'}
        </h2>
        <div className="prose max-w-none">
          <p className="text-gray-700 leading-relaxed">
            {isArabic
              ? 'نظام حماية البيانات الشخصية (PDPL) هو الإطار التنظيمي الرئيسي لحماية البيانات في المملكة العربية السعودية. يهدف النظام إلى حماية خصوصية الأفراد وتنظيم معالجة البيانات الشخصية.'
              : 'The Personal Data Protection Law (PDPL) is the main regulatory framework for data protection in Saudi Arabia. The law aims to protect individuals\' privacy and regulate personal data processing.'}
          </p>
          <div className="bg-green-50 border-l-4 border-green-500 p-4 mt-4">
            <p className="font-semibold text-green-900">
              {isArabic ? 'المبادئ الأساسية:' : 'Core Principles:'}
            </p>
            <ul className="list-disc list-inside mt-2 text-green-800">
              <li>{isArabic ? 'الموافقة والشفافية' : 'Consent & Transparency'}</li>
              <li>{isArabic ? 'الغرض المحدد' : 'Purpose Limitation'}</li>
              <li>{isArabic ? 'الحد الأدنى للبيانات' : 'Data Minimization'}</li>
              <li>{isArabic ? 'حقوق صاحب البيانات' : 'Data Subject Rights'}</li>
              <li>{isArabic ? 'الأمن والحماية' : 'Security & Protection'}</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Controls by Domain */}
      <div className="space-y-6">
        <h2 className="text-2xl font-bold">
          {isArabic ? 'الضوابط حسب المجال' : 'Controls by Domain'}
        </h2>
        
        {Object.entries(domains).map(([domain, domainControls]: [string, any]) => (
          <div key={domain} className="bg-white rounded-lg shadow-lg overflow-hidden">
            <div className="bg-green-600 text-white px-6 py-4">
              <h3 className="text-xl font-bold">{domain}</h3>
              <p className="text-sm opacity-90">{domainControls.length} {isArabic ? 'ضوابط' : 'controls'}</p>
            </div>
            <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
              {domainControls.map((control: any) => (
                <Link
                  key={control.control_id}
                  href={`/${locale}/controls/${control.control_id}`}
                  className="block border-2 border-gray-200 rounded-lg p-4 hover:border-green-500 hover:shadow-md transition-all"
                >
                  <div className="flex justify-between items-start mb-2">
                    <span className="font-mono text-sm font-bold text-green-600">
                      {control.control_id}
                    </span>
                    <span className={`px-2 py-1 text-xs rounded-full ${
                      control.status === 'compliant'
                        ? 'bg-green-100 text-green-800'
                        : control.status === 'in_progress'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {control.status.replace('_', ' ')}
                    </span>
                  </div>
                  <h4 className="font-semibold text-gray-900 mb-2">
                    {isArabic ? control.title_ar : control.title_en}
                  </h4>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {isArabic ? control.description_ar : control.description_en}
                  </p>
                  <div className="mt-3 flex items-center justify-between text-xs text-gray-500">
                    <span>{isArabic ? 'الأولوية:' : 'Priority:'} {control.priority}</span>
                    <span>{isArabic ? 'النضج:' : 'Maturity:'} {control.maturity_level}/5</span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Resources */}
      <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-2xl font-bold mb-4">
          {isArabic ? 'الموارد والوثائق' : 'Resources & Documents'}
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <a href="https://sdaia.gov.sa/en/PDPL.html" target="_blank" className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50">
            <span className="text-xs font-semibold tracking-wide text-gray-500">DOC</span>
            <div>
              <p className="font-semibold">{isArabic ? 'نص النظام الرسمي' : 'Official Law Text'}</p>
              <p className="text-sm text-gray-600">SDAIA Website</p>
            </div>
          </a>
          <a href="#" className="flex items-center gap-3 p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50">
            <span className="text-xs font-semibold tracking-wide text-gray-500">RPT</span>
            <div>
              <p className="font-semibold">{isArabic ? 'تقرير الامتثال' : 'Compliance Report'}</p>
              <p className="text-sm text-gray-600">{isArabic ? 'تنزيل PDF' : 'Download PDF'}</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
}
