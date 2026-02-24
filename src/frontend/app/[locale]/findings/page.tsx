'use client';

import Link from 'next/link';
import { useEffect, useMemo, useState } from 'react';
import { useParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import useSWR from 'swr';
import apiClient from '@/lib/api-client';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

interface FindingItem {
  id: string;
  finding_id: string;
  title_en: string;
  title_ar?: string;
  severity: string;
  status: string;
  target_closure_date?: string;
  is_overdue?: boolean;
  risk_rating?: string;
}
const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export default function FindingsListPage() {
  const params = useParams();
  const locale = params.locale as string;
  const t = useTranslations('findingsList');

  const [search, setSearch] = useState('');
  const [severity, setSeverity] = useState('all');
  const [status, setStatus] = useState('all');
  const [visibleColumns, setVisibleColumns] = useState({
    owner: true,
    dueDate: true,
    framework: true,
  });

  const [page, setPage] = useState(1);
  const limit = 20;

  const queryParams = new URLSearchParams();
  if (severity !== 'all') queryParams.append('severity', severity);
  if (status !== 'all') queryParams.append('status', status);
  if (search) queryParams.append('search', search);
  queryParams.append('skip', String((page - 1) * limit));
  queryParams.append('limit', String(limit));

  const { data, error, isLoading } = useSWR(
    `/api/v1/enterprise/audit-findings?${queryParams.toString()}`,
    fetcher
  );

  useEffect(() => {
    setPage(1);
  }, [search, severity, status]);

  const filteredItems = useMemo(() => {
    const items: FindingItem[] = data?.items || [];
    return items;
  }, [data?.items]);

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
    if (value === 'critical') return t('critical');
    if (value === 'high') return t('high');
    if (value === 'medium') return t('medium');
    if (value === 'low') return t('low');
    if (value === 'observation') return t('observation');
    if (value === 'opportunity_for_improvement') return t('opportunityForImprovement');
    return value;
  };

  const statusLabel = (value: string) => {
    if (value === 'open') return t('open');
    if (value === 'in_progress') return t('inProgress');
    if (value === 'pending_verification') return t('pendingVerification');
    if (value === 'verified') return t('verified');
    if (value === 'closed') return t('closed');
    if (value === 'risk_accepted') return t('riskAccepted');
    return value;
  };

  const total = data?.total ?? filteredItems.length;
  const pagedItems = filteredItems;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-foreground"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background px-6 py-6">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">{t('title')}</h1>
          <p className="text-sm text-muted-foreground">{t('description')}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">{t('export')}</Button>
          <Button size="sm">{t('create')}</Button>
        </div>
      </div>

      <Card className="mb-6">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg">{t('filters')}</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t('searchPlaceholder')}
          />
          <Select value={severity} onValueChange={setSeverity}>
            <SelectTrigger>
              <SelectValue placeholder={t('severity')} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t('allSeverities')}</SelectItem>
              <SelectItem value="critical">{t('critical')}</SelectItem>
              <SelectItem value="high">{t('high')}</SelectItem>
              <SelectItem value="medium">{t('medium')}</SelectItem>
              <SelectItem value="low">{t('low')}</SelectItem>
              <SelectItem value="observation">{t('observation')}</SelectItem>
              <SelectItem value="opportunity_for_improvement">{t('opportunityForImprovement')}</SelectItem>
            </SelectContent>
          </Select>
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger>
              <SelectValue placeholder={t('status')} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t('allStatuses')}</SelectItem>
              <SelectItem value="open">{t('open')}</SelectItem>
              <SelectItem value="in_progress">{t('inProgress')}</SelectItem>
              <SelectItem value="pending_verification">{t('pendingVerification')}</SelectItem>
              <SelectItem value="verified">{t('verified')}</SelectItem>
              <SelectItem value="closed">{t('closed')}</SelectItem>
              <SelectItem value="risk_accepted">{t('riskAccepted')}</SelectItem>
            </SelectContent>
          </Select>
          <div className="flex items-center justify-end">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">{t('columns')}</Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>{t('columns')}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onSelect={() => setVisibleColumns((prev) => ({ ...prev, owner: !prev.owner }))}>
                  {visibleColumns.owner ? t('hide') : t('show')} {t('owner')}
                </DropdownMenuItem>
                <DropdownMenuItem onSelect={() => setVisibleColumns((prev) => ({ ...prev, dueDate: !prev.dueDate }))}>
                  {visibleColumns.dueDate ? t('hide') : t('show')} {t('dueDate')}
                </DropdownMenuItem>
                <DropdownMenuItem onSelect={() => setVisibleColumns((prev) => ({ ...prev, framework: !prev.framework }))}>
                  {visibleColumns.framework ? t('hide') : t('show')} {t('riskRating')}
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('findingId')}</TableHead>
                <TableHead>{t('titleColumn')}</TableHead>
                <TableHead>{t('severity')}</TableHead>
                <TableHead>{t('status')}</TableHead>
                {visibleColumns.owner && <TableHead>{t('owner')}</TableHead>}
                {visibleColumns.dueDate && <TableHead>{t('dueDate')}</TableHead>}
                {visibleColumns.framework && <TableHead>{t('riskRating')}</TableHead>}
                <TableHead className="text-right">{t('actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {pagedItems.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="py-10 text-center text-muted-foreground">
                    {t('noResults')}
                  </TableCell>
                </TableRow>
              ) : (
                pagedItems.map((item) => (
                  <TableRow key={item.finding_id}>
                    <TableCell>
                      <Link
                        href={`/${locale}/findings/${item.finding_id}`}
                        className="font-mono text-xs font-semibold hover:underline"
                      >
                        {item.finding_id}
                      </Link>
                    </TableCell>
                    <TableCell>
                      <div className="font-semibold text-sm">{item.title_en}</div>
                      {item.title_ar && (
                        <div className="text-xs text-muted-foreground" dir="rtl">
                          {item.title_ar}
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge variant={severityVariant[item.severity] || 'muted'}>
                        {severityLabel(item.severity)}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={statusVariant[item.status] || 'muted'}>
                        {statusLabel(item.status)}
                      </Badge>
                    </TableCell>
                    {visibleColumns.owner && <TableCell>{t('unassigned')}</TableCell>}
                    {visibleColumns.dueDate && (
                      <TableCell>{item.target_closure_date || t('notScheduled')}</TableCell>
                    )}
                    {visibleColumns.framework && <TableCell>{item.risk_rating || '--'}</TableCell>}
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">⋯</Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem asChild>
                            <Link href={`/${locale}/findings/${item.finding_id}`}>{t('view')}</Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem>{t('auditTrail')}</DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
        <div>{t('results', { count: pagedItems.length, total })}</div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(page - 1)}>
            {t('previous')}
          </Button>
          <span>{t('page', { page })}</span>
          <Button
            variant="outline"
            size="sm"
            disabled={items.length < limit}
            onClick={() => setPage(page + 1)}
          >
            {t('next')}
          </Button>
        </div>
      </div>

      {error && (
        <div className="text-xs text-destructive mt-2">
          {t('loadError')}
        </div>
      )}
    </div>
  );
}
