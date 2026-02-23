'use client';

import { useTranslations } from 'next-intl';
import useSWR from 'swr';
import apiClient from '@/lib/api-client';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { useMemo, useState } from 'react';
import { usePermission } from '@/lib/role-guard';
  const canApprove = usePermission('approve_evidence');
  const canReject = usePermission('approve_evidence');
  const canAssign = usePermission('manage_users');
  const canArchive = usePermission('edit_control');
  const canDelete = usePermission('delete_control');

  const [selected, setSelected] = useState<string[]>([]);
  const [selectAll, setSelectAll] = useState(false);
  const [bulkLoading, setBulkLoading] = useState(false);
  const [assignOwner, setAssignOwner] = useState('');
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { PermissionGuard } from '@/components/PermissionGuard';
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

export default function EvidenceListPage() {
  const params = useParams();
  const locale = params.locale as string;
  const t = useTranslations('evidenceList');

  const [statusFilter, setStatusFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const limit = 20;
  const [visibleColumns, setVisibleColumns] = useState({
    control: true,
    type: true,
    source: true,
    period: true,
    owner: true,
  });

  const queryParams = new URLSearchParams();
  if (statusFilter !== 'all') queryParams.append('status', statusFilter);
  if (typeFilter !== 'all') queryParams.append('evidence_type', typeFilter);
  queryParams.append('offset', String((page - 1) * limit));
  queryParams.append('limit', String(limit));

  const { data: evidence, isLoading } = useSWR(
    `/api/v1/evidence?${queryParams.toString()}`,
    fetcher
  );

  const items = evidence?.items || [];
  const filteredItems = useMemo(() => {
    if (!search) return items;
    const term = search.toLowerCase();
    return items.filter((item: any) =>
      item.title?.toLowerCase().includes(term) ||
      item.control_id?.toLowerCase().includes(term)
    );
  }, [items, search]);

  // Handle select all
  const handleSelectAll = () => {
    if (selectAll) {
      setSelected([]);
      setSelectAll(false);
    } else {
      setSelected(filteredItems.map((item: any) => item.id));
      setSelectAll(true);
    }
  };

  const handleSelect = (id: string) => {
    setSelected((prev) => prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]);
  };

  // Bulk actions
  const handleBulkAction = async (action: string) => {
    setBulkLoading(true);
    try {
      if (action === 'assign_owner') {
        await Promise.all(selected.map(id => apiClient.patch(`/api/v1/evidence/${id}`, { owner: assignOwner })));
      } else {
        await Promise.all(selected.map(id => apiClient.patch(`/api/v1/evidence/${id}`, { status: action })));
      }
      setSelected([]);
      setSelectAll(false);
      setAssignOwner('');
    } finally {
      setBulkLoading(false);
    }
  };

  const total = evidence?.total ?? filteredItems.length;

  const validationVariant: Record<string, 'success' | 'warning' | 'destructive' | 'muted'> = {
    approved: 'success',
    pending: 'warning',
    rejected: 'destructive',
  };

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
          <PermissionGuard action="generate_report">
            <Button variant="outline" size="sm">
              {t('export')}
            </Button>
          </PermissionGuard>
          <PermissionGuard action="approve_evidence">
            <Button size="sm" asChild>
              <Link href={`/${locale}/evidence/upload`}>{t('upload')}</Link>
            </Button>
          </PermissionGuard>
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
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger>
              <SelectValue placeholder={t('status')} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t('allStatuses')}</SelectItem>
              <SelectItem value="approved">{t('approved')}</SelectItem>
              <SelectItem value="pending">{t('pending')}</SelectItem>
              <SelectItem value="rejected">{t('rejected')}</SelectItem>
            </SelectContent>
          </Select>
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger>
              <SelectValue placeholder={t('type')}></SelectValue>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t('allTypes')}</SelectItem>
              <SelectItem value="document">{t('document')}</SelectItem>
              <SelectItem value="screenshot">{t('screenshot')}</SelectItem>
              <SelectItem value="log">{t('log')}</SelectItem>
              <SelectItem value="certificate">{t('certificate')}</SelectItem>
              <SelectItem value="report">{t('report')}</SelectItem>
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
                <DropdownMenuItem onSelect={() => setVisibleColumns((prev) => ({ ...prev, control: !prev.control }))}>
                  {visibleColumns.control ? t('hide') : t('show')} {t('control')}
                </DropdownMenuItem>
                <DropdownMenuItem onSelect={() => setVisibleColumns((prev) => ({ ...prev, type: !prev.type }))}>
                  {visibleColumns.type ? t('hide') : t('show')} {t('type')}
                </DropdownMenuItem>
                <DropdownMenuItem onSelect={() => setVisibleColumns((prev) => ({ ...prev, source: !prev.source }))}>
                  {visibleColumns.source ? t('hide') : t('show')} {t('source')}
                </DropdownMenuItem>
                <DropdownMenuItem onSelect={() => setVisibleColumns((prev) => ({ ...prev, period: !prev.period }))}>
                  {visibleColumns.period ? t('hide') : t('show')} {t('period')}
                </DropdownMenuItem>
                <DropdownMenuItem onSelect={() => setVisibleColumns((prev) => ({ ...prev, owner: !prev.owner }))}>
                  {visibleColumns.owner ? t('hide') : t('show')} {t('owner')}
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
                <TableHead>
                  <input
                    type="checkbox"
                    checked={selectAll}
                    onChange={handleSelectAll}
                    aria-label="Select all"
                  />
                </TableHead>
                <TableHead>{t('titleColumn')}</TableHead>
                {visibleColumns.control && <TableHead>{t('control')}</TableHead>}
                {visibleColumns.type && <TableHead>{t('type')}</TableHead>}
                {visibleColumns.source && <TableHead>{t('source')}</TableHead>}
                {visibleColumns.period && <TableHead>{t('period')}</TableHead>}
                {visibleColumns.owner && <TableHead>{t('owner')}</TableHead>}
                <TableHead>{t('status')}</TableHead>
                <TableHead className="text-right">{t('actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredItems.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="py-10 text-center text-muted-foreground">
                    {t('noResults')}
                  </TableCell>
                </TableRow>
              ) : (
                filteredItems.map((item: any) => (
                  <TableRow key={item.id} className={selected.includes(item.id) ? 'bg-blue-50' : ''}>
                    <TableCell>
                      <input
                        type="checkbox"
                        checked={selected.includes(item.id)}
                        onChange={() => handleSelect(item.id)}
                        aria-label="Select row"
                      />
                    </TableCell>
                    <TableCell>
                      <div className="font-semibold text-sm">{item.title}</div>
                      {item.description && (
                        <div className="text-xs text-muted-foreground line-clamp-1">
                          {item.description}
                        </div>
                      )}
                    </TableCell>
                    {visibleColumns.control && <TableCell>{item.control_id || '--'}</TableCell>}
                    {visibleColumns.type && <TableCell>{item.evidence_type || '--'}</TableCell>}
                    {visibleColumns.source && <TableCell>{item.source || t('notSet')}</TableCell>}
                    {visibleColumns.period && (
                      <TableCell>
                        {item.collection_date
                          ? new Date(item.collection_date).toLocaleDateString()
                          : '--'}
                      </TableCell>
                    )}
                    {visibleColumns.owner && <TableCell>{item.owner || t('unassigned')}</TableCell>}
                    <TableCell>
                      <Badge variant={validationVariant[item.validation_status] || 'muted'}>
                        {item.validation_status || t('notSet')}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">⋯</Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem asChild>
                            <Link href={`/${locale}/evidence/${item.id}`}>{t('view')}</Link>
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

      {/* Bulk action bar */}
      {selected.length > 0 && (
        <div className="fixed bottom-0 left-0 w-full bg-white border-t border-gray-200 shadow-lg z-50 p-4 flex items-center gap-4">
          <span className="font-semibold">{selected.length} selected</span>
          {canApprove && <Button size="sm" disabled={bulkLoading} onClick={() => handleBulkAction('approved')}>Approve</Button>}
          {canReject && <Button size="sm" disabled={bulkLoading} onClick={() => handleBulkAction('rejected')}>Reject</Button>}
          {canAssign && (
            <>
              <Input
                placeholder="Assign owner..."
                value={assignOwner}
                onChange={e => setAssignOwner(e.target.value)}
                className="w-32"
                disabled={bulkLoading}
              />
              <Button size="sm" disabled={bulkLoading || !assignOwner} onClick={() => handleBulkAction('assign_owner')}>Assign Owner</Button>
            </>
          )}
          {canArchive && <Button size="sm" disabled={bulkLoading} onClick={() => handleBulkAction('archived')}>Archive</Button>}
          {canDelete && <Button size="sm" disabled={bulkLoading} onClick={() => handleBulkAction('deleted')}>Delete</Button>}
          {bulkLoading && <span className="ml-4 animate-spin h-5 w-5 border-b-2 border-blue-500 rounded-full"></span>}
        </div>
      )}

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
