# Troubleshooting - DataWash by Stratesys

Quick fixes for common installation and runtime issues.

## Installation
- Python version error
  - Install Python 3.8+ and ensure `python --version`
- Permission denied during `pip install`
  - Run PowerShell as Administrator
  - Or use: `pip install --user -r requirements.txt`
- ImportError after install (e.g., `ModuleNotFoundError: streamlit`)
  - Activate venv: `.\gewrapper_env\Scripts\Activate.ps1`
  - Reinstall: `pip install -r requirements.txt --force-reinstall`

## Running the app
- Port already in use
  - `streamlit run streamlit_app.py --server.port 8502`
- File upload issues
  - Check size < 100MB (or adjust `AppConfig.MAX_FILE_SIZE`)
  - Use supported formats: CSV/JSON/Parquet/Excel
  - Try another browser
- Slow performance with big data
  - Enable sampling in "Run Validation"
  - Prefer Parquet; close other heavy apps

## Validation
- "Expectation suite has no expectations"
  - Go back to Configure and add expectations or import a suite
- Custom SQL query errors
  - Use `{table_name}` placeholder
  - Return `COUNT(*) as violation_count`
  - For booleans, use `column = True/False`; avoid `'1'/'0'` strings

## Reports and exports
- Excel export fails
  - Ensure `openpyxl` is installed
- HTML/JSON export encoding issues
  - Try re-running after restart; verify data types/encodings

## Reset the app
- In Results, click "🔄 Restart" to clear session/cache and return to Upload

## Getting help
- Check `docs/INSTALL_GUIDE.md` and this guide
- Open an issue with error details and steps to reproduce
