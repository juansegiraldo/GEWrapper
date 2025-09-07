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
- Python 3.8 or higher (tested with Python 3.13)
- Git
- Windows PowerShell (for Windows users)

### Installation

⚠️ **Important**: Due to dependency conflicts between numpy, streamlit, and great-expectations, we need to follow a specific installation order.

```powershell
# Clone the repository
git clone https://github.com/juansegiraldo/GEWrapper.git
cd GEWrapper

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\Activate.ps1

# Upgrade pip and install build tools
python -m pip install --upgrade pip
pip install setuptools wheel

# Install streamlit first (this will install compatible numpy)
pip install streamlit

# Install other core dependencies
pip install plotly openpyxl xlrd sqlalchemy pydantic pandasql sqlparse

# Install OpenAI integration dependencies
pip install openai python-dotenv

# Install great-expectations without dependencies (to avoid conflicts)
pip install great-expectations --no-deps

# Install great-expectations dependencies manually
pip install cryptography ipython ipywidgets jsonpatch makefun mistune nbformat notebook pyparsing scipy tqdm tzlocal

# Fix version conflicts
pip install "marshmallow<4.0.0,>=3.7.1"
pip install "altair<5.0.0,>=4.2.1"

# Launch the application
streamlit run streamlit_app.py
```

