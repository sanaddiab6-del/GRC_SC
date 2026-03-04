"use client";

import axios from "axios";
import { useCallback, useEffect, useState } from "react";

interface Control {
  control_id: string;
  control_number: string;
  title_en: string;
  title_ar: string;
}

interface EvidenceUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  locale: "en" | "ar";
}

export default function EvidenceUploadModal({
  isOpen,
  onClose,
  onSuccess,
  locale,
}: EvidenceUploadModalProps) {
  const isArabic = locale === "ar";

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    evidence_type: "document",
    control_id: "",
  });

  const [file, setFile] = useState<File | null>(null);
  const [controls, setControls] = useState<Control[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<number | null>(null);
  const [error, setError] = useState("");
  const [loadingControls, setLoadingControls] = useState(false);

  const fetchControls = useCallback(async () => {
    setLoadingControls(true);
    try {
      const response = await axios.get(
        "http://localhost:8000/api/v1/controls",
        {
          params: { limit: 1000 }, // Get all controls for dropdown
        },
      );
      setControls(response.data.items || []);
    } catch (err) {
      console.error("Failed to fetch controls:", err);
      setError(isArabic ? "فشل تحميل الضوابط" : "Failed to load controls");
    } finally {
      setLoadingControls(false);
    }
  }, [isArabic]);

  // Fetch controls when modal opens
  useEffect(() => {
    if (isOpen) {
      fetchControls();
    }
  }, [isOpen, fetchControls]);

  const handleInputChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (error) setError("");
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      // Enforce 25MB max
      if (selectedFile.size > 25 * 1024 * 1024) {
        setError(
          isArabic
            ? "حجم الملف يجب أن يكون أقل من 25 ميجابايت"
            : "File size must be less than 25MB",
        );
        setFile(null);
        return;
      }
      // Validate MIME type
      const allowedTypes = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "image/png",
        "image/jpeg",
        "text/plain",
        "text/csv",
        "application/zip",
        "application/x-zip-compressed",
        "text/log",
      ];
      if (!allowedTypes.includes(selectedFile.type)) {
        setError(isArabic ? "نوع الملف غير مدعوم" : "Unsupported file type");
        setFile(null);
        return;
      }
      setFile(selectedFile);
      if (error) setError("");
    }
  };

  const validateForm = (): boolean => {
    if (!formData.title.trim()) {
      setError(isArabic ? "العنوان مطلوب" : "Title is required");
      return false;
    }
    if (!formData.control_id) {
      setError(isArabic ? "يجب اختيار ضابط" : "Control selection is required");
      return false;
    }
    // File is optional - metadata can be submitted without actual file
    if (file && file.size > 25 * 1024 * 1024) {
      setError(
        isArabic
          ? "حجم الملف يجب أن يكون أقل من 25 ميجابايت"
          : "File size must be less than 25MB",
      );
      return false;
    }
    // Validate MIME type again (defensive)
    if (file) {
      const allowedTypes = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "image/png",
        "image/jpeg",
        "text/plain",
        "text/csv",
        "application/zip",
        "application/x-zip-compressed",
        "text/log",
      ];
      if (!allowedTypes.includes(file.type)) {
        setError(isArabic ? "نوع الملف غير مدعوم" : "Unsupported file type");
        return false;
      }
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
    setUploadProgress(null);

    try {
      // Generate evidence ID
      const timestamp = Date.now();
      const evidenceId = `EVD-${formData.control_id}-${timestamp}`;

      // Get auth token from sessionStorage (adjust based on your auth implementation)
      const token = sessionStorage.getItem("access_token");

      // If file is present, upload file first (simulate upload progress)
      if (file) {
        // Simulate file upload with progress (replace with real upload API if available)
        const formDataObj = new FormData();
        formDataObj.append("file", file);
        // Example: upload to /api/v1/evidence/upload (adjust as needed)
        await axios.post(
          "http://localhost:8000/api/v1/evidence/upload",
          formDataObj,
          {
            headers: {
              "Content-Type": "multipart/form-data",
              ...(token && { Authorization: `Bearer ${token}` }),
            },
            onUploadProgress: (progressEvent) => {
              if (progressEvent.total) {
                setUploadProgress(
                  Math.round(
                    (progressEvent.loaded * 100) / progressEvent.total,
                  ),
                );
              }
            },
          },
        );
      }

      // Create evidence data (JSON, not FormData for now - backend expects JSON)
      const evidenceData = {
        evidence_id: evidenceId,
        control_id: formData.control_id,
        evidence_type: formData.evidence_type,
        title_en: formData.title,
        title_ar: formData.title, // Same content for both languages for now
        description_en: formData.description || null,
        description_ar: formData.description || null,
        file_name: file?.name || null,
        file_size: file?.size || null,
        file_format: file?.name.split(".").pop() || null,
        file_path: file ? `/evidence/${evidenceId}/${file.name}` : null,
        retention_period_days: 2555, // 7 years default
      };

      const response = await axios.post(
        "http://localhost:8000/api/v1/evidence",
        evidenceData,
        {
          headers: {
            "Content-Type": "application/json",
            ...(token && { Authorization: `Bearer ${token}` }),
          },
        },
      );

      if (response.status === 201 || response.status === 200) {
        showSuccessToast(
          isArabic ? "تم رفع الدليل بنجاح" : "Evidence uploaded successfully",
        );
        setFormData({
          title: "",
          description: "",
          evidence_type: "document",
          control_id: "",
        });
        setFile(null);
        setUploadProgress(null);
        onSuccess();
        onClose();
      }
    } catch (err: any) {
      console.error("Upload failed:", err);
      const errorMessage =
        err.response?.data?.detail ||
        (isArabic
          ? "فشل رفع الدليل. يرجى المحاولة مرة أخرى."
          : "Failed to upload evidence. Please try again.");
      setError(errorMessage);
    } finally {
      setLoading(false);
      setUploadProgress(null);
    }
  };

  const showSuccessToast = (message: string) => {
    // Simple toast implementation - you can replace with a proper toast library
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
        title: "",
        description: "",
        evidence_type: "document",
        control_id: "",
      });
      setFile(null);
      setError("");
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-t-2xl">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold">
                {isArabic ? "رفع دليل جديد" : "Upload Evidence"}
              </h2>
              <p className="text-blue-100 mt-1">
                {isArabic
                  ? "قم برفع دليل الامتثال وربطه بالضابط المناسب"
                  : "Upload compliance evidence and link it to a control"}
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

          {/* Title */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {isArabic ? "العنوان *" : "Title *"}
            </label>
            <input
              type="text"
              name="title"
              value={formData.title}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={isArabic ? "عنوان الدليل" : "Evidence title"}
              required
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {isArabic ? "الوصف" : "Description"}
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              rows={3}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder={
                isArabic
                  ? "وصف تفصيلي للدليل..."
                  : "Detailed description of the evidence..."
              }
            />
          </div>

          {/* Evidence Type */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {isArabic ? "نوع الدليل *" : "Evidence Type *"}
            </label>
            <select
              name="evidence_type"
              value={formData.evidence_type}
              onChange={handleInputChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="document">
                {isArabic ? "مستند" : "Document"}
              </option>
              <option value="screenshot">
                {isArabic ? "لقطة شاشة" : "Screenshot"}
              </option>
              <option value="log">{isArabic ? "سجل" : "Log"}</option>
              <option value="certificate">
                {isArabic ? "شهادة" : "Certificate"}
              </option>
              <option value="policy">{isArabic ? "سياسة" : "Policy"}</option>
              <option value="other">{isArabic ? "أخرى" : "Other"}</option>
            </select>
          </div>

          {/* Control Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {isArabic ? "الضابط المرتبط *" : "Linked Control *"}
            </label>
            {loadingControls ? (
              <div className="flex items-center justify-center py-3 text-gray-500">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600 mr-2"></div>
                {isArabic ? "جاري التحميل..." : "Loading..."}
              </div>
            ) : (
              <select
                name="control_id"
                value={formData.control_id}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="">
                  {isArabic ? "اختر الضابط" : "Select control"}
                </option>
                {controls.map((control) => (
                  <option key={control.control_id} value={control.control_id}>
                    {control.control_number} -{" "}
                    {isArabic ? control.title_ar : control.title_en}
                  </option>
                ))}
              </select>
            )}
            <p className="text-xs text-gray-500 mt-1">
              {isArabic
                ? `${controls.length} ضابط متاح`
                : `${controls.length} controls available`}
            </p>
          </div>

          {/* File Upload */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              {isArabic ? "رفع الملف (اختياري)" : "Upload File (Optional)"}
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition">
              <input
                type="file"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg,.txt,.log"
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer flex flex-col items-center"
              >
                <svg
                  className="w-12 h-12 text-gray-400 mb-3"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                  />
                </svg>
                <span className="text-sm font-semibold text-gray-700">
                  {isArabic ? "اضغط لرفع الملف" : "Click to upload file"}
                </span>
                <span className="text-xs text-gray-500 mt-1">
                  {isArabic
                    ? "PDF, Word, Excel, صورة، أو ملف نصي (حد أقصى 25 ميجابايت)"
                    : "PDF, Word, Excel, Image, or Text file (Max 25MB)"}
                </span>
              </label>
            </div>
            {file && (
              <div className="mt-3 bg-blue-50 border border-blue-200 rounded-lg p-3 flex items-center justify-between">
                <div className="flex items-center">
                  <svg
                    className="w-5 h-5 text-blue-600 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M8 4a3 3 0 00-3 3v4a5 5 0 0010 0V7a1 1 0 112 0v4a7 7 0 11-14 0V7a5 5 0 0110 0v4a3 3 0 11-6 0V7a1 1 0 012 0v4a1 1 0 102 0V7a3 3 0 00-3-3z" />
                  </svg>
                  <div>
                    <p className="text-sm font-semibold text-gray-900">
                      {file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => setFile(null)}
                  className="text-red-600 hover:text-red-800 font-semibold text-sm"
                >
                  {isArabic ? "إزالة" : "Remove"}
                </button>
              </div>
            )}
            {/* Upload Progress Bar */}
            {uploadProgress !== null && (
              <div className="mt-2 w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-blue-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
                <div className="text-xs text-gray-700 mt-1 text-center">
                  {isArabic
                    ? `جاري رفع الملف... ${uploadProgress}%`
                    : `Uploading file... ${uploadProgress}%`}
                </div>
              </div>
            )}
          </div>

          {/* Info Box */}
          <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-700">
            <p className="font-semibold mb-2">
              {isArabic ? "📋 ملاحظة:" : "📋 Note:"}
            </p>
            <ul className="list-disc list-inside space-y-1 text-xs">
              <li>
                {isArabic
                  ? "سيتم مراجعة الدليل من قبل المسؤول قبل الموافقة"
                  : "Evidence will be reviewed by admin before approval"}
              </li>
              <li>
                {isArabic
                  ? "تأكد من أن الملف يحتوي على معلومات صحيحة وكاملة"
                  : "Ensure the file contains accurate and complete information"}
              </li>
              <li>
                {isArabic
                  ? "يمكنك رفع ملفات متعددة عن طريق تكرار العملية"
                  : "You can upload multiple files by repeating this process"}
              </li>
            </ul>
          </div>

          {/* Buttons */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={loading || loadingControls}
              className="flex-1 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-3 rounded-lg font-bold transition shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  {isArabic ? "جاري الرفع..." : "Uploading..."}
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
                      d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                    />
                  </svg>
                  {isArabic ? "رفع الدليل" : "Upload Evidence"}
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
        </form>
      </div>
    </div>
  );
}
