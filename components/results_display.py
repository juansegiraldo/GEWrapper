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
        st.markdown("### 📋 Validation Results")
        
        if not validation_results:
            st.error("No validation results available!")
            return
        
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
                summary_metrics['successful'],
                delta=f"+{summary_metrics['successful']}"
            )
        
        with col3:
            st.metric(
                "Failed", 
                summary_metrics['failed'],
                delta=f"+{summary_metrics['failed']}" if summary_metrics['failed'] > 0 else None,
                delta_color="inverse"
            )
        
        with col4:
            success_rate = summary_metrics['success_rate']
            st.metric(
                "Success Rate",
                f"{success_rate:.1f}%",
                delta=f"{success_rate-100:.1f}%" if success_rate < 100 else "Perfect!",
                delta_color="normal" if success_rate == 100 else "inverse"
            )
        
        with col5:
            execution_time = st.session_state.get('validation_execution_time', 0)
            st.metric(
                "Execution Time",
                f"{execution_time:.2f}s"
            )
        
        # Status indicator
        if success_rate == 100:
            st.success("🎉 Perfect! All expectations passed successfully!")
        elif success_rate >= 80:
            st.warning(f"⚠️ {summary_metrics['failed']} expectations failed. Review details below.")
        else:
            st.error(f"❌ {summary_metrics['failed']} expectations failed. Data quality needs attention.")
        
        # Execution info
        validation_mode = validation_results.get('meta', {}).get('validation_mode', 'batch')
        sample_size = st.session_state.get('validation_sample_size')
        
        info_text = f"Validation mode: {validation_mode.title()}"
        if sample_size:
            info_text += f" | Sample size: {sample_size:,} rows"
        
        st.info(info_text)
    
    def _render_visualizations(self, validation_results: Dict):
        """Render interactive visualizations"""
        st.markdown("#### 📈 Visual Analysis")
        
        summary_metrics = self.report_generator.create_summary_metrics(validation_results)
        
        if not summary_metrics:
            return
        
        # Create tabs for different visualizations
        tab1, tab2, tab3, tab4 = st.tabs(["Overall Results", "By Expectation Type", "By Column", "Data Distribution"])
        
        with tab1:
            # Success rate donut chart
            fig_success = self.report_generator.create_success_rate_chart(summary_metrics)
            st.plotly_chart(fig_success, use_container_width=True, config=self.config.CHART_CONFIG)
        
        with tab2:
            # Results by expectation type
            if summary_metrics['expectation_types']:
                fig_types = self.report_generator.create_expectation_type_chart(summary_metrics)
                st.plotly_chart(fig_types, use_container_width=True, config=self.config.CHART_CONFIG)
            else:
                st.info("No expectation type data available")
        
        with tab3:
            # Results by column (if available)
            if st.session_state.uploaded_data is not None:
                fig_columns = self.report_generator.create_column_quality_chart(
                    validation_results, st.session_state.uploaded_data
                )
                if fig_columns.data:
                    st.plotly_chart(fig_columns, use_container_width=True, config=self.config.CHART_CONFIG)
                else:
                    st.info("No column-specific expectations found")
            else:
                st.info("Original data not available for column analysis")
        
        with tab4:
            # Data distribution charts
            if st.session_state.uploaded_data is not None:
                st.markdown("**Sample Data Distributions**")
                distribution_figs = self.report_generator.create_data_distribution_charts(
                    st.session_state.uploaded_data
                )
                
                if distribution_figs:
                    # Display charts in a grid
                    cols = st.columns(2)
                    for i, fig in enumerate(distribution_figs):
                        with cols[i % 2]:
                            st.plotly_chart(fig, use_container_width=True, config=self.config.CHART_CONFIG)
                else:
                    st.info("No numeric columns available for distribution analysis")
            else:
                st.info("Original data not available for distribution analysis")
    
    def _render_detailed_results(self, validation_results: Dict):
        """Render detailed results table"""
        st.markdown("#### 📋 Detailed Results")
        
        # Create detailed results table
        detailed_table = self.report_generator.create_detailed_results_table(validation_results)
        
        if detailed_table.empty:
            st.warning("No detailed results available!")
            return
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
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
        
        # Display the table
        if not filtered_table.empty:
            styled_table = filtered_table.style.applymap(
                highlight_status, subset=['Status']
            ).format({
                'Observed Value': lambda x: str(x)[:50] + '...' if len(str(x)) > 50 else str(x),
                'Expected': lambda x: str(x)[:50] + '...' if len(str(x)) > 50 else str(x)
            })
            
            st.dataframe(
                styled_table,
                use_container_width=True,
                height=400,
                column_config={
                    "ID": st.column_config.NumberColumn("ID", width="small"),
                    "Status": st.column_config.TextColumn("Status", width="small"),
                    "Details": st.column_config.TextColumn("Details", width="large")
                }
            )
        else:
            st.warning("No results match the selected filters")
        
        # Show failed expectations details
        failed_results = detailed_table[detailed_table['Status'].str.contains('Fail')]
        if not failed_results.empty:
            with st.expander(f"❌ Failed Expectations Details ({len(failed_results)} failures)"):
                for _, row in failed_results.iterrows():
                    st.markdown(f"**{row['ID']}. {row['Expectation Type']}** (Column: `{row['Column']}`)")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Observed:** {row['Observed Value']}")
                    with col2:
                        st.write(f"**Expected:** {row['Expected']}")
                    
                    if row['Details'] != 'No details available':
                        st.write(f"**Details:** {row['Details']}")
                    
                    st.markdown("---")
    
    def _render_export_options(self, validation_results: Dict):
        """Render export options"""
        st.markdown("#### 💾 Export Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Export as JSON
            if st.button("📄 Export JSON", use_container_width=True):
                json_data = json.dumps(validation_results, indent=2, default=str)
                st.download_button(
                    "Download JSON Report",
                    data=json_data,
                    file_name=f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        with col2:
            # Export as HTML
            if st.button("🌐 Export HTML", use_container_width=True):
                if st.session_state.uploaded_data is not None:
                    suite_name = st.session_state.get('current_suite_name', 'validation_suite')
                    html_report = self.report_generator.generate_html_report(
                        validation_results, 
                        st.session_state.uploaded_data,
                        suite_name
                    )
                    st.download_button(
                        "Download HTML Report",
                        data=html_report,
                        file_name=f"validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html"
                    )
                else:
                    st.warning("Original data not available for HTML report")
        
        with col3:
            # Export detailed table as CSV
            if st.button("📊 Export CSV", use_container_width=True):
                detailed_table = self.report_generator.create_detailed_results_table(validation_results)
                if not detailed_table.empty:
                    csv_data = detailed_table.to_csv(index=False)
                    st.download_button(
                        "Download CSV Report",
                        data=csv_data,
                        file_name=f"validation_details_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("No detailed results available")
        
        # Data quality score
        st.markdown("#### 📊 Data Quality Assessment")
        summary_metrics = self.report_generator.create_summary_metrics(validation_results)
        
        if summary_metrics:
            success_rate = summary_metrics['success_rate']
            
            # Determine quality grade
            if success_rate >= 95:
                grade = "A"
                grade_color = "green"
                assessment = "Excellent data quality!"
            elif success_rate >= 85:
                grade = "B" 
                grade_color = "lightgreen"
                assessment = "Good data quality with minor issues"
            elif success_rate >= 70:
                grade = "C"
                grade_color = "orange"
                assessment = "Acceptable data quality, improvements recommended"
            elif success_rate >= 50:
                grade = "D"
                grade_color = "red"
                assessment = "Poor data quality, immediate attention needed"
            else:
                grade = "F"
                grade_color = "darkred"
                assessment = "Critical data quality issues"
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(f"## <span style='color: {grade_color}'>Grade: {grade}</span>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"**Assessment:** {assessment}")
                st.progress(success_rate / 100)
        
        # Action recommendations
        if summary_metrics and summary_metrics['failed'] > 0:
            st.markdown("#### 💡 Recommendations")
            
            failed_types = {k: v for k, v in summary_metrics['expectation_types'].items() 
                          if v['total'] > v['passed']}
            
            if failed_types:
                st.write("**Focus areas for data quality improvement:**")
                for exp_type, counts in failed_types.items():
                    failures = counts['total'] - counts['passed']
                    st.write(f"- **{exp_type.replace('expect_', '').replace('_', ' ').title()}**: {failures} failures")
                
                st.write("**Suggested actions:**")
                st.write("1. Review the detailed results table for specific failure details")
                st.write("2. Investigate data sources for the most frequently failing expectations") 
                st.write("3. Consider updating data collection or cleaning processes")
                st.write("4. Re-run validation after implementing fixes")
    
    def _render_navigation_buttons(self):
        """Render navigation buttons"""
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("← Back to Validation", type="secondary"):
                st.session_state.current_step = 'validate'
                st.rerun()
        
        with col2:
            if st.button("🔄 Run New Validation", type="secondary"):
                # Reset validation state
                st.session_state.validation_completed = False
                st.session_state.validation_results = None
                st.session_state.current_step = 'expectations'
                st.rerun()
        
        with col3:
            if st.button("📁 Upload New Data", type="primary"):
                # Reset all state
                for key in ['uploaded_data', 'expectation_configs', 'expectation_suite', 
                           'validation_results', 'validation_completed']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.session_state.current_step = 'upload'
                st.rerun()