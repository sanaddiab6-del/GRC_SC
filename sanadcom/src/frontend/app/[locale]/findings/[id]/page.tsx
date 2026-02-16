'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import useSWR from 'swr';
import { useTranslations } from 'next-intl';
import apiClient from '@/lib/api-client';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export default function FindingDetailPage() {
  const params = useParams();
  const locale = params.locale as string;
  const findingId = params.id as string;
  const t = useTranslations('findingDetail');
  const tList = useTranslations('findingsList');

  const { data: finding, error, isLoading } = useSWR(
    `/api/v1/enterprise/audit-findings/${findingId}`,
    fetcher
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-foreground"></div>
      </div>
    );
  }

  if (error || !finding) {
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
    observation: 'muted',
    opportunity_for_improvement: 'muted',
  };

  const statusVariant: Record<string, 'success' | 'warning' | 'destructive' | 'muted'> = {
    open: 'destructive',
    in_progress: 'warning',
    pending_verification: 'warning',
    verified: 'success',
    closed: 'success',
    risk_accepted: 'muted',
  };

  const severityLabel = (value: string) => {
    if (value === 'critical') return tList('critical');
    if (value === 'high') return tList('high');
    if (value === 'medium') return tList('medium');
    if (value === 'low') return tList('low');
    if (value === 'observation') return tList('observation');
    if (value === 'opportunity_for_improvement') return tList('opportunityForImprovement');
    return value;
  };

  const statusLabel = (value: string) => {
    if (value === 'open') return tList('open');
    if (value === 'in_progress') return tList('inProgress');
    if (value === 'pending_verification') return tList('pendingVerification');
    if (value === 'verified') return tList('verified');
    if (value === 'closed') return tList('closed');
    if (value === 'risk_accepted') return tList('riskAccepted');
    return value;
  };

  return (
    <div className="min-h-screen bg-background px-6 py-6">
      <div className="mb-6 flex items-center justify-between">
        <Link href={`/${locale}/findings`} className="text-sm text-muted-foreground hover:text-foreground">
          {t('back')}
        </Link>
        <Button variant="outline" size="sm">{t('edit')}</Button>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="text-xs text-muted-foreground">{finding.finding_id || finding.id}</div>
              <CardTitle className="text-2xl">{finding.title_en || finding.title}</CardTitle>
              {finding.title_ar && (
                <div className="text-sm text-muted-foreground mt-1" dir="rtl">
                  {finding.title_ar}
                </div>
              )}
              <div className="mt-3 flex flex-wrap gap-2">
                <Badge variant={severityVariant[finding.severity] || 'muted'}>
                  {t('severity')}: {finding.severity ? severityLabel(finding.severity) : t('notAvailable')}
                </Badge>
                <Badge variant={statusVariant[finding.status] || 'muted'}>
                  {t('status')}: {finding.status ? statusLabel(finding.status) : t('notAvailable')}
                </Badge>
                <Badge variant="outline">{t('owner')}: {t('unassigned')}</Badge>
                {finding.is_overdue && (
                  <Badge variant="destructive">{t('overdue')}</Badge>
                )}
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">{t('dueDate')}: {finding.target_closure_date || t('notScheduled')}</Badge>
              <Badge variant="outline">{t('riskRating')}: {finding.risk_rating || t('notAvailable')}</Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-4">
          <div>
            <div className="text-xs text-muted-foreground">{t('lastUpdated')}</div>
            <div className="text-sm font-semibold">
              {finding.updated_at
                ? new Date(finding.updated_at).toLocaleString()
                : finding.identified_at
                  ? new Date(finding.identified_at).toLocaleString()
                  : t('notAvailable')}
            </div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('updatedBy')}</div>
            <div className="text-sm font-semibold">{finding.updated_by || t('system')}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('changeReason')}</div>
            <div className="text-sm font-semibold">{finding.change_reason || t('notProvided')}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('version')}</div>
            <div className="text-sm font-semibold">{finding.version || 'v1'}</div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="summary">
        <TabsList>
          <TabsTrigger value="summary">{t('summary')}</TabsTrigger>
          <TabsTrigger value="rootCause">{t('rootCause')}</TabsTrigger>
          <TabsTrigger value="remediation">{t('remediation')}</TabsTrigger>
          <TabsTrigger value="evidence">{t('evidence')}</TabsTrigger>
          <TabsTrigger value="activity">{t('activity')}</TabsTrigger>
        </TabsList>

        <TabsContent value="summary">
          <Card>
            <CardContent className="p-6">
              <div className="text-sm font-semibold">{t('summary')}</div>
              <p className="text-sm text-muted-foreground mt-2">
                {locale === 'ar'
                  ? (finding.description_ar || t('notProvided'))
                  : (finding.description_en || t('notProvided'))}
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rootCause">
          <Card>
            <CardContent className="p-6">
              <div className="text-sm font-semibold">{t('rootCause')}</div>
              <p className="text-sm text-muted-foreground mt-2">
                {finding.root_cause || t('notProvided')}
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="remediation">
          <Card>
            <CardContent className="p-6 space-y-2">
              <div className="text-sm font-semibold">{t('remediation')}</div>
              <p className="text-sm text-muted-foreground">
                {locale === 'ar'
                  ? (finding.remediation_plan_ar || t('notProvided'))
                  : (finding.remediation_plan_en || t('notProvided'))}
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
    </div>
  );
}
