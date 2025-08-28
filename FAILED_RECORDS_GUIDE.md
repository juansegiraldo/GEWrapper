# 📊 Failed Records Report Generator

## Overview

The Failed Records Report Generator is a powerful feature that allows you to create comprehensive, downloadable reports of all records that failed validation expectations. This is particularly useful for data quality analysis, debugging, and compliance reporting.

## 🚀 How to Use

### 1. Prerequisites
- You must have run data validation first
- There must be at least one failed expectation
- The original data must be available

### 2. Access the Feature
1. Navigate to the **"📋 View Results"** step in the application
2. Scroll down to the **"📊 Failed Records Report Generator"** section
3. The feature will only appear if there are validation failures

### 3. Configure Report Options

#### Basic Options
- **Report Format**: Choose between CSV, Excel, or JSON
- **Include Validation Metadata**: Add expectation details, failure reasons, and validation context
- **Include Original Record Data**: Include the complete original record data for failed records
- **Group by Expectation Type**: Organize failed records by the expectation that failed

#### Advanced Options
- **Max Records Per File**: Split large reports into multiple files (1,000 - 100,000 records)
- **Include Success Summary**: Add a summary of passed expectations for context
- **Timestamp Format**: Choose between ISO, Readable, or Unix timestamp formats

### 4. Generate and Download
1. Click the **"🔍 Generate Failed Records Report"** button
2. Wait for the generation process to complete
3. Use the **"📥 Download [Format] Report"** button to download your report

## 📋 What You'll Get

### Report Contents
- **Summary Statistics**: Total failed records, failed expectations, affected columns, overall failure rate
- **Breakdown by Expectation Type**: Failure rates for each expectation type and column
- **Detailed Failed Records**: Each failed record with:
  - Row index (if available)
  - Failed expectations list
  - Primary column that failed
  - Failed value
  - Expectation type
  - Failure reason
  - Detailed failure information
  - Original record data (if enabled)
  - Validation metadata (if enabled)

### File Formats

#### CSV Format
- Flattened structure with all information in columns
- Easy to import into Excel, Google Sheets, or data analysis tools
- Includes original data columns if enabled

#### Excel Format
- **Summary Sheet**: Overview and expectation summary
- **Failed Records Sheet**: Detailed failed records data
- Auto-formatted with proper column widths
- Professional appearance suitable for business reports

#### JSON Format
- Structured data format
- Preserves all metadata and relationships
- Easy to process programmatically
- Configurable timestamp formats

## 🔍 Report Preview

Before downloading, you can preview:
- **Sample Failed Records**: First 10 failed records with key information
- **Expectation Summary**: Breakdown of failures by expectation type
- **Total Count**: Number of failed records and expectations

## 💡 Use Cases

### Data Quality Analysis
- Identify patterns in data quality issues
- Track failure rates across different columns
- Monitor data quality over time

### Compliance Reporting
- Generate audit reports for regulatory requirements
- Document data quality issues for stakeholders
- Track data quality metrics

### Debugging and Fixes
- Identify specific records that need attention
- Understand why expectations failed
- Plan data cleaning strategies

### Business Intelligence
- Analyze failure patterns by business context
- Identify data quality hotspots
- Prioritize data quality improvement efforts

## ⚠️ Important Notes

### Performance Considerations
- Large datasets may take time to process
- Consider using data sampling for very large datasets
- Excel files with many records may be large

### Data Privacy
- Failed records reports contain actual data values
- Ensure appropriate access controls are in place
- Consider data anonymization for sensitive information

### Storage
- Reports are generated on-demand and not stored permanently
- Download reports immediately after generation
- Consider archiving important reports externally

## 🛠️ Troubleshooting

### Common Issues

#### "No validation results available"
- Ensure you have run validation first
- Check that validation completed successfully

#### "Original data not available"
- Make sure you haven't cleared the session state
- Re-upload your data if needed

#### "No failed records found"
- All expectations passed successfully
- The generator only works when there are failures

#### Excel export errors
- Ensure `openpyxl` is installed
- Check that the data doesn't contain unsupported characters

### Getting Help
- Check the validation results for detailed error information
- Review the expectation configuration
- Ensure your data format is supported

## 🔄 Integration with Existing Features

The Failed Records Report Generator integrates seamlessly with:
- **Data Upload**: Works with all supported data formats
- **Expectation Builder**: Respects all configured expectations
- **Validation Runner**: Processes results from both batch and step-by-step validation
- **Results Display**: Appears automatically when there are failures

## 📈 Future Enhancements

Planned improvements include:
- **Email Reports**: Send reports directly via email
- **Scheduled Reports**: Automatically generate reports on a schedule
- **Custom Templates**: User-defined report formats
- **API Integration**: Programmatic access to report generation
- **Advanced Filtering**: Filter failed records by custom criteria
- **Trend Analysis**: Track failure patterns over time
