# Virtual Environment Setup for DataWashCopiaMia

This project uses a Python virtual environment to manage dependencies cleanly and avoid conflicts.

## Quick Start (Windows)

### Option 1: Use helper script
```powershell
.\scripts\activate_env.ps1
```

### Option 2: Manual activation
```powershell
python -m venv gewrapper_env
.\gewrapper_env\Scripts\Activate.ps1
```

Then run the app:
```powershell
streamlit run streamlit_app.py
```

## Environment Details
- **Environment Name**: `gewrapper_env`
- **Location**: `./gewrapper_env/`
- **Python Version**: 3.8+ (tested up to 3.13)

## Managing the Environment

### Activate
```powershell
.\gewrapper_env\Scripts\Activate.ps1
```

### Deactivate
```powershell
deactivate
```

### Install packages
```powershell
pip install <package>
```

### Freeze/update requirements
```powershell
pip freeze > requirements_venv.txt
```

### Recreate the environment
```powershell
# Remove old env
rmdir /s /q gewrapper_env

# Create and activate
python -m venv gewrapper_env
.\gewrapper_env\Scripts\Activate.ps1

# Install deps
pip install -r requirements_venv.txt
```

## Tips
- Run PowerShell as Administrator if you hit permission errors
- Prefer `requirements.txt` for app usage; `requirements_venv.txt` is for pinning a dev snapshot
