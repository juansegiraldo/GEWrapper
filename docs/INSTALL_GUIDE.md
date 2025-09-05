# Installation Guide - DataWashCopiaMia

This guide will help you set up and run the DataWashCopiaMia application on your local machine.

## Prerequisites

- **Python 3.8 or higher** (Python 3.9+ recommended)
- **pip** (Python package installer)
- **Git** (optional, for cloning repository)

## Installation Steps

### 1. Download the Application

**Option A: Download as ZIP**
- Download the project as a ZIP file
- Extract to your desired location
- Navigate to the extracted folder

**Option B: Clone with Git**
```powershell
git clone https://github.com/juansegiraldo/GEWrapper.git
cd GEWrapper
```

### 2. Set Up Python Environment (Recommended)

Create a virtual environment to isolate dependencies:

**Windows (PowerShell):**
```powershell
python -m venv gewrapper_env
.\gewrapper_env\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv gewrapper_env
source gewrapper_env/bin/activate
```

Alternatively, use the helper scripts (Windows):
```powershell
.\scripts\activate_env.ps1
```

### 3. Install Dependencies

Install all required Python packages:
```powershell
pip install -r requirements.txt
```

This will install:
- Streamlit (web framework)
- Great Expectations (data validation)
- Pandas (data processing)
- Plotly (visualizations)
- OpenPyXL (Excel support)
- PyArrow (Parquet support)
- Additional utilities

### 4. Verify Installation

Test that all components are working:
```powershell
python -c "import streamlit, great_expectations, pandas, plotly; print('All dependencies installed successfully!')"
```

### 5. Run the Application

Start the Streamlit server:
```powershell
streamlit run streamlit_app.py
```

The application should automatically open in your default web browser at:
`http://localhost:8501`

## First Run

### Testing with Sample Data

1. **Start the application** using the command above
2. **Navigate to the Upload Data section**
3. **Try the sample files** in the `data/sample_data/` folder:
   - `customers.csv` - Customer information dataset
   - `sales_data.csv` - Transaction data  
   - `inventory.json` - Product inventory

### Basic Workflow Test

1. **Upload** one of the sample CSV files
2. **Review** the data profiling information
3. **Apply** a basic template (e.g., "Basic Data Quality")
4. **Run validation** to see results
5. **Export** a report to verify functionality

## Troubleshooting

### Common Installation Issues

#### Dependency Conflicts (Most Common)

**⚠️ Important**: Due to dependency conflicts between numpy, streamlit, and great-expectations, follow the specific installation order in this guide.

**Issue 1: Numpy Compilation Errors**
```
ERROR: Unknown compiler(s): [['icl'], ['cl'], ['cc'], ['gcc'], ['clang'], ['clang-cl'], ['pgcc']]
```
**Cause**: Numpy is trying to compile from source but no C compiler is available.

**Solution**: Install streamlit first, which will pull in pre-compiled numpy wheels.
```powershell
pip install streamlit
```

**Issue 2: Great Expectations Import Errors**
```
ModuleNotFoundError: No module named 'marshmallow.warnings'
```
**Cause**: Version conflicts between great-expectations and its dependencies.

**Solution**: Install great-expectations without dependencies, then install compatible versions manually.
```powershell
# Install great-expectations without dependencies
pip install great-expectations --no-deps

# Install compatible dependencies
pip install "marshmallow<4.0.0,>=3.7.1"
pip install "altair<5.0.0,>=4.2.1"
```

**Issue 3: Version Resolution Conflicts**
```
ERROR: ResolutionImpossible: for help visit https://pip.pypa.io/en/latest/topics/dependency-resolution/
```
**Cause**: Conflicting version requirements between packages.

**Solution**: Use the tested requirements file or follow the manual installation order above.

#### Known Working Versions

The following versions have been tested and work together:
- **Python**: 3.13
- **Streamlit**: 1.49.1
- **Numpy**: 2.3.2
- **Pandas**: 2.3.2
- **Great Expectations**: 0.18.22
- **Marshmallow**: 3.26.1
- **Altair**: 4.2.2

#### Alternative Installation Method

If the manual installation doesn't work, use the tested requirements file:
```powershell
pip install -r requirements_venv.txt
```

#### General Installation Issues

**Python Version Error**
```
Error: Python 3.8+ required
```
*Solution: Upgrade Python or use a compatible version*

**Permission Errors**
```
Error: Permission denied installing packages
```
*Solutions:*
- Use `pip install --user -r requirements.txt`
- Run PowerShell as Administrator (Windows)
- Use `sudo pip install -r requirements.txt` (macOS/Linux)

