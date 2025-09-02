import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import re


class SmartTemplateEngine:
    """Intelligent template engine that analyzes data and creates better expectations"""
    
    def __init__(self):
        pass
    
    def analyze_data_for_template(self, data: pd.DataFrame, template_name: str) -> List[Dict[str, Any]]:
        """Analyze data and generate intelligent expectations for a given template"""
        
        if template_name == "Smart Basic Quality":
            return self._generate_smart_basic_quality(data)
        elif template_name == "Smart Numeric Validation":
            return self._generate_smart_numeric_validation(data)
        elif template_name == "Smart Text Validation":
            return self._generate_smart_text_validation(data)
        elif template_name == "Smart Business Rules":
            return self._generate_smart_business_rules(data)
        else:
            return []
    
    def _generate_smart_basic_quality(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate intelligent basic quality expectations"""
        expectations = []
        
        # Table row count with smart bounds
        row_count = len(data)
        expectations.append({
            'expectation_type': 'expect_table_row_count_to_be_between',
            'kwargs': {
                'min_value': max(1, int(row_count * 0.95)),
                'max_value': int(row_count * 1.05)
            }
        })
        
        # Column structure validation
        expectations.append({
            'expectation_type': 'expect_table_columns_to_match_ordered_list',
            'kwargs': {
                'column_list': list(data.columns)
            }
        })
        
        # Smart null validation - only for columns with low null rates
        for col in data.columns:
            null_pct = (data[col].isnull().sum() / len(data)) * 100
            if null_pct < 10:  # Only add null check for columns with < 10% nulls
                expectations.append({
                    'expectation_type': 'expect_column_values_to_not_be_null',
                    'kwargs': {'column': col}
                })
        
        # Unique value validation for likely ID columns
        for col in data.columns:
            col_lower = col.lower()
            unique_ratio = data[col].nunique() / len(data) if len(data) > 0 else 0
            
            if (any(term in col_lower for term in ['id', 'key', 'uuid', 'guid']) or 
                unique_ratio > 0.95):
                expectations.append({
                    'expectation_type': 'expect_column_values_to_be_unique',
                    'kwargs': {'column': col}
                })
        
        return expectations
    
    def _generate_smart_numeric_validation(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate intelligent numeric validation expectations"""
        expectations = []
        numeric_columns = data.select_dtypes(include=[np.number]).columns
        
        for col in numeric_columns:
            clean_data = data[col].dropna()
            if len(clean_data) == 0:
                continue
            
            # Smart range validation with outlier consideration
            q1 = clean_data.quantile(0.25)
            q3 = clean_data.quantile(0.75)
            iqr = q3 - q1
            
            # Use IQR-based bounds but not too restrictive
            lower_bound = max(clean_data.min(), q1 - 2 * iqr)
            upper_bound = min(clean_data.max(), q3 + 2 * iqr)
            
            expectations.append({
                'expectation_type': 'expect_column_values_to_be_between',
                'kwargs': {
                    'column': col,
                    'min_value': float(lower_bound),
                    'max_value': float(upper_bound)
                }
            })
            
            # Type validation
            expectations.append({
                'expectation_type': 'expect_column_values_to_be_of_type',
                'kwargs': {
                    'column': col,
                    'type_': 'float' if clean_data.dtype == 'float64' else 'int'
                }
            })
            
            # Statistical validation for stable datasets
            if clean_data.std() > 0:  # Only if there's variation
                mean_val = clean_data.mean()
                std_val = clean_data.std()
                
                expectations.append({
                    'expectation_type': 'expect_column_mean_to_be_between',
                    'kwargs': {
                        'column': col,
                        'min_value': float(mean_val - 2 * std_val),
                        'max_value': float(mean_val + 2 * std_val)
                    }
                })
        
        return expectations
    
    def _generate_smart_text_validation(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate intelligent text validation expectations"""
        expectations = []
        text_columns = data.select_dtypes(include=['object']).columns
        
        for col in text_columns:
            clean_data = data[col].dropna().astype(str)
            if len(clean_data) == 0:
                continue
            
            col_lower = col.lower()
            
            # Email validation
            if 'email' in col_lower or self._is_email_column(clean_data):
                expectations.append({
                    'expectation_type': 'expect_column_values_to_match_regex',
                    'kwargs': {
                        'column': col,
                        'regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    }
                })
                continue
            
            # Length validation with smart bounds
            lengths = clean_data.str.len()
            min_len = int(lengths.min())
            max_len = int(lengths.max())
            avg_len = lengths.mean()
            
            # Use reasonable bounds - not too restrictive
            lower_bound = max(0, min_len - 1)
            upper_bound = max_len + max(5, int(avg_len * 0.2))  # Add 20% tolerance or 5 chars
            
            expectations.append({
                'expectation_type': 'expect_column_value_lengths_to_be_between',
                'kwargs': {
                    'column': col,
                    'min_value': lower_bound,
                    'max_value': upper_bound
                }
            })
            
            # Categorical validation for low-cardinality columns
            unique_count = clean_data.nunique()
            if unique_count <= 20 and unique_count / len(clean_data) < 0.1:
                expectations.append({
                    'expectation_type': 'expect_column_values_to_be_in_set',
                    'kwargs': {
                        'column': col,
                        'value_set': list(clean_data.unique())
                    }
                })
        
        return expectations
    
    def _generate_smart_business_rules(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate business rule expectations based on data patterns"""
        expectations = []
        
        # Detect common business patterns
        for col in data.columns:
            col_lower = col.lower()
            clean_data = data[col].dropna()
            
            if len(clean_data) == 0:
                continue
            
            # Age validation
            if 'age' in col_lower and pd.api.types.is_numeric_dtype(data[col]):
                expectations.append({
                    'expectation_type': 'expect_column_values_to_be_between',
                    'kwargs': {
                        'column': col,
                        'min_value': 0,
                        'max_value': 150
                    }
                })
            
            # Percentage validation
            elif ('percent' in col_lower or 'rate' in col_lower or 'ratio' in col_lower) and pd.api.types.is_numeric_dtype(data[col]):
                expectations.append({
                    'expectation_type': 'expect_column_values_to_be_between',
                    'kwargs': {
                        'column': col,
                        'min_value': 0,
                        'max_value': 100
                    }
                })
            
            # Currency/Amount validation (non-negative)
            elif any(term in col_lower for term in ['amount', 'price', 'cost', 'salary', 'revenue']) and pd.api.types.is_numeric_dtype(data[col]):
                current_max = float(clean_data.max()) if len(clean_data) > 0 else 1000000
                expectations.append({
                    'expectation_type': 'expect_column_values_to_be_between',
                    'kwargs': {
                        'column': col,
                        'min_value': 0,
                        'max_value': current_max * 1.5  # Allow 50% increase
                    }
                })
            
            # Phone number validation
            elif 'phone' in col_lower and pd.api.types.is_object_dtype(data[col]):
                # Simple phone validation - allows various formats
                expectations.append({
                    'expectation_type': 'expect_column_values_to_match_regex',
                    'kwargs': {
                        'column': col,
                        'regex': r'^[\+\d\s\-\(\)\.]{10,15}$'
                    }
                })
        
        # Duplicate detection
        if len(data) > 0:
            duplicate_count = data.duplicated().sum()
            if duplicate_count == 0:  # Only add if currently no duplicates
                expectations.append({
                    'expectation_type': 'expect_table_row_count_to_equal',
                    'kwargs': {
                        'value': len(data)
                    }
                })
        
        return expectations
    
    def _is_email_column(self, series: pd.Series) -> bool:
        """Check if a series contains email addresses"""
        if len(series) == 0:
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        sample_size = min(50, len(series))
        sample = series.head(sample_size)
        
        email_matches = sum(1 for val in sample if isinstance(val, str) and re.match(email_pattern, val))
        return email_matches / len(sample) > 0.7