import pandas as pd
import numpy as np
import json
from typing import Dict, List, Any, Optional, Tuple
import streamlit as st
from io import StringIO, BytesIO

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