'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

interface RiskAssessmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  locale: 'en' | 'ar';
  riskId: string;
  currentLikelihood?: number;
  currentImpact?: number;
}

export default function RiskAssessmentModal({
  isOpen,
  onClose,
  onSuccess,
  locale,
  riskId,
  currentLikelihood = 3,
  currentImpact = 3,
}: RiskAssessmentModalProps) {
  const isArabic = locale === 'ar';

  const [formData, setFormData] = useState({
    likelihood: currentLikelihood,
    impact: currentImpact,
    justification: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Update form data when current values change
  useEffect(() => {
    if (isOpen) {
      setFormData({
        likelihood: currentLikelihood,
        impact: currentImpact,
        justification: '',
      });
      setError('');
    }
  }, [isOpen, currentLikelihood, currentImpact]);

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'likelihood' || name === 'impact' ? parseInt(value) || 1 : value,
    }));
    if (error) setError('');
  };

  const calculateRiskScore = () => {
    return formData.likelihood * formData.impact;
  };

  const getRiskLevel = (score: number) => {
    if (score >= 20) return { label: isArabic ? 'حرج' : 'Critical', color: 'text-red-600' };
    if (score >= 12) return { label: isArabic ? 'عالي' : 'High', color: 'text-orange-600' };
    if (score >= 6) return { label: isArabic ? 'متوسط' : 'Medium', color: 'text-yellow-600' };
    return { label: isArabic ? 'منخفض' : 'Low', color: 'text-green-600' };
  };

  const validateForm = (): boolean => {
    if (!formData.justification.trim() || formData.justification.length < 10) {
      setError(
        isArabic
          ? 'المبرر مطلوب (10 أحرف على الأقل)'
          : 'Justification is required (min 10 characters)'
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
      const token = sessionStorage.getItem('access_token');

      const response = await axios.post(
        `http://localhost:8000/api/v1/risks/${riskId}/assess`,
        {
          likelihood: formData.likelihood,
          impact: formData.impact,
          justification: formData.justification,
        },
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
            ? 'تم تقييم المخاطرة بنجاح'
            : 'Risk assessed successfully'
        );

        // Reset form
        setFormData({
          likelihood: currentLikelihood,
          impact: currentImpact,
          justification: '',
        });

        onSuccess();
        onClose();
      }
    } catch (err: any) {
      console.error('Assessment failed:', err);
      const errorMessage =
        err.response?.data?.detail ||
        (isArabic
          ? 'فشل تقييم المخاطرة. يرجى المحاولة مرة أخرى.'
          : 'Failed to assess risk. Please try again.');
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
      setFormData({
        likelihood: currentLikelihood,
        impact: currentImpact,
        justification: '',
      });
      setError('');
      onClose();
    }
  };

  if (!isOpen) return null;

  const riskScore = calculateRiskScore();
  const riskLevel = getRiskLevel(riskScore);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-indigo-600 text-white p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">
                {isArabic ? 'تقييم المخاطرة' : 'Assess Risk'}
              </h2>
              <p className="text-white/90 mt-1">
                {isArabic
                  ? 'قم بتحديث احتمالية وتأثير المخاطرة'
                  : 'Update likelihood and impact assessment'}
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

          {/* Info Box */}
          <div className="bg-blue-50 rounded-lg p-4 text-sm text-gray-700">
            <p className="font-semibold mb-2">
              {isArabic ? '📊 نظرة عامة:' : '📊 Overview:'}
            </p>
            <ul className="list-disc list-inside space-y-1 text-xs">
              <li>
                {isArabic
                  ? 'قيّم الاحتمالية والتأثير الحالي للمخاطرة'
                  : 'Assess the current likelihood and impact of the risk'}
              </li>
              <li>
                {isArabic
                  ? 'يتم حساب درجة المخاطرة تلقائياً (الاحتمالية × التأثير)'
                  : 'Risk score is calculated automatically (likelihood × impact)'}
              </li>
              <li>
                {isArabic
                  ? 'المبرر مطلوب لتوثيق سبب التقييم'
                  : 'Justification is required to document the assessment rationale'}
              </li>
            </ul>
          </div>

          {/* Risk Assessment Grid */}
          <div className="grid grid-cols-2 gap-4">
            {/* Likelihood */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {isArabic ? 'الاحتمالية (1-5) *' : 'Likelihood (1-5) *'}
              </label>
              <select
                name="likelihood"
                value={formData.likelihood}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value={1}>{isArabic ? '1 - نادر جداً' : '1 - Very Rare'}</option>
                <option value={2}>{isArabic ? '2 - نادر' : '2 - Rare'}</option>
                <option value={3}>{isArabic ? '3 - محتمل' : '3 - Possible'}</option>
                <option value={4}>{isArabic ? '4 - مرجح' : '4 - Likely'}</option>
                <option value={5}>{isArabic ? '5 - شبه مؤكد' : '5 - Almost Certain'}</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">
                {isArabic
                  ? 'احتمالية وقوع المخاطرة'
                  : 'Probability of the risk occurring'}
              </p>
            </div>

            {/* Impact */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {isArabic ? 'التأثير (1-5) *' : 'Impact (1-5) *'}
              </label>
              <select
                name="impact"
                value={formData.impact}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value={1}>{isArabic ? '1 - ضئيل' : '1 - Insignificant'}</option>
                <option value={2}>{isArabic ? '2 - بسيط' : '2 - Minor'}</option>
                <option value={3}>{isArabic ? '3 - متوسط' : '3 - Moderate'}</option>
                <option value={4}>{isArabic ? '4 - كبير' : '4 - Major'}</option>
                <option value={5}>{isArabic ? '5 - كارثي' : '5 - Catastrophic'}</option>
              </select>
              <p className="text-xs text-gray-500 mt-1">
                {isArabic
                  ? 'حجم التأثير إذا حدثت المخاطرة'
                  : 'Magnitude of impact if risk occurs'}
              </p>
            </div>
          </div>

          {/* Risk Score Display */}
          <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg p-5 border-2 border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 font-semibold">
                  {isArabic ? 'درجة المخاطرة المحدثة:' : 'Updated Risk Score:'}
                </p>
                <p className="text-4xl font-bold text-gray-900 mt-1">{riskScore}</p>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-600 font-semibold">
                  {isArabic ? 'مستوى المخاطرة:' : 'Risk Level:'}
                </p>
                <p className={`text-3xl font-bold ${riskLevel.color} mt-1`}>{riskLevel.label}</p>
              </div>
            </div>
            <div className="mt-3 pt-3 border-t border-gray-300">
              <p className="text-xs text-gray-500">
                {isArabic
                  ? `الصيغة: ${formData.likelihood} (احتمالية) × ${formData.impact} (تأثير) = ${riskScore}`
                  : `Formula: ${formData.likelihood} (likelihood) × ${formData.impact} (impact) = ${riskScore}`}
              </p>
            </div>
          </div>

          {/* Justification */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {isArabic ? 'المبرر *' : 'Justification *'}
            </label>
            <textarea
              name="justification"
              value={formData.justification}
              onChange={handleInputChange}
              rows={4}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={
                isArabic
                  ? 'اشرح سبب هذا التقييم، بما في ذلك أي عوامل أو أدلة جديدة...'
                  : 'Explain the rationale for this assessment, including any new factors or evidence...'
              }
              required
              minLength={10}
            />
            <p className="text-xs text-gray-500 mt-1">
              {isArabic
                ? 'يُرجى تقديم مبرر تفصيلي لتوثيق التقييم (10 أحرف على الأقل)'
                : 'Please provide detailed justification to document the assessment (min 10 characters)'}
            </p>
          </div>

          {/* Warning if scores changed significantly */}
          {(Math.abs(formData.likelihood - currentLikelihood) >= 2 ||
            Math.abs(formData.impact - currentImpact) >= 2) && (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start">
                <svg
                  className="w-5 h-5 text-yellow-600 mr-2 flex-shrink-0"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
                <div>
                  <p className="text-sm font-semibold text-yellow-800">
                    {isArabic ? 'تغيير كبير في التقييم' : 'Significant Assessment Change'}
                  </p>
                  <p className="text-xs text-yellow-700 mt-1">
                    {isArabic
                      ? 'لقد قمت بتعديل التقييم بشكل كبير. يُرجى التأكد من أن المبرر يوثق هذا التغيير بوضوح.'
                      : 'You have significantly modified the assessment. Please ensure your justification clearly documents this change.'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white px-8 py-3 rounded-lg font-bold transition shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  {isArabic ? 'جاري التقييم...' : 'Assessing...'}
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
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                  {isArabic ? 'تقييم المخاطرة' : 'Assess Risk'}
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
