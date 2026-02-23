
import { useState, useMemo } from "react";
import useSWR from "swr";
import { PermissionGuard } from "@/components/PermissionGuard";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
// Optionally import a DateRangePicker if available in your UI kit
// import { DateRangePicker } from "@/components/ui/date-range-picker";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export default function AuditLogViewer() {
  // Filters
  const [user, setUser] = useState("");
  const [module, setModule] = useState("");
  const [action, setAction] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [page, setPage] = useState(1);
  const limit = 20;

  const queryParams = useMemo(() => {
    const params = new URLSearchParams();
    if (user) params.append("user", user);
    if (module) params.append("module", module);
    if (action) params.append("action", action);
    if (dateFrom) params.append("from", dateFrom);
    if (dateTo) params.append("to", dateTo);
    params.append("offset", String((page - 1) * limit));
    params.append("limit", String(limit));
    return params.toString();
  }, [user, module, action, dateFrom, dateTo, page]);

  const { data, isLoading } = useSWR(`/api/v1/audit-logs?${queryParams}`, fetcher);
  const logs = data?.items || [];
  const total = data?.total || 0;

  // CSV Export
  const handleExport = () => {
    const csvRows = [
      ["Timestamp", "User", "Module", "Action", "Details"],
      ...logs.map((log: any) => [
        log.timestamp,
        log.user,
        log.module,
        log.action,
        JSON.stringify(log.details || "")
      ])
    ];
    const csvContent = csvRows.map((row) => row.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(",")).join("\n");
    const blob = new Blob([csvContent], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "audit-logs.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <PermissionGuard action="manage_users">
      <div className="min-h-screen bg-background px-6 py-6">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-semibold">Audit Logs</h1>
            <p className="text-sm text-muted-foreground">View all system audit logs.</p>
          </div>
          <Button variant="outline" size="sm" onClick={handleExport} disabled={logs.length === 0}>
            Export CSV
          </Button>
        </div>
        <Card className="mb-6">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg">Filters</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-1 gap-4 md:grid-cols-5">
            <Input value={user} onChange={e => setUser(e.target.value)} placeholder="User" />
            <Input value={module} onChange={e => setModule(e.target.value)} placeholder="Module" />
            <Input value={action} onChange={e => setAction(e.target.value)} placeholder="Action" />
            <Input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} placeholder="From" />
            <Input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} placeholder="To" />
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>User</TableHead>
                  <TableHead>Module</TableHead>
                  <TableHead>Action</TableHead>
                  <TableHead>Details</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={5} className="py-10 text-center text-muted-foreground">
                      Loading...
                    </TableCell>
                  </TableRow>
                ) : logs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="py-10 text-center text-muted-foreground">
                      No logs found.
                    </TableCell>
                  </TableRow>
                ) : (
                  logs.map((log: any) => (
                    <TableRow key={log.id}>
                      <TableCell>{log.timestamp}</TableCell>
                      <TableCell>{log.user}</TableCell>
                      <TableCell>{log.module}</TableCell>
                      <TableCell>{log.action}</TableCell>
                      <TableCell><pre className="whitespace-pre-wrap text-xs">{JSON.stringify(log.details, null, 2)}</pre></TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
        <div className="mt-4 flex items-center justify-between text-xs text-muted-foreground">
          <div>{`${logs.length} of ${total}`}</div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" disabled={page === 1} onClick={() => setPage(page - 1)}>
              Previous
            </Button>
            <span>{`Page ${page}`}</span>
            <Button
              variant="outline"
              size="sm"
              disabled={logs.length < limit}
              onClick={() => setPage(page + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      </div>
    </PermissionGuard>
  );
}
