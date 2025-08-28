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
            results = validation_results.get('results', [])
            
            total_expectations = len(results)
            successful = sum(1 for r in results if r.get('success', False))
            failed = total_expectations - successful
            
            success_rate = (successful / total_expectations * 100) if total_expectations > 0 else 0
            
            # Group by expectation type
            expectation_types = {}
            for result in results:
                exp_type = result.get('expectation_config', {}).get('expectation_type', 'unknown')
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
    def create_detailed_results_table(validation_results: Dict) -> pd.DataFrame:
        """Create detailed results table"""
        try:
            results = validation_results.get('results', [])
            
            table_data = []
            for i, result in enumerate(results, 1):
                exp_config = result.get('expectation_config', {})
                
                table_data.append({
                    'ID': i,
                    'Expectation Type': exp_config.get('expectation_type', 'Unknown'),
                    'Column': exp_config.get('column', 'N/A'),
                    'Status': '✅ Pass' if result.get('success', False) else '❌ Fail',
                    'Observed Value': result.get('result', {}).get('observed_value', 'N/A'),
                    'Expected': str(exp_config.get('kwargs', {})),
                    'Details': result.get('result', {}).get('details', 'No details available')
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
                
                <div class="details">
                    <h3>Detailed Results</h3>
                    <table>
                        <tr>
                            <th>ID</th>
                            <th>Expectation Type</th>
                            <th>Column</th>
                            <th>Status</th>
                            <th>Observed Value</th>
                            <th>Expected</th>
                        </tr>
                        {% for row in detailed_results %}
                        <tr class="{% if 'Pass' in row.Status %}pass{% else %}fail{% endif %}">
                            <td>{{ row.ID }}</td>
                            <td>{{ row['Expectation Type'] }}</td>
                            <td>{{ row.Column }}</td>
                            <td>{{ row.Status }}</td>
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
                data_rows=len(data),
                data_cols=len(data.columns),
                data_types=', '.join([f"{col}: {dtype}" for col, dtype in data.dtypes.head().items()])
            )
            
        except Exception as e:
            st.error(f"Error generating HTML report: {str(e)}")
            return "<html><body><h1>Error generating report</h1></body></html>"
    
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