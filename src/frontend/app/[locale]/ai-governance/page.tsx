'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'next/navigation';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, BarChart, Bar, Legend } from 'recharts';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// ==================== INTERFACES ====================

interface AIModel {
  model_id: string;
  model_name: string;
  model_version: string;
  model_type: string;
  status: string;
  description_en: string;
  description_ar: string;
  use_case_en: string;
  use_case_ar: string;
  framework?: string;
  algorithm?: string;
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1_score?: number;
  bias_assessment_completed: boolean;
  is_explainable: boolean;
  processes_personal_data: boolean;
  model_owner: string;
  created_by: string;
  created_at: string;
  deployed_at?: string;
}

interface BiasTest {
  test_id: string;
  model_id: string;
  test_name: string;
  test_type: string;
  protected_attribute: string;
  bias_detected: boolean;
  severity?: string;
  bias_score?: number;
  findings_en: string;
  findings_ar: string;
  recommendations_en?: string;
  recommendations_ar?: string;
  test_date: string;
}

interface EthicsReview {
  review_id: string;
  model_id: string;
  review_type: string;
  reviewer_name: string;
  ethical_concerns_en: string;
  ethical_concerns_ar: string;
  recommendations_en: string;
  recommendations_ar: string;
  approval_status: string;
  review_date: string;
}

interface Statistics {
  totalModels: number;
  productionModels: number;
  biasTestsPassed: number;
  ethicsReviews: number;
  avgAccuracy: number;
  avgComplianceScore: number;
}

// ==================== MAIN COMPONENT ====================

