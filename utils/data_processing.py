import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Optional, Tuple
import streamlit as st
from io import StringIO, BytesIO
import base64
from datetime import datetime
import html

class DataProcessor:
    """Utility class for data processing operations"""
    
    @staticmethod
    def load_file(uploaded_file) -> Optional[pd.DataFrame]:
        """Load uploaded file into pandas DataFrame"""
        try:
            file_extension = uploaded_file.name.split('.')[-1].lower()
            
            if file_extension == 'csv':
                # Try different encodings and separators
                content = uploaded_file.read()
                
                # Try UTF-8 first
                try:
                    df = pd.read_csv(StringIO(content.decode('utf-8')))
                    # Convert string booleans to actual booleans
                    df = DataProcessor._convert_string_booleans(df)
                    return df
                except UnicodeDecodeError:
                    # Try other encodings
                    for encoding in ['latin-1', 'iso-8859-1', 'cp1252']:
                        try:
                            df = pd.read_csv(StringIO(content.decode(encoding)))
                            # Convert string booleans to actual booleans
                            df = DataProcessor._convert_string_booleans(df)
                            return df
                        except:
                            continue
                    
                    # If all encodings fail, try with errors='ignore'
                    df = pd.read_csv(StringIO(content.decode('utf-8', errors='ignore')))
                    # Convert string booleans to actual booleans
                    df = DataProcessor._convert_string_booleans(df)
                    return df
                    
            elif file_extension in ['xlsx', 'xls']:
                df = pd.read_excel(uploaded_file, engine='openpyxl')
                return df
                
            elif file_extension == 'json':
                # Read as JSON
                content = uploaded_file.read()
                json_data = json.loads(content.decode('utf-8'))
                
                # Handle different JSON structures
                if isinstance(json_data, list):
                    df = pd.json_normalize(json_data)
                elif isinstance(json_data, dict):
                    # Check if it's a dictionary with arrays
                    if all(isinstance(v, list) for v in json_data.values()):
                        df = pd.DataFrame(json_data)
                    else:
                        # Single record
                        df = pd.json_normalize([json_data])
                else:
                    raise ValueError("Unsupported JSON structure")
                
                return df
                
            elif file_extension == 'parquet':
                df = pd.read_parquet(uploaded_file)
                return df
                
            else:
                st.error(f"Unsupported file format: {file_extension}")
                return None
                
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return None
    
    @staticmethod
    def get_data_profile(df: pd.DataFrame) -> Dict[str, Any]:
        """Generate comprehensive data profile"""
        try:
            profile = {
                'basic_info': {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'memory_usage': df.memory_usage(deep=True).sum(),
                    'data_types': {str(k): v for k, v in df.dtypes.value_counts().to_dict().items()}
                },
                'column_info': {},
                'missing_data': {
                    'total_missing': df.isnull().sum().sum(),
                    'missing_percentage': (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
                    'columns_with_missing': df.isnull().sum()[df.isnull().sum() > 0].to_dict()
                },
                'duplicates': {
                    'duplicate_rows': df.duplicated().sum(),
                    'duplicate_percentage': (df.duplicated().sum() / len(df)) * 100
                }
            }
            
            # Column-specific information
            for col in df.columns:
                try:
                    col_info = {
                        'dtype': str(df[col].dtype),
                        'non_null_count': df[col].count(),
                        'null_count': df[col].isnull().sum(),
                        'null_percentage': (df[col].isnull().sum() / len(df)) * 100,
                        'unique_count': df[col].nunique(),
                        'unique_percentage': (df[col].nunique() / len(df)) * 100
                    }
                    
                    # Numeric columns - handle potential boolean string columns
                    if pd.api.types.is_numeric_dtype(df[col]):
                        # Check if it's actually numeric and not boolean strings
                        try:
                            col_info.update({
                                'mean': df[col].mean(),
                                'median': df[col].median(),
                                'std': df[col].std(),
                                'min': df[col].min(),
                                'max': df[col].max(),
                                'q25': df[col].quantile(0.25),
                                'q75': df[col].quantile(0.75)
                            })
                        except (TypeError, ValueError) as e:
                            # Handle cases where numeric operations fail (e.g., boolean strings)
                            col_info['numeric_stats_error'] = str(e)
                    
                    # Text columns
                    elif pd.api.types.is_object_dtype(df[col]):
                        try:
                            col_info.update({
                                'max_length': df[col].astype(str).str.len().max(),
                                'min_length': df[col].astype(str).str.len().min(),
                                'avg_length': df[col].astype(str).str.len().mean(),
                                'most_common': df[col].value_counts().head().to_dict()
                            })
                        except Exception as e:
                            col_info['text_stats_error'] = str(e)
                    
                    # Datetime columns
                    elif pd.api.types.is_datetime64_any_dtype(df[col]):
                        try:
                            col_info.update({
                                'earliest': df[col].min(),
                                'latest': df[col].max(),
                                'date_range_days': (df[col].max() - df[col].min()).days
                            })
                        except Exception as e:
                            col_info['datetime_stats_error'] = str(e)
                    
                    # Boolean columns (including string booleans)
                    elif str(df[col].dtype) == 'bool' or DataProcessor._is_boolean_column(df[col]):
                        try:
                            # Convert string booleans to actual booleans for analysis
                            if pd.api.types.is_object_dtype(df[col]):
                                bool_series = df[col].astype(str).str.lower().map({'true': True, 'false': False})
                            else:
                                bool_series = df[col].astype(bool)
                            
                            col_info.update({
                                'true_count': bool_series.sum(),
                                'false_count': (~bool_series).sum(),
                                'true_percentage': (bool_series.sum() / len(bool_series)) * 100,
                                'false_percentage': ((~bool_series).sum() / len(bool_series)) * 100
                            })
                        except Exception as e:
                            col_info['boolean_stats_error'] = str(e)
                    
                    profile['column_info'][col] = col_info
                    
                except Exception as col_error:
                    # If individual column processing fails, add error info
                    profile['column_info'][col] = {
                        'dtype': str(df[col].dtype),
                        'processing_error': str(col_error)
                    }
            
            return profile
            
        except Exception as e:
            st.error(f"Error generating data profile: {str(e)}")
            return {}
    
    @staticmethod
    def detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
        """Detect and suggest optimal column types"""
        suggestions = {}
        
        for col in df.columns:
            current_type = str(df[col].dtype)
            
            # Skip if already datetime
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                suggestions[col] = 'datetime'
                continue
            
            # Try to detect dates
            if pd.api.types.is_object_dtype(df[col]):
                sample_values = df[col].dropna().head(100)
                
                # Check if it looks like dates
                date_like_count = 0
                for val in sample_values:
                    try:
                        pd.to_datetime(val)
                        date_like_count += 1
                    except:
                        pass
                
                if date_like_count > len(sample_values) * 0.8:
                    suggestions[col] = 'datetime'
                    continue
            
            # Check if numeric columns can be optimized
            if pd.api.types.is_numeric_dtype(df[col]):
                if pd.api.types.is_integer_dtype(df[col]):
                    max_val = df[col].max()
                    min_val = df[col].min()
                    
                    if min_val >= 0:
                        if max_val <= 255:
                            suggestions[col] = 'uint8'
                        elif max_val <= 65535:
                            suggestions[col] = 'uint16'
                        elif max_val <= 4294967295:
                            suggestions[col] = 'uint32'
                        else:
                            suggestions[col] = 'uint64'
                    else:
                        if min_val >= -128 and max_val <= 127:
                            suggestions[col] = 'int8'
                        elif min_val >= -32768 and max_val <= 32767:
                            suggestions[col] = 'int16'
                        elif min_val >= -2147483648 and max_val <= 2147483647:
                            suggestions[col] = 'int32'
                        else:
                            suggestions[col] = 'int64'
                else:
                    suggestions[col] = 'float32' if df[col].dtype == 'float64' else current_type
            else:
                # Check if categorical
                if df[col].nunique() / len(df) < 0.1 and df[col].nunique() < 50:
                    suggestions[col] = 'category'
                else:
                    suggestions[col] = current_type
        
        return suggestions
    
    @staticmethod
    def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
        """Clean column names for better compatibility"""
        df_clean = df.copy()
        
        # Replace spaces and special characters
        df_clean.columns = df_clean.columns.str.replace(' ', '_')
        df_clean.columns = df_clean.columns.str.replace('[^A-Za-z0-9_]', '', regex=True)
        df_clean.columns = df_clean.columns.str.lower()
        
        # Ensure no duplicate column names
        cols = pd.Series(df_clean.columns)
        for dup in cols[cols.duplicated()].unique():
            cols[cols == dup] = [f"{dup}_{i}" for i in range(sum(cols == dup))]
        df_clean.columns = cols
        
        return df_clean
    
    @staticmethod
    def sample_data_smart(df: pd.DataFrame, max_rows: int = 10000) -> Tuple[pd.DataFrame, bool]:
        """Smart sampling that preserves data characteristics"""
        if len(df) <= max_rows:
            return df, False
        
        # For categorical columns, ensure all categories are represented
        sampled_df = df.copy()
        is_sampled = True
        
        # Try stratified sampling if there are categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        if len(categorical_cols) > 0:
            # Use the first categorical column for stratification
            strat_col = categorical_cols[0]
            try:
                # Sample proportionally from each category
                sample_df = df.groupby(strat_col, group_keys=False).apply(
                    lambda x: x.sample(min(len(x), max_rows // df[strat_col].nunique() + 1))
                ).reset_index(drop=True)
                
                if len(sample_df) <= max_rows:
                    return sample_df, is_sampled
            except:
                pass
        
        # Fallback to random sampling
        return df.sample(n=max_rows, random_state=42).reset_index(drop=True), is_sampled
    
    @staticmethod
    def _is_boolean_column(series: pd.Series) -> bool:
        """Check if a column contains boolean-like values"""
        if pd.api.types.is_object_dtype(series):
            unique_vals = series.dropna().unique()
            if len(unique_vals) <= 2:
                # Check if all values are boolean-like
                bool_like = all(str(val).lower() in ['true', 'false', '1', '0', 'yes', 'no'] for val in unique_vals)
                return bool_like
        return False
    
    @staticmethod
    def _convert_string_booleans(df: pd.DataFrame) -> pd.DataFrame:
        """Convert string boolean values to actual boolean type"""
        df_clean = df.copy()
        
        for col in df_clean.columns:
            if pd.api.types.is_object_dtype(df_clean[col]):
                # Check if column contains only boolean-like strings
                unique_vals = df_clean[col].dropna().unique()
                if len(unique_vals) <= 2:
                    # Check if all values are boolean-like
                    bool_like = all(str(val).lower() in ['true', 'false', '1', '0', 'yes', 'no'] for val in unique_vals)
                    if bool_like:
                        try:
                            # Convert to boolean
                            df_clean[col] = df_clean[col].astype(str).str.lower().map({
                                'true': True, 'false': False,
                                '1': True, '0': False,
                                'yes': True, 'no': False
                            })
                        except Exception:
                            # If conversion fails, keep as is
                            pass
        
        return df_clean
    
    @staticmethod
    def export_to_format(df: pd.DataFrame, format_type: str) -> bytes:
        """Export DataFrame to specified format"""
        try:
            if format_type == 'csv':
                return df.to_csv(index=False).encode('utf-8')
            elif format_type == 'json':
                return df.to_json(orient='records', indent=2).encode('utf-8')
            elif format_type == 'excel':
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Data')
                return buffer.getvalue()
            elif format_type == 'parquet':
                buffer = BytesIO()
                df.to_parquet(buffer, index=False)
                return buffer.getvalue()
            else:
                raise ValueError(f"Unsupported format: {format_type}")
        except Exception as e:
            st.error(f"Error exporting data: {str(e)}")
            return None
    
    @staticmethod
    def generate_downloadable_profile(df: pd.DataFrame, profile: Dict[str, Any], format_type: str = 'json') -> bytes:
        """Generate downloadable data profile in specified format"""
        try:
            if format_type == 'json':
                return DataProcessor._generate_json_profile(df, profile)
            elif format_type == 'excel':
                return DataProcessor._generate_excel_profile(df, profile)
            elif format_type == 'html':
                return DataProcessor._generate_html_profile(df, profile)
            elif format_type == 'csv':
                return DataProcessor._generate_csv_profile(df, profile)
            else:
                raise ValueError(f"Unsupported format: {format_type}")
        except Exception as e:
            st.error(f"Error generating profile download: {str(e)}")
            return None
    
    @staticmethod
    def _generate_json_profile(df: pd.DataFrame, profile: Dict[str, Any]) -> bytes:
        """Generate JSON format data profile"""
        # Add metadata
        profile_with_metadata = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'file_name': getattr(df, 'name', 'unknown'),
                'total_rows': len(df),
                'total_columns': len(df.columns)
            },
            'profile': profile
        }
        
        return json.dumps(profile_with_metadata, indent=2, default=str).encode('utf-8')
    
    @staticmethod
    def _generate_excel_profile(df: pd.DataFrame, profile: Dict[str, Any]) -> bytes:
        """Generate Excel format data profile with multiple sheets"""
        buffer = BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = [
                ['Metric', 'Value'],
                ['Total Rows', profile['basic_info']['rows']],
                ['Total Columns', profile['basic_info']['columns']],
                ['Memory Usage (MB)', profile['basic_info']['memory_usage'] / (1024 * 1024)],
                ['Total Missing Values', profile['missing_data']['total_missing']],
                ['Missing Percentage', f"{profile['missing_data']['missing_percentage']:.2f}%"],
                ['Duplicate Rows', profile['duplicates']['duplicate_rows']],
                ['Duplicate Percentage', f"{profile['duplicates']['duplicate_percentage']:.2f}%"],
                ['Generated At', datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
            ]
            
            summary_df = pd.DataFrame(summary_data[1:], columns=summary_data[0])
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Data types distribution
            dtype_data = list(profile['basic_info']['data_types'].items())
            dtype_df = pd.DataFrame(dtype_data, columns=['Data Type', 'Count'])
            dtype_df.to_excel(writer, sheet_name='Data Types', index=False)
            
            # Missing data analysis
            if profile['missing_data']['columns_with_missing']:
                missing_data = list(profile['missing_data']['columns_with_missing'].items())
                missing_df = pd.DataFrame(missing_data, columns=['Column', 'Missing Count'])
                missing_df['Missing Percentage'] = (missing_df['Missing Count'] / len(df)) * 100
                missing_df = missing_df.sort_values('Missing Count', ascending=False)
                missing_df.to_excel(writer, sheet_name='Missing Data', index=False)
            
            # Column details
            column_details = []
            for col, col_info in profile['column_info'].items():
                row = {
                    'Column': col,
                    'Data Type': col_info.get('dtype', 'N/A'),
                    'Non-null Count': col_info.get('non_null_count', 0),
                    'Null Count': col_info.get('null_count', 0),
                    'Null Percentage': f"{col_info.get('null_percentage', 0):.2f}%",
                    'Unique Count': col_info.get('unique_count', 0),
                    'Unique Percentage': f"{col_info.get('unique_percentage', 0):.2f}%"
                }
                
                # Add type-specific information
                if 'mean' in col_info:
                    row.update({
                        'Mean': col_info.get('mean', 'N/A'),
                        'Median': col_info.get('median', 'N/A'),
                        'Std Dev': col_info.get('std', 'N/A'),
                        'Min': col_info.get('min', 'N/A'),
                        'Max': col_info.get('max', 'N/A')
                    })
                elif 'max_length' in col_info:
                    row.update({
                        'Max Length': col_info.get('max_length', 'N/A'),
                        'Min Length': col_info.get('min_length', 'N/A'),
                        'Avg Length': f"{col_info.get('avg_length', 0):.1f}"
                    })
                elif 'earliest' in col_info:
                    row.update({
                        'Earliest': col_info.get('earliest', 'N/A'),
                        'Latest': col_info.get('latest', 'N/A'),
                        'Date Range (Days)': col_info.get('date_range_days', 'N/A')
                    })
                
                column_details.append(row)
            
            column_df = pd.DataFrame(column_details)
            column_df.to_excel(writer, sheet_name='Column Details', index=False)
            
            # Sample data
            sample_df = df.head(1000)  # Limit to first 1000 rows for Excel
            sample_df.to_excel(writer, sheet_name='Sample Data', index=False)
        
        return buffer.getvalue()
    
    @staticmethod
    def _generate_html_profile(df: pd.DataFrame, profile: Dict[str, Any]) -> bytes:
        """Generate HTML format data profile with styling"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Profile Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
                .section {{ margin-bottom: 30px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e8f4fd; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .warning {{ color: #856404; background-color: #fff3cd; padding: 10px; border-radius: 5px; }}
                .success {{ color: #155724; background-color: #d4edda; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Data Profile Report</h1>
                <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Dataset:</strong> {len(df):,} rows × {len(df.columns)} columns</p>
            </div>
            
            <div class="section">
                <h2>📋 Dataset Overview</h2>
                <div class="metric"><strong>Total Rows:</strong> {profile['basic_info']['rows']:,}</div>
                <div class="metric"><strong>Total Columns:</strong> {profile['basic_info']['columns']}</div>
                <div class="metric"><strong>Memory Usage:</strong> {profile['basic_info']['memory_usage'] / (1024 * 1024):.1f} MB</div>
                <div class="metric"><strong>Duplicate Rows:</strong> {profile['duplicates']['duplicate_rows']:,}</div>
            </div>
            
            <div class="section">
                <h2>🏷️ Data Types Distribution</h2>
                <table>
                    <tr><th>Data Type</th><th>Count</th></tr>
        """
        
        for dtype, count in profile['basic_info']['data_types'].items():
            html_content += f"<tr><td>{html.escape(str(dtype))}</td><td>{count}</td></tr>"
        
        html_content += """
                </table>
            </div>
        """
        
        # Missing data section
        if profile['missing_data']['columns_with_missing']:
            html_content += """
            <div class="section">
                <h2>🕳️ Missing Data Analysis</h2>
                <table>
                    <tr><th>Column</th><th>Missing Count</th><th>Missing Percentage</th></tr>
            """
            
            for col, missing_count in profile['missing_data']['columns_with_missing'].items():
                missing_pct = (missing_count / len(df)) * 100
                html_content += f"<tr><td>{html.escape(col)}</td><td>{missing_count:,}</td><td>{missing_pct:.2f}%</td></tr>"
            
            html_content += """
                </table>
            </div>
            """
        
        # Column details section
        html_content += """
            <div class="section">
                <h2>📊 Column Details</h2>
                <table>
                    <tr><th>Column</th><th>Data Type</th><th>Non-null</th><th>Null</th><th>Null %</th><th>Unique</th><th>Unique %</th></tr>
        """
        
        for col, col_info in profile['column_info'].items():
            html_content += f"""
                <tr>
                    <td>{html.escape(col)}</td>
                    <td>{html.escape(str(col_info.get('dtype', 'N/A')))}</td>
                    <td>{col_info.get('non_null_count', 0):,}</td>
                    <td>{col_info.get('null_count', 0):,}</td>
                    <td>{col_info.get('null_percentage', 0):.2f}%</td>
                    <td>{col_info.get('unique_count', 0):,}</td>
                    <td>{col_info.get('unique_percentage', 0):.2f}%</td>
                </tr>
            """
        
        html_content += """
                </table>
            </div>
        """
        
        # Data quality insights
        html_content += """
            <div class="section">
                <h2>🎯 Data Quality Insights</h2>
        """
        
        # Check for potential issues
        issues = []
        if profile['missing_data']['missing_percentage'] > 10:
            issues.append(f"High missing data rate: {profile['missing_data']['missing_percentage']:.1f}%")
        
        if profile['duplicates']['duplicate_percentage'] > 5:
            issues.append(f"High duplicate rate: {profile['duplicates']['duplicate_percentage']:.1f}%")
        
        if issues:
            html_content += '<div class="warning"><h3>⚠️ Potential Issues:</h3><ul>'
            for issue in issues:
                html_content += f'<li>{issue}</li>'
            html_content += '</ul></div>'
        else:
            html_content += '<div class="success"><h3>✅ Data Quality Assessment:</h3><p>No major data quality issues detected.</p></div>'
        
        html_content += """
            </div>
        </body>
        </html>
        """
        
        return html_content.encode('utf-8')
    
    @staticmethod
    def _generate_csv_profile(df: pd.DataFrame, profile: Dict[str, Any]) -> bytes:
        """Generate CSV format data profile summary"""
        # Create a summary CSV with key metrics
        summary_data = []
        
        # Basic info
        summary_data.append(['Metric', 'Value'])
        summary_data.append(['Total Rows', profile['basic_info']['rows']])
        summary_data.append(['Total Columns', profile['basic_info']['columns']])
        summary_data.append(['Memory Usage (MB)', profile['basic_info']['memory_usage'] / (1024 * 1024)])
        summary_data.append(['Total Missing Values', profile['missing_data']['total_missing']])
        summary_data.append(['Missing Percentage', f"{profile['missing_data']['missing_percentage']:.2f}%"])
        summary_data.append(['Duplicate Rows', profile['duplicates']['duplicate_rows']])
        summary_data.append(['Duplicate Percentage', f"{profile['duplicates']['duplicate_percentage']:.2f}%"])
        summary_data.append(['Generated At', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        summary_data.append(['', ''])  # Empty row
        
        # Column details
        summary_data.append(['Column', 'Data Type', 'Non-null', 'Null', 'Null %', 'Unique', 'Unique %'])
        for col, col_info in profile['column_info'].items():
            summary_data.append([
                col,
                str(col_info.get('dtype', 'N/A')),
                col_info.get('non_null_count', 0),
                col_info.get('null_count', 0),
                f"{col_info.get('null_percentage', 0):.2f}%",
                col_info.get('unique_count', 0),
                f"{col_info.get('unique_percentage', 0):.2f}%"
            ])
        
        # Convert to CSV
        csv_content = '\n'.join([','.join([str(cell) for cell in row]) for row in summary_data])
        return csv_content.encode('utf-8')