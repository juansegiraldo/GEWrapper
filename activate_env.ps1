Write-Host "Activating GEWrapper Virtual Environment..." -ForegroundColor Green
& ".\gewrapper_env\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Virtual environment activated! You can now run:" -ForegroundColor Yellow
Write-Host "  python -m streamlit run streamlit_app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Or use the start_app.bat file to run the app directly." -ForegroundColor Yellow
Write-Host ""
Write-Host "To deactivate the environment, type: deactivate" -ForegroundColor Gray
