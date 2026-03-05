# 🎯 SICO GRC vs Jira Hybrid Model - Gap Analysis
## Achieving Smart Configurability for Saudi GRC Platform

**Report Date:** March 5, 2026  
**Strategy:** Hybrid Model (Jira-style) for NCA/ISO 27001/Saudi CSCC Compliance  
**Goal:** Product that works out-of-the-box + targeted configurability  

---

## 📋 EXECUTIVE SUMMARY

### ⚠️ CRITICAL FINDING: ALL PAGES ARE HARDCODED

**Your observation is 100% correct and represents THE most critical architectural gap.**

**Current State:**
- Every page is a hardcoded TypeScript/React file (`.tsx`)
- Evidence form, Control detail, Risk register, Dashboard - ALL hardcoded in code
- Cannot add a field, reorder sections, or customize layout without editing React components
- **This is NOT how professional enterprise GRC platforms work**

**What Professional GRC Platforms Do:**
- Pages render from database configuration (metadata-driven)
- Admins customize pages via UI, not code
- Jira, ServiceNow, Salesforce - all use this architecture
- **This is the #1 blocker to commercial viability**

**Impact:** Without database-driven UI, all other configurability features are pointless.

### Architecture Comparison

**❌ CURRENT (SICO) - Hardcoded Architecture:**
```
User requests "View Evidence #123"
  ↓
Frontend routes to: app/[locale]/evidence/[id]/page.tsx
  ↓
React renders HARDCODED component:
  - <h1>Title</h1>               ← Hardcoded in JSX
  - <p>Description</p>           ← Hardcoded in JSX  
  - <FormField name="type" />    ← Hardcoded in JSX
  - <Section title="Metadata">   ← Hardcoded in JSX
  ↓
Result: EVERY change requires editing TypeScript files
```

**✅ PROFESSIONAL GRC (Jira/ServiceNow) - Database-Driven:**
```
User requests "View Evidence #123"
  ↓
Frontend routes to: <DynamicPage pageCode="evidence_detail" />
  ↓
Load page config from database (ui_pages table):
  {
    sections: ["details", "metadata", "workflow"],
    fields: ["title", "description", "type", "control_id"]
  }
  ↓
Generic renderer builds page from config
  ↓
Result: Changes via admin UI in seconds, NO code deployment
```

### Impact Comparison

| Task | Hardcoded (Current) | Database-Driven (Needed) |
|------|---------------------|--------------------------|
| **Add field to form** | Edit `.tsx` file → 1 week dev work | Admin UI → 2 minutes |
| **Reorder form fields** | Change JSX order → 1 day dev | Drag-drop → 30 seconds |
| **Customize per client** | Fork codebase → Impossible at scale | Configure per tenant → Minutes |
| **Hide field for role** | Add if-statement → 3 days | Set visibility rule → 2 minutes |
| **Multi-tenancy** | Deploy separately → Unsustainable | One platform, many configs → Scalable |

### The Jira Hybrid Model Explained

**Jira's Success Formula:**
```
Fixed Core (Issue Tracking) + DATABASE-DRIVEN UI + Configurable Layer = 90% customer satisfaction
```

**How Jira Does It:**
- ✅ **Core is FIXED:** Issues, Projects, Boards (cannot change fundamental concepts)
- ✅ **UI is DATABASE-DRIVEN:** Pages render from configuration, not hardcoded JSX
- ✅ **Surface is FLEXIBLE:** Custom fields, workflow states, issue types (easy to add)
- ✅ **Result:** Works Day 1, customizes by Week 2

### SICO GRC Hybrid Model (Proposed)

**Your Success Formula:**
```
Fixed Core (NCA/ISO Controls) + DATABASE-DRIVEN UI + Configurable Layer = Saudi mid-market domination
```

**How SICO Should Do It:**
- ✅ **Core is FIXED:** NCA ECC/CCC/PDPL frameworks, ISO 27001 controls (pre-loaded)
- ✅ **UI is DATABASE-DRIVEN:** All pages render from ui_pages/ui_sections/ui_field_placements tables
- ✅ **Surface is FLEXIBLE:** Custom fields, workflow states, dashboard widgets (customer-specific)
- ✅ **Result:** NCA-compliant Day 1, customized to org by Week 3 (via admin UI, not code)

---

## 🔍 DETAILED COMPARISON: JIRA MODEL vs SICO CURRENT STATE

### **1. CORE ENTITIES (Fixed Foundation)**

#### **Jira Model:**

| Entity | Status | Configurability |
|--------|--------|----------------|
| **Issue** | ✅ Fixed | Cannot remove, rename to "Ticket" |
| **Project** | ✅ Fixed | Cannot change concept |
| **Board** | ✅ Fixed | Scrum/Kanban templates provided |
| **Sprint** | ✅ Fixed | Core agile concept |

**Philosophy:** Core domain model is NOT configurable. You work WITH Jira's concepts, not against them.

#### **SICO Current State:**

| Entity | Status | Configurability | Gap |
|--------|--------|----------------|-----|
| **Control** | ✅ Fixed | Cannot remove | ✅ Good |
| **Evidence** | ✅ Fixed | Cannot change concept | ✅ Good |
| **Risk** | ✅ Fixed | Core GRC concept | ✅ Good |
| **Assessment** | ✅ Fixed | Standard entity | ✅ Good |
| **Finding** | ✅ Fixed | Standard entity | ✅ Good |
| **Framework** (NCA/ISO) | ✅ Fixed | Pre-loaded | ✅ Good |

**Assessment:** ✅ **SICO matches Jira philosophy** - Core domain is fixed and correct.

**No Gap Here - Core entities are solid foundation.**

---

### **2. PAGE/UI CONFIGURATION (Database-Driven vs Hardcoded)** ⚠️ CRITICAL

#### **Jira Model:**

**How Jira Renders Pages:**
```
User clicks "View Issue" 
  ↓
Jira loads issue_type configuration from database
  ↓
Jira reads field layout from sys_ui_section table
  ↓
Jira renders form dynamically (generic renderer)
  ↓
Page appears with correct fields, tabs, sections
```

**Key Point:** Jira does NOT have separate React components for "Bug.tsx", "Story.tsx", "Epic.tsx"

**Instead:** One generic `<IssueView>` component that reads configuration from database:

```javascript
// Jira's approach (simplified)
function IssueView({ issueId }) {
    const issue = useIssue(issueId);
    const layout = useIssueLayout(issue.issue_type_id); // FROM DATABASE
    
    return (
        <DynamicForm layout={layout} data={issue} />
    );
}

// Layout comes from database:
{
    "sections": [
        {"name": "Details", "fields": ["summary", "description", "assignee"]},
        {"name": "Dates", "fields": ["created", "due_date"]},
        {"name": "Custom", "fields": ["story_points", "sprint"]}
    ]
}
```

#### **SICO Current State: ALL PAGES HARDCODED** ❌

**Evidence Upload Page:**
```typescript
// src/frontend/app/[locale]/evidence/upload/page.tsx (HARDCODED)
export default function EvidenceUploadPage() {
    return (
        <form>
            <FormField name="title" type="text" required />
            <FormField name="description" type="textarea" />
            <FormField name="evidence_type" type="select" 
                       options={['Document', 'Screenshot', 'Log']} />
            <FormField name="control_id" type="select" />
            <FormField name="file" type="file" />
        </form>
    );
}
```

**Control Detail Page:**
```typescript
// src/frontend/app/[locale]/controls/[id]/page.tsx (HARDCODED)
export default function ControlDetailPage({ params }) {
    return (
        <div>
            <h1>{control.control_id}</h1>
            <p>{control.description}</p>
            <Section title="Framework">
                <FrameworkBadge framework={control.framework} />
            </Section>
            <Section title="Evidence">
                <EvidenceList controlId={control.id} />
            </Section>
            <Section title="Risk">
                <RiskMapping controlId={control.id} />
            </Section>
        </div>
    );
}
```

**Dashboard Page:**
```typescript
// src/frontend/app/[locale]/dashboard/page.tsx (HARDCODED)
export default function DashboardPage() {
    return (
        <div className="grid grid-cols-2">
            <ComplianceScoreCard />      {/* HARDCODED WIDGET */}
            <RiskHeatMap />              {/* HARDCODED WIDGET */}
            <EvidenceStatusChart />      {/* HARDCODED WIDGET */}
            <RecentAssessments />        {/* HARDCODED WIDGET */}
        </div>
    );
}
```

**Assessment Form:**
```typescript
// src/frontend/app/[locale]/assessments/[id]/page.tsx (HARDCODED)
export default function AssessmentPage({ params }) {
    return (
        <div>
            <FormField name="title" />
            <FormField name="description" />
            <FormField name="assessment_type" />
            <FormField name="framework" />
            <FormField name="scope" />
            <FormField name="start_date" />
            <FormField name="end_date" />
            <FormField name="assigned_to" />
            <FormField name="status" />
        </div>
    );
}
```

**Risk Register Page:**
```typescript
// src/frontend/app/[locale]/risks/page.tsx (HARDCODED)
export default function RiskRegisterPage() {
    return (
        <DataTable 
            columns={[
                'risk_id', 'title', 'risk_level', 'impact', 
                'likelihood', 'owner', 'status'
            ]}  // HARDCODED COLUMNS
            data={risks}
        />
    );
}
```

**What This Means:**

| Page | Current Implementation | Problem |
|------|----------------------|---------|
| **Evidence Upload** | `evidence/upload/page.tsx` | Cannot add "Budget Code" field without editing TypeScript |
| **Control Detail** | `controls/[id]/page.tsx` | Cannot add "Internal Notes" section without code change |
| **Dashboard** | `dashboard/page.tsx` | Cannot customize widgets per user/role |
| **Assessment Form** | `assessments/[id]/page.tsx` | Cannot add "CFO Approval Date" field |
| **Risk Register** | `risks/page.tsx` | Cannot add "Mitigation Plan" column |
| **Reports** | Separate page per report type | Cannot create custom report without developer |

**Result:** 
- ❌ Every UI change requires React developer
- ❌ Every new field requires TypeScript interface update
- ❌ Every client customization requires code deployment
- ❌ Cannot offer SaaS (all clients see identical UI)
- ❌ Not a professional enterprise GRC platform

