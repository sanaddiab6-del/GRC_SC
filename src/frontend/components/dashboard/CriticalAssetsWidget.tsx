'use client';

import React from 'react';

interface Asset {
  id: string;
  name: string;
  type: 'Server' | 'Database' | 'Application' | 'Network' | 'Endpoint';
  criticality: 'Critical' | 'High' | 'Medium' | 'Low';
  compliance_status: 'compliant' | 'non_compliant' | 'partial';
  last_assessed: string;
  risk_score: number; // 0-100
}

interface CriticalAssetsProps {
  assets: Asset[];
  locale?: 'ar' | 'en';
}

export const CriticalAssetsWidget: React.FC<CriticalAssetsProps> = ({ assets, locale = 'en' }) => {
  const labels = locale === 'ar'
    ? {
        title: 'الأصول الحرجة',
        name: 'الاسم',
        type: 'النوع',
        criticality: 'الأهمية',
        status: 'حالة التوافق',
        riskScore: 'درجة المخاطر',
        viewAll: 'عرض جميع الأصول',
        compliant: 'متوافق',
        partial: 'جزئياً',
        nonCompliant: 'غير متوافق'
      }
    : {
        title: 'Critical Assets',
        name: 'Name',
        type: 'Type',
        criticality: 'Criticality',
        status: 'Compliance Status',
        riskScore: 'Risk Score',
        viewAll: 'View All Assets',
        compliant: 'Compliant',
        partial: 'Partial',
        nonCompliant: 'Non-Compliant'
      };

  const statusConfig = {
    compliant: { color: 'bg-green-100 text-green-800', label: labels.compliant },
    partial: { color: 'bg-yellow-100 text-yellow-800', label: labels.partial },
    non_compliant: { color: 'bg-red-100 text-red-800', label: labels.nonCompliant }
  };

  const getRiskColor = (score: number): string => {
    if (score >= 75) return 'text-red-600';
    if (score >= 50) return 'text-orange-600';
    if (score >= 25) return 'text-yellow-600';
    return 'text-green-600';
  };

  const criticalAssets = assets
    .filter(a => a.criticality === 'Critical' || a.criticality === 'High')
    .sort((a, b) => b.risk_score - a.risk_score)
    .slice(0, 5);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-900">{labels.title}</h2>
        <button className="text-sm text-blue-600 hover:text-blue-800 font-semibold">
          {labels.viewAll} →
        </button>
      </div>

      <div className="space-y-3">
        {criticalAssets.map((asset) => {
          const statusStyle = statusConfig[asset.compliance_status];
          
          return (
            <div 
              key={asset.id}
              className="border border-gray-200 hover:border-blue-400 rounded-lg p-4 
                transition-all cursor-pointer hover:shadow-md"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-1">{asset.name}</h3>
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <span className="font-medium">{asset.type}</span>
                    <span className="text-gray-400">•</span>
                    <span className={`font-bold ${
                      asset.criticality === 'Critical' ? 'text-red-600' : 'text-orange-600'
                    }`}>
                      {asset.criticality}
                    </span>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded text-xs font-semibold ${statusStyle.color}`}>
                  {statusStyle.label}
                </span>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex justify-between text-xs text-gray-600 mb-1">
                    <span>{labels.riskScore}</span>
                    <span className={`font-bold ${getRiskColor(asset.risk_score)}`}>
                      {asset.risk_score}/100
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all ${
                        asset.risk_score >= 75 ? 'bg-red-600' :
                        asset.risk_score >= 50 ? 'bg-orange-500' :
                        asset.risk_score >= 25 ? 'bg-yellow-400' : 'bg-green-500'
                      }`}
                      style={{ width: `${asset.risk_score}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary */}
      <div className="mt-6 pt-6 border-t grid grid-cols-3 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">
            {assets.filter(a => a.criticality === 'Critical').length}
          </div>
          <div className="text-xs text-gray-600">
            {locale === 'ar' ? 'حرج' : 'Critical'}
          </div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">
            {assets.filter(a => a.compliance_status === 'compliant').length}
          </div>
          <div className="text-xs text-gray-600">
            {locale === 'ar' ? 'متوافق' : 'Compliant'}
          </div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600">
            {assets.filter(a => a.compliance_status === 'non_compliant').length}
          </div>
          <div className="text-xs text-gray-600">
            {locale === 'ar' ? 'غير متوافق' : 'Non-Compliant'}
          </div>
        </div>
      </div>
    </div>
  );
};
