'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import axios from 'axios';

export default function RegisterPage() {
  const params = useParams();
  const router = useRouter();
  const locale = params.locale as string;
  const isArabic = locale === 'ar';

  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    organization: '',
    jobTitle: '',
    phone: '',
    reason: '',
  });

  const [submitted, setSubmitted] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);
  const [requestId, setRequestId] = useState<string>('');

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.fullName.trim()) {
      newErrors.fullName = isArabic ? 'الاسم الكامل مطلوب' : 'Full name is required';
    }

    if (!formData.email.trim()) {
      newErrors.email = isArabic ? 'البريد الإلكتروني مطلوب' : 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = isArabic ? 'البريد الإلكتروني غير صالح' : 'Invalid email format';
    }

    if (!formData.password) {
      newErrors.password = isArabic ? 'كلمة المرور مطلوبة' : 'Password is required';
    } else if (formData.password.length < 12) {
      newErrors.password = isArabic ? 'كلمة المرور يجب أن تكون 12 حرفاً على الأقل (ECC-IS-3)' : 'Password must be at least 12 characters (ECC-IS-3 compliant)';
    } else {
      // Check password complexity for NCA compliance
      const hasUpper = /[A-Z]/.test(formData.password);
      const hasLower = /[a-z]/.test(formData.password);
      const hasDigit = /[0-9]/.test(formData.password);
      const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(formData.password);
      
      if (!hasUpper || !hasLower || !hasDigit || !hasSpecial) {
        newErrors.password = isArabic
          ? 'كلمة المرور يجب أن تحتوي على حروف كبيرة وصغيرة وأرقام ورموز خاصة'
          : 'Password must contain uppercase, lowercase, digit, and special character';
      }
    }

    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = isArabic ? 'كلمات المرور غير متطابقة' : 'Passwords do not match';
    }

    if (!formData.organization.trim()) {
      newErrors.organization = isArabic ? 'اسم المنظمة مطلوب' : 'Organization is required';
    }

    if (!formData.jobTitle.trim()) {
      newErrors.jobTitle = isArabic ? 'المسمى الوظيفي مطلوب' : 'Job title is required';
    }

    if (!formData.reason.trim()) {
      newErrors.reason = isArabic ? 'سبب الطلب مطلوب' : 'Reason for access is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    try {
      // Submit registration request to backend API
      const response = await axios.post('http://localhost:8000/api/v1/auth/register', {
        email: formData.email,
        password: formData.password,
        full_name_en: formData.fullName,
        full_name_ar: formData.fullName
      });

      const newRequestId = `REQ-${Date.now()}`;
      setRequestId(newRequestId);

      // Store request metadata in localStorage for admin approval tracking
      // (In production, this would be handled entirely by backend)
      const existingRequests = JSON.parse(localStorage.getItem('userRequests') || '[]');
      const newRequest = {
        id: newRequestId,
        ...formData,
        userId: response.data.user_id,
        status: 'pending',
        requestDate: new Date().toISOString(),
      };
      localStorage.setItem('userRequests', JSON.stringify([...existingRequests, newRequest]));

      setSubmitted(true);
    } catch (error: any) {
      console.error('Registration failed:', error);
      const errorMessage = error.response?.data?.detail || 'Registration failed. Please try again.';
      setErrors({ submit: isArabic ? 'فشل التسجيل. حاول مرة أخرى.' : errorMessage });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    // Clear error for this field
    if (errors[e.target.name]) {
      setErrors({
        ...errors,
        [e.target.name]: '',
      });
    }
  };

  if (submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-blue-50 flex items-center justify-center p-6">
        <div className="max-w-2xl w-full bg-white rounded-2xl shadow-2xl p-12 text-center">
          <div className="text-6xl mb-6">✅</div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            {isArabic ? 'تم إرسال طلبك بنجاح!' : 'Request Submitted Successfully!'}
          </h1>
          <p className="text-gray-600 mb-8 text-lg">
            {isArabic
              ? 'تم استلام طلب التسجيل الخاص بك. سيقوم المسؤول بمراجعة طلبك والموافقة عليه قريباً. ستتلقى إشعاراً عبر البريد الإلكتروني عند الموافقة.'
              : 'Your registration request has been received. An administrator will review and approve your request shortly. You will receive an email notification once approved.'}
          </p>
          <div className="bg-blue-50 rounded-lg p-6 mb-8">
            <h3 className="font-semibold text-gray-900 mb-2">
              {isArabic ? '📋 تفاصيل الطلب' : '📋 Request Details'}
            </h3>
            <div className="text-sm text-gray-700 space-y-1">
              <p><strong>{isArabic ? 'رقم الطلب:' : 'Request ID:'}</strong> {requestId}</p>
              <p><strong>{isArabic ? 'البريد الإلكتروني:' : 'Email:'}</strong> {formData.email}</p>
              <p><strong>{isArabic ? 'الحالة:' : 'Status:'}</strong> <span className="text-yellow-600 font-semibold">{isArabic ? 'قيد المراجعة' : 'Pending Review'}</span></p>
            </div>
          </div>
          <Link
            href={`/${locale}`}
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg font-semibold transition shadow-lg"
          >
            {isArabic ? 'العودة للصفحة الرئيسية' : 'Back to Home'}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-blue-50 py-12 px-6">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <Link href={`/${locale}`} className="inline-block mb-6">
            <div className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              SICO GRC
            </div>
          </Link>
          <h1 className="text-4xl font-bold text-gray-900 mb-3">
            {isArabic ? 'طلب الوصول إلى المنصة' : 'Request Platform Access'}
          </h1>
          <p className="text-gray-600 text-lg">
            {isArabic
              ? 'املأ النموذج أدناه لطلب الوصول إلى منصة SICO GRC'
              : 'Fill out the form below to request access to the SICO GRC platform'}
          </p>
        </div>

        {/* Registration Form */}
        <div className="bg-white rounded-2xl shadow-2xl p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Full Name */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {isArabic ? 'الاسم الكامل *' : 'Full Name *'}
              </label>
              <input
                type="text"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.fullName ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder={isArabic ? 'أدخل اسمك الكامل' : 'Enter your full name'}
              />
              {errors.fullName && <p className="text-red-600 text-sm mt-1">{errors.fullName}</p>}
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {isArabic ? 'البريد الإلكتروني *' : 'Email Address *'}
              </label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder={isArabic ? 'name@company.com' : 'name@company.com'}
              />
              {errors.email && <p className="text-red-600 text-sm mt-1">{errors.email}</p>}
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {isArabic ? 'كلمة المرور *' : 'Password *'}
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.password ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder={isArabic ? '12 حرفاً على الأقل (متطلبات NCA)' : 'At least 12 characters (NCA compliant)'}
              />
              {errors.password && <p className="text-red-600 text-sm mt-1">{errors.password}</p>}
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {isArabic ? 'تأكيد كلمة المرور *' : 'Confirm Password *'}
              </label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.confirmPassword ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder={isArabic ? 'أعد إدخال كلمة المرور' : 'Re-enter password'}
              />
              {errors.confirmPassword && <p className="text-red-600 text-sm mt-1">{errors.confirmPassword}</p>}
            </div>

            {/* Organization */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {isArabic ? 'المنظمة *' : 'Organization *'}
              </label>
              <input
                type="text"
                name="organization"
                value={formData.organization}
                onChange={handleChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.organization ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder={isArabic ? 'اسم الشركة أو المؤسسة' : 'Company or institution name'}
              />
              {errors.organization && <p className="text-red-600 text-sm mt-1">{errors.organization}</p>}
            </div>

            {/* Job Title */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {isArabic ? 'المسمى الوظيفي *' : 'Job Title *'}
              </label>
              <input
                type="text"
                name="jobTitle"
                value={formData.jobTitle}
                onChange={handleChange}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.jobTitle ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder={isArabic ? 'مثال: مدير الأمن السيبراني' : 'e.g., Cybersecurity Manager'}
              />
              {errors.jobTitle && <p className="text-red-600 text-sm mt-1">{errors.jobTitle}</p>}
            </div>

            {/* Phone */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {isArabic ? 'رقم الهاتف (اختياري)' : 'Phone Number (Optional)'}
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder={isArabic ? '+966 5X XXX XXXX' : '+966 5X XXX XXXX'}
              />
            </div>

            {/* Reason for Access */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {isArabic ? 'سبب طلب الوصول *' : 'Reason for Access Request *'}
              </label>
              <textarea
                name="reason"
                value={formData.reason}
                onChange={handleChange}
                rows={4}
                className={`w-full px-4 py-3 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  errors.reason ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder={isArabic
                  ? 'اشرح لماذا تحتاج إلى الوصول إلى منصة SICO GRC...'
                  : 'Explain why you need access to the SICO GRC platform...'}
              />
              {errors.reason && <p className="text-red-600 text-sm mt-1">{errors.reason}</p>}
            </div>

            {/* Terms */}
            <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
              <p className="mb-2">
                {isArabic
                  ? 'بإرسال هذا الطلب، فإنك توافق على:'
                  : 'By submitting this request, you agree to:'}
              </p>
              <ul className="list-disc list-inside space-y-1">
                <li>{isArabic ? 'الالتزام بسياسات أمن المعلومات' : 'Comply with information security policies'}</li>
                <li>{isArabic ? 'استخدام المنصة لأغراض العمل فقط' : 'Use the platform for business purposes only'}</li>
                <li>{isArabic ? 'الحفاظ على سرية بيانات الاعتماد' : 'Maintain confidentiality of credentials'}</li>
              </ul>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-lg font-bold text-lg transition shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {isArabic ? 'جارٍ الإرسال...' : 'Submitting...'}
                </span>
              ) : (
                <>{isArabic ? '📤 إرسال الطلب' : '📤 Submit Request'}</>
              )}
            </button>

            {/* Error Message */}
            {errors.submit && (
              <div className="bg-red-50 border border-red-300 text-red-700 px-4 py-3 rounded">
                {errors.submit}
              </div>
            )}

            {/* Login Link */}
            <div className="text-center text-sm text-gray-600">
              {isArabic ? 'هل لديك حساب بالفعل؟ ' : 'Already have an account? '}
              <Link href={`/${locale}/login`} className="text-blue-600 hover:text-blue-800 font-semibold">
                {isArabic ? 'تسجيل الدخول' : 'Login'}
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