**Memory/Dependency Conflicts**
```
Error: Cannot install conflicting dependencies
```
*Solution: Use a fresh virtual environment*

**Import Errors After Installation**
```
ModuleNotFoundError: No module named 'streamlit'
```
*Solutions:*
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

### Runtime Issues

**Port Already in Use**
```
Error: Port 8501 is already in use
```
*Solution: Use a different port*
```powershell
streamlit run streamlit_app.py --server.port 8502
```

**File Upload Issues**
- Check file size (100MB limit)
- Verify file format compatibility
- Try different browsers if upload fails

**Slow Performance**
- Enable data sampling for large files
- Close other resource-intensive applications
- Consider upgrading hardware for very large datasets

### Configuration Issues

**Great Expectations Context Errors**
- Application creates temporary contexts automatically
- Restart application if context issues persist
- Check disk space for temporary files

**Visualization Problems**
- Ensure stable internet connection (for some Plotly features)
- Try refreshing the browser page
- Clear browser cache if charts don't load

### Validation Issues

**"Expectation suite has no expectations" Error**
- Go back to Configure and add expectations or import a suite
- See the [User Guide](USER_GUIDE.md) for step-by-step instructions

**Custom SQL Query Errors**
- Use `{table_name}` placeholder
- Return `COUNT(*) as violation_count`
- For booleans, use `column = True/False`; avoid `'1'/'0'` strings
- See [Custom SQL Guide](CUSTOM_SQL_GUIDE.md) for detailed examples

**Excel Export Fails**
- Ensure `openpyxl` is installed: `pip install openpyxl`
- Try restarting the application

### Getting Help

**Installation Verification**
To verify the installation is working:
```powershell
# Test great-expectations import
python -c "import great_expectations as gx; print('Great Expectations imported successfully!')"

# Test streamlit
python -c "import streamlit as st; print('Streamlit imported successfully!')"

# Launch the app
streamlit run streamlit_app.py
```

**Additional Support**
If you continue to have issues:
1. Check the [FAQ](FAQ.md) for common questions
2. Review the [User Guide](USER_GUIDE.md) for usage instructions
3. See [Installation Troubleshooting](INSTALLATION_TROUBLESHOOTING.md) for detailed troubleshooting
4. Open an issue on GitHub with your error messages and system information

### System Requirements

- **OS**: Windows 10/11 (tested), Linux/macOS (should work)
- **Python**: 3.8+ (tested with 3.13)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk**: 2GB free space for dependencies

## Advanced Configuration

### Custom Settings

Edit `config/app_config.py` to modify:
- File size limits
- Sample sizes
- UI preferences
- Color schemes

### Environment Variables

Set these environment variables for advanced configuration (PowerShell):

```powershell
# Maximum file upload size (in bytes)
$env:STREAMLIT_MAX_UPLOAD_SIZE = 104857600

# Disable usage statistics
$env:STREAMLIT_GATHER_USAGE_STATS = "false"
```

### Network Configuration

**Running on Different Host/Port:**
```powershell
streamlit run streamlit_app.py --server.address 0.0.0.0 --server.port 8080
```

**Behind Corporate Firewall:**
- Configure proxy settings in pip: `pip install --proxy http://proxy.company.com:port -r requirements.txt`
- Add firewall exceptions for port 8501

## Docker Installation (Optional)

For containerized deployment, create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.address", "0.0.0.0"]
```

Build and run:
```powershell
docker build -t datawash .
docker run -p 8501:8501 datawash
```

## Performance Optimization

### For Large Datasets
- Use Parquet format when possible
- Enable smart sampling
- Consider upgrading RAM for better performance

### For Production Use
- Set up reverse proxy (nginx/Apache)
- Configure HTTPS
- Implement authentication if needed
- Monitor resource usage

## Next Steps

After successful installation:

1. **Read the User Guide** in `docs/USER_GUIDE.md`
2. **Try sample datasets** to understand features
3. **Import your own data** for validation
4. **Create expectation templates** for your use cases
5. **Set up regular validation workflows**

## Getting Help

If you encounter issues:

1. **Check this troubleshooting section**
2. **Review error messages carefully**
3. **Test with sample data first**
4. **Create GitHub issues for persistent problems**
5. **Contribute solutions back to the community**

---

**Happy Data Validating!** 🎉

Need more help? Check `docs/USER_GUIDE.md` for detailed usage instructions and examples.