# Comprehensive Troubleshooting Guide - DataWash by Stratesys

This guide provides solutions for common issues encountered during installation, configuration, and usage of DataWash.

## 🚨 Quick Reference

| Issue Type | Quick Solution | Detailed Section |
|------------|----------------|------------------|
| Installation fails | Check [Installation Issues](#installation-issues) | [Installation Troubleshooting](INSTALLATION_TROUBLESHOOTING.md) |
| App won't start | Check port, Python version | [Runtime Issues](#runtime-issues) |
| File upload fails | Check size/format | [File Upload Issues](#file-upload-issues) |
| Validation errors | Check expectations setup | [Validation Issues](#validation-issues) |
| Custom SQL problems | Check syntax/placeholders | [SQL Issues](#custom-sql-issues) |
| Export failures | Check dependencies | [Export Issues](#export-issues) |

## 📥 Installation Issues

### Dependency Conflicts (Most Common)
**⚠️ Critical**: DataWash has specific dependency requirements due to numpy/streamlit/great-expectations conflicts.

**Symptoms:**
- Numpy compilation errors
- Great Expectations import failures
- Version resolution conflicts

**Solution:**
1. **Use specific installation order** (see [Installation Guide](INSTALL_GUIDE.md))
2. **Install streamlit first** to get compatible numpy
3. **Use tested requirements file**: `pip install -r requirements_venv.txt`

### Python Environment Issues
- **Python version error**: Upgrade to Python 3.8+
- **Permission denied**: Run PowerShell as Administrator or use `--user` flag
- **Virtual environment issues**: Ensure venv is activated
- **Import errors**: Reinstall dependencies with `--force-reinstall`

**Quick Diagnostic:**
```powershell
# Check Python version
python --version

# Test core imports
python -c "import streamlit, great_expectations, pandas; print('All imports successful')"

# Verify virtual environment
pip list | findstr streamlit
```

## 🚀 Runtime Issues

### Application Startup Problems

**Port Already in Use**
```
Error: Port 8501 is already in use
```
**Solutions:**
```powershell
# Use different port
streamlit run streamlit_app.py --server.port 8502

# Kill existing Streamlit processes (Windows)
taskkill /f /im streamlit.exe

# Find what's using the port
netstat -ano | findstr :8501
```

**Python/Streamlit Not Found**
```
'streamlit' is not recognized as an internal or external command
```
**Solutions:**
- Activate virtual environment: `.\gewrapper_env\Scripts\Activate.ps1`
- Check PATH variables
- Reinstall in virtual environment

### Performance Issues

**Slow Loading/Processing**
- Enable data sampling for large files (>10MB)
- Close other resource-intensive applications
- Use Parquet format for better performance
- Check available RAM (recommended: 8GB+)

**Browser Issues**
- Clear browser cache and cookies
- Try incognito/private browsing mode
- Switch to Chrome/Edge for best compatibility
- Disable browser extensions that might interfere

## 📁 File Upload Issues

### Supported Formats and Limits

**File Format Issues**
```
Supported formats: CSV, JSON, Parquet, Excel (.xlsx, .xls)
```
**Solutions:**
- Convert unsupported formats (e.g., .txt to .csv)
- Check file extension matches actual format
- For Excel files, ensure `openpyxl` is installed

**File Size Limits**
```
Error: File size exceeds 100MB limit
```
**Solutions:**
```python
# Increase limit in config/app_config.py
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB

# Or set environment variable
$env:STREAMLIT_MAX_UPLOAD_SIZE = 209715200  # 200MB in bytes
```

**Encoding Issues**
- Try UTF-8 encoding for text files
- Use Excel format for files with special characters
- Check for BOM (Byte Order Mark) in CSV files

## ✅ Validation Issues

### Expectation Suite Problems

**"Expectation suite has no expectations"**
1. Go to "⚙️ Configure Expectations"
2. Add at least one expectation or import existing suite
3. Ensure expectations are saved before validation

**Validation Fails Immediately**
- Check data types match expectation requirements
- Verify column names exist in uploaded data
- Review expectation parameters for typos

### Data Quality Check Failures

**All Validations Fail**
- Review data preview for unexpected formats
- Check for extra headers or footers in data files
- Verify data types (numbers vs strings)

**Inconsistent Results**
- Check if sampling is enabled (may give different results)
- Ensure data is sorted consistently if order matters
- Review for datetime parsing issues

## 🔍 Custom SQL Issues

### Query Syntax Problems

**Common SQL Errors:**
```sql
-- ❌ Wrong: Using actual table name
SELECT COUNT(*) FROM employees

-- ✅ Correct: Using placeholder
SELECT COUNT(*) FROM {table_name}
```

```sql
-- ❌ Wrong: Incorrect return column
SELECT COUNT(*) as count

-- ✅ Correct: Expected return column
SELECT COUNT(*) as violation_count
```

**Boolean Column Issues:**
```sql
-- ✅ Recommended: Use True/False
WHERE active = True AND status = 'enabled'

-- ⚠️ Works but less clear: Use 1/0 (auto-converted)
WHERE active = 1 AND status = 1

-- ❌ Wrong: String comparison
WHERE active = 'true' AND status = '1'
```

### Query Testing

**Use the Test Query Feature:**
1. Write your SQL query
2. Click "🧪 Test Query" button
3. Review results before adding expectation
4. Check violation count makes sense

**Debugging SQL Issues:**
- Start with simple WHERE conditions
- Add complexity gradually
- Use the LLM prompt in [Custom SQL Guide](CUSTOM_SQL_GUIDE.md)
- Check [SQL Quick Reference](SQL_QUICK_REFERENCE.md) for patterns

## 📤 Export Issues

### Report Generation Problems

**Excel Export Fails**
```powershell
# Install required dependency
pip install openpyxl

# Verify installation
python -c "import openpyxl; print('openpyxl installed successfully')"
```

**HTML/PDF Export Issues**
- Check disk space for temporary files
- Ensure write permissions in output directory
- Try smaller data sets for large exports
- Restart application if exports hang

**JSON Export Encoding**
- Check for special characters in data
- Try UTF-8 encoding
- Review data types (dates, decimals)

### Failed Records Export

**No Failed Records Generated**
- Ensure validation has actually failed expectations
- Check if "empty" result type expects zero violations
- Review expectation logic

**Large Failed Records Dataset**
- Use sampling to limit size
- Export in chunks for very large datasets
- Consider CSV format for better performance

## 🔄 Session and Cache Issues

### Application State Problems

**Lost Configuration After Navigation**
- Session state should persist across steps
- Try refreshing browser if state is lost
- Use "Export Expectations" as backup

**Cache Issues**
```
Error: Cached data is corrupted
```
**Solutions:**
- Click "🔄 Restart" in Results section
- Clear browser cache
- Restart Streamlit application

## 🌐 Network and Security Issues

### Corporate/Firewall Issues

**Proxy Configuration**
```powershell
# Configure pip for corporate proxy
pip install --proxy http://proxy.company.com:port -r requirements.txt

# Set environment variables
$env:HTTP_PROXY = "http://proxy.company.com:port"
$env:HTTPS_PROXY = "http://proxy.company.com:port"
```

**Port Restrictions**
- Use different port if 8501 is blocked
- Check firewall exceptions
- Consider using `--server.address 0.0.0.0` for network access

## 🆘 Getting Advanced Help

### Diagnostic Information to Collect

When reporting issues, include:

**System Information:**
```powershell
# Python version
python --version

# Package versions
pip list | findstr -i "streamlit great pandas plotly"

# System specs
systeminfo | findstr /C:"Total Physical Memory"
```

**Application Logs:**
- Console output from Streamlit
- Browser developer console errors
- Screenshot of error messages

### Self-Diagnosis Steps

1. **Test with Sample Data**
   - Use provided `data/sample_data/customers.csv`
   - Follow [Tutorial](TUTORIALS.md) steps exactly
   - If sample works, issue is with your data

2. **Minimal Reproduction**
   - Create smallest possible data file that reproduces issue
   - Use simplest expectation that fails
   - Note exact steps to reproduce

3. **Environment Reset**
   ```powershell
   # Create fresh environment
   python -m venv test_env
   .\test_env\Scripts\Activate.ps1
   pip install -r requirements_venv.txt
   streamlit run streamlit_app.py
   ```

### Community Support

**Documentation Resources:**
- [Installation Guide](INSTALL_GUIDE.md) - Setup and configuration
- [User Guide](USER_GUIDE.md) - Complete workflow walkthrough
- [Custom SQL Guide](CUSTOM_SQL_GUIDE.md) - SQL validation patterns
- [FAQ](FAQ.md) - Quick answers to common questions

**Getting Help:**
1. Check this troubleshooting guide first
2. Review relevant documentation sections
3. Test with sample data to isolate issues
4. Open GitHub issue with detailed information
5. Include diagnostic information and steps to reproduce

## 🔧 Configuration Tweaks

### Performance Optimization

**For Large Files:**
```python
# In config/app_config.py
DEFAULT_SAMPLE_SIZE = 10000  # Reduce for faster processing
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit
```

**For Memory Issues:**
- Reduce preview row count
- Enable sampling by default
- Close other applications
- Use 64-bit Python

### UI Customization

**Streamlit Configuration:**
```toml
# .streamlit/config.toml
[server]
maxUploadSize = 200
enableCORS = false
enableXsrfProtection = false

[browser]
gatherUsageStats = false
```

---

## 🎯 Quick Resolution Checklist

When encountering issues:

- [ ] Check Python version (3.8+)
- [ ] Verify virtual environment is activated
- [ ] Test with sample data first
- [ ] Review error messages carefully
- [ ] Check file format and size
- [ ] Try different browser/incognito mode
- [ ] Clear cache and restart application
- [ ] Review expectation configuration
- [ ] Check SQL syntax and placeholders
- [ ] Verify all dependencies are installed

**Still having issues?** Check [Installation Troubleshooting](INSTALLATION_TROUBLESHOOTING.md) for detailed dependency resolution steps.
