# GEWrapper Project Organization Script
# This script helps maintain the organized project structure

param(
    [switch]$ShowStructure,
    [switch]$CleanCache,
    [switch]$Help
)

function Show-ProjectStructure {
    Write-Host "`nGEWrapper Project Structure" -ForegroundColor Cyan
    Write-Host "================================`n"
    
    $structure = @"
GEWrapper/
├── components/           # Core application components
│   ├── custom_sql_expectations.py
│   ├── data_upload.py
│   ├── expectation_builder.py
│   ├── failed_records_generator.py
│   ├── results_display.py
│   ├── sql_query_builder.py
│   └── validation_runner.py
├── config/              # Configuration files
│   ├── app_config.py
│   ├── *.json files
├── data/                # Data files
│   ├── output/          # Generated output files
│   ├── processed/       # Processed data files
│   └── sample_data/     # Sample datasets
├── docs/                # Documentation
│   ├── *.md files
├── scripts/             # Utility scripts
│   ├── activate_env.*
│   ├── start_app.bat
│   └── organize_project.ps1
├── tests/               # Test files
│   ├── test_*.py files
├── utils/               # Utility modules
│   ├── data_processing.py
│   ├── ge_helpers.py
│   ├── report_generator.py
│   └── suite_helpers.py
├── requirements.txt        # Production dependencies
├── requirements_venv.txt   # Full environment dependencies
├── setup.py               # Package setup
└── streamlit_app.py       # Main application entry point
"@
    
    Write-Host $structure -ForegroundColor White
}

function Clean-PythonCache {
    Write-Host "`nCleaning Python cache files..." -ForegroundColor Yellow
    
    $cacheDirs = Get-ChildItem -Path . -Recurse -Directory -Name "__pycache__"
    $pycFiles = Get-ChildItem -Path . -Recurse -File -Include "*.pyc", "*.pyo"
    
    if ($cacheDirs) {
        Remove-Item -Path $cacheDirs -Recurse -Force
        Write-Host "Removed $($cacheDirs.Count) __pycache__ directories" -ForegroundColor Green
    }
    
    if ($pycFiles) {
        Remove-Item -Path $pycFiles -Force
        Write-Host "Removed $($pycFiles.Count) .pyc/.pyo files" -ForegroundColor Green
    }
    
    Write-Host "Cache cleanup completed!" -ForegroundColor Green
}

function Show-Help {
    Write-Host "`nGEWrapper Project Organization Script" -ForegroundColor Cyan
    Write-Host "==========================================`n"
    Write-Host "Usage: .\scripts\organize_project.ps1 [options]`n"
    Write-Host "Options:" -ForegroundColor Yellow
    Write-Host "  -ShowStructure    Display the current project structure"
    Write-Host "  -CleanCache       Remove Python cache files"
    Write-Host "  -Help             Show this help message"
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\scripts\organize_project.ps1 -ShowStructure"
    Write-Host "  .\scripts\organize_project.ps1 -CleanCache"
    Write-Host "  .\scripts\organize_project.ps1 -Help"
}

# Main script logic
if ($Help) {
    Show-Help
}
elseif ($ShowStructure) {
    Show-ProjectStructure
}
elseif ($CleanCache) {
    Clean-PythonCache
}
else {
    # Default: show structure
    Show-ProjectStructure
    Write-Host "`nTip: Use -Help for more options" -ForegroundColor Cyan
}
