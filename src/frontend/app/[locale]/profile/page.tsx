'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { fetchCurrentUser, logout, authFetch } from '@/lib/auth';
import type { CurrentUser } from '@/lib/auth';

export default function ProfilePage() {
  const params = useParams();
  const router = useRouter();
  const locale = params.locale as string;
  const isArabic = locale === 'ar';

  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);

  // Password change form
  const [pwForm, setPwForm] = useState({ old_password: '', new_password: '', confirm: '' });
  const [pwLoading, setPwLoading] = useState(false);
  const [pwError, setPwError] = useState('');
  const [pwSuccess, setPwSuccess] = useState('');

  useEffect(() => {
    fetchCurrentUser().then((u) => {
      if (!u) {
        router.push(`/${locale}/login`);
        return;
      }
      setUser(u);
      setLoading(false);
    });
  }, [locale, router]);

  const handleLogout = async () => {
    await logout();
    router.push(`/${locale}/login`);
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPwError('');
    setPwSuccess('');

    if (pwForm.new_password !== pwForm.confirm) {
      setPwError(isArabic ? 'كلمتا المرور غير متطابقتين' : 'Passwords do not match');
      return;
    }
    if (pwForm.new_password.length < 12) {
      setPwError(isArabic ? 'كلمة المرور يجب أن تكون 12 حرفاً على الأقل' : 'Password must be at least 12 characters');
      return;
    }

    setPwLoading(true);
    try {
      const res = await authFetch('/api/v1/auth/change-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          old_password: pwForm.old_password,
          new_password: pwForm.new_password,
        }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setPwError(data?.detail ?? (isArabic ? 'فشل تغيير كلمة المرور' : 'Failed to change password'));
      } else {
        setPwSuccess(isArabic ? 'تم تغيير كلمة المرور بنجاح' : 'Password changed successfully');
        setPwForm({ old_password: '', new_password: '', confirm: '' });
      }
    } catch {
      setPwError(isArabic ? 'خطأ في الشبكة' : 'Network error');
    } finally {
      setPwLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">
          {isArabic ? 'الملف الشخصي' : 'My Profile'}
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          {isArabic ? 'إدارة معلومات حسابك' : 'Manage your account information'}
        </p>
      </div>

      {/* Account info card */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 space-y-4">
        <h2 className="font-semibold text-gray-900 text-lg">
          {isArabic ? 'معلومات الحساب' : 'Account Information'}
        </h2>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <p className="text-xs text-gray-500 mb-1">{isArabic ? 'البريد الإلكتروني' : 'Email'}</p>
            <p className="text-sm font-medium text-gray-900">{user?.email}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">{isArabic ? 'الاسم (إنجليزي)' : 'Full Name (EN)'}</p>
            <p className="text-sm font-medium text-gray-900">{user?.full_name_en || '—'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">{isArabic ? 'الاسم (عربي)' : 'Full Name (AR)'}</p>
            <p className="text-sm font-medium text-gray-900">{user?.full_name_ar || '—'}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">{isArabic ? 'الأدوار' : 'Roles'}</p>
            <div className="flex flex-wrap gap-1">
              {user?.roles?.length ? (
                user.roles.map((r) => (
                  <span
                    key={r}
                    className="inline-block bg-blue-100 text-blue-800 text-xs font-semibold px-2 py-0.5 rounded-full"
                  >
                    {r}
                  </span>
                ))
              ) : (
                <span className="text-gray-400 text-sm">—</span>
              )}
            </div>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">{isArabic ? 'الحالة' : 'Status'}</p>
            <span className={`inline-block text-xs font-semibold px-2 py-0.5 rounded-full ${
              user?.is_active ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            }`}>
              {user?.is_active
                ? (isArabic ? 'نشط' : 'Active')
                : (isArabic ? 'قيد المراجعة' : 'Pending Approval')}
            </span>
          </div>
        </div>
      </div>

      {/* Change password card */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6">
        <h2 className="font-semibold text-gray-900 text-lg mb-4">
          {isArabic ? 'تغيير كلمة المرور' : 'Change Password'}
        </h2>

        <form onSubmit={handleChangePassword} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {isArabic ? 'كلمة المرور الحالية' : 'Current Password'}
            </label>
            <input
              type="password"
              value={pwForm.old_password}
              onChange={(e) => setPwForm({ ...pwForm, old_password: e.target.value })}
              className="w-full px-3.5 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {isArabic ? 'كلمة المرور الجديدة' : 'New Password'}
            </label>
            <input
              type="password"
              value={pwForm.new_password}
              onChange={(e) => setPwForm({ ...pwForm, new_password: e.target.value })}
              className="w-full px-3.5 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder={isArabic ? '12 حرفاً على الأقل' : 'At least 12 characters'}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {isArabic ? 'تأكيد كلمة المرور' : 'Confirm New Password'}
            </label>
            <input
              type="password"
              value={pwForm.confirm}
              onChange={(e) => setPwForm({ ...pwForm, confirm: e.target.value })}
              className="w-full px-3.5 py-2.5 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 outline-none"
              required
            />
          </div>

          {pwError && (
            <p className="text-sm text-red-600 bg-red-50 border border-red-200 px-3 py-2 rounded-lg">{pwError}</p>
          )}
          {pwSuccess && (
            <p className="text-sm text-green-700 bg-green-50 border border-green-200 px-3 py-2 rounded-lg">{pwSuccess}</p>
          )}

          <button
            type="submit"
            disabled={pwLoading}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold px-5 py-2.5 rounded-lg text-sm transition"
          >
            {pwLoading
              ? (isArabic ? 'جارٍ الحفظ…' : 'Saving…')
              : (isArabic ? 'تغيير كلمة المرور' : 'Change Password')}
          </button>
        </form>
      </div>

      {/* Logout */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 flex items-center justify-between">
        <div>
          <p className="font-semibold text-gray-900">{isArabic ? 'تسجيل الخروج' : 'Sign Out'}</p>
          <p className="text-sm text-gray-500">
            {isArabic ? 'إنهاء الجلسة الحالية' : 'End your current session'}
          </p>
        </div>
        <button
          onClick={handleLogout}
          className="bg-red-600 hover:bg-red-700 text-white font-semibold px-5 py-2.5 rounded-lg text-sm transition"
        >
          {isArabic ? 'تسجيل الخروج' : 'Log Out'}
        </button>
      </div>
    </div>
  );
}
