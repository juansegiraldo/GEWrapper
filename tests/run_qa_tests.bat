@echo off
echo ===============================================
echo  Data Quality QA Test Runner
echo ===============================================
echo.

cd /d "%~dp0"

echo Running comprehensive QA tests...
echo.

python tests/simple_qa_runner.py

echo.
echo ===============================================
echo Tests completed! Check the generated CSV files.
echo ===============================================
pause