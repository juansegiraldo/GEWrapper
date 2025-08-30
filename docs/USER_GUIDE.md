# User Guide - DataWash by Stratesys

This guide walks you through the end-to-end workflow in the app: Upload → Profile → Configure → Validate → Results.

![Upload and profiling](assets/upload.gif)

## 1) Start the app (Windows PowerShell)

```powershell
# From the project root
.\scripts\activate_env.ps1

# Install dependencies (first run)
pip install -r requirements.txt

# Launch
streamlit run streamlit_app.py
```

Alternative quick run:

```powershell
.\scripts\start_app.bat
```

The app opens at http://localhost:8501

## 2) Upload data
- Click "📁 Upload Data"
- Supported: CSV, JSON, Parquet, Excel (`.xlsx`, `.xls`)
- Max size: 100 MB (configurable)
- After upload you’ll see a preview and basic stats

Tip: For large datasets, prefer Parquet.

## 3) Profile your dataset
- Go to "📊 Data Profiling"
- Review:
  - Overview (rows, columns, memory, duplicates)
  - Data type distribution
  - Missing data analysis
  - Column-level details (stats/plots)
- Download the profile in JSON, Excel, HTML or CSV

## 4) Configure expectations
- Go to "⚙️ Configure Expectations"
- Options:
  - Apply Quick Start templates (e.g., Basic Data Quality)
  - Build expectations for columns (nulls, ranges, regex, etc.)
  - Use "🔍 Custom SQL Query Builder" for multi-column/business rules
- Export or import expectation suites (JSON)

![Configure expectations](assets/configure.gif)

Custom SQL tips:
- Use `{table_name}` placeholder
- Return `violation_count`
- For booleans, prefer `column = True/False`
- See `docs/CUSTOM_SQL_GUIDE.md` and `docs/SQL_QUICK_REFERENCE.md`

## 5) Run validation
- Open "✅ Run Validation"
- Options: sampling, all-at-once or step-by-step, detail level
- Start validation and monitor progress/metrics

![Run validation](assets/validate.gif)

## 6) Review results and export
- Open "📋 View Results"
- Explore metrics, visuals, detailed table, and failed records dataset
- Export JSON / HTML / CSV and failed records (summary/detailed CSV, JSON)
- Use "Download ALL" to get a zip of everything

![Results and exports](assets/results.gif)

## 7) Failed Records report
- Appears when failures exist
- Choose CSV/Excel/JSON; include original data/metadata as needed

## 8) Save/restore configurations
- Export expectations (popover in Configure step)
- Import expectations JSON to recreate a suite quickly

## 9) Reset the app
- In Results, click "🔄 Restart" to clear session and cache

## Troubleshooting quick tips
- Port busy → `streamlit run streamlit_app.py --server.port 8502`
- Excel export → ensure `openpyxl` is installed
- Custom SQL booleans → use `active = True` instead of `active = 1`

## Configuration
- See `docs/CONFIGURATION.md` and `config/app_config.py`

---
Happy data validating!
