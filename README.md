# GEWrapper - Great Expectations Data Validation Tool

A comprehensive Streamlit application for data validation using Great Expectations with custom SQL query capabilities.

## 🚀 Quick Start

```powershell
# Activate virtual environment
.\scripts\activate_env.ps1

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run streamlit_app.py
```

## 📁 Project Structure

```
GEWrapper/
├── 📁 components/           # Core application components
│   ├── custom_sql_expectations.py
│   ├── data_upload.py
│   ├── expectation_builder.py
│   ├── failed_records_generator.py
│   ├── results_display.py
│   ├── sql_query_builder.py
│   └── validation_runner.py
├── 📁 config/              # Configuration files
│   ├── app_config.py
│   ├── default_suite.json
│   ├── sales_salary_validation.json
│   ├── sample_custom_sql_expectations.json
│   └── sample_expectations.json
├── 📁 data/                # Data files
│   ├── 📁 output/          # Generated output files
│   ├── 📁 processed/       # Processed data files
│   └── 📁 sample_data/     # Sample datasets
│       ├── customers.csv
│       ├── inventory.json
│       ├── sales_data.csv
│       └── test_data_with_issues.csv
├── 📁 docs/                # Documentation
│   ├── CUSTOM_SQL_GUIDE.md
│   ├── FAILED_RECORDS_GUIDE.md
│   ├── INSTALL_GUIDE.md
│   ├── PROJECT_SUMMARY.md
│   ├── README.md
│   ├── SQL_QUICK_REFERENCE.md
│   ├── VENV_SETUP.md
│   └── roadmap.md
├── 📁 scripts/             # Utility scripts
│   ├── activate_env.bat
│   ├── activate_env.ps1
│   └── start_app.bat
├── 📁 tests/               # Test files
│   ├── test_app_data_loading.py
│   ├── test_boolean_fix.py
│   ├── test_download.py
│   ├── test_sales_validation.py
│   ├── test_streamlit_app.py
│   └── test_validation_fix.py
├── 📁 utils/               # Utility modules
│   ├── data_processing.py
│   ├── ge_helpers.py
│   ├── report_generator.py
│   └── suite_helpers.py
├── 📁 gewrapper_env/       # Virtual environment
├── requirements.txt        # Production dependencies
├── requirements_venv.txt   # Full environment dependencies
├── setup.py               # Package setup
└── streamlit_app.py       # Main application entry point
```

## 🎯 Key Features

- **Custom SQL Query Builder**: Create complex data validation rules using SQL
- **Data Upload & Processing**: Support for CSV, JSON, and other data formats
- **Expectation Management**: Build, save, and reuse validation expectations
- **Results Visualization**: Interactive displays of validation results
- **Failed Records Analysis**: Detailed analysis of validation failures
- **Report Generation**: Automated report creation for validation results

## 📚 Documentation

- **[Installation Guide](docs/INSTALL_GUIDE.md)**: Complete setup instructions
- **[Custom SQL Guide](docs/CUSTOM_SQL_GUIDE.md)**: How to create custom SQL validations
- **[Failed Records Guide](docs/FAILED_RECORDS_GUIDE.md)**: Understanding validation failures
- **[SQL Quick Reference](docs/SQL_QUICK_REFERENCE.md)**: SQL syntax and examples
- **[Project Summary](docs/PROJECT_SUMMARY.md)**: Detailed project overview

## 🛠️ Development

### Running Tests
```powershell
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_sales_validation.py
```

### Environment Setup
```powershell
# Create virtual environment
python -m venv gewrapper_env

# Activate (Windows)
.\scripts\activate_env.ps1

# Install dependencies
pip install -r requirements_venv.txt
```

## 📊 Sample Data

The application includes sample datasets in `data/sample_data/`:
- `customers.csv`: Customer information
- `sales_data.csv`: Sales transaction data
- `inventory.json`: Inventory management data
- `test_data_with_issues.csv`: Data with known validation issues

## 🔧 Configuration

Configuration files are stored in `config/`:
- `app_config.py`: Application settings
- `default_suite.json`: Default validation suite
- `sample_expectations.json`: Example expectations

## 📝 License

This project is part of the CodingCamp initiative for data validation and quality assurance.

---

**Happy Data Validating! 🎉**
