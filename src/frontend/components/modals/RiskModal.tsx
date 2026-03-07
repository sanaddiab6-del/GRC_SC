"use client";

import React, { useCallback, useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import DynamicFieldRenderer from "@/components/dynamic/DynamicFieldRenderer";
import { saveCustomFieldValues, useCustomFields } from "@/lib/dynamic-config";

interface Control {
  control_id: string;
  control_number: string;
  title_en: string;
  title_ar: string;
}

interface User {
  id: string;
  user_id?: string;
  name: string;
  email: string;
  role?: string;
}

interface RiskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  locale: "en" | "ar";
  mode: "create" | "edit";
  riskData?: {
    risk_id: string;
    category: string;
    title_en: string;
    title_ar: string;
    description_en: string;
    description_ar: string;
    likelihood: number;
    impact: number;
    risk_owner: string;
    control_id?: string;
    existing_controls_en?: string;
    existing_controls_ar?: string;
    control_effectiveness?: number;
  };
}

const RISK_CATEGORIES = [
  { value: "strategic", label_en: "Strategic", label_ar: "استراتيجي" },
  { value: "operational", label_en: "Operational", label_ar: "تشغيلي" },
  { value: "financial", label_en: "Financial", label_ar: "مالي" },
  { value: "compliance", label_en: "Compliance", label_ar: "امتثال" },
  { value: "reputational", label_en: "Reputational", label_ar: "سمعة" },
  { value: "technology", label_en: "Technology", label_ar: "تقنية" },
  { value: "security", label_en: "Security", label_ar: "أمن" },
  { value: "legal", label_en: "Legal", label_ar: "قانوني" },
];