export default function AIGovernancePage() {
  const params = useParams();
  const locale = params.locale as string;
  const isArabic = locale === 'ar';

  // State
  const [models, setModels] = useState<AIModel[]>([]);
  const [statistics, setStatistics] = useState<Statistics>({
    totalModels: 0,
    productionModels: 0,
    biasTestsPassed: 0,
    ethicsReviews: 0,
    avgAccuracy: 0,
    avgComplianceScore: 0
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Filter state
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [filterType, setFilterType] = useState<string>('all');

  // Modal states
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [showBiasTestModal, setShowBiasTestModal] = useState(false);
  const [showEthicsReviewModal, setShowEthicsReviewModal] = useState(false);
  const [showRiskAssessmentModal, setShowRiskAssessmentModal] = useState(false);
  const [showModelDetailsModal, setShowModelDetailsModal] = useState(false);
  const [selectedModel, setSelectedModel] = useState<AIModel | null>(null);

  // Form state - Register Model
  const [newModel, setNewModel] = useState({
    model_name: '',
    model_version: '1.0.0',
    model_type: 'CLASSIFICATION',
    description_en: '',
    description_ar: '',
    use_case_en: '',
    use_case_ar: '',
    framework: '',
    algorithm: '',
    processes_personal_data: false,
    model_owner: ''
  });

  // Form state - Bias Test
  const [newBiasTest, setNewBiasTest] = useState({
    model_id: '',
    test_name: '',
    test_type: 'demographic_parity',
    protected_attribute: 'gender',
    attribute_values: ['male', 'female'],
    test_dataset_size: 1000,
    findings_en: '',
    findings_ar: '',
    bias_detected: false,
    severity: 'low',
    bias_score: 0,
    recommendations_en: '',
    recommendations_ar: '',
    requires_action: false
  });

  // Form state - Ethics Review
  const [newEthicsReview, setNewEthicsReview] = useState({
    model_id: '',
    review_type: 'INITIAL',
    reviewer_name: '',
    ethical_concerns_en: '',
    ethical_concerns_ar: '',
    recommendations_en: '',
    recommendations_ar: '',
    approval_status: 'PENDING'
  });

  // Risk Assessment state
  const [riskAssessment, setRiskAssessment] = useState({
    model_id: '',
    data_privacy_risk: 3,
    bias_risk: 3,
    explainability_risk: 3,
    security_risk: 3,
    societal_impact_risk: 3
  });

  // Helper function to get auth headers
  const getAuthHeaders = () => {
    const token = localStorage.getItem('access_token');
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  // ==================== DATA FETCHING ====================

  const fetchAllData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const headers = getAuthHeaders();

      // Fetch models
      const modelsRes = await axios.get(`${API_BASE}/ai-governance/models`, { headers });
      setModels(modelsRes.data);

      // Calculate statistics
      const totalModels = modelsRes.data.length;
      const productionModels = modelsRes.data.filter((m: AIModel) => m.status === 'PRODUCTION').length;
      const biasTestsPassed = modelsRes.data.filter((m: AIModel) => m.bias_assessment_completed).length;
      const avgAccuracy = modelsRes.data.reduce((sum: number, m: AIModel) => sum + (m.accuracy || 0), 0) / (totalModels || 1);
      
      // Mock compliance score calculation
      const avgComplianceScore = calculateComplianceScore(modelsRes.data);

      setStatistics({
        totalModels,
        productionModels,
        biasTestsPassed,
        ethicsReviews: Math.floor(totalModels * 0.8), // Mock
        avgAccuracy: avgAccuracy * 100,
        avgComplianceScore
      });

    } catch (err: any) {
      console.error('Failed to fetch data:', err);
      setError(err.response?.data?.detail || 'Failed to load AI Governance data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // Calculate compliance score based on multiple factors
  const calculateComplianceScore = (models: AIModel[]) => {
    if (models.length === 0) return 0;
    
    let score = 0;
    models.forEach(model => {
      let modelScore = 0;
      if (model.bias_assessment_completed) modelScore += 25;
      if (model.is_explainable) modelScore += 25;
      if (model.accuracy && model.accuracy >= 0.85) modelScore += 25;
      if (model.status === 'PRODUCTION' && model.deployed_at) modelScore += 25;
      score += modelScore;
    });
    
    return Math.round(score / models.length);
  };

  // ==================== HANDLERS ====================

  const handleRegisterModel = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const headers = getAuthHeaders();
      
      // Mock user ID (in production, get from auth context)
      const userId = 'f47ac10b-58cc-4372-a567-0e02b2c3d479';
      
      const modelData = {
        ...newModel,
        model_owner: userId
      };

      await axios.post(`${API_BASE}/ai-governance/models`, modelData, { headers });
      
      setShowRegisterModal(false);
      setNewModel({
        model_name: '',
        model_version: '1.0.0',
        model_type: 'CLASSIFICATION',
        description_en: '',
        description_ar: '',
        use_case_en: '',
        use_case_ar: '',
        framework: '',
        algorithm: '',
        processes_personal_data: false,
        model_owner: ''
      });
      
      await fetchAllData();
      alert(isArabic ? 'تم تسجيل النموذج بنجاح' : 'Model registered successfully');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to register model');
    } finally {
      setLoading(false);
    }
  };

  const handleRunBiasTest = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const headers = getAuthHeaders();
      await axios.post(`${API_BASE}/ai-governance/bias-tests`, newBiasTest, { headers });
      
      setShowBiasTestModal(false);
      setNewBiasTest({
        model_id: '',
        test_name: '',
        test_type: 'demographic_parity',
        protected_attribute: 'gender',
        attribute_values: ['male', 'female'],
        test_dataset_size: 1000,
        findings_en: '',
        findings_ar: '',
        bias_detected: false,
        severity: 'low',
        bias_score: 0,
        recommendations_en: '',
        recommendations_ar: '',
        requires_action: false
      });
      
      await fetchAllData();
      alert(isArabic ? 'تم تشغيل اختبار التحيز بنجاح' : 'Bias test completed successfully');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to run bias test');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateEthicsReview = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const headers = getAuthHeaders();
      await axios.post(`${API_BASE}/ai-governance/ethics-reviews`, newEthicsReview, { headers });
      
      setShowEthicsReviewModal(false);
      setNewEthicsReview({
        model_id: '',
        review_type: 'INITIAL',
        reviewer_name: '',
        ethical_concerns_en: '',
        ethical_concerns_ar: '',
        recommendations_en: '',
        recommendations_ar: '',
        approval_status: 'PENDING'
      });
      
      await fetchAllData();
      alert(isArabic ? 'تمت المراجعة الأخلاقية بنجاح' : 'Ethics review created successfully');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create ethics review');
    } finally {
      setLoading(false);
    }
  };

  const calculateRiskScore = () => {
    const { data_privacy_risk, bias_risk, explainability_risk, security_risk, societal_impact_risk } = riskAssessment;
    const avgRisk = (data_privacy_risk + bias_risk + explainability_risk + security_risk + societal_impact_risk) / 5;
    return Math.round(avgRisk * 20); // Convert to 0-100 scale
  };

  const openBiasTestModal = (model: AIModel) => {
    setSelectedModel(model);
    setNewBiasTest({ ...newBiasTest, model_id: model.model_id });
    setShowBiasTestModal(true);
  };

  const openEthicsReviewModal = (model: AIModel) => {
    setSelectedModel(model);
    setNewEthicsReview({ ...newEthicsReview, model_id: model.model_id });
    setShowEthicsReviewModal(true);
  };

  const openRiskAssessmentModal = (model: AIModel) => {
    setSelectedModel(model);
    setRiskAssessment({ ...riskAssessment, model_id: model.model_id });
    setShowRiskAssessmentModal(true);
  };

  const openModelDetailsModal = (model: AIModel) => {
    setSelectedModel(model);
    setShowModelDetailsModal(true);
  };

  // ==================== HELPER FUNCTIONS ====================

  const getStatusBadgeClass = (status: string) => {
    const statusMap: { [key: string]: string } = {
      'DEVELOPMENT': 'bg-blue-100 text-blue-800',
      'TESTING': 'bg-yellow-100 text-yellow-800',
      'STAGING': 'bg-purple-100 text-purple-800',
      'PRODUCTION': 'bg-green-100 text-green-800',
      'DEPRECATED': 'bg-orange-100 text-orange-800',
      'RETIRED': 'bg-gray-100 text-gray-800'
    };
    return statusMap[status] || 'bg-gray-100 text-gray-800';
  };

  const getStatusLabel = (status: string) => {
    const labels: { [key: string]: { en: string; ar: string } } = {
      'DEVELOPMENT': { en: 'Development', ar: 'تطوير' },
      'TESTING': { en: 'Testing', ar: 'اختبار' },
      'STAGING': { en: 'Staging', ar: 'تجهيز' },
      'PRODUCTION': { en: 'Production', ar: 'إنتاج' },
      'DEPRECATED': { en: 'Deprecated', ar: 'مهمل' },
      'RETIRED': { en: 'Retired', ar: 'متقاعد' }
    };
    return isArabic ? labels[status]?.ar : labels[status]?.en;
  };

  const getModelTypeLabel = (type: string) => {
    const labels: { [key: string]: { en: string; ar: string } } = {
      'CLASSIFICATION': { en: 'Classification', ar: 'تصنيف' },
      'REGRESSION': { en: 'Regression', ar: 'انحدار' },
      'NLP': { en: 'NLP', ar: 'معالجة اللغة' },
      'COMPUTER_VISION': { en: 'Computer Vision', ar: 'رؤية حاسوبية' },
      'GENERATIVE': { en: 'Generative', ar: 'توليد' },
      'RECOMMENDATION': { en: 'Recommendation', ar: 'توصية' },
      'OTHER': { en: 'Other', ar: 'أخرى' }
    };
    return isArabic ? labels[type]?.ar : labels[type]?.en;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return isArabic 
      ? date.toLocaleDateString('ar-SA') 
      : date.toLocaleDateString('en-US');
  };

  // Filter models
  const filteredModels = models.filter(model => {
    if (filterStatus !== 'all' && model.status !== filterStatus) return false;
    if (filterType !== 'all' && model.model_type !== filterType) return false;
    return true;
  });

  // Performance monitoring data (mock)
  const performanceData = [
    { month: 'Jan', accuracy: 88, precision: 85, recall: 82 },
    { month: 'Feb', accuracy: 89, precision: 87, recall: 84 },
    { month: 'Mar', accuracy: 90, precision: 88, recall: 86 },
    { month: 'Apr', accuracy: 91, precision: 90, recall: 87 },
    { month: 'May', accuracy: 92, precision: 91, recall: 89 },
    { month: 'Jun', accuracy: 93, precision: 92, recall: 90 }
  ];

  const radarData = selectedModel ? [
    { metric: isArabic ? 'الدقة' : 'Accuracy', value: (selectedModel.accuracy || 0) * 100 },
    { metric: isArabic ? 'الضبط' : 'Precision', value: (selectedModel.precision || 0) * 100 },
    { metric: isArabic ? 'الاستدعاء' : 'Recall', value: (selectedModel.recall || 0) * 100 },
    { metric: isArabic ? 'F1' : 'F1 Score', value: (selectedModel.f1_score || 0) * 100 },
    { metric: isArabic ? 'القابلية للتفسير' : 'Explainability', value: selectedModel.is_explainable ? 100 : 0 }
  ] : [];

  // ==================== RENDER ====================

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-xl shadow-lg p-8 mb-6">
          <h1 className="text-4xl font-bold text-white mb-2">
            {isArabic ? '🤖 حوكمة الذكاء الاصطناعي' : '🤖 AI Governance'}
          </h1>
          <p className="text-indigo-100 text-lg">
            {isArabic
              ? 'إدارة نماذج الذكاء الاصطناعي والامتثال لمبادئ سدايا'
              : 'AI Model Management & SDAIA Principles Compliance'}
          </p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm mb-1">
              {isArabic ? 'إجمالي النماذج' : 'Total Models'}
            </div>
            <div className="text-3xl font-bold text-gray-900">{statistics.totalModels}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm mb-1">
              {isArabic ? 'في الإنتاج' : 'In Production'}
            </div>
            <div className="text-3xl font-bold text-green-600">{statistics.productionModels}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm mb-1">
              {isArabic ? 'اختبار التحيز' : 'Bias Tested'}
            </div>
            <div className="text-3xl font-bold text-blue-600">{statistics.biasTestsPassed}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm mb-1">
              {isArabic ? 'المراجعات الأخلاقية' : 'Ethics Reviews'}
            </div>
            <div className="text-3xl font-bold text-purple-600">{statistics.ethicsReviews}</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm mb-1">
              {isArabic ? 'متوسط الدقة' : 'Avg Accuracy'}
            </div>
            <div className="text-3xl font-bold text-indigo-600">{statistics.avgAccuracy.toFixed(1)}%</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <div className="text-gray-500 text-sm mb-1">
              {isArabic ? 'درجة الامتثال' : 'Compliance Score'}
            </div>
            <div className="text-3xl font-bold text-purple-600">{statistics.avgComplianceScore}%</div>
          </div>
        </div>

        {/* Performance Monitoring Chart */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            {isArabic ? '📊 مراقبة الأداء' : '📊 Performance Monitoring'}
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={performanceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis domain={[75, 100]} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="accuracy" stroke="#8b5cf6" strokeWidth={2} name={isArabic ? 'الدقة' : 'Accuracy'} />
              <Line type="monotone" dataKey="precision" stroke="#3b82f6" strokeWidth={2} name={isArabic ? 'الضبط' : 'Precision'} />
              <Line type="monotone" dataKey="recall" stroke="#10b981" strokeWidth={2} name={isArabic ? 'الاستدعاء' : 'Recall'} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Filters and Register Button */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex flex-wrap items-center gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {isArabic ? 'الحالة' : 'Status'}
              </label>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="all">{isArabic ? 'الكل' : 'All'}</option>
                <option value="DEVELOPMENT">{isArabic ? 'تطوير' : 'Development'}</option>
                <option value="TESTING">{isArabic ? 'اختبار' : 'Testing'}</option>
                <option value="STAGING">{isArabic ? 'تجهيز' : 'Staging'}</option>
                <option value="PRODUCTION">{isArabic ? 'إنتاج' : 'Production'}</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                {isArabic ? 'النوع' : 'Type'}
              </label>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
              >
                <option value="all">{isArabic ? 'الكل' : 'All'}</option>
                <option value="CLASSIFICATION">{isArabic ? 'تصنيف' : 'Classification'}</option>
                <option value="REGRESSION">{isArabic ? 'انحدار' : 'Regression'}</option>
                <option value="NLP">{isArabic ? 'معالجة اللغة' : 'NLP'}</option>
                <option value="COMPUTER_VISION">{isArabic ? 'رؤية حاسوبية' : 'Computer Vision'}</option>
              </select>
            </div>

            <div className={`${isArabic ? 'mr-auto' : 'ml-auto'}`}>
              <button
                onClick={() => setShowRegisterModal(true)}
                className="px-6 py-2 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition shadow-md"
              >
                {isArabic ? '➕ تسجيل نموذج جديد' : '➕ Register New Model'}
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Models List */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            {isArabic ? '📋 سجل النماذج' : '📋 Model Registry'}
          </h2>

          {loading && filteredModels.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              {isArabic ? 'جاري التحميل...' : 'Loading...'}
            </div>
          ) : filteredModels.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              {isArabic ? 'لا توجد نماذج' : 'No models found'}
            </div>
          ) : (
            <div className="space-y-4">
              {filteredModels.map((model) => (
                <div
                  key={model.model_id}
                  className="border border-gray-200 rounded-lg p-4 hover:shadow-lg transition"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-bold text-gray-900">
                          {model.model_name} v{model.model_version}
                        </h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getStatusBadgeClass(model.status)}`}>
                          {getStatusLabel(model.status)}
                        </span>
                        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-800">
                          {getModelTypeLabel(model.model_type)}
                        </span>
                        {model.bias_assessment_completed && (
                          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-green-100 text-green-800">
                            {isArabic ? '✓ تم اختبار التحيز' : '✓ Bias Tested'}
                          </span>
                        )}
                        {model.is_explainable && (
                          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-purple-100 text-purple-800">
                            {isArabic ? '✓ قابل للتفسير' : '✓ Explainable'}
                          </span>
                        )}
                        {model.processes_personal_data && (
                          <span className="px-3 py-1 rounded-full text-xs font-semibold bg-orange-100 text-orange-800">
                            {isArabic ? '⚠️ بيانات شخصية' : '⚠️ PII'}
                          </span>
                        )}
                      </div>
                      <p className="text-gray-600 text-sm mb-2">
                        {isArabic ? model.description_ar : model.description_en}
                      </p>
                      <div className="flex flex-wrap gap-4 text-sm text-gray-500">
                        <span>
                          {isArabic ? 'الاستخدام:' : 'Use Case:'} {isArabic ? model.use_case_ar : model.use_case_en}
                        </span>
                        {model.framework && (
                          <span>
                            {isArabic ? 'الإطار:' : 'Framework:'} {model.framework}
                          </span>
                        )}
                        {model.accuracy && (
                          <span>
                            {isArabic ? 'الدقة:' : 'Accuracy:'} {(model.accuracy * 100).toFixed(1)}%
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex flex-wrap gap-2 pt-3 border-t border-gray-200">
                    <button
                      onClick={() => openModelDetailsModal(model)}
                      className="px-4 py-2 bg-indigo-600 text-white text-sm font-semibold rounded-lg hover:bg-indigo-700 transition"
                    >
                      {isArabic ? '👁️ عرض التفاصيل' : '👁️ View Details'}
                    </button>
                    <button
                      onClick={() => openBiasTestModal(model)}
                      className="px-4 py-2 bg-blue-600 text-white text-sm font-semibold rounded-lg hover:bg-blue-700 transition"
                    >
                      {isArabic ? '⚖️ اختبار التحيز' : '⚖️ Run Bias Test'}
                    </button>
                    <button
                      onClick={() => openRiskAssessmentModal(model)}
                      className="px-4 py-2 bg-orange-600 text-white text-sm font-semibold rounded-lg hover:bg-orange-700 transition"
                    >
                      {isArabic ? '🎯 تقييم المخاطر' : '🎯 Risk Assessment'}
                    </button>
                    <button
                      onClick={() => openEthicsReviewModal(model)}
                      className="px-4 py-2 bg-purple-600 text-white text-sm font-semibold rounded-lg hover:bg-purple-700 transition"
                    >
                      {isArabic ? '🔍 مراجعة أخلاقية' : '🔍 Ethics Review'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ==================== REGISTER MODEL MODAL ==================== */}
      {showRegisterModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white p-6 border-b z-10">
              <h3 className="text-2xl font-bold text-gray-900">
                {isArabic ? 'تسجيل نموذج ذكاء اصطناعي جديد' : 'Register New AI Model'}
              </h3>
            </div>
            <form onSubmit={handleRegisterModel} className="p-6 space-y-4">
              {/* Model Name & Version */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isArabic ? 'اسم النموذج *' : 'Model Name *'}
                  </label>
                  <input
                    type="text"
                    value={newModel.model_name}
                    onChange={(e) => setNewModel({ ...newModel, model_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    required
                    minLength={2}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isArabic ? 'الإصدار *' : 'Version *'}
                  </label>
                  <input
                    type="text"
                    value={newModel.model_version}
                    onChange={(e) => setNewModel({ ...newModel, model_version: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                </div>
              </div>

              {/* Model Type & Framework */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isArabic ? 'نوع النموذج *' : 'Model Type *'}
                  </label>
                  <select
                    value={newModel.model_type}
                    onChange={(e) => setNewModel({ ...newModel, model_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    required
                  >
                    <option value="CLASSIFICATION">{isArabic ? 'تصنيف' : 'Classification'}</option>
                    <option value="REGRESSION">{isArabic ? 'انحدار' : 'Regression'}</option>
                    <option value="NLP">{isArabic ? 'معالجة اللغة' : 'NLP'}</option>
                    <option value="COMPUTER_VISION">{isArabic ? 'رؤية حاسوبية' : 'Computer Vision'}</option>
                    <option value="GENERATIVE">{isArabic ? 'توليد' : 'Generative'}</option>
                    <option value="RECOMMENDATION">{isArabic ? 'توصية' : 'Recommendation'}</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isArabic ? 'الإطار' : 'Framework'}
                  </label>
                  <input
                    type="text"
                    value={newModel.framework}
                    onChange={(e) => setNewModel({ ...newModel, framework: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    placeholder="TensorFlow, PyTorch, Scikit-learn"
                  />
                </div>
              </div>

              {/* Description EN */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'الوصف (إنجليزي) *' : 'Description (English) *'}
                </label>
                <textarea
                  value={newModel.description_en}
                  onChange={(e) => setNewModel({ ...newModel, description_en: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  rows={3}
                  required
                  minLength={10}
                />
              </div>

              {/* Description AR */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'الوصف (عربي) *' : 'Description (Arabic) *'}
                </label>
                <textarea
                  value={newModel.description_ar}
                  onChange={(e) => setNewModel({ ...newModel, description_ar: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  rows={3}
                  dir="rtl"
                  required
                  minLength={10}
                />
              </div>

              {/* Use Case EN */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'حالة الاستخدام (إنجليزي) *' : 'Use Case (English) *'}
                </label>
                <textarea
                  value={newModel.use_case_en}
                  onChange={(e) => setNewModel({ ...newModel, use_case_en: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  rows={2}
                  required
                  minLength={10}
                />
              </div>

              {/* Use Case AR */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'حالة الاستخدام (عربي) *' : 'Use Case (Arabic) *'}
                </label>
                <textarea
                  value={newModel.use_case_ar}
                  onChange={(e) => setNewModel({ ...newModel, use_case_ar: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  rows={2}
                  dir="rtl"
                  required
                  minLength={10}
                />
              </div>

              {/* Algorithm */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'الخوارزمية' : 'Algorithm'}
                </label>
                <input
                  type="text"
                  value={newModel.algorithm}
                  onChange={(e) => setNewModel({ ...newModel, algorithm: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  placeholder="Random Forest, Neural Network, etc."
                />
              </div>

              {/* Processes Personal Data */}
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="processes_personal_data"
                  checked={newModel.processes_personal_data}
                  onChange={(e) => setNewModel({ ...newModel, processes_personal_data: e.target.checked })}
                  className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                />
                <label htmlFor="processes_personal_data" className="text-sm font-medium text-gray-700">
                  {isArabic ? 'يعالج بيانات شخصية (PDPL)' : 'Processes Personal Data (PDPL)'}
                </label>
              </div>

              {/* Buttons */}
              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-6 py-3 bg-indigo-600 text-white font-semibold rounded-lg hover:bg-indigo-700 transition disabled:bg-gray-400"
                >
                  {loading ? (isArabic ? 'جاري التسجيل...' : 'Registering...') : (isArabic ? 'تسجيل' : 'Register')}
                </button>
                <button
                  type="button"
                  onClick={() => setShowRegisterModal(false)}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-800 font-semibold rounded-lg hover:bg-gray-300 transition"
                >
                  {isArabic ? 'إلغاء' : 'Cancel'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ==================== BIAS TEST MODAL ==================== */}
      {showBiasTestModal && selectedModel && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white p-6 border-b z-10">
              <h3 className="text-2xl font-bold text-gray-900">
                {isArabic ? `اختبار التحيز: ${selectedModel.model_name}` : `Bias Test: ${selectedModel.model_name}`}
              </h3>
            </div>
            <form onSubmit={handleRunBiasTest} className="p-6 space-y-4">
              {/* Test Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'اسم الاختبار *' : 'Test Name *'}
                </label>
                <input
                  type="text"
                  value={newBiasTest.test_name}
                  onChange={(e) => setNewBiasTest({ ...newBiasTest, test_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                  minLength={5}
                />
              </div>

              {/* Test Type & Protected Attribute */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isArabic ? 'نوع الاختبار *' : 'Test Type *'}
                  </label>
                  <select
                    value={newBiasTest.test_type}
                    onChange={(e) => setNewBiasTest({ ...newBiasTest, test_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="demographic_parity">{isArabic ? 'التكافؤ الديموغرافي' : 'Demographic Parity'}</option>
                    <option value="equal_opportunity">{isArabic ? 'تكافؤ الفرص' : 'Equal Opportunity'}</option>
                    <option value="calibration">{isArabic ? 'المعايرة' : 'Calibration'}</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isArabic ? 'السمة المحمية *' : 'Protected Attribute *'}
                  </label>
                  <select
                    value={newBiasTest.protected_attribute}
                    onChange={(e) => setNewBiasTest({ ...newBiasTest, protected_attribute: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                  >
                    <option value="gender">{isArabic ? 'الجنس' : 'Gender'}</option>
                    <option value="age">{isArabic ? 'العمر' : 'Age'}</option>
                    <option value="nationality">{isArabic ? 'الجنسية' : 'Nationality'}</option>
                    <option value="race">{isArabic ? 'العرق' : 'Race'}</option>
                  </select>
                </div>
              </div>

              {/* Dataset Size & Bias Detected */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isArabic ? 'حجم مجموعة البيانات *' : 'Dataset Size *'}
                  </label>
                  <input
                    type="number"
                    value={newBiasTest.test_dataset_size}
                    onChange={(e) => setNewBiasTest({ ...newBiasTest, test_dataset_size: parseInt(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    required
                    min={1}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isArabic ? 'الخطورة' : 'Severity'}
                  </label>
                  <select
                    value={newBiasTest.severity}
                    onChange={(e) => setNewBiasTest({ ...newBiasTest, severity: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="low">{isArabic ? 'منخفض' : 'Low'}</option>
                    <option value="medium">{isArabic ? 'متوسط' : 'Medium'}</option>
                    <option value="high">{isArabic ? 'عالي' : 'High'}</option>
                  </select>
                </div>
              </div>

              {/* Bias Score */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'درجة التحيز (0-1)' : 'Bias Score (0-1)'}
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={newBiasTest.bias_score}
                  onChange={(e) => setNewBiasTest({ ...newBiasTest, bias_score: parseFloat(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  min={0}
                  max={1}
                />
              </div>

              {/* Findings EN */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'النتائج (إنجليزي) *' : 'Findings (English) *'}
                </label>
                <textarea
                  value={newBiasTest.findings_en}
                  onChange={(e) => setNewBiasTest({ ...newBiasTest, findings_en: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  required
                  minLength={10}
                />
              </div>

              {/* Findings AR */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'النتائج (عربي) *' : 'Findings (Arabic) *'}
                </label>
                <textarea
                  value={newBiasTest.findings_ar}
                  onChange={(e) => setNewBiasTest({ ...newBiasTest, findings_ar: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  rows={3}
                  dir="rtl"
                  required
                  minLength={10}
                />
              </div>

              {/* Bias Detected & Requires Action */}
              <div className="flex items-center gap-6">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="bias_detected"
                    checked={newBiasTest.bias_detected}
                    onChange={(e) => setNewBiasTest({ ...newBiasTest, bias_detected: e.target.checked })}
                    className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="bias_detected" className="text-sm font-medium text-gray-700">
                    {isArabic ? 'تم اكتشاف تحيز' : 'Bias Detected'}
                  </label>
                </div>
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="requires_action"
                    checked={newBiasTest.requires_action}
                    onChange={(e) => setNewBiasTest({ ...newBiasTest, requires_action: e.target.checked })}
                    className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="requires_action" className="text-sm font-medium text-gray-700">
                    {isArabic ? 'يتطلب إجراء' : 'Requires Action'}
                  </label>
                </div>
              </div>

              {/* Buttons */}
              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition disabled:bg-gray-400"
                >
                  {loading ? (isArabic ? 'جاري التنفيذ...' : 'Running...') : (isArabic ? 'تشغيل الاختبار' : 'Run Test')}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowBiasTestModal(false);
                    setSelectedModel(null);
                  }}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-800 font-semibold rounded-lg hover:bg-gray-300 transition"
                >
                  {isArabic ? 'إلغاء' : 'Cancel'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ==================== ETHICS REVIEW MODAL ==================== */}
      {showEthicsReviewModal && selectedModel && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white p-6 border-b z-10">
              <h3 className="text-2xl font-bold text-gray-900">
                {isArabic ? `مراجعة أخلاقية: ${selectedModel.model_name}` : `Ethics Review: ${selectedModel.model_name}`}
              </h3>
            </div>
            <form onSubmit={handleCreateEthicsReview} className="p-6 space-y-4">
              {/* Review Type & Reviewer Name */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isArabic ? 'نوع المراجعة *' : 'Review Type *'}
                  </label>
                  <select
                    value={newEthicsReview.review_type}
                    onChange={(e) => setNewEthicsReview({ ...newEthicsReview, review_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    required
                  >
                    <option value="INITIAL">{isArabic ? 'أولي' : 'Initial'}</option>
                    <option value="PERIODIC">{isArabic ? 'دوري' : 'Periodic'}</option>
                    <option value="INCIDENT_DRIVEN">{isArabic ? 'حادثة' : 'Incident Driven'}</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    {isArabic ? 'اسم المراجع *' : 'Reviewer Name *'}
                  </label>
                  <input
                    type="text"
                    value={newEthicsReview.reviewer_name}
                    onChange={(e) => setNewEthicsReview({ ...newEthicsReview, reviewer_name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                    required
                  />
                </div>
              </div>

              {/* Ethical Concerns EN */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'المخاوف الأخلاقية (إنجليزي) *' : 'Ethical Concerns (English) *'}
                </label>
                <textarea
                  value={newEthicsReview.ethical_concerns_en}
                  onChange={(e) => setNewEthicsReview({ ...newEthicsReview, ethical_concerns_en: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  rows={3}
                  required
                  minLength={10}
                />
              </div>

              {/* Ethical Concerns AR */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'المخاوف الأخلاقية (عربي) *' : 'Ethical Concerns (Arabic) *'}
                </label>
                <textarea
                  value={newEthicsReview.ethical_concerns_ar}
                  onChange={(e) => setNewEthicsReview({ ...newEthicsReview, ethical_concerns_ar: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  rows={3}
                  dir="rtl"
                  required
                  minLength={10}
                />
              </div>

              {/* Recommendations EN */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'التوصيات (إنجليزي) *' : 'Recommendations (English) *'}
                </label>
                <textarea
                  value={newEthicsReview.recommendations_en}
                  onChange={(e) => setNewEthicsReview({ ...newEthicsReview, recommendations_en: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  rows={3}
                  required
                  minLength={10}
                />
              </div>

              {/* Recommendations AR */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'التوصيات (عربي) *' : 'Recommendations (Arabic) *'}
                </label>
                <textarea
                  value={newEthicsReview.recommendations_ar}
                  onChange={(e) => setNewEthicsReview({ ...newEthicsReview, recommendations_ar: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  rows={3}
                  dir="rtl"
                  required
                  minLength={10}
                />
              </div>

              {/* Approval Status */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  {isArabic ? 'حالة الموافقة' : 'Approval Status'}
                </label>
                <select
                  value={newEthicsReview.approval_status}
                  onChange={(e) => setNewEthicsReview({ ...newEthicsReview, approval_status: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                >
                  <option value="PENDING">{isArabic ? 'معلق' : 'Pending'}</option>
                  <option value="APPROVED">{isArabic ? 'موافق' : 'Approved'}</option>
                  <option value="REJECTED">{isArabic ? 'مرفوض' : 'Rejected'}</option>
                  <option value="REQUIRES_CHANGES">{isArabic ? 'يتطلب تعديلات' : 'Requires Changes'}</option>
                </select>
              </div>

              {/* Buttons */}
              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition disabled:bg-gray-400"
                >
                  {loading ? (isArabic ? 'جاري الحفظ...' : 'Saving...') : (isArabic ? 'حفظ المراجعة' : 'Save Review')}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowEthicsReviewModal(false);
                    setSelectedModel(null);
                  }}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-800 font-semibold rounded-lg hover:bg-gray-300 transition"
                >
                  {isArabic ? 'إلغاء' : 'Cancel'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ==================== RISK ASSESSMENT MODAL ==================== */}
      {showRiskAssessmentModal && selectedModel && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white p-6 border-b z-10">
              <h3 className="text-2xl font-bold text-gray-900">
                {isArabic ? `تقييم المخاطر: ${selectedModel.model_name}` : `Risk Assessment: ${selectedModel.model_name}`}
              </h3>
            </div>
            <div className="p-6 space-y-6">
              {/* Risk Sliders */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {isArabic ? 'مخاطر خصوصية البيانات' : 'Data Privacy Risk'}: {riskAssessment.data_privacy_risk}/5
                </label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={riskAssessment.data_privacy_risk}
                  onChange={(e) => setRiskAssessment({ ...riskAssessment, data_privacy_risk: parseInt(e.target.value) })}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {isArabic ? 'مخاطر التحيز' : 'Bias Risk'}: {riskAssessment.bias_risk}/5
                </label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={riskAssessment.bias_risk}
                  onChange={(e) => setRiskAssessment({ ...riskAssessment, bias_risk: parseInt(e.target.value) })}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {isArabic ? 'مخاطر القابلية للتفسير' : 'Explainability Risk'}: {riskAssessment.explainability_risk}/5
                </label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={riskAssessment.explainability_risk}
                  onChange={(e) => setRiskAssessment({ ...riskAssessment, explainability_risk: parseInt(e.target.value) })}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {isArabic ? 'المخاطر الأمنية' : 'Security Risk'}: {riskAssessment.security_risk}/5
                </label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={riskAssessment.security_risk}
                  onChange={(e) => setRiskAssessment({ ...riskAssessment, security_risk: parseInt(e.target.value) })}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {isArabic ? 'مخاطر التأثير المجتمعي' : 'Societal Impact Risk'}: {riskAssessment.societal_impact_risk}/5
                </label>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={riskAssessment.societal_impact_risk}
                  onChange={(e) => setRiskAssessment({ ...riskAssessment, societal_impact_risk: parseInt(e.target.value) })}
                  className="w-full"
                />
              </div>

              {/* Overall Risk Score */}
              <div className="bg-orange-50 border-2 border-orange-200 rounded-lg p-6 text-center">
                <div className="text-sm font-medium text-gray-700 mb-2">
                  {isArabic ? 'إجمالي درجة المخاطر' : 'Overall Risk Score'}
                </div>
                <div className="text-5xl font-bold text-orange-600">
                  {calculateRiskScore()}%
                </div>
              </div>

              {/* Buttons */}
              <div className="flex gap-3 pt-4">
                <button
                  onClick={() => {
                    alert(isArabic ? `تم حفظ تقييم المخاطر: ${calculateRiskScore()}%` : `Risk assessment saved: ${calculateRiskScore()}%`);
                    setShowRiskAssessmentModal(false);
                    setSelectedModel(null);
                  }}
                  className="flex-1 px-6 py-3 bg-orange-600 text-white font-semibold rounded-lg hover:bg-orange-700 transition"
                >
                  {isArabic ? 'حفظ التقييم' : 'Save Assessment'}
                </button>
                <button
                  onClick={() => {
                    setShowRiskAssessmentModal(false);
                    setSelectedModel(null);
                  }}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-800 font-semibold rounded-lg hover:bg-gray-300 transition"
                >
                  {isArabic ? 'إلغاء' : 'Cancel'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ==================== MODEL DETAILS MODAL ==================== */}
      {showModelDetailsModal && selectedModel && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white p-6 border-b z-10">
              <h3 className="text-2xl font-bold text-gray-900">
                {isArabic ? 'تفاصيل النموذج' : 'Model Details'}
              </h3>
            </div>
            <div className="p-6 space-y-6">
              {/* Performance Radar Chart */}
              <div className="bg-gray-50 rounded-lg p-6">
                <h4 className="text-lg font-bold text-gray-900 mb-4 text-center">
                  {isArabic ? 'مقاييس الأداء' : 'Performance Metrics'}
                </h4>
                {radarData.length > 0 && (
                  <ResponsiveContainer width="100%" height={300}>
                    <RadarChart data={radarData}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="metric" />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} />
                      <Radar name="Performance" dataKey="value" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.6} />
                      <Tooltip />
                    </RadarChart>
                  </ResponsiveContainer>
                )}
              </div>

              {/* Model Information */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-gray-500">{isArabic ? 'اسم النموذج' : 'Model Name'}</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedModel.model_name}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">{isArabic ? 'الإصدار' : 'Version'}</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedModel.model_version}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">{isArabic ? 'النوع' : 'Type'}</div>
                  <div className="text-lg font-semibold text-gray-900">{getModelTypeLabel(selectedModel.model_type)}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">{isArabic ? 'الحالة' : 'Status'}</div>
                  <div className="text-lg font-semibold text-gray-900">{getStatusLabel(selectedModel.status)}</div>
                </div>
                {selectedModel.framework && (
                  <div>
                    <div className="text-sm font-medium text-gray-500">{isArabic ? 'الإطار' : 'Framework'}</div>
                    <div className="text-lg font-semibold text-gray-900">{selectedModel.framework}</div>
                  </div>
                )}
                {selectedModel.algorithm && (
                  <div>
                    <div className="text-sm font-medium text-gray-500">{isArabic ? 'الخوارزمية' : 'Algorithm'}</div>
                    <div className="text-lg font-semibold text-gray-900">{selectedModel.algorithm}</div>
                  </div>
                )}
              </div>

              {/* Description */}
              <div>
                <div className="text-sm font-medium text-gray-500 mb-1">{isArabic ? 'الوصف' : 'Description'}</div>
                <div className="text-gray-900">{isArabic ? selectedModel.description_ar : selectedModel.description_en}</div>
              </div>

              {/* Use Case */}
              <div>
                <div className="text-sm font-medium text-gray-500 mb-1">{isArabic ? 'حالة الاستخدام' : 'Use Case'}</div>
                <div className="text-gray-900">{isArabic ? selectedModel.use_case_ar : selectedModel.use_case_en}</div>
              </div>

              {/* Compliance Score */}
              <div className="bg-purple-50 border-2 border-purple-200 rounded-lg p-6 text-center">
                <div className="text-sm font-medium text-gray-700 mb-2">
                  {isArabic ? 'درجة الامتثال' : 'Compliance Score'}
                </div>
                <div className="text-5xl font-bold text-purple-600">
                  {calculateComplianceScore([selectedModel])}%
                </div>
                <div className="mt-4 text-sm text-gray-600">
                  {isArabic ? 'بناءً على التحيز، القابلية للتفسير، الدقة، والنشر' : 'Based on bias testing, explainability, accuracy, and deployment'}
                </div>
              </div>

              {/* Close Button */}
              <div className="pt-4">
                <button
                  onClick={() => {
                    setShowModelDetailsModal(false);
                    setSelectedModel(null);
                  }}
                  className="w-full px-6 py-3 bg-gray-200 text-gray-800 font-semibold rounded-lg hover:bg-gray-300 transition"
                >
                  {isArabic ? 'إغلاق' : 'Close'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
