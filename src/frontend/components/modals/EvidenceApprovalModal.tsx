'use client';

import { useState } from 'react';
import axios from 'axios';

interface EvidenceApprovalModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  evidenceId: string;
  evidenceTitle: string;
  action: 'approve' | 'reject';
  locale: 'en' | 'ar';
}

export default function EvidenceApprovalModal({
  isOpen,
  onClose,
  onSuccess,
  evidenceId,
  evidenceTitle,
  action,
  locale,
}: EvidenceApprovalModalProps) {
  const isArabic = locale === 'ar';
  const [comments, setComments] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const isApprove = action === 'approve';

  const handleSubmit = async () => {
    if (!comments.trim()) {
      setError(isArabic ? 'التعليقات مطلوبة' : 'Comments are required');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Get auth token from localStorage
      const token = localStorage.getItem('access_token');
      
      // Get current user for validated_by field
      const currentUser = localStorage.getItem('currentUser');
      let validatedBy = 'system';
      if (currentUser) {
        try {
          const userData = JSON.parse(currentUser);
          validatedBy = userData.email || userData.name || 'system';
        } catch {
          validatedBy = 'system';
        }
      }

      const response = await axios.post(
        `http://localhost:8000/api/v1/evidence/${evidenceId}/validate`,
        {
          approved: isApprove, // Backend expects boolean
          validation_notes: comments,
          validated_by: validatedBy,
        },
        {
          headers: {
            'Content-Type': 'application/json',
            ...(token && { Authorization: `Bearer ${token}` }),
          },
        }
      );

      if (response.status === 200 || response.status === 201) {
        // Success - show toast
        showSuccessToast(
          isApprove
            ? isArabic
              ? 'تمت الموافقة على الدليل بنجاح'
              : 'Evidence approved successfully'
            : isArabic
            ? 'تم رفض الدليل'
            : 'Evidence rejected'
        );

        // Reset form
        setComments('');

        // Notify parent
        onSuccess();

        // Close modal
        onClose();
      }
    } catch (err: any) {
      console.error('Validation failed:', err);
      const errorMessage =
        err.response?.data?.detail ||
        (isArabic
          ? 'فشلت عملية التحقق. يرجى المحاولة مرة أخرى.'
          : 'Validation failed. Please try again.');
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
      setComments('');
      setError('');
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-xl w-full">
        {/* Header */}
        <div
          className={`sticky top-0 ${
            isApprove
              ? 'bg-gradient-to-r from-green-600 to-emerald-600'
              : 'bg-gradient-to-r from-red-600 to-rose-600'
          } text-white p-6 rounded-t-2xl`}
        >
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">
                {isApprove
                  ? isArabic
                    ? 'الموافقة على الدليل'
                    : 'Approve Evidence'
                  : isArabic
                  ? 'رفض الدليل'
                  : 'Reject Evidence'}
              </h2>
              <p className="text-white/90 mt-1 text-sm">
                {isArabic
                  ? 'قدم تعليقاتك للمراجعة'
                  : 'Provide your comments for review'}
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

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Evidence Info */}
          <div className="bg-gray-50 rounded-lg p-4">
            <p className="text-sm font-semibold text-gray-700 mb-1">
              {isArabic ? 'الدليل:' : 'Evidence:'}
            </p>
            <p className="text-gray-900 font-medium">{evidenceTitle}</p>
            <p className="text-xs text-gray-500 mt-1">
              {isArabic ? 'المعرف:' : 'ID:'} {evidenceId}
            </p>
          </div>

          {/* Confirmation Message */}
          <div
            className={`${
              isApprove ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
            } border rounded-lg p-4`}
          >
            <div className="flex items-start">
              <svg
                className={`w-6 h-6 ${
                  isApprove ? 'text-green-600' : 'text-red-600'
                } mr-3 mt-0.5 flex-shrink-0`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                {isApprove ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                )}
              </svg>
              <div>
                <p
                  className={`font-semibold ${
                    isApprove ? 'text-green-900' : 'text-red-900'
                  }`}
                >
                  {isApprove
                    ? isArabic
                      ? 'هل أنت متأكد من الموافقة على هذا الدليل؟'
                      : 'Are you sure you want to approve this evidence?'
                    : isArabic
                    ? 'هل أنت متأكد من رفض هذا الدليل؟'
                    : 'Are you sure you want to reject this evidence?'}
                </p>
                <p
                  className={`text-sm mt-1 ${
                    isApprove ? 'text-green-700' : 'text-red-700'
                  }`}
                >
                  {isApprove
                    ? isArabic
                      ? 'سيتم قبول الدليل وسيكون متاحاً للاستخدام في التقارير.'
                      : 'The evidence will be accepted and available for use in reports.'
                    : isArabic
                    ? 'سيتم رفض الدليل وسيحتاج إلى مراجعة إضافية.'
                    : 'The evidence will be rejected and will require additional review.'}
                </p>
              </div>
            </div>
          </div>

          {/* Comments Textarea */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {isArabic ? 'التعليقات *' : 'Comments *'}
            </label>
            <textarea
              value={comments}
              onChange={(e) => {
                setComments(e.target.value);
                if (error) setError('');
              }}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder={
                isApprove
                  ? isArabic
                    ? 'أدخل تعليقات الموافقة (مثال: الدليل مكتمل ويستوفي جميع المتطلبات)'
                    : 'Enter approval comments (e.g., Evidence is complete and meets all requirements)'
                  : isArabic
                  ? 'أدخل سبب الرفض (مثال: الدليل غير مكتمل أو يفتقد معلومات مهمة)'
                  : 'Enter rejection reason (e.g., Evidence is incomplete or missing critical information)'
              }
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              {isArabic
                ? 'التعليقات مطلوبة للتدقيق والمراجعة المستقبلية'
                : 'Comments are required for audit trail and future review'}
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              onClick={handleSubmit}
              disabled={loading || !comments.trim()}
              className={`flex-1 ${
                isApprove
                  ? 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700'
                  : 'bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700'
              } text-white px-8 py-3 rounded-lg font-bold transition shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center`}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  {isArabic ? 'جاري المعالجة...' : 'Processing...'}
                </>
              ) : (
                <>
                  <svg
                    className="w-5 h-5 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    {isApprove ? (
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    ) : (
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    )}
                  </svg>
                  {isApprove
                    ? isArabic
                      ? 'تأكيد الموافقة'
                      : 'Confirm Approval'
                    : isArabic
                    ? 'تأكيد الرفض'
                    : 'Confirm Rejection'}
                </>
              )}
            </button>
            <button
              onClick={handleClose}
              disabled={loading}
              className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 px-8 py-3 rounded-lg font-bold transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isArabic ? 'إلغاء' : 'Cancel'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
