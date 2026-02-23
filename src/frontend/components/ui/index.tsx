/**
 * Professional Arabic UI Component Library for SICO GRC Platform
 * Built with TypeScript, React, and Tailwind CSS
 * RTL (Right-to-Left) support for Arabic language
 */

import React from 'react';

// ============================================================================
// Type Definitions
// ============================================================================

export interface Control {
  control_id: string;
  framework: 'ECC' | 'CCC' | 'PDPL';
  domain: string;
  title_ar: string;
  title_en: string;
  description_ar: string;
  description_en: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'compliant' | 'in_progress' | 'not_started' | 'non_compliant';
  maturity_level?: number;
}

export interface ComplianceStats {
  total_controls: number;
  compliant: number;
  in_progress: number;
  not_started: number;
  non_compliant: number;
  compliance_score: number;
}

export interface Framework {
  id: 'ECC' | 'CCC' | 'PDPL';
  name_ar: string;
  name_en: string;
  authority_ar: string;
  authority_en: string;
  icon: string;
  color: string;
  controls_count: number;
  compliance_score: number;
}

// ============================================================================
// Status Badge Component
// ============================================================================

export const StatusBadge = React.memo<{ status: Control['status']; locale?: string }>(({ 
  status, 
  locale = 'ar' 
}) => {
  const statusConfig = {
    compliant: {
      ar: 'متوافق',
      en: 'Compliant',
      color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
    },
    in_progress: {
      ar: 'قيد التنفيذ',
      en: 'In Progress',
      color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
    },
    not_started: {
      ar: 'لم يبدأ',
      en: 'Not Started',
      color: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
    },
    non_compliant: {
      ar: 'غير متوافق',
      en: 'Non-Compliant',
      color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
    }
  };

  const config = statusConfig[status];
  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
      {locale === 'ar' ? config.ar : config.en}
    </span>
  );
});

StatusBadge.displayName = 'StatusBadge';

// ============================================================================
// Priority Badge Component
// ============================================================================

export const PriorityBadge = React.memo<{ priority: Control['priority']; locale?: string }>(({
  priority,
  locale = 'ar'
}) => {
  const priorityConfig = {
    critical: {
      ar: 'حرج',
      en: 'Critical',
      color: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
    },
    high: {
      ar: 'عالي',
      en: 'High',
      color: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300'
    },
    medium: {
      ar: 'متوسط',
      en: 'Medium',
      color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
    },
    low: {
      ar: 'منخفض',
      en: 'Low',
      color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
    }
  };

  const config = priorityConfig[priority];
  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.color}`}>
      <span>{locale === 'ar' ? config.ar : config.en}</span>
    </span>
  );
});

PriorityBadge.displayName = 'PriorityBadge';

// ============================================================================
// Framework Badge Component
// ============================================================================

export const FrameworkBadge = React.memo<{ framework: Framework['id']; locale?: string }>(({
  framework,
  locale = 'ar'
}) => {
  const frameworkConfig = {
    ECC: {
      ar: 'الضوابط الأساسية للأمن السيبراني',
      en: 'Essential Cybersecurity Controls',
      color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300'
    },
    CCC: {
      ar: 'ضوابط الأمن السيبراني السحابي',
      en: 'Cloud Cybersecurity Controls',
      color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300'
    },
    PDPL: {
      ar: 'نظام حماية البيانات الشخصية',
      en: 'Personal Data Protection Law',
      color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
    }
  };

  const config = frameworkConfig[framework];
  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-lg text-xs font-semibold ${config.color}`}>
      {framework}
    </span>
  );
});

FrameworkBadge.displayName = 'FrameworkBadge';

// ============================================================================
// Stats Card Component
// ============================================================================

