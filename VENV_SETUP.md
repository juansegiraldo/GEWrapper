# Virtual Environment Setup for DataWashCopiaMia

This project now uses a Python virtual environment to manage dependencies cleanly and avoid conflicts.

## Quick Start

### Option 1: Using the Batch File (Windows)
```bash
# Double-click or run:
start_app.bat
```

### Option 2: Using PowerShell
```powershell
# Activate the environment:
.\activate_env.ps1

# Then run the app:
python -m streamlit run streamlit_app.py
```

### Option 3: Manual Activation
```bash
# Activate the virtual environment:
.\gewrapper_env\Scripts\activate.bat

# Run the app:
python -m streamlit run streamlit_app.py
```

## Virtual Environment Details

- **Environment Name**: `gewrapper_env`
- **Location**: `./gewrapper_env/`
- **Python Version**: Compatible with Python 3.13

## Key Dependencies

The virtual environment includes:
- **Streamlit**: Web application framework
- **Great Expectations**: Data validation library
- **Pandas**: Data manipulation
- **Plotly**: Interactive visualizations
- **Other supporting libraries**: See `requirements_venv.txt`

## Managing the Environment

### Activating the Environment
```bash
# Windows Command Prompt:
.\gewrapper_env\Scripts\activate.bat

# Windows PowerShell:
.\gewrapper_env\Scripts\Activate.ps1
```

### Deactivating the Environment
```bash
deactivate
```

### Installing New Packages
```bash
# Make sure the environment is activated first
pip install package_name
```

### Updating Requirements
```bash
# After installing new packages, update the requirements file:
pip freeze > requirements_venv.txt
```

### Recreating the Environment
If you need to recreate the environment:
```bash
# Remove the old environment
rmdir /s gewrapper_env

# Create a new one
python -m venv gewrapper_env

# Activate it
.\gewrapper_env\Scripts\activate.bat

# Install dependencies
pip install -r requirements_venv.txt
```

## Troubleshooting

### Port Already in Use
If you get a port conflict, the app will automatically try the next available port (8501, 8502, etc.).

### Environment Not Found
If the virtual environment is missing, recreate it using the steps above.

### Permission Issues
Run PowerShell as Administrator if you encounter permission issues.

## Benefits of Using Virtual Environment

1. **Isolation**: Dependencies don't conflict with other Python projects
2. **Reproducibility**: Exact same environment across different machines
3. **Clean Installation**: No system-wide package pollution
4. **Easy Management**: Simple activation/deactivation

## Files Overview

- `gewrapper_env/`: Virtual environment directory
- `activate_env.bat`: Batch file to activate environment
- `activate_env.ps1`: PowerShell script to activate environment
- `start_app.bat`: Updated to use virtual environment
- `requirements_venv.txt`: Exact package versions in the environment
- `requirements.txt`: Original requirements file
