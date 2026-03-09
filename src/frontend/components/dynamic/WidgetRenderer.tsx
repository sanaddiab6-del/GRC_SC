"use client";

import dynamic from "next/dynamic";
import { DashboardWidget } from "@/lib/dynamic-config";

const ComplianceGauge = dynamic(() => import("@/components/dashboard/ComplianceGauge").then(m => ({ default: m.ComplianceGauge })), { ssr: false });
const ComplianceTrendChart = dynamic(() => import("@/components/dashboard/ComplianceTrendChart").then(m => ({ default: m.ComplianceTrendChart })), { ssr: false });
const ActivityTimeline = dynamic(() => import("@/components/dashboard/ActivityTimeline").then(m => ({ default: m.ActivityTimeline })), { ssr: false });
const RiskHeatMap = dynamic(() => import("@/components/dashboard/RiskHeatMap").then(m => ({ default: m.RiskHeatMap })), { ssr: false });
const TaskWidget = dynamic(() => import("@/components/dashboard/TaskWidget").then(m => ({ default: m.TaskWidget })), { ssr: false });
const SecurityIncidentFeed = dynamic(() => import("@/components/dashboard/SecurityIncidentFeed").then(m => ({ default: m.SecurityIncidentFeed })), { ssr: false });

interface WidgetRendererProps {
  widget: DashboardWidget;
  locale: "en" | "ar";
  data: {
    kpiData?: any;
    complianceFrameworks?: any[];
    risks?: any[];
    activities?: any[];
    tasks?: any[];
    complianceTrendData?: any[];
    incidents?: any[];
  };
}

export default function WidgetRenderer({ widget, locale, data }: WidgetRendererProps) {
  switch (widget.component_type) {
    case "risk_heatmap":
      return <RiskHeatMap risks={data.risks || []} locale={locale} />;
    case "compliance_gauge": {
      const framework = data.complianceFrameworks?.[0];
      if (!framework) return null;
      return (
        <ComplianceGauge
          score={framework.score}
          framework={framework.framework}
          compliant={framework.compliant}
          total={framework.total}
          locale={locale}
        />
      );
    }
    case "compliance_trend":
      return <ComplianceTrendChart data={data.complianceTrendData || []} locale={locale} />;
    case "activity_timeline":
      return <ActivityTimeline items={data.activities || []} locale={locale} />;
    case "task_widget":
      return <TaskWidget tasks={data.tasks || []} locale={locale} />;
    case "security_incident_feed":
      return <SecurityIncidentFeed incidents={data.incidents || []} locale={locale} />;
    default:
      return null;
  }
}
