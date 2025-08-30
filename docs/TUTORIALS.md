# Tutorials - DataWash by Stratesys

This page provides hands-on walkthroughs using the sample datasets in `data/sample_data/`.

## Tutorial 1: Sales dataset validation starter
![Sales dataset walkthrough](assets/upload.gif)
Dataset: `data/sample_data/sales_data.csv`

### Goal
- Ensure `total_amount ≈ quantity * unit_price`
- Ensure `quantity` is between 1 and 10
- Ensure `transaction_date` is within a reasonable range

### Steps
1) Start app and upload the CSV
```powershell
.\scripts\activate_env.ps1
streamlit run streamlit_app.py
```
2) In "📁 Upload Data", select `sales_data.csv`
3) Go to "📊 Data Profiling" and review columns
4) Open "⚙️ Configure Expectations" and add:
   - Column: `quantity` → Expect values to be between (min=1, max=10)
   - Column: `transaction_date` → Expect values to be date-parseable
5) Add a custom SQL expectation to check totals:
   - Open "🔍 Custom SQL Query Builder" → use Manual SQL Query
   - Paste and validate:
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE ABS(total_amount - (quantity * unit_price)) > 0.01
```
   - Expected Result: `empty` (no violations)
   - Name: "Totals match quantity × price"
6) Click "Add Expectation"
7) Proceed to "✅ Run Validation" (sampling optional)
8) View results in "📋 View Results" and export reports if needed

### What to look for
- If any rows fail the totals check, inspect `quantity`, `unit_price`, and `total_amount`
- Use Failed Records dataset and report generator to analyze and export

## Tutorial 2: Duplicates and categories
![Configure expectations](assets/configure.gif)
Dataset: `data/sample_data/sales_data.csv`

### Goal
- Check duplicates on `(transaction_id)`
- Ensure `category` values are within an allowed set

### Steps
1) Add expectation: `expect_column_values_to_be_unique` on `transaction_id`
2) Add expectation: `expect_column_values_to_be_in_set` on `category` with values like:
   - `Electronics`, `Footwear`, `Appliances`, `Fitness`, `Sports`, `Office`, `Education`, `Kitchen`, `Clothing`, `Travel`, `Health`, `Beauty`
3) Run validation and review failure rates by expectation type

---
See also:
- `docs/USER_GUIDE.md` for the full workflow
- `docs/CUSTOM_SQL_GUIDE.md` for more SQL patterns
- `docs/FAILED_RECORDS_GUIDE.md` to export detailed failures
