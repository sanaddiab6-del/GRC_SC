'use client';

import { useTranslations } from 'next-intl';
import useSWR from 'swr';
import { useMemo, useState } from 'react';
import apiClient from '@/lib/api-client';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
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

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export default function ControlsPage() {
  const t = useTranslations('controlsList');
  const params = useParams();
  const locale = params.locale as string;
  const [framework, setFramework] = useState<string>('all');
  const [status, setStatus] = useState<string>('all');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const limit = 20;
  const [visibleColumns, setVisibleColumns] = useState({
    framework: true,
    domain: true,
    maturity: true,
    updated: true,
    owner: true,
  });
  const [selected, setSelected] = useState<Record<string, boolean>>({});

  const queryParams = new URLSearchParams();
  if (framework !== 'all') queryParams.append('framework', framework);
  if (status !== 'all') queryParams.append('status', status);
  queryParams.append('offset', String((page - 1) * limit));
  queryParams.append('limit', String(limit));

  const { data, error, isLoading } = useSWR(
    `/api/v1/controls?${queryParams.toString()}`,
    fetcher
  );

  const items = data?.items || [];
  const filteredItems = useMemo(() => {
    if (!search) return items;
    const term = search.toLowerCase();
    return items.filter((control: any) =>
      control.control_id?.toLowerCase().includes(term) ||
      control.title_en?.toLowerCase().includes(term) ||
      control.title_ar?.includes(search)
    );
  }, [items, search]);

  const total = data?.total ?? filteredItems.length;

  const handleToggleColumn = (key: keyof typeof visibleColumns) => {
    setVisibleColumns((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleToggleAll = (checked: boolean) => {
    const next: Record<string, boolean> = {};
    filteredItems.forEach((control: any) => {
      next[control.control_id] = checked;
    });
    setSelected(next);
  };

  const handleToggleRow = (id: string) => {
    setSelected((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-foreground"></div>
      </div>
    );
  }

  const statusVariant: Record<string, 'success' | 'warning' | 'destructive' | 'muted'> = {
    compliant: 'success',
    in_progress: 'warning',
    non_compliant: 'destructive',
    not_started: 'muted',
  };

  return (
    <div className="min-h-screen bg-background px-6 py-6">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold">{t('title')}</h1>
          <p className="text-sm text-muted-foreground">{t('description')}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            {t('export')}
          </Button>
          <Button size="sm" asChild>
            <Link href={`/${locale}/controls/new`}>{t('create')}</Link>
          </Button>
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
          <Select value={framework} onValueChange={setFramework}>
            <SelectTrigger>
              <SelectValue placeholder={t('framework')} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t('allFrameworks')}</SelectItem>
              <SelectItem value="ECC">ECC</SelectItem>
              <SelectItem value="CCC">CCC</SelectItem>
              <SelectItem value="PDPL">PDPL</SelectItem>
            </SelectContent>
          </Select>
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger>
              <SelectValue placeholder={t('status')} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t('allStatuses')}</SelectItem>
              <SelectItem value="compliant">{t('compliant')}</SelectItem>
              <SelectItem value="in_progress">{t('inProgress')}</SelectItem>
              <SelectItem value="non_compliant">{t('nonCompliant')}</SelectItem>
              <SelectItem value="not_started">{t('notStarted')}</SelectItem>
            </SelectContent>
          </Select>
          <div className="flex items-center justify-end">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  {t('columns')}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>{t('columns')}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onSelect={() => handleToggleColumn('framework')}>
                  {visibleColumns.framework ? t('hide') : t('show')} {t('framework')}
                </DropdownMenuItem>
                <DropdownMenuItem onSelect={() => handleToggleColumn('domain')}>
                  {visibleColumns.domain ? t('hide') : t('show')} {t('domain')}
                </DropdownMenuItem>
                <DropdownMenuItem onSelect={() => handleToggleColumn('owner')}>
                  {visibleColumns.owner ? t('hide') : t('show')} {t('owner')}
                </DropdownMenuItem>
                <DropdownMenuItem onSelect={() => handleToggleColumn('maturity')}>
                  {visibleColumns.maturity ? t('hide') : t('show')} {t('maturity')}
                </DropdownMenuItem>
                <DropdownMenuItem onSelect={() => handleToggleColumn('updated')}>
                  {visibleColumns.updated ? t('hide') : t('show')} {t('updated')}
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
                <TableHead className="w-[40px]">
                  <input
                    type="checkbox"
                    aria-label={t('selectAll')}
                    checked={filteredItems.length > 0 && filteredItems.every((c: any) => selected[c.control_id])}
                    onChange={(e) => handleToggleAll(e.target.checked)}
                  />
                </TableHead>
                <TableHead>{t('controlId')}</TableHead>
                <TableHead>{t('titleColumn')}</TableHead>
                {visibleColumns.framework && <TableHead>{t('framework')}</TableHead>}
                {visibleColumns.domain && <TableHead>{t('domain')}</TableHead>}
                {visibleColumns.owner && <TableHead>{t('owner')}</TableHead>}
                <TableHead>{t('status')}</TableHead>
                {visibleColumns.maturity && <TableHead>{t('maturity')}</TableHead>}
                {visibleColumns.updated && <TableHead>{t('updated')}</TableHead>}
                <TableHead className="text-right">{t('actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredItems.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={10} className="py-10 text-center text-muted-foreground">
                    {t('noResults')}
                  </TableCell>
                </TableRow>
              ) : (
                filteredItems.map((control: any) => (
                  <TableRow key={control.control_id}>
                    <TableCell>
                      <input
                        type="checkbox"
                        aria-label={control.control_id}
                        checked={!!selected[control.control_id]}
                        onChange={() => handleToggleRow(control.control_id)}
                      />
                    </TableCell>
                    <TableCell className="font-mono text-xs font-semibold">
                      {control.control_id}
                    </TableCell>
                    <TableCell>
                      <div className="font-semibold text-sm">{control.title_en}</div>
                      {control.title_ar && (
                        <div className="text-xs text-muted-foreground" dir="rtl">
                          {control.title_ar}
                        </div>
                      )}
                    </TableCell>
                    {visibleColumns.framework && <TableCell>{control.framework}</TableCell>}
                    {visibleColumns.domain && (
                      <TableCell className="max-w-[200px] truncate">{control.domain}</TableCell>
                    )}
                    {visibleColumns.owner && <TableCell>{t('unassigned')}</TableCell>}
                    <TableCell>
                      <Badge variant={statusVariant[control.status] || 'muted'}>
                        {control.status?.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    {visibleColumns.maturity && <TableCell>{control.maturity_level ?? '--'}</TableCell>}
                    {visibleColumns.updated && (
                      <TableCell>
                        {control.updated_at ? new Date(control.updated_at).toLocaleDateString() : '--'}
                      </TableCell>
                    )}
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">⋯</Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem asChild>
                            <Link href={`/${locale}/controls/${control.control_id}`}>{t('view')}</Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem>{t('edit')}</DropdownMenuItem>
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
        <div>{t('results', { count: filteredItems.length, total })}</div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(page - 1)}>
            {t('previous')}
          </Button>
          <span>{t('page', { page })}</span>
          <Button
            variant="outline"
            size="sm"
            disabled={filteredItems.length < limit}
            onClick={() => setPage(page + 1)}
          >
            {t('next')}
          </Button>
        </div>
      </div>
    </div>
  );
}