**Alternative**: Use the pre-configured requirements file (if the above doesn't work):
```powershell
# Use the working requirements file
pip install -r requirements_venv.txt
```

**That's it!** Your DataWash by Stratesys application will open in your default browser at `http://localhost:8501`

### Troubleshooting Installation Issues

If you encounter dependency conflicts:

1. **Numpy compilation errors**: The installation above uses pre-compiled wheels
2. **Great Expectations import errors**: Make sure marshmallow and altair are the correct versions
3. **Streamlit not starting**: Check that all dependencies are installed in the correct order

For a complete working environment, use the `requirements_venv.txt` file which contains tested, compatible versions.

---

## Key Features

### **Data Validation Engine**
- **AI-Powered SQL Generation**: Generate validation queries using OpenAI GPT-5
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
│   ├── openai_sql_generator.py      # AI-powered SQL query generation
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
│   ├── data_processing.py         # Data loading, profiling, and export utilities
│   ├── ge_helpers.py             # Great Expectations integration and validation
│   ├── report_generator.py       # Report generation and visualization
│   ├── smart_template_engine.py  # Intelligent validation template generation
│   └── suite_helpers.py          # Suite management and naming utilities
└── 🚀 scripts/             # Automation and utility scripts
```

---

## 🛠️ Utils Directory - Utility Functions & Helpers

The `utils/` directory contains essential utility functions and helpers that power the core functionality of DataWash by Stratesys. These utilities work together to provide a robust, enterprise-grade data validation platform.

### 📊 **data_processing.py** - Data Processing Engine
**The backbone of data operations** - handles all data loading, processing, and analysis:

**🔧 Core Features:**
- **Multi-format File Loading**: Supports CSV, Excel, JSON, and Parquet with intelligent encoding detection
- **Comprehensive Data Profiling**: Generates detailed data quality metrics, statistics, and insights
- **Smart Data Cleaning**: Automatically cleans column names, converts data types, and handles missing values
- **Intelligent Sampling**: Preserves data characteristics while reducing processing time
- **Export Capabilities**: Multiple format support (CSV, JSON, Excel, HTML, Parquet)
- **Row UUID Management**: Adds stable identifiers for reliable data tracking

**🎯 Key Methods:**
```python
DataProcessor.load_file()           # Load files with encoding fallbacks
DataProcessor.get_data_profile()    # Generate comprehensive data profiles
DataProcessor.clean_column_names()  # SQL-compatible column naming
DataProcessor.sample_data_smart()   # Intelligent data sampling
DataProcessor.export_to_format()    # Multi-format data export
```

### 🎯 **ge_helpers.py** - Great Expectations Integration
**The validation engine** - manages all Great Expectations operations with robust error handling:

**🔧 Core Features:**
- **Context Management**: Initializes and manages GE contexts across versions
- **Expectation Suite Creation**: Creates and manages validation suites
- **Robust Validation Engine**: Multiple fallback methods for reliable validation
- **Manual Validation System**: Custom validation when GE APIs fail
- **Expectation Management**: Adds expectations with comprehensive error handling
- **Data Documentation**: Generates data docs and exports suites

**🎯 Key Methods:**
```python
GEHelpers.initialize_context()      # Set up GE context
GEHelpers.create_expectation_suite() # Create validation suites
GEHelpers.validate_data()           # Execute validation with fallbacks
GEHelpers.add_expectation_to_suite() # Add validation rules
GEHelpers.get_available_expectations() # List supported validations
```

### 📈 **report_generator.py** - Reporting & Visualization
**The reporting powerhouse** - creates comprehensive reports and interactive visualizations:

**🔧 Core Features:**
- **Interactive Charts**: Plotly-based success rates, failure analysis, and data quality metrics
- **Comprehensive Reports**: HTML reports with detailed validation results
- **Failed Records Analysis**: Identifies and analyzes problematic data rows
- **Data Distribution Charts**: Visualizes data patterns and distributions
- **Multiple Chart Types**: Donut charts, bar charts, histograms, and more
- **Export Capabilities**: Generate reports in multiple formats

**🎯 Key Methods:**
```python
ReportGenerator.create_summary_metrics()     # Generate validation statistics
ReportGenerator.create_success_rate_chart()  # Interactive success rate visualization
ReportGenerator.create_failed_records_dataset() # Analyze failed data rows
ReportGenerator.generate_html_report()       # Comprehensive HTML reports
ReportGenerator.create_data_distribution_charts() # Data visualization
```

### 🧠 **smart_template_engine.py** - Intelligent Template Generation
**The AI-powered analyzer** - automatically generates intelligent validation templates:

**🔧 Core Features:**
- **Smart Basic Quality**: Generates intelligent quality checks based on data characteristics
- **Numeric Validation**: Creates statistical-based range validations using IQR and outlier analysis
- **Text Validation**: Detects email columns, creates length validations, and categorical checks
- **Business Rules**: Identifies common patterns (age, percentages, currency, phone numbers)
- **Pattern Recognition**: Automatically detects data types and applies appropriate validations
- **Adaptive Thresholds**: Uses data-driven thresholds rather than fixed values

**🎯 Key Methods:**
```python
SmartTemplateEngine.analyze_data_for_template() # Main analysis entry point
SmartTemplateEngine._generate_smart_basic_quality() # Basic quality checks
SmartTemplateEngine._generate_smart_numeric_validation() # Numeric validations
SmartTemplateEngine._generate_smart_text_validation() # Text validations
SmartTemplateEngine._generate_smart_business_rules() # Business rule detection
```

### 🏷️ **suite_helpers.py** - Suite Management Utilities
**The organizational backbone** - manages expectation suite naming and organization:

**🔧 Core Features:**
- **Suite Name Generation**: Creates unique, timestamped suite names
- **Filename Cleaning**: Sanitizes filenames for safe use in suite names
- **Timestamp Management**: Handles timestamp formatting for suite identification

**🎯 Key Methods:**
```python
generate_suite_name()    # Create unique suite names
get_clean_filename()     # Sanitize filenames
```

### 🔄 **How Utils Work Together**

These utilities form a powerful, integrated system:

1. **Data Processing** loads and prepares your data with intelligent cleaning and profiling
2. **Smart Template Engine** analyzes the data and suggests appropriate validation rules
3. **GE Helpers** creates and manages the expectation suites with robust error handling
4. **Report Generator** creates comprehensive reports and visualizations
5. **Suite Helpers** manages naming and organization for easy tracking

**🛡️ Enterprise-Grade Features:**
- **Robust Error Handling**: Extensive fallback mechanisms ensure reliability
- **Version Compatibility**: Works across different Great Expectations versions
- **Performance Optimization**: Smart sampling and efficient processing
- **Comprehensive Logging**: Detailed debugging and error reporting
- **Modular Design**: Clean, maintainable, and extensible architecture

---

## Documentation

Our comprehensive documentation has been consolidated and organized for easy navigation:

### 🚀 Essential Guides
| Guide | Description | Use Case |
|-------|-------------|----------|
| 📚 [**Docs Index**](docs/INDEX.md) | Complete documentation navigation | Find any guide quickly |
| 📖 [**Installation Guide**](docs/INSTALL_GUIDE.md) | Complete setup with troubleshooting | Getting started, resolving issues |
| 🚀 [**User Guide**](docs/USER_GUIDE.md) | End-to-end workflow walkthrough | Daily usage and operations |
| 🔧 [**Troubleshooting Guide**](docs/TROUBLESHOOTING.md) | Comprehensive problem resolution | When anything goes wrong |

### 📘 Learning Resources
| Guide | Description | Use Case |
|-------|-------------|----------|
| 📘 [**Tutorials**](docs/TUTORIALS.md) | Hands-on walkthroughs | Learn by example |
| 🤖 [**OpenAI Integration**](OPENAI_INTEGRATION.md) | AI-powered SQL query generation | Generate queries with GPT-5 |
| 🔍 [**Custom SQL Guide**](docs/CUSTOM_SQL_GUIDE.md) | Advanced SQL validation patterns | Complex business rules |
| 🗃️ [**SQL Quick Reference**](docs/SQL_QUICK_REFERENCE.md) | Copy-paste SQL examples | Quick SQL queries |
| ❓ [**FAQ**](docs/FAQ.md) | Quick answers to common questions | Instant help |

### 🛠️ Technical Documentation
| Guide | Description | Use Case |
|-------|-------------|----------|
| 🛠️ [**Developer Guide**](docs/DEVELOPER_GUIDE.md) | For contributors and developers | Extend and contribute |
| 🔧 [**Configuration**](docs/CONFIGURATION.md) | Settings and customization | Advanced configuration |
| 📋 [**Project Summary**](docs/PROJECT_SUMMARY.md) | Technical architecture overview | Understand the platform |
| 🧭 [**Roadmap**](docs/roadmap.md) | Feature development milestones | What's coming next |

**📝 All documentation is now cross-referenced and consolidated to eliminate duplication while ensuring comprehensive coverage.**

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

# Install development dependencies (use the working requirements file)
pip install -r requirements_venv.txt

# Or follow the manual installation procedure above for troubleshooting
```

**Note**: The `requirements_venv.txt` file contains tested, compatible versions that work together. If you encounter issues, follow the manual installation steps in the Quick Start section.

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
