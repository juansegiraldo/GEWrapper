@echo off
echo Starting DataWashCopiaMia with Virtual Environment...
call gewrapper_env\Scripts\activate.bat
streamlit run streamlit_app.py
pause
