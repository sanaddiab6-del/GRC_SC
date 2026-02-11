/**
 * Risk Assessment Workflow Module
 * Interactive risk assessment with likelihood/impact matrix and mitigation planning
 */

'use client';

import React, { useState } from 'react';
import { Card, Badge } from '../ui/Cards';

interface Risk {
  id: string;
  title: string;
  description: string;
  category: string;
  likelihood: number;
  impact: number;
  inherentRisk: number;
  residualRisk: number;
  mitigations: string[];
  controls: string[];
  owner?: string;
  status: 'identified' | 'assessed' | 'mitigated' | 'accepted' | 'transferred';
  reviewDate: Date;
}

interface RiskAssessmentProps {
  locale: 'ar' | 'en';
  onSaveRisk?: (risk:Partial<Risk>) => void;
}

export function RiskAssessment({ locale, onSaveRisk }: RiskAssessmentProps) {
  const [step, setStep] = useState<'identify' | 'assess' | 'mitigate' | 'review'>('identify');
  const [formData, setFormData] = useState<Partial<Risk>>({
    title: '',
    description: '',
    category: '',
    likelihood: 3,
    impact: 3,
    status: 'identified',
  });

  const categories = [
    { value: 'operational', label: locale === 'ar' ? 'تشغيلية' : 'Operational' },
    { value: 'strategic', label: locale === 'ar' ? 'استراتيجية' : 'Strategic' },
    { value: 'financial', label: locale === 'ar' ? 'مالية' : 'Financial' },
    { value: 'compliance', label: locale === 'ar' ? 'امتثال' : 'Compliance' },
    { value: 'reputational', label: locale === 'ar' ? 'سمعة' : 'Reputational' },
    { value: 'technology', label: locale === 'ar' ? 'تقنية' : 'Technology' },
  ];

  const getRiskScore = (likelihood: number, impact: number) => likelihood * impact;
  const getRiskLevel = (score: number) => {
    if (score >= 20) return { level: 'Critical', color: 'bg-red-600', text: locale === 'ar' ? 'حرج' : 'Critical' };
    if (score >= 15) return { level: 'High', color: 'bg-orange-500', text: locale === 'ar' ? 'عالي' : 'High' };
    if (score >= 8) return { level: 'Medium', color: 'bg-yellow-500', text: locale === 'ar' ? 'متوسط' : 'Medium' };
    return { level: 'Low', color: 'bg-green-500', text: locale === 'ar' ? 'منخفض' : 'Low' };
  };

  const currentScore = getRiskScore(formData.likelihood || 1, formData.impact || 1);
  const riskLevel = getRiskLevel(currentScore);

  const steps = [
    { id: 'identify', label: locale === 'ar' ? 'التعريف' : 'Identify', icon: '1' },
    { id: 'assess', label: locale === 'ar' ? 'التقييم' : 'Assess', icon: '2' },
    { id: 'mitigate', label: locale === 'ar' ? 'المعالجة' : 'Mitigate', icon: '3' },
    { id: 'review', label: locale === 'ar' ? 'المراجعة' : 'Review', icon: '4' },
  ];

  const handleSubmit = () => {
    onSaveRisk?.(formData);
    // Reset form
    setFormData({
      title: '',
      description: '',
      category: '',
      likelihood: 3,
      impact: 3,
      status: 'identified',
    });
    setStep('identify');
  };

  return (
    <Card className="max-w-5xl mx-auto">
      {/* Progress Steps */}
      <div className="flex items-center justify-between mb-8">
        {steps.map((s, index) => (
          <React.Fragment key={s.id}>
            <div 
              className={`flex items-center gap-3 cursor-pointer transition-all ${
                step === s.id ? 'scale-110' : 'opacity-60'
              }`}
              onClick={() => setStep(s.id as any)}
            >
              <div className={`
                w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold
                ${step === s.id ? 'bg-gray-900 text-white' : 'bg-gray-200 text-gray-600'}
              `}>
                {s.icon}
              </div>
              <div className="hidden md:block">
                <p className={`text-sm font-semibold ${step === s.id ? 'text-gray-900' : 'text-gray-500'}`}>
                  {s.label}
                </p>
              </div>
            </div>
            {index < steps.length - 1 && (
              <div className="flex-1 h-1 bg-gray-200 mx-4">
                <div 
                  className="h-full bg-gray-900 transition-all duration-500"
                  style={{ width: steps.findIndex(st => st.id === step) > index ? '100%' : '0%' }}
                ></div>
              </div>
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Step Content */}
      <div className="space-y-6">
        {/* Step 1: Identify */}
        {step === 'identify' && (
          <div className="space-y-4">
            <h3 className="text-2xl font-bold text-gray-900">
              {locale === 'ar' ? 'تحديد المخاطرة' : 'Identify the Risk'}
            </h3>
            
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {locale === 'ar' ? 'عنوان المخاطرة' : 'Risk Title'}
              </label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-gray-900/10 focus:border-transparent"
                placeholder={locale === 'ar' ? 'مثال: ثغرات أمنية غير معالجة' : 'e.g., Unpatched security vulnerabilities'}
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {locale === 'ar' ? 'الوصف' : 'Description'}
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-gray-900/10 focus:border-transparent"
                placeholder={locale === 'ar' ? 'وصف تفصيلي للمخاطرة...' : 'Detailed description of the risk...'}
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {locale === 'ar' ? 'التصنيف' : 'Category'}
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-gray-900/10 focus:border-transparent"
              >
                <option value="">{locale === 'ar' ? 'اختر التصنيف' : 'Select category'}</option>
                {categories.map(cat => (
                  <option key={cat.value} value={cat.value}>{cat.label}</option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* Step 2: Assess */}
        {step === 'assess' && (
          <div className="space-y-6">
            <h3 className="text-2xl font-bold text-gray-900">
              {locale === 'ar' ? 'تقييم المخاطرة' : 'Assess the Risk'}
            </h3>

            {/* Likelihood */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                {locale === 'ar' ? 'الاحتمالية' : 'Likelihood'} - {formData.likelihood}/5
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={formData.likelihood}
                onChange={(e) => setFormData({ ...formData, likelihood: parseInt(e.target.value) })}
                className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-600 mt-2">
                <span>{locale === 'ar' ? 'نادر' : 'Rare'}</span>
                <span>{locale === 'ar' ? 'محتمل جداً' : 'Very Likely'}</span>
              </div>
            </div>

            {/* Impact */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                {locale === 'ar' ? 'التأثير' : 'Impact'} - {formData.impact}/5
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={formData.impact}
                onChange={(e) => setFormData({ ...formData, impact: parseInt(e.target.value) })}
                className="w-full h-3 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-600 mt-2">
                <span>{locale === 'ar' ? 'ضئيل' : 'Negligible'}</span>
                <span>{locale === 'ar' ? 'كارثي' : 'Catastrophic'}</span>
              </div>
            </div>

            {/* Risk Score Display */}
            <div className="p-6 bg-gray-50 rounded-md border border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">
                    {locale === 'ar' ? 'درجة المخاطرة الأولية' : 'Inherent Risk Score'}
                  </p>
                  <p className="text-5xl font-bold text-gray-900">{currentScore}</p>
                  <p className="text-sm text-gray-600 mt-1">
                    {formData.likelihood} × {formData.impact}
                  </p>
                </div>
                <div className={`px-4 py-2 ${riskLevel.color} text-white rounded-md`}> 
                  <p className="text-lg font-semibold">{riskLevel.text}</p>
                </div>
              </div>
            </div>

            {/* Risk Matrix Visualization */}
            <div className="grid grid-cols-5 gap-1 p-4 bg-white border border-gray-200 rounded-md">
              {[5, 4, 3, 2, 1].map(impact => (
                [1, 2, 3, 4, 5].map(likelihood => {
                  const score = likelihood * impact;
                  const cell = getRiskLevel(score);
                  const isSelected = formData.likelihood === likelihood && formData.impact === impact;
                  
                  return (
                    <div
                      key={`${impact}-${likelihood}`}
                      className={`
                        h-14 ${cell.color} rounded-md flex items-center justify-center
                        font-semibold text-white cursor-pointer transition-all text-sm
                        ${isSelected ? 'ring-2 ring-gray-900 ring-offset-2' : 'opacity-80 hover:opacity-100'}
                      `}
                      onClick={() => setFormData({ ...formData, likelihood, impact })}
                    >
                      {score}
                    </div>
                  );
                })
              ))}
            </div>
          </div>
        )}

        {/* Step 3: Mitigate */}
        {step === 'mitigate' && (
          <div className="space-y-4">
            <h3 className="text-2xl font-bold text-gray-900">
              {locale === 'ar' ? 'خطة المعالجة' : 'Mitigation Plan'}
            </h3>
            
            <div className="grid md:grid-cols-2 gap-4">
              <Card className="p-4 bg-blue-50 border-blue-200">
                <h4 className="font-semibold text-blue-900 mb-2">
                  {locale === 'ar' ? 'استراتيجية المعالجة' : 'Treatment Strategy'}
                </h4>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md bg-white">
                  <option>{locale === 'ar' ? 'تخفيف' : 'Mitigate'}</option>
                  <option>{locale === 'ar' ? 'قبول' : 'Accept'}</option>
                  <option>{locale === 'ar' ? 'نقل' : 'Transfer'}</option>
                  <option>{locale === 'ar' ? 'تجنب' : 'Avoid'}</option>
                </select>
              </Card>

              <Card className="p-4 bg-green-50 border-green-200">
                <h4 className="font-semibold text-green-900 mb-2">
                  {locale === 'ar' ? 'المسؤول' : 'Risk Owner'}
                </h4>
                <input
                  type="text"
                  placeholder={locale === 'ar' ? 'اسم المسؤول' : 'Assign owner'}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </Card>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {locale === 'ar' ? 'الضوابط المطبقة' : 'Applied Controls'}
              </label>
              <textarea
                rows={3}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-gray-900/10"
                placeholder={locale === 'ar' ? 'قائمة بالضوابط المطبقة...' : 'List of controls applied...'}
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {locale === 'ar' ? 'خطوات المعالجة' : 'Mitigation Actions'}
              </label>
              <textarea
                rows={4}
                className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:ring-2 focus:ring-gray-900/10"
                placeholder={locale === 'ar' ? 'وصف خطة المعالجة التفصيلية...' : 'Describe mitigation plan...'}
              />
            </div>
          </div>
        )}

        {/* Step 4: Review */}
        {step === 'review' && (
          <div className="space-y-6">
            <h3 className="text-2xl font-bold text-gray-900">
              {locale === 'ar' ? 'مراجعة وحفظ' : 'Review & Save'}
            </h3>

            <Card className="p-6 bg-gray-50">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h4 className="text-xl font-bold text-gray-900">{formData.title}</h4>
                  <div className="mt-2">
                    <Badge variant="info" size="sm">
                      {categories.find(c => c.value === formData.category)?.label}
                    </Badge>
                  </div>
                </div>
                <div className={`px-4 py-2 ${riskLevel.color} text-white rounded-md font-semibold`}>
                  {riskLevel.text}
                </div>
              </div>

              <p className="text-gray-700 mb-4">{formData.description}</p>

              <div className="grid md:grid-cols-3 gap-4">
                <div className="text-center p-4 bg-white rounded-md">
                  <p className="text-sm text-gray-600">{locale === 'ar' ? 'الاحتمالية' : 'Likelihood'}</p>
                  <p className="text-3xl font-bold text-blue-600">{formData.likelihood}/5</p>
                </div>
                <div className="text-center p-4 bg-white rounded-md">
                  <p className="text-sm text-gray-600">{locale === 'ar' ? 'التأثير' : 'Impact'}</p>
                  <p className="text-3xl font-bold text-orange-600">{formData.impact}/5</p>
                </div>
                <div className="text-center p-4 bg-white rounded-md">
                  <p className="text-sm text-gray-600">{locale === 'ar' ? 'النتيجة' : 'Score'}</p>
                  <p className="text-3xl font-bold text-red-600">{currentScore}</p>
                </div>
              </div>
            </Card>

            <div className="flex gap-3">
              <button
                onClick={handleSubmit}
                className="flex-1 py-2.5 bg-gray-900 text-white rounded-md font-medium hover:bg-gray-800 transition-all"
              >
                {locale === 'ar' ? 'حفظ المخاطرة' : 'Save Risk'}
              </button>
              <button
                onClick={() => setStep('identify')}
                className="px-4 py-2.5 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
              >
                {locale === 'ar' ? 'إعادة' : 'Reset'}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
        <button
          onClick={() => {
            const currentIndex = steps.findIndex(s => s.id === step);
            if (currentIndex > 0) setStep(steps[currentIndex - 1].id as any);
          }}
          disabled={step === 'identify'}
          className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {locale === 'ar' ? 'السابق' : 'Previous'}
        </button>

        <button
          onClick={() => {
            const currentIndex = steps.findIndex(s => s.id === step);
            if (currentIndex < steps.length - 1) setStep(steps[currentIndex + 1].id as any);
          }}
          disabled={step === 'review'}
          className="px-4 py-2 bg-gray-900 text-white rounded-md hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {locale === 'ar' ? 'التالي' : 'Next'}
        </button>
      </div>
    </Card>
  );
}
