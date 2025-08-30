# Configuration - DataWash by Stratesys

Central configuration lives in `config/app_config.py` via the `AppConfig` class. You can also control some behavior via environment variables or Streamlit flags.

## AppConfig keys (config/app_config.py)
- File upload:
  - `MAX_FILE_SIZE` (bytes) — default 100MB
  - `SUPPORTED_FILE_TYPES` — `['csv','json','parquet','xlsx','xls']`
- Data display:
  - `PREVIEW_ROWS` — rows to show in preview
  - `MAX_COLUMNS_DISPLAY`
- Validation:
  - `DEFAULT_SAMPLE_SIZE` — default sample size for large datasets
  - `MAX_EXPECTATIONS_PER_SUITE`
- UI:
  - `SIDEBAR_WIDTH`, `CHART_HEIGHT`
- Great Expectations:
  - `GE_DATA_CONTEXT_ROOT_DIR`
  - `DEFAULT_DATASOURCE_NAME`, `DEFAULT_DATA_CONNECTOR_NAME`, `DEFAULT_DATA_ASSET_NAME`
- Exports:
  - `EXPORT_FORMATS` — `['HTML', 'PDF', 'JSON']`
- Expectation templates:
  - `EXPECTATION_TEMPLATES` — templates used by the Configure step
- Colors and chart config:
  - `COLORS`, `CHART_CONFIG`

### Example: increase max upload size to 200MB
```python
# config/app_config.py
class AppConfig:
    MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB
```

## Environment variables (optional)
These can be set before launching Streamlit (PowerShell):

```powershell
# Max upload size for Streamlit file uploader (bytes)
$env:STREAMLIT_MAX_UPLOAD_SIZE = 104857600

# Disable anonymous usage stats
$env:STREAMLIT_GATHER_USAGE_STATS = "false"
```

Unset after the session:
```powershell
Remove-Item Env:STREAMLIT_MAX_UPLOAD_SIZE -ErrorAction SilentlyContinue
Remove-Item Env:STREAMLIT_GATHER_USAGE_STATS -ErrorAction SilentlyContinue
```

## Streamlit server flags
- Change port/address when launching:
```powershell
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8080
```

## Expectation templates
- Defined in `AppConfig.EXPECTATION_TEMPLATES`
- Used by the Configure step to quickly add common expectations

Tip: Keep `AppConfig` as the single source of truth and import values where needed.
