"use client";

import EvidenceApprovalModal from "@/components/modals/EvidenceApprovalModal";
import EvidenceUploadModal from "@/components/modals/EvidenceUploadModal";
import DynamicSectionRenderer from "@/components/dynamic/DynamicSectionRenderer";
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
import { useMemo, useState } from "react";
import useSWR from "swr";
import { useUiPageConfig, useWorkflowConfig } from "@/lib/dynamic-config";

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

// Helper function to get user role from localStorage
const getUserRole = (): string => {
  if (typeof window !== "undefined") {
    const user = localStorage.getItem("currentUser");
    if (user) {
      try {
        const userData = JSON.parse(user);
        return userData.role?.toLowerCase() || "";
      } catch {
        return "";
      }
    }
  }
  return "";
};

// Helper function to check if user can approve/reject evidence
const canApproveEvidence = (): boolean => {
  const role = getUserRole();
  return role === "admin" || role === "auditor";
};

export default function EvidenceListPage() {
  const params = useParams();
  const locale = params.locale as string;
  const t = useTranslations("evidenceList");

  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [isApprovalModalOpen, setIsApprovalModalOpen] = useState(false);
  const [selectedEvidence, setSelectedEvidence] = useState<{
    id: string;
    title: string;
  } | null>(null);
  const [approvalAction, setApprovalAction] = useState<"approve" | "reject">(
    "approve",
  );

  const [statusFilter, setStatusFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [search, setSearch] = useState("");
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
  if (statusFilter !== "all") queryParams.append("status", statusFilter);
  if (typeFilter !== "all") queryParams.append("evidence_type", typeFilter);
  queryParams.append("offset", String((page - 1) * limit));
  queryParams.append("limit", String(limit));

  const {
    data: evidence,
    isLoading,
    mutate,
  } = useSWR(`/api/v1/evidence?${queryParams.toString()}`, fetcher);
  const { data: workflowConfig } = useWorkflowConfig("evidence");
  const { data: uiConfig } = useUiPageConfig("evidence");

  const filteredItems = useMemo(() => {
    const items = evidence?.items || [];
    if (!search) return items;
    const term = search.toLowerCase();
    return items.filter(
      (item: any) =>
        item.title?.toLowerCase().includes(term) ||
        item.control_id?.toLowerCase().includes(term),
    );
  }, [evidence?.items, search]);

  const total = evidence?.total ?? filteredItems.length;

  // Check if current user can approve/reject evidence
  const userCanApprove = canApproveEvidence();

  // Handler for approve/reject actions
  const handleApprove = (evidenceId: string, title: string) => {
    setSelectedEvidence({ id: evidenceId, title });
    setApprovalAction("approve");
    setIsApprovalModalOpen(true);
  };

  const handleReject = (evidenceId: string, title: string) => {
    setSelectedEvidence({ id: evidenceId, title });
    setApprovalAction("reject");
    setIsApprovalModalOpen(true);
  };

  const validationVariant: Record<
    string,
    "success" | "warning" | "destructive" | "muted"
  > = {
    approved: "success",
    pending: "warning",
    rejected: "destructive",
  };

  const statusLabel = (value: string) => {
    const workflowLabel = workflowConfig?.states.find((state) => state.state_key === value)?.label;
    if (workflowLabel) return workflowLabel;
    return value;
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
          <h1 className="text-2xl font-semibold">{t("title")}</h1>
          <p className="text-sm text-muted-foreground">{t("description")}</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            {t("export")}
          </Button>
          <Button size="sm" onClick={() => setIsUploadModalOpen(true)}>
            {t("upload")}
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
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger>
              <SelectValue placeholder={t("status")} />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t("allStatuses")}</SelectItem>
              <SelectItem value="approved">{t("approved")}</SelectItem>
              <SelectItem value="pending">{t("pending")}</SelectItem>
              <SelectItem value="rejected">{t("rejected")}</SelectItem>
            </SelectContent>
          </Select>
          <Select value={typeFilter} onValueChange={setTypeFilter}>
            <SelectTrigger>
              <SelectValue placeholder={t("type")}></SelectValue>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">{t("allTypes")}</SelectItem>
              <SelectItem value="document">{t("document")}</SelectItem>
              <SelectItem value="screenshot">{t("screenshot")}</SelectItem>
              <SelectItem value="log">{t("log")}</SelectItem>
              <SelectItem value="certificate">{t("certificate")}</SelectItem>
              <SelectItem value="report">{t("report")}</SelectItem>
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
                    setVisibleColumns((prev) => ({
                      ...prev,
                      control: !prev.control,
                    }))
                  }
                >
                  {visibleColumns.control ? t("hide") : t("show")}{" "}
                  {t("control")}
                </DropdownMenuItem>
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
                      source: !prev.source,
                    }))
                  }
                >
                  {visibleColumns.source ? t("hide") : t("show")} {t("source")}
                </DropdownMenuItem>
                <DropdownMenuItem
                  onSelect={() =>
                    setVisibleColumns((prev) => ({
                      ...prev,
                      period: !prev.period,
                    }))
                  }
                >
                  {visibleColumns.period ? t("hide") : t("show")} {t("period")}
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
                <TableHead>{t("titleColumn")}</TableHead>
                {visibleColumns.control && (
                  <TableHead>{t("control")}</TableHead>
                )}
                {visibleColumns.type && <TableHead>{t("type")}</TableHead>}
                {visibleColumns.source && <TableHead>{t("source")}</TableHead>}
                {visibleColumns.period && <TableHead>{t("period")}</TableHead>}
                {visibleColumns.owner && <TableHead>{t("owner")}</TableHead>}
                <TableHead>{t("status")}</TableHead>
                <TableHead className="text-right">{t("actions")}</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredItems.length === 0 ? (
                <TableRow>
                  <TableCell
                    colSpan={8}
                    className="py-10 text-center text-muted-foreground"
                  >
                    {t("noResults")}
                  </TableCell>
                </TableRow>
              ) : (
                filteredItems.map((item: any) => (
                  <TableRow key={item.id}>
                    <TableCell>
                      <div className="font-semibold text-sm">{item.title}</div>
                      {item.description && (
                        <div className="text-xs text-muted-foreground line-clamp-1">
                          {item.description}
                        </div>
                      )}
                    </TableCell>
                    {visibleColumns.control && (
                      <TableCell>{item.control_id || "--"}</TableCell>
                    )}
                    {visibleColumns.type && (
                      <TableCell>{item.evidence_type || "--"}</TableCell>
                    )}
                    {visibleColumns.source && (
                      <TableCell>{item.source || t("notSet")}</TableCell>
                    )}
                    {visibleColumns.period && (
                      <TableCell>
                        {item.collection_date
                          ? new Date(item.collection_date).toLocaleDateString()
                          : "--"}
                      </TableCell>
                    )}
                    {visibleColumns.owner && (
                      <TableCell>{item.owner || t("unassigned")}</TableCell>
                    )}
                    <TableCell>
                      <Badge
                        variant={
                          validationVariant[item.validation_status || item.status] || "muted"
                        }
                      >
                        {item.validation_status
                          ? statusLabel(item.validation_status)
                          : item.status
                            ? statusLabel(item.status)
                            : t("notSet")}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            ⋯
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem asChild>
                            <Link href={`/${locale}/evidence/${item.id}`}>
                              {t("view")}
                            </Link>
                          </DropdownMenuItem>

                          {/* Approve/Reject actions - only for admin/auditor on pending evidence */}
                          {userCanApprove &&
                            item.validation_status === "pending" && (
                              <>
                                <DropdownMenuSeparator />
                                <DropdownMenuItem
                                  onClick={() =>
                                    handleApprove(
                                      item.evidence_id || item.id,
                                      item.title,
                                    )
                                  }
                                  className="text-green-600 font-semibold cursor-pointer"
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
                                      d="M5 13l4 4L19 7"
                                    />
                                  </svg>
                                  {t("approve") || "Approve"}
                                </DropdownMenuItem>
                                <DropdownMenuItem
                                  onClick={() =>
                                    handleReject(
                                      item.evidence_id || item.id,
                                      item.title,
                                    )
                                  }
                                  className="text-red-600 font-semibold cursor-pointer"
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
                                      d="M6 18L18 6M6 6l12 12"
                                    />
                                  </svg>
                                  {t("reject") || "Reject"}
                                </DropdownMenuItem>
                              </>
                            )}

                          <DropdownMenuSeparator />
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

      {uiConfig && (
        <div className="mt-6">
          <DynamicSectionRenderer
            config={uiConfig}
            renderSection={(section) => {
              if (section.section_key !== "custom_fields") {
                return null;
              }
              return (
                <div className="text-sm text-muted-foreground">
                  {t("description")}
                </div>
              );
            }}
          />
        </div>
      )}

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

      {/* Upload Evidence Modal */}
      <EvidenceUploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onSuccess={() => {
          mutate(); // Refresh the evidence list
          setPage(1); // Reset to first page
        }}
        locale={locale as "en" | "ar"}
      />

      {/* Evidence Approval Modal */}
      {selectedEvidence && (
        <EvidenceApprovalModal
          isOpen={isApprovalModalOpen}
          onClose={() => {
            setIsApprovalModalOpen(false);
            setSelectedEvidence(null);
          }}
          onSuccess={() => {
            mutate(); // Refresh the evidence list
          }}
          evidenceId={selectedEvidence.id}
          evidenceTitle={selectedEvidence.title}
          action={approvalAction}
          locale={locale as "en" | "ar"}
        />
      )}
    </div>
  );
}
