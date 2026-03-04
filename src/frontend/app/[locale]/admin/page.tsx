'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { AdminGuard } from '@/components/auth/AuthGuard';
import { get, post, patch } from '@/lib/api-client';
import { getErrorMessage } from '@/lib/api-client';

// ── Types ─────────────────────────────────────────────────────────────────────

interface UserResponse {
  user_id: string;
  email: string;
  full_name_en?: string | null;
  full_name_ar?: string | null;
  organization_name?: string | null;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  roles: string[];
}

interface AdminUser {
  id: string;
  name: string;
  email: string;
  role: string;
  status: string;
}

interface AdminStatsApi {
  total_users: number;
  active_users: number;
  total_controls: number;
  total_evidence: number;
  total_reports: number;
}

interface AdminStats {
  totalUsers: number;
  totalControls: number;
  totalEvidence: number;
  totalReports: number;
  activeUsers: number;
}

interface SystemStatusApi {
  backend_ok: boolean;
  database_ok: boolean;
  security_ok: boolean;
  database_size_bytes?: number | null;
}

interface SystemStatus {
  backendOk: boolean;
  databaseOk: boolean;
  securityOk: boolean;
  databaseSizeBytes: number | null;
}

interface AuditLogEntry {
  log_id: string;
  user_id?: string | null;
  action: string;
  resource: string;
  resource_id?: string | null;
  status: string;
  timestamp: string;
}

// ── Main Component ────────────────────────────────────────────────────────────

