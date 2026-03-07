'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useState } from 'react';
import useSWR from 'swr';
import { useTranslations } from 'next-intl';
import apiClient from '@/lib/api-client';
import DynamicSectionRenderer from '@/components/dynamic/DynamicSectionRenderer';
import { applyWorkflowTransition, useCustomFields, useUiPageConfig, useWorkflowConfig } from '@/lib/dynamic-config';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import RiskAssessmentModal from '@/components/modals/RiskAssessmentModal';

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export default function RiskDetailPage() {
  const params = useParams();
  const locale = params.locale as string;
  const riskId = params.id as string;
  const t = useTranslations('riskDetail');
  const tList = useTranslations('riskList');

  const { data: risk, error, isLoading, mutate } = useSWR(
    `/api/v1/risks/${riskId}`,
    fetcher
  );
  const { data: workflowConfig } = useWorkflowConfig('risk');
  const { fields: customFields } = useCustomFields('risk', riskId);
  const { data: uiConfig } = useUiPageConfig('risks');

  const [workflowError, setWorkflowError] = useState<string | null>(null);

  // Assessment Modal State
  const [isAssessModalOpen, setIsAssessModalOpen] = useState(false);

  // Role-based access control
  const canAssessRisk = () => {
    try {
      const userStr = localStorage.getItem('currentUser');
      if (!userStr) return false;
      const user = JSON.parse(userStr);
      const role = user.role?.toLowerCase() || '';
      // Only Admin, Compliance Officer, and Auditor can assess risks
      return ['admin', 'compliance officer', 'auditor'].includes(role);
    } catch {
      return false;
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-foreground"></div>
      </div>
    );
  }

  if (error || !risk) {
    return (
      <div className="min-h-screen bg-background px-6 py-6">
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
          {t('loadError')}
        </div>
      </div>
    );
  }

  const severityVariant: Record<string, 'success' | 'warning' | 'destructive' | 'muted'> = {
    critical: 'destructive',
    high: 'warning',
    medium: 'warning',
    low: 'success',
  };

  const statusVariant: Record<string, 'success' | 'warning' | 'destructive' | 'muted'> = {
    identified: 'muted',
    assessed: 'warning',
    treated: 'warning',
    accepted: 'muted',
    transferred: 'warning',
    mitigated: 'warning',
    closed: 'success',
  };

  const severityLabel = (value: string) => {
    if (value === 'critical') return tList('critical');
    if (value === 'high') return tList('high');
    if (value === 'medium') return tList('medium');
    if (value === 'low') return tList('low');
    return value;
  };

  const statusLabel = (value: string) => {
    const workflowLabel = workflowConfig?.states.find((state) => state.state_key === value)?.label;
    if (workflowLabel) return workflowLabel;
    if (value === 'identified') return tList('identified');
    if (value === 'assessed') return tList('assessed');
    if (value === 'treated') return tList('treated');
    if (value === 'accepted') return tList('accepted');
    if (value === 'transferred') return tList('transferred');
    if (value === 'mitigated') return tList('mitigated');
    if (value === 'closed') return tList('closed');
    return value;
  };

  const riskLevel = risk.residual_risk_level || risk.inherent_risk_level || '';
  const riskScore = risk.residual_risk_score ?? risk.inherent_risk_score;

  const currentWorkflowState = workflowConfig?.states.find(
    (state) => state.state_key === risk.status,
  );
  const workflowTransitions = workflowConfig?.transitions.filter(
    (transition) => transition.from_state === currentWorkflowState?.id,
  );

  const handleWorkflowTransition = async (toStateKey: string) => {
    setWorkflowError(null);
    try {
      await applyWorkflowTransition('risk', riskId, toStateKey);
      await mutate();
    } catch (err: any) {
      setWorkflowError(err?.response?.data?.detail || t('loadError'));
    }
  };

  return (
    <div className="min-h-screen bg-background px-6 py-6">
      <div className="mb-6 flex items-center justify-between">
        <Link href={`/${locale}/risks`} className="text-sm text-muted-foreground hover:text-foreground">
          {t('back')}
        </Link>
        <div className="flex gap-2">
          {canAssessRisk() && (
            <Button
              variant="default"
              size="sm"
              onClick={() => setIsAssessModalOpen(true)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <svg
                className="w-4 h-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              {t('assessRisk')}
            </Button>
          )}
          <Button variant="outline" size="sm">
            {t('edit')}
          </Button>
        </div>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="text-xs text-muted-foreground">{risk.risk_number || risk.risk_id}</div>
              <CardTitle className="text-2xl">{risk.title_en || t('notAvailable')}</CardTitle>
              {risk.title_ar && (
                <div className="text-sm text-muted-foreground mt-1" dir="rtl">
                  {risk.title_ar}
                </div>
              )}
              <div className="mt-3 flex flex-wrap gap-2">
                <Badge variant={severityVariant[riskLevel] || 'muted'}>
                  {t('severity')}: {riskLevel ? severityLabel(riskLevel) : t('notAvailable')}
                </Badge>
                <Badge variant={statusVariant[risk.status] || 'muted'}>
                  {t('status')}: {risk.status ? statusLabel(risk.status) : t('notAvailable')}
                </Badge>
                <Badge variant="outline">{t('type')}: {risk.category || t('notAvailable')}</Badge>
              </div>
              {workflowTransitions && workflowTransitions.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-2">
                  {workflowTransitions.map((transition) => {
                    const targetState = workflowConfig?.states.find(
                      (state) => state.id === transition.to_state,
                    );
                    if (!targetState?.state_key) {
                      return null;
                    }
                    return (
                      <Button
                        key={transition.id}
                        size="sm"
                        variant="outline"
                        onClick={() => handleWorkflowTransition(targetState.state_key)}
                      >
                        {transition.action_label}
                      </Button>
                    );
                  })}
                </div>
              )}
              {workflowError && (
                <div className="mt-2 text-sm text-destructive">{workflowError}</div>
              )}
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">{t('owner')}: {risk.risk_owner || t('unassigned')}</Badge>
              <Badge variant="outline">
                {t('nextReview')}: {risk.next_review_date || t('notScheduled')}
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-4">
          <div>
            <div className="text-xs text-muted-foreground">{t('likelihood')}</div>
            <div className="text-sm font-semibold">{risk.likelihood ?? '--'}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('impact')}</div>
            <div className="text-sm font-semibold">{risk.impact ?? '--'}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('score')}</div>
            <div className="text-sm font-semibold">{riskScore ?? '--'}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('lastUpdated')}</div>
            <div className="text-sm font-semibold">
              {risk.last_assessed_at
                ? new Date(risk.last_assessed_at).toLocaleString()
                : risk.identified_at
                  ? new Date(risk.identified_at).toLocaleString()
                  : t('notAvailable')}
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="mb-6">
        <CardHeader>
          <CardTitle>{t('auditMeta')}</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-5">
          <div>
            <div className="text-xs text-muted-foreground">{t('lastUpdated')}</div>
            <div className="text-sm font-semibold">
              {risk.last_assessed_at
                ? new Date(risk.last_assessed_at).toLocaleString()
                : risk.identified_at
                  ? new Date(risk.identified_at).toLocaleString()
                  : t('notAvailable')}
            </div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('updatedBy')}</div>
            <div className="text-sm font-semibold">{risk.updated_by || t('system')}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('changeReason')}</div>
            <div className="text-sm font-semibold">{risk.change_reason || t('notProvided')}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('version')}</div>
            <div className="text-sm font-semibold">{risk.version || 'v1'}</div>
          </div>
          <div className="flex items-end">
            <Button variant="outline" size="sm">{t('auditTrail')}</Button>
          </div>
        </CardContent>
      </Card>

      {uiConfig && customFields.length > 0 && (
        <DynamicSectionRenderer
          config={uiConfig}
          renderSection={(section) => {
            if (section.section_key !== 'custom_fields') {
              return null;
            }
            return (
              <div className="grid gap-3 md:grid-cols-2">
                {customFields.map((field) => (
                  <div key={field.id} className="rounded-lg border border-border/60 p-3">
                    <div className="text-xs text-muted-foreground">{field.field_label}</div>
                    <div className="text-sm font-medium">
                      {field.value !== undefined && field.value !== null && field.value !== ''
                        ? String(field.value)
                        : t('notAvailable')}
                    </div>
                  </div>
                ))}
              </div>
            );
          }}
        />
      )}

      <Tabs defaultValue="summary">
        <TabsList>
          <TabsTrigger value="summary">{t('summary')}</TabsTrigger>
          <TabsTrigger value="assessment">{t('assessment')}</TabsTrigger>
          <TabsTrigger value="treatment">{t('treatment')}</TabsTrigger>
          <TabsTrigger value="evidence">{t('evidence')}</TabsTrigger>
          <TabsTrigger value="activity">{t('activity')}</TabsTrigger>
        </TabsList>

        <TabsContent value="summary">
          <Card>
            <CardContent className="p-6 space-y-3">
              <div className="text-sm font-semibold">{t('summary')}</div>
              <p className="text-sm text-muted-foreground">
                {locale === 'ar'
                  ? (risk.description_ar || t('notProvided'))
                  : (risk.description_en || t('notProvided'))}
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="assessment">
          <Card>
            <CardContent className="p-6 grid gap-4 md:grid-cols-3">
              <div>
                <div className="text-xs text-muted-foreground">{t('likelihood')}</div>
                <div className="text-sm font-semibold">{risk.likelihood ?? '--'}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">{t('impact')}</div>
                <div className="text-sm font-semibold">{risk.impact ?? '--'}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">{t('score')}</div>
                <div className="text-sm font-semibold">{riskScore ?? '--'}</div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="treatment">
          <Card>
            <CardContent className="p-6 space-y-2">
              <div className="text-sm font-semibold">{t('treatmentPlan')}</div>
              <p className="text-sm text-muted-foreground">
                {locale === 'ar'
                  ? (risk.treatment_plan_ar || t('notProvided'))
                  : (risk.treatment_plan_en || t('notProvided'))}
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="evidence">
          <Card>
            <CardContent className="p-6">
              <div className="text-sm text-muted-foreground">{t('noEvidence')}</div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity">
          <Card>
            <CardContent className="p-6">
              <div className="text-sm text-muted-foreground">{t('noActivity')}</div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Risk Assessment Modal */}
      <RiskAssessmentModal
        isOpen={isAssessModalOpen}
        onClose={() => setIsAssessModalOpen(false)}
        onSuccess={() => mutate()}
        locale={locale as 'en' | 'ar'}
        riskId={riskId}
        currentLikelihood={risk?.likelihood}
        currentImpact={risk?.impact}
      />
    </div>
  );
}
