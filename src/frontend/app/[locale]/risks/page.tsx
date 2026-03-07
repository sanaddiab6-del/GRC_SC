"use client";

import RiskModal from "@/components/modals/RiskModal";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import apiClient from "@/lib/api-client";
import { useTranslations } from "next-intl";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import useSWR from "swr";
import { useWorkflowConfig } from "@/lib/dynamic-config";

interface RiskItem {
  risk_id: string;
  risk_number?: string;
  category?: string;
  status: string;
  title_en: string;
  title_ar: string;
  description_en?: string;
  description_ar?: string;
  likelihood: number;
  impact: number;
  inherent_risk_score?: number;
  inherent_risk_level?: string;
  residual_risk_score?: number;
  residual_risk_level?: string;
  risk_owner?: string;
  next_review_date?: string;
}

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export default function RiskManagementPage() {
  const params = useParams();
  const locale = (params?.locale as "ar" | "en") || "en";
  const t = useTranslations("riskList");

  const [search, setSearch] = useState("");
  const [severity, setSeverity] = useState("all");
  const [status, setStatus] = useState("all");
  const [visibleColumns, setVisibleColumns] = useState({
    type: true,
    likelihood: true,
    impact: true,
    owner: true,
  });

  const [page, setPage] = useState(1);
  const limit = 20;

  // Risk Modal States
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedRisk, setSelectedRisk] = useState<RiskItem | null>(null);

  const queryParams = new URLSearchParams();
  if (status !== "all") queryParams.append("status", status);
  queryParams.append("skip", String((page - 1) * limit));
  queryParams.append("limit", String(limit));

  const { data, error, isLoading, mutate } = useSWR(
    `/api/v1/risks?${queryParams.toString()}`,
    fetcher,
  );
  const { data: workflowConfig } = useWorkflowConfig("risk");

  useEffect(() => {
    setPage(1);
  }, [search, severity, status]);

  const filteredItems = useMemo(() => {
    const risks: RiskItem[] = Array.isArray(data) ? data : [];
    return risks.filter((risk) => {
      const riskLevel =
        risk.residual_risk_level || risk.inherent_risk_level || "";
      const matchesSearch =
        !search ||
        risk.risk_number?.toLowerCase().includes(search.toLowerCase()) ||
        risk.risk_id.toLowerCase().includes(search.toLowerCase()) ||
        risk.title_en?.toLowerCase().includes(search.toLowerCase()) ||
        (risk.title_ar && risk.title_ar.includes(search));
      const matchesSeverity = severity === "all" || riskLevel === severity;
      const matchesStatus = status === "all" || risk.status === status;
      return matchesSearch && matchesSeverity && matchesStatus;
    });
  }, [data, search, severity, status]);

  const severityVariant: Record<
    string,
    "success" | "warning" | "destructive" | "muted"
  > = {
    critical: "destructive",
    high: "warning",
    medium: "warning",
    low: "success",
  };

  const statusVariant: Record<
    string,
    "success" | "warning" | "destructive" | "muted"
  > = {
    identified: "muted",
    assessed: "warning",
    treated: "warning",
    accepted: "muted",
    transferred: "warning",
    mitigated: "warning",
    closed: "success",
  };

  const severityLabel = (value: string) => {
    if (value === "critical") return t("critical");
    if (value === "high") return t("high");
    if (value === "medium") return t("medium");
    if (value === "low") return t("low");
    return value;
  };

  const statusLabel = (value: string) => {
    const workflowLabel = workflowConfig?.states.find((state) => state.state_key === value)?.label;
    if (workflowLabel) return workflowLabel;
    if (value === "identified") return t("identified");
    if (value === "assessed") return t("assessed");
    if (value === "treated") return t("treated");
    if (value === "accepted") return t("accepted");
    if (value === "transferred") return t("transferred");
    if (value === "mitigated") return t("mitigated");
    if (value === "closed") return t("closed");
    return value;
  };

  const total = filteredItems.length;

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
          <h1 className="text-2xl font-semibold">{t("title")}</h1>
          <p className="text-sm text-muted-foreground">{t("description")}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            {t("export")}
          </Button>
          <Button size="sm" onClick={() => setIsCreateModalOpen(true)}>
            {t("create")}
          </Button>
        </div>
      </div>

      <Card className="mb-6">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg">{t("filters")}</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder={t("searchPlaceholder")}
          />
          <Select value={severity} onValueChange={setSeverity}>
            <SelectTrigger>
              <SelectValue placeholder={t("severity")} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t("allSeverities")}</SelectItem>
              <SelectItem value="critical">{t("critical")}</SelectItem>
              <SelectItem value="high">{t("high")}</SelectItem>
              <SelectItem value="medium">{t("medium")}</SelectItem>
              <SelectItem value="low">{t("low")}</SelectItem>
            </SelectContent>
          </Select>
          <Select value={status} onValueChange={setStatus}>
            <SelectTrigger>
              <SelectValue placeholder={t("status")} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t("allStatuses")}</SelectItem>
              <SelectItem value="identified">{t("identified")}</SelectItem>
              <SelectItem value="assessed">{t("assessed")}</SelectItem>
              <SelectItem value="treated">{t("treated")}</SelectItem>
              <SelectItem value="accepted">{t("accepted")}</SelectItem>
              <SelectItem value="transferred">{t("transferred")}</SelectItem>
              <SelectItem value="mitigated">{t("mitigated")}</SelectItem>
              <SelectItem value="closed">{t("closed")}</SelectItem>
            </SelectContent>
          </Select>
          <div className="flex items-center justify-end">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm">
                  {t("columns")}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>{t("columns")}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onSelect={() =>
                    setVisibleColumns((prev) => ({ ...prev, type: !prev.type }))
                  }
                >
                  {visibleColumns.type ? t("hide") : t("show")} {t("type")}
                </DropdownMenuItem>
                <DropdownMenuItem
                  onSelect={() =>
                    setVisibleColumns((prev) => ({
                      ...prev,
                      likelihood: !prev.likelihood,
                    }))
                  }
                >
                  {visibleColumns.likelihood ? t("hide") : t("show")}{" "}
                  {t("likelihood")}
                </DropdownMenuItem>
                <DropdownMenuItem
                  onSelect={() =>
                    setVisibleColumns((prev) => ({
                      ...prev,
                      impact: !prev.impact,
                    }))
                  }
                >
                  {visibleColumns.impact ? t("hide") : t("show")} {t("impact")}
                </DropdownMenuItem>
                <DropdownMenuItem
                  onSelect={() =>
                    setVisibleColumns((prev) => ({
                      ...prev,
                      owner: !prev.owner,
                    }))
                  }
                >
                  {visibleColumns.owner ? t("hide") : t("show")} {t("owner")}
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
                <TableHead>{t("riskId")}</TableHead>
                <TableHead>{t("titleColumn")}</TableHead>
                {visibleColumns.type && <TableHead>{t("type")}</TableHead>}
                {visibleColumns.likelihood && (
                  <TableHead>{t("likelihood")}</TableHead>
                )}
                {visibleColumns.impact && <TableHead>{t("impact")}</TableHead>}
                <TableHead>{t("score")}</TableHead>
                <TableHead>{t("severity")}</TableHead>
                <TableHead>{t("status")}</TableHead>
                {visibleColumns.owner && <TableHead>{t("owner")}</TableHead>}
                <TableHead className="text-right">{t("actions")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredItems.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={10}
                    className="py-10 text-center text-muted-foreground"
                  >
                    {t("noResults")}
                  </TableCell>
                </TableRow>
              ) : (
                filteredItems.map((risk) => (
                  <TableRow key={risk.risk_id}>
                    <TableCell>
                      <Link
                        href={`/${locale}/risks/${risk.risk_id}`}
                        className="font-mono text-xs font-semibold hover:underline"
                      >
                        {risk.risk_number || risk.risk_id}
                      </Link>
                    </TableCell>
                    <TableCell>
                      <div className="font-semibold text-sm">
                        {locale === "ar" ? risk.title_ar : risk.title_en}
                      </div>
                    </TableCell>
                    {visibleColumns.type && (
                      <TableCell>{risk.category || "--"}</TableCell>
                    )}
                    {visibleColumns.likelihood && (
                      <TableCell>{risk.likelihood ?? "--"}</TableCell>
                    )}
                    {visibleColumns.impact && (
                      <TableCell>{risk.impact ?? "--"}</TableCell>
                    )}
                    <TableCell>
                      {risk.residual_risk_score ??
                        risk.inherent_risk_score ??
                        "--"}
                    </TableCell>
                    <TableCell>
                      <Badge
                        variant={
                          severityVariant[
                            risk.residual_risk_level ||
                              risk.inherent_risk_level ||
                              ""
                          ] || "muted"
                        }
                      >
                        {severityLabel(
                          risk.residual_risk_level ||
                            risk.inherent_risk_level ||
                            "",
                        )}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={statusVariant[risk.status] || "muted"}>
                        {statusLabel(risk.status)}
                      </Badge>
                    </TableCell>
                    {visibleColumns.owner && (
                      <TableCell>{risk.risk_owner || "--"}</TableCell>
                    )}
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            ⋯
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem asChild>
                            <Link href={`/${locale}/risks/${risk.risk_id}`}>
                              {t("view")}
                            </Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => {
                              setSelectedRisk(risk);
                              setIsEditModalOpen(true);
                            }}
                          >
                            {t("edit")}
                          </DropdownMenuItem>
                          <DropdownMenuItem>{t("auditTrail")}</DropdownMenuItem>
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
        <div>{t("results", { count: filteredItems.length, total })}</div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page === 1}
            onClick={() => setPage(page - 1)}
          >
            {t("previous")}
          </Button>
          <span>{t("page", { page })}</span>
          <Button
            variant="outline"
            size="sm"
            disabled={filteredItems.length < limit}
            onClick={() => setPage(page + 1)}
          >
            {t("next")}
          </Button>
        </div>
      </div>

      {error && (
        <div className="text-xs text-destructive mt-2">{t("loadError")}</div>
      )}

      {/* Risk Create Modal */}
      <RiskModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSuccess={() => {
          mutate();
          setPage(1);
        }}
        locale={locale}
        mode="create"
      />

      {/* Risk Edit Modal */}
      {selectedRisk && (
        <RiskModal
          isOpen={isEditModalOpen}
          onClose={() => {
            setIsEditModalOpen(false);
            setSelectedRisk(null);
          }}
          onSuccess={() => mutate()}
          locale={locale}
          mode="edit"
          riskData={{
            risk_id: selectedRisk.risk_id,
            category: selectedRisk.category || "",
            title_en: selectedRisk.title_en,
            title_ar: selectedRisk.title_ar,
            description_en: selectedRisk.description_en || "",
            description_ar: selectedRisk.description_ar || "",
            likelihood: selectedRisk.likelihood,
            impact: selectedRisk.impact,
            risk_owner: selectedRisk.risk_owner || "",
          }}
        />
      )}
    </div>
  );
}