#### **Gap Analysis:**

| Feature | Jira/Enterprise GRC | SICO | Gap Severity |
|---------|---------------------|------|--------------|
| **Page layouts from database** | ✅ Yes | ❌ Hardcoded TSX | 🔴 **CRITICAL** |
| **Form schemas from database** | ✅ Yes | ❌ Hardcoded components | 🔴 **CRITICAL** |
| **Table columns configurable** | ✅ Yes | ❌ Hardcoded arrays | 🔴 **CRITICAL** |
| **Dynamic field rendering** | ✅ Yes | ❌ Static FormField | 🔴 **CRITICAL** |
| **Section/tab configuration** | ✅ Yes | ❌ Hardcoded divs | 🔴 **CRITICAL** |
| **Role-based page visibility** | ✅ Yes | ❌ All see same pages | 🟡 MEDIUM |

#### **What SICO Needs: DATABASE-DRIVEN UI**

**Database Schema for UI Configuration:**

```sql
-- Page definitions (what pages exist in the system)
CREATE TABLE ui_pages (
    page_id SERIAL PRIMARY KEY,
    page_code VARCHAR(50) UNIQUE NOT NULL,  -- 'evidence_detail', 'control_form'
    page_name_en VARCHAR(100),
    page_name_ar VARCHAR(100),
    page_type VARCHAR(50),  -- 'form', 'detail', 'list', 'dashboard'
    entity_type VARCHAR(50),  -- 'evidence', 'control', 'risk'
    layout_config JSONB,  -- Grid layout, sections, tabs
    is_active BOOLEAN DEFAULT TRUE
);

-- Page sections (tabs, panels, groups)
CREATE TABLE ui_sections (
    section_id SERIAL PRIMARY KEY,
    page_id INTEGER REFERENCES ui_pages(page_id),
    section_code VARCHAR(50),
    section_name_en VARCHAR(100),
    section_name_ar VARCHAR(100),
    section_type VARCHAR(50),  -- 'tab', 'panel', 'fieldset'
    display_order INTEGER,
    collapsible BOOLEAN DEFAULT FALSE,
    default_collapsed BOOLEAN DEFAULT FALSE
);

-- Field placements (which fields appear on which pages/sections)
CREATE TABLE ui_field_placements (
    placement_id SERIAL PRIMARY KEY,
    page_id INTEGER REFERENCES ui_pages(page_id),
    section_id INTEGER REFERENCES ui_sections(section_id),
    field_code VARCHAR(50),  -- 'title', 'description', 'evidence_type'
    field_label_en VARCHAR(100),
    field_label_ar VARCHAR(100),
    field_type VARCHAR(50),  -- 'text', 'textarea', 'select', 'date', 'file'
    is_required BOOLEAN DEFAULT FALSE,
    is_readonly BOOLEAN DEFAULT FALSE,
    display_order INTEGER,
    width VARCHAR(20),  -- 'full', 'half', 'third'
    help_text_en TEXT,
    help_text_ar TEXT,
    validation_rules JSONB,
    visibility_rules JSONB  -- Show if condition met
);

-- List view configurations (table columns)
CREATE TABLE ui_list_configs (
    config_id SERIAL PRIMARY KEY,
    page_code VARCHAR(50),  -- 'evidence_list', 'risk_register'
    column_code VARCHAR(50),  -- 'title', 'status', 'created_at'
    column_label_en VARCHAR(100),
    column_label_ar VARCHAR(100),
    column_type VARCHAR(50),  -- 'text', 'badge', 'date', 'user', 'actions'
    display_order INTEGER,
    is_sortable BOOLEAN DEFAULT TRUE,
    is_filterable BOOLEAN DEFAULT TRUE,
    width VARCHAR(20),  -- '150px', '20%', 'auto'
    align VARCHAR(20)  -- 'left', 'center', 'right'
);

-- Example: Evidence Detail Page Configuration
INSERT INTO ui_pages (page_code, page_name_en, page_name_ar, page_type, entity_type, layout_config)
VALUES (
    'evidence_detail',
    'Evidence Details',
    'تفاصيل الدليل',
    'detail',
    'evidence',
    '{"sections": ["details", "metadata", "workflow", "history"], "layout": "tabs"}'
);

-- Sections for Evidence Detail Page
INSERT INTO ui_sections (page_id, section_code, section_name_en, section_name_ar, section_type, display_order)
VALUES
    (1, 'details', 'Evidence Details', 'تفاصيل الدليل', 'tab', 1),
    (1, 'metadata', 'Metadata', 'البيانات الوصفية', 'tab', 2),
    (1, 'workflow', 'Workflow', 'سير العمل', 'tab', 3),
    (1, 'history', 'Audit Trail', 'سجل التدقيق', 'tab', 4);

-- Fields in "Details" section
INSERT INTO ui_field_placements (page_id, section_id, field_code, field_label_en, field_label_ar, field_type, is_required, display_order, width)
VALUES
    (1, 1, 'title', 'Title', 'العنوان', 'text', TRUE, 1, 'full'),
    (1, 1, 'description', 'Description', 'الوصف', 'textarea', FALSE, 2, 'full'),
    (1, 1, 'evidence_type', 'Evidence Type', 'نوع الدليل', 'select', TRUE, 3, 'half'),
    (1, 1, 'control_id', 'Related Control', 'الضابط المرتبط', 'select', TRUE, 4, 'half'),
    (1, 1, 'file', 'File Upload', 'رفع الملف', 'file', TRUE, 5, 'full');

-- Fields in "Metadata" section
INSERT INTO ui_field_placements (page_id, section_id, field_code, field_label_en, field_label_ar, field_type, display_order, width)
VALUES
    (1, 2, 'upload_date', 'Upload Date', 'تاريخ الرفع', 'date', 1, 'half'),
    (1, 2, 'validity_date', 'Validity Date', 'تاريخ الصلاحية', 'date', 2, 'half'),
    (1, 2, 'uploaded_by', 'Uploaded By', 'رفع بواسطة', 'user', 3, 'half'),
    (1, 2, 'file_hash', 'File Hash (SHA-256)', 'تجزئة الملف', 'text', 4, 'full');

-- Example: Risk Register List Configuration
INSERT INTO ui_list_configs (page_code, column_code, column_label_en, column_label_ar, column_type, display_order, width)
VALUES
    ('risk_register', 'risk_id', 'Risk ID', 'معرف المخاطر', 'text', 1, '100px'),
    ('risk_register', 'title', 'Risk Title', 'عنوان المخاطر', 'text', 2, 'auto'),
    ('risk_register', 'risk_level', 'Risk Level', 'مستوى المخاطر', 'badge', 3, '120px'),
    ('risk_register', 'impact', 'Impact', 'التأثير', 'number', 4, '80px'),
    ('risk_register', 'likelihood', 'Likelihood', 'الاحتمالية', 'number', 5, '80px'),
    ('risk_register', 'owner', 'Owner', 'المسؤول', 'user', 6, '150px'),
    ('risk_register', 'status', 'Status', 'الحالة', 'badge', 7, '120px'),
    ('risk_register', 'actions', 'Actions', 'الإجراءات', 'actions', 8, '100px');
```

**Frontend: Generic Page Renderer (Replace Hardcoded Pages)**

```typescript
// components/DynamicPage.tsx (NEW - REPLACES ALL HARDCODED PAGES)
interface DynamicPageProps {
    pageCode: string;
    entityId?: number;
    mode?: 'view' | 'edit' | 'create';
}

export function DynamicPage({ pageCode, entityId, mode = 'view' }: DynamicPageProps) {
    // Load page configuration from database
    const { data: pageConfig } = usePageConfig(pageCode);
    const { data: entityData } = useEntityData(pageConfig.entity_type, entityId);
    
    if (!pageConfig) return <Loading />;
    
    // Render page based on type
    switch (pageConfig.page_type) {
        case 'detail':
            return <DetailPageRenderer config={pageConfig} data={entityData} mode={mode} />;
        case 'form':
            return <FormPageRenderer config={pageConfig} data={entityData} mode={mode} />;
        case 'list':
            return <ListPageRenderer config={pageConfig} />;
        case 'dashboard':
            return <DashboardPageRenderer config={pageConfig} />;
        default:
            return <div>Unknown page type</div>;
    }
}

// components/DetailPageRenderer.tsx
function DetailPageRenderer({ config, data, mode }) {
    const sections = config.sections;
    
    return (
        <div className="detail-page">
            <Tabs>
                {sections.map(section => (
                    <Tab key={section.section_id} label={section.section_name_en}>
                        <SectionRenderer 
                            section={section}
                            data={data}
                            mode={mode}
                        />
                    </Tab>
                ))}
            </Tabs>
        </div>
    );
}

// components/SectionRenderer.tsx
function SectionRenderer({ section, data, mode }) {
    const { data: fields } = useFieldPlacements(section.section_id);
    
    return (
        <div className="section">
            {fields.map(field => (
                <DynamicField
                    key={field.placement_id}
                    field={field}
                    value={data?.[field.field_code]}
                    onChange={(val) => updateField(field.field_code, val)}
                    readonly={mode === 'view' || field.is_readonly}
                />
            ))}
        </div>
    );
}

// components/DynamicField.tsx
function DynamicField({ field, value, onChange, readonly }) {
    // Check visibility rules
    if (field.visibility_rules && !evaluateVisibility(field.visibility_rules, data)) {
        return null;
    }
    
    // Render based on field type
    switch (field.field_type) {
        case 'text':
            return <Input label={field.field_label_en} value={value} onChange={onChange} disabled={readonly} required={field.is_required} />;
        case 'textarea':
            return <Textarea label={field.field_label_en} value={value} onChange={onChange} disabled={readonly} />;
        case 'select':
            return <Select label={field.field_label_en} value={value} onChange={onChange} disabled={readonly} options={getFieldOptions(field.field_code)} />;
        case 'date':
            return <DatePicker label={field.field_label_en} value={value} onChange={onChange} disabled={readonly} />;
        case 'file':
            return <FileUpload label={field.field_label_en} value={value} onChange={onChange} disabled={readonly} />;
        case 'user':
            return <UserPicker label={field.field_label_en} value={value} onChange={onChange} disabled={readonly} />;
        // ... more field types
        default:
            return <div>Unknown field type: {field.field_type}</div>;
    }
}

// components/ListPageRenderer.tsx
function ListPageRenderer({ config }) {
    const { data: columns } = useListColumns(config.page_code);
    const { data: rows } = useEntityList(config.entity_type);
    
    return (
        <DataTable
            columns={columns.map(col => ({
                header: col.column_label_en,
                field: col.column_code,
                sortable: col.is_sortable,
                width: col.width,
                align: col.align,
                render: (row) => renderCell(row, col)
            }))}
            data={rows}
        />
    );
}
```

