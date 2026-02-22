'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

interface ControlEditModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  locale: 'en' | 'ar';
  controlData: {
    control_id: string;
    framework: string;
    domain: string;
    title_en: string;
    title_ar: string;
    description_en: string;
    description_ar: string;
    status: string;
    maturity_level?: number;
  };
}

const STATUS_OPTIONS = [
  { value: 'not_started', label_en: 'Not Started', label_ar: 'لم يبدأ' },
  { value: 'in_progress', label_en: 'In Progress', label_ar: 'قيد التنفيذ' },
  { value: 'compliant', label_en: 'Compliant', label_ar: 'متوافق' },
  { value: 'non_compliant', label_en: 'Non-Compliant', label_ar: 'غير متوافق' },
  { value: 'not_applicable', label_en: 'Not Applicable', label_ar: 'غير قابل للتطبيق' },
];

export default function ControlEditModal({
  isOpen,
  onClose,
  onSuccess,
  locale,
  controlData,
}: ControlEditModalProps) {
  const isArabic = locale === 'ar';

  const [formData, setFormData] = useState({
    title_en: '',
    title_ar: '',
    description_en: '',
    description_ar: '',
    status: 'not_started',
    maturity_level: 1,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Load control data when modal opens
  useEffect(() => {
    if (isOpen && controlData) {
      setFormData({
        title_en: controlData.title_en || '',
        title_ar: controlData.title_ar || '',
        description_en: controlData.description_en || '',
        description_ar: controlData.description_ar || '',
        status: controlData.status || 'not_started',
        maturity_level: controlData.maturity_level || 1,
      });
      setError('');
    }
  }, [isOpen, controlData]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'maturity_level' ? parseInt(value) || 1 : value,
    }));
    if (error) setError('');
  };

  const validateForm = (): boolean => {
    if (!formData.title_en.trim() || formData.title_en.length < 5) {
      setError(
        isArabic
          ? 'العنوان بالإنجليزية مطلوب (5 أحرف على الأقل)'
          : 'English title is required (min 5 characters)'
      );
      return false;
    }
    if (!formData.title_ar.trim() || formData.title_ar.length < 5) {
      setError(
        isArabic
          ? 'العنوان بالعربية مطلوب (5 أحرف على الأقل)'
          : 'Arabic title is required (min 5 characters)'
      );
      return false;
    }
    if (!formData.description_en.trim() || formData.description_en.length < 10) {
      setError(
        isArabic
          ? 'الوصف بالإنجليزية مطلوب (10 أحرف على الأقل)'
          : 'English description is required (min 10 characters)'
      );
      return false;
    }
    if (!formData.description_ar.trim() || formData.description_ar.length < 10) {
      setError(
        isArabic
          ? 'الوصف بالعربية مطلوب (10 أحرف على الأقل)'
          : 'Arabic description is required (min 10 characters)'
      );
      return false;
    }
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');

      // Prepare request body with only changed fields
      const requestBody: any = {};
      
      if (formData.title_en !== controlData.title_en) {
        requestBody.title_en = formData.title_en;
      }
      if (formData.title_ar !== controlData.title_ar) {
        requestBody.title_ar = formData.title_ar;
      }
      if (formData.description_en !== controlData.description_en) {
        requestBody.description_en = formData.description_en;
      }
      if (formData.description_ar !== controlData.description_ar) {
        requestBody.description_ar = formData.description_ar;
      }
      if (formData.status !== controlData.status) {
        requestBody.status = formData.status;
      }
      if (formData.maturity_level !== controlData.maturity_level) {
        requestBody.maturity_level = formData.maturity_level;
      }

      // Only send request if there are changes
      if (Object.keys(requestBody).length === 0) {
        setError(
          isArabic
            ? 'لا توجد تغييرات لحفظها'
            : 'No changes to save'
        );
        setLoading(false);
        return;
      }

      const response = await axios.patch(
        `http://localhost:8000/api/v1/controls/${controlData.control_id}`,
        requestBody,
        {
          headers: {
            'Content-Type': 'application/json',
            ...(token && { Authorization: `Bearer ${token}` }),
          },
        }
      );

      if (response.status === 200) {
        showSuccessToast(
          isArabic
            ? 'تم تحديث الضابط بنجاح'
            : 'Control updated successfully'
        );

        onSuccess();
        onClose();
      }
    } catch (err: any) {
      console.error('Update failed:', err);
      const errorMessage =
        err.response?.data?.detail?.message_en ||
        err.response?.data?.detail ||
        (isArabic
          ? 'فشل تحديث الضابط. يرجى المحاولة مرة أخرى.'
          : 'Failed to update control. Please try again.');
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const showSuccessToast = (message: string) => {
    const toast = document.createElement('div');
    toast.className =
      'fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in';
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.remove();
    }, 3000);
  };

  const handleClose = () => {
    if (!loading) {
      setError('');
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">
                {isArabic ? 'تعديل الضابط' : 'Edit Control'}
              </h2>
              <p className="text-white/90 mt-1">
                {controlData.control_id} - {controlData.framework}
              </p>
            </div>
            <button
              onClick={handleClose}
              disabled={loading}
              className="text-white hover:text-gray-200 transition text-2xl font-bold"
            >
              ×
            </button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Read-only Info */}
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600 font-semibold">
                  {isArabic ? 'معرف الضابط:' : 'Control ID:'}
                </p>
                <p className="text-gray-900 font-mono">{controlData.control_id}</p>
              </div>
              <div>
                <p className="text-gray-600 font-semibold">
                  {isArabic ? 'الإطار:' : 'Framework:'}
                </p>
                <p className="text-gray-900">{controlData.framework}</p>
              </div>
              <div className="col-span-2">
                <p className="text-gray-600 font-semibold">
                  {isArabic ? 'المجال:' : 'Domain:'}
                </p>
                <p className="text-gray-900">{controlData.domain}</p>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {isArabic
                ? 'ملاحظة: معرف الضابط والإطار والمجال غير قابلة للتعديل'
                : 'Note: Control ID, Framework, and Domain are not editable'}
            </p>
          </div>

          {/* English Title */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {isArabic ? 'العنوان (إنجليزي) *' : 'Title (English) *'}
            </label>
            <input
              type="text"
              name="title_en"
              value={formData.title_en}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Enter English title..."
              required
              minLength={5}
            />
          </div>

          {/* Arabic Title */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {isArabic ? 'العنوان (عربي) *' : 'Title (Arabic) *'}
            </label>
            <input
              type="text"
              name="title_ar"
              value={formData.title_ar}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="أدخل العنوان بالعربية..."
              required
              minLength={5}
              dir="rtl"
            />
          </div>

          {/* English Description */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {isArabic ? 'الوصف (إنجليزي) *' : 'Description (English) *'}
            </label>
            <textarea
              name="description_en"
              value={formData.description_en}
              onChange={handleInputChange}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="Enter detailed description in English..."
              required
              minLength={10}
            />
          </div>

          {/* Arabic Description */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {isArabic ? 'الوصف (عربي) *' : 'Description (Arabic) *'}
            </label>
            <textarea
              name="description_ar"
              value={formData.description_ar}
              onChange={handleInputChange}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              placeholder="أدخل وصفاً تفصيلياً بالعربية..."
              required
              minLength={10}
              dir="rtl"
            />
          </div>

          {/* Status and Maturity Grid */}
          <div className="grid grid-cols-2 gap-4">
            {/* Status */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {isArabic ? 'الحالة *' : 'Status *'}
              </label>
              <select
                name="status"
                value={formData.status}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                required
              >
                {STATUS_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {isArabic ? option.label_ar : option.label_en}
                  </option>
                ))}
              </select>
            </div>

            {/* Maturity Level */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {isArabic ? 'مستوى النضج (1-5)' : 'Maturity Level (1-5)'}
              </label>
              <select
                name="maturity_level"
                value={formData.maturity_level}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value={1}>1 - {isArabic ? 'مبدئي' : 'Initial'}</option>
                <option value={2}>2 - {isArabic ? 'مُدار' : 'Managed'}</option>
                <option value={3}>3 - {isArabic ? 'مُعرّف' : 'Defined'}</option>
                <option value={4}>4 - {isArabic ? 'قابل للقياس' : 'Quantitatively Managed'}</option>
                <option value={5}>5 - {isArabic ? 'محسّن' : 'Optimizing'}</option>
              </select>
            </div>
          </div>

          {/* Info Box */}
          <div className="bg-blue-50 rounded-lg p-4 text-sm text-gray-700">
            <p className="font-semibold mb-2">
              {isArabic ? '📋 ملاحظة:' : '📋 Note:'}
            </p>
            <ul className="list-disc list-inside space-y-1 text-xs">
              <li>
                {isArabic
                  ? 'يرجى ملء الحقول بكلا اللغتين (إنجليزي وعربي)'
                  : 'Please fill in fields in both languages (English and Arabic)'}
              </li>
              <li>
                {isArabic
                  ? 'يتم إرسال الحقول المتغيرة فقط إلى الخادم'
                  : 'Only changed fields will be sent to the server'}
              </li>
              <li>
                {isArabic
                  ? 'الحد الأدنى للعنوان 5 أحرف، وللوصف 10 أحرف'
                  : 'Minimum 5 characters for titles, 10 for descriptions'}
              </li>
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white px-8 py-3 rounded-lg font-bold transition shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  {isArabic ? 'جاري الحفظ...' : 'Saving...'}
                </>
              ) : (
                <>
                  <svg
                    className="w-5 h-5 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                  {isArabic ? 'حفظ التغييرات' : 'Save Changes'}
                </>
              )}
            </button>
            <button
              type="button"
              onClick={handleClose}
              disabled={loading}
              className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 px-8 py-3 rounded-lg font-bold transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isArabic ? 'إلغاء' : 'Cancel'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
