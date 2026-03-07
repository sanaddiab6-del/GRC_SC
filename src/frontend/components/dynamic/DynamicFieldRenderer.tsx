"use client";

import { useMemo } from "react";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { CustomField } from "@/lib/dynamic-config";

interface DynamicFieldRendererProps {
  fields: CustomField[];
  values: Record<string, any>;
  onChange: (fieldId: string, value: any) => void;
  locale?: "en" | "ar";
}

const parseOptions = (field: CustomField) => {
  if (!field.options_json) return [];
  if (Array.isArray(field.options_json)) return field.options_json;
  if (Array.isArray(field.options_json.options)) return field.options_json.options;
  return [];
};

export default function DynamicFieldRenderer({
  fields,
  values,
  onChange,
  locale = "en",
}: DynamicFieldRendererProps) {
  const normalizedFields = useMemo(() => fields || [], [fields]);

  if (!normalizedFields.length) {
    return null;
  }

  return (
    <div className="space-y-4">
      {normalizedFields.map((field) => {
        const value = values[field.id] ?? field.value ?? "";
        const label = field.field_label || field.field_key;
        const options = parseOptions(field);

        return (
          <div key={field.id} className="space-y-2">
            <label className="text-sm font-medium text-foreground">
              {label}
              {field.required ? <span className="text-red-500 ml-1">*</span> : null}
            </label>

            {field.field_type === "text" && (
              <Input
                value={value}
                onChange={(e) => onChange(field.id, e.target.value)}
                placeholder={label}
              />
            )}

            {field.field_type === "number" && (
              <Input
                type="number"
                value={value}
                onChange={(e) => onChange(field.id, e.target.value === "" ? "" : Number(e.target.value))}
                placeholder={label}
              />
            )}

            {field.field_type === "date" && (
              <Input
                type="date"
                value={value}
                onChange={(e) => onChange(field.id, e.target.value)}
              />
            )}

            {field.field_type === "boolean" && (
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={Boolean(value)}
                  onChange={(e) => onChange(field.id, e.target.checked)}
                  className="h-4 w-4"
                />cd 
                <span className="text-sm text-muted-foreground">
                  {locale === "ar" ? "تفعيل" : "Enabled"}
                </span>
              </div>
            )}

            {field.field_type === "select" && (
              <Select
                value={value}
                onValueChange={(selected) => onChange(field.id, selected)}
              >
                <SelectTrigger>
                  <SelectValue placeholder={label} />
                </SelectTrigger>
                <SelectContent>
                  {options.map((option: any) => {
                    const optValue = typeof option === "string" ? option : option.value;
                    const optLabel = typeof option === "string" ? option : option.label;
                    return (
                      <SelectItem key={optValue} value={optValue}>
                        {optLabel}
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            )}

            {field.field_type === "user" && (
              <Textarea
                value={value}
                onChange={(e) => onChange(field.id, e.target.value)}
                placeholder={locale === "ar" ? "حدد المستخدم" : "Specify user"}
              />
            )}

            {! ["text", "number", "select", "user", "date", "boolean"].includes(field.field_type) && (
              <Input
                value={value}
                onChange={(e) => onChange(field.id, e.target.value)}
                placeholder={label}
              />
            )}
          </div>
        );
      })}
    </div>
  );
}