export const StatsCard = React.memo<{
  title: string;
  value: string | number;
  icon: string;
  color: string;
  trend?: { value: number; isPositive: boolean };
  locale?: string;
}>(({ title, value, icon, color, trend, locale = 'ar' }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className={`w-12 h-12 rounded-lg ${color} flex items-center justify-center text-2xl`}>
          {icon}
        </div>
        {trend && (
          <div className={`flex items-center gap-1 text-sm font-medium ${
            trend.isPositive ? 'text-green-600' : 'text-red-600'
          }`}>
            <span>{trend.isPositive ? '↑' : '↓'}</span>
            <span>{Math.abs(trend.value)}%</span>
          </div>
        )}
      </div>
      <h3 className="text-gray-600 dark:text-gray-400 text-sm font-medium mb-2">{title}</h3>
      <p className="text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
    </div>
  );
});

StatsCard.displayName = 'StatsCard';

// ============================================================================
// Compliance Progress Bar
// ============================================================================

export const ComplianceProgress = React.memo<{
  percentage: number;
  label: string;
  color?: string;
  showLabel?: boolean;
}>(({ percentage, label, color = 'bg-blue-600', showLabel = true }) => {
  return (
    <div className="w-full">
      {showLabel && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</span>
          <span className="text-sm font-bold text-gray-900 dark:text-white">{percentage}%</span>
        </div>
      )}
      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
        <div
          className={`${color} h-3 rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${Math.min(percentage, 100)}%` }}
        />
      </div>
    </div>
  );
});

ComplianceProgress.displayName = 'ComplianceProgress';

// ============================================================================
// Control Card Component
// ============================================================================

