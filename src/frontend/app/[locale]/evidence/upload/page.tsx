'use client';

import { useTranslations } from 'next-intl';
import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import apiClient from '@/lib/api-client';
import useSWR from 'swr';

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export default function EvidenceUploadPage() {
  const t = useTranslations('evidence');
  const router = useRouter();
  const searchParams = useSearchParams();
  const preselectedControlId = searchParams.get('control_id');

  const [formData, setFormData] = useState({
    control_id: preselectedControlId || '',
    title: '',
    description: '',
    evidence_type: 'document',
    collection_date: new Date().toISOString().split('T')[0],
    expiry_date: '',
    file_path: '',
  });

  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const { data: controls } = useSWR('/api/v1/controls', fetcher);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      
      // Validate file size (max 10MB)
      if (selectedFile.size > 10 * 1024 * 1024) {
        setError('File size must be less than 10MB');
        return;
      }

      // Validate file type
      const allowedTypes = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'image/png',
        'image/jpeg',
        'text/plain',
      ];
      
      if (!allowedTypes.includes(selectedFile.type)) {
        setError('Invalid file type. Allowed: PDF, DOC, DOCX, PNG, JPG, TXT');
        return;
      }

      setFile(selectedFile);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setUploading(true);
    setError(null);

    try {
      // Validate required fields
      if (!formData.control_id || !formData.title || !file) {
        setError('Please fill in all required fields and select a file');
        setUploading(false);
        return;
      }

      // In a real app, we would upload the file to a storage service (Azure Blob, S3)
      // For now, we'll simulate with the filename
      const evidenceData = {
        ...formData,
        file_path: `/uploads/evidence/${Date.now()}_${file.name}`,
        file_size: file.size,
        mime_type: file.type,
      };

      await apiClient.post('/api/v1/evidence', evidenceData);
      
      setSuccess(true);
      setTimeout(() => {
        router.push(`/controls/${formData.control_id}`);
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload evidence');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Upload Evidence</h1>

        {success && (
          <div className="mb-6 bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-800 font-semibold">✓ Evidence uploaded successfully!</p>
            <p className="text-green-600 text-sm mt-1">Redirecting to control page...</p>
          </div>
        )}

        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">✗ {error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-lg p-6 space-y-6">
          {/* Control Selection */}
          <div>
            <label className="block text-sm font-semibold mb-2">
              Control <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.control_id}
              onChange={(e) => setFormData({ ...formData, control_id: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              required
            >
              <option value="">Select a control</option>
              {controls?.items?.map((control: any) => (
                <option key={control.control_id} value={control.control_id}>
                  {control.control_id} - {control.title_en}
                </option>
              ))}
            </select>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-semibold mb-2">
              Evidence Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              placeholder="e.g., Access Control Policy Document"
              required
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-semibold mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              rows={4}
              placeholder="Describe the evidence and what it demonstrates..."
            />
          </div>

          {/* Evidence Type */}
          <div>
            <label className="block text-sm font-semibold mb-2">
              Evidence Type <span className="text-red-500">*</span>
            </label>
            <select
              value={formData.evidence_type}
              onChange={(e) => setFormData({ ...formData, evidence_type: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              required
            >
              <option value="document">Document</option>
              <option value="screenshot">Screenshot</option>
              <option value="log">System Log</option>
              <option value="certificate">Certificate</option>
              <option value="report">Report</option>
              <option value="other">Other</option>
            </select>
          </div>

          {/* Dates */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-semibold mb-2">
                Collection Date <span className="text-red-500">*</span>
              </label>
              <input
                type="date"
                value={formData.collection_date}
                onChange={(e) => setFormData({ ...formData, collection_date: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-semibold mb-2">Expiry Date (Optional)</label>
              <input
                type="date"
                value={formData.expiry_date}
                onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          {/* File Upload */}
          <div>
            <label className="block text-sm font-semibold mb-2">
              Upload File <span className="text-red-500">*</span>
            </label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-500 transition-colors">
              <input
                type="file"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
                accept=".pdf,.doc,.docx,.png,.jpg,.jpeg,.txt"
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
                {file ? (
                  <div>
                    <p className="text-primary-600 font-semibold">{file.name}</p>
                    <p className="text-sm text-gray-500 mt-1">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                ) : (
                  <div>
                    <p className="text-gray-600 font-semibold">Click to upload or drag and drop</p>
                    <p className="text-sm text-gray-500 mt-1">
                      PDF, DOC, DOCX, PNG, JPG, TXT (max 10MB)
                    </p>
                  </div>
                )}
              </label>
            </div>
          </div>

          {/* Submit Buttons */}
          <div className="flex gap-4 pt-4">
            <button
              type="submit"
              disabled={uploading || success}
              className="flex-1 bg-primary-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              {uploading ? 'Uploading...' : 'Upload Evidence'}
            </button>
            <button
              type="button"
              onClick={() => router.back()}
              className="px-6 py-3 border border-gray-300 rounded-lg font-semibold hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </form>

        {/* Guidelines */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="font-semibold text-blue-900 mb-2">Evidence Guidelines</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Ensure evidence is recent and relevant to the control</li>
            <li>• Remove any sensitive or confidential information before uploading</li>
            <li>• Use clear, descriptive titles and descriptions</li>
            <li>• Set expiry dates for time-sensitive evidence (e.g., certificates)</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
