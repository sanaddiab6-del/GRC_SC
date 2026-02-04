export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="max-w-5xl w-full text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-6xl font-bold text-gray-900">
            🛡️ SICO GRC Platform
          </h1>
          <p className="text-2xl text-gray-600">
            Saudi Regulatory Compliance Engine
          </p>
          <p className="text-xl text-gray-500">
            منصة سيكو للحوكمة والمخاطر والامتثال
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
            <div className="text-4xl mb-4">🔐</div>
            <h3 className="text-xl font-semibold mb-2">ECC 3.0</h3>
            <p className="text-gray-600">Essential Cybersecurity Controls</p>
            <p className="text-sm text-gray-500 mt-2">الضوابط الأساسية للأمن السيبراني</p>
          </div>

          <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
            <div className="text-4xl mb-4">☁️</div>
            <h3 className="text-xl font-semibold mb-2">CCC 1.0</h3>
            <p className="text-gray-600">Cloud Cybersecurity Controls</p>
            <p className="text-sm text-gray-500 mt-2">ضوابط الأمن السيبراني السحابي</p>
          </div>

          <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200">
            <div className="text-4xl mb-4">🔒</div>
            <h3 className="text-xl font-semibold mb-2">PDPL 2023</h3>
            <p className="text-gray-600">Personal Data Protection Law</p>
            <p className="text-sm text-gray-500 mt-2">نظام حماية البيانات الشخصية</p>
          </div>
        </div>

        <div className="mt-12 space-y-4">
          <h2 className="text-2xl font-semibold text-gray-800">Key Features</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="p-4 bg-blue-50 rounded">
              <p className="font-medium">Unified Control Library</p>
            </div>
            <div className="p-4 bg-green-50 rounded">
              <p className="font-medium">ECC-CCC Baseline</p>
            </div>
            <div className="p-4 bg-purple-50 rounded">
              <p className="font-medium">PDPL Registers</p>
            </div>
            <div className="p-4 bg-orange-50 rounded">
              <p className="font-medium">Evidence Automation</p>
            </div>
            <div className="p-4 bg-pink-50 rounded">
              <p className="font-medium">SOC-GRC Bridge</p>
            </div>
            <div className="p-4 bg-indigo-50 rounded">
              <p className="font-medium">Bilingual AI</p>
            </div>
            <div className="p-4 bg-yellow-50 rounded">
              <p className="font-medium">Executive Reporting</p>
            </div>
            <div className="p-4 bg-red-50 rounded">
              <p className="font-medium">Audit Ready</p>
            </div>
          </div>
        </div>

        <div className="mt-12 pt-8 border-t border-gray-200">
          <p className="text-sm text-gray-500">
            Version 0.1.0-alpha | Phase: Foundation & Regulatory Preparation
          </p>
          <p className="text-xs text-gray-400 mt-2">
            © 2026 SICO Security - All Rights Reserved
          </p>
        </div>
      </div>
    </main>
  )
}
