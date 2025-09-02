# DataWash by Stratesys - Data Quality Made Simple

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Great Expectations](https://img.shields.io/badge/Great%20Expectations-0.17+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

**A powerful, enterprise-grade data validation platform built with Great Expectations and Streamlit**

*Data Quality Made Simple* • *v0.2*

<img src="docs/assets/hero.gif" alt="DataWash demo" width="720"/>

[Quick Start](#quick-start) • [Documentation](#documentation) • [Features](#key-features) • [Development](#development)

</div>

---

## What is DataWash by Stratesys?

**DataWash by Stratesys** is a comprehensive data validation and quality assurance platform that combines the power of Great Expectations with an intuitive Streamlit interface. It's designed for data engineers, analysts, and scientists who need robust data validation capabilities with the flexibility of custom SQL queries and automated reporting.

### Why Choose DataWash by Stratesys?

- **Advanced Validation**: Custom SQL-based validation rules with Great Expectations
- **Interactive UI**: Beautiful Streamlit interface for seamless user experience
- **Comprehensive Reporting**: Automated validation reports and failure analysis
- **Workflow Automation**: Streamlined data validation pipelines
- **Enterprise Ready**: Production-grade architecture with proper error handling

---

## Quick Start

### Prerequisites
- Python 3.8 or higher
- Git
- Windows PowerShell (for Windows users)

### Installation

```powershell
# Clone the repository
git clone https://github.com/juansegiraldo/GEWrapper.git
cd GEWrapper

# Activate virtual environment
.\scripts\activate_env.ps1

# Install dependencies
pip install -r requirements.txt

# Launch the application
streamlit run streamlit_app.py
```

**That's it!** Your DataWash by Stratesys application will open in your default browser at `http://localhost:8501`

---

## Key Features

### **Data Validation Engine**
- **Custom SQL Expectations**: Create complex validation rules using SQL syntax
- **Built-in Validators**: Pre-configured validators for common data quality checks
- **Batch Processing**: Validate large datasets efficiently
- **Real-time Validation**: Instant feedback on data quality

### **Data Management**
- **Multi-format Support**: CSV, JSON, Excel, and more
- **Data Upload Interface**: Drag-and-drop file uploads
- **Data Preview**: Interactive data exploration before validation
- **Processing Pipeline**: Automated data cleaning and transformation

### **Results & Reporting**
- **Interactive Dashboards**: Real-time validation results visualization
- **Failed Records Analysis**: Detailed breakdown of validation failures
- **Export Capabilities**: Generate reports in multiple formats
- **Historical Tracking**: Maintain validation history and trends

### **Developer Experience**
- **Modular Architecture**: Clean, maintainable codebase
- **Comprehensive Testing**: Full test coverage with pytest
- **Configuration Management**: Flexible configuration system
- **API Integration**: Ready for CI/CD pipeline integration

---

## Project Architecture

```
GEWrapper/
├── components/          # Core application components
│   ├── custom_sql_expectations.py    # SQL-based validation engine
│   ├── data_upload.py               # File upload and processing
│   ├── expectation_builder.py       # Validation rule builder
│   ├── failed_records_generator.py  # Failure analysis
│   ├── results_display.py           # Results visualization
│   ├── sql_query_builder.py         # SQL query interface
│   └── validation_runner.py         # Validation execution engine
├── ⚙️ config/              # Configuration and settings
│   ├── app_config.py               # Application configuration
│   ├── default_suite.json          # Default validation suite
│   ├── sample_expectations.json    # Example validation rules
│   └── sample_custom_sql_expectations.json # SQL validation templates (samples)
├── 📊 data/                # Data storage and samples
│   ├── output/             # Generated reports and exports
│   ├── processed/          # Processed data files
│   └── sample_data/        # Sample datasets for testing
├── 📚 docs/                # Comprehensive documentation
│   ├── README.md                 # Docs index and navigation
│   ├── INSTALL_GUIDE.md          # Setup and installation
│   ├── USER_GUIDE.md             # End-to-end usage
│   ├── CUSTOM_SQL_GUIDE.md       # SQL validation guide
│   ├── SQL_QUICK_REFERENCE.md    # SQL syntax reference
│   ├── FAILED_RECORDS_GUIDE.md   # Failure analysis guide
│   ├── CONFIGURATION.md          # Settings and env vars
│   ├── PROJECT_SUMMARY.md        # Technical overview
│   ├── VENV_SETUP.md             # Virtual environment guide
│   └── roadmap.md                # Milestones
├── 🧪 tests/               # Test suite and validation
├── 🛠️ utils/               # Utility functions and helpers
└── 🚀 scripts/             # Automation and utility scripts
```

---

## Documentation

Our comprehensive documentation covers every aspect of DataWash by Stratesys:

| Guide | Description | Use Case |
|-------|-------------|----------|
| 📚 [Docs Index](docs/INDEX.md) | Navigation for all docs | Find the right guide fast |
| 📖 [Installation Guide](docs/INSTALL_GUIDE.md) | Setup and configuration | Getting started |
| 🚀 [User Guide](docs/USER_GUIDE.md) | End-to-end app workflow | Everyday usage |
| 📘 [Tutorials](docs/TUTORIALS.md) | Hands-on walkthroughs | Learn by example |
| ❓ [FAQ](docs/FAQ.md) | Common questions | Quick answers |
| 🔧 [Configuration](docs/CONFIGURATION.md) | Settings and env vars | Tune defaults |
| 🔍 [Custom SQL Guide](docs/CUSTOM_SQL_GUIDE.md) | SQL-based validations | Business rules |
| 🗃️ [SQL Quick Reference](docs/SQL_QUICK_REFERENCE.md) | SQL syntax & examples | Write queries |
| ❌ [Failed Records Guide](docs/FAILED_RECORDS_GUIDE.md) | Failure analysis | Troubleshooting data |
| 📋 [Project Summary](docs/PROJECT_SUMMARY.md) | Technical overview | Understand platform |
| 🧪 [VENV Setup](docs/VENV_SETUP.md) | Virtual env usage | Local dev |
| 🧭 [Roadmap](docs/roadmap.md) | Milestones | What's next |
| 🛠️ [Developer Guide](docs/DEVELOPER_GUIDE.md) | For contributors | Extend the app |

---

## Development

### Running Tests

```powershell
# Run complete test suite
python -m pytest tests/ -v

# Run specific test category
python -m pytest tests/test_validation/ -v

# Run with coverage report
python -m pytest tests/ --cov=components --cov-report=html
```

### Development Environment

```powershell
# Create development environment
python -m venv gewrapper_dev

# Activate environment
.\gewrapper_dev\Scripts\Activate.ps1

# Install development dependencies
pip install -r requirements_venv.txt

# Install pre-commit hooks
pre-commit install
```

### Code Quality

- **Type Hints**: Full type annotation support
- **Linting**: Flake8 and Black code formatting
- **Testing**: Comprehensive pytest coverage
- **Documentation**: Inline docstrings and external guides

---

## Sample Data & Use Cases

GEWrapper includes comprehensive sample datasets for testing and learning:

| Dataset | Description | Use Case |
|---------|-------------|----------|
| `customers.csv` | Customer information with validation rules | Customer data quality checks |
| `sales_data.csv` | Sales transactions with business rules | Sales data validation |
| `inventory.json` | Inventory management data | Stock level validation |
| `test_data_with_issues.csv` | Data with known problems | Testing validation rules |

### Example Validation Scenarios

- **Data Completeness**: Ensure required fields are populated
- **Data Format**: Validate email addresses, phone numbers, dates
- **Business Rules**: Check salary ranges, inventory levels
- **Data Relationships**: Validate foreign key constraints
- **Statistical Validation**: Outlier detection and distribution checks

---

## Configuration & Customization

### Application Settings

```python
# config/app_config.py
APP_CONFIG = {
    "max_file_size": "100MB",
    "supported_formats": ["csv", "json", "xlsx"],
    "validation_timeout": 300,
    "enable_advanced_features": True
}
```

### Validation Suites

```json
{
    "suite_name": "sales_validation",
    "expectations": [
        {
            "expectation_type": "expect_column_values_to_be_between",
            "kwargs": {
                "column": "salary",
                "min_value": 30000,
                "max_value": 200000
            }
        }
    ]
}
```

---

## Deployment Options

### Local Development
```powershell
streamlit run streamlit_app.py --server.port 8501
```

### Production Deployment
```powershell
# Using Streamlit Cloud
streamlit deploy

# Using Docker
docker build -t gewrapper .
docker run -p 8501:8501 gewrapper
```

### Cloud Platforms
- **Streamlit Cloud**: One-click deployment
- **AWS**: EC2 with load balancer
- **Azure**: App Service deployment
- **Google Cloud**: Cloud Run containerization

---

## Contributing

We welcome contributions from the community! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add tests for new features
- Update documentation as needed
- Use meaningful commit messages

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**DataWash by Stratesys** is part of the **CodingCamp** initiative, dedicated to advancing data quality and validation practices in the data engineering community.

---

## Acknowledgments

- **Great Expectations Team** for the powerful validation framework
- **Streamlit Team** for the amazing web app framework
- **CodingCamp Community** for inspiration and support
- **Open Source Contributors** who make projects like this possible

---

<div align="center">

**Made with ❤️ by [Stratesys](https://www.stratesys-ts.com/)**

**Developed by [Juan Giraldo](https://www.linkedin.com/in/juan-sebastian-giraldo/)**  
**Product: DataWash by [Stratesys](https://www.stratesys-ts.com/) v0.2**

[🌐 Website](https://github.com/juansegiraldo/GEWrapper) • [📧 Contact](mailto:juan.giraldo@stratesys-ts.com) • [🐛 Issues](https://github.com/juansegiraldo/GEWrapper/issues)

**© 2025 All Rights Reserved**  
**Data Quality Made Simple**  
**Happy Data Validating! 🎉**

</div>