**Usage: Replace ALL Hardcoded Pages**

```typescript
// OLD (HARDCODED):
// app/[locale]/evidence/[id]/page.tsx
export default function EvidenceDetailPage({ params }) {
    return (
        <div>
            <h1>{evidence.title}</h1>
            <p>{evidence.description}</p>
            {/* 50 lines of hardcoded JSX */}
        </div>
    );
}

// NEW (DATABASE-DRIVEN):
// app/[locale]/evidence/[id]/page.tsx
export default function EvidenceDetailPage({ params }) {
    return <DynamicPage pageCode="evidence_detail" entityId={params.id} mode="view" />;
}

// OLD (HARDCODED):
// app/[locale]/risks/page.tsx
export default function RiskRegisterPage() {
    return (
        <DataTable 
            columns={['risk_id', 'title', 'risk_level']}  // HARDCODED
            data={risks}
        />
    );
}

// NEW (DATABASE-DRIVEN):
// app/[locale]/risks/page.tsx
export default function RiskRegisterPage() {
    return <DynamicPage pageCode="risk_register" />;
}
```

**Admin UI: Page Configuration**

```
Location: /admin/ui-configuration

┌─────────────────────────────────────────────────┐
│ UI Configuration                                │
│                                                 │
│ Pages:  [Evidence Detail ▼]  [Edit Page]       │
│                                                 │
│ Current Layout:                                 │
│ ┌──────────────────────────────────────────┐   │
│ │ Section 1: Details (Tab)                 │   │
│ │   - Title (text, required)               │   │
│ │   - Description (textarea)               │   │
│ │   - Evidence Type (select, required)     │   │
│ │   - Control (select, required)           │   │
│ │   [Add Field] [Reorder]                  │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ ┌──────────────────────────────────────────┐   │
│ │ Section 2: Metadata (Tab)                │   │
│ │   - Upload Date (date, readonly)         │   │
│ │   - Validity Date (date)                 │   │
│ │   - Uploaded By (user, readonly)         │   │
│ │   - File Hash (text, readonly)           │   │
│ │   [Add Field] [Reorder]                  │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ [+ Add Section]  [Save Changes]                │
└─────────────────────────────────────────────────┘

Add Field Dialog:
┌─────────────────────────────────────────────────┐
│ Add Field to Section                            │
│                                                 │
│ Field Name: [Budget Code_____________]          │
│ Field Type: [Text ▼]                            │
│ Required:   ☐                                   │
│ Readonly:   ☐                                   │
│ Width:      ● Full  ○ Half  ○ Third             │
│                                                 │
│ Label (EN): [Budget Code_____________]          │
│ Label (AR): [رمز الميزانية____________]         │
│                                                 │
│ Help Text (EN): [___________________________]   │
│                                                 │
│ [Cancel]  [Add Field]                           │
└─────────────────────────────────────────────────┘
```

**Backend API:**

```python
# ui_config/router.py (NEW MODULE)

@router.get("/ui-config/pages/{page_code}")
async def get_page_config(page_code: str):
    """Get page configuration including sections and fields."""
    # Query ui_pages, ui_sections, ui_field_placements
    # Return complete page structure
    return {
        "page_code": "evidence_detail",
        "page_name_en": "Evidence Details",
        "page_type": "detail",
        "entity_type": "evidence",
        "sections": [
            {
                "section_id": 1,
                "section_name_en": "Details",
                "section_type": "tab",
                "fields": [
                    {
                        "field_code": "title",
                        "field_label_en": "Title",
                        "field_type": "text",
                        "is_required": True,
                        "width": "full"
                    },
                    # ... more fields
                ]
            }
        ]
    }

@router.get("/ui-config/lists/{page_code}")
async def get_list_config(page_code: str):
    """Get list/table column configuration."""
    # Query ui_list_configs
    return columns

@router.post("/ui-config/pages/{page_code}/fields")
async def add_field_to_page(
    page_code: str,
    section_id: int,
    field: FieldPlacementCreate,
    current_user: User = Depends(get_current_admin)
):
    """Add a new field to a page section."""
    # Insert into ui_field_placements
    pass

@router.put("/ui-config/pages/{page_code}/layout")
async def update_page_layout(
    page_code: str,
    layout: PageLayoutUpdate,
    current_user: User = Depends(get_current_admin)
):
    """Update page section order, field positions."""
    # Update ui_sections.display_order, ui_field_placements.display_order
    pass
```

**Impact Assessment:**

| Scenario | Current (Hardcoded) | After Database-Driven UI |
|----------|---------------------|--------------------------|
| **Add field to Evidence form** | Edit `evidence/upload/page.tsx` → 1 week dev | Admin clicks "Add Field" → 2 minutes |
| **Rearrange form sections** | Edit TSX, adjust CSS → 1 day | Drag-drop in UI → 30 seconds |
| **Customize dashboard per role** | Create separate pages → 1 week | Select widgets in admin → 10 minutes |
| **Hide field for certain clients** | if/else in code → 3 days | Set visibility rule → 5 minutes |
| **Add new report type** | Create new page + API → 1-2 weeks | Use report template + config → 1 hour |
| **Multi-tenant customization** | Fork codebase per client → Impossible | Configure per tenant → Minutes |

**Effort Estimate:** 6-8 weeks (2 developers)

**Priority:** 🔴 **CRITICAL** - This is THE fundamental gap preventing enterprise viability

---

### **3. CUSTOM FIELDS (Configurable Layer)**

#### **Jira Model:**

**Out-of-Box Fields (Fixed):**
```
Issue:
  - Summary (text, required)
  - Description (rich text)
  - Status (workflow-driven)
  - Assignee (user picker)
  - Reporter (auto-set)
  - Priority (dropdown: High/Medium/Low)
  - Created Date (auto)
```

**Custom Fields (Customer Adds via UI):**
```
Admin > Issues > Custom Fields > Create Custom Field

Field Types Available:
  ✅ Text (single/multi-line)
  ✅ Number
  ✅ Date/DateTime
  ✅ Dropdown (single/multi-select)
  ✅ User Picker
  ✅ Checkbox
  ✅ URL
  ✅ Labels
  ✅ Cascading Select

Example Custom Fields Added by Customers:
  - "Story Points" (number)
  - "Sprint" (dropdown)
  - "Customer Impact" (dropdown: High/Medium/Low/None)
  - "QA Verified" (checkbox)
  - "External Reference" (text)
```

**Key Feature:** Non-technical admin can add fields in 2 minutes via UI.

#### **SICO Current State:**

**Out-of-Box Fields (Fixed in Code):**
```python
# Evidence model (example)
class Evidence(Base):
    id: int                    # Auto
    title: str                 # Required
    description: str           # Optional
    evidence_type: str         # Dropdown
    upload_date: datetime      # Auto
    validity_date: date        # Optional
    file_hash: str             # Auto
    uploaded_by: int           # Auto
    status: str                # Workflow-driven
    control_id: int            # Foreign key
```

**Custom Fields:**
❌ **NOT IMPLEMENTED**

**What Customers Cannot Do:**
- ❌ Add "Internal Audit Reference" field
- ❌ Add "Budget Code" field
- ❌ Add "Department" dropdown
- ❌ Add "Requires CFO Approval" checkbox
- ❌ Add "External Auditor Notes" text field

**Result:** Every custom field request = developer work + code deployment

#### **Gap Analysis:**

| Feature | Jira | SICO | Gap Severity |
|---------|------|------|--------------|
| **Add custom text field** | ✅ 2 min via UI | ❌ 1 week dev work | 🔴 CRITICAL |
| **Add custom dropdown** | ✅ 3 min via UI | ❌ 1-2 weeks dev | 🔴 CRITICAL |
| **Add custom date field** | ✅ 2 min via UI | ❌ 1 week dev | 🔴 CRITICAL |
| **Add custom checkbox** | ✅ 2 min via UI | ❌ 1 week dev | 🔴 CRITICAL |
| **Field-level permissions** | ✅ Yes | ❌ No | 🟡 MEDIUM |
| **Conditional field display** | ⚠️ Paid add-on | ❌ No | 🟡 MEDIUM |

#### **What SICO Needs:**

**Database Schema (New Tables):**
```sql
-- Custom field definitions
CREATE TABLE custom_field_definitions (
    field_id SERIAL PRIMARY KEY,
    entity_type VARCHAR(50) NOT NULL,  -- 'control', 'evidence', 'risk', 'assessment'
    field_name VARCHAR(100) NOT NULL,  -- 'internal_audit_ref'
    field_label_en VARCHAR(100),       -- 'Internal Audit Reference'
    field_label_ar VARCHAR(100),       -- 'مرجع التدقيق الداخلي'
    field_type VARCHAR(50) NOT NULL,   -- 'text', 'number', 'date', 'dropdown', 'checkbox'
    is_required BOOLEAN DEFAULT FALSE,
    default_value TEXT,
    validation_regex VARCHAR(200),
    display_order INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by INTEGER,
    is_active BOOLEAN DEFAULT TRUE
);

-- Dropdown options (for dropdown/multi-select fields)
CREATE TABLE custom_field_options (
    option_id SERIAL PRIMARY KEY,
    field_id INTEGER REFERENCES custom_field_definitions(field_id),
    option_value VARCHAR(100),
    option_label_en VARCHAR(100),
    option_label_ar VARCHAR(100),
    option_order INTEGER
);

-- Custom field values (stores actual data)
CREATE TABLE custom_field_values (
    value_id SERIAL PRIMARY KEY,
    field_id INTEGER REFERENCES custom_field_definitions(field_id),
    entity_type VARCHAR(50),
    entity_id INTEGER,  -- ID of the control/evidence/risk record
    field_value TEXT,   -- Stores the actual value (JSON for complex types)
    updated_at TIMESTAMP DEFAULT NOW(),
    updated_by INTEGER,
    UNIQUE(field_id, entity_type, entity_id)
);

-- Example data:
INSERT INTO custom_field_definitions (entity_type, field_name, field_label_en, field_label_ar, field_type)
VALUES ('evidence', 'budget_code', 'Budget Code', 'رمز الميزانية', 'text');

INSERT INTO custom_field_definitions (entity_type, field_name, field_label_en, field_label_ar, field_type)
VALUES ('evidence', 'department', 'Department', 'القسم', 'dropdown');

INSERT INTO custom_field_options (field_id, option_value, option_label_en, option_label_ar)
VALUES (2, 'IT', 'Information Technology', 'تكنولوجيا المعلومات');
```

