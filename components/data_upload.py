import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, Dict, Any
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_processing import DataProcessor
from config.app_config import AppConfig

class DataUploadComponent:
    """Component for data upload and initial analysis"""
    
    def __init__(self):
        self.processor = DataProcessor()
        self.config = AppConfig()
    
    def render(self):
        """Render the data upload interface"""
        st.markdown("### Upload your data file")
        
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
                
                # Show success message
                st.success(f"✅ Data loaded successfully! {len(df)} rows, {len(df.columns)} columns")
                
                # Show preview
                self.show_data_preview(df)
                
                # Show basic stats
                self.show_basic_stats(df)
                
                # Advance to next step button
                if st.button("Continue to Data Profiling →", type="primary"):
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
        
        # Data types distribution
        st.markdown("### 🏷️ Data Types Distribution")
        dtype_df = pd.DataFrame(list(profile['basic_info']['data_types'].items()), 
                               columns=['Data Type', 'Count'])
        
        fig_dtype = px.pie(dtype_df, values='Count', names='Data Type', 
                          title="Distribution of Data Types")
        fig_dtype.update_layout(height=400)
        st.plotly_chart(fig_dtype, use_container_width=True)
        
        # Missing data analysis
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
        
        # Action buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back to Upload", type="secondary"):
                st.session_state.current_step = 'upload'
                st.rerun()
        
        with col2:
            if st.button("Configure Expectations →", type="primary"):
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