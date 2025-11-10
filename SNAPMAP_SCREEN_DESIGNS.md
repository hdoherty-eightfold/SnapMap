# SnapMap Screen-by-Screen Design Specifications
## Eightfold.ai Branded Interface Mockups

**Document Version:** 1.0
**Last Updated:** November 7, 2025
**Companion to:** EIGHTFOLD_UI_REBRANDING_GUIDE.md

---

## Table of Contents

1. [Dashboard/Upload Screen](#dashboardupload-screen)
2. [Field Mapping Interface](#field-mapping-interface)
3. [Review & Validate Screen](#review--validate-screen)
4. [CSV Preview](#csv-preview)
5. [XML Preview](#xml-preview)
6. [SFTP Upload](#sftp-upload)
7. [Settings Panel](#settings-panel)
8. [Navigation Components](#navigation-components)

---

## Dashboard/Upload Screen

### Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│ SIDEBAR (256px)          │ MAIN CONTENT AREA                    │
│                          │                                       │
│ [Logo: SnapMap]          │ TOP BAR (64px height)                │
│ HR Data Transformer      │ ┌──────────────────────────────────┐ │
│                          │ │ Breadcrumb: Home > Upload        │ │
│ ┌─────────────────────┐  │ │                      [Dark Mode] │ │
│ │ WORKFLOW            │  │ └──────────────────────────────────┘ │
│ ├─────────────────────┤  │                                       │
│ │ ▶ Upload [Active]   │  │ CONTENT (padding: 32px)              │
│ │   Map Fields        │  │ ┌──────────────────────────────────┐ │
│ │   Review & Validate │  │ │ HERO CARD (gradient background)  │ │
│ │   Preview CSV       │  │ │                                  │ │
│ │   Preview XML       │  │ │   [Icon: Sparkles] 48px         │ │
│ │   SFTP Upload       │  │ │                                  │ │
│ │   Settings          │  │ │   Upload Your Data               │ │
│ └─────────────────────┘  │ │   Transform HR data from any     │ │
│                          │ │   system to Eightfold format     │ │
│ ┌─────────────────────┐  │ │                                  │ │
│ │ [Dark Mode]         │  │ │   Entity Type: [Employee ▼]     │ │
│ │ [Start Over]        │  │ │                                  │ │
│ └─────────────────────┘  │ │   ┌──────────────────────────┐  │ │
│                          │ │   │ UPLOAD ZONE (dashed)     │  │ │
│ Progress:                │ │   │                          │  │ │
│ File: ✗ No               │ │   │  [Upload Icon] 64px      │  │ │
│ Mapped: ✗ None           │ │   │                          │  │ │
│                          │ │   │  Drop files here or      │  │ │
│ v1.0.0                   │ │   │  [Browse Files]          │  │ │
│ Eightfold AI 🚀          │ │   │                          │  │ │
│                          │ │   │  Supports CSV, Excel     │  │ │
└──────────────────────────┘ │   └──────────────────────────┘  │ │
                             │                                  │ │
                             │   [Try Sample Data ▼]           │ │
                             │                                  │ │
                             └──────────────────────────────────┘ │
                             │                                     │
                             │ TIP CARD (teal accent border)       │
                             │ 💡 Getting Started                  │
                             │ Upload CSV or Excel files up to...  │
                             └─────────────────────────────────────┘
```

### Design Specifications

#### Hero Card
```css
{
  background: linear-gradient(135deg, #191841 0%, #5741dc 100%);
  border-radius: 12px;
  padding: 48px 40px;
  color: white;
  max-width: 900px;
  margin: 0 auto;
}
```

**Typography:**
- Title: 2.5rem (40px), font-weight: 700, Gilroy
- Subtitle: 1.125rem (18px), font-weight: 400, opacity: 0.9
- Spacing: 16px between title and subtitle

#### Entity Type Selector
```css
{
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(136, 226, 210, 0.3);
  border-radius: 8px;
  padding: 12px 16px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
}
```

**Label:**
- "📋 Select Entity Type"
- Font-size: 0.875rem, font-weight: 600
- Color: rgba(255, 255, 255, 0.9)
- Badge: "AI POWERED" in teal with 20% opacity background

#### Upload Zone
```css
{
  border: 2px dashed rgba(136, 226, 210, 0.5);
  border-radius: 12px;
  padding: 64px 32px;
  background: rgba(255, 255, 255, 0.05);
  text-align: center;
  transition: all 0.3s cubic-bezier(0.87, 0, 0.13, 1);
}

/* Hover State */
:hover {
  border-color: #88e2d2;
  background: rgba(136, 226, 210, 0.1);
  transform: scale(1.01);
}

/* Dragging State */
.dragging {
  border-color: #88e2d2;
  background: rgba(136, 226, 210, 0.15);
  transform: scale(1.02);
  box-shadow: 0 0 24px rgba(136, 226, 210, 0.3);
}
```

**Upload Icon:**
- Size: 64px
- Color: #88e2d2
- Background circle: rgba(136, 226, 210, 0.1), 96px diameter

**Text:**
- "Drop your file here, or browse"
- Font-size: 1.125rem, font-weight: 500
- "browse" in teal color (#88e2d2)

**Button:**
- Style: Primary teal button
- Text: "Browse Files"
- Icon: File icon (lucide-react)

#### Sample Data Dropdown
```css
{
  width: 100%;
  padding: 12px 24px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(136, 226, 210, 0.3);
  border-radius: 8px;
  color: white;
  font-weight: 500;
  margin-top: 16px;
}
```

#### Tip Card (Below Hero)
```css
{
  background: rgba(136, 226, 210, 0.1);
  border: 1px solid rgba(136, 226, 210, 0.3);
  border-radius: 12px;
  padding: 16px 20px;
  margin-top: 24px;
  display: flex;
  gap: 12px;
}
```

**Icon:** 💡 (24px)
**Title:** "Getting Started" - font-weight: 600, color: white
**Text:** font-size: 0.875rem, color: rgba(255, 255, 255, 0.8)

---

## Field Mapping Interface

### Layout Structure

```
┌──────────────────────────────────────────────────────────────────┐
│ HEADER (with gradient background)                                │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Field Mapping                                [Auto-Map] [→]  │ │
│ │ Map your source fields to Eightfold employee schema          │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ STATS BAR (teal accent)                                            │
│ ┌─────────┬─────────┬─────────┬─────────┐                        │
│ │ 45/50   │ 12      │ 3       │ 90%     │                        │
│ │ Mapped  │ AI      │ Manual  │ Match   │                        │
│ └─────────┴─────────┴─────────┴─────────┘                        │
│                                                                    │
│ MAPPING INTERFACE (2-column with connecting lines)                │
│ ┌─────────────────────┐          ┌─────────────────────┐         │
│ │ SOURCE FIELDS       │ ──────→ │ TARGET FIELDS       │         │
│ ├─────────────────────┤          ├─────────────────────┤         │
│ │ □ First Name    [✓] │ ═══════► │ firstName [90%]    │         │
│ │ □ Last Name     [✓] │ ═══════► │ lastName [95%]     │         │
│ │ □ Email         [✓] │ ═══════► │ email [99%]        │         │
│ │ □ Start_Date    [⚠] │ ········► │ hireDate [60%]     │         │
│ │ □ Department    [ ] │          │ department [empty] │         │
│ │ □ Position      [✓] │ ═══════► │ jobTitle [85%]     │         │
│ │                     │          │                     │         │
│ │ [+ Add Custom]      │          │ [Show All: 50]     │         │
│ └─────────────────────┘          └─────────────────────┘         │
│                                                                    │
│ PREVIEW PANEL (bottom drawer, collapsible)                        │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Sample Preview (first 5 rows)                  [Expand ▲]   │ │
│ │ ┌─────────────┬──────────────┬──────────────┐               │ │
│ │ │ firstName   │ lastName     │ email        │               │ │
│ │ ├─────────────┼──────────────┼──────────────┤               │ │
│ │ │ John        │ Smith        │ john@...     │               │ │
│ │ │ Jane        │ Doe          │ jane@...     │               │ │
│ └─────────────┴──────────────┴──────────────┘               │ │
│ └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

### Design Specifications

#### Header Card
```css
{
  background: linear-gradient(135deg, #88e2d2 0%, #5741dc 50%, #0708ee 100%);
  padding: 32px 40px;
  border-radius: 12px 12px 0 0;
  color: white;
}
```

**Title:** 2rem (32px), font-weight: 700
**Subtitle:** 1rem (16px), font-weight: 400, opacity: 0.95

**Auto-Map Button:**
```css
{
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(8px);
  color: white;
  padding: 10px 32px;
  border-radius: 112px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  font-weight: 600;
}
```

#### Stats Bar
```css
.stat-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  flex: 1;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #88e2d2;
  line-height: 1;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-top: 8px;
}
```

#### Field Cards

**Source Field (Unmapped)**
```css
{
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

:hover {
  border-color: #88e2d2;
  background: rgba(136, 226, 210, 0.05);
  transform: translateX(4px);
}
```

**Source Field (Mapped - High Confidence)**
```css
{
  background: rgba(136, 226, 210, 0.1);
  border: 2px solid #88e2d2;
  border-radius: 8px;
}
```

**Source Field (Mapped - Low Confidence)**
```css
{
  background: rgba(251, 191, 36, 0.1);
  border: 2px solid #fbbf24;
  border-radius: 8px;
}
```

**Confidence Badge:**
```css
.badge-high {
  background: rgba(136, 226, 210, 0.2);
  color: #1d6259;
  padding: 4px 12px;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 600;
  border: 1px solid #88e2d2;
}

.badge-medium {
  background: rgba(251, 191, 36, 0.2);
  color: #92400e;
  border: 1px solid #fbbf24;
}

.badge-ai {
  background: linear-gradient(90deg, #88e2d2 0%, #5741dc 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 100px;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}
```

#### Connection Lines

**High Confidence (90%+)**
```css
{
  stroke: #88e2d2;
  stroke-width: 3px;
  stroke-dasharray: none;
  filter: drop-shadow(0 0 4px rgba(136, 226, 210, 0.4));
}
```

**Medium Confidence (60-89%)**
```css
{
  stroke: #fbbf24;
  stroke-width: 2px;
  stroke-dasharray: 8 4;
}
```

**Low Confidence (<60%)**
```css
{
  stroke: #9ca3af;
  stroke-width: 1px;
  stroke-dasharray: 4 4;
}
```

#### Target Field Cards
```css
{
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px 16px;
  margin-bottom: 8px;
  position: relative;
}

/* Required field indicator */
.required::before {
  content: '*';
  color: #ef4444;
  font-size: 1.25rem;
  position: absolute;
  left: -12px;
  top: 12px;
}

/* Mapped state */
.mapped {
  border-color: #88e2d2;
  background: rgba(136, 226, 210, 0.05);
}
```

**Field Label:**
- Font-size: 0.875rem
- Font-weight: 600
- Color: #191841
- Monospace font for technical fields

**Field Description:**
- Font-size: 0.75rem
- Color: #6b7280
- Margin-top: 4px

---

## Review & Validate Screen

### Layout Structure

```
┌──────────────────────────────────────────────────────────────────┐
│ HEADER                                                             │
│ Schema Validation                                   [Run Check]   │
│ Review data quality and schema compliance                          │
│                                                                    │
│ VALIDATION SUMMARY (cards in row)                                  │
│ ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│ │ ✓ 45     │  │ ⚠ 3      │  │ ✗ 2      │  │ ○ 1250  │          │
│ │ Passed   │  │ Warnings │  │ Errors   │  │ Rows    │          │
│ └──────────┘  └──────────┘  └──────────┘  └──────────┘          │
│                                                                    │
│ ISSUES LIST (grouped by severity)                                 │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ ERRORS (2) - Must fix before export                          │ │
│ │ ┌────────────────────────────────────────────────────────┐   │ │
│ │ │ ✗ Missing Required Field: "employeeId"                 │   │ │
│ │ │ Location: All rows (1250 affected)                     │   │ │
│ │ │ Solution: Map source field or add default value        │   │ │
│ │ │ [Fix Now]  [Skip]                                      │   │ │
│ │ └────────────────────────────────────────────────────────┘   │ │
│ │                                                              │ │
│ │ ┌────────────────────────────────────────────────────────┐   │ │
│ │ │ ✗ Invalid Date Format: "hireDate"                      │   │ │
│ │ │ Location: Rows 45, 67, 89 (3 affected)                │   │ │
│ │ │ Current: "12-25-2023" | Expected: "2023-12-25"        │   │ │
│ │ │ [Auto-Fix]  [View Rows]  [Ignore]                     │   │ │
│ │ └────────────────────────────────────────────────────────┘   │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ WARNINGS (3) - Recommended fixes                             │ │
│ │ ┌────────────────────────────────────────────────────────┐   │ │
│ │ │ ⚠ Inconsistent Format: "phoneNumber"                   │   │ │
│ │ │ Various formats detected: (555) 123-4567, 555-123-4567 │   │ │
│ │ │ Recommendation: Standardize to E.164 format            │   │ │
│ │ │ [Standardize]  [Leave As-Is]                           │   │ │
│ │ └────────────────────────────────────────────────────────┘   │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ ACTIONS (bottom bar)                                               │
│ [← Back to Mapping]              [Export Anyway]  [Fix & Export]  │
└────────────────────────────────────────────────────────────────────┘
```

### Design Specifications

#### Summary Cards
```css
.validation-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  flex: 1;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.validation-card.success {
  border-color: #10b981;
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(16, 185, 129, 0.1) 100%);
}

.validation-card.warning {
  border-color: #f59e0b;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.05) 0%, rgba(245, 158, 11, 0.1) 100%);
}

.validation-card.error {
  border-color: #ef4444;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.05) 0%, rgba(239, 68, 68, 0.1) 100%);
}
```

**Icon:**
- Size: 48px
- Success: ✓ in green circle
- Warning: ⚠ in orange circle
- Error: ✗ in red circle

**Value:**
- Font-size: 3rem (48px)
- Font-weight: 800
- Color matches severity

**Label:**
- Font-size: 0.875rem
- Font-weight: 600
- Color: #6b7280
- Text-transform: uppercase

#### Issue Cards

**Error Issue**
```css
{
  background: rgba(239, 68, 68, 0.05);
  border-left: 4px solid #ef4444;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 12px;
}
```

**Warning Issue**
```css
{
  background: rgba(245, 158, 11, 0.05);
  border-left: 4px solid #f59e0b;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 12px;
}
```

**Issue Title:**
- Font-size: 1rem (16px)
- Font-weight: 600
- Color: #191841
- Icon (✗ or ⚠) in matching severity color

**Issue Details:**
- Font-size: 0.875rem
- Color: #6b7280
- Line-height: 1.6
- Monospace font for field names and values

**Action Buttons:**
- Primary action: Teal button (e.g., "Fix Now", "Auto-Fix")
- Secondary action: Ghost button (e.g., "Skip", "Ignore")
- Size: Small (sm)

#### Section Headers
```css
{
  font-size: 1.125rem;
  font-weight: 700;
  color: #191841;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 12px 16px;
  background: rgba(136, 226, 210, 0.1);
  border-radius: 8px 8px 0 0;
  margin-bottom: 0;
}
```

---

## CSV Preview

### Layout Structure

```
┌──────────────────────────────────────────────────────────────────┐
│ HEADER                                                             │
│ CSV Preview                                  [Download] [→ XML]   │
│ Review transformed data before export                              │
│                                                                    │
│ FILTER & SEARCH BAR                                                │
│ ┌────────────────────────┐  ┌──────────┐  ┌──────────┐          │
│ │ 🔍 Search fields...    │  │ Filter ▼ │  │ Rows: ▼  │          │
│ └────────────────────────┘  └──────────┘  └──────────┘          │
│                                                                    │
│ DATA TABLE (scrollable, sticky header)                            │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ SELECT │ firstName  │ lastName   │ email          │ hireDate │ │
│ ├──────────────────────────────────────────────────────────────┤ │
│ │   □    │ John       │ Smith      │ john@co.com    │ 2023-01  │ │
│ │   □    │ Jane       │ Doe        │ jane@co.com    │ 2022-06  │ │
│ │   □    │ Michael    │ Johnson    │ mike@co.com    │ 2021-03  │ │
│ │   □    │ Sarah      │ Williams   │ sarah@co.com   │ 2023-08  │ │
│ │   □    │ David      │ Brown      │ david@co.com   │ 2020-11  │ │
│ │   ...  │ ...        │ ...        │ ...            │ ...      │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ PAGINATION                                                         │
│ Showing 1-50 of 1,250 rows       [←] [1] [2] [3] ... [25] [→]   │
│                                                                    │
│ SUMMARY PANEL                                                      │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ 📊 Dataset Summary                                           │ │
│ │ • Total Rows: 1,250                                          │ │
│ │ • Total Columns: 45                                          │ │
│ │ • File Size: 2.4 MB                                          │ │
│ │ • Last Modified: 2025-11-07 10:30 AM                        │ │
│ └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

### Design Specifications

#### Data Table
```css
.data-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 0 15px rgba(34, 31, 32, 0.1);
}

.data-table thead {
  background: linear-gradient(135deg, #191841 0%, #5741dc 100%);
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table th {
  padding: 16px 20px;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: white;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.data-table td {
  padding: 16px 20px;
  font-size: 0.875rem;
  color: #484b58;
  border-bottom: 1px solid #e5e7eb;
  font-family: 'Monaco', 'Courier New', monospace;
}

.data-table tr:hover {
  background: rgba(136, 226, 210, 0.05);
}

/* Alternating row colors */
.data-table tr:nth-child(even) {
  background: rgba(248, 248, 248, 0.5);
}

.data-table tr:nth-child(even):hover {
  background: rgba(136, 226, 210, 0.08);
}
```

#### Search & Filter Bar
```css
.search-input {
  padding: 10px 16px 10px 40px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.875rem;
  width: 100%;
  max-width: 400px;
  background-image: url('data:image/svg+xml,...'); /* Search icon */
  background-position: 12px center;
  background-repeat: no-repeat;
  transition: all 0.2s ease;
}

.search-input:focus {
  border-color: #88e2d2;
  box-shadow: 0 0 0 3px rgba(136, 226, 210, 0.1);
}

.filter-dropdown {
  padding: 10px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  background: white;
  cursor: pointer;
}
```

#### Pagination
```css
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.page-button {
  width: 36px;
  height: 36px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  background: white;
  font-weight: 600;
  font-size: 0.875rem;
  color: #484b58;
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-button:hover {
  border-color: #88e2d2;
  background: rgba(136, 226, 210, 0.1);
  color: #1d6259;
}

.page-button.active {
  background: #88e2d2;
  border-color: #88e2d2;
  color: #191841;
  font-weight: 700;
}
```

#### Summary Panel
```css
{
  background: linear-gradient(135deg, rgba(136, 226, 210, 0.1) 0%, rgba(87, 65, 220, 0.1) 100%);
  border: 1px solid rgba(136, 226, 210, 0.3);
  border-radius: 12px;
  padding: 24px;
  margin-top: 24px;
}
```

**Icon:** 📊 (24px)
**Title:** 1rem, font-weight: 700
**List Items:** 0.875rem, line-height: 2

---

## XML Preview

### Layout Structure

```
┌──────────────────────────────────────────────────────────────────┐
│ HEADER                                                             │
│ XML Preview                             [Download] [→ SFTP]       │
│ Review XML structure before export                                 │
│                                                                    │
│ TOOLBAR                                                            │
│ [Format] [Validate] [Copy]       Syntax: [On] Dark: [Off]        │
│                                                                    │
│ CODE VIEWER (syntax highlighted)                                   │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ 1  <?xml version="1.0" encoding="UTF-8"?>                    │ │
│ │ 2  <employees xmlns="http://eightfold.ai/schema/v1">        │ │
│ │ 3    <employee id="E001">                                    │ │
│ │ 4      <firstName>John</firstName>                           │ │
│ │ 5      <lastName>Smith</lastName>                            │ │
│ │ 6      <email>john@company.com</email>                       │ │
│ │ 7      <hireDate>2023-01-15</hireDate>                       │ │
│ │ 8      <department>                                          │ │
│ │ 9        <code>ENG</code>                                    │ │
│ │ 10       <name>Engineering</name>                            │ │
│ │ 11     </department>                                         │ │
│ │ 12   </employee>                                             │ │
│ │ ...                                                           │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ STATS BAR                                                          │
│ ┌────────────┬────────────┬────────────┬────────────┐            │
│ │ 1,250      │ 45         │ 2.4 MB     │ ✓ Valid    │            │
│ │ Records    │ Fields     │ Size       │ Schema     │            │
│ └────────────┴────────────┴────────────┴────────────┘            │
└────────────────────────────────────────────────────────────────────┘
```

### Design Specifications

#### Code Viewer
```css
.code-viewer {
  background: #1e1e1e;
  border-radius: 12px;
  padding: 24px;
  font-family: 'Monaco', 'Menlo', 'Courier New', monospace;
  font-size: 0.875rem;
  line-height: 1.6;
  color: #d4d4d4;
  overflow-x: auto;
  max-height: 600px;
  overflow-y: auto;
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.3);
}

/* Light Mode */
.code-viewer.light {
  background: #f8f8f8;
  color: #383a42;
  box-shadow: inset 0 0 20px rgba(0, 0, 0, 0.05);
}
```

**Syntax Highlighting (Dark Mode):**
```css
.xml-tag { color: #569cd6; }          /* Blue */
.xml-attribute { color: #9cdcfe; }    /* Light blue */
.xml-value { color: #ce9178; }        /* Orange */
.xml-text { color: #d4d4d4; }         /* Light gray */
.xml-comment { color: #6a9955; }      /* Green */
.line-number {
  color: #858585;
  margin-right: 24px;
  user-select: none;
  min-width: 40px;
  display: inline-block;
  text-align: right;
}
```

#### Toolbar Buttons
```css
.toolbar-button {
  padding: 8px 20px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #484b58;
  cursor: pointer;
  transition: all 0.2s ease;
}

.toolbar-button:hover {
  border-color: #88e2d2;
  background: rgba(136, 226, 210, 0.1);
  color: #1d6259;
}

.toolbar-button.active {
  background: #88e2d2;
  border-color: #88e2d2;
  color: #191841;
}
```

#### Toggle Switches
```css
.toggle {
  width: 48px;
  height: 24px;
  background: #e5e7eb;
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: all 0.3s ease;
}

.toggle.on {
  background: #88e2d2;
}

.toggle-handle {
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: all 0.3s cubic-bezier(0.87, 0, 0.13, 1);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.toggle.on .toggle-handle {
  left: 26px;
}
```

---

## SFTP Upload

### Layout Structure

```
┌──────────────────────────────────────────────────────────────────┐
│ HEADER                                                             │
│ SFTP Upload                                          [← Back]     │
│ Upload transformed files to your SFTP server                       │
│                                                                    │
│ CREDENTIAL SELECTOR                                                │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ 🔐 Select SFTP Credentials                 [+ New Credential] │ │
│ │ ┌────────────────────────────────────────────────────────┐   │ │
│ │ │ Production Server (prod.eightfold.ai)           [Edit] │   │ │
│ │ │ Last used: 2 hours ago                                 │   │ │
│ │ └────────────────────────────────────────────────────────┘   │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ FILE BROWSER (2-column: local + remote)                            │
│ ┌────────────────────────┐    ┌────────────────────────┐         │
│ │ LOCAL FILES            │    │ REMOTE DIRECTORY       │         │
│ │ ┌────────────────────┐ │    │ ┌────────────────────┐ │         │
│ │ │ ☑ employee.xml     │ │    │ │ 📁 /uploads/       │ │         │
│ │ │   2.4 MB           │ │    │ │ 📁 /archive/       │ │         │
│ │ │   Ready            │ │    │ │ 📄 previous.xml    │ │         │
│ │ └────────────────────┘ │    │ └────────────────────┘ │         │
│ └────────────────────────┘    └────────────────────────┘         │
│                                                                    │
│ UPLOAD PROGRESS                                                    │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Uploading: employee.xml                               [◼]    │ │
│ │ ┌────────────────────────────────────────────────────────┐   │ │
│ │ │ ████████████████████████████████░░░░░░░░░░░░  75%     │   │ │
│ │ └────────────────────────────────────────────────────────┘   │ │
│ │ 1.8 MB of 2.4 MB • 45 seconds remaining                    │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ UPLOAD HISTORY                                                     │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ Recent Uploads                                               │ │
│ │ ✓ employee_20251107.xml - 2.4 MB - 10:30 AM - Success      │ │
│ │ ✓ candidate_20251106.xml - 1.8 MB - Yesterday - Success    │ │
│ │ ✗ position_20251105.xml - 0.9 MB - 2 days ago - Failed     │ │
│ └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

### Design Specifications

#### Credential Card
```css
.credential-card {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px 24px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.credential-card:hover {
  border-color: #88e2d2;
  background: rgba(136, 226, 210, 0.05);
  transform: translateX(4px);
}

.credential-card.selected {
  border-color: #88e2d2;
  background: linear-gradient(135deg, rgba(136, 226, 210, 0.1) 0%, rgba(87, 65, 220, 0.05) 100%);
  box-shadow: 0 0 0 3px rgba(136, 226, 210, 0.2);
}
```

**Icon:** 🔐 (20px)
**Title:** 1rem, font-weight: 600, color: #191841
**Subtitle:** 0.75rem, color: #6b7280

#### File Browser

**Column Container:**
```css
{
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 16px;
  height: 300px;
  overflow-y: auto;
}
```

**File Item:**
```css
.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.file-item:hover {
  background: rgba(136, 226, 210, 0.1);
}

.file-item.selected {
  background: rgba(136, 226, 210, 0.15);
  border-left: 3px solid #88e2d2;
}
```

**File Icon:** 24px, color: #88e2d2
**File Name:** 0.875rem, font-weight: 500
**File Size:** 0.75rem, color: #6b7280

#### Progress Bar
```css
.progress-container {
  background: white;
  border: 2px solid #88e2d2;
  border-radius: 12px;
  padding: 24px;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background: #e5e7eb;
  border-radius: 100px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #88e2d2 0%, #5741dc 100%);
  border-radius: 100px;
  transition: width 0.5s ease;
  box-shadow: 0 0 12px rgba(136, 226, 210, 0.5);
}

/* Animated gradient */
.progress-fill {
  background-size: 200% 100%;
  animation: progress-shimmer 2s linear infinite;
}

@keyframes progress-shimmer {
  0% { background-position: 100% 0; }
  100% { background-position: -100% 0; }
}
```

**Progress Text:**
- Filename: 1rem, font-weight: 600
- Stats: 0.875rem, color: #6b7280

#### Upload History

**History Item:**
```css
.history-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  font-size: 0.875rem;
}

.history-item:last-child {
  border-bottom: none;
}

.status-icon.success {
  color: #10b981;
  font-size: 1.25rem;
}

.status-icon.error {
  color: #ef4444;
  font-size: 1.25rem;
}
```

---

## Settings Panel

### Layout Structure

```
┌──────────────────────────────────────────────────────────────────┐
│ HEADER                                                             │
│ Settings                                                           │
│ Configure API keys and preferences                                 │
│                                                                    │
│ TABS                                                               │
│ ┌─────────┬─────────┬─────────┬─────────┐                        │
│ │ API     │ Display │ Data    │ About   │                        │
│ └─────────┴─────────┴─────────┴─────────┘                        │
│                                                                    │
│ TAB CONTENT: API CONFIGURATION                                     │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ 🔑 Google Gemini API Key                                     │ │
│ │ ┌────────────────────────────────────────┐ [Test] [Save]    │ │
│ │ │ ●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●●● │                  │ │
│ │ └────────────────────────────────────────┘                   │ │
│ │ ℹ Required for semantic field mapping features              │ │
│ │                                                              │ │
│ │ Status: ✓ Connected | Last verified: 5 minutes ago          │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ 💾 Vector Database                                           │ │
│ │ ┌────────────────────────────────────────┐                   │ │
│ │ │ ChromaDB (Local) ▼                     │                   │ │
│ │ └────────────────────────────────────────┘                   │ │
│ │ • ChromaDB (Local) - Default                                │ │
│ │ • Pinecone (Cloud) - Requires API key                       │ │
│ │ • Weaviate (Cloud) - Requires API key                       │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                    │
│ TAB CONTENT: DISPLAY PREFERENCES                                   │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ 🎨 Theme                                                     │ │
│ │ ○ Light  ● Dark  ○ Auto                                     │ │
│ │                                                              │ │
│ │ 📏 Density                                                   │ │
│ │ ○ Comfortable  ● Compact  ○ Spacious                        │ │
│ │                                                              │ │
│ │ 🌐 Language                                                  │ │
│ │ English (US) ▼                                              │ │
│ └──────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────┘
```

### Design Specifications

#### Setting Sections
```css
.setting-section {
  background: white;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
}
```

**Section Title:**
```css
{
  font-size: 1.125rem;
  font-weight: 700;
  color: #191841;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}
```

**Icon:** 24px

#### Input Fields

**API Key Input:**
```css
.api-key-input {
  width: 100%;
  padding: 12px 16px;
  font-family: 'Monaco', monospace;
  font-size: 0.875rem;
  background: #f8f8f8;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  letter-spacing: 0.1em;
}

.api-key-input:focus {
  border-color: #88e2d2;
  background: white;
}
```

**Status Indicator:**
```css
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 100px;
  font-size: 0.875rem;
  font-weight: 600;
}

.status-badge.connected {
  background: rgba(16, 185, 129, 0.1);
  color: #059669;
  border: 1px solid #10b981;
}

.status-badge.disconnected {
  background: rgba(239, 68, 68, 0.1);
  color: #b91c1c;
  border: 1px solid #ef4444;
}
```

#### Radio Buttons (Custom)
```css
.radio-group {
  display: flex;
  gap: 24px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.radio-circle {
  width: 20px;
  height: 20px;
  border: 2px solid #e5e7eb;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.radio-option:hover .radio-circle {
  border-color: #88e2d2;
}

.radio-circle.checked {
  border-color: #88e2d2;
  background: white;
}

.radio-circle.checked::after {
  content: '';
  width: 10px;
  height: 10px;
  background: #88e2d2;
  border-radius: 50%;
}

.radio-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #484b58;
}
```

---

## Navigation Components

### Sidebar

```css
.sidebar {
  width: 256px;
  height: 100vh;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  position: fixed;
  left: 0;
  top: 0;
  transition: all 0.3s cubic-bezier(0.87, 0, 0.13, 1);
}

.sidebar.collapsed {
  width: 80px;
}

.dark .sidebar {
  background: #191841;
  border-color: rgba(87, 65, 220, 0.2);
}
```

**Logo Section:**
```css
.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.logo-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #191841;
  background: linear-gradient(135deg, #88e2d2 0%, #5741dc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.logo-subtitle {
  font-size: 0.75rem;
  color: #6b7280;
  margin-top: 4px;
}
```

**Nav Items:**
```css
.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin: 4px 12px;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #484b58;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.nav-item:hover {
  background: rgba(136, 226, 210, 0.1);
  color: #1d6259;
}

.nav-item.active {
  background: linear-gradient(135deg, rgba(136, 226, 210, 0.15) 0%, rgba(87, 65, 220, 0.1) 100%);
  color: #88e2d2;
  font-weight: 600;
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #88e2d2 0%, #5741dc 100%);
  border-radius: 0 4px 4px 0;
}

.nav-item .badge {
  margin-left: auto;
  padding: 2px 8px;
  font-size: 0.65rem;
  border-radius: 100px;
}

.nav-item .badge.done {
  background: rgba(16, 185, 129, 0.15);
  color: #059669;
}
```

### Top Bar

```css
.top-bar {
  height: 64px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: sticky;
  top: 0;
  z-index: 10;
}

.dark .top-bar {
  background: rgba(25, 24, 65, 0.9);
  backdrop-filter: blur(8px);
  border-color: rgba(87, 65, 220, 0.2);
}
```

**Breadcrumb:**
```css
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
}

.breadcrumb-item {
  color: #6b7280;
}

.breadcrumb-item.active {
  color: #191841;
  font-weight: 600;
}

.breadcrumb-separator {
  color: #d1d5db;
}
```

---

## Color Usage Examples

### Example: Upload Screen Color Application

```
BACKGROUND: #f8f8f8 (light gray)
HERO CARD: Gradient #191841 → #5741dc (navy to indigo)
HERO TEXT: white (#ffffff)
UPLOAD ZONE BORDER: #88e2d2 (teal, dashed)
UPLOAD ZONE BG HOVER: rgba(136, 226, 210, 0.1) (teal 10%)
PRIMARY BUTTON: #88e2d2 background, #191841 text
SECONDARY TEXT: #6b7280 (medium gray)
BORDER/DIVIDER: #e5e7eb (light gray)
```

### Example: Field Mapping Color Application

```
HEADER: Gradient #88e2d2 → #5741dc → #0708ee (teal to indigo to blue)
MAPPED FIELD (High): #88e2d2 border, rgba(136, 226, 210, 0.1) background
MAPPED FIELD (Medium): #fbbf24 border, rgba(251, 191, 36, 0.1) background
UNMAPPED FIELD: #e5e7eb border, white background
CONNECTION LINE (High): #88e2d2, 3px solid
CONNECTION LINE (Medium): #fbbf24, 2px dashed
AI BADGE: Gradient #88e2d2 → #5741dc, white text
```

---

## Implementation Priority

### Phase 1: Core Components (Week 1)
1. Update color tokens in Tailwind config
2. Implement Button component with all variants
3. Implement Card component with gradient option
4. Update Typography system (fonts, sizes)

### Phase 2: Navigation (Week 2)
5. Redesign Sidebar with new styles
6. Update Top Bar with breadcrumbs
7. Add smooth transitions and animations

### Phase 3: Main Screens (Week 3-4)
8. Upload screen with gradient hero
9. Field mapping interface with connection lines
10. Review & validate with new issue cards
11. CSV/XML preview with syntax highlighting

### Phase 4: Polish (Week 5)
12. SFTP upload with progress animations
13. Settings panel with custom controls
14. Dark mode refinements
15. Responsive design adjustments

---

## Testing Checklist

- [ ] All colors meet WCAG AA contrast (4.5:1)
- [ ] Gradients render correctly in all browsers
- [ ] Pill buttons maintain shape at different sizes
- [ ] Dark mode switches smoothly
- [ ] Hover states provide clear feedback
- [ ] Focus indicators visible on all elements
- [ ] Animations respect reduced-motion preference
- [ ] Mobile responsive at 320px viewport
- [ ] Touch targets minimum 44x44px
- [ ] Loading states clearly indicate progress

---

## Conclusion

These screen-by-screen specifications provide pixel-perfect guidance for implementing the Eightfold.ai design system in SnapMap. The design balances modern aesthetics with functional requirements, ensuring a professional, cohesive experience throughout the application.

Key visual signatures:
- Gradient headers (navy to indigo to blue)
- Teal as primary accent everywhere
- Pill-shaped buttons (112px radius)
- 12px card radius with generous padding
- White/light backgrounds with gradient heroes
- Monospace fonts for technical content
- Clear visual hierarchy with bold typography

Follow the implementation priority to roll out changes systematically, ensuring each component works correctly before moving to the next phase.
