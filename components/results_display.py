import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List
import json
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.report_generator import ReportGenerator
from config.app_config import AppConfig

class ResultsDisplayComponent:
    """Component for displaying validation results"""
    
    def __init__(self):
        self.report_generator = ReportGenerator()
        self.config = AppConfig()
    
    def render(self, validation_results: Dict):
        """Render the validation results interface"""
        
        if not validation_results:
            st.error("No validation results available!")
            return
        
        # Debug UI removed for a cleaner experience
        
        # Results overview
        self._render_results_overview(validation_results)
        
        # Interactive visualizations
        self._render_visualizations(validation_results)
        
        # Detailed results table
        self._render_detailed_results(validation_results)
        
        # Export options
        self._render_export_options(validation_results)
        
        # Navigation
        self._render_navigation_buttons()
    
    def _render_results_overview(self, validation_results: Dict):
        """Render high-level results overview"""
        st.markdown("#### 📊 Results Overview")
        
        # Get summary metrics
        summary_metrics = self.report_generator.create_summary_metrics(validation_results)
        
        if not summary_metrics:
            st.error("Could not generate summary metrics!")
            return
        
        # Key metrics cards
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Total Expectations",
                summary_metrics['total_expectations']
            )
        
        with col2:
            st.metric(
                "Passed",
                summary_metrics['successful']
            )
        
        with col3:
            st.metric(
                "Failed", 
                summary_metrics['failed']
            )
        
        with col4:
            success_rate = summary_metrics['success_rate']
            st.metric(
                "Success Rate",
                f"{success_rate:.1f}%"
            )
        
        with col5:
            execution_time = st.session_state.get('validation_execution_time', 0)
            st.metric(
                "Execution Time",
                f"{execution_time:.2f}s"
            )
        
        # Status banner removed to avoid redundancy; metrics above convey the state succinctly
        
        # Execution info
        validation_mode = validation_results.get('meta', {}).get('validation_mode', 'batch')
        sample_size = st.session_state.get('validation_sample_size')
        
        info_text = f"Validation mode: {validation_mode.title()}"
        if sample_size:
            info_text += f" | Sample size: {sample_size:,} rows"
        
        st.info(info_text)
        
        # Failure rate summary
        if 'results' in validation_results and validation_results['results']:
            st.markdown("#### 📉 Data Quality Failure Rates")
            
            # Create a summary of failure rates by expectation
            failure_summary = []
            for result in validation_results['results']:
                if 'result' in result and 'element_count' in result['result']:
                    exp_config = result.get('expectation_config', {})
                    exp_type = exp_config.get('type', exp_config.get('expectation_type', 'Unknown'))
                    column = exp_config.get('kwargs', {}).get('column', 'N/A')
                    
                    element_count = result['result']['element_count']
                    unexpected_count = result['result'].get('unexpected_count', 0)
                    missing_count = result['result'].get('missing_count', 0)
                    
                    if element_count > 0:
                        failure_rate = (unexpected_count + missing_count) / element_count * 100
                        failure_summary.append({
                            'Expectation': exp_type.replace('expect_', '').replace('_', ' ').title(),
                            'Column': column,
                            'Total Records': element_count,
                            'Failed Records': unexpected_count + missing_count,
                            'Failure Rate': f"{failure_rate:.1f}%"
                        })
            
            if failure_summary:
                # Display as a table with color coding
                import pandas as pd
                failure_df = pd.DataFrame(failure_summary)
                
                def color_failure_rate(val):
                    try:
                        rate = float(val.rstrip('%'))
                        if rate == 0:
                            return 'background-color: #d4edda; color: #155724'
                        elif rate <= 5:
                            return 'background-color: #fff3cd; color: #856404'
                        elif rate <= 20:
                            return 'background-color: #f8d7da; color: #721c24'
                        else:
                            return 'background-color: #721c24; color: #ffffff'
                    except:
                        return ''
                
                styled_failure_df = failure_df.style.map(
                    color_failure_rate, subset=['Failure Rate']
                )
                
                st.dataframe(
                    styled_failure_df,
                    width='stretch',
                    column_config={
                        "Expectation": st.column_config.TextColumn("Expectation Type", width="medium"),
                        "Column": st.column_config.TextColumn("Column", width="small"),
                        "Total Records": st.column_config.NumberColumn("Total Records", width="small"),
                        "Failed Records": st.column_config.NumberColumn("Failed Records", width="small"),
                        "Failure Rate": st.column_config.TextColumn("Failure Rate", width="small")
                    }
                )
            else:
                st.info("No failure rate data available")
    
    def _render_visualizations(self, validation_results: Dict):
        """Render simplified visual analysis with two pie charts"""
        st.markdown("#### 📈 Visual Analysis")
        
        summary_metrics = self.report_generator.create_summary_metrics(validation_results)
        if not summary_metrics:
            return
        
        col1, col2 = st.columns(2)
        with col1:
            fig_tests = self.report_generator.create_failed_tests_rate_chart(summary_metrics)
            st.plotly_chart(fig_tests, width='stretch', config=self.config.CHART_CONFIG)
        with col2:
            fig_rows = self.report_generator.create_failed_rows_rate_chart(
                validation_results, st.session_state.get('uploaded_data')
            )
            st.plotly_chart(fig_rows, width='stretch', config=self.config.CHART_CONFIG)
    
    def _render_detailed_results(self, validation_results: Dict):
        """Render detailed results table"""
        st.markdown("#### 📋 Detailed Results")
        
        # Create detailed results table
        detailed_table, debug_messages = self.report_generator.create_detailed_results_table(validation_results)
        
        # Internal debug messages are suppressed in the UI for cleanliness
        
        if detailed_table.empty:
            st.warning("No detailed results available!")
            return
        
        # Hide table and filters behind an expander to reduce clutter
        with st.expander("Detailed Results", expanded=False):
            # Filter options
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                status_filter = st.selectbox(
                    "Filter by status:",
                    options=["All", "Passed Only", "Failed Only"],
                    index=0
                )

            with col2:
                if 'Expectation Type' in detailed_table.columns:
                    exp_types = ["All"] + list(detailed_table['Expectation Type'].unique())
                    type_filter = st.selectbox(
                        "Filter by type:",
                        options=exp_types,
                        index=0
                    )
                else:
                    type_filter = "All"

            with col3:
                if 'Column' in detailed_table.columns:
                    columns = ["All"] + list(detailed_table['Column'].unique())
                    column_filter = st.selectbox(
                        "Filter by column:",
                        options=columns,
                        index=0
                    )
                else:
                    column_filter = "All"

            with col4:
                if 'Failure Rate' in detailed_table.columns:
                    # Extract numeric values for failure rate filtering
                    try:
                        failure_rates = detailed_table['Failure Rate'].replace('N/A', '0.0%').str.rstrip('%').astype(float)
                        max_rate = failure_rates.max() if not failure_rates.empty else 100.0
                        min_rate = failure_rates.min() if not failure_rates.empty else 0.0

                        # Ensure we have valid numeric values
                        if pd.isna(max_rate) or pd.isna(min_rate):
                            max_rate = 100.0
                            min_rate = 0.0

                        # Ensure min_value is less than max_value
                        if min_rate >= max_rate:
                            min_rate = 0.0
                            max_rate = 100.0

                        failure_rate_filter = st.slider(
                            "Max Failure Rate (%):",
                            min_value=min_rate,
                            max_value=max_rate,
                            value=min(max_rate, 100.0),
                            step=0.1,
                            help="Filter expectations by maximum failure rate"
                        )
                    except Exception as e:
                        st.warning(f"Error creating failure rate filter: {str(e)}")
                        failure_rate_filter = 100.0
                else:
                    failure_rate_filter = 100.0

            # Apply filters
            filtered_table = detailed_table.copy()

            if status_filter == "Passed Only":
                filtered_table = filtered_table[filtered_table['Status'].str.contains('Pass')]
            elif status_filter == "Failed Only":
                filtered_table = filtered_table[filtered_table['Status'].str.contains('Fail')]

            if type_filter != "All":
                filtered_table = filtered_table[filtered_table['Expectation Type'] == type_filter]

            if column_filter != "All":
                filtered_table = filtered_table[filtered_table['Column'] == column_filter]

            # Apply failure rate filter
            if 'Failure Rate' in filtered_table.columns and failure_rate_filter < 100:
                # Convert failure rates to numeric for comparison
                failure_rates = filtered_table['Failure Rate'].replace('N/A', '0.0%').str.rstrip('%').astype(float)
                filtered_table = filtered_table[failure_rates <= failure_rate_filter]

            # Display results count
            total_results = len(detailed_table)
            filtered_results = len(filtered_table)
            st.info(f"Showing {filtered_results} of {total_results} results")

            # Style the dataframe
            def highlight_status(val):
                if 'Pass' in str(val):
                    return 'background-color: #d4edda; color: #155724'
                elif 'Fail' in str(val):
                    return 'background-color: #f8d7da; color: #721c24'
                return ''

            def highlight_failure_rate(val):
                if val == 'N/A':
                    return ''
                try:
                    rate = float(val.rstrip('%'))
                    if rate == 0:
                        return 'background-color: #d4edda; color: #155724'
                    elif rate <= 5:
                        return 'background-color: #fff3cd; color: #856404'
                    elif rate <= 20:
                        return 'background-color: #f8d7da; color: #721c24'
                    else:
                        return 'background-color: #721c24; color: #ffffff'
                except:
                    return ''

            # Display the table
            if not filtered_table.empty:
                styled_table = filtered_table.style.map(
                    highlight_status, subset=['Status']
                ).map(
                    highlight_failure_rate, subset=['Failure Rate']
                ).format({
                    'Observed Value': lambda x: str(x)[:50] + '...' if len(str(x)) > 50 else str(x),
                    'Expected': lambda x: str(x)[:50] + '...' if len(str(x)) > 50 else str(x)
                })

                st.dataframe(
                        styled_table,
                        width='stretch',
                        height=400,
                        column_config={
                            "ID": st.column_config.NumberColumn("ID", width="small"),
                            "Status": st.column_config.TextColumn("Status", width="small"),
                            "Failure Rate": st.column_config.TextColumn("Failure Rate", width="small"),
                            "Details": st.column_config.TextColumn("Details", width="large")
                        }
                    )
            else:
                st.warning("No results match the selected filters")

            # Removed inline failed expectations detail list for a cleaner UI
        
        # Removed secondary failed expectations expander to avoid duplication
    
    def _render_export_options(self, validation_results: Dict):
        """Render export options"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Direct JSON download
            json_data = json.dumps(validation_results, indent=2, default=str)
            st.download_button(
                "📥 Download JSON",
                data=json_data,
                file_name=f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                key="download_json_report_btn",
                use_container_width=True
            )
        
        with col2:
            # Direct HTML download (if original data available)
            if st.session_state.uploaded_data is not None:
                suite_name = st.session_state.get('current_suite_name', 'validation_suite')
                html_report = self.report_generator.generate_html_report(
                    validation_results, 
                    st.session_state.uploaded_data,
                    suite_name
                )
                st.download_button(
                    "📥 Download HTML",
                    data=html_report,
                    file_name=f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    key="download_html_report_btn",
                    use_container_width=True
                )
            else:
                st.info("Original data required to generate HTML report")
        
        with col3:
            # Direct CSV download of detailed results
            detailed_table, _ = self.report_generator.create_detailed_results_table(validation_results)
            if not detailed_table.empty:
                csv_data = detailed_table.to_csv(index=False)
                st.download_button(
                    "📥 Download CSV",
                    data=csv_data,
                    file_name=f"validation_details_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    key="download_csv_report_btn",
                    use_container_width=True
                )
            else:
                st.info("No detailed results available for CSV export")
        
        # Failed Records Dataset Export
        st.markdown("#### ❌ Failed Records Dataset")
        st.markdown("*Original data rows that failed validation tests*")
        
        if st.session_state.uploaded_data is not None:
            failed_records_df = self.report_generator.create_failed_records_dataset(
                validation_results, st.session_state.uploaded_data
            )
            
            if not failed_records_df.empty:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Failed Rows", len(failed_records_df))
                
                with col2:
                    total_original_rows = len(st.session_state.uploaded_data)
                    failure_percentage = (len(failed_records_df) / total_original_rows) * 100
                    st.metric("Failure Rate", f"{failure_percentage:.1f}%")
                
                with col3:
                    if 'Failed_Tests_Count' in failed_records_df.columns:
                        avg_failures_per_row = failed_records_df['Failed_Tests_Count'].mean()
                        st.metric(
                            "Tests Failed per Row", 
                            f"{avg_failures_per_row:.1f}",
                            help="Average number of validation tests that failed per problematic row. 1.0 means each failed row failed exactly one test."
                        )
                
                # Removed interpretation/explanatory box for a cleaner UI
                
                # Column selection for preview
                st.markdown("##### Preview Options")
                col1, col2 = st.columns(2)
                
                with col1:
                    # Get all original columns (excluding our added failure columns)
                    original_cols = [col for col in failed_records_df.columns 
                                   if not col.startswith('Failed_Test_') and col not in ['All_Failed_Tests', 'Failed_Tests_Count']]
                    
                    show_original_only = st.checkbox(
                        "Show original columns only", 
                        value=True,
                        help="Hide the individual test failure columns and show only original data with summary"
                    )
                
                with col2:
                    # Ensure min_value is always less than max_value and handle edge cases
                    max_available = min(500, len(failed_records_df))
                    
                    # Handle very small datasets
                    if max_available <= 1:
                        # For 1 or fewer rows, just show a simple text display
                        st.info(f"Showing all {max_available} failed record(s)")
                        max_rows_to_show = max_available
                    else:
                        # Ensure min_value is always strictly less than max_value
                        min_value = min(9, max_available - 1)  # Use max_available - 1 to ensure min < max
                        
                        # Adjust step size for small datasets
                        if max_available <= 10:
                            step = 1
                        elif max_available <= 50:
                            step = 5
                        else:
                            step = 10
                        
                        max_rows_to_show = st.slider(
                            "Rows to preview:",
                            min_value=min_value,
                            max_value=max_available,
                            value=min(100, max_available),
                            step=step
                        )
                
                # Preview of failed records
                with st.expander("🔍 Preview Failed Records", expanded=True):
                    if show_original_only:
                        # Show original columns plus summary columns
                        display_cols = original_cols + ['Failed_Tests_Count', 'All_Failed_Tests']
                        preview_df = failed_records_df[display_cols].head(max_rows_to_show)
                    else:
                        # Show all columns
                        preview_df = failed_records_df.head(max_rows_to_show)
                    
                    st.dataframe(
                        preview_df,
                        width='stretch',
                        column_config={
                            "Failed_Tests_Count": st.column_config.NumberColumn("# Tests Failed", width="small"),
                            "All_Failed_Tests": st.column_config.TextColumn("Failed Tests Summary", width="large")
                        }
                    )
                
                # Download options
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Original data + summary columns only
                    summary_cols = original_cols + ['Failed_Tests_Count', 'All_Failed_Tests']
                    summary_df = failed_records_df[summary_cols]
                    summary_csv = summary_df.to_csv(index=False)
                    st.download_button(
                        "📥 Download CSV (Summary)",
                        data=summary_csv,
                        file_name=f"failed_records_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_failed_records_summary_csv",
                        use_container_width=True,
                        help="Download original data with failed rows and test summary"
                    )
                
                with col2:
                    # Full dataset with all failure details
                    full_csv = failed_records_df.to_csv(index=False)
                    st.download_button(
                        "📥 Download CSV (Detailed)",
                        data=full_csv,
                        file_name=f"failed_records_detailed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        key="download_failed_records_detailed_csv",
                        use_container_width=True,
                        help="Download complete dataset with individual test failure columns"
                    )
                
                with col3:
                    # JSON format for programmatic use
                    failed_json = failed_records_df.to_json(orient='records', indent=2)
                    st.download_button(
                        "📥 Download JSON",
                        data=failed_json,
                        file_name=f"failed_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json",
                        key="download_failed_records_json",
                        use_container_width=True,
                        help="Download failed records in JSON format"
                    )
                
                # Additional insights
                if 'Failed_Tests_Count' in failed_records_df.columns:
                    with st.expander("🔍 Failure Pattern Analysis", expanded=False):
                        # Compact list styling for this section
                        st.markdown(
                            """
                            <style>
                            .failure-patterns ul, .failure-patterns ol { margin: 0 0 4px 1.25rem; padding-left: 1rem; }
                            .failure-patterns li { margin: 0; }
                            </style>
                            """,
                            unsafe_allow_html=True,
                        )
                        
                        # Distribution of failures per row
                        failure_counts = failed_records_df['Failed_Tests_Count'].value_counts().sort_index()
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Failures per Row Distribution:**")
                            dist_lines = []
                            for count, freq in failure_counts.items():
                                percentage = (freq / len(failed_records_df)) * 100
                                dist_lines.append(f"- {count} test(s) failed: {freq} rows ({percentage:.1f}%)")
                            st.markdown("\n".join(dist_lines), help=None)
                        
                        with col2:
                            # Show most common failure combinations
                            if 'All_Failed_Tests' in failed_records_df.columns:
                                st.markdown("**Most Common Failure Patterns:**")
                                top_patterns = failed_records_df['All_Failed_Tests'].value_counts().head(5)
                                pattern_lines = []
                                for i, (pattern, count) in enumerate(top_patterns.items(), 1):
                                    pattern_lines.append(f"{i}. {count} rows: {pattern[:100]}...")
                                st.markdown("\n".join(pattern_lines))
            else:
                st.success("🎉 No failed records found! All data rows passed validation successfully.")
        else:
            st.warning("⚠️ Original dataset not available. Cannot create failed records dataset.")
        
        # Removed Data Quality Assessment and Recommendations blocks per UX simplification
    
    def _download_all_reports(self):
        """Download all report files currently available on screen"""
        try:
            # Get current timestamp for file naming
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Create comprehensive ZIP file with all reports
            import zipfile
            import io
            
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                
                # 1. Export JSON Report (validation_results_*.json)
                if st.session_state.get('validation_results'):
                    json_data = json.dumps(st.session_state.validation_results, indent=2, default=str)
                    zip_file.writestr(f'validation_results_{timestamp}.json', json_data)
                
                # 2. Export HTML Report (validation_report_*.html)
                if st.session_state.get('validation_results') and st.session_state.get('uploaded_data') is not None:
                    try:
                        suite_name = st.session_state.get('current_suite_name', 'validation_suite')
                        html_report = self.report_generator.generate_html_report(
                            st.session_state.validation_results, 
                            st.session_state.uploaded_data,
                            suite_name
                        )
                        zip_file.writestr(f'validation_report_{timestamp}.html', html_report)
                    except Exception as e:
                        st.warning(f"Could not generate HTML report: {str(e)}")
                
                # 3. Export CSV Report (validation_details_*.csv)
                if st.session_state.get('validation_results'):
                    try:
                        detailed_table, _ = self.report_generator.create_detailed_results_table(st.session_state.validation_results)
                        if not detailed_table.empty:
                            csv_data = detailed_table.to_csv(index=False)
                            zip_file.writestr(f'validation_details_{timestamp}.csv', csv_data)
                    except Exception as e:
                        st.warning(f"Could not generate detailed CSV: {str(e)}")
                
                # 4-6. Failed Records Reports (if available)
                if st.session_state.get('validation_results') and st.session_state.get('uploaded_data') is not None:
                    try:
                        failed_records_df = self.report_generator.create_failed_records_dataset(
                            st.session_state.validation_results, st.session_state.uploaded_data
                        )
                        
                        if not failed_records_df.empty:
                            # Get original columns (excluding our added failure columns)
                            original_cols = [col for col in failed_records_df.columns 
                                           if not col.startswith('Failed_Test_') and col not in ['All_Failed_Tests', 'Failed_Tests_Count']]
                            
                            # 4. Download Summary CSV (failed_records_summary_*.csv)
                            summary_cols = original_cols + ['Failed_Tests_Count', 'All_Failed_Tests']
                            summary_df = failed_records_df[summary_cols]
                            summary_csv = summary_df.to_csv(index=False)
                            zip_file.writestr(f'failed_records_summary_{timestamp}.csv', summary_csv)
                            
                            # 5. Download Detailed CSV (failed_records_detailed_*.csv)
                            full_csv = failed_records_df.to_csv(index=False)
                            zip_file.writestr(f'failed_records_detailed_{timestamp}.csv', full_csv)
                            
                            # 6. Download JSON (failed_records_*.json)
                            failed_json = failed_records_df.to_json(orient='records', indent=2)
                            zip_file.writestr(f'failed_records_{timestamp}.json', failed_json)
                    except Exception as e:
                        st.warning(f"Could not generate failed records reports: {str(e)}")
                
                # Additional comprehensive report with metadata
                comprehensive_report = {
                    'timestamp': timestamp,
                    'suite_name': st.session_state.get('current_suite_name', 'unknown'),
                    'dataset_info': {
                        'filename': st.session_state.get('uploaded_filename', 'unknown'),
                        'rows': len(st.session_state.uploaded_data) if st.session_state.get('uploaded_data') is not None else 0,
                        'columns': len(st.session_state.uploaded_data.columns) if st.session_state.get('uploaded_data') is not None else 0,
                        'columns_list': list(st.session_state.uploaded_data.columns) if st.session_state.get('uploaded_data') is not None else []
                    },
                    'summary_metrics': self.report_generator.create_summary_metrics(st.session_state.validation_results) if st.session_state.get('validation_results') else None
                }
                
                comprehensive_json = json.dumps(comprehensive_report, indent=2, default=str)
                zip_file.writestr(f'comprehensive_report_{timestamp}.json', comprehensive_json)
            
            zip_buffer.seek(0)
            
            # Count files in ZIP
            with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
                file_count = len(zip_file.namelist())
            
            # Provide download button
            st.download_button(
                label=f"📦 Download All Reports ({file_count} files)",
                data=zip_buffer.getvalue(),
                file_name=f"complete_validation_report_{timestamp}.zip",
                mime="application/zip",
                key=f"download_all_reports_{timestamp}",
                help=f"Download all {file_count} available reports including validation results, failed records, and summary metrics"
            )
            
            st.success(f"✅ All {file_count} reports packaged and ready for download!")
            
        except Exception as e:
            st.error(f"❌ Error creating download package: {str(e)}")
            st.exception(e)
    
    def _restart_app(self):
        """Clear all cache and rerun the app"""
        try:
            # Clear all session state variables
            keys_to_clear = [
                'uploaded_data', 'uploaded_filename', 'data_context',
                'expectation_configs', 'expectation_suite', 'current_suite_name',
                'validation_results', 'validation_completed', 'failed_records_data',
                'ge_helpers', 'current_step'
            ]
            
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
            
            # Reset to initial state
            st.session_state.current_step = 'upload'
            
            # Clear any cached data
            st.cache_data.clear()
            st.cache_resource.clear()
            
            st.success("✅ Application restarted successfully! All data and cache cleared.")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error restarting application: {str(e)}")
            st.exception(e)

    def _render_navigation_buttons(self):
        """Render navigation buttons"""
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("← Back to Validation", type="secondary", key="back_to_validation_btn"):
                st.session_state.current_step = 'validate'
                st.rerun()
        
        with col2:
            if st.button("📥 Download ALL", type="secondary", key="download_all_btn"):
                # Download all report files currently available on screen
                self._download_all_reports()
        
        with col3:
            if st.button("🔄 Restart", type="primary", key="restart_btn"):
                # Clear all cache and rerun the app
                self._restart_app()