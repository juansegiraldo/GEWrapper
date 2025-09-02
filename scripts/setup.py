#!/usr/bin/env python3
"""
Setup script for DataWashCopiaMia - Great Expectations Streamlit Wrapper
"""

import sys
import subprocess
import os
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        print("   Please upgrade Python and try again")
        return False
    
    print(f"Python {sys.version.split()[0]} detected")
    return True

def install_requirements():
    """Install required packages"""
    print("\nInstalling required packages...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("All packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing packages: {e}")
        print("   Try running: pip install -r requirements.txt")
        return False

def verify_installation():
    """Verify that all required packages are installed"""
    print("\nVerifying installation...")
    
    required_packages = [
        "streamlit",
        "great_expectations", 
        "pandas",
        "plotly",
        "openpyxl",
        "pyarrow"
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  {package}")
        except ImportError:
            print(f"  {package}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\nFailed to import: {', '.join(failed_imports)}")
        print("   Try reinstalling with: pip install -r requirements.txt --force-reinstall")
        return False
    
    print("All packages verified successfully")
    return True

def check_sample_data():
    """Check if sample data files exist"""
    print("\nChecking sample data...")
    
    sample_files = [
        "sample_data/customers.csv",
        "sample_data/sales_data.csv", 
        "sample_data/inventory.json"
    ]
    
    all_exist = True
    for file_path in sample_files:
        if Path(file_path).exists():
            print(f"  {file_path}")
        else:
            print(f"  {file_path} (missing)")
            all_exist = False
    
    if all_exist:
        print("All sample data files found")
    else:
        print("Some sample data files are missing")
    
    return all_exist

def create_startup_script():
    """Create a startup script for easy launching"""
    print("\nCreating startup script...")
    
    if os.name == 'nt':  # Windows
        script_content = """@echo off
echo Starting DataWashCopiaMia...
streamlit run streamlit_app.py
pause
"""
        script_name = "start_app.bat"
    else:  # Unix-like
        script_content = """#!/bin/bash
echo "Starting DataWashCopiaMia..."
streamlit run streamlit_app.py
"""
        script_name = "start_app.sh"
    
    try:
        with open(script_name, 'w') as f:
            f.write(script_content)
        
        if os.name != 'nt':  # Make executable on Unix-like systems
            os.chmod(script_name, 0o755)
        
        print(f"Created {script_name}")
        return True
    except Exception as e:
        print(f"Error creating startup script: {e}")
        return False

def main():
    """Main setup function"""
    print("🧹 DataWashCopiaMia Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("\nInstallation completed with errors")
        print("   You may need to install packages manually")
    
    # Verify installation
    if not verify_installation():
        print("\nSetup failed - some packages could not be imported")
        sys.exit(1)
    
    # Check sample data
    check_sample_data()
    
    # Create startup script
    create_startup_script()
    
    # Final instructions
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nTo start the application:")
    print("  Option 1: streamlit run streamlit_app.py")
    if os.name == 'nt':
        print("  Option 2: Double-click start_app.bat")
    else:
        print("  Option 2: ./start_app.sh")
    
    print("\nThe application will open in your web browser at:")
    print("  http://localhost:8501")
    
    print("\nTo get started:")
    print("  1. Upload one of the sample CSV files")
    print("  2. Explore data profiling features") 
    print("  3. Configure expectations using templates")
    print("  4. Run validation and view results")
    
    print("\nFor help and documentation:")
    print("  - README.md (user guide)")
    print("  - INSTALL_GUIDE.md (troubleshooting)")
    
    print("\nHappy data validating!")

if __name__ == "__main__":
    main()