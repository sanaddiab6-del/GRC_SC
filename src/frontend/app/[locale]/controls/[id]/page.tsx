'use client';

import { useTranslations } from 'next-intl';
import useSWR from 'swr';
import apiClient from '@/lib/api-client';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export default function ControlDetailPage() {
  const params = useParams();
  const controlId = params.id as string;
  const locale = params.locale as string;
  const t = useTranslations('controlDetail');
  const tCommon = useTranslations('common');

  const { data: control, error, isLoading } = useSWR(
    `/api/v1/controls/${controlId}`,
    fetcher
  );

  const { data: evidenceList } = useSWR(
    `/api/v1/evidence?control_id=${controlId}`,
    fetcher
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-foreground"></div>
      </div>
    );
  }

  if (error || !control) {
    return (
      <div className="min-h-screen bg-background px-6 py-6">
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
          {t('loadError')}
        </div>
      </div>
    );
  }

  const statusVariant: Record<string, 'success' | 'warning' | 'destructive' | 'muted'> = {
    compliant: 'success',
    in_progress: 'warning',
    non_compliant: 'destructive',
    not_started: 'muted',
  };

  const evidenceCount = evidenceList?.items?.length || 0;
  const evidenceCompletenessLabel = evidenceCount > 0 ? t('evidencePartial') : t('evidenceMissing');
  const evidenceVariant = evidenceCount > 0 ? 'warning' : 'destructive';

  const auditMeta = {
    updatedAt: control.updated_at ? new Date(control.updated_at).toLocaleString() : t('notAvailable'),
    updatedBy: control.updated_by || t('system'),
    changeReason: control.change_reason || t('notProvided'),
    version: control.version || 'v1',
  };

  return (
    <div className="min-h-screen bg-background px-6 py-6">
      <div className="mb-6 flex items-center justify-between">
        <Link href={`/${locale}/controls`} className="text-sm text-muted-foreground hover:text-foreground">
          {t('back')}
        </Link>
        <Button variant="outline" size="sm">
          {tCommon('edit')}
        </Button>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="text-xs text-muted-foreground">{control.control_id}</div>
              <CardTitle className="text-2xl">{control.title_en}</CardTitle>
              {control.title_ar && (
                <div className="text-sm text-muted-foreground mt-1" dir="rtl">
                  {control.title_ar}
                </div>
              )}
              <div className="mt-3 flex flex-wrap gap-2">
                <Badge variant={statusVariant[control.status] || 'muted'}>
                  {t('implementationStatus')}: {control.status?.replace('_', ' ')}
                </Badge>
                <Badge variant={evidenceVariant}>
                  {t('evidenceCompleteness')}: {evidenceCompletenessLabel}
                </Badge>
                <Badge variant="muted">{t('effectiveness')}: {t('notTested')}</Badge>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">ECC</Badge>
              <Badge variant="outline">CCC</Badge>
              <Badge variant="outline">PDPL</Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <div>
            <div className="text-xs text-muted-foreground">{t('owner')}</div>
            <div className="text-sm font-semibold">{t('unassigned')}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('dueDate')}</div>
            <div className="text-sm font-semibold">{t('notScheduled')}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('nextReview')}</div>
            <div className="text-sm font-semibold">{t('notScheduled')}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('lastUpdated')}</div>
            <div className="text-sm font-semibold">{auditMeta.updatedAt}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('updatedBy')}</div>
            <div className="text-sm font-semibold">{auditMeta.updatedBy}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('changeReason')}</div>
            <div className="text-sm font-semibold">{auditMeta.changeReason}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('version')}</div>
            <div className="text-sm font-semibold">{auditMeta.version}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('auditTrail')}</div>
            <Link href={`/${locale}/controls/${controlId}#activity`} className="text-sm font-semibold text-foreground">
              {t('viewAuditTrail')}
            </Link>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="summary">
        <TabsList>
          <TabsTrigger value="summary">{t('summary')}</TabsTrigger>
          <TabsTrigger value="requirements">{t('requirements')}</TabsTrigger>
          <TabsTrigger value="implementation">{t('implementation')}</TabsTrigger>
          <TabsTrigger value="evidence">{t('evidence')}</TabsTrigger>
          <TabsTrigger value="testing">{t('testing')}</TabsTrigger>
          <TabsTrigger value="exceptions">{t('exceptions')}</TabsTrigger>
          <TabsTrigger value="activity">{t('activity')}</TabsTrigger>
        </TabsList>

        <TabsContent value="summary">
          <Card>
            <CardContent className="space-y-4 pt-6">
              <div>
                <div className="text-sm font-semibold">{t('controlText')}</div>
                <p className="text-sm text-muted-foreground mt-2">{control.description_en}</p>
                {control.description_ar && (
                  <p className="text-sm text-muted-foreground mt-2" dir="rtl">
                    {control.description_ar}
                  </p>
                )}
              </div>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
                <div>
                  <div className="text-xs text-muted-foreground">{t('framework')}</div>
                  <div className="text-sm font-semibold">{control.framework}</div>
                  import { Badge } from '@/components/ui/badge';
                  import { Button } from '@/components/ui/button';
                  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
                  import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
                  import {
                    Table,
                    TableBody,
                    TableCell,
                    TableHead,
                    TableHeader,
                    TableRow,
                  } from '@/components/ui/table';
                </div>
                <div>
                  <div className="text-xs text-muted-foreground">{t('domain')}</div>
                  <div className="text-sm font-semibold">{control.domain}</div>
                </div>
                <div>
                  <div className="text-xs text-muted-foreground">{t('maturity')}</div>
                  <div className="text-sm font-semibold">{control.maturity_level ?? '--'}</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="requirements">
          <Card>
                      activeTab === 'evidence' ? `/api/v1/evidence?control_id=${controlId}` : null,
              <div>
                <div className="text-sm font-semibold">{t('mappings')}</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  <Badge variant="outline">ECC</Badge>
                  <Badge variant="outline">CCC</Badge>
                  <Badge variant="outline">PDPL</Badge>
                </div>
              </div>
              <div>
                <div className="text-sm font-semibold">{t('requirements')}</div>
                <p className="text-sm text-muted-foreground mt-2">{control.description_en}</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="implementation">
          <Card>
            <CardContent className="space-y-4 pt-6">
              <div className="text-sm font-semibold">{t('policyProcedure')}</div>
              <p className="text-sm text-muted-foreground mt-2">
                {control.implementation_guidance || t('notProvided')}
              </p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="evidence">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle className="text-lg">{t('evidenceItems')}</CardTitle>
              <Button size="sm" asChild>
                <Link href={`/${locale}/evidence/upload?control_id=${controlId}`}>
                  {t('uploadEvidence')}
                </Link>
              </Button>
            </CardHeader>
            <CardContent>
              {evidenceList?.items?.length ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>{t('evidenceTitle')}</TableHead>
                      <TableHead>{t('evidenceType')}</TableHead>
                      <TableHead>{t('evidenceSource')}</TableHead>
                      <TableHead>{t('timePeriod')}</TableHead>
                      <TableHead>{t('validation')}</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {evidenceList.items.map((evidence: any) => (
                      <TableRow key={evidence.id}>
                        <TableCell className="font-semibold">{evidence.title}</TableCell>
                        <TableCell>{evidence.evidence_type}</TableCell>
                        <TableCell>{evidence.source || t('notAvailable')}</TableCell>
                        <TableCell>{evidence.collection_date ? new Date(evidence.collection_date).toLocaleDateString() : '--'}</TableCell>
                        <TableCell>
                          <Badge variant={evidence.validation_status === 'approved' ? 'success' : evidence.validation_status === 'rejected' ? 'destructive' : 'warning'}>
                            {evidence.validation_status || t('notAvailable')}
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="py-10 text-center text-sm text-muted-foreground">
                  <div className="font-semibold">{t('noEvidenceTitle')}</div>
                  <div>{t('noEvidenceBody')}</div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="testing">
          <Card>
            <CardContent className="space-y-4 pt-6">
              <div className="text-sm font-semibold">{t('testingProcedure')}</div>
              {control.testing_procedure ? (
                <ol className="list-decimal space-y-2 pl-5 text-sm text-muted-foreground">
                  {control.testing_procedure.split('\n').map((step: string, idx: number) => (
                    <li key={idx}>{step}</li>
                  ))}
                </ol>
              ) : (
                <div className="text-sm text-muted-foreground">{t('notProvided')}</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="exceptions">
          <Card>
            <CardContent className="space-y-3 pt-6">
              <div className="text-sm font-semibold">{t('exceptionsTitle')}</div>
              <div className="text-sm text-muted-foreground">{t('noExceptions')}</div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity">
          <Card id="activity">
            <CardContent className="space-y-4 pt-6">
              <div className="text-sm font-semibold">{t('activity')}</div>
              <div className="space-y-4 text-sm">
                <div className="border-l-2 border-border pl-4">
                  <div className="font-semibold">{t('statusUpdated')}</div>
                  <div className="text-muted-foreground">{t('statusUpdatedDetail', { status: control.status })}</div>
                  <div className="text-xs text-muted-foreground">{auditMeta.updatedAt}</div>
                </div>
                <div className="border-l-2 border-border pl-4">
                  <div className="font-semibold">{t('controlCreated')}</div>
                  <div className="text-muted-foreground">{t('controlCreatedDetail')}</div>
                  <div className="text-xs text-muted-foreground">
                    {control.created_at ? new Date(control.created_at).toLocaleDateString() : '--'}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
