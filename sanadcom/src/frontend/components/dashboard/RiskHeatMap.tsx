'use client';

import React from 'react';

interface Risk {
  id: string;
  title: string;
  likelihood: number; // 1-5
  impact: number; // 1-5
  status: 'open' | 'mitigated' | 'accepted' | 'transferred';
}

interface RiskHeatMapProps {
  risks: Risk[];
  locale?: 'ar' | 'en';
}

export const RiskHeatMap: React.FC<RiskHeatMapProps> = ({ risks, locale = 'en' }) => {
  const labels = locale === 'ar' 
    ? { impact: 'التأثير', likelihood: 'الاحتمالية', critical: 'حرج', high: 'عالي', medium: 'متوسط', low: 'منخفض' }
    : { impact: 'Impact', likelihood: 'Likelihood', critical: 'Critical', high: 'High', medium: 'Medium', low: 'Low' };

  // Calculate risk distribution in 5x5 matrix
  const matrix = Array(5).fill(null).map(() => Array(5).fill(0));
  const riskDetails: Record<string, Risk[]> = {};

  risks.forEach(risk => {
    const i = 5 - risk.impact; // Invert for visual (high impact at top)
    const j = risk.likelihood - 1;
    matrix[i][j]++;
    const key = `${i}-${j}`;
    if (!riskDetails[key]) riskDetails[key] = [];
    riskDetails[key].push(risk);
  });

  // Risk level calculation (Impact * Likelihood)
  const getRiskLevel = (impact: number, likelihood: number): string => {
    const score = (6 - impact) * likelihood;
    if (score >= 20) return 'critical';
    if (score >= 12) return 'high';
    if (score >= 6) return 'medium';
    return 'low';
  };

  const getColorClass = (level: string): string => {
    const colors = {
      critical: 'bg-red-600 hover:bg-red-700',
      high: 'bg-orange-500 hover:bg-orange-600',
      medium: 'bg-yellow-400 hover:bg-yellow-500',
      low: 'bg-green-500 hover:bg-green-600'
    };
    return colors[level as keyof typeof colors] || 'bg-gray-300';
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 text-gray-900">
        {locale === 'ar' ? 'خريطة المخاطر الحرارية' : 'Risk Heat Map'}
      </h2>
      
      <div className="flex gap-4 mb-4">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-red-600 rounded"></div>
          <span className="text-sm">{labels.critical}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-orange-500 rounded"></div>
          <span className="text-sm">{labels.high}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-yellow-400 rounded"></div>
          <span className="text-sm">{labels.medium}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-green-500 rounded"></div>
          <span className="text-sm">{labels.low}</span>
        </div>
      </div>

      <div className="relative">
        {/* Y-axis label (Impact) */}
        <div className="absolute -left-16 top-1/2 -translate-y-1/2 -rotate-90">
          <span className="text-sm font-semibold text-gray-700">{labels.impact}</span>
        </div>

        {/* Heat map grid */}
        <div className="ml-4">
          <div className="grid grid-cols-5 gap-2">
            {matrix.map((row, i) => 
              row.map((count, j) => {
                const impact = 5 - i;
                const likelihood = j + 1;
                const level = getRiskLevel(impact, likelihood);
                const key = `${i}-${j}`;
                const cellRisks = riskDetails[key] || [];
                
                return (
                  <div
                    key={`${i}-${j}`}
                    className={`relative aspect-square rounded-lg ${getColorClass(level)} 
                      flex items-center justify-center cursor-pointer transition-all
                      border-2 border-transparent hover:border-gray-900 group`}
                    title={cellRisks.map(r => r.title).join(', ')}
                  >
                    <span className="text-white font-bold text-xl">{count}</span>
                    {count > 0 && (
                      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 
                        hidden group-hover:block bg-gray-900 text-white text-xs rounded py-2 px-3 
                        w-64 z-10 shadow-xl">
                        <div className="font-bold mb-1">
                          {locale === 'ar' ? `${count} مخاطر` : `${count} Risk${count > 1 ? 's' : ''}`}
                        </div>
                        {cellRisks.slice(0, 3).map((risk, idx) => (
                          <div key={idx} className="text-xs mb-1">• {risk.title}</div>
                        ))}
                        {cellRisks.length > 3 && (
                          <div className="text-xs opacity-75">
                            +{cellRisks.length - 3} {locale === 'ar' ? 'المزيد' : 'more'}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
          
          {/* X-axis label (Likelihood) */}
          <div className="text-center mt-2">
            <span className="text-sm font-semibold text-gray-700">{labels.likelihood}</span>
          </div>
          
          {/* Axis values */}
          <div className="grid grid-cols-5 gap-2 mt-1">
            {[1, 2, 3, 4, 5].map(n => (
              <div key={n} className="text-center text-xs text-gray-600">{n}</div>
            ))}
          </div>
        </div>

        {/* Y-axis values */}
        <div className="absolute -left-8 top-0 h-full flex flex-col justify-around">
          {[5, 4, 3, 2, 1].map(n => (
            <div key={n} className="text-xs text-gray-600">{n}</div>
          ))}
        </div>
      </div>

      {/* Summary statistics */}
      <div className="mt-6 grid grid-cols-4 gap-4 pt-4 border-t">
        <div className="text-center">
          <div className="text-2xl font-bold text-red-600">
            {risks.filter(r => getRiskLevel(r.impact, r.likelihood) === 'critical').length}
          </div>
          <div className="text-xs text-gray-600">{labels.critical}</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-orange-600">
            {risks.filter(r => getRiskLevel(r.impact, r.likelihood) === 'high').length}
          </div>
          <div className="text-xs text-gray-600">{labels.high}</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-yellow-600">
            {risks.filter(r => getRiskLevel(r.impact, r.likelihood) === 'medium').length}
          </div>
          <div className="text-xs text-gray-600">{labels.medium}</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">
            {risks.filter(r => getRiskLevel(r.impact, r.likelihood) === 'low').length}
          </div>
          <div className="text-xs text-gray-600">{labels.low}</div>
        </div>
      </div>
    </div>
  );
};