**Admin UI Required:**
```
Location: /admin/custom-fields

Page Layout:
┌─────────────────────────────────────────────┐
│ Custom Fields Management                    │
│                                             │
│ Entity: [Evidence ▼]  [+ Add Field]        │
│                                             │
│ ┌──────────────────────────────────────┐   │
│ │ Field Name: Budget Code              │   │
│ │ Type: Text                           │   │
│ │ Required: ☐                          │   │
│ │ [Edit] [Delete]                      │   │
│ └──────────────────────────────────────┘   │
│                                             │
│ ┌──────────────────────────────────────┐   │
│ │ Field Name: Department               │   │
│ │ Type: Dropdown                       │   │
│ │ Options: IT, Finance, HR, Legal      │   │
│ │ Required: ☑                          │   │
│ │ [Edit] [Delete]                      │   │
│ └──────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

**Backend API Required:**
```python
# New router: custom_fields/router.py

@router.post("/custom-fields")
async def create_custom_field(
    field: CustomFieldCreate,
    current_user: User = Depends(get_current_admin)
):
    """Create a new custom field definition."""
    # Validate field_name (alphanumeric, no spaces)
    # Insert into custom_field_definitions table
    # Return field_id
    pass

@router.get("/custom-fields/{entity_type}")
async def list_custom_fields(entity_type: str):
    """Get all custom fields for an entity type."""
    # Query custom_field_definitions WHERE entity_type = ?
    # Return list of fields with options
    pass

@router.put("/custom-field-values/{entity_type}/{entity_id}")
async def save_custom_field_values(
    entity_type: str,
    entity_id: int,
    values: Dict[str, Any]
):
    """Save custom field values for a specific record."""
    # Upsert into custom_field_values table
    pass

@router.get("/{entity_type}/{entity_id}/custom-fields")
async def get_custom_field_values(entity_type: str, entity_id: int):
    """Get custom field values for a record."""
    # Join custom_field_definitions + custom_field_values
    # Return merged dict
    pass
```

**Frontend Changes Required:**
```typescript
// components/CustomFieldRenderer.tsx
export function CustomFieldRenderer({ 
    entityType, 
    entityId, 
    mode = 'edit' // or 'view'
}) {
    const { data: customFields } = useCustomFields(entityType);
    const { data: values, mutate } = useCustomFieldValues(entityType, entityId);
    
    return (
        <div className="custom-fields-section">
            <h3>Additional Fields</h3>
            {customFields?.map(field => (
                <CustomFieldInput 
                    key={field.field_id}
                    field={field}
                    value={values?.[field.field_name]}
                    onChange={(val) => mutate({ [field.field_name]: val })}
                    disabled={mode === 'view'}
                />
            ))}
        </div>
    );
}

// Usage in Evidence form:
<FormField name="title" ... />
<FormField name="description" ... />
<FormField name="evidence_type" ... />

{/* NEW: Render custom fields */}
<CustomFieldRenderer 
    entityType="evidence" 
    entityId={evidenceId}
    mode="edit"
/>
```

**Effort Estimate:** 3-4 weeks (2 developers)

---

### **3. WORKFLOW STATES (Configurable Layer)**

#### **Jira Model:**

**Default Workflow (Fixed for starters):**
```
To Do → In Progress → Done
```

**Custom Workflows (Admin adds states via UI):**
```
Admin > Issues > Workflows > Edit Workflow

Example Custom Workflow:
  Backlog → 
  To Do → 
  In Development → 
  Code Review → 
  QA Testing → 
  QA Failed → (loop back to In Development)
  QA Passed → 
  UAT → 
  Deployed → 
  Closed

Transitions:
  - From "QA Testing" to "QA Passed" IF test_results = "Pass"
  - From "QA Testing" to "QA Failed" IF test_results = "Fail"
  - Auto-transition to "Closed" after 30 days in "Deployed"
