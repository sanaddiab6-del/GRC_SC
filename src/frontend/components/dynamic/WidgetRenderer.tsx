"use client";

import { ComplianceGauge } from "@/components/dashboard/ComplianceGauge";
import { ComplianceTrendChart } from "@/components/dashboard/ComplianceTrendChart";
import { ActivityTimeline } from "@/components/dashboard/ActivityTimeline";
import { RiskHeatMap } from "@/components/dashboard/RiskHeatMap";
import { TaskWidget } from "@/components/dashboard/TaskWidget";
import { SecurityIncidentFeed } from "@/components/dashboard/SecurityIncidentFeed";
import { DashboardWidget } from "@/lib/dynamic-config";

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
