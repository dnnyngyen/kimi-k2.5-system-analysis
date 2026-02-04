name: pivot-table
description: "Create PivotTables in Excel using the pivot command (pure OpenXML SDK)."
--

<Technology Stack>

**PivotTable Creation**: `pivot` command (pure OpenXML SDK)

**Why Pure OpenXML**:
- The `pivot` command provides stable, tested PivotTable creation
- Agent only needs to pass parameters, no manual code writing required

</Technology Stack>

<Execution Order>

**CRITICAL: Follow this order when adding PivotTable to existing data**

```
1. recheck         → Verify NO formula errors
2. reference-check → Verify NO reference errors
3. inspect         → Get sheet names, data range, headers
4. pivot           → Create PivotTable (MUST run LAST)
5. validate        → Run OpenXML validation (with smart whitelist)
```

**Why this order**:
- PivotTable caches source data at creation time
- Modifying source data after pivot creation does NOT update the pivot
- All data validation MUST complete before creating PivotTable

**About validate step**:
- Validator auto-ignores safe openpyxl schema issues (font ordering, etc.)
- PivotTable errors are **NEVER ignored** - if validate fails on pivot-related errors, you MUST fix them
- Exit code 0 = safe to deliver (even with `pass_with_warnings` status)

</Execution Order>

<Tool: pivot command>

## Usage

```bash
/app/.kimi/skills/xlsx/scripts/KimiXlsx pivot \
    <input.xlsx> <output.xlsx> \
    --source "Sheet!A1:Z100" \
    --location "PivotSheet!A3" \
    --values "Field:sum" \
    [--rows "Field1,Field2"] \
    [--cols "Field1"] \
    [--filters "Field1"] \
    [--name "MyPivotTable"]
```

## Required Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `input.xlsx` | Input Excel file (positional) | `data.xlsx` |
| `output.xlsx` | Output Excel file (positional) | `output.xlsx` |
| `--source` | Source data range | `"Sales!A1:F100"` |
| `--location` | Where to place PivotTable | `"Summary!A3"` |
| `--values` | Value fields with aggregation | `"Revenue:sum,Units:count"` |

## Optional Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--rows` | Row fields (comma-separated) | `"Product,Region"` |
| `--cols` | Column fields (comma-separated) | `"Quarter"` |
| `--filters` | Filter/page fields | `"Year,Department"` |
| `--name` | PivotTable name | `"SalesPivot"` (default: PivotTable1) |
| `--style` | Style theme | `"monochrome"` or `"finance"` |
| `--chart` | Chart type for visualization | `"bar"`, `"line"`, or `"pie"` (default: bar) |

## Chart Options

| Chart Type | Description | Best For |
|------------|-------------|----------|
| `bar` | Clustered column chart | Comparing categories side-by-side (DEFAULT) |
| `line` | Line chart with markers | Showing trends over time/sequence |
| `pie` | Pie chart with percentages | Showing proportions of a whole |

**Chart Behavior**:
- Chart is automatically created alongside PivotTable
- Chart uses pre-aggregated data from PivotTable configuration
- Categories come from `--rows` fields, values from `--values` fields
- Chart is positioned below the PivotTable on the same sheet

## Style Options

| Style | Description | Use Case |
|-------|-------------|----------|
| `monochrome` | Black/White/Grey theme | General analysis, statistics (DEFAULT) |
| `finance` | Blue/White theme | Financial reports, revenue, ROI |