```

**Key Feature:** Non-technical admin can add/remove states, set transition rules.

#### **SICO Current State:**

**Evidence Workflow (Hardcoded in Python Enum):**
```python
class EvidenceStatus(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"
```

**Assessment Workflow (Hardcoded):**
```python
class AssessmentStatus(str, Enum):
    DRAFT = "draft"
    LAUNCHED = "launched"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    CLOSED = "closed"
```

**What Customers Cannot Do:**
- ❌ Add "Quality Review" state between "Submitted" and "Approved"
- ❌ Add "CFO Approval" state for high-risk findings
- ❌ Add "External Audit" state for evidence
- ❌ Remove "Archived" state if not needed
- ❌ Rename "Pending Approval" to "Awaiting Sign-Off"

**Result:** Every workflow change = code change + redeployment

#### **Gap Analysis:**

| Feature | Jira | SICO | Gap Severity |
|---------|------|------|--------------|
| **Add custom workflow state** | ✅ 5 min via UI | ❌ 1 week dev work | 🔴 CRITICAL |
| **Remove workflow state** | ✅ Yes | ❌ No | 🔴 CRITICAL |
| **Rename state** | ✅ Yes | ❌ No | 🟡 MEDIUM |
| **Set transition conditions** | ✅ Yes | ❌ No | 🟡 MEDIUM |
| **Auto-transitions (SLA)** | ✅ Plugin | ❌ No | 🟡 MEDIUM |
| **Workflow versioning** | ✅ Yes | ❌ One version | 🟢 LOW |

#### **What SICO Needs:**

**Database Schema:**
```sql
-- Workflow definitions
CREATE TABLE workflow_definitions (
    workflow_id SERIAL PRIMARY KEY,
    workflow_name VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,  -- 'evidence', 'assessment', 'finding'
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Workflow states
CREATE TABLE workflow_states (
    state_id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES workflow_definitions(workflow_id),
    state_name VARCHAR(50) NOT NULL,
    state_label_en VARCHAR(100),
    state_label_ar VARCHAR(100),
    state_color VARCHAR(20),  -- For UI display (e.g., 'green', 'yellow', 'red')
    state_order INTEGER,      -- Display order
    is_initial BOOLEAN DEFAULT FALSE,  -- Starting state?
    is_final BOOLEAN DEFAULT FALSE     -- Ending state?
);

-- Workflow transitions (what moves are allowed)
CREATE TABLE workflow_transitions (
    transition_id SERIAL PRIMARY KEY,
    workflow_id INTEGER REFERENCES workflow_definitions(workflow_id),
    from_state_id INTEGER REFERENCES workflow_states(state_id),
    to_state_id INTEGER REFERENCES workflow_states(state_id),
    transition_name VARCHAR(100),      -- "Approve", "Reject", "Send for Review"
    require_comment BOOLEAN DEFAULT FALSE,
    allowed_roles JSONB,               -- ["admin", "compliance_officer"]
    condition_rules JSONB,             -- {"field": "risk_score", "operator": ">", "value": 7}
    UNIQUE(workflow_id, from_state_id, to_state_id)
);

-- Example data (Evidence workflow):
INSERT INTO workflow_definitions (workflow_name, entity_type, is_default)
VALUES ('Standard Evidence Workflow', 'evidence', TRUE);

INSERT INTO workflow_states (workflow_id, state_name, state_label_en, state_label_ar, state_order, is_initial)
VALUES 
    (1, 'draft', 'Draft', 'مسودة', 1, TRUE),
    (1, 'pending_approval', 'Pending Approval', 'في انتظار الموافقة', 2, FALSE),
    (1, 'quality_review', 'Quality Review', 'مراجعة الجودة', 3, FALSE),  -- CUSTOM STATE ADDED
    (1, 'approved', 'Approved', 'موافق عليه', 4, FALSE),
    (1, 'rejected', 'Rejected', 'مرفوض', 5, FALSE),
    (1, 'archived', 'Archived', 'مؤرشف', 6, TRUE);

INSERT INTO workflow_transitions (workflow_id, from_state_id, to_state_id, transition_name, allowed_roles)
VALUES
    (1, 1, 2, 'Submit for Approval', '["analyst", "compliance_officer"]'),
    (1, 2, 3, 'Send to Quality', '["compliance_officer"]'),
    (1, 3, 4, 'Approve', '["admin", "compliance_officer"]'),
    (1, 3, 2, 'Request Changes', '["admin"]'),
    (1, 2, 5, 'Reject', '["admin", "compliance_officer"]');
```

**Admin UI Required:**
```
Location: /admin/workflows

Page Layout:
┌─────────────────────────────────────────────────┐
│ Workflow Designer                               │
│                                                 │
│ Workflow: Evidence Approval  Entity: Evidence  │
│                                                 │
│ States:                        [+ Add State]    │
│                                                 │
│ ┌─────────────────────────────────────────┐    │
│ │ 1. Draft (Initial)                      │    │
│ │    Color: Gray                          │    │
│ │    [Edit] [Delete]                      │    │
│ └─────────────────────────────────────────┘    │
│                 ↓                               │
│ ┌─────────────────────────────────────────┐    │
│ │ 2. Pending Approval                     │    │
│ │    Color: Yellow                        │    │
│ │    Transition: Submit for Approval      │    │
│ │    Allowed: Analyst, Compliance Officer │    │
│ │    [Edit] [Delete]                      │    │
│ └─────────────────────────────────────────┘    │
│                 ↓                               │
│ ┌─────────────────────────────────────────┐    │
│ │ 3. Quality Review (CUSTOM)              │    │
│ │    Color: Orange                        │    │
│ │    Transition: Send to Quality          │    │
│ │    Allowed: Compliance Officer          │    │
│ │    [Edit] [Delete]                      │    │
│ └─────────────────────────────────────────┘    │
│            ↓              ↓                     │
│      Approve       Request Changes             │
└─────────────────────────────────────────────────┘
```

**Backend Changes:**
```python
# Update Evidence model to reference workflow
class Evidence(Base):
    # ... existing fields ...
    workflow_id: int = 1  # Default workflow
    current_state_id: int  # References workflow_states

# Dynamic status endpoint
@router.get("/evidence/{evidence_id}/transitions")
async def get_available_transitions(evidence_id: int, current_user: User):
    """Get valid state transitions for this evidence based on workflow + user role."""
    evidence = await get_evidence(evidence_id)
    workflow = await get_workflow(evidence.workflow_id)
    current_state = evidence.current_state_id
    
    # Query workflow_transitions WHERE from_state_id = current_state
    # Filter by user's roles
    # Return allowed transitions
    return {
        "current_state": "pending_approval",
        "transitions": [
            {"to_state": "quality_review", "label": "Send to Quality", "requires_comment": False},
            {"to_state": "rejected", "label": "Reject", "requires_comment": True}
        ]
    }

@router.post("/evidence/{evidence_id}/transition")
async def execute_transition(
    evidence_id: int,
    to_state_id: int,
    comment: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Move evidence to new state."""
    # Validate transition is allowed
    # Update evidence.current_state_id
    # Log in audit trail
    # Send notifications
    pass
```

**Frontend Changes:**
```typescript
// components/WorkflowActions.tsx
export function WorkflowActions({ entityType, entityId }) {
    const { data: transitions } = useAvailableTransitions(entityType, entityId);
    
    return (
        <div className="workflow-actions">
            <h4>Available Actions:</h4>
            {transitions?.map(t => (
                <Button 
                    key={t.to_state}
                    onClick={() => executeTransition(t.to_state)}
                >
                    {t.label}
                </Button>
            ))}
        </div>
    );
}

// Usage in Evidence detail page:
<EvidenceDetails evidence={evidence} />
<WorkflowActions entityType="evidence" entityId={evidence.id} />
```

**Effort Estimate:** 4-5 weeks (2 developers)

---

### **4. DASHBOARD WIDGETS (Configurable Layer)**

#### **Jira Model:**

**Default Dashboard (Fixed Widgets):**
```
- Assigned to Me (issue list)
- Activity Stream (recent updates)
- Created vs Resolved Chart (line chart)
```

**Custom Dashboard (User adds widgets):**
```
Dashboard > Edit > Add Gadget

Widget Library (50+ options):
  ✅ Issue Statistics (pie chart)
  ✅ Filter Results (custom query)
  ✅ Sprint Burndown (chart)
  ✅ Velocity Chart (bar chart)
  ✅ Created vs Resolved (line chart)
  ✅ Average Age (number)
  ✅ Text (custom message)
  ✅ iFrame (embed external)

User Creates:
  - 2x2 grid layout
  - Drag-drop widgets
  - Configure each widget (filters, display options)
  - Save as personal or team dashboard
```

**Key Feature:** Each user can have 5-10 different dashboards with different widgets.

#### **SICO Current State:**

**Single Dashboard (Hardcoded in React):**
```typescript
// app/[locale]/dashboard/page.tsx
export default function DashboardPage() {
    return (
        <div className="grid">
            <ComplianceScoreCard />      {/* Hardcoded */}
            <RiskHeatMap />              {/* Hardcoded */}
            <EvidenceStatusChart />      {/* Hardcoded */}
            <RecentAssessments />        {/* Hardcoded */}
            <PendingApprovals />         {/* Hardcoded */}
        </div>
    );
}
```

**What Users Cannot Do:**
- ❌ Add "My Open Findings" widget
- ❌ Remove "Risk HeatMap" if not needed
- ❌ Rearrange widget positions
- ❌ Create separate dashboard for Auditors vs Analysts
- ❌ Add custom KPI widget (e.g., "Controls Due This Month")

**Result:** Everyone sees same dashboard, cannot personalize.

#### **Gap Analysis:**

| Feature | Jira | SICO | Gap Severity |
|---------|------|------|--------------|
| **Add widget from library** | ✅ 1 min via UI | ❌ Hardcoded | 🔴 CRITICAL |
| **Remove widget** | ✅ Yes | ❌ No | 🔴 CRITICAL |
| **Rearrange widgets** | ✅ Drag-drop | ❌ Fixed grid | 🔴 CRITICAL |
| **Multiple dashboards** | ✅ Unlimited | ❌ One dashboard | 🟡 MEDIUM |
| **Role-based dashboards** | ✅ Yes | ❌ No | 🟡 MEDIUM |
| **Export dashboard** | ✅ PDF | ❌ No | 🟢 LOW |

#### **What SICO Needs:**

**Simplified Approach (Not Full Drag-Drop):**

Instead of complex drag-drop builder, use **widget selection from library**:

**Database Schema:**
```sql
-- Widget library (pre-defined by developers)
CREATE TABLE widget_library (
    widget_id SERIAL PRIMARY KEY,
    widget_code VARCHAR(50) UNIQUE NOT NULL,  -- 'compliance_score', 'risk_heatmap'
    widget_name_en VARCHAR(100),
    widget_name_ar VARCHAR(100),
    widget_description_en TEXT,
    widget_type VARCHAR(50),  -- 'chart', 'kpi', 'list', 'table'
    requires_params BOOLEAN DEFAULT FALSE,
    default_config JSONB,
    applicable_roles JSONB  -- ["admin", "analyst", "auditor"]
);

-- User dashboard configurations
CREATE TABLE user_dashboards (
    dashboard_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    dashboard_name VARCHAR(100),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Dashboard widgets (user's selected widgets)
CREATE TABLE dashboard_widgets (
    id SERIAL PRIMARY KEY,
    dashboard_id INTEGER REFERENCES user_dashboards(dashboard_id),
    widget_id INTEGER REFERENCES widget_library(widget_id),
    position_row INTEGER,      -- 1-based row number
    position_col INTEGER,      -- 1-based column number (1-2 for 2-column layout)
    width INTEGER DEFAULT 1,   -- 1 = half width, 2 = full width
    height INTEGER DEFAULT 1,  -- 1 = standard, 2 = tall
    config JSONB,              -- Widget-specific settings (filters, etc.)
    display_order INTEGER
);

-- Example data (Widget Library):
INSERT INTO widget_library (widget_code, widget_name_en, widget_name_ar, widget_type, default_config)
VALUES 
    ('compliance_score', 'Compliance Score', 'نقاط الامتثال', 'kpi', '{}'),
    ('risk_heatmap', 'Risk Heat Map', 'خريطة المخاطر', 'chart', '{"framework": "all"}'),
    ('evidence_status', 'Evidence Status', 'حالة الأدلة', 'chart', '{"chart_type": "pie"}'),
    ('recent_assessments', 'Recent Assessments', 'التقييمات الأخيرة', 'list', '{"limit": 5}'),
    ('pending_approvals', 'Pending Approvals', 'الموافقات المعلقة', 'list', '{"limit": 10}'),
    ('my_findings', 'My Open Findings', 'نتائجي المفتوحة', 'table', '{"status": "open"}'),
    ('controls_due', 'Controls Due This Month', 'الضوابط المستحقة', 'list', '{"days": 30}'),
    ('framework_gap', 'Framework Gap Analysis', 'تحليل الفجوات', 'chart', '{"framework": "nca_ecc"}');

-- Example: User's custom dashboard
INSERT INTO user_dashboards (user_id, dashboard_name, is_default)
VALUES (1, 'My Compliance Dashboard', TRUE);

INSERT INTO dashboard_widgets (dashboard_id, widget_id, position_row, position_col, width)
VALUES
    (1, 1, 1, 1, 2),  -- Compliance Score (full width, row 1)
    (1, 5, 2, 1, 1),  -- Pending Approvals (half width, row 2 col 1)
    (1, 6, 2, 2, 1),  -- My Findings (half width, row 2 col 2)
    (1, 2, 3, 1, 2);  -- Risk HeatMap (full width, row 3)
```

**Admin/User UI Required:**
```
Location: /dashboard/customize

Page Layout:
┌─────────────────────────────────────────────────┐
│ Customize Dashboard                             │
│                                                 │
│ Available Widgets:         [+ Add Widget]       │
│                                                 │
│ ┌──────────────────┐  ┌──────────────────┐    │
│ │ Compliance Score │  │ Risk Heat Map    │    │
│ │ • KPI widget     │  │ • Chart widget   │    │
│ │ [Add to Dashboard]│  │ [Add to Dashboard]│    │
│ └──────────────────┘  └──────────────────┘    │
│                                                 │
│ ┌──────────────────┐  ┌──────────────────┐    │
│ │ My Findings      │  │ Controls Due     │    │
│ │ • Table widget   │  │ • List widget    │    │
│ │ [Add to Dashboard]│  │ [Add to Dashboard]│    │
│ └──────────────────┘  └──────────────────┘    │
│                                                 │
│ ────────────────────────────────────────       │
│ Your Dashboard Preview:                        │
│                                                 │
│ ┌─────────────────────────────────────────┐   │
│ │ Compliance Score: 87%                   │   │
│ └─────────────────────────────────────────┘   │
│ ┌────────────────────┐ ┌─────────────────┐   │
│ │ Pending Approvals  │ │ My Findings     │   │
│ │ • Evidence #123    │ │ • Finding #45   │   │
│ │ • Evidence #124    │ │ • Finding #47   │   │
│ │ [Remove]           │ │ [Remove]        │   │
│ └────────────────────┘ └─────────────────┘   │
│ ┌─────────────────────────────────────────┐   │
│ │ Risk Heat Map                           │   │
│ │ [Remove]                                │   │
│ └─────────────────────────────────────────┘   │
│                                                 │
│ [Save Dashboard]  [Reset to Default]           │
└─────────────────────────────────────────────────┘
```

**Backend API:**
```python
# dashboards/router.py

@router.get("/widget-library")
async def get_widget_library(current_user: User):
    """Get available widgets for user's role."""
    # Query widget_library WHERE user.role in applicable_roles
    return widgets

@router.get("/dashboards/my")
async def get_user_dashboards(current_user: User):
    """Get user's saved dashboards."""
    return dashboards

@router.post("/dashboards")
async def create_dashboard(
    dashboard: DashboardCreate,
    widgets: List[WidgetConfig],
    current_user: User
):
    """Create custom dashboard with selected widgets."""
    # Insert into user_dashboards + dashboard_widgets
    pass

@router.get("/dashboards/{dashboard_id}/data")
async def get_dashboard_data(dashboard_id: int, current_user: User):
    """Get data for all widgets in dashboard."""
    # For each widget in dashboard:
    #   - Fetch widget config
    #   - Execute widget's data query
    #   - Return merged data
    return {
        "widgets": [
            {"widget_id": 1, "data": {"score": 87, "trend": "up"}},
            {"widget_id": 5, "data": {"items": [...]}}
        ]
    }
```

**Frontend Changes:**
```typescript
// components/DynamicDashboard.tsx
export function DynamicDashboard({ dashboardId }) {
    const { data: dashboard } = useDashboard(dashboardId);
    
    return (
        <div className="grid grid-cols-2 gap-4">
            {dashboard?.widgets.map(widget => (
                <div 
                    key={widget.id}
                    className={`col-span-${widget.width} row-span-${widget.height}`}
                >
                    <WidgetRenderer 
                        widgetCode={widget.widget_code}
                        config={widget.config}
                        data={widget.data}
                    />
                </div>
            ))}
        </div>
    );
}

// components/WidgetRenderer.tsx
export function WidgetRenderer({ widgetCode, config, data }) {
    switch (widgetCode) {
        case 'compliance_score':
            return <ComplianceScoreWidget data={data} />;
        case 'risk_heatmap':
            return <RiskHeatMapWidget data={data} config={config} />;
        case 'my_findings':
            return <FindingsTableWidget data={data} />;
        // ... etc
        default:
            return <div>Unknown widget</div>;
    }
}
```

**Effort Estimate:** 3-4 weeks (2 developers)

---

### **5. REPORT TEMPLATES (Configurable Layer)**

#### **Jira Model:**

**Built-in Reports:**
- Issue Statistics
- Pie Chart Report
- Time Tracking Report
- Version Report
- Sprint Report

**Custom Reports (Marketplace + Plugins):**
- Custom Charts for Jira Cloud
- eazyBI Reports and Charts
- Advanced Roadmaps

**PDF Export:** ✅ All reports exportable to PDF/Excel

#### **SICO Current State:**

**Reports:**
```typescript
// Hardcoded in frontend
- Compliance Dashboard (view only, no export)
- Risk HeatMap (view only)
- Evidence Status Chart (view only)
```

❌ **No Export Functionality**
❌ **No Report Templates**
❌ **No Scheduled Reports**
❌ **No Custom Reports**

#### **Gap Analysis:**

| Feature | Jira | SICO | Gap Severity |
|---------|------|------|--------------|
| **PDF Export** | ✅ Yes | ❌ Not working | 🔴 CRITICAL |
| **Excel Export** | ✅ Yes | ❌ Not working | 🔴 CRITICAL |
| **Report Templates** | ✅ 20+ built-in | ❌ None | 🔴 CRITICAL |
| **Custom Reports** | ✅ Via plugins | ❌ No | 🟡 MEDIUM |
| **Scheduled Reports** | ✅ Email delivery | ❌ No | 🟡 MEDIUM |

#### **What SICO Needs:**

**Simplified Approach: Pre-built Templates (Not Custom Report Builder)**

Instead of complex SQL query builder, provide **10-15 Saudi-specific report templates**:

**Database Schema:**
```sql
-- Report templates (pre-defined by developers)
CREATE TABLE report_templates (
    template_id SERIAL PRIMARY KEY,
    template_code VARCHAR(50) UNIQUE NOT NULL,
    template_name_en VARCHAR(100),
    template_name_ar VARCHAR(100),
    description_en TEXT,
    description_ar TEXT,
    category VARCHAR(50),  -- 'compliance', 'risk', 'audit', 'evidence'
    output_formats JSONB,  -- ["pdf", "excel", "csv"]
    parameters JSONB,      -- Required/optional parameters (date range, framework, etc.)
    query_definition TEXT  -- SQL or API endpoint
);

-- Generated reports (history)
CREATE TABLE report_history (
    report_id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES report_templates(template_id),
    generated_by INTEGER REFERENCES users(id),
    parameters JSONB,
    file_path VARCHAR(500),
    file_format VARCHAR(10),
    generated_at TIMESTAMP DEFAULT NOW()
);

-- Example templates for Saudi GRC:
INSERT INTO report_templates (template_code, template_name_en, template_name_ar, category, output_formats, parameters)
VALUES
    ('nca_ecc_gap', 'NCA ECC Gap Analysis', 'تحليل فجوات ECC', 'compliance', 
     '["pdf", "excel"]', 
     '{"framework": "nca_ecc", "include_evidence": true}'),
    
    ('nca_ccc_gap', 'NCA CCC Gap Analysis', 'تحليل فجوات CCC', 'compliance',
     '["pdf", "excel"]',
     '{"framework": "nca_ccc"}'),
    
    ('pdpl_compliance', 'PDPL Compliance Summary', 'ملخص امتثال PDPL', 'compliance',
     '["pdf"]',
     '{"date_range": "required"}'),
    
    ('evidence_register', 'Evidence Register', 'سجل الأدلة', 'evidence',
     '["excel", "csv"]',
     '{"status": "all", "date_range": "optional"}'),
    
    ('risk_register', 'Risk Register', 'سجل المخاطر', 'risk',
     '["excel", "pdf"]',
     '{"risk_level": "all", "include_mitigations": true}'),
    
    ('control_effectiveness', 'Control Effectiveness Report', 'تقرير فعالية الضوابط', 'compliance',
     '["pdf"]',
     '{"framework": "required", "department": "optional"}'),
    
    ('assessment_summary', 'Assessment Executive Summary', 'ملخص التقييمات', 'audit',
     '["pdf"]',
     '{"assessment_id": "required"}'),
    
    ('findings_remediation', 'Findings Remediation Status', 'حالة معالجة النتائج', 'audit',
     '["excel"]',
     '{"status": "open", "priority": "all"}'),
    
    ('audit_trail', 'System Audit Trail', 'سجل التدقيق', 'audit',
     '["excel", "csv"]',
     '{"date_range": "required", "user": "optional", "action_type": "optional"}'),
    
    ('compliance_scorecard', 'Compliance Scorecard', 'بطاقة الامتثال', 'compliance',
     '["pdf"]',
     '{"frameworks": ["nca_ecc", "nca_ccc", "pdpl"], "date": "required"}');
```

**User UI Required:**
```
Location: /reports

Page Layout:
┌─────────────────────────────────────────────────┐
│ Reports                                         │
│                                                 │
│ Category: [All ▼]  Search: [________]          │
│                                                 │
│ Compliance Reports:                             │
│                                                 │
│ ┌──────────────────────────────────────────┐   │
│ │ 📊 NCA ECC Gap Analysis                  │   │
│ │    Identify compliance gaps vs NCA ECC   │   │
│ │    Formats: PDF • Excel                  │   │
│ │    [Generate Report]                     │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ ┌──────────────────────────────────────────┐   │
│ │ 📊 PDPL Compliance Summary               │   │
│ │    SDAIA PDPL compliance status          │   │
│ │    Formats: PDF                          │   │
│ │    [Generate Report]                     │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ Evidence Reports:                               │
│                                                 │
│ ┌──────────────────────────────────────────┐   │
│ │ 📋 Evidence Register                     │   │
│ │    Complete evidence inventory           │   │
│ │    Formats: Excel • CSV                  │   │
│ │    [Generate Report]                     │   │
│ └──────────────────────────────────────────┘   │
│                                                 │
│ Recent Reports:                                 │
│ • NCA ECC Gap - Generated 2 hours ago [View]   │
│ • Evidence Register - Generated Mar 4 [View]   │
└─────────────────────────────────────────────────┘

Generate Report Dialog:
┌─────────────────────────────────────────────────┐
│ Generate: NCA ECC Gap Analysis                  │
│                                                 │
│ Parameters:                                     │
│                                                 │
│ Framework: ● NCA ECC v3.0                       │
│                                                 │
│ Include Evidence: ☑ Yes ☐ No                    │
│                                                 │
│ Output Format: ● PDF  ○ Excel                   │
│                                                 │
│ [Cancel]  [Generate Report]                     │
└─────────────────────────────────────────────────┘
```

**Backend API:**
```python
# reporting/router.py

@router.get("/report-templates")
async def list_templates(category: Optional[str] = None):
    """Get available report templates."""
    # Query report_templates WHERE category = ? or all
    return templates

@router.post("/reports/generate")
async def generate_report(
    template_code: str,
    parameters: Dict[str, Any],
    output_format: str,  # 'pdf', 'excel', 'csv'
    current_user: User = Depends(get_current_user)
):
    """Generate a report from template."""
    # 1. Get template definition
    # 2. Execute query with parameters
    # 3. Generate file (PDF via ReportLab, Excel via openpyxl)
    # 4. Save to report_history
    # 5. Return file URL or stream
    
    # Example for NCA ECC Gap Analysis:
    if template_code == 'nca_ecc_gap':
        # Query controls mapped to NCA ECC
        # Group by domain/control family
        # Calculate compliance % per domain
        # Generate PDF:
        #   - Cover page (logo, title, date, generated by)
        #   - Executive summary (overall compliance %)
        #   - Domain breakdown (table)
        #   - Gap details (controls missing evidence)
        #   - Recommendations
        
        pdf_path = await generate_nca_gap_pdf(data, parameters)
        return {"report_url": f"/reports/download/{report_id}"}

@router.get("/reports/download/{report_id}")
async def download_report(report_id: int):
    """Download generated report file."""
    # Get file_path from report_history
    # Stream file
    pass

@router.get("/reports/history")
async def get_report_history(current_user: User):
    """Get user's report generation history."""
    # Query report_history WHERE generated_by = user_id
    return reports
```

**Report Generation Libraries:**
```python
# requirements.txt additions
reportlab==4.0.7     # PDF generation
openpyxl==3.1.2      # Excel generation
jinja2==3.1.3        # Template rendering
weasyprint==60.2     # Alternative HTML→PDF
```

**Example PDF Template (NCA ECC Gap Analysis):**
```python
# reporting/templates/nca_ecc_gap.py
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.lib.styles import getSampleStyleSheet

async def generate_nca_gap_pdf(data, params):
    """Generate NCA ECC Gap Analysis PDF."""
    
    # Create PDF
    pdf = SimpleDocTemplate("nca_ecc_gap.pdf", pagesize=A4)
    story = []
    
    # Cover Page
    story.append(Paragraph("NCA ECC Gap Analysis Report", styles['Heading1']))
    story.append(Paragraph(f"Generated: {datetime.now()}", styles['Normal']))
    story.append(Paragraph(f"Framework: NCA ECC v3.0", styles['Normal']))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    story.append(Paragraph(f"Overall Compliance: {data['compliance_pct']}%", styles['Normal']))
    story.append(Paragraph(f"Controls Implemented: {data['implemented']}/{data['total']}", styles['Normal']))
    
    # Domain Breakdown Table
    story.append(Paragraph("Domain-Level Compliance", styles['Heading2']))
    table_data = [["Domain", "Total Controls", "Implemented", "% Complete"]]
    for domain in data['domains']:
        table_data.append([
            domain['name_en'],
            domain['total_controls'],
            domain['implemented_controls'],
            f"{domain['compliance_pct']}%"
        ])
    story.append(Table(table_data))
    
    # Gap Details
    story.append(Paragraph("Control Gaps (Requiring Attention)", styles['Heading2']))
    for gap in data['gaps']:
        story.append(Paragraph(f"• {gap['control_id']}: {gap['control_name']}", styles['Normal']))
        story.append(Paragraph(f"  Status: {gap['status']}", styles['Indent']))
        story.append(Paragraph(f"  Evidence: {gap['evidence_status']}", styles['Indent']))
    
    # Build PDF
    pdf.build(story)
    return "nca_ecc_gap.pdf"
```

**Effort Estimate:** 4-5 weeks (2 developers)

---

## 📊 GAP SUMMARY: SICO vs JIRA MODEL

### **Overall Comparison Matrix**

| Capability Layer | Jira Model | SICO Current | Gap | Effort |
|------------------|------------|--------------|-----|--------|
| **1. Core Entities** | Fixed | ✅ Fixed | ✅ NO GAP | 0 weeks |
| **2. Page/UI Configuration** | Database-driven | ❌ Hardcoded TSX | 🔴 **BLOCKING** | 6-8 weeks |
| **3. Custom Fields** | Configurable | ❌ Hardcoded | 🔴 CRITICAL | 3-4 weeks |
| **4. Workflow States** | Configurable | ❌ Hardcoded | 🔴 CRITICAL | 4-5 weeks |
| **5. Dashboard Widgets** | Configurable | ❌ Hardcoded | 🔴 CRITICAL | 3-4 weeks |
| **6. Report Templates** | Library (50+) | ❌ Export broken | 🔴 CRITICAL | 4-5 weeks |
| **7. Business Rules** | Basic triggers | ❌ None | 🟡 MEDIUM | 2-3 weeks |
| **8. Integration APIs** | ✅ REST APIs | ✅ Good | ✅ NO GAP | 0 weeks |
| **9. User Permissions** | ✅ Role-based | ✅ Good | ✅ NO GAP | 0 weeks |

### **Total Effort to Achieve Jira-Model Configurability:**

**Phase 0: FOUNDATION (Weeks 1-8)** ⚠️ **MUST DO FIRST**
- Database-Driven UI Rendering: 6-8 weeks
  - Generic page renderer (replaces all hardcoded pages)
  - UI configuration tables (ui_pages, ui_sections, ui_field_placements)
  - Admin UI for page configuration
  - Migration of existing pages to config

**Phase 1: Critical Configurability (Weeks 9-16)**
- Custom Fields System: 3-4 weeks
- Workflow States: 4-5 weeks

**Phase 2: High Priority (Weeks 17-24)**
- Dashboard Widgets: 3-4 weeks
- Report Templates: 4-5 weeks

**Phase 3: Nice-to-Have (Weeks 25-28)**
- Business Rules Engine: 2-3 weeks

**Total: 26-30 weeks (6-7 months) with 2 developers**

**Investment: $450K-550K USD**

**CRITICAL NOTE:** Phase 0 (Database-Driven UI) is MANDATORY. Without it, all other configurability features are pointless because:
- Adding custom fields won't help if forms are hardcoded
- Workflow states won't work if pages are hardcoded
- Dashboard widgets won't matter if dashboard is hardcoded

**This is the single biggest gap preventing SICO from being a professional GRC platform.**

---

## 🎯 SICO-SPECIFIC ADVANTAGES (Leveraging Saudi Focus)

### What Makes SICO Different from Jira

Jira is generic project management → customizable to any workflow.

SICO should be **Saudi GRC-specific** → customizable within GRC domain.

### **Pre-Loaded Saudi Content (Out-of-Box Value)**

| Asset | Quantity | Value Proposition |
|-------|----------|-------------------|
| **NCA ECC Controls** | 114 controls | Pre-loaded, Arabic/English |
| **NCA CCC Controls** | 132 controls | Pre-loaded, Arabic/English |
| **PDPL Articles** | 56 articles | Mapped to controls |
| **ISO 27001 Controls** | 93 controls | International standard |
| **SAMA Framework** | Coming Soon | For banking sector |
| **CITC Framework** | Coming Soon | For telecom |
| **Control Mappings** | 500+ mappings | NCA↔ISO↔CCC cross-references |
| **Report Templates** | 10 Saudi-specific | NCA Gap, PDPL Summary, etc. |
| **Workflow Templates** | 5 templates | Evidence approval, Risk treatment |

### **Saudi-Specific Features (Unique Differentiators)**

Unlike Jira (generic) or ServiceNow (global), SICO can have:

1. **Arabic-First UX**
   - Not just translation, but RTL-native design
   - Arabic technical terms (not transliterated English)
   - Arabic date formats (Hijri calendar support)

2. **NCA Report Formats**
   - PDF templates matching NCA submission requirements
   - Pre-filled templates for NCA audits
   - Arabic official document formats

3. **Saudi Calendar Integration**
   - Hijri date support
   - Saudi working days (Sun-Thu)
   - Saudi holidays calendar

4. **Local Compliance Workflows**
   - SDAIA PDPL breach notification (72-hour SLA)
   - NCA incident reporting workflow
   - SAMA regulatory reporting

5. **Saudi Market Templates**
   - Banking sector (SAMA regulations)
   - Healthcare sector (MOH + SDAIA)
   - Government sector (YESSER + NCA)
   - Telecom (CITC)

### **Positioning Statement**

**Jira:** "Flexible project management for any team"  
**ServiceNow GRC:** "Enterprise GRC platform for global compliance"  
**SICO GRC:** "The ONLY platform purpose-built for Saudi NCA/SAMA/SDAIA compliance with smart configurability"

---

## 🚀 RECOMMENDED ROADMAP (REVISED)

### **Phase 0: ARCHITECTURAL FOUNDATION (Months 1-2)** ⚠️ **MANDATORY FIRST**

**Goal:** Replace hardcoded pages with database-driven UI

**Deliverables:**
1. ✅ Database schema for UI configuration (ui_pages, ui_sections, ui_field_placements, ui_list_configs)
2. ✅ Generic page renderer components (DynamicPage, DetailPageRenderer, ListPageRenderer, FormPageRenderer)
3. ✅ Admin UI for page configuration
4. ✅ Migration of all existing pages to database-driven config
5. ✅ Dynamic field rendering system

**Effort:** 6-8 weeks, 2 developers, $120K-160K

**Result:** All pages render from database configuration, not hardcoded React

**WHY THIS MUST BE FIRST:**
- Without this, custom fields are useless (can't add to hardcoded forms)
- Without this, workflows won't work (state changes hardcoded in pages)
- Without this, dashboards can't be customized
- This is THE fundamental architectural gap

### **Phase 1: Core Configurability (Months 3-5)**

**Goal:** Achieve 70% Jira-model parity

**Deliverables:**
1. ✅ Custom fields system (add fields via UI) - builds on Phase 0
2. ✅ Workflow state customization (add 1-3 states)
3. ✅ Dashboard widget selector (choose from 15 widgets)
4. ✅ Export functionality (PDF/Excel for all reports)

**Effort:** 12-14 weeks, 2 developers, $230K-280K

**Result:** Can customize to most client needs without code changes

### **Phase 2: Saudi Templates (Month 5)**

**Goal:** Pre-load all Saudi content

**Deliverables:**
1. ✅ 10 Saudi-specific report templates
2. ✅ NCA/PDPL/ISO frameworks fully loaded
3. ✅ Control mappings (NCA↔ISO)
4. ✅ Arabic report templates
5. ✅ Saudi workflow templates

**Effort:** 4 weeks, 1 developer, $40K

**Result:** Works out-of-box for Saudi clients

### **Phase 3: Advanced Features (Month 6-7)**

**Goal:** Polish and differentiation

**Deliverables:**
1. ✅ Business rule engine (basic)
2. ✅ Scheduled reports
3. ✅ Bulk operations (all modules)
4. ✅ Gap analysis feature
5. ✅ Control→Risk→Evidence mapping UI

**Effort:** 8 weeks, 2 developers, $120K

**Result:** Feature-complete for mid-market

### **Phase 4: Go-to-Market (Month 8-9)**

**Goal:** Pilot deployments

**Deliverables:**
1. ✅ Onboarding wizard (guided setup)
2. ✅ Training materials (video tutorials)
3. ✅ Documentation (admin guide, user guide)
4. ✅ 3 pilot clients (banking, healthcare, gov)

**Effort:** 8 weeks, 2 developers, $120K

**Total: 10-11 months, $610K investment, 75% competitive with ServiceNow, 120% for Saudi market**

**CRITICAL PATH:**
```
Month 1-2: Database-Driven UI (FOUNDATION) ← MUST COMPLETE FIRST
Month 3-5: Configurability Layer (builds on foundation)
Month 6: Saudi Templates (leverages configurable UI)
Month 7-8: Advanced Features
Month 9-11: Polish & Pilots
```

---

## 📊 SUCCESS METRICS

### **How to Measure Jira-Model Achievement**

| Metric | Jira Standard | SICO Target | Current |
|--------|--------------|-------------|---------|
| **Pages Rendered from DB** | 100% | 100% | ❌ 0% (all hardcoded) |
| **Time to Add Custom Field** | 2 min | 5 min | ❌ 1 week |
| **Time to Add Workflow State** | 5 min | 10 min | ❌ 1 week |
| **Time to Customize Dashboard** | 10 min | 15 min | ❌ Not possible |
| **Time to Reorder Form Fields** | 30 sec (drag-drop) | 1 min | ❌ 1 day (edit code) |
| **Time to Generate Report** | 1 min | 1 min | ❌ Not working |
| **Client Onboarding Time** | 2-4 weeks | 3-6 weeks | ❌ 2-3 months |
| **Code Deploys per Client** | 0-1 | 0-2 | ❌ 5-10 |
| **% Customization via UI** | 80% | 60% | ❌ 5% |

### **Target State (After 10-11 months)**

| Metric | Target | Impact |
|--------|--------|--------|
| **Pages Rendered from DB** | ✅ 100% | All pages configurable via admin UI |
| **Time to Add Custom Field** | ✅ 5 min | Admin can do it |
| **Time to Add Workflow State** | ✅ 10 min | No developer needed |
| **Time to Customize Dashboard** | ✅ 15 min | Select from widget library |
| **Time to Reorder Form Fields** | ✅ 1 min | Drag-drop in page config |
| **Time to Generate Report** | ✅ 1 min | PDF/Excel export works |
| **Client Onboarding Time** | ✅ 3-6 weeks | Pre-loaded NCA content |
| **Code Deploys per Client** | ✅ 0-1 | Config changes only |
| **% Customization via UI** | ✅ 60% | Most needs met without code |

---

## ✅ FINAL RECOMMENDATIONS

### **Strategic Decision: HYBRID MODEL (Jira-Style) with Database-Driven UI**

**Why This is the RIGHT approach for SICO:**

1. ✅ **Achievable:** 10-11 months, $610K (not 24 months, $1M+)
2. ✅ **Defensible:** Saudi content + smart config = moat
3. ✅ **Scalable:** Can onboard 10+ clients without code changes
4. ✅ **Marketable:** "Works Day 1, customized Week 3"
5. ✅ **Realistic:** Don't compete with ServiceNow on full configurability
6. ✅ **Foundation-First:** Database-driven UI is mandatory (Months 1-2)

### **CRITICAL: The Architecture Must Change FIRST**

**You CANNOT skip Phase 0 (Database-Driven UI).** Here's why:

| If you skip Phase 0... | What happens... |
|------------------------|-----------------|
| Add custom fields feature | Fields have nowhere to appear (forms are hardcoded) |
| Add workflow states | State changes don't work (pages hardcoded) |
| Add dashboard widgets | Widgets can't be arranged (dashboard hardcoded) |
| Build report designer | Reports can't be customized (layouts hardcoded) |

**The hardcoded pages are THE bottleneck. Everything else depends on fixing this first.**

### **What Success Looks Like (After Phase 0 + Phase 1)**

**Scenario: New Client (Saudi Bank) Onboarding**

**Day 1:** Deploy SICO platform  
**Day 2:** NCA ECC/CCC + SAMA frameworks auto-loaded (no data entry)  
**Week 1:** Admin opens page configuration UI
- Adds "Branch Code" field to Evidence form (dropdown with 50 branches) - 5 minutes
- Adds "SAMA Audit Reference" field to Control detail page - 3 minutes  
- Adds "CFO Approval Date" field to Risk assessment - 3 minutes
- Total: 11 minutes, no developer involvement ✅  

**Week 2:** Admin customizes workflows
- Adds "SAMA Approval" state to evidence workflow - 10 minutes
- Adds "Board Review" state to high-risk findings - 8 minutes
- Total: 18 minutes, no code changes ✅

**Week 3:** Admin customizes dashboards  
- Selects 8 widgets from library (compliance score, risk heatmap, SAMA gaps, etc.) - 20 minutes
- Hides "PDPL Compliance" widget (not applicable to banking) - 2 minutes
- Total: 22 minutes ✅

**Week 4:** Admin generates reports
- NCA Gap Analysis report - PDF ready in 2 minutes ✅  
- SAMA Compliance Summary - customized template - 5 minutes ✅

**Week 5:** Admin customizes page layouts
- Reorders fields on Evidence form (move "Branch Code" to top) - 2 minutes
- Adds new tab "Internal Audit Notes" to Control detail page - 5 minutes
- Hides "External Reference" field for Analyst role - 3 minutes
- Total: 10 minutes ✅

**Week 6:** Go live with fully customized platform
- ✅ 5 custom fields added
- ✅ 2 workflow states added
- ✅ Dashboard personalized (8 widgets)
- ✅ 2 reports configured
- ✅ Page layouts adjusted
- ✅ **ZERO code changes**
- ✅ **ZERO developer time**

**Total onboarding time: 6 weeks**  
**Developer involvement: 0 hours** (Platform ops only)  
**Customization time: 71 minutes total** (all via admin UI)  
**Client satisfaction: Very High** (NCA-ready + customized without waiting for dev cycles)

### **Competitive Position After Implementation**

| Platform | Configurability | Saudi Content | Price | Sweet Spot |
|----------|----------------|---------------|-------|------------|
| ServiceNow GRC | 95% | 40% | $$$$$ | Enterprise Global |
| RSA Archer | 90% | 30% | $$$$ | Large Orgs |
| **SICO GRC (Hybrid)** | **60%** | **95%** | **$$** | **Saudi Mid-Market** ✅ |

**Market Position:** "Not the most configurable, but the BEST for Saudi compliance"

---

## 📝 APPENDIX: IMPLEMENTATION CHECKLIST

### **Phase 0: Database-Driven UI Foundation (Month 1-2)** ⚠️ CRITICAL
- [ ] Database schema design
  - [ ] ui_pages table
  - [ ] ui_sections table
  - [ ] ui_field_placements table
  - [ ] ui_list_configs table
- [ ] Generic page renderer components
  - [ ] DynamicPage component (main router)
  - [ ] DetailPageRenderer (tab-based detail views)
  - [ ] ListPageRenderer (data tables)
  - [ ] FormPageRenderer (create/edit forms)
  - [ ] DashboardPageRenderer (widget-based dashboards)
- [ ] Dynamic field rendering
  - [ ] DynamicField component (renders any field type)
  - [ ] Support for 15+ field types (text, textarea, select, date, file, user, etc.)
  - [ ] Field validation system
  - [ ] Conditional visibility rules
- [ ] Admin UI for page configuration
  - [ ] Page list and editor
  - [ ] Section management (add/remove/reorder tabs)
  - [ ] Field placement UI (add fields, drag-drop reorder)
  - [ ] List column configuration
- [ ] Migration tools
  - [ ] Script to convert existing Evidence page → DB config
  - [ ] Script to convert existing Control page → DB config
  - [ ] Script to convert existing Risk page → DB config
  - [ ] Script to convert existing Assessment page → DB config
  - [ ] Script to convert existing Dashboard → widget config
- [ ] Replace all hardcoded pages
  - [ ] Replace evidence/upload/page.tsx with <DynamicPage>
  - [ ] Replace controls/[id]/page.tsx with <DynamicPage>
  - [ ] Replace risks/page.tsx with <DynamicPage>
  - [ ] Replace assessments/[id]/page.tsx with <DynamicPage>
  - [ ] Replace dashboard/page.tsx with <DynamicPage>
- [ ] Testing
  - [ ] Test all entity pages render correctly from config
  - [ ] Test admin can add/remove fields
  - [ ] Test custom field values save correctly
  - [ ] Performance testing (config lookup overhead)

### **Month 1-2: Custom Fields**
- [ ] Database schema (custom_field_definitions, custom_field_values)
- [ ] Backend API (/custom-fields endpoints)
- [ ] Admin UI (field creation form)
- [ ] Frontend renderer (display custom fields in entity forms)
- [ ] Migration tool (existing fields → custom fields)

### **Month 2-3: Workflow States**
- [ ] Database schema (workflow_definitions, workflow_states, workflow_transitions)
- [ ] Backend API (/workflows endpoints)
- [ ] Admin UI (workflow designer - simple version)
- [ ] Update existing routers (dynamic state validation)
- [ ] Migration tool (existing enums → workflow states)

### **Month 3-4: Dashboard Widgets**
- [ ] Database schema (widget_library, user_dashboards, dashboard_widgets)
- [ ] Widget library (15 pre-built widgets)
- [ ] Backend API (/dashboards endpoints)
- [ ] User UI (widget selector + preview)
- [ ] Dynamic dashboard renderer

### **Month 4-5: Report Templates**
- [ ] Database schema (report_templates, report_history)
- [ ] Report generators (PDF/Excel for 10 templates)
- [ ] Backend API (/reports/generate)
- [ ] User UI (report gallery + parameter inputs)
- [ ] File storage (S3 or local)

### **Month 5: Saudi Content**
- [ ] Load all NCA frameworks (ECC, CCC)
- [ ] Load PDPL articles
- [ ] Load ISO 27001 controls
- [ ] Create control mappings (NCA↔ISO)
- [ ] Create 10 Saudi report templates
- [ ] Arabic translations (all reports)

### **Month 6-7: Advanced Features**
- [ ] Business rule engine (basic if-then)
- [ ] Scheduled reports (cron jobs)
- [ ] Bulk operations (evidence approve, control assign)
- [ ] Gap analysis (compare org vs framework)
- [ ] Mapping UI (control→risk→evidence)

### **Month 8-9: Polish & Pilots**
- [ ] Onboarding wizard
- [ ] Video tutorials (10 videos)
- [ ] Admin documentation (100 pages)
- [ ] User documentation (50 pages)
- [ ] 3 pilot deployments
- [ ] Feedback collection
- [ ] Bug fixes

---

**Document Status:** STRATEGIC ROADMAP  
**Next Steps:** Secure budget approval + assign development team  
**Success Criteria:** Deploy to first pilot client within 9 months  
**Contact:** GitHub @sonaiso/sanadcom
