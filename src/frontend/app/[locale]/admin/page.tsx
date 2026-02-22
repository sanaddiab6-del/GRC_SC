'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import axios from 'axios';

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
  status: string;
}

interface UserRequest {
  id: string;
  fullName: string;
  email: string;
  password: string;
  organization: string;
  jobTitle: string;
  phone: string;
  reason: string;
  status: 'pending' | 'approved' | 'rejected';
  requestDate: string;
}

interface SystemStats {
  totalUsers: number;
  totalControls: number;
  totalEvidence: number;
  totalReports: number;
  activeUsers: number;
}

export default function AdminPage() {
  const params = useParams();
  const locale = params.locale as string;
  const isArabic = locale === 'ar';

  const [selectedTab, setSelectedTab] = useState<'users' | 'requests' | 'system' | 'settings' | 'audit'>('users');
  const [showAddUserModal, setShowAddUserModal] = useState(false);
  const [userRequests, setUserRequests] = useState<UserRequest[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [stats, setStats] = useState<SystemStats>({
    totalUsers: 0,
    totalControls: 0,
    totalEvidence: 0,
    totalReports: 0,
    activeUsers: 0,
  });
  
  const [newUser, setNewUser] = useState({
    name: '',
    email: '',
    role: 'Analyst',
    password: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('No authentication token found');
        return;
      }

      // Fetch users from backend
      const usersResponse = await axios.get('http://localhost:8000/api/v1/auth/users', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      const fetchedUsers = usersResponse.data.map((user: any) => ({
        id: user.user_id,
        name: user.full_name_en || user.email,
        email: user.email,
        role: user.roles && user.roles.length > 0 ? user.roles[0] : 'Viewer',
        status: user.is_active ? 'Active' : 'Inactive'
      }));
      setUsers(fetchedUsers);

      // Fetch system stats
      const controlsResponse = await fetch('http://localhost:8000/api/v1/controls?limit=1');
      const controlsData = await controlsResponse.json();
      setStats(prev => ({
        ...prev,
        totalControls: controlsData.total || 495,
        activeUsers: fetchedUsers.filter((u: any) => u.status === 'Active').length
      }));

      // Load pending user requests from localStorage (temporary until backend endpoint exists)
      const requests = JSON.parse(localStorage.getItem('userRequests') || '[]');
      setUserRequests(requests);
    } catch (error: any) {
      console.error('Failed to fetch data:', error);
      setError(error.response?.data?.detail || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleApproveRequest = async (requestId: string) => {
    const request = userRequests.find((r) => r.id === requestId);
    if (!request) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert(isArabic ? 'خطأ في المصادقة' : 'Authentication error');
        return;
      }

      // Create user via backend API
      const registerResponse = await axios.post(
        'http://localhost:8000/api/v1/auth/register',
        {
          email: request.email,
          password: request.password,
          full_name_en: request.fullName,
          full_name_ar: request.fullName
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const newUserId = registerResponse.data.user_id;

      // Assign default Analyst role
      const rolesResponse = await axios.get('http://localhost:8000/api/v1/auth/roles', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const analystRole = rolesResponse.data.find((r: any) => r.role_name === 'Analyst');
      
      if (analystRole) {
        await axios.post(
          `http://localhost:8000/api/v1/auth/users/${newUserId}/roles`,
          { user_id: newUserId, role_ids: [analystRole.role_id] },
          { headers: { Authorization: `Bearer ${token}` } }
        );
      }

      // Update request status in localStorage
      const requests = JSON.parse(localStorage.getItem('userRequests') || '[]');
      const updatedRequests = requests.map((r: UserRequest) =>
        r.id === requestId ? { ...r, status: 'approved' as const } : r
      );
      localStorage.setItem('userRequests', JSON.stringify(updatedRequests));
      setUserRequests(updatedRequests);

      // Refresh users list
      await fetchData();

      alert(isArabic ? 'تمت الموافقة على المستخدم بنجاح!' : 'User approved successfully!');
    } catch (error: any) {
      console.error('Failed to approve user:', error);
      alert(
        isArabic
          ? `فشل في الموافقة على المستخدم: ${error.response?.data?.detail || error.message}`
          : `Failed to approve user: ${error.response?.data?.detail || error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

  const handleRejectRequest = (requestId: string) => {
    const requests = JSON.parse(localStorage.getItem('userRequests') || '[]');
    const updatedRequests = requests.map((r: UserRequest) =>
      r.id === requestId ? { ...r, status: 'rejected' as const } : r
    );
    localStorage.setItem('userRequests', JSON.stringify(updatedRequests));
    setUserRequests(updatedRequests);
    
    alert(isArabic ? 'تم رفض الطلب' : 'Request rejected');
  };

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!newUser.name || !newUser.email || !newUser.password) {
      alert(isArabic ? 'الرجاء ملء جميع الحقول المطلوبة' : 'Please fill all required fields');
      return;
    }

    if (newUser.password.length < 12) {
      alert(isArabic ? 'كلمة المرور يجب أن تكون 12 حرفاً على الأقل' : 'Password must be at least 12 characters');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert(isArabic ? 'خطأ في المصادقة' : 'Authentication error');
        return;
      }

      // Create user via backend API
      const registerResponse = await axios.post(
        'http://localhost:8000/api/v1/auth/register',
        {
          email: newUser.email,
          password: newUser.password,
          full_name_en: newUser.name,
          full_name_ar: newUser.name
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const newUserId = registerResponse.data.user_id;

      // Assign selected role
      const rolesResponse = await axios.get('http://localhost:8000/api/v1/auth/roles', {
        headers: { Authorization: `Bearer ${token}` }
      });
      const selectedRole = rolesResponse.data.find((r: any) => r.role_name === newUser.role);
      
      if (selectedRole) {
        await axios.post(
          `http://localhost:8000/api/v1/auth/users/${newUserId}/roles`,
          { user_id: newUserId, role_ids: [selectedRole.role_id] },
          { headers: { Authorization: `Bearer ${token}` } }
        );
      }

      // Refresh users list
      await fetchData();

      setShowAddUserModal(false);
      setNewUser({ name: '', email: '', role: 'Analyst', password: '' });
      
      alert(isArabic ? 'تمت إضافة المستخدم بنجاح!' : 'User added successfully!');
    } catch (error: any) {
      console.error('Failed to add user:', error);
      alert(
        isArabic
          ? `فشل في إضافة المستخدم: ${error.response?.data?.detail || error.message}`
          : `Failed to add user: ${error.response?.data?.detail || error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

  const pendingRequestsCount = userRequests.filter(r => r.status === 'pending').length;

  const handleDeactivateUser = async (userId: string) => {
    const user = users.find((u) => u.id === userId);
    if (!user) return;

    const action = user.status === 'Active' ? 'deactivate' : 'activate';
    const confirmMessage = isArabic
      ? `\u0647\u0644 \u0623\u0646\u062a \u0645\u062a\u0623\u0643\u062f \u0645\u0646 ${action === 'deactivate' ? '\u062a\u0639\u0637\u064a\u0644' : '\u062a\u0641\u0639\u064a\u0644'} \u0647\u0630\u0627 \u0627\u0644\u0645\u0633\u062a\u062e\u062f\u0645\u061f`
      : `Are you sure you want to ${action} this user?`;

    if (!confirm(confirmMessage)) return;

    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        alert(isArabic ? 'خطأ في المصادقة' : 'Authentication error');
        return;
      }

      // Update user status via backend API
      await axios.patch(
        `http://localhost:8000/api/v1/auth/users/${userId}`,
        { is_active: user.status !== 'Active' },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      await fetchData();

      alert(
        isArabic
          ? `تم ${action === 'deactivate' ? 'تعطيل' : 'تفعيل'} المستخدم بنجاح`
          : `User ${action}d successfully`
      );
    } catch (error: any) {
      console.error(`Failed to ${action} user:`, error);
      alert(
        isArabic
          ? `فشل في ${action === 'deactivate' ? 'تعطيل' : 'تفعيل'} المستخدم: ${error.response?.data?.detail || error.message}`
          : `Failed to ${action} user: ${error.response?.data?.detail || error.message}`
      );
    } finally {
      setLoading(false);
    }
  };

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
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">USR</div>
            <div className="text-3xl font-bold text-blue-600 mb-1">{users.length}</div>
            <div className="text-sm text-gray-600">{isArabic ? 'إجمالي المستخدمين' : 'Total Users'}</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg border p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">CTRL</div>
            <div className="text-3xl font-bold text-purple-600 mb-1">{stats.totalControls}</div>
            <div className="text-sm text-gray-600">{isArabic ? 'الضوابط المحملة' : 'Controls Loaded'}</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg border p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">EVD</div>
            <div className="text-3xl font-bold text-green-600 mb-1">{stats.totalEvidence}</div>
            <div className="text-sm text-gray-600">{isArabic ? 'الأدلة المحملة' : 'Evidence Items'}</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg border p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">RPT</div>
            <div className="text-3xl font-bold text-orange-600 mb-1">{stats.totalReports}</div>
            <div className="text-sm text-gray-600">{isArabic ? 'التقارير المنشأة' : 'Reports Generated'}</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg border p-6">
            <div className="text-xs font-semibold tracking-wide text-gray-500 mb-2">ACT</div>
            <div className="text-3xl font-bold text-teal-600 mb-1">{users.filter(u => u.status === 'Active').length}</div>
            <div className="text-sm text-gray-600">{isArabic ? 'المستخدمون النشطون' : 'Active Users'}</div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-lg border overflow-hidden">
          <div className="border-b">
            <div className="flex overflow-x-auto">
              <button
                onClick={() => setSelectedTab('users')}
                className={`px-6 py-4 font-semibold transition whitespace-nowrap ${
                  selectedTab === 'users'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                }`}
              >
                {isArabic ? '👥 المستخدمون' : '👥 Users'}
              </button>
              <button
                onClick={() => setSelectedTab('requests')}
                className={`px-6 py-4 font-semibold transition whitespace-nowrap relative ${
                  selectedTab === 'requests'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                }`}
              >
                {isArabic ? '📥 طلبات الوصول' : '📥 Access Requests'}
                {pendingRequestsCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-600 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
                    {pendingRequestsCount}
                  </span>
                )}
              </button>
              <button
                onClick={() => setSelectedTab('system')}
                className={`px-6 py-4 font-semibold transition whitespace-nowrap ${
                  selectedTab === 'system'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                }`}
              >
                {isArabic ? '⚙️ النظام' : '⚙️ System'}
              </button>
              <button
                onClick={() => setSelectedTab('settings')}
                className={`px-6 py-4 font-semibold transition whitespace-nowrap ${
                  selectedTab === 'settings'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                }`}
              >
                {isArabic ? '🔧 الإعدادات' : '🔧 Settings'}
              </button>
              <button
                onClick={() => setSelectedTab('audit')}
                className={`px-6 py-4 font-semibold transition whitespace-nowrap ${
                  selectedTab === 'audit'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                }`}
              >
                {isArabic ? '📋 سجل التدقيق' : '📋 Audit Log'}
              </button>
            </div>
          </div>

          <div className="p-6">
            {/* Users Tab */}
            {selectedTab === 'users' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {isArabic ? 'إدارة المستخدمين' : 'User Management'}
                  </h2>
                  <button 
                    onClick={() => setShowAddUserModal(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition shadow"
                  >
                    {isArabic ? '+ إضافة مستخدم' : '+ Add User'}
                  </button>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="bg-gray-50 border-b">
                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                          {isArabic ? 'الاسم' : 'Name'}
                        </th>
                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                          {isArabic ? 'البريد الإلكتروني' : 'Email'}
                        </th>
                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                          {isArabic ? 'الدور' : 'Role'}
                        </th>
                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                          {isArabic ? 'الحالة' : 'Status'}
                        </th>
                        <th className="px-6 py-4 text-left text-sm font-semibold text-gray-700">
                          {isArabic ? 'الإجراءات' : 'Actions'}
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map((user) => (
                        <tr key={user.id} className="border-b hover:bg-gray-50 transition">
                          <td className="px-6 py-4 text-sm text-gray-900 font-medium">{user.name}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">{user.email}</td>
                          <td className="px-6 py-4">
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-800">
                              {user.role}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                              {user.status}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <button className="text-blue-600 hover:text-blue-800 font-semibold text-sm mr-4">
                              {isArabic ? 'تعديل' : 'Edit'}
                            </button>
                            <button 
                              onClick={() => handleDeactivateUser(user.id)}
                              className="text-red-600 hover:text-red-800 font-semibold text-sm"
                              disabled={loading}
                            >
                              {user.status === 'Active' ? (isArabic ? 'تعطيل' : 'Deactivate') : (isArabic ? 'تفعيل' : 'Activate')}
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Pending Requests Tab */}
            {selectedTab === 'requests' && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">
                    {isArabic ? 'طلبات وصول المستخدمين' : 'User Access Requests'}
                  </h2>
                  <div className="text-sm text-gray-600">
                    {isArabic ? `${pendingRequestsCount} طلب قيد الانتظار` : `${pendingRequestsCount} Pending Requests`}
                  </div>
                </div>

                {userRequests.length === 0 ? (
                  <div className="text-center py-12 bg-gray-50 rounded-lg border">
                    <div className="text-6xl mb-4">📥</div>
                    <p className="text-gray-600 text-lg">
                      {isArabic ? 'لا توجد طلبات وصول' : 'No access requests'}
                    </p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {userRequests.map((request) => (
                      <div key={request.id} className="bg-white border rounded-lg p-6 shadow-sm hover:shadow-md transition">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <h3 className="text-xl font-bold text-gray-900">{request.fullName}</h3>
                              <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                                request.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                                request.status === 'approved' ? 'bg-green-100 text-green-800' :
                                'bg-red-100 text-red-800'
                              }`}>
                                {request.status === 'pending' && (isArabic ? '⏳ قيد المراجعة' : '⏳ Pending')}
                                {request.status === 'approved' && (isArabic ? '✅ تمت الموافقة' : '✅ Approved')}
                                {request.status === 'rejected' && (isArabic ? '❌ مرفوض' : '❌ Rejected')}
                              </span>
                            </div>
                            <p className="text-gray-600 mb-1">✉️ {request.email}</p>
                            <p className="text-gray-600 mb-1">🏢 {request.organization}</p>
                            <p className="text-gray-600 mb-1">💼 {request.jobTitle}</p>
                            {request.phone && <p className="text-gray-600 mb-1">📱 {request.phone}</p>}
                            <p className="text-sm text-gray-500 mt-2">
                              {isArabic ? 'تاريخ الطلب:' : 'Request Date:'} {new Date(request.requestDate).toLocaleDateString()}
                            </p>
                          </div>
                        </div>

                        <div className="bg-gray-50 rounded-lg p-4 mb-4">
                          <p className="text-sm font-semibold text-gray-700 mb-2">
                            {isArabic ? 'سبب الطلب:' : 'Reason for Request:'}
                          </p>
                          <p className="text-gray-700">{request.reason}</p>
                        </div>

                        {request.status === 'pending' && (
                          <div className="flex gap-3">
                            <button
                              onClick={() => handleApproveRequest(request.id)}
                              className="flex-1 bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-semibold transition shadow"
                            >
                              ✅ {isArabic ? 'الموافقة على الطلب' : 'Approve Request'}
                            </button>
                            <button
                              onClick={() => handleRejectRequest(request.id)}
                              className="flex-1 bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-semibold transition shadow"
                            >
                              ❌ {isArabic ? 'رفض الطلب' : 'Reject Request'}
                            </button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* System Tab */}
            {selectedTab === 'system' && (
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  {isArabic ? 'معلومات النظام' : 'System Information'}
                </h2>
                <div className="space-y-6">
                  <div className="bg-gray-50 rounded-lg p-6 border">
                    <h3 className="font-semibold text-lg mb-4 text-gray-900">
                      {isArabic ? 'حالة الخدمات' : 'Service Status'}
                    </h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-gray-700">{isArabic ? 'Backend API' : 'Backend API'}</span>
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                          ✓ {isArabic ? 'متصل' : 'Online'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-700">{isArabic ? 'قاعدة البيانات' : 'Database'}</span>
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                          ✓ {isArabic ? 'متصل' : 'Connected'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-gray-700">{isArabic ? 'خدمة الأمان' : 'Security Service'}</span>
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                          ✓ {isArabic ? 'نشط' : 'Active'}
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
                        <p className="text-2xl font-bold text-gray-900 mt-1">2.4 MB</p>
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
                  {[
                    { time: '2026-02-22 14:45', user: 'admin@sico-grc.sa', action: 'User login', status: 'success' },
                    { time: '2026-02-22 14:40', user: 'admin@sico-grc.sa', action: 'Control updated: ECC-1-1', status: 'success' },
                    { time: '2026-02-22 14:35', user: 'compliance@sico-grc.sa', action: 'Evidence uploaded', status: 'success' },
                    { time: '2026-02-22 14:30', user: 'auditor@sico-grc.sa', action: 'Report generated', status: 'success' },
                  ].map((log, idx) => (
                    <div key={idx} className="bg-gray-50 rounded-lg p-4 border hover:shadow-md transition">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold text-gray-900">{log.action}</p>
                          <p className="text-sm text-gray-600 mt-1">{log.user} • {log.time}</p>
                        </div>
                        <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                          ✓ {log.status}
                        </span>
                      </div>
                    </div>
                  ))}
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
                  placeholder={isArabic ? '8 أحرف على الأقل' : 'At least 8 characters'}
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
                  className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 rounded-lg font-bold transition shadow-lg"
                >
                  ✅ {isArabic ? 'إضافة المستخدم' : 'Add User'}
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
    </div>
  );
}
