# 🔬 Comprehensive Data Quality QA Testing System

## Overview

This system automatically tests **ALL** your data quality expectation types with various scenarios and edge cases, outputting results to easy-to-analyze CSV files.

**No more manual testing one expectation at a time!**

## What It Tests

✅ **16+ Expectation Types:**
- Table-level: row count, column structure
- Column validation: null checks, uniqueness, data types, value sets, ranges
- String validation: length, regex patterns
- Statistical: mean, median, standard deviation, sum
- Date/time: format validation, parsing
- Custom SQL: complex business rules

✅ **Multiple Data Scenarios:**
- Clean data (should pass)
- Data with nulls (should fail null checks)
- Data with duplicates (should fail uniqueness)
- Data with type issues (should fail type checks)
- Data with range violations (should fail range checks)
- Data with format issues (should fail format checks)
- Edge cases (boundary conditions)

## Quick Start

### Option 1: Windows Batch File (Easiest)
```bash
# Just double-click this file:
run_qa_tests.bat
```

### Option 2: Python Command Line
```bash
# Run comprehensive tests
python tests/simple_qa_runner.py

# Analyze the results
python analyze_qa_results.py
```

## Output Files

After running tests, you'll get:

1. **`qa_test_results_TIMESTAMP.csv`** - Detailed results for every test
   - Columns: expectation_type, test_scenario, test_passed, execution_time, error_message, etc.
   
2. **`qa_summary_TIMESTAMP.csv`** - Summary statistics  
   - Overall success rates, performance metrics, category breakdowns

## Example Results Analysis

```
📊 QA TEST RESULTS ANALYSIS
================================================================================
🔢 OVERALL RESULTS:
   Total Tests: 112
   Passed: 89 ✅
   Failed: 23 ❌
   Success Rate: 79.5%

📋 RESULTS BY CATEGORY:
   Table Level: 100.0% (8/8)
   Column Validation: 75.0% (48/64)
   Statistical: 85.7% (18/21)
   Format Pattern: 72.2% (13/18)
   Custom Sql: 100.0% (2/2)

🎭 RESULTS BY TEST SCENARIO:
   Clean Data Pass: 95.8% (23/24)
   Edge Cases: 45.8% (11/24)
   With Nulls Fail: 87.5% (14/16)
   With Duplicates Fail: 100.0% (8/8)
```

## Use Cases

### 🔍 **Before Production**
Run comprehensive tests to ensure your expectations work correctly with various data scenarios.

### 🚀 **Regression Testing**  
Run after code changes to make sure you didn't break any expectations.

### 📊 **Quality Assessment**
Understand which expectation types work best with your data patterns.

### 🐛 **Debugging**
Quickly identify which expectations fail and why.

## Customization

### Test Only Specific Expectations
Edit `simple_qa_runner.py` and modify the `expectation_types` list:

```python
# Test only null and uniqueness checks
quick_expectations = [
    "expect_column_values_to_not_be_null",
    "expect_column_values_to_be_unique"
]
runner.run_quick_test(quick_expectations)
```

### Adjust Dataset Size
Change the dataset size in test scenarios:

```python
# Generate larger test datasets
test_data = data_generator_method(rows=10000)  # Instead of 100
```

### Add Your Own Test Scenarios
Extend the `SyntheticDataGenerator` class with your own data generation methods.

## Advanced Analysis

### Excel/Google Sheets
Import the CSV files for pivot tables, charts, and detailed analysis.

### Python Analysis
```python
import pandas as pd

# Load results
df = pd.read_csv('qa_test_results_TIMESTAMP.csv')

# Analyze failure patterns
failed_tests = df[df['test_passed'] == False]
failure_patterns = failed_tests.groupby(['expectation_category', 'test_scenario']).size()
print(failure_patterns)
```

## Troubleshooting

### Import Errors
Make sure you're running from the project root directory:
```bash
cd D:\Users\juan.giraldo\Desktop\CodingCamp\GEWrapper
python tests/simple_qa_runner.py
```

### Missing Dependencies
If you get import errors, install missing packages:
```bash
pip install pandas numpy great-expectations
```

### No Results Generated
Check that the tests actually ran by looking for error messages in the console output.

## Files Created

- `tests/comprehensive_qa_framework.py` - Core testing framework
- `tests/simple_qa_runner.py` - Simple runner that outputs CSV
- `analyze_qa_results.py` - Results analysis script  
- `run_qa_tests.bat` - Windows batch file for easy running
- `QA_TESTING_README.md` - This documentation

## Next Steps

1. **Run the tests** to get your baseline results
2. **Analyze the CSV** to understand your data quality patterns
3. **Fix failing expectations** or adjust them based on insights
4. **Set up regular testing** as part of your data pipeline

Happy testing! 🎉