**Monochrome Style**:
- Header: Dark grey (#333333) + White text
- Row labels: Light grey (#F5F5F5)
- Data: White with alternating grey rows
- Built-in: PivotStyleMedium9

**Finance Style**:
- Header: Dark blue (#1F4E79) + White text
- Row labels: Light blue (#D6E3F0)
- Data: White with alternating light blue rows
- Built-in: PivotStyleMedium2

## Aggregation Functions

| Function | Usage | Description |
|----------|-------|-------------|
| `sum` | `Revenue:sum` | Total values |
| `count` | `Orders:count` | Count items |
| `average` / `avg` | `Price:avg` | Mean value |
| `max` | `Sales:max` | Maximum value |
| `min` | `Cost:min` | Minimum value |

</Tool: pivot command>

<Tool: inspect command>

**Purpose**: Get sheet names, data range, and headers before creating PivotTable.

**CRITICAL**: You MUST run `inspect` first to get the parameters for `pivot` command.

```bash
/app/.kimi/skills/xlsx/scripts/KimiXlsx inspect data.xlsx --pretty
```

**Example Output**:
```json
{
  "sheets": [{
    "name": "SalesData",
    "dataRange": "A1:F500",
    "tables": [{
      "headers": ["Date", "Region", "Product", "Category", "Revenue", "Quantity"]
    }]
  }]
}
```

**Parameter Mapping** (inspect output → pivot parameters):

| inspect output | pivot parameter | Example |
|----------------|-----------------|---------|
| `sheets[].name` | `--source` (sheet name) | `"SalesData!..."` |
| `sheets[].dataRange` | `--source` (range) | `"...A1:F500"` |
| `sheets[].tables[].headers` | `--rows`, `--cols`, `--values`, `--filters` | `"Product"`, `"Revenue:sum"` |

**Combined**: `--source "SalesData!A1:F500"` (sheet name + data range)

</Tool: inspect command>

<Complete Workflow Example>

```bash
# Step 1: Verify formulas (assumes data.xlsx already exists)
/app/.kimi/skills/xlsx/scripts/KimiXlsx recheck data.xlsx
/app/.kimi/skills/xlsx/scripts/KimiXlsx reference-check data.xlsx

# Step 2: Inspect structure (get sheet names, headers)
/app/.kimi/skills/xlsx/scripts/KimiXlsx inspect data.xlsx --pretty

# Step 3: Create PivotTable (use --style for theme)
/app/.kimi/skills/xlsx/scripts/KimiXlsx pivot \
    data.xlsx output.xlsx \
    --source "SalesData!A1:F500" \
    --rows "Product,Region" \
    --values "Revenue:sum,Quantity:count" \
    --location "Summary!A3" \
    --name "SalesSummary" \
    --style "finance"

# Step 4: Validate output (auto-ignores safe openpyxl issues, but NOT pivot errors)
/app/.kimi/skills/xlsx/scripts/KimiXlsx validate output.xlsx
# Exit code 0 = safe to deliver
# Exit code 1 = critical errors (pivot structure problems) - MUST FIX
```

</Complete Workflow Example>

<Example Scenarios>

**Sales Summary by Product**:
```bash
/app/.kimi/skills/xlsx/scripts/KimiXlsx pivot \
    sales.xlsx output.xlsx \
    --source "Sales!A1:F500" \
    --rows "Product" \
    --values "Revenue:sum,Units:count" \
    --location "Summary!A3"
```

**Quarterly Comparison with Filters**:
```bash
/app/.kimi/skills/xlsx/scripts/KimiXlsx pivot \
    quarterly.xlsx report.xlsx \
    --source "Data!A1:H200" \
    --rows "Category" \
    --cols "Quarter" \
    --values "Amount:sum" \
    --filters "Year,Department" \
    --location "Pivot!B2"
```

**Multi-Dimension Analysis (with Finance style)**:
```bash
/app/.kimi/skills/xlsx/scripts/KimiXlsx pivot \
    transactions.xlsx report.xlsx \
    --source "Transactions!A1:G2000" \
    --rows "Category,Subcategory" \
    --cols "Month" \
    --values "Amount:sum,TransactionID:count" \
    --filters "Year" \
    --location "Analysis!B2" \
    --name "TransactionAnalysis" \
    --style "finance"
```

**Trend Analysis with Line Chart**:
```bash
/app/.kimi/skills/xlsx/scripts/KimiXlsx pivot \
    monthly_data.xlsx trend_report.xlsx \
    --source "Data!A1:D100" \
    --rows "Month" \
    --values "Revenue:sum" \
    --location "Trend!A3" \
    --chart "line"
```

**Market Share with Pie Chart**:
```bash
/app/.kimi/skills/xlsx/scripts/KimiXlsx pivot \
    market_data.xlsx share_report.xlsx \
    --source "Sales!A1:C50" \
    --rows "Region" \
    --values "Sales:sum" \
    --location "Share!A3" \
    --chart "pie"
```

</Example Scenarios>

<When to Use PivotTable>

**Use PivotTable when**:
- User explicitly requests "pivot table" or "data pivot"
- Task requires data summarization by categories
- Dataset has 50+ rows with grouping needs
- Cross-tabulation or multi-dimensional analysis needed

**Trigger Keywords**: summarize, aggregate, group by, categorize, breakdown, statistics, distribution, count by, total by

**PivotTable vs Formulas**:
| Scenario | Use PivotTable | Use Formulas |
|----------|----------------|--------------|
| Multi-dimension grouping | ✅ | ❌ |
| Large dataset (50+ rows) | ✅ | ❌ |
| Simple single aggregation | ❌ | ✅ |

</When to Use PivotTable>

<Best Practices>

**Source Data Requirements**:
- First row MUST contain unique column headers
- No merged cells, no blank rows within data
- Consistent data types in each column

**Location Placement**:
- Use a NEW sheet for PivotTable (avoids overwriting data)
- Start at cell A3 or B2 (leaves room for filter dropdowns)

**Field Selection**:
| Field Type | Best For |
|------------|----------|
| Row fields | Primary categorization, many unique values |
| Column fields | Secondary categorization, few unique values (≤10) |
| Value fields | Numeric data for aggregation |
| Filter fields | Optional filtering by user |

</Best Practices>

<Troubleshooting>

| Issue | Solution |
|-------|----------|
| "Field not found" | Check exact spelling/case of column headers via `inspect` |
| Empty PivotTable | Verify source range includes all data rows |
| Tool fails | Use absolute paths; ensure file not open in Excel |
| Validation `pass_with_warnings` | Safe to deliver - these are openpyxl schema quirks, not pivot errors |
| Validation `failed` with pivot errors | Critical! Check for `pivotCache`, `pivotTable`, `rowItems` in error messages - these MUST be fixed |
| Validation `failed` with unknown errors | Treat as critical, investigate before delivery |

**Validation Tips**:
- Use `--lenient` flag to see what errors were ignored: `validate output.xlsx --lenient`
- PivotTable errors (pivotCache, pivotTable, rowItems, colItems) are NEVER ignored
- If validation fails on pivot-related errors, the file will crash Excel - do not deliver

</Troubleshooting>

<Post-Creation Notes>

After creating PivotTable, inform user:
1. Open file in Excel to refresh cache and render properly
2. User can drag fields, apply filters, change aggregations
3. Right-click → Refresh if source data changes

</Post-Creation Notes>

<🚨 CRITICAL: DO NOT MODIFY PIVOT OUTPUT WITH OPENPYXL>

**⛔ NEVER open pivot output file with openpyxl after running `pivot` command!**

openpyxl will corrupt the pivotCache paths when saving, causing MS Excel to crash.

**If you need Cover sheet or extra styling:**
```
✅ CORRECT WORKFLOW:
1. openpyxl: Create base.xlsx with ALL sheets (Cover, Data, etc.)
2. pivot command: base.xlsx → final.xlsx (adds PivotTable as LAST step)
3. validate final.xlsx
4. DELIVER (do NOT modify final.xlsx again)

❌ WRONG WORKFLOW (CORRUPTS FILE):
1. pivot command: data.xlsx → pivot.xlsx
2. openpyxl: Open pivot.xlsx, add Cover sheet, save  ← FILE CORRUPTED!
3. MS Excel cannot open the file
```

**Why this happens:**
- `pivot` command uses OpenXML SDK with correct pivotCache paths (`xl/pivotCache/`)
- openpyxl rewrites the entire xlsx package with its own path format
- This path mismatch causes MS Excel to fail loading the file

</🚨 CRITICAL: DO NOT MODIFY PIVOT OUTPUT WITH OPENPYXL>
