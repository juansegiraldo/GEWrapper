# DataWash Installation Troubleshooting Guide

## Overview

This guide addresses the common dependency conflicts encountered when installing DataWash, particularly the issues with numpy, streamlit, and great-expectations compatibility.

## Common Issues and Solutions

### Issue 1: Numpy Compilation Errors

**Error**: `ERROR: Unknown compiler(s): [['icl'], ['cl'], ['cc'], ['gcc'], ['clang'], ['clang-cl'], ['pgcc']]`

**Cause**: Numpy is trying to compile from source but no C compiler is available.

**Solution**: Install streamlit first, which will pull in pre-compiled numpy wheels.

```powershell
# Install streamlit first (this installs compatible numpy)
pip install streamlit
```

### Issue 2: Great Expectations Import Errors

**Error**: `ModuleNotFoundError: No module named 'marshmallow.warnings'`

**Cause**: Version conflicts between great-expectations and its dependencies.

**Solution**: Install great-expectations without dependencies, then install compatible versions manually.

```powershell
# Install great-expectations without dependencies
pip install great-expectations --no-deps

# Install compatible dependencies
pip install "marshmallow<4.0.0,>=3.7.1"
pip install "altair<5.0.0,>=4.2.1"
```

### Issue 3: Version Conflicts

**Error**: `ERROR: ResolutionImpossible: for help visit https://pip.pypa.io/en/latest/topics/dependency-resolution/`

**Cause**: Conflicting version requirements between packages.

**Solution**: Use the tested requirements file or follow the manual installation order.

## Complete Installation Procedure

### Step 1: Environment Setup

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# Upgrade pip and install build tools
python -m pip install --upgrade pip
pip install setuptools wheel
```

### Step 2: Core Dependencies

```powershell
# Install streamlit first (this handles numpy compatibility)
pip install streamlit

# Install other core dependencies
pip install plotly openpyxl xlrd sqlalchemy pydantic pandasql sqlparse
```

### Step 3: Great Expectations

```powershell
# Install great-expectations without dependencies
pip install great-expectations --no-deps

# Install great-expectations dependencies manually
pip install cryptography ipython ipywidgets jsonpatch makefun mistune nbformat notebook pyparsing scipy tqdm tzlocal
```

### Step 4: Fix Version Conflicts

```powershell
# Fix marshmallow version conflict
pip install "marshmallow<4.0.0,>=3.7.1"

# Fix altair version conflict
pip install "altair<5.0.0,>=4.2.1"
```

### Step 5: Launch Application

```powershell
streamlit run streamlit_app.py
```

## Alternative: Use Pre-configured Requirements

If the manual installation doesn't work, use the tested requirements file:

```powershell
pip install -r requirements_venv.txt
```

## Verification

To verify the installation is working:

```powershell
# Test great-expectations import
python -c "import great_expectations as gx; print('Great Expectations imported successfully!')"

# Test streamlit
python -c "import streamlit as st; print('Streamlit imported successfully!')"

# Launch the app
streamlit run streamlit_app.py
```

## Known Working Versions

The following versions have been tested and work together:

- **Python**: 3.13
- **Streamlit**: 1.49.1
- **Numpy**: 2.3.2
- **Pandas**: 2.3.2
- **Great Expectations**: 0.18.22
- **Marshmallow**: 3.26.1
- **Altair**: 4.2.2

## Troubleshooting Tips

1. **Always use a virtual environment** to avoid system-wide conflicts
2. **Install streamlit first** to get compatible numpy
3. **Use `--no-deps` for great-expectations** to avoid automatic dependency resolution
4. **Install dependencies in the correct order** as shown above
5. **Check for version conflicts** if you encounter import errors

## Getting Help

If you continue to have issues:

1. Check the [FAQ](FAQ.md) for common questions
2. Review the [User Guide](USER_GUIDE.md) for usage instructions
3. Open an issue on GitHub with your error messages and system information

## System Requirements

- **OS**: Windows 10/11 (tested), Linux/macOS (should work)
- **Python**: 3.8+ (tested with 3.13)
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk**: 2GB free space for dependencies
