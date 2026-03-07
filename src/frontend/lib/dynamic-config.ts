import useSWR from "swr";
import apiClient from "@/lib/api-client";

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

export interface CustomField {
  id: string;
  entity_type: string;
  field_key: string;
  field_label: string;
  field_type: string;
  required: boolean;
  options_json?: Record<string, any> | null;
  organization_id?: number | null;
  created_at: string;
  value?: any;
}

export interface WorkflowState {
  id: string;
  entity_type: string;
  state_key: string;
  label: string;
  order_index: number;
  organization_id?: number | null;
}

export interface WorkflowTransition {
  id: string;
  from_state: string;
  to_state: string;
  action_label: string;
  allowed_roles?: string[] | null;
}

export interface WorkflowConfig {
  states: WorkflowState[];
  transitions: WorkflowTransition[];
}

export interface DashboardWidget {
  id: string;
  widget_key: string;
  title: string;
  component_type: string;
  data_source?: string | null;
  config_json?: Record<string, any> | null;
}

export interface DashboardLayout {
  id: string;
  organization_id?: number | null;
  widget_id: string;
  position?: Record<string, any> | null;
  size?: Record<string, any> | null;
  widget?: DashboardWidget;
}

export interface UiSection {
  id: string;
  section_key: string;
  title: string;
  order_index: number;
}

export interface UiFieldPlacement {
  id: string;
  field_key: string;
  order_index: number;
}

export interface UiPageConfig {
  page: { id: string; page_key: string; title: string };
  sections: UiSection[];
  placements: UiFieldPlacement[];
}

export interface ReportTemplate {
  id: string;
  template_key: string;
  name: string;
  entity_type?: string | null;
  query_config?: Record<string, any> | null;
  export_format: string;
  created_at: string;
}

export const useCustomFields = (
  entityType: string,
  entityId?: string,
  organizationId?: number
) => {
  const params = new URLSearchParams({ entity_type: entityType });
  if (organizationId !== undefined) {
    params.append("organization_id", String(organizationId));
  }

  const { data: fields, error: fieldsError, mutate: mutateFields } = useSWR<CustomField[]>(
    `/api/v1/config/custom-fields?${params.toString()}`,
    fetcher
  );

  const valueParams = new URLSearchParams({ entity_type: entityType, entity_id: entityId || "" });
  if (organizationId !== undefined) {
    valueParams.append("organization_id", String(organizationId));
  }

  const shouldFetchValues = Boolean(entityId);
  const { data: values, error: valuesError, mutate: mutateValues } = useSWR<CustomField[]>(
    shouldFetchValues ? `/api/v1/config/custom-fields/values?${valueParams.toString()}` : null,
    fetcher
  );

  return {
    fields: values || fields || [],
    error: fieldsError || valuesError,
    isLoading: !fields && !fieldsError,
    mutate: async () => {
      await mutateFields();
      if (shouldFetchValues) {
        await mutateValues();
      }
    },
  };
};

export const saveCustomFieldValues = async (
  entityType: string,
  entityId: string,
  values: { field_id: string; value: any }[]
) => {
  return apiClient.put("/api/v1/config/custom-fields/values", {
    entity_type: entityType,
    entity_id: entityId,
    values,
  });
};

export const useWorkflowConfig = (entityType: string, organizationId?: number) => {
  const params = new URLSearchParams({ entity_type: entityType });
  if (organizationId !== undefined) {
    params.append("organization_id", String(organizationId));
  }
  return useSWR<WorkflowConfig>(`/api/v1/config/workflows?${params.toString()}`, fetcher);
};

export const applyWorkflowTransition = async (entityType: string, entityId: string, toStateKey: string) => {
  return apiClient.post("/api/v1/config/workflows/apply", {
    entity_type: entityType,
    entity_id: entityId,
    to_state_key: toStateKey,
  });
};

export const useDashboardLayout = (organizationId?: number) => {
  const params = new URLSearchParams();
  if (organizationId !== undefined) {
    params.append("organization_id", String(organizationId));
  }
  const url = params.toString() ? `/api/v1/config/dashboard/layouts?${params.toString()}` : "/api/v1/config/dashboard/layouts";
  return useSWR<DashboardLayout[]>(url, fetcher);
};

export const useUiPageConfig = (pageKey: string) => {
  return useSWR<UiPageConfig>(`/api/v1/config/ui/pages/${pageKey}`, fetcher, {
    shouldRetryOnError: false,
  });
};

export const useReportTemplates = () => {
  return useSWR<ReportTemplate[]>("/api/v1/report-templates", fetcher);
};
