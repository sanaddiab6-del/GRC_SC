'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { loginUser, debugAuthState } from '@/lib/authService';

export default function LoginPage() {
  const params = useParams();
  const router = useRouter();
  const locale = params.locale as string;
  const isArabic = locale === 'ar';

  const [credentials, setCredentials] = useState({ email: '', password: '' });
  const [rememberMe, setRememberMe] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!credentials.email || !credentials.password) {
      setError(
        isArabic
          ? 'الرجاء إدخال البريد الإلكتروني وكلمة المرور'
          : 'Please enter your email and password'
      );
      return;
    }

    setLoading(true);

    try {
      const result = await loginUser(credentials.email, credentials.password);

      if (result.success) {
        // Debug auth state in development
        if (process.env.NODE_ENV === 'development') {
          console.log('✅ Login successful');
          debugAuthState();
        }

        // Successful login - redirect to dashboard
        // Using window.location.href to ensure proper navigation with new auth state
        window.location.href = `/${locale}/dashboard`;
      } else {
        setError(result.error || (isArabic ? 'فشل تسجيل الدخول' : 'Login failed'));
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(isArabic ? 'حدث خطأ في الاتصال' : 'Connection error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 flex items-center justify-center p-6">
      <div className="max-w-md w-full">

        {/* ── Logo / Brand ─────────────────────── */}
        <div className="text-center mb-8">
          <Link href={`/${locale}`}>
            <div className="inline-flex items-center justify-center mb-3">
              <svg className="w-11 h-11 text-blue-600" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4z" />
              </svg>
            </div>
            <div className="text-3xl font-bold text-slate-800 tracking-tight">
              SICO<span className="text-blue-600"> GRC</span>
            </div>
          </Link>
          <p className="text-slate-500 mt-1 text-sm">
            {isArabic
              ? 'منصة الحوكمة والمخاطر والامتثال للمؤسسات'
              : 'Enterprise Governance, Risk & Compliance Platform'}
          </p>
        </div>

        {/* ── Auth Card ────────────────────────── */}
        <div className="bg-white rounded-2xl shadow-xl ring-1 ring-slate-200 p-8">
          <h1 className="text-2xl font-bold text-slate-900 mb-1">
            {isArabic ? 'تسجيل الدخول' : 'Sign in to your account'}
          </h1>
          <p className="text-sm text-slate-500 mb-7">
            {isArabic ? 'أدخل بيانات اعتمادك للمتابعة' : 'Enter your credentials to continue'}
          </p>

          {error && (
            <div className="flex items-start gap-3 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 text-sm">
              <svg className="w-5 h-5 mt-0.5 shrink-0" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clipRule="evenodd" />
              </svg>
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                {isArabic ? 'البريد الإلكتروني' : 'Email address'}
              </label>
              <input
                type="email"
                autoComplete="email"
                value={credentials.email}
                onChange={(e) => { setCredentials({ ...credentials, email: e.target.value }); setError(''); }}
                className="w-full px-3.5 py-2.5 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition placeholder-slate-400"
                placeholder="you@organization.com"
                suppressHydrationWarning={true}
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                {isArabic ? 'كلمة المرور' : 'Password'}
              </label>
              <input
                type="password"
                autoComplete="current-password"
                value={credentials.password}
                onChange={(e) => { setCredentials({ ...credentials, password: e.target.value }); setError(''); }}
                className="w-full px-3.5 py-2.5 border border-slate-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition placeholder-slate-400"
                placeholder="••••••••••••"
                suppressHydrationWarning={true}
                required
              />
            </div>

            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 accent-blue-600 rounded"
                  suppressHydrationWarning={true}
                />
                <span className="text-sm text-slate-600">
                  {isArabic ? 'تذكرني' : 'Remember me'}
                </span>
              </label>
              <a href="#" className="text-sm text-blue-600 hover:text-blue-700 font-medium transition">
                {isArabic ? 'نسيت كلمة المرور؟' : 'Forgot password?'}
              </a>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-2.5 rounded-lg text-sm transition shadow-sm flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  {isArabic ? 'جارٍ التحقق…' : 'Signing in…'}
                </>
              ) : (
                isArabic ? 'تسجيل الدخول' : 'Sign in'
              )}
            </button>
          </form>

          <div className="flex items-center gap-3 my-6">
            <div className="flex-1 h-px bg-slate-200" />
            <span className="text-xs text-slate-400 uppercase tracking-wide">
              {isArabic ? 'أو' : 'or'}
            </span>
            <div className="flex-1 h-px bg-slate-200" />
          </div>

          <Link
            href={`/${locale}/register`}
            className="block w-full text-center border border-slate-300 hover:border-slate-400 text-slate-700 font-medium py-2.5 rounded-lg text-sm transition"
          >
            {isArabic ? 'طلب حساب جديد' : 'Request a new account'}
          </Link>
        </div>

        {/* ── Footer ───────────────────────────── */}
        <p className="text-center text-xs text-slate-400 mt-6">
          © {new Date().getFullYear()} SICO GRC Platform. All rights reserved.
        </p>
      </div>
    </div>
  );
}
