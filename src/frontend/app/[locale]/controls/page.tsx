'use client';

import { useTranslations } from 'next-intl';
import { useMemo, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import ControlEditModal from '@/components/modals/ControlEditModal';
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
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useEffect } from 'react';

export default function ControlsPage() {
  const t = useTranslations('controlsList');
  const params = useParams();
  const locale = params.locale as string;
  const [framework, setFramework] = useState<string>('all');
  const [status, setStatus] = useState<string>('all');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const limit = 50;
  const [controls, setControls] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, ecc: 0, ccc: 0, pdpl: 0 });

  // Edit Modal State
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedControl, setSelectedControl] = useState<any>(null);

  const fetchControls = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (framework !== 'all') params.append('framework', framework);
      if (status !== 'all') params.append('status', status);
      params.append('offset', String((page - 1) * limit));
      params.append('limit', String(limit));
      
      const response = await fetch(`http://localhost:8000/api/v1/controls?${params}`);
      const data = await response.json();
      setControls(data.items || []);
      setTotal(data.total || 0);
    } catch (error) {
      console.error('Failed to fetch controls:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchControls();
  }, [framework, status, page]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const [allRes, eccRes, cccRes, pdplRes] = await Promise.all([
          fetch('http://localhost:8000/api/v1/controls?limit=1'),
          fetch('http://localhost:8000/api/v1/controls?framework=ECC&limit=1'),
          fetch('http://localhost:8000/api/v1/controls?framework=CCC&limit=1'),
          fetch('http://localhost:8000/api/v1/controls?framework=PDPL&limit=1'),
        ]);
        const [all, ecc, ccc, pdpl] = await Promise.all([
          allRes.json(),
          eccRes.json(),
          cccRes.json(),
          pdplRes.json(),
        ]);
        setStats({
          total: all.total || 0,
          ecc: ecc.total || 0,
          ccc: ccc.total || 0,
          pdpl: pdpl.total || 0,
        });
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };
    
    fetchStats();
  }, []);

  
  const filteredItems = useMemo(() => {
    if (!search) return controls;
    const term = search.toLowerCase();
    return controls.filter((control: any) =>
      control.control_id?.toLowerCase().includes(term) ||
      control.title_en?.toLowerCase().includes(term) ||
      control.title_ar?.includes(search)
    );
  }, [controls, search]);

  if (loading && controls.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-foreground"></div>
      </div>
    );
  }

  const statusVariant: Record<string, 'success' | 'warning' | 'destructive' | 'default'> = {
    COMPLIANT: 'success',
    IN_PROGRESS: 'warning',
    NON_COMPLIANT: 'destructive',
    NOT_STARTED: 'default',
    compliant: 'success',
    in_progress: 'warning',
    non_compliant: 'destructive',
    not_started: 'default',
    active: 'success',
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

      {/* Statistics Dashboard */}
      <div className="grid grid-cols-1 gap-4 mb-6 md:grid-cols-4">
        <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-950 dark:to-blue-900">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Controls</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">{stats.total}</div>
            <p className="text-xs text-muted-foreground mt-1">All frameworks</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-950 dark:to-purple-900">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">ECC Controls</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">{stats.ecc}</div>
            <p className="text-xs text-muted-foreground mt-1">Essential Cybersecurity</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950 dark:to-green-900">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">CCC Controls</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600 dark:text-green-400">{stats.ccc}</div>
            <p className="text-xs text-muted-foreground mt-1">Cloud Cybersecurity</p>
          </CardContent>
        </Card>
        <Card className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950 dark:to-orange-900">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">PDPL Articles</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-orange-600 dark:text-orange-400">{stats.pdpl}</div>
            <p className="text-xs text-muted-foreground mt-1">Data Protection Law</p>
          </CardContent>
        </Card>
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
              <SelectItem value="COMPLIANT">Compliant</SelectItem>
              <SelectItem value="IN_PROGRESS">In Progress</SelectItem>
              <SelectItem value="NON_COMPLIANT">Non Compliant</SelectItem>
              <SelectItem value="NOT_STARTED">Not Started</SelectItem>
            </SelectContent>
          </Select>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>{t('controlId')}</TableHead>
                <TableHead>{t('titleColumn')}</TableHead>
                <TableHead>{t('framework')}</TableHead>
                <TableHead>{t('domain')}</TableHead>
                <TableHead>{t('status')}</TableHead>
                <TableHead>{t('maturity')}</TableHead>
                <TableHead className="text-right">{t('actions')}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredItems.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="py-10 text-center text-muted-foreground">
                    {loading ? 'Loading...' : t('noResults')}
                  </TableCell>
                </TableRow>
              ) : (
                filteredItems.map((control: any) => (
                  <TableRow key={control.control_id}>
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
                    <TableCell>
                      <Badge variant="outline">{control.framework}</Badge>
                    </TableCell>
                    <TableCell className="max-w-[200px] truncate">{control.domain}</TableCell>
                    <TableCell>
                      <Badge variant={statusVariant[control.status] || 'default'}>
                        {control.status?.replace('_', ' ')}
                      </Badge>
                    </TableCell>
                    <TableCell>{control.maturity_level ?? '--'}</TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">⋯</Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem asChild>
                            <Link href={`/${locale}/controls/${control.control_id}`}>View Details</Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => {
                              setSelectedControl(control);
                              setIsEditModalOpen(true);
                            }}
                          >
                            Edit Control
                          </DropdownMenuItem>
                          <DropdownMenuItem>View Evidence</DropdownMenuItem>
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
        <div>Showing {filteredItems.length} of {total} controls</div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" disabled={page === 1 || loading} onClick={() => setPage(page - 1)}>
            Previous
          </Button>
          <span>Page {page}</span>
          <Button
            variant="outline"
            size="sm"
            disabled={filteredItems.length < limit || loading}
            onClick={() => setPage(page + 1)}
          >
            Next
          </Button>
        </div>
      </div>

      {/* Control Edit Modal */}
      {selectedControl && (
        <ControlEditModal
          isOpen={isEditModalOpen}
          onClose={() => {
            setIsEditModalOpen(false);
            setSelectedControl(null);
          }}
          onSuccess={() => {
            fetchControls();
          }}
          locale={locale as 'en' | 'ar'}
          controlData={{
            control_id: selectedControl.control_id,
            framework: selectedControl.framework,
            domain: selectedControl.domain,
            title_en: selectedControl.title_en,
            title_ar: selectedControl.title_ar,
            description_en: selectedControl.description_en || '',
            description_ar: selectedControl.description_ar || '',
            status: selectedControl.status,
            maturity_level: selectedControl.maturity_level,
          }}
        />
      )}
    </div>
  );
}
