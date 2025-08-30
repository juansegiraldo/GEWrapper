import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, Dict, Any
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_processing import DataProcessor
from utils.suite_helpers import get_clean_filename
from config.app_config import AppConfig

class DataUploadComponent:
    """Component for data upload and initial analysis"""
    
    def __init__(self):
        self.processor = DataProcessor()
        self.config = AppConfig()
    
    def render(self):
        """Render the data upload interface"""
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=self.config.SUPPORTED_FILE_TYPES,
            help=f"Supported formats: {', '.join(self.config.SUPPORTED_FILE_TYPES)}"
        )
        
        if uploaded_file is not None:
            # Check file size
            if uploaded_file.size > self.config.MAX_FILE_SIZE:
                st.error(f"File too large! Maximum size is {self.config.MAX_FILE_SIZE / (1024*1024):.1f} MB")
                return
            
            # Show file info
            st.info(f"📄 **{uploaded_file.name}** ({uploaded_file.size / (1024*1024):.2f} MB)")
            
            # Load data with progress
            with st.spinner("Loading data..."):
                df = self.processor.load_file(uploaded_file)
            
            if df is not None:
                # Store in session state
                st.session_state.uploaded_data = df
                
                # Store uploaded file name for suite naming
                uploaded_filename = uploaded_file.name
                base_filename = get_clean_filename(uploaded_filename)
                st.session_state.uploaded_filename = base_filename
                
                # Regenerate suite name with new filename
                from utils.suite_helpers import generate_suite_name
                new_suite_name = generate_suite_name()
                st.session_state.current_suite_name = new_suite_name
                
                # Show success message
                st.success(f"✅ Data loaded successfully! {len(df)} rows, {len(df.columns)} columns")
                
                # Show preview
                self.show_data_preview(df)
                
                # Show basic stats
                self.show_basic_stats(df)
                
                # Advance to next step button
                if st.button("Continue to Data Profiling →", type="primary", key="continue_to_profiling_btn"):
                    st.session_state.current_step = 'profile'
                    st.rerun()
    
    def show_data_preview(self, df: pd.DataFrame):
        """Show data preview"""
        st.markdown("### 👁️ Data Preview")
        
        # Show first few rows
        preview_rows = min(self.config.PREVIEW_ROWS, len(df))
        st.dataframe(
            df.head(preview_rows),
            use_container_width=True,
            height=min(400, (preview_rows + 1) * 35)
        )
        
        if len(df) > preview_rows:
            st.caption(f"Showing first {preview_rows} rows of {len(df)} total rows")
    
    def show_basic_stats(self, df: pd.DataFrame):
        """Show basic statistics"""
        st.markdown("### 📈 Basic Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Rows", f"{len(df):,}")
        
        with col2:
            st.metric("Columns", len(df.columns))
        
        with col3:
            memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
            st.metric("Memory Usage", f"{memory_mb:.1f} MB")
        
        with col4:
            missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
            st.metric("Missing Data", f"{missing_pct:.1f}%")
    
    def show_data_profile(self, df: pd.DataFrame):
        """Show comprehensive data profiling"""
        if df is None:
            st.warning("No data available for profiling!")
            return
        
        # Generate profile
        with st.spinner("Generating data profile..."):
            profile = self.processor.get_data_profile(df)
        
        if not profile:
            st.error("Failed to generate data profile!")
            return
        
        # Basic Information
        st.markdown("### 📋 Dataset Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Rows", f"{profile['basic_info']['rows']:,}")
        with col2:
            st.metric("Total Columns", profile['basic_info']['columns'])
        with col3:
            memory_mb = profile['basic_info']['memory_usage'] / (1024 * 1024)
            st.metric("Memory Usage", f"{memory_mb:.1f} MB")
        with col4:
            st.metric("Duplicate Rows", f"{profile['duplicates']['duplicate_rows']:,}")
        
        # Data types distribution and Missing data analysis in columns
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏷️ Data Types Distribution")
            dtype_df = pd.DataFrame(list(profile['basic_info']['data_types'].items()), 
                                   columns=['Data Type', 'Count'])
            
            fig_dtype = px.pie(dtype_df, values='Count', names='Data Type', 
                              title="Distribution of Data Types")
            fig_dtype.update_layout(height=400)
            st.plotly_chart(fig_dtype, use_container_width=True)
        
        with col2:
            if profile['missing_data']['columns_with_missing']:
                st.markdown("### 🕳️ Missing Data Analysis")
                
                missing_df = pd.DataFrame(list(profile['missing_data']['columns_with_missing'].items()),
                                        columns=['Column', 'Missing Count'])
                missing_df['Missing Percentage'] = (missing_df['Missing Count'] / len(df)) * 100
                missing_df = missing_df.sort_values('Missing Count', ascending=False)
                
                fig_missing = px.bar(missing_df, x='Column', y='Missing Percentage',
                                   title="Missing Data by Column",
                                   color='Missing Percentage',
                                   color_continuous_scale='Reds')
                fig_missing.update_layout(height=400, xaxis_tickangle=-45)
                st.plotly_chart(fig_missing, use_container_width=True)
                
                # Show table
                st.dataframe(missing_df, use_container_width=True)
            else:
                st.markdown("### 🕳️ Missing Data Analysis")
                st.info("No missing data found in the dataset!")
                st.markdown("🎉 **Perfect!** All columns have complete data.")
        
        # Column details
        st.markdown("### 📊 Column Details")
        
        # Allow user to select columns to view
        selected_columns = st.multiselect(
            "Select columns to view details:",
            options=list(df.columns),
            default=list(df.columns)[:5] if len(df.columns) > 5 else list(df.columns)
        )
        
        if selected_columns:
            for col in selected_columns:
                with st.expander(f"📊 {col} ({profile['column_info'][col]['dtype']})"):
                    col_info = profile['column_info'][col]
                    
                    # Basic metrics
                    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
                    
                    with metrics_col1:
                        st.metric("Non-null Count", f"{col_info['non_null_count']:,}")
                        st.metric("Unique Values", f"{col_info['unique_count']:,}")
                    
                    with metrics_col2:
                        st.metric("Null Count", f"{col_info['null_count']:,}")
                        st.metric("Unique %", f"{col_info['unique_percentage']:.1f}%")
                    
                    with metrics_col3:
                        st.metric("Null %", f"{col_info['null_percentage']:.1f}%")
                    
                    # Type-specific information
                    if pd.api.types.is_numeric_dtype(df[col]):
                        self._show_numeric_column_details(df[col], col_info)
                    elif pd.api.types.is_object_dtype(df[col]):
                        self._show_text_column_details(df[col], col_info)
                    elif pd.api.types.is_datetime64_any_dtype(df[col]):
                        self._show_datetime_column_details(df[col], col_info)
        
        # Column type suggestions
        st.markdown("### 🎯 Column Type Optimization Suggestions")
        suggestions = self.processor.detect_column_types(df)
        
        suggestion_data = []
        for col, suggested_type in suggestions.items():
            current_type = str(df[col].dtype)
            if current_type != suggested_type:
                suggestion_data.append({
                    'Column': col,
                    'Current Type': current_type,
                    'Suggested Type': suggested_type,
                    'Memory Savings': self._estimate_memory_savings(df[col], suggested_type)
                })
        
        if suggestion_data:
            suggestions_df = pd.DataFrame(suggestion_data)
            st.dataframe(suggestions_df, use_container_width=True)
        else:
            st.info("All columns are already using optimal data types!")
        
        # Download section
        st.markdown("### 💾 Download Data Profile")
        st.write("Export your data profile in various formats for reporting and analysis.")
        
        # Preview what will be included in the download
        with st.expander("👁️ Preview Download Contents", expanded=False):
            st.markdown("**📊 What's included in your download:**")
            
            preview_col1, preview_col2 = st.columns(2)
            with preview_col1:
                st.markdown("**Summary Information:**")
                st.write(f"• Total rows: {profile['basic_info']['rows']:,}")
                st.write(f"• Total columns: {profile['basic_info']['columns']}")
                st.write(f"• Memory usage: {profile['basic_info']['memory_usage'] / (1024 * 1024):.1f} MB")
                st.write(f"• Missing data: {profile['missing_data']['missing_percentage']:.1f}%")
                st.write(f"• Duplicate rows: {profile['duplicates']['duplicate_rows']:,}")
            
            with preview_col2:
                st.markdown("**Detailed Analysis:**")
                st.write(f"• Column-by-column statistics")
                st.write(f"• Data type distribution")
                st.write(f"• Missing data analysis")
                st.write(f"• Data quality insights")
                st.write(f"• Sample data (Excel format)")
        
        # Show download options with descriptions
        with st.expander("📋 Download Options", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📄 JSON Format**")
                st.write("Complete profile data in JSON format. Best for programmatic analysis and integration.")
                if st.button("Download JSON", key="download_json_btn", type="secondary"):
                    self._download_profile(df, profile, 'json')
                
                st.markdown("**📊 Excel Format**")
                st.write("Multi-sheet Excel file with summary, column details, and sample data. Best for business users.")
                if st.button("Download Excel", key="download_excel_btn", type="secondary"):
                    self._download_profile(df, profile, 'excel')
            
            with col2:
                st.markdown("**🌐 HTML Format**")
                st.write("Formatted HTML report with styling. Best for web viewing and sharing.")
                if st.button("Download HTML", key="download_html_btn", type="secondary"):
                    self._download_profile(df, profile, 'html')
                
                st.markdown("**📋 CSV Format**")
                st.write("Summary data in CSV format. Best for spreadsheet analysis.")
                if st.button("Download CSV", key="download_csv_btn", type="secondary"):
                    self._download_profile(df, profile, 'csv')
        
        # Quick download all formats
        st.markdown("**🚀 Quick Download All Formats**")
        if st.button("Download All Formats", key="download_all_btn", type="primary"):
            self._download_all_formats(df, profile)
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Upload", type="secondary", key="back_to_upload_btn"):
                st.session_state.current_step = 'upload'
                st.rerun()
        
        with col2:
            if st.button("Configure Expectations →", type="primary", key="configure_expectations_btn"):
                st.session_state.current_step = 'expectations'
                st.rerun()
    
    def _show_numeric_column_details(self, series: pd.Series, col_info: Dict):
        """Show details for numeric columns"""
        # Statistics
        stats_col1, stats_col2 = st.columns(2)
        
        with stats_col1:
            st.write("**Statistics:**")
            st.write(f"Mean: {col_info.get('mean', 'N/A'):.2f}")
            st.write(f"Median: {col_info.get('median', 'N/A'):.2f}")
            st.write(f"Std Dev: {col_info.get('std', 'N/A'):.2f}")
        
        with stats_col2:
            st.write("**Range:**")
            st.write(f"Min: {col_info.get('min', 'N/A')}")
            st.write(f"Max: {col_info.get('max', 'N/A')}")
            st.write(f"Q25: {col_info.get('q25', 'N/A'):.2f}")
            st.write(f"Q75: {col_info.get('q75', 'N/A'):.2f}")
        
        # Distribution plot
        try:
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=series.dropna(), nbinsx=30, name="Distribution"))
            fig.update_layout(
                title=f"Distribution of {series.name}",
                xaxis_title=series.name,
                yaxis_title="Frequency",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not create distribution plot: {str(e)}")
    
    def _show_text_column_details(self, series: pd.Series, col_info: Dict):
        """Show details for text columns"""
        # Text statistics
        stats_col1, stats_col2 = st.columns(2)
        
        with stats_col1:
            st.write("**Text Length:**")
            st.write(f"Max Length: {col_info.get('max_length', 'N/A')}")
            st.write(f"Min Length: {col_info.get('min_length', 'N/A')}")
            st.write(f"Avg Length: {col_info.get('avg_length', 'N/A'):.1f}")
        
        with stats_col2:
            st.write("**Most Common Values:**")
            most_common = col_info.get('most_common', {})
            for value, count in list(most_common.items())[:5]:
                st.write(f"{value}: {count}")
        
        # Value counts chart
        if most_common:
            try:
                top_values = dict(list(most_common.items())[:10])
                fig = px.bar(
                    x=list(top_values.keys()),
                    y=list(top_values.values()),
                    title=f"Top Values in {series.name}"
                )
                fig.update_layout(height=300, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Could not create value counts chart: {str(e)}")
    
    def _show_datetime_column_details(self, series: pd.Series, col_info: Dict):
        """Show details for datetime columns"""
        st.write("**Date Range:**")
        st.write(f"Earliest: {col_info.get('earliest', 'N/A')}")
        st.write(f"Latest: {col_info.get('latest', 'N/A')}")
        st.write(f"Range: {col_info.get('date_range_days', 'N/A')} days")
        
        # Timeline plot
        try:
            daily_counts = series.dt.date.value_counts().sort_index()
            fig = px.line(
                x=daily_counts.index,
                y=daily_counts.values,
                title=f"Timeline of {series.name}"
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not create timeline plot: {str(e)}")
    
    def _estimate_memory_savings(self, series: pd.Series, suggested_type: str) -> str:
        """Estimate memory savings from type conversion"""
        try:
            current_memory = series.memory_usage(deep=True)
            
            # Rough estimates based on type
            type_sizes = {
                'int8': 1, 'int16': 2, 'int32': 4, 'int64': 8,
                'uint8': 1, 'uint16': 2, 'uint32': 4, 'uint64': 8,
                'float32': 4, 'float64': 8,
                'category': series.nunique() * 8 + len(series)  # rough estimate
            }
            
            if suggested_type in type_sizes:
                new_memory = type_sizes[suggested_type] * len(series)
                savings_pct = ((current_memory - new_memory) / current_memory) * 100
                return f"{savings_pct:.1f}%"
            
            return "Unknown"
        except:
            return "Unknown"
    
    def _download_profile(self, df: pd.DataFrame, profile: Dict[str, Any], format_type: str):
        """Download data profile in specified format"""
        try:
            # Generate the profile content
            profile_content = self.processor.generate_downloadable_profile(df, profile, format_type)
            
            if profile_content is None:
                st.error("Failed to generate profile download!")
                return
            
            # Create filename with original filename and timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_filename = st.session_state.get('uploaded_filename', 'unknown_dataset')
            
            # Map format types to proper file extensions
            file_extensions = {
                'json': 'json',
                'excel': 'xlsx',
                'html': 'html',
                'csv': 'csv'
            }
            
            file_extension = file_extensions.get(format_type, format_type)
            filename = f"{original_filename}_profile_{timestamp}.{file_extension}"
            
            # Set appropriate MIME type
            mime_types = {
                'json': 'application/json',
                'excel': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'html': 'text/html',
                'csv': 'text/csv'
            }
            
            # Create download button
            st.download_button(
                label=f"📥 Download {format_type.upper()} Profile",
                data=profile_content,
                file_name=filename,
                mime=mime_types.get(format_type, 'application/octet-stream'),
                key=f"download_{format_type}_{timestamp}"
            )
            
            # Show success message
            st.success(f"✅ {format_type.upper()} profile ready for download!")
            
        except Exception as e:
            st.error(f"Error creating download: {str(e)}")
    
    def _download_all_formats(self, df: pd.DataFrame, profile: Dict[str, Any]):
        """Download data profile in all available formats"""
        try:
            formats = ['json', 'excel', 'html', 'csv']
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            original_filename = st.session_state.get('uploaded_filename', 'unknown_dataset')
            
            # Create a zip file containing all formats
            import zipfile
            from io import BytesIO
            
            zip_buffer = BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for format_type in formats:
                    try:
                        # Generate content for each format
                        content = self.processor.generate_downloadable_profile(df, profile, format_type)
                        if content:
                            # Map format types to proper file extensions
                            file_extensions = {
                                'json': 'json',
                                'excel': 'xlsx',
                                'html': 'html',
                                'csv': 'csv'
                            }
                            file_extension = file_extensions.get(format_type, format_type)
                            filename = f"{original_filename}_profile_{timestamp}.{file_extension}"
                            zip_file.writestr(filename, content)
                    except Exception as e:
                        st.warning(f"Could not generate {format_type.upper()} format: {str(e)}")
            
            # Create download button for zip file
            zip_filename = f"{original_filename}_profile_all_formats_{timestamp}.zip"
            
            st.download_button(
                label="📦 Download All Formats (ZIP)",
                data=zip_buffer.getvalue(),
                file_name=zip_filename,
                mime='application/zip',
                key=f"download_all_{timestamp}"
            )
            
            st.success("✅ All formats packaged and ready for download!")
            
        except Exception as e:
            st.error(f"Error creating multi-format download: {str(e)}")