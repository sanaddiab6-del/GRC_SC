import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gradient-to-b from-white to-gray-50">
      <div className="max-w-5xl w-full space-y-8">
        <div className="text-center space-y-4">
          <h1 className="text-6xl font-bold text-gray-900">
            🛡️ SICO GRC Platform
          </h1>
          <p className="text-2xl text-gray-600">
            Saudi Regulatory Compliance Engine
          </p>
          <p className="text-lg text-gray-500">
            ECC • CCC • PDPL
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
          <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
            <h3 className="text-xl font-semibold text-green-700 mb-2">
              ECC Framework
            </h3>
            <p className="text-gray-600 text-sm mb-4">
              Essential Cybersecurity Controls by NCA
            </p>
            <div className="text-3xl font-bold text-green-600">114</div>
            <p className="text-xs text-gray-500">Controls</p>
          </div>

          <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
            <h3 className="text-xl font-semibold text-blue-700 mb-2">
              CCC Framework
            </h3>
            <p className="text-gray-600 text-sm mb-4">
              Cloud Cybersecurity Controls by NCA
            </p>
            <div className="text-3xl font-bold text-blue-600">180</div>
            <p className="text-xs text-gray-500">Controls</p>
          </div>

          <div className="p-6 bg-white rounded-lg shadow-md border border-gray-200 hover:shadow-lg transition-shadow">
            <h3 className="text-xl font-semibold text-purple-700 mb-2">
              PDPL Framework
            </h3>
            <p className="text-gray-600 text-sm mb-4">
              Personal Data Protection Law by SDAIA
            </p>
            <div className="text-3xl font-bold text-purple-600">42</div>
            <p className="text-xs text-gray-500">Controls</p>
          </div>
        </div>

        <div className="flex justify-center space-x-4 mt-8">
          <Link
            href="/dashboard"
            className="px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors"
          >
            Go to Dashboard
          </Link>
          <Link
            href="/api/docs"
            target="_blank"
            className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
          >
            View API Docs
          </Link>
        </div>

        <div className="mt-12 text-center text-sm text-gray-500">
          <p>Version 0.1.0 • Built with ❤️ for Saudi Regulatory Excellence</p>
        </div>
      </div>
    </main>
  );
}