function AdminPageContent() {
  const params = useParams();
  const locale = params.locale as string;
  const isArabic = locale === 'ar';

  // ── State ───────────────────────────────────────────────────────────────────

  const [selectedTab, setSelectedTab] = useState<'users' | 'requests' | 'system' | 'settings' | 'audit'>('users');
  const [showAddUserModal, setShowAddUserModal] = useState(false);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [userRequests, setUserRequests] = useState<UserResponse[]>([]);
  const [stats, setStats] = useState<AdminStats>({
    totalUsers: 0,
    totalControls: 0,
    totalEvidence: 0,
    totalReports: 0,
    activeUsers: 0
  });
  const [userDirectory, setUserDirectory] = useState<Record<string, string>>({});
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [systemStatus, setSystemStatus] = useState<SystemStatus>({
    backendOk: false,
    databaseOk: false,
    securityOk: false,
    databaseSizeBytes: null
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    role: 'Analyst',
    password: ''
  });

  // ── Data Fetching ───────────────────────────────────────────────────────────

  useEffect(() => {
    fetchData();
  }, []);

  const formatBytes = (bytes: number | null): string => {
    if (!bytes || bytes <= 0) return isArabic ? 'غير متاح' : 'N/A';
    const units = ['B', 'KB', 'MB', 'GB', 'TB'];
    const exponent = Math.min(Math.floor(Math.log(bytes) / Math.log(1024)), units.length - 1);
    const value = bytes / Math.pow(1024, exponent);
    return `${value.toFixed(1)} ${units[exponent]}`;
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const emptyStats: AdminStatsApi = {
        total_users: 0,
        active_users: 0,
        total_controls: 0,
        total_evidence: 0,
        total_reports: 0,
      };

      const [usersData, requestsData, statsData, auditData, statusData] = await Promise.all([
        get<UserResponse[]>('/api/v1/auth/users').catch(() => []),
        get<UserResponse[]>('/api/v1/auth/pending-registrations').catch(() => []),
        get<AdminStatsApi>('/api/v1/auth/admin/stats').catch(() => emptyStats),
        get<AuditLogEntry[]>('/api/v1/auth/admin/audit-logs?limit=50').catch(() => []),
        get<SystemStatusApi>('/api/v1/auth/admin/system-status').catch(() => null),
      ]);

      const unwrap = <T,>(payload: T | { data: T }): T => {
        if (payload && typeof payload === 'object' && 'data' in payload) {
          return (payload as { data: T }).data;
        }
        return payload as T;
      };

      const rawUsers = unwrap<UserResponse[]>(usersData) || [];
      const rawRequests = unwrap<UserResponse[]>(requestsData) || [];
      const rawStats = unwrap<AdminStatsApi>(statsData) || emptyStats;
      const rawAuditLogs = unwrap<AuditLogEntry[]>(auditData) || [];
      const rawStatus = statusData ? unwrap<SystemStatusApi | null>(statusData) : null;

      const mappedUsers = rawUsers.map((user) => ({
        id: user.user_id,
        name: user.full_name_en || user.full_name_ar || user.email,
        email: user.email,
        role: user.roles?.length ? user.roles.join(', ') : (isArabic ? 'غير محدد' : 'Unassigned'),
        status: user.is_active ? 'Active' : 'Inactive',
      }));

      const directory = rawUsers.reduce<Record<string, string>>((acc, user) => {
        acc[user.user_id] = user.email;
        return acc;
      }, {});

      setUsers(mappedUsers);
      setUserDirectory(directory);
      setUserRequests(rawRequests);
      setAuditLogs(rawAuditLogs);
      setStats({
        totalUsers: rawStats.total_users || 0,
        activeUsers: rawStats.active_users || 0,
        totalControls: rawStats.total_controls || 0,
        totalEvidence: rawStats.total_evidence || 0,
        totalReports: rawStats.total_reports || 0,
      });
      setSystemStatus({
        backendOk: rawStatus?.backend_ok ?? false,
        databaseOk: rawStatus?.database_ok ?? false,
        securityOk: rawStatus?.security_ok ?? false,
        databaseSizeBytes: rawStatus?.database_size_bytes ?? null,
      });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // ── Event Handlers ──────────────────────────────────────────────────────────

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setLoading(true);
      await post('/api/v1/auth/users', {
        email: newUser.email,
        password: newUser.password,
        full_name_en: newUser.name,
        full_name_ar: isArabic ? newUser.name : undefined,
        role_name: newUser.role,
        is_active: true,
        is_verified: true,
      });
      await fetchData();
      setShowAddUserModal(false);
      setNewUser({ name: '', email: '', role: 'Analyst', password: '' });
    } catch (err) {
      alert(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleApproveUser = async (userId: string) => {
    if (!confirm(isArabic ? 'هل أنت متأكد من الموافقة على هذا المستخدم؟' : 'Are you sure you want to approve this user?')) {
      return;
    }
    try {
      setLoading(true);
      await post(`/api/v1/auth/users/${userId}/approve`, {});
      await fetchData();
    } catch (err) {
      alert(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleRejectUser = async (userId: string) => {
    if (!confirm(isArabic ? 'هل أنت متأكد من رفض هذا المستخدم؟' : 'Are you sure you want to reject this user?')) {
      return;
    }
    try {
      setLoading(true);
      await post(`/api/v1/auth/users/${userId}/deny`, {});
      await fetchData();
    } catch (err) {
      alert(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleDeactivateUser = async (userId: string) => {
    if (!confirm(isArabic ? 'هل أنت متأكد من تعطيل هذا المستخدم؟' : 'Are you sure you want to deactivate this user?')) {
      return;
    }
    try {
      setLoading(true);
      await patch(`/api/v1/auth/users/${userId}/deactivate`, {});
      await fetchData();
    } catch (err) {
      alert(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  // ── Render ──────────────────────────────────────────────────────────────────

  if (loading && !users.length) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <svg className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <p className="text-sm text-gray-500">{isArabic ? 'جاري التحقّق من الصلاحيات...' : 'Verifying permissions...'}</p>
        </div>
      </div>
    );
  }

  if (error && !users.length) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="bg-white border border-red-200 rounded-xl p-8 max-w-lg text-center shadow">
          <div className="text-4xl mb-4">⛔</div>
          <h2 className="text-xl font-bold text-red-700 mb-2">
            {isArabic ? 'خطأ في التحميل' : 'Failed to Load Admin Panel'}
          </h2>
          <p className="text-sm text-red-600 mb-4">{error}</p>
          <button
            onClick={() => fetchData()}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700"
          >
            {isArabic ? 'إعادة المحاولة' : 'Retry'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-gray-100 to-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-900 via-purple-900 to-blue-900 text-white">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold">
                {isArabic ? 'لوحة الإدارة' : 'Administration Panel'}
              </h1>
              <p className="mt-2 text-gray-200">
                {isArabic ? 'إدارة المستخدمين والنظام والإعدادات' : 'Manage users, system, and settings'}
              </p>
            </div>
            <Link
              href={`/${locale}/dashboard`}
              className="bg-white/20 hover:bg-white/30 text-white px-6 py-3 rounded-lg transition font-semibold"
            >
              {isArabic ? '← العودة للوحة التحكم' : '← Back to Dashboard'}
            </Link>
          </div>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-lg border p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">
              {isArabic ? 'المستخدمون' : 'USERS'}
            </div>
            <div className="text-3xl font-bold text-blue-600 mb-1">{stats.activeUsers}</div>
            <div className="text-sm text-gray-600">{isArabic ? 'مستخدم نشط' : 'Active Users'}</div>
          </div>

          <div className="bg-white rounded-xl shadow-lg border p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">
              {isArabic ? 'الطلبات' : 'REQUESTS'}
            </div>
            <div className="text-3xl font-bold text-orange-600 mb-1">{userRequests.length}</div>
            <div className="text-sm text-gray-600">{isArabic ? 'طلب معلق' : 'Pending Requests'}</div>
          </div>

          <div className="bg-white rounded-xl shadow-lg border p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">
              {isArabic ? 'الضوابط' : 'CONTROLS'}
            </div>
            <div className="text-3xl font-bold text-green-600 mb-1">{stats.totalControls}</div>
            <div className="text-sm text-gray-600">{isArabic ? 'إجمالي الضوابط' : 'Total Controls'}</div>
          </div>

          <div className="bg-white rounded-xl shadow-lg border p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">
              {isArabic ? 'الأدلة' : 'EVIDENCE'}
            </div>
            <div className="text-3xl font-bold text-purple-600 mb-1">{stats.totalEvidence}</div>
            <div className="text-sm text-gray-600">{isArabic ? 'ملف مرفوع' : 'Uploaded Files'}</div>
          </div>

          <div className="bg-white rounded-xl shadow-lg border p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">
              {isArabic ? 'التقارير' : 'REPORTS'}
            </div>
            <div className="text-3xl font-bold text-indigo-600 mb-1">{stats.totalReports}</div>
            <div className="text-sm text-gray-600">{isArabic ? 'تقرير منشأ' : 'Generated Reports'}</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white border-b rounded-t-xl shadow-sm">
          <nav className="flex gap-1 p-2">
            {[
              { key: 'users', label: isArabic ? 'المستخدمون' : 'Users', icon: '👥' },
              { key: 'requests', label: isArabic ? 'الطلبات المعلقة' : 'Pending Requests', icon: '⏳', badge: userRequests.length },
              { key: 'system', label: isArabic ? 'حالة النظام' : 'System Status', icon: '🖥' },
              { key: 'settings', label: isArabic ? 'الإعدادات' : 'Settings', icon: '⚙️' },
              { key: 'audit', label: isArabic ? 'سجل التدقيق' : 'Audit Log', icon: '📋' },
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setSelectedTab(tab.key as typeof selectedTab)}
                className={`relative flex-1 px-5 py-3 rounded-lg font-semibold transition ${
                  selectedTab === tab.key
                    ? 'bg-blue-600 text-white shadow-md'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
                {tab.badge !== undefined && tab.badge > 0 && (
                  <span className="absolute top-1 right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                    {tab.badge}
                  </span>
                )}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-b-xl shadow-lg p-8">
          <div className="space-y-6">
            {/* Users Tab */}
            {selectedTab === 'users' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {isArabic ? 'إدارة المستخدمين' : 'User Management'}
                  </h2>
                  <button
                    onClick={() => setShowAddUserModal(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-bold transition shadow"
                  >
                    ➕ {isArabic ? 'إضافة مستخدم' : 'Add User'}
                  </button>
                </div>

                <div className="space-y-3">
                  {users.map((user) => (
                    <div key={user.id} className="flex items-center justify-between bg-gray-50 rounded-lg p-4 border hover:shadow-md transition">
                      <div>
                        <h3 className="font-semibold text-gray-900">{user.name}</h3>
                        <p className="text-sm text-gray-600">{user.email}</p>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold">
                          {user.role}
                        </span>
                        <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                          user.status === 'Active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {user.status}
                        </span>
                        {user.status === 'Active' && (
                          <button
                            onClick={() => handleDeactivateUser(user.id)}
                            className="text-red-600 hover:text-red-800 font-semibold text-sm"
                          >
                            {isArabic ? 'تعطيل' : 'Deactivate'}
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Pending Requests Tab */}
            {selectedTab === 'requests' && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  {isArabic ? 'طلبات التسجيل المعلقة' : 'Pending Registration Requests'}
                </h2>
                {userRequests.length === 0 ? (
                  <div className="text-center py-12 bg-gray-50 rounded-xl">
                    <div className="text-6xl mb-4">✅</div>
                    <p className="text-xl font-semibold text-gray-900">
                      {isArabic ? 'لا توجد طلبات معلقة' : 'No Pending Requests'}
                    </p>
                    <p className="text-sm text-gray-600 mt-2">
                      {isArabic ? 'جميع طلبات التسجيل تم معالجتها' : 'All registration requests have been processed'}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {userRequests.map((req) => (
                      <div key={req.user_id} className="bg-gradient-to-r from-orange-50 to-yellow-50 rounded-xl p-6 border border-orange-200 shadow">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <h3 className="font-bold text-gray-900 text-lg">
                              {req.full_name_en || req.email}
                            </h3>
                            <p className="text-sm text-gray-600 mt-1">{req.email}</p>
                            {req.organization_name && (
                              <p className="text-sm text-gray-600">
                                {isArabic ? 'المنظمة:' : 'Organization:'} {req.organization_name}
                              </p>
                            )}
                            <p className="text-xs text-gray-500 mt-2">
                              {isArabic ? 'تاريخ الطلب:' : 'Requested on:'} {new Date(req.created_at).toLocaleString()}
                            </p>
                          </div>
                          <div className="flex gap-3">
                            <button
                              onClick={() => handleApproveUser(req.user_id)}
                              className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-bold transition shadow"
                            >
                              ✓ {isArabic ? 'موافقة' : 'Approve'}
                            </button>
                            <button
                              onClick={() => handleRejectUser(req.user_id)}
                              className="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-lg font-bold transition shadow"
                            >
                              ✗ {isArabic ? 'رفض' : 'Reject'}
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* System Status Tab */}
            {selectedTab === 'system' && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  {isArabic ? 'حالة النظام' : 'System Status'}
                </h2>
                <div className="space-y-6">
                  <div className="bg-gray-50 rounded-lg p-6 border">
                    <h3 className="font-semibold text-lg mb-4 text-gray-900">
                      {isArabic ? 'حالة الخدمات' : 'Service Health'}
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-700">{isArabic ? 'خدمة الواجهة الخلفية' : 'Backend Service'}</span>
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                          systemStatus.backendOk ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {systemStatus.backendOk ? '✓' : '✗'} {isArabic ? (systemStatus.backendOk ? 'نشط' : 'غير متصل') : (systemStatus.backendOk ? 'Active' : 'Down')}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-700">{isArabic ? 'قاعدة البيانات' : 'Database'}</span>
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                          systemStatus.databaseOk ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {systemStatus.databaseOk ? '✓' : '✗'} {isArabic ? (systemStatus.databaseOk ? 'نشط' : 'غير متصل') : (systemStatus.databaseOk ? 'Active' : 'Down')}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-700">{isArabic ? 'خدمة الأمان' : 'Security Service'}</span>
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                          systemStatus.securityOk ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {systemStatus.securityOk ? '✓' : '✗'} {isArabic ? (systemStatus.securityOk ? 'نشط' : 'غير متصل') : (systemStatus.securityOk ? 'Active' : 'Down')}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-6 border">
                    <h3 className="font-semibold text-lg mb-4 text-gray-900">
                      {isArabic ? 'إحصائيات قاعدة البيانات' : 'Database Statistics'}
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">{isArabic ? 'إجمالي الضوابط' : 'Total Controls'}</p>
                        <p className="text-2xl font-bold text-gray-900 mt-1">{stats.totalControls}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">{isArabic ? 'حجم قاعدة البيانات' : 'Database Size'}</p>
                        <p className="text-2xl font-bold text-gray-900 mt-1">{formatBytes(systemStatus.databaseSizeBytes)}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Settings Tab */}
            {selectedTab === 'settings' && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  {isArabic ? 'إعدادات النظام' : 'System Settings'}
                </h2>
                <div className="space-y-6">
                  <div className="bg-gray-50 rounded-lg p-6 border">
                    <h3 className="font-semibold text-lg mb-4 text-gray-900">
                      {isArabic ? 'الإعدادات العامة' : 'General Settings'}
                    </h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          {isArabic ? 'اسم المنصة' : 'Platform Name'}
                        </label>
                        <input
                          type="text"
                          defaultValue="SICO GRC Platform"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          {isArabic ? 'اللغة الافتراضية' : 'Default Language'}
                        </label>
                        <select className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                          <option value="en">English</option>
                          <option value="ar">Arabic</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-lg p-6 border">
                    <h3 className="font-semibold text-lg mb-4 text-gray-900">
                      {isArabic ? 'إعدادات الأمان' : 'Security Settings'}
                    </h3>
                    <div className="space-y-3">
                      <label className="flex items-center">
                        <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600 rounded" />
                        <span className="ml-3 text-gray-700">
                          {isArabic ? 'تفعيل المصادقة الثنائية' : 'Enable Two-Factor Authentication'}
                        </span>
                      </label>
                      <label className="flex items-center">
                        <input type="checkbox" defaultChecked className="w-5 h-5 text-blue-600 rounded" />
                        <span className="ml-3 text-gray-700">
                          {isArabic ? 'تسجيل جميع الأنشطة' : 'Log All Activities'}
                        </span>
                      </label>
                      <label className="flex items-center">
                        <input type="checkbox" className="w-5 h-5 text-blue-600 rounded" />
                        <span className="ml-3 text-gray-700">
                          {isArabic ? 'إجبار تغيير كلمة المرور' : 'Force Password Change'}
                        </span>
                      </label>
                    </div>
                  </div>

                  <button className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition shadow">
                    {isArabic ? 'حفظ الإعدادات' : 'Save Settings'}
                  </button>
                </div>
              </div>
            )}

            {/* Audit Log Tab */}
            {selectedTab === 'audit' && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  {isArabic ? 'سجل التدقيق' : 'Audit Log'}
                </h2>
                <div className="space-y-3">
                  {auditLogs.length === 0 ? (
                    <div className="text-center py-10 bg-gray-50 rounded-xl">
                      <p className="text-sm text-gray-600">
                        {isArabic ? 'لا توجد سجلات تدقيق حالياً' : 'No audit logs available'}
                      </p>
                    </div>
                  ) : (
                    auditLogs.map((log) => (
                      <div key={log.log_id} className="bg-gray-50 rounded-lg p-4 border hover:shadow-md transition">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="font-semibold text-gray-900">{log.action}</p>
                            <p className="text-sm text-gray-600 mt-1">
                              {(log.user_id && userDirectory[log.user_id]) || (isArabic ? 'النظام' : 'System')} • {new Date(log.timestamp).toLocaleString()}
                            </p>
                          </div>
                          <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                            log.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                          }`}>
                            {log.status === 'success' ? '✓' : '✗'} {log.status}
                          </span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Add User Modal */}
      {showAddUserModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-6">
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-2xl">
              <h2 className="text-2xl font-bold">
                {isArabic ? 'إضافة مستخدم جديد' : 'Add New User'}
              </h2>
              <p className="text-blue-100 mt-1">
                {isArabic ? 'املأ النموذج أدناه لإضافة مستخدم يدوياً' : 'Fill out the form below to manually add a user'}
              </p>
            </div>

            <form onSubmit={handleAddUser} className="p-6 space-y-6">
              {/* Full Name */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  {isArabic ? 'الاسم الكامل *' : 'Full Name *'}
                </label>
                <input
                  type="text"
                  value={newUser.name}
                  onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder={isArabic ? 'أدخل الاسم الكامل' : 'Enter full name'}
                  required
                />
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  {isArabic ? 'البريد الإلكتروني *' : 'Email Address *'}
                </label>
                <input
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder={isArabic ? 'name@company.com' : 'name@company.com'}
                  required
                />
              </div>

              {/* Password */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  {isArabic ? 'كلمة المرور المؤقتة *' : 'Temporary Password *'}
                </label>
                <input
                  type="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder={isArabic ? '12 حرف على الأقل' : 'At least 12 characters'}
                  required
                />
                <p className="text-sm text-gray-500 mt-1">
                  {isArabic ? 'سيُطلب من المستخدم تغيير كلمة المرور عند تسجيل الدخول الأول' : 'User will be required to change password on first login'}
                </p>
              </div>

              {/* Role */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  {isArabic ? 'الدور *' : 'Role *'}
                </label>
                <select
                  value={newUser.role}
                  onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="Admin">{isArabic ? 'مسؤول' : 'Admin'}</option>
                  <option value="Compliance Officer">{isArabic ? 'مسؤول الامتثال' : 'Compliance Officer'}</option>
                  <option value="Auditor">{isArabic ? 'مدقق' : 'Auditor'}</option>
                  <option value="Analyst">{isArabic ? 'محلل' : 'Analyst'}</option>
                  <option value="Viewer">{isArabic ? 'مشاهد' : 'Viewer'}</option>
                </select>
              </div>

              {/* Role Descriptions */}
              <div className="bg-blue-50 rounded-lg p-4 text-sm">
                <p className="font-semibold text-gray-900 mb-2">
                  {isArabic ? '📋 أدوار المستخدمين:' : '📋 User Roles:'}
                </p>
                <ul className="space-y-1 text-gray-700">
                  <li><strong>{isArabic ? 'مسؤول:' : 'Admin:'}</strong> {isArabic ? 'وصول كامل لجميع الميزات' : 'Full access to all features'}</li>
                  <li><strong>{isArabic ? 'مسؤول الامتثال:' : 'Compliance Officer:'}</strong> {isArabic ? 'إدارة الضوابط والأدلة' : 'Manage controls and evidence'}</li>
                  <li><strong>{isArabic ? 'مدقق:' : 'Auditor:'}</strong> {isArabic ? 'مراجعة وإنشاء التقارير' : 'Review and create reports'}</li>
                  <li><strong>{isArabic ? 'محلل:' : 'Analyst:'}</strong> {isArabic ? 'عرض وتحليل البيانات' : 'View and analyze data'}</li>
                  <li><strong>{isArabic ? 'مشاهد:' : 'Viewer:'}</strong> {isArabic ? 'عرض فقط' : 'View-only access'}</li>
                </ul>
              </div>

              {/* Buttons */}
              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 text-white px-8 py-3 rounded-lg font-bold transition shadow-lg"
                >
                  {loading ? (
                    <>
                      <svg className="w-5 h-5 animate-spin mr-2" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      {isArabic ? 'جاري الإضافة...' : 'Adding...'}
                    </>
                  ) : (
                    <>✅ {isArabic ? 'إضافة المستخدم' : 'Add User'}</>
                  )}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowAddUserModal(false);
                    setNewUser({ name: '', email: '', role: 'Analyst', password: '' });
                  }}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 px-8 py-3 rounded-lg font-bold transition"
                >
                  ❌ {isArabic ? 'إلغاء' : 'Cancel'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Loading Overlay */}
      {loading && (
        <div className="fixed inset-0 bg-black bg-opacity-25 flex items-center justify-center z-40">
          <div className="bg-white rounded-lg p-6 shadow-xl">
            <div className="flex items-center gap-3">
              <svg className="w-6 h-6 animate-spin text-blue-600" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              <span className="font-medium text-gray-900">
                {isArabic ? 'جاري التحديث...' : 'Updating...'}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Exported Component with AdminGuard ───────────────────────────────────────

/**
 * AdminPage with automatic role-based access control
 */
export default function AdminPage() {
  return (
    <AdminGuard>
      <AdminPageContent />
    </AdminGuard>
  );
}
