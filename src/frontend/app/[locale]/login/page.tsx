'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LoginPage() {
  const params = useParams();
  const router = useRouter();
  const locale = params.locale as string;
  const isArabic = locale === 'ar';

  const [credentials, setCredentials] = useState({
    email: '',
    password: '',
  });
  const [error, setError] = useState('');

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Simple validation (will be replaced with real authentication)
    if (!credentials.email || !credentials.password) {
      setError(isArabic ? 'الرجاء إدخال البريد الإلكتروني وكلمة المرور' : 'Please enter email and password');
      return;
    }

    // For demo purposes, accept any login
    // In production, this would validate against backend
    router.push(`/${locale}/dashboard`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-blue-50 flex items-center justify-center p-6">
      <div className="max-w-md w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href={`/${locale}`}>
            <div className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
              SICO GRC
            </div>
          </Link>
          <p className="text-gray-600">
            {isArabic ? 'منصة الحوكمة والمخاطر والامتثال' : 'Governance, Risk & Compliance Platform'}
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-6 text-center">
            {isArabic ? 'تسجيل الدخول' : 'Login'}
          </h1>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-6">
            {/* Email */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {isArabic ? 'البريد الإلكتروني' : 'Email Address'}
              </label>
              <input
                type="email"
                value={credentials.email}
                onChange={(e) => {
                  setCredentials({ ...credentials, email: e.target.value });
                  setError('');
                }}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder={isArabic ? 'name@company.com' : 'name@company.com'}
              />
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {isArabic ? 'كلمة المرور' : 'Password'}
              </label>
              <input
                type="password"
                value={credentials.password}
                onChange={(e) => {
                  setCredentials({ ...credentials, password: e.target.value });
                  setError('');
                }}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder={isArabic ? '••••••••' : '••••••••'}
              />
            </div>

            {/* Remember Me */}
            <div className="flex items-center justify-between">
              <label className="flex items-center">
                <input type="checkbox" className="w-4 h-4 text-blue-600 rounded" />
                <span className="ml-2 text-sm text-gray-700">
                  {isArabic ? 'تذكرني' : 'Remember me'}
                </span>
              </label>
              <a href="#" className="text-sm text-blue-600 hover:text-blue-800 font-semibold">
                {isArabic ? 'نسيت كلمة المرور؟' : 'Forgot password?'}
              </a>
            </div>

            {/* Login Button */}
            <button
              type="submit"
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-lg font-bold text-lg transition shadow-lg"
            >
              {isArabic ? '🔓 تسجيل الدخول' : '🔓 Login'}
            </button>
          </form>

          {/* Divider */}
          <div className="relative my-8">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white text-gray-500">
                {isArabic ? 'أو' : 'OR'}
              </span>
            </div>
          </div>

          {/* Register Link */}
          <div className="text-center">
            <p className="text-gray-600 mb-3">
              {isArabic ? 'ليس لديك حساب؟' : "Don't have an account?"}
            </p>
            <Link
              href={`/${locale}/register`}
              className="inline-block bg-gray-100 hover:bg-gray-200 text-gray-800 px-8 py-3 rounded-lg font-semibold transition"
            >
              {isArabic ? '📝 طلب وصول جديد' : '📝 Request Access'}
            </Link>
          </div>
        </div>

        {/* Demo Credentials */}
        <div className="mt-6 bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm">
          <p className="font-semibold text-yellow-900 mb-2">
            {isArabic ? '💡 للمعاينة - استخدم أي بيانات تسجيل دخول' : '💡 Demo Mode - Use any credentials'}
          </p>
          <p className="text-yellow-800">
            {isArabic 
              ? 'يمكنك استخدام أي بريد إلكتروني وكلمة مرور للدخول إلى المنصة'
              : 'You can use any email and password to access the platform'}
          </p>
        </div>
      </div>
    </div>
  );
}
