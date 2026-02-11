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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export default function EvidenceDetailPage() {
  const params = useParams();
  const locale = params.locale as string;
  const evidenceId = params.id as string;
  const t = useTranslations('evidenceDetail');

  const { data: evidence, error, isLoading } = useSWR(
    `/api/v1/evidence/${evidenceId}`,
    fetcher
  );

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-foreground"></div>
      </div>
    );
  }

  if (error || !evidence) {
    return (
      <div className="min-h-screen bg-background px-6 py-6">
        <div className="rounded-lg border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
          {t('loadError')}
        </div>
      </div>
    );
  }

  const validationVariant: Record<string, 'success' | 'warning' | 'destructive' | 'muted'> = {
    approved: 'success',
    pending: 'warning',
    rejected: 'destructive',
  };

  const auditMeta = {
    updatedAt: evidence.updated_at ? new Date(evidence.updated_at).toLocaleString() : t('notAvailable'),
    updatedBy: evidence.updated_by || t('system'),
    changeReason: evidence.change_reason || t('notProvided'),
    version: evidence.version || 'v1',
  };

  return (
    <div className="min-h-screen bg-background px-6 py-6">
      <div className="mb-6 flex items-center justify-between">
        <Link href={`/${locale}/evidence`} className="text-sm text-muted-foreground hover:text-foreground">
          {t('back')}
        </Link>
        <Button variant="outline" size="sm">
          {t('edit')}
        </Button>
      </div>

      <Card className="mb-6">
        <CardHeader>
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div>
              <div className="text-xs text-muted-foreground">{evidence.evidence_id || evidence.id}</div>
              <CardTitle className="text-2xl">{evidence.title}</CardTitle>
              {evidence.description && (
                <div className="text-sm text-muted-foreground mt-1">
                  {evidence.description}
                </div>
              )}
              <div className="mt-3 flex flex-wrap gap-2">
                <Badge variant={validationVariant[evidence.validation_status] || 'muted'}>
                  {t('validation')}: {evidence.validation_status || t('notAvailable')}
                </Badge>
                <Badge variant="outline">{t('type')}: {evidence.evidence_type || t('notAvailable')}</Badge>
                <Badge variant="outline">{t('source')}: {evidence.source || t('notAvailable')}</Badge>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge variant="outline">{t('classification')}: {evidence.classification || t('notAvailable')}</Badge>
              <Badge variant="outline">{t('retention')}: {evidence.retention || t('notAvailable')}</Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <div>
            <div className="text-xs text-muted-foreground">{t('owner')}</div>
            <div className="text-sm font-semibold">{evidence.owner || t('unassigned')}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('period')}</div>
            <div className="text-sm font-semibold">
              {evidence.collection_date ? new Date(evidence.collection_date).toLocaleDateString() : t('notAvailable')}
            </div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('control')}</div>
            <div className="text-sm font-semibold">{evidence.control_id || t('notAvailable')}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">{t('lastUpdated')}</div>
            <div className="text-sm font-semibold">{auditMeta.updatedAt}</div>
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
          <div className="flex items-end">
            <Button variant="outline" size="sm">
              {t('auditTrail')}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="summary">
        <TabsList>
          <TabsTrigger value="summary">{t('summary')}</TabsTrigger>
          <TabsTrigger value="validation">{t('validation')}</TabsTrigger>
          <TabsTrigger value="linked">{t('linkedControls')}</TabsTrigger>
          <TabsTrigger value="activity">{t('activity')}</TabsTrigger>
        </TabsList>

        <TabsContent value="summary">
          <Card>
            <CardContent className="grid gap-4 p-6 md:grid-cols-2">
              <div>
                <div className="text-xs text-muted-foreground">{t('type')}</div>
                <div className="text-sm font-semibold">{evidence.evidence_type || t('notAvailable')}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">{t('source')}</div>
                <div className="text-sm font-semibold">{evidence.source || t('notAvailable')}</div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">{t('period')}</div>
                <div className="text-sm font-semibold">
                  {evidence.collection_date ? new Date(evidence.collection_date).toLocaleDateString() : t('notAvailable')}
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground">{t('retention')}</div>
                <div className="text-sm font-semibold">{evidence.retention || t('notAvailable')}</div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="validation">
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{t('checklist')}</TableHead>
                    <TableHead>{t('status')}</TableHead>
                    <TableHead>{t('reviewer')}</TableHead>
                    <TableHead>{t('timestamp')}</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  <TableRow>
                    <TableCell>{t('hashVerification')}</TableCell>
                    <TableCell>{t('notAvailable')}</TableCell>
                    <TableCell>{t('notAvailable')}</TableCell>
                    <TableCell>{t('notAvailable')}</TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>{t('metadataReview')}</TableCell>
                    <TableCell>{t('notAvailable')}</TableCell>
                    <TableCell>{t('notAvailable')}</TableCell>
                    <TableCell>{t('notAvailable')}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="linked">
          <Card>
            <CardContent className="p-6">
              <div className="text-sm text-muted-foreground">
                {evidence.control_id ? (
                  <Link href={`/${locale}/controls/${evidence.control_id}`} className="font-semibold text-foreground hover:underline">
                    {evidence.control_id}
                  </Link>
                ) : (
                  t('noLinkedControls')
                )}
              </div>
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