export const ControlCard = React.memo<{
  control: Control;
  locale?: string;
  onClick?: () => void;
}>(({ control, locale = 'ar', onClick }) => {
  const title = locale === 'ar' ? control.title_ar : control.title_en;
  const description = locale === 'ar' ? control.description_ar : control.description_en;

  return (
    <div
      onClick={onClick}
      className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 hover:shadow-xl transition-all cursor-pointer border border-gray-200 dark:border-gray-700 hover:border-blue-500"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <FrameworkBadge framework={control.framework} locale={locale} />
          <span className="text-sm font-mono text-gray-600 dark:text-gray-400">
            {control.control_id}
          </span>
        </div>
        <StatusBadge status={control.status} locale={locale} />
      </div>

      <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2 line-clamp-2">
        {title}
      </h3>

      <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-3">
        {description}
      </p>

      <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
        <PriorityBadge priority={control.priority} locale={locale} />
        {control.maturity_level !== undefined && (
          <div className="flex items-center gap-2">
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {locale === 'ar' ? 'مستوى النضج' : 'Maturity'}
            </span>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((level) => (
                <div
                  key={level}
                  className={`w-2 h-6 rounded ${
                    level <= (control.maturity_level || 0)
                      ? 'bg-blue-500'
                      : 'bg-gray-300 dark:bg-gray-600'
                  }`}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

ControlCard.displayName = 'ControlCard';

// ============================================================================
// Framework Card Component
// ============================================================================

export const FrameworkCard: React.FC<{
  framework: Framework;
  locale?: string;
  onClick?: () => void;
}> = ({ framework, locale = 'ar', onClick }) => {
  const name = locale === 'ar' ? framework.name_ar : framework.name_en;
  const authority = locale === 'ar' ? framework.authority_ar : framework.authority_en;

  return (
    <div
      onClick={onClick}
      className={`bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-2xl transition-all cursor-pointer border-2 hover:scale-105 ${framework.color}`}
    >
      <div className="flex items-center justify-between mb-4">
        <div className="text-4xl">{framework.icon}</div>
        <span className="text-3xl font-bold text-gray-900 dark:text-white">
          {framework.compliance_score}%
        </span>
      </div>

      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
        {framework.id}
      </h3>

      <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
        {name}
      </p>

      <p className="text-xs text-gray-600 dark:text-gray-400 mb-4">
        {authority}
      </p>

      <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
        <span className="text-sm text-gray-600 dark:text-gray-400">
          {locale === 'ar' ? 'الضوابط' : 'Controls'}
        </span>
        <span className="text-lg font-bold text-gray-900 dark:text-white">
          {framework.controls_count}
        </span>
      </div>

      <ComplianceProgress
        percentage={framework.compliance_score}
        label={locale === 'ar' ? 'نسبة الامتثال' : 'Compliance Score'}
        color={framework.color.replace('border-', 'bg-')}
        showLabel={false}
      />
    </div>
  );
};

// ============================================================================
// Search and Filter Bar
// ============================================================================

export const SearchFilterBar: React.FC<{
  searchTerm: string;
  onSearchChange: (term: string) => void;
  filters: {
    framework?: Framework['id'][];
    status?: Control['status'][];
    priority?: Control['priority'][];
  };
  onFilterChange: (filters: any) => void;
  locale?: string;
}> = ({ searchTerm, onSearchChange, filters, onFilterChange, locale = 'ar' }) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
      <div className="flex flex-col md:flex-row gap-4">
        {/* Search Input */}
        <div className="flex-1">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder={locale === 'ar' ? 'البحث في الضوابط...' : 'Search controls...'}
            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Framework Filter */}
        <select
          value={filters.framework?.[0] || ''}
          onChange={(e) => onFilterChange({ ...filters, framework: e.target.value ? [e.target.value as Framework['id']] : undefined })}
          className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="">{locale === 'ar' ? 'جميع الأطر' : 'All Frameworks'}</option>
          <option value="ECC">ECC</option>
          <option value="CCC">CCC</option>
          <option value="PDPL">PDPL</option>
        </select>

        {/* Status Filter */}
        <select
          value={filters.status?.[0] || ''}
          onChange={(e) => onFilterChange({ ...filters, status: e.target.value ? [e.target.value as Control['status']] : undefined })}
          className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="">{locale === 'ar' ? 'جميع الحالات' : 'All Status'}</option>
          <option value="compliant">{locale === 'ar' ? 'متوافق' : 'Compliant'}</option>
          <option value="in_progress">{locale === 'ar' ? 'قيد التنفيذ' : 'In Progress'}</option>
          <option value="not_started">{locale === 'ar' ? 'لم يبدأ' : 'Not Started'}</option>
          <option value="non_compliant">{locale === 'ar' ? 'غير متوافق' : 'Non-Compliant'}</option>
        </select>

        {/* Priority Filter */}
        <select
          value={filters.priority?.[0] || ''}
          onChange={(e) => onFilterChange({ ...filters, priority: e.target.value ? [e.target.value as Control['priority']] : undefined })}
          className="px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
        >
          <option value="">{locale === 'ar' ? 'جميع الأولويات' : 'All Priorities'}</option>
          <option value="critical">{locale === 'ar' ? 'حرج' : 'Critical'}</option>
          <option value="high">{locale === 'ar' ? 'عالي' : 'High'}</option>
          <option value="medium">{locale === 'ar' ? 'متوسط' : 'Medium'}</option>
          <option value="low">{locale === 'ar' ? 'منخفض' : 'Low'}</option>
        </select>
      </div>
    </div>
  );
};

// ============================================================================
// Loading Spinner
// ============================================================================

export const LoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg' }> = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-12 h-12',
    lg: 'w-16 h-16'
  };

  return (
    <div className="flex items-center justify-center p-8">
      <div className={`${sizeClasses[size]} border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin`} />
    </div>
  );
};

// ============================================================================
// Empty State Component
// ============================================================================

export const EmptyState: React.FC<{
  title: string;
  description: string;
  icon: string;
  action?: { label: string; onClick: () => void };
}> = ({ title, description, icon, action }) => {
  return (
    <div className="flex flex-col items-center justify-center p-12 text-center">
      <div className="text-6xl mb-4">{icon}</div>
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">{title}</h3>
      <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md">{description}</p>
      {action && (
        <button
          onClick={action.onClick}
          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          {action.label}
        </button>
      )}
    </div>
  );
};
