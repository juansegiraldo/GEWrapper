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
```bash
git clone <repository-url>
cd GEWrapper
```

### 2. Set Up Python Environment (Recommended)

Create a virtual environment to isolate dependencies:

**Windows:**
```bash
python -m venv datawash_env
datawash_env\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv datawash_env
source datawash_env/bin/activate
```

### 3. Install Dependencies

Install all required Python packages:
```bash
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
```bash
python -c "import streamlit, great_expectations, pandas, plotly; print('All dependencies installed successfully!')"
```

### 5. Run the Application

Start the Streamlit server:
```bash
streamlit run streamlit_app.py
```

The application should automatically open in your default web browser at:
`http://localhost:8501`

## First Run

### Testing with Sample Data

1. **Start the application** using the command above
2. **Navigate to the Upload Data section**
3. **Try the sample files** in the `sample_data/` folder:
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
- Run command prompt as administrator (Windows)
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
```bash
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

## Advanced Configuration

### Custom Settings

Edit `config/app_config.py` to modify:
- File size limits
- Sample sizes
- UI preferences
- Color schemes

### Environment Variables

Set these environment variables for advanced configuration:

```bash
# Maximum file upload size (in bytes)
export STREAMLIT_MAX_UPLOAD_SIZE=104857600

# Disable usage statistics
export STREAMLIT_GATHER_USAGE_STATS=false
```

### Network Configuration

**Running on Different Host/Port:**
```bash
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
```bash
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

1. **Read the User Guide** in README.md
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

Need more help? Check the README.md for detailed usage instructions and examples.