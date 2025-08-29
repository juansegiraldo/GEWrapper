@echo off
echo Activating GEWrapper Virtual Environment...
call gewrapper_env\Scripts\activate.bat
echo.
echo Virtual environment activated! You can now run:
echo   python -m streamlit run streamlit_app.py
echo.
echo Or use the start_app.bat file to run the app directly.
pause
