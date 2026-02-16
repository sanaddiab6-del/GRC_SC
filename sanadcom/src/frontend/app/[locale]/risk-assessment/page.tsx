'use client';

/**
 * Risk Assessment Page
 * Full-page risk assessment workflow module
 */

import React from 'react';
import { RiskAssessment } from '@/components/dashboard/RiskAssessment';
import { useParams } from 'next/navigation';

export default function RiskAssessmentPage() {
  const params = useParams();
  const locale = (params?.locale as 'ar' | 'en') || 'en';

  const handleSaveRisk = (risk: any) => {
    console.log('Saving risk:', risk);
    // In production: API call to save risk
    alert(locale === 'ar' ? 'تم حفظ المخاطرة بنجاح!' : 'Risk saved successfully!');
  };

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          {locale === 'ar' ? 'تقييم المخاطر' : 'Risk Assessment'}
        </h1>
        <p className="text-gray-600">
          {locale === 'ar' 
            ? 'أداة شاملة لتحديد وتقييم ومعالجة المخاطر' 
            : 'Comprehensive tool to identify, assess, and mitigate risks'
          }
        </p>
      </div>

      <RiskAssessment locale={locale} onSaveRisk={handleSaveRisk} />
    </div>
  );
}
