import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import streamlit as st
from jinja2 import Template

class ReportGenerator:
    """Generate reports and visualizations for validation results"""
    
    @staticmethod
    def create_summary_metrics(validation_results: Dict) -> Dict[str, Any]:
        """Create summary metrics from validation results"""
        try:
            # Handle different result structures
            results = []
            
            # Check for GE validation results structure
            if 'results' in validation_results:
                results = validation_results.get('results', [])
            elif 'statistics' in validation_results:
                # Handle statistics-based results
                stats = validation_results.get('statistics', {})
                total_expectations = stats.get('evaluated_expectations', 0)
                successful = stats.get('successful_expectations', 0)
                failed = stats.get('unsuccessful_expectations', 0)
                success_rate = stats.get('success_percent', 0)
                
                # Create expectation types summary
                expectation_types = {}
                if 'results' in validation_results:
                    for result in validation_results['results']:
                        exp_config = result.get('expectation_config', {})
                        exp_type = exp_config.get('type', exp_config.get('expectation_type', 'unknown'))
                        if exp_type not in expectation_types:
                            expectation_types[exp_type] = {'total': 0, 'passed': 0}
                        expectation_types[exp_type]['total'] += 1
                        if result.get('success', False):
                            expectation_types[exp_type]['passed'] += 1
                
                return {
                    'total_expectations': total_expectations,
                    'successful': successful,
                    'failed': failed,
                    'success_rate': success_rate,
                    'expectation_types': expectation_types,
                    'run_time': validation_results.get('meta', {}).get('execution_time', 'Unknown')
                }
            
            # Standard results processing
            total_expectations = len(results)
            successful = sum(1 for r in results if r.get('success', False))
            failed = total_expectations - successful
            
            success_rate = (successful / total_expectations * 100) if total_expectations > 0 else 0
            
            # Group by expectation type
            expectation_types = {}
            for result in results:
                exp_config = result.get('expectation_config', {})
                exp_type = exp_config.get('type', exp_config.get('expectation_type', 'unknown'))
                if exp_type not in expectation_types:
                    expectation_types[exp_type] = {'total': 0, 'passed': 0}
                expectation_types[exp_type]['total'] += 1
                if result.get('success', False):
                    expectation_types[exp_type]['passed'] += 1
            
            return {
                'total_expectations': total_expectations,
                'successful': successful,
                'failed': failed,
                'success_rate': success_rate,
                'expectation_types': expectation_types,
                'run_time': validation_results.get('meta', {}).get('run_id', {}).get('run_time', 'Unknown')
            }
        except Exception as e:
            st.error(f"Error creating summary metrics: {str(e)}")
            return {}
    
    @staticmethod
    def create_success_rate_chart(summary_metrics: Dict) -> go.Figure:
        """Create success rate donut chart"""
        try:
            fig = go.Figure(data=[go.Pie(
                labels=['Passed', 'Failed'],
                values=[summary_metrics['successful'], summary_metrics['failed']],
                hole=0.6,
                marker_colors=['#2ca02c', '#d62728'],
                textinfo='label+percent',
                textposition='outside'
            )])
            
            fig.update_layout(
                title=f"Overall Success Rate: {summary_metrics['success_rate']:.1f}%",
                font=dict(size=14),
                height=400,
                showlegend=True,
                annotations=[dict(text=f"{summary_metrics['successful']}/{summary_metrics['total_expectations']}", 
                                x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            
            return fig
        except Exception as e:
            st.error(f"Error creating success rate chart: {str(e)}")
            return go.Figure()
    
    @staticmethod
    def create_expectation_type_chart(summary_metrics: Dict) -> go.Figure:
        """Create chart showing results by expectation type"""
        try:
            types = list(summary_metrics['expectation_types'].keys())
            passed = [summary_metrics['expectation_types'][t]['passed'] for t in types]
            failed = [summary_metrics['expectation_types'][t]['total'] - 
                     summary_metrics['expectation_types'][t]['passed'] for t in types]
            
            fig = go.Figure(data=[
                go.Bar(name='Passed', x=types, y=passed, marker_color='#2ca02c'),
                go.Bar(name='Failed', x=types, y=failed, marker_color='#d62728')
            ])
            
            fig.update_layout(
                barmode='stack',
                title='Results by Expectation Type',
                xaxis_title='Expectation Type',
                yaxis_title='Count',
                height=400,
                xaxis_tickangle=-45
            )
            
            return fig
        except Exception as e:
            st.error(f"Error creating expectation type chart: {str(e)}")
            return go.Figure()
    
    @staticmethod
    def create_column_quality_chart(validation_results: Dict, data: pd.DataFrame) -> go.Figure:
        """Create chart showing data quality by column"""
        try:
            results = validation_results.get('results', [])
            
            # Group results by column
            column_results = {}
            for result in results:
                exp_config = result.get('expectation_config', {})
                column = exp_config.get('column')
                
                if column:
                    if column not in column_results:
                        column_results[column] = {'total': 0, 'passed': 0}
                    column_results[column]['total'] += 1
                    if result.get('success', False):
                        column_results[column]['passed'] += 1
            
            if not column_results:
                return go.Figure()
            
            columns = list(column_results.keys())
            success_rates = [column_results[col]['passed'] / column_results[col]['total'] * 100 
                           for col in columns]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=columns,
                    y=success_rates,
                    marker_color=['#2ca02c' if rate == 100 else '#ff7f0e' if rate >= 80 else '#d62728' 
                                for rate in success_rates],
                    text=[f"{rate:.1f}%" for rate in success_rates],
                    textposition='auto'
                )
            ])
            
            fig.update_layout(
                title='Data Quality by Column',
                xaxis_title='Column',
                yaxis_title='Success Rate (%)',
                height=400,
                xaxis_tickangle=-45,
                yaxis=dict(range=[0, 100])
            )
            
            return fig
        except Exception as e:
            st.error(f"Error creating column quality chart: {str(e)}")
            return go.Figure()
    
    @staticmethod
    def _format_expected_value(kwargs: Dict) -> str:
        """Format expected value for display"""
        if not kwargs:
            return 'N/A'
        
        # Remove batch_id and other internal fields
        display_kwargs = {k: v for k, v in kwargs.items() 
                         if k not in ['batch_id', 'ge_batch_id']}
        
        if not display_kwargs:
            return 'N/A'
        
        # Format specific expectation types
        if 'column' in display_kwargs:
            column = display_kwargs.pop('column')
            if display_kwargs:
                return f"Column '{column}': {display_kwargs}"
            else:
                return f"Column '{column}'"
        
        return str(display_kwargs)
    
    @staticmethod
    def create_detailed_results_table(validation_results: Dict) -> pd.DataFrame:
        """Create detailed results table"""
        try:
            results = validation_results.get('results', [])
            
            # If no results in standard format, try to create from statistics
            if not results and 'statistics' in validation_results:
                stats = validation_results.get('statistics', {})
                total = stats.get('evaluated_expectations', 0)
                passed = stats.get('successful_expectations', 0)
                failed = stats.get('unsuccessful_expectations', 0)
                
                # Create placeholder results for display
                table_data = []
                for i in range(total):
                    if i < passed:
                        status = '✅ Pass'
                        details = 'Expectation passed successfully'
                    else:
                        status = '❌ Fail'
                        details = 'Expectation failed validation'
                    
                    # Try to get actual expectation info from results if available
                    expectation_type = 'Unknown'
                    column = 'N/A'
                    
                    if 'results' in validation_results and i < len(validation_results['results']):
                        result = validation_results['results'][i]
                        exp_config = result.get('expectation_config', {})
                        expectation_type = exp_config.get('type', exp_config.get('expectation_type', 'Unknown'))
                        column = exp_config.get('kwargs', {}).get('column', 'N/A')
                    
                    table_data.append({
                        'ID': i + 1,
                        'Expectation Type': expectation_type,
                        'Column': column,
                        'Status': status,
                        'Observed Value': 'N/A',
                        'Expected': 'N/A',
                        'Details': details
                    })
                
                return pd.DataFrame(table_data)
            
            # Standard results processing
            table_data = []
            for i, result in enumerate(results, 1):
                exp_config = result.get('expectation_config', {})
                
                # Handle different result structures
                observed_value = 'N/A'
                details = 'No details available'
                failure_rate = 'N/A'
                
                if 'result' in result:
                    result_data = result['result']
                    # Try to get meaningful observed value from various fields
                    if 'element_count' in result_data:
                        total_records = result_data['element_count']
                        observed_value = f"Total: {total_records}"
                        
                        # Calculate failure rate
                        if 'unexpected_count' in result_data:
                            unexpected_count = result_data['unexpected_count']
                            observed_value += f", Unexpected: {unexpected_count}"
                            
                            # Calculate failure percentage
                            if total_records > 0:
                                failure_rate = f"{(unexpected_count / total_records * 100):.1f}%"
                            else:
                                failure_rate = "0.0%"
                        
                        if 'missing_count' in result_data:
                            missing_count = result_data['missing_count']
                            observed_value += f", Missing: {missing_count}"
                            
                            # Include missing records in failure rate if they exist
                            if total_records > 0 and 'unexpected_count' in result_data:
                                total_failures = result_data['unexpected_count'] + missing_count
                                failure_rate = f"{(total_failures / total_records * 100):.1f}%"
                    
                    elif 'observed_value' in result_data:
                        observed_value = str(result_data['observed_value'])
                    
                    # Build detailed information
                    detail_parts = []
                    if 'unexpected_percent' in result_data:
                        detail_parts.append(f"Unexpected: {result_data['unexpected_percent']:.1f}%")
                    if 'missing_percent' in result_data:
                        detail_parts.append(f"Missing: {result_data['missing_percent']:.1f}%")
                    if 'partial_unexpected_list' in result_data and result_data['partial_unexpected_list']:
                        detail_parts.append(f"Sample unexpected: {result_data['partial_unexpected_list'][:3]}")
                    
                    if detail_parts:
                        details = ' | '.join(detail_parts)
                elif 'exception_info' in result:
                    details = result['exception_info'].get('exception_message', 'Exception occurred')
                
                # Extract expectation type and column from the correct structure
                expectation_type = exp_config.get('type', exp_config.get('expectation_type', 'Unknown'))
                column = exp_config.get('kwargs', {}).get('column', 'N/A')
                
                table_data.append({
                    'ID': i,
                    'Expectation Type': expectation_type,
                    'Column': column,
                    'Status': '✅ Pass' if result.get('success', False) else '❌ Fail',
                    'Failure Rate': failure_rate,
                    'Observed Value': observed_value,
                    'Expected': ReportGenerator._format_expected_value(exp_config.get('kwargs', {})),
                    'Details': details
                })
            
            return pd.DataFrame(table_data)
        except Exception as e:
            st.error(f"Error creating detailed results table: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def generate_html_report(validation_results: Dict, data: pd.DataFrame, suite_name: str) -> str:
        """Generate comprehensive HTML report"""
        try:
            summary_metrics = ReportGenerator.create_summary_metrics(validation_results)
            detailed_table = ReportGenerator.create_detailed_results_table(validation_results)
            
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Data Validation Report - {{ suite_name }}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .header { background-color: #f8f9fa; padding: 20px; border-radius: 5px; }
                    .metric-card { display: inline-block; margin: 10px; padding: 15px; 
                                  border: 1px solid #ddd; border-radius: 5px; text-align: center; }
                    .success { color: #2ca02c; }
                    .failure { color: #d62728; }
                    .warning { color: #ff7f0e; }
                    table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                    th { background-color: #f2f2f2; }
                    .pass { background-color: #d4edda; }
                    .fail { background-color: #f8d7da; }
                    .failure-rate-0 { background-color: #d4edda; color: #155724; }
                    .failure-rate-low { background-color: #fff3cd; color: #856404; }
                    .failure-rate-medium { background-color: #f8d7da; color: #721c24; }
                    .failure-rate-high { background-color: #721c24; color: #ffffff; }
                    .failure-rates { margin: 20px 0; }
                    .failure-rates table { margin-top: 15px; }
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>Data Validation Report</h1>
                    <h2>Suite: {{ suite_name }}</h2>
                    <p>Generated on: {{ timestamp }}</p>
                </div>
                
                <div class="summary">
                    <h3>Summary</h3>
                    <div class="metric-card">
                        <h4>Total Expectations</h4>
                        <div style="font-size: 24px; font-weight: bold;">{{ total_expectations }}</div>
                    </div>
                    <div class="metric-card">
                        <h4>Success Rate</h4>
                        <div style="font-size: 24px; font-weight: bold;" class="{% if success_rate == 100 %}success{% elif success_rate >= 80 %}warning{% else %}failure{% endif %}">
                            {{ "%.1f"|format(success_rate) }}%
                        </div>
                    </div>
                    <div class="metric-card">
                        <h4>Passed</h4>
                        <div style="font-size: 24px; font-weight: bold;" class="success">{{ successful }}</div>
                    </div>
                    <div class="metric-card">
                        <h4>Failed</h4>
                        <div style="font-size: 24px; font-weight: bold;" class="failure">{{ failed }}</div>
                    </div>
                </div>
                
                <div class="failure-rates">
                    <h3>Data Quality Failure Rates</h3>
                    <table>
                        <tr>
                            <th>Expectation Type</th>
                            <th>Column</th>
                            <th>Total Records</th>
                            <th>Failed Records</th>
                            <th>Failure Rate</th>
                        </tr>
                        {% for result in validation_results.results %}
                        {% if result.result and result.result.element_count %}
                        <tr>
                            <td>{{ result.expectation_config.type.replace('expect_', '').replace('_', ' ').title() if result.expectation_config.type else 'Unknown' }}</td>
                            <td>{{ result.expectation_config.kwargs.column if result.expectation_config.kwargs and result.expectation_config.kwargs.column else 'N/A' }}</td>
                            <td>{{ result.result.element_count }}</td>
                            <td>{{ (result.result.unexpected_count or 0) + (result.result.missing_count or 0) }}</td>
                            <td class="{% if result.result.element_count > 0 %}{% set failure_rate = ((result.result.unexpected_count or 0) + (result.result.missing_count or 0)) / result.result.element_count * 100 %}{% if failure_rate == 0 %}failure-rate-0{% elif failure_rate <= 5 %}failure-rate-low{% elif failure_rate <= 20 %}failure-rate-medium{% else %}failure-rate-high{% endif %}{% endif %}">
                                {% if result.result.element_count > 0 %}
                                {{ "%.1f"|format(((result.result.unexpected_count or 0) + (result.result.missing_count or 0)) / result.result.element_count * 100) }}%
                                {% else %}
                                N/A
                                {% endif %}
                            </td>
                        </tr>
                        {% endif %}
                        {% endfor %}
                    </table>
                </div>
                
                <div class="details">
                    <h3>Detailed Results</h3>
                    <table>
                        <tr>
                            <th>ID</th>
                            <th>Expectation Type</th>
                            <th>Column</th>
                            <th>Status</th>
                            <th>Failure Rate</th>
                            <th>Observed Value</th>
                            <th>Expected</th>
                        </tr>
                        {% for row in detailed_results %}
                        <tr class="{% if 'Pass' in row.Status %}pass{% else %}fail{% endif %}">
                            <td>{{ row.ID }}</td>
                            <td>{{ row['Expectation Type'] }}</td>
                            <td>{{ row.Column }}</td>
                            <td>{{ row.Status }}</td>
                            <td class="{% if row['Failure Rate'] == 'N/A' %}{% elif row['Failure Rate'] == '0.0%' %}failure-rate-0{% elif row['Failure Rate']|float <= 5 %}failure-rate-low{% elif row['Failure Rate']|float <= 20 %}failure-rate-medium{% else %}failure-rate-high{% endif %}">{{ row['Failure Rate'] }}</td>
                            <td>{{ row['Observed Value'] }}</td>
                            <td>{{ row.Expected }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
                
                <div class="data-info">
                    <h3>Data Information</h3>
                    <p><strong>Rows:</strong> {{ data_rows }}</p>
                    <p><strong>Columns:</strong> {{ data_cols }}</p>
                    <p><strong>Data Types:</strong> {{ data_types }}</p>
                </div>
            </body>
            </html>
            """
            
            template = Template(html_template)
            
            return template.render(
                suite_name=suite_name,
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                total_expectations=summary_metrics['total_expectations'],
                success_rate=summary_metrics['success_rate'],
                successful=summary_metrics['successful'],
                failed=summary_metrics['failed'],
                detailed_results=detailed_table.to_dict('records'),
                validation_results=validation_results,
                data_rows=len(data),
                data_cols=len(data.columns),
                data_types=', '.join([f"{col}: {dtype}" for col, dtype in data.dtypes.head().items()])
            )
            
        except Exception as e:
            st.error(f"Error generating HTML report: {str(e)}")
            return "<html><body><h1>Error generating report</h1></body></html>"
    
    @staticmethod
    def create_failed_records_dataset(validation_results: Dict, original_data: pd.DataFrame = None) -> pd.DataFrame:
        """Create a dataset containing original data rows that failed validation with failure details"""
        try:
            if original_data is None:
                st.warning("Original dataset not available. Cannot create failed records dataset.")
                return pd.DataFrame()
            
            results = validation_results.get('results', [])
            failed_data_rows = []
            
            # Create a copy of original data to work with
            data_copy = original_data.copy()
            
            # Add columns to track which expectations failed for each row
            expectation_failure_columns = []
            
            for i, result in enumerate(results, 1):
                if not result.get('success', False):
                    exp_config = result.get('expectation_config', {})
                    result_data = result.get('result', {})
                    
                    expectation_type = exp_config.get('type', exp_config.get('expectation_type', 'Unknown'))
                    column = exp_config.get('kwargs', {}).get('column', 'N/A')
                    
                    # Create column name for this failed expectation
                    failure_col_name = f"Failed_Test_{i}_{expectation_type.replace('expect_', '')}"
                    expectation_failure_columns.append(failure_col_name)
                    
                    # Initialize failure column
                    data_copy[failure_col_name] = ''
                    
                    # Handle different types of failures
                    unexpected_list = result_data.get('partial_unexpected_list', [])
                    
                    if column != 'N/A' and column in data_copy.columns:
                        # Mark rows with unexpected values
                        if unexpected_list:
                            mask = data_copy[column].isin(unexpected_list)
                            data_copy.loc[mask, failure_col_name] = f"Unexpected value: {expectation_type}"
                        
                        # Mark rows with missing values if this expectation checks for missing values
                        if 'missing_count' in result_data and result_data.get('missing_count', 0) > 0:
                            missing_mask = data_copy[column].isna()
                            data_copy.loc[missing_mask, failure_col_name] = f"Missing value: {expectation_type}"
                        
                        # For range-based expectations, we need to check the actual condition
                        kwargs = exp_config.get('kwargs', {})
                        if 'min_value' in kwargs or 'max_value' in kwargs:
                            min_val = kwargs.get('min_value')
                            max_val = kwargs.get('max_value')
                            
                            if min_val is not None and max_val is not None:
                                mask = ~data_copy[column].between(min_val, max_val)
                                data_copy.loc[mask, failure_col_name] = f"Out of range ({min_val}-{max_val}): {expectation_type}"
                            elif min_val is not None:
                                mask = data_copy[column] < min_val
                                data_copy.loc[mask, failure_col_name] = f"Below minimum ({min_val}): {expectation_type}"
                            elif max_val is not None:
                                mask = data_copy[column] > max_val
                                data_copy.loc[mask, failure_col_name] = f"Above maximum ({max_val}): {expectation_type}"
                        
                        # For value set expectations
                        if 'value_set' in kwargs:
                            value_set = kwargs['value_set']
                            if expectation_type == 'expect_column_values_to_be_in_set':
                                mask = ~data_copy[column].isin(value_set)
                                data_copy.loc[mask, failure_col_name] = f"Not in allowed set: {expectation_type}"
                            elif expectation_type == 'expect_column_values_to_not_be_in_set':
                                mask = data_copy[column].isin(value_set)
                                data_copy.loc[mask, failure_col_name] = f"In forbidden set: {expectation_type}"
                        
                        # For uniqueness expectations
                        if expectation_type == 'expect_column_values_to_be_unique':
                            duplicated_mask = data_copy[column].duplicated(keep=False)
                            data_copy.loc[duplicated_mask, failure_col_name] = f"Duplicate value: {expectation_type}"
                        
                        # For null expectations
                        if expectation_type == 'expect_column_values_to_not_be_null':
                            null_mask = data_copy[column].isna()
                            data_copy.loc[null_mask, failure_col_name] = f"Null value: {expectation_type}"
                        elif expectation_type == 'expect_column_values_to_be_null':
                            not_null_mask = data_copy[column].notna()
                            data_copy.loc[not_null_mask, failure_col_name] = f"Not null value: {expectation_type}"
                    
                    else:
                        # For table-level expectations or when column is not found
                        if len(unexpected_list) > 0:
                            # Try to find rows matching unexpected values across all columns
                            for unexpected_val in unexpected_list:
                                mask = (data_copy == unexpected_val).any(axis=1)
                                data_copy.loc[mask, failure_col_name] = f"Table-level failure: {expectation_type}"
            
            # Filter to only rows that have at least one failure
            failure_mask = pd.Series(False, index=data_copy.index)
            for col in expectation_failure_columns:
                if col in data_copy.columns:
                    failure_mask |= (data_copy[col] != '')
            
            failed_rows = data_copy[failure_mask].copy()
            
            # Add a summary column showing all failed tests for each row
            if not failed_rows.empty:
                failed_rows['All_Failed_Tests'] = failed_rows[expectation_failure_columns].apply(
                    lambda row: ' | '.join([test for test in row if test != '']), axis=1
                )
                
                # Add a count of failed tests per row
                failed_rows['Failed_Tests_Count'] = failed_rows[expectation_failure_columns].apply(
                    lambda row: sum(1 for test in row if test != ''), axis=1
                )
            
            return failed_rows
            
        except Exception as e:
            st.error(f"Error creating failed records dataset: {str(e)}")
            return pd.DataFrame()
    
    @staticmethod
    def create_data_distribution_charts(data: pd.DataFrame, max_columns: int = 6) -> List[go.Figure]:
        """Create distribution charts for numeric columns"""
        try:
            numeric_cols = data.select_dtypes(include=['number']).columns[:max_columns]
            figures = []
            
            for col in numeric_cols:
                fig = go.Figure()
                
                # Add histogram
                fig.add_trace(go.Histogram(
                    x=data[col].dropna(),
                    name=col,
                    opacity=0.7,
                    nbinsx=30
                ))
                
                fig.update_layout(
                    title=f'Distribution of {col}',
                    xaxis_title=col,
                    yaxis_title='Frequency',
                    height=300,
                    showlegend=False
                )
                
                figures.append(fig)
            
            return figures
        except Exception as e:
            st.error(f"Error creating distribution charts: {str(e)}")
            return []