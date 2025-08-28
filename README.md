# DataWashCopiaMia - Great Expectations Streamlit Wrapper

A comprehensive Streamlit web application that provides a user-friendly interface for Great Expectations data validation functionality. This application enables users to perform data validation, profiling, and quality assessment without requiring direct coding knowledge.

## 🚀 Features

### Core Functionality
- **Multi-format Data Upload**: Support for CSV, JSON, Parquet, and Excel files
- **Interactive Data Profiling**: Comprehensive data analysis with statistics and visualizations  
- **Visual Expectation Builder**: Intuitive interface for creating data validation rules
- **Real-time Validation**: Execute expectations with progress tracking
- **Rich Results Dashboard**: Interactive charts and detailed reporting
- **Export Capabilities**: Generate HTML, PDF, JSON, and CSV reports

### Data Validation Capabilities
- **Column-level Expectations**: Null checks, data types, value ranges, regex patterns
- **Table-level Expectations**: Row counts, column presence, uniqueness constraints
- **Statistical Validations**: Mean, median, standard deviation checks
- **Custom Templates**: Pre-configured expectation suites for common scenarios

### Advanced Features
- **Smart Data Sampling**: Handle large datasets efficiently
- **Step-by-step Validation**: Progressive validation with real-time feedback
- **Import/Export Suites**: Save and reuse expectation configurations
- **Data Quality Scoring**: Automatic assessment with actionable recommendations

## 📋 Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## 🛠️ Installation

1. Clone or download the project:
```bash
git clone <repository-url>
cd GEWrapper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run streamlit_app.py
```

## 📖 Usage Guide

### Step 1: Upload Data
- Navigate to the "Upload Data" section
- Select your data file (CSV, JSON, Parquet, Excel)
- Preview your data and basic statistics

### Step 2: Data Profiling  
- Review comprehensive data profiling
- Analyze column types, missing values, and distributions
- Get optimization suggestions for data types

### Step 3: Configure Expectations
- Choose from predefined templates or build custom expectations
- Configure parameters for each validation rule
- Preview and manage your expectation suite

### Step 4: Run Validation
- Choose validation mode (batch or step-by-step)
- Configure sampling options for large datasets
- Execute validation with real-time progress tracking

### Step 5: View Results
- Analyze results through interactive dashboards
- Review detailed failure information
- Export reports in multiple formats
- Get data quality recommendations

## 📁 Project Structure

```
GEWrapper/
├── streamlit_app.py          # Main application entry point
├── components/               # UI components
│   ├── data_upload.py       # Data upload and profiling
│   ├── expectation_builder.py # Expectation configuration
│   ├── validation_runner.py  # Validation execution
│   └── results_display.py   # Results visualization
├── utils/                   # Utility functions
│   ├── ge_helpers.py        # Great Expectations helpers
│   ├── data_processing.py   # Data processing utilities
│   └── report_generator.py  # Report generation
├── config/                  # Configuration
│   └── app_config.py        # Application settings
├── sample_data/             # Sample datasets for testing
│   ├── customers.csv
│   ├── sales_data.csv
│   └── inventory.json
└── requirements.txt         # Python dependencies
```

## 🧪 Sample Data

The `sample_data/` directory contains example datasets for testing:

- **customers.csv**: Customer information with various data types
- **sales_data.csv**: Transaction data with relationships
- **inventory.json**: Product inventory in JSON format

## 🎯 Use Cases

### Data Quality Monitoring
- Validate daily data feeds
- Monitor data pipeline health  
- Ensure data consistency across systems

### Data Migration Validation
- Verify data integrity after migrations
- Validate row counts and relationships
- Check data type preservation

### Exploratory Data Analysis
- Profile new datasets quickly
- Identify data quality issues
- Generate data documentation

### Compliance Reporting
- Create audit trails for data quality
- Generate compliance reports
- Track data quality metrics over time

## 🔧 Configuration

### Application Settings
Modify `config/app_config.py` to customize:
- File upload limits
- Sampling thresholds  
- UI preferences
- Export formats
- Expectation templates

### Great Expectations Integration
The application uses Great Expectations for validation logic:
- Temporary contexts for isolation
- JSON-based suite serialization
- Comprehensive result formatting

## 📊 Supported Expectations

### Table-level
- Row count validation
- Column presence checks
- Duplicate detection

### Column-level  
- Null value validation
- Data type verification
- Value range checks
- Pattern matching (regex)
- Set membership validation
- Statistical constraints

### Advanced
- Cross-column relationships
- Custom business rules
- Multi-column constraints

## 🚨 Troubleshooting

### Common Issues

**File Upload Errors**
- Check file size limits (100MB default)
- Verify file format compatibility
- Try different encoding if CSV fails

**Memory Issues with Large Files**
- Enable data sampling
- Reduce sample size
- Use Parquet format for better performance

**Validation Failures**
- Check expectation parameters
- Verify column names match exactly
- Review data types for numeric validations

### Performance Tips
- Use sampling for datasets > 10,000 rows
- Choose batch validation for faster execution
- Optimize expectation complexity

## 🤝 Contributing

1. Fork the repository
2. Create feature branches
3. Add comprehensive tests
4. Update documentation
5. Submit pull requests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built on [Great Expectations](https://greatexpectations.io/)
- UI powered by [Streamlit](https://streamlit.io/)
- Visualizations using [Plotly](https://plotly.com/)

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review sample data examples  
3. Create GitHub issues for bugs
4. Contribute improvements via pull requests

---

**DataWashCopiaMia** - Making data validation accessible to everyone! 🧹✨