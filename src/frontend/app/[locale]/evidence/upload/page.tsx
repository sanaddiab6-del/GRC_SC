"use client";

import { useTranslations } from 'next-intl';
import { useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import apiClient from '@/lib/api-client';
import useSWR from 'swr';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export default function EvidenceUploadPage() {
  const t = useTranslations('evidenceUpload');
  const router = useRouter();
  const searchParams = useSearchParams();
  const preselectedControlId = searchParams.get('control_id');

  const [step, setStep] = useState(0);
  const [showChangeReason, setShowChangeReason] = useState(false);
  const [changeReason, setChangeReason] = useState('');
  const [formData, setFormData] = useState({
    control_id: preselectedControlId || '',
    title: '',
    description: '',
    evidence_type: 'document',
    source: 'manual',
    owner: '',
    classification: 'internal',
    retention: '7y',
    period_start: new Date().toISOString().split('T')[0],
    period_end: new Date().toISOString().split('T')[0],
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
        setError(t('errors.fileSize'));
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
        setError(t('errors.fileType'));
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
        setError(t('errors.required'));
        setUploading(false);
        return;
      }

      if (!changeReason) {
        setError(t('errors.changeReason'));
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
        change_reason: changeReason,
      };

      await apiClient.post('/api/v1/evidence', evidenceData);
      
      setSuccess(true);
      setTimeout(() => {
        router.push(`/controls/${formData.control_id}`);
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || t('errors.uploadFailed'));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background px-6 py-6">
      <div className="mx-auto max-w-4xl space-y-6">
        <div>
          <h1 className="text-2xl font-semibold">{t('title')}</h1>
          <p className="text-sm text-muted-foreground">{t('description')}</p>
        </div>

        {success && (
          <Card className="border border-success/30 bg-success/10">
            <CardContent className="p-4 text-sm text-foreground">
              {t('success')}
            </CardContent>
          </Card>
        )}

        {error && (
          <Card className="border border-destructive/30 bg-destructive/10">
            <CardContent className="p-4 text-sm text-destructive">{error}</CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>{t('steps.title', { step: step + 1, total: 3 })}</CardTitle>
              <Badge variant="outline">{t(`steps.step${step + 1}`)}</Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-6">
            {step === 0 && (
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label className="text-sm font-semibold">
                    {t('control')} <span className="text-destructive">*</span>
                  </label>
                  <Select
                    value={formData.control_id}
                    onValueChange={(value) => setFormData({ ...formData, control_id: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t('controlPlaceholder')} />
                    </SelectTrigger>
                    <SelectContent>
                      {controls?.items?.map((control: any) => (
                        <SelectItem key={control.control_id} value={control.control_id}>
                          {control.control_id} - {control.title_en}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-semibold">
                    {t('titleLabel')} <span className="text-destructive">*</span>
                  </label>
                  <Input
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    placeholder={t('titlePlaceholder')}
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="text-sm font-semibold">{t('description')}</label>
                  <Textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder={t('descriptionPlaceholder')}
                  />
                </div>
                <div>
                  <label className="text-sm font-semibold">
                    {t('evidenceType')} <span className="text-destructive">*</span>
                  </label>
                  <Select
                    value={formData.evidence_type}
                    onValueChange={(value) => setFormData({ ...formData, evidence_type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t('evidenceType')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="document">{t('document')}</SelectItem>
                      <SelectItem value="screenshot">{t('screenshot')}</SelectItem>
                      <SelectItem value="log">{t('log')}</SelectItem>
                      <SelectItem value="certificate">{t('certificate')}</SelectItem>
                      <SelectItem value="report">{t('report')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-semibold">{t('source')}</label>
                  <Select
                    value={formData.source}
                    onValueChange={(value) => setFormData({ ...formData, source: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t('source')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="manual">{t('sourceManual')}</SelectItem>
                      <SelectItem value="system">{t('sourceSystem')}</SelectItem>
                      <SelectItem value="integration">{t('sourceIntegration')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            )}

            {step === 1 && (
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                <div>
                  <label className="text-sm font-semibold">{t('classification')}</label>
                  <Select
                    value={formData.classification}
                    onValueChange={(value) => setFormData({ ...formData, classification: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t('classification')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="public">{t('classificationPublic')}</SelectItem>
                      <SelectItem value="internal">{t('classificationInternal')}</SelectItem>
                      <SelectItem value="confidential">{t('classificationConfidential')}</SelectItem>
                      <SelectItem value="restricted">{t('classificationRestricted')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-semibold">{t('retention')}</label>
                  <Select
                    value={formData.retention}
                    onValueChange={(value) => setFormData({ ...formData, retention: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder={t('retention')} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1y">{t('retention1y')}</SelectItem>
                      <SelectItem value="3y">{t('retention3y')}</SelectItem>
                      <SelectItem value="7y">{t('retention7y')}</SelectItem>
                      <SelectItem value="permanent">{t('retentionPermanent')}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-semibold">{t('periodStart')}</label>
                  <Input
                    type="date"
                    value={formData.period_start}
                    onChange={(e) => setFormData({ ...formData, period_start: e.target.value })}
                  />
                </div>
                <div>
                  <label className="text-sm font-semibold">{t('periodEnd')}</label>
                  <Input
                    type="date"
                    value={formData.period_end}
                    onChange={(e) => setFormData({ ...formData, period_end: e.target.value })}
                  />
                </div>
                <div>
                  <label className="text-sm font-semibold">{t('owner')}</label>
                  <Input
                    value={formData.owner}
                    onChange={(e) => setFormData({ ...formData, owner: e.target.value })}
                    placeholder={t('ownerPlaceholder')}
                  />
                </div>
                <div>
                  <label className="text-sm font-semibold">{t('expiryDate')}</label>
                  <Input
                    type="date"
                    value={formData.expiry_date}
                    onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                  />
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="space-y-4">
                <div>
                  <label className="text-sm font-semibold">
                    {t('uploadFile')} <span className="text-destructive">*</span>
                  </label>
                  <Input
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.doc,.docx,.png,.jpg,.jpeg,.txt"
                  />
                  <p className="text-xs text-muted-foreground mt-2">{t('allowedTypes')}</p>
                </div>
                <Card className="bg-muted/40">
                  <CardContent className="p-4 text-sm">
                    <div className="font-semibold mb-2">{t('review')}</div>
                    <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
                      <div>{t('control')}: {formData.control_id || '--'}</div>
                      <div>{t('evidenceType')}: {formData.evidence_type}</div>
                      <div>{t('classification')}: {formData.classification}</div>
                      <div>{t('retention')}: {formData.retention}</div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            <div className="flex items-center justify-between border-t border-border pt-4">
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={step === 0}
                  onClick={() => setStep((prev) => Math.max(prev - 1, 0))}
                >
                  {t('back')}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setStep((prev) => Math.min(prev + 1, 2))}
                  disabled={step === 2}
                >
                  {t('next')}
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="secondary" size="sm">
                  {t('saveDraft')}
                </Button>
                <Button size="sm" onClick={() => setShowChangeReason(true)} disabled={uploading || success || step < 2}>
                  {uploading ? t('submitting') : t('submit')}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Dialog open={showChangeReason} onOpenChange={setShowChangeReason}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{t('changeReasonTitle')}</DialogTitle>
              <DialogDescription>{t('changeReasonDescription')}</DialogDescription>
            </DialogHeader>
            <Textarea
              value={changeReason}
              onChange={(e) => setChangeReason(e.target.value)}
              placeholder={t('changeReasonPlaceholder')}
            />
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowChangeReason(false)}>
                {t('cancel')}
              </Button>
              <Button
                onClick={() => {
                  setShowChangeReason(false);
                  handleSubmit({ preventDefault: () => {} } as React.FormEvent);
                }}
              >
                {t('confirmSubmit')}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
