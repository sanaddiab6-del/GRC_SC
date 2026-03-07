"use client";

import { UiPageConfig } from "@/lib/dynamic-config";

interface DynamicSectionRendererProps {
  config?: UiPageConfig;
  renderSection?: (section: UiPageConfig["sections"][number]) => React.ReactNode;
}

export default function DynamicSectionRenderer({ config, renderSection }: DynamicSectionRendererProps) {
  if (!config) {
    return null;
  }

  const sections = [...config.sections].sort((a, b) => a.order_index - b.order_index);

  return (
    <div className="space-y-6">
      {sections.map((section) => (
        <div key={section.id} className="rounded-lg border border-border/60 bg-background p-4">
          <h3 className="text-sm font-semibold text-foreground mb-3">{section.title}</h3>
          <div className="text-sm text-muted-foreground">
            {renderSection ? renderSection(section) : null}
          </div>
        </div>
      ))}
    </div>
  );
}