export default function RiskModal({
  isOpen,
  onClose,
  onSuccess,
  locale,
  mode,
  riskData,
}: RiskModalProps) {
  const isArabic = locale === "ar";
  const isEdit = mode === "edit";

  const [formData, setFormData] = useState({
    category: "",
    title: "",
    description: "",
    likelihood: 3,
    impact: 3,
    owner_id: "",
    control_id: "",
    control_effectiveness: 3,
  });

  const [controls, setControls] = useState<Control[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(false);
  const [error, setError] = useState("");
  const { fields: customFields } = useCustomFields(
    "risk",
    isEdit ? riskData?.risk_id : undefined,
  );
  const [customValues, setCustomValues] = useState<Record<string, any>>({});

  // Load form data if editing
  useEffect(() => {
    if (isOpen && isEdit && riskData) {
      setFormData({
        category: riskData.category || "",
        title: isArabic ? riskData.title_ar : riskData.title_en,
        description: isArabic
          ? riskData.description_ar
          : riskData.description_en,
        likelihood: riskData.likelihood || 3,
        impact: riskData.impact || 3,
        owner_id: riskData.risk_owner || "",
        control_id: riskData.control_id || "",
        control_effectiveness: riskData.control_effectiveness || 3,
      });
    } else if (isOpen && !isEdit) {
      // Reset for create mode
      setFormData({
        category: "",
        title: "",
        description: "",
        likelihood: 3,
        impact: 3,
        owner_id: "",
        control_id: "",
        control_effectiveness: 3,
      });
    }
  }, [isOpen, isEdit, riskData, isArabic]);

  useEffect(() => {
    if (customFields?.length) {
      const nextValues: Record<string, any> = {};
      customFields.forEach((field) => {
        if (field.value !== undefined) {
          nextValues[field.id] = field.value;
        }
      });
      setCustomValues(nextValues);
    }
  }, [customFields]);

  const fetchDropdownData = useCallback(async () => {
    setLoadingData(true);
    console.log("🔵 fetchDropdownData called");
    try {
      // Fetch controls
      console.log("📡 Fetching controls...");
      const controlsResponse = await apiClient.get("/api/v1/controls", {
        params: { limit: 1000 },
      });
      setControls(controlsResponse.data.items || []);
      console.log("✅ Controls loaded:", controlsResponse.data.items?.length);

      // Fetch real users from the API
      try {
        console.log("📡 Fetching users...");
        const usersResponse = await apiClient.get("/api/v1/users", {
          params: { limit: 100 },
        });
        
        console.log("📦 Users response:", usersResponse.data);
        
        if (usersResponse.data && Array.isArray(usersResponse.data)) {
          // Map users to have consistent id field (use user_id)
          const mappedUsers = usersResponse.data.map((user: any) => ({
            id: user.user_id || user.id,
            user_id: user.user_id || user.id,
            name: user.name || user.email,
            email: user.email,
            role: user.role,
          }));
          setUsers(mappedUsers);
          console.log("✅ Fetched users:", mappedUsers.length, mappedUsers);
        } else {
          console.error("❌ Invalid users response format:", usersResponse.data);
          throw new Error("Invalid users response");
        }
      } catch (userErr) {
        console.error("❌ Failed to fetch users from API:", userErr);
        // Fallback: try localStorage
        const storedUsers = localStorage.getItem("users");
        if (storedUsers) {
          try {
            const parsedUsers = JSON.parse(storedUsers);
            setUsers(Array.isArray(parsedUsers) ? parsedUsers : [parsedUsers]);
            console.log("⚠️ Using localStorage users:", parsedUsers);
          } catch {
            setError(isArabic ? "فشل تحميل قائمة المستخدمين" : "Failed to load users. Please ensure you are logged in.");
          }
        } else {
          setError(isArabic ? "فشل تحميل قائمة المستخدمين" : "Failed to load users. Please ensure you are logged in.");
        }
      }
    } catch (err) {
      console.error("Failed to fetch dropdown data:", err);
      setError(isArabic ? "فشل تحميل البيانات" : "Failed to load data");
    } finally {
      setLoadingData(false);
    }
  }, [isArabic]);

  // Fetch controls and users when modal opens
  useEffect(() => {
    if (isOpen) {
      fetchDropdownData();
    }
  }, [isOpen, fetchDropdownData]);

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        name === "likelihood" ||
        name === "impact" ||
        name === "control_effectiveness"
          ? parseInt(value) || 1
          : value,
    }));
    if (error) setError("");
  };

  const handleCustomValueChange = (fieldId: string, value: any) => {
    setCustomValues((prev) => ({ ...prev, [fieldId]: value }));
  };

  const calculateRiskScore = () => {
    return formData.likelihood * formData.impact;
  };

  const getRiskLevel = (score: number) => {
    if (score >= 20)
      return { label: isArabic ? "حرج" : "Critical", color: "text-red-600" };
    if (score >= 12)
      return { label: isArabic ? "عالي" : "High", color: "text-orange-600" };
    if (score >= 6)
      return { label: isArabic ? "متوسط" : "Medium", color: "text-yellow-600" };
    return { label: isArabic ? "منخفض" : "Low", color: "text-green-600" };
  };

  const validateForm = (): boolean => {
    if (!formData.category) {
      setError(isArabic ? "الفئة مطلوبة" : "Category is required");
      return false;
    }
    if (!formData.title.trim() || formData.title.length < 5) {
      setError(
        isArabic
          ? "العنوان مطلوب (5 أحرف على الأقل)"
          : "Title is required (min 5 characters)",
      );
      return false;
    }
    if (!formData.description.trim() || formData.description.length < 10) {
      setError(
        isArabic
          ? "الوصف مطلوب (10 أحرف على الأقل)"
          : "Description is required (min 10 characters)",
      );
      return false;
    }
    if (!formData.owner_id) {
      setError(isArabic ? "يجب اختيار المسؤول" : "Owner is required");
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
    setError("");

    try {
      // Prepare request body
      const requestBody = isEdit
        ? {
            // For edit, only send fields that can be updated
            likelihood: formData.likelihood,
            impact: formData.impact,
            control_effectiveness: formData.control_id
              ? formData.control_effectiveness
              : undefined,
          }
        : {
            // For create, send all required fields
            category: formData.category,
            title_en: formData.title,
            title_ar: formData.title, // Using same text for both languages
            description_en: formData.description,
            description_ar: formData.description,
            likelihood: formData.likelihood,
            impact: formData.impact,
            risk_owner: formData.owner_id,
            existing_controls_en: formData.control_id
              ? `Linked to control ${formData.control_id}`
              : null,
            existing_controls_ar: formData.control_id
              ? `مرتبط بالضابط ${formData.control_id}`
              : null,
            control_effectiveness: formData.control_id
              ? formData.control_effectiveness
              : null,
          };

      const url = isEdit
        ? `/api/v1/risks/${riskData?.risk_id}`
        : "/api/v1/risks";

      console.log("Submitting risk:", {
        method: isEdit ? 'PATCH' : 'POST',
        url,
        body: requestBody,
      });

      const response = isEdit 
        ? await apiClient.patch(url, requestBody)
        : await apiClient.post(url, requestBody);

      if (response.status === 200 || response.status === 201) {
        const entityId = response.data?.risk_id || riskData?.risk_id;
        const valueEntries = Object.entries(customValues).map(([fieldId, value]) => ({
          field_id: fieldId,
          value,
        }));

        if (entityId && valueEntries.length) {
          await saveCustomFieldValues("risk", String(entityId), valueEntries);
        }
        showSuccessToast(
          isEdit
            ? isArabic
              ? "تم تحديث المخاطرة بنجاح"
              : "Risk updated successfully"
            : isArabic
              ? "تم إنشاء المخاطرة بنجاح"
              : "Risk created successfully",
        );

        // Reset form for create mode
        if (!isEdit) {
          setFormData({
            category: "",
            title: "",
            description: "",
            likelihood: 3,
            impact: 3,
            owner_id: "",
            control_id: "",
            control_effectiveness: 3,
          });
        }

        onSuccess();
        onClose();
      }
    } catch (err: any) {
      console.error("Operation failed:", err);
      console.error("Error details:", {
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data,
        message: err.message
      });
      
      let errorMessage = "";
      
      // Handle validation errors from backend
      if (err.response?.status === 422) {
        const validationErrors = err.response?.data?.detail;
        if (Array.isArray(validationErrors)) {
          errorMessage = validationErrors.map((e: any) => 
            `${e.loc?.join('.') || 'Field'}: ${e.msg}`
          ).join(', ');
        } else {
          errorMessage = validationErrors || "Validation error";
        }
      } else if (err.response?.status === 401 || err.response?.status === 403) {
        errorMessage = isArabic 
          ? "غير مصرح. الرجاء تسجيل الدخول أولاً."
          : "Unauthorized. Please log in first.";
      } else {
        errorMessage = err.response?.data?.detail ||
          (isArabic
            ? isEdit
              ? "فشل تحديث المخاطرة. يرجى المحاولة مرة أخرى."
              : "فشل إنشاء المخاطرة. يرجى المحاولة مرة أخرى."
            : isEdit
              ? "Failed to update risk. Please try again."
              : "Failed to create risk. Please try again.");
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const showSuccessToast = (message: string) => {
    const toast = document.createElement("div");
    toast.className =
      "fixed top-4 right-4 bg-green-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-fade-in";
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.remove();
    }, 3000);
  };

  const handleClose = () => {
    if (!loading) {
      setFormData({
        category: "",
        title: "",
        description: "",
        likelihood: 3,
        impact: 3,
        owner_id: "",
        control_id: "",
        control_effectiveness: 3,
      });
      setError("");
      onClose();
    }
  };

  if (!isOpen) return null;

  const riskScore = calculateRiskScore();
  const riskLevel = getRiskLevel(riskScore);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-orange-600 to-red-600 text-white p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">
                {isEdit
                  ? isArabic
                    ? "تعديل المخاطرة"
                    : "Edit Risk"
                  : isArabic
                    ? "إنشاء مخاطرة جديدة"
                    : "Create New Risk"}
              </h2>
              <p className="text-white/90 mt-1">
                {isArabic
                  ? "قم بتحديد وتقييم المخاطرة"
                  : "Identify and assess the risk"}
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

          {/* Loading State */}
          {loadingData && (
            <div className="text-center py-4 text-gray-500">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600 mx-auto mb-2"></div>
              {isArabic ? "جاري التحميل..." : "Loading..."}
            </div>
          )}

          {!loadingData && (
            <>
              {/* Category - Only in create mode */}
              {!isEdit && (
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? "الفئة *" : "Category *"}
                  </label>
                  <select
                    name="category"
                    value={formData.category}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    required
                  >
                    <option value="">
                      {isArabic ? "اختر الفئة" : "Select category"}
                    </option>
                    {RISK_CATEGORIES.map((cat) => (
                      <option key={cat.value} value={cat.value}>
                        {isArabic ? cat.label_ar : cat.label_en}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Title - Only in create mode */}
              {!isEdit && (
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? "العنوان *" : "Title *"}
                  </label>
                  <input
                    type="text"
                    name="title"
                    value={formData.title}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    placeholder={isArabic ? "عنوان المخاطرة" : "Risk title"}
                    required
                    minLength={5}
                  />
                </div>
              )}

              {/* Description - Only in create mode */}
              {!isEdit && (
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? "الوصف *" : "Description *"}
                  </label>
                  <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    rows={3}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    placeholder={
                      isArabic
                        ? "وصف تفصيلي للمخاطرة..."
                        : "Detailed description of the risk..."
                    }
                    required
                    minLength={10}
                  />
                </div>
              )}

              {/* Risk Assessment Grid */}
              <div className="grid grid-cols-2 gap-4">
                {/* Likelihood */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? "الاحتمالية (1-5) *" : "Likelihood (1-5) *"}
                  </label>
                  <select
                    name="likelihood"
                    value={formData.likelihood}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    required
                  >
                    <option value={1}>
                      {isArabic ? "1 - نادر جداً" : "1 - Very Rare"}
                    </option>
                    <option value={2}>
                      {isArabic ? "2 - نادر" : "2 - Rare"}
                    </option>
                    <option value={3}>
                      {isArabic ? "3 - محتمل" : "3 - Possible"}
                    </option>
                    <option value={4}>
                      {isArabic ? "4 - مرجح" : "4 - Likely"}
                    </option>
                    <option value={5}>
                      {isArabic ? "5 - شبه مؤكد" : "5 - Almost Certain"}
                    </option>
                  </select>
                </div>

                {/* Impact */}
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? "التأثير (1-5) *" : "Impact (1-5) *"}
                  </label>
                  <select
                    name="impact"
                    value={formData.impact}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    required
                  >
                    <option value={1}>
                      {isArabic ? "1 - ضئيل" : "1 - Insignificant"}
                    </option>
                    <option value={2}>
                      {isArabic ? "2 - بسيط" : "2 - Minor"}
                    </option>
                    <option value={3}>
                      {isArabic ? "3 - متوسط" : "3 - Moderate"}
                    </option>
                    <option value={4}>
                      {isArabic ? "4 - كبير" : "4 - Major"}
                    </option>
                    <option value={5}>
                      {isArabic ? "5 - كارثي" : "5 - Catastrophic"}
                    </option>
                  </select>
                </div>
              </div>

              {/* Risk Score Display */}
              <div className="bg-gray-50 rounded-lg p-4 border-2 border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600 font-semibold">
                      {isArabic ? "النتيجة الإجمالية للمخاطرة:" : "Risk Score:"}
                    </p>
                    <p className="text-3xl font-bold text-gray-900">
                      {riskScore}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600 font-semibold">
                      {isArabic ? "مستوى المخاطرة:" : "Risk Level:"}
                    </p>
                    <p className={`text-2xl font-bold ${riskLevel.color}`}>
                      {riskLevel.label}
                    </p>
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {isArabic
                    ? "النتيجة = الاحتمالية × التأثير"
                    : "Score = Likelihood × Impact"}
                </p>
              </div>

              {/* Owner - Only in create mode */}
              {!isEdit && (
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic ? "المسؤول *" : "Risk Owner *"}
                  </label>
                  <select
                    name="owner_id"
                    value={formData.owner_id}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                    required
                  >
                    <option value="">
                      {isArabic ? "اختر المسؤول" : "Select owner"}
                    </option>
                    {users.map((user) => (
                      <option
                        key={user.id || user.user_id}
                        value={user.id || user.user_id}
                      >
                        {user.name} ({user.email})
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Optional: Linked Control */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  {isArabic
                    ? "الضابط المرتبط (اختياري)"
                    : "Linked Control (Optional)"}
                </label>
                <select
                  name="control_id"
                  value={formData.control_id}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                >
                  <option value="">{isArabic ? "لا يوجد" : "None"}</option>
                  {controls.map((control) => (
                    <option key={control.control_id} value={control.control_id}>
                      {control.control_number} -{" "}
                      {isArabic ? control.title_ar : control.title_en}
                    </option>
                  ))}
                </select>
              </div>

              {/* Control Effectiveness - Only if control is selected */}
              {formData.control_id && (
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    {isArabic
                      ? "فعالية الضابط (1-5)"
                      : "Control Effectiveness (1-5)"}
                  </label>
                  <select
                    name="control_effectiveness"
                    value={formData.control_effectiveness}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                  >
                    <option value={1}>
                      {isArabic ? "1 - ضعيف" : "1 - Weak"}
                    </option>
                    <option value={2}>
                      {isArabic ? "2 - محدود" : "2 - Limited"}
                    </option>
                    <option value={3}>
                      {isArabic ? "3 - متوسط" : "3 - Moderate"}
                    </option>
                    <option value={4}>
                      {isArabic ? "4 - فعال" : "4 - Effective"}
                    </option>
                    <option value={5}>
                      {isArabic ? "5 - فعال جداً" : "5 - Highly Effective"}
                    </option>
                  </select>
                </div>
              )}

              {customFields.length > 0 && (
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="text-sm font-semibold text-gray-700 mb-3">
                    {isArabic ? "حقول إضافية" : "Additional Fields"}
                  </h3>
                  <DynamicFieldRenderer
                    fields={customFields}
                    values={customValues}
                    onChange={handleCustomValueChange}
                    locale={isArabic ? "ar" : "en"}
                  />
                </div>
              )}

              {/* Info Box */}
              <div className="bg-blue-50 rounded-lg p-4 text-sm text-gray-700">
                <p className="font-semibold mb-2">
                  {isArabic ? "📋 ملاحظة:" : "📋 Note:"}
                </p>
                <ul className="list-disc list-inside space-y-1 text-xs">
                  <li>
                    {isArabic
                      ? "سيتم حساب النتيجة الأولية والمتبقية للمخاطرة تلقائياً"
                      : "Inherent and residual risk scores will be calculated automatically"}
                  </li>
                  <li>
                    {isArabic
                      ? "سيتم جدولة المراجعة التالية خلال 90 يوماً"
                      : "Next review will be scheduled in 90 days"}
                  </li>
                  {!isEdit && (
                    <li>
                      {isArabic
                        ? "سيتم إنشاء رقم فريد للمخاطرة تلقائياً"
                        : "A unique risk number will be generated automatically"}
                    </li>
                  )}
                </ul>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4">
                <button
                  type="submit"
                  disabled={loading || loadingData}
                  className="flex-1 bg-gradient-to-r from-orange-600 to-red-600 hover:from-orange-700 hover:to-red-700 text-white px-8 py-3 rounded-lg font-bold transition shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      {isArabic ? "جاري الحفظ..." : "Saving..."}
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
                      {isEdit
                        ? isArabic
                          ? "تحديث المخاطرة"
                          : "Update Risk"
                        : isArabic
                          ? "إنشاء المخاطرة"
                          : "Create Risk"}
                    </>
                  )}
                </button>
                <button
                  type="button"
                  onClick={handleClose}
                  disabled={loading}
                  className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-800 px-8 py-3 rounded-lg font-bold transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isArabic ? "إلغاء" : "Cancel"}
                </button>
              </div>
            </>
          )}
        </form>
      </div>
    </div>
  );
}
