# FAQ - DataWash by Stratesys

## What file types are supported?
CSV, JSON, Parquet, Excel (`.xlsx`, `.xls`). See `config/app_config.py` for the list.

## Why must custom SQL use `{table_name}`?
The data is loaded into an in-memory table for the SQL engine; `{table_name}` is replaced at runtime.

## Do I use True/False or 1/0 for booleans?
Prefer `column = True/False`. `1/0` is auto-fixed for boolean columns, but may be less readable.

## How do I increase the upload size limit?
Edit `AppConfig.MAX_FILE_SIZE` (bytes). Optionally set `STREAMLIT_MAX_UPLOAD_SIZE` env var.

## Where are failed records stored?
They are generated in-memory and downloaded via the browser; not persisted server-side by default.

## How do I restart the app?
In Results, click "🔄 Restart" to clear session and cache.

## How can I run on a different port or host?
```powershell
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8080
```

## Where can I learn by example?
See `docs/TUTORIALS.md`. For SQL-based rules, see `docs/CUSTOM_SQL_GUIDE.md` and `docs/SQL_QUICK_REFERENCE.md`.
