import great_expectations as gx
from great_expectations.core import ExpectationSuite

# Try new import path for GE 0.18+, fallback to old path for earlier versions
try:
    from great_expectations.expectations.expectation_configuration import ExpectationConfiguration
except ImportError:
    try:
        from great_expectations.core.expectation_configuration import ExpectationConfiguration
    except ImportError:
        # For very old versions
        from great_expectations.core import ExpectationConfiguration

import pandas as pd
import json
import tempfile
import os
from typing import Dict, List, Any, Optional
import streamlit as st
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.custom_sql_expectations import CustomSQLExpectation

class GEHelpers:
    """Helper class for Great Expectations operations"""
    
    def __init__(self):
        self.context = None
        self.data_source = None
        self.custom_sql_expectation = CustomSQLExpectation()
        
    def initialize_context(self):
        """Initialize Great Expectations context"""
        try:
            # Create a temporary directory for GE context
            temp_dir = tempfile.mkdtemp()
            self.context = gx.get_context(context_root_dir=temp_dir)
            return True
        except Exception as e:
            st.error(f"Error initializing Great Expectations context: {str(e)}")
            return False
    
    def create_expectation_suite(self, suite_name: str) -> ExpectationSuite:
        """Create a new expectation suite"""
        try:
            if self.context is None:
                if not self.initialize_context():
                    return None
            
            # Create expectation suite directly - handle different GE versions
            try:
                # Try the new GE 0.18+ style first
                suite = ExpectationSuite()
                suite.name = suite_name
            except TypeError:
                # Fallback to older style if needed
                suite = ExpectationSuite(expectation_suite_name=suite_name)
            
            # Add the suite to context if it has suites attribute
            if hasattr(self.context, 'suites'):
                self.context.suites.add(suite)
            
            st.write(f"Debug: Created suite '{suite_name}' with {len(suite.expectations)} expectations")
            return suite
        except Exception as e:
            st.error(f"Error creating expectation suite: {str(e)}")
            return None
    
    def add_expectation_to_suite(self, suite: ExpectationSuite, expectation_config: Dict) -> bool:
        """Add an expectation to a suite, robust across GE versions."""
        try:
            # Validate incoming config
            expectation_type: Optional[str] = expectation_config.get('expectation_type') if isinstance(expectation_config, dict) else None
            if not expectation_type:
                st.error("Expectation config missing 'expectation_type'")
                return False

            kwargs: Dict[str, Any] = expectation_config.get('kwargs', {})

            # Try different approaches for GE 0.18+
            try:
                # Method 1: Try using the new GE 0.18+ API
                exp_config_obj = ExpectationConfiguration(
                    expectation_type=expectation_type,
                    kwargs=kwargs,
                )
                suite.add_expectation_configuration(exp_config_obj)
                st.write(f"Added expectation '{expectation_type}' using add_expectation_configuration")
                return True
            except Exception as e1:
                st.write(f"Debug: Method 1 failed: {str(e1)}")
                
                try:
                    # Method 2: Try using the new GE 0.18+ API with different parameter names
                    exp_config_obj = ExpectationConfiguration(
                        expectation_type=expectation_type,
                        kwargs=kwargs,
                    )
                    # Try to add directly to expectations list
                    if not hasattr(suite, 'expectations'):
                        suite.expectations = []
                    suite.expectations.append(exp_config_obj)
                    st.write(f"Added expectation '{expectation_type}' directly to expectations list")
                    return True
                except Exception as e2:
                    st.write(f"Debug: Method 2 failed: {str(e2)}")
                    
                    try:
                        # Method 3: Try using the new GE 0.18+ API with different constructor
                        exp_config_obj = ExpectationConfiguration(
                            expectation_type=expectation_type,
                            kwargs=kwargs,
                        )
                        # Try to use the new add_expectation method if it exists
                        if hasattr(suite, 'add_expectation'):
                            suite.add_expectation(exp_config_obj)
                            st.write(f"Added expectation '{expectation_type}' using add_expectation")
                            return True
                        else:
                            # Last resort: add to expectations list
                            if not hasattr(suite, 'expectations'):
                                suite.expectations = []
                            suite.expectations.append(exp_config_obj)
                            st.write(f"Added expectation '{expectation_type}' to expectations list (fallback)")
                            return True
                    except Exception as e3:
                        st.error("Failed to add expectation using any Great Expectations API method")
                        st.write("Debug: All methods failed:")
                        st.write(f"  Method 1 (add_expectation_configuration) -> {str(e1)}")
                        st.write(f"  Method 2 (direct list append) -> {str(e2)}")
                        st.write(f"  Method 3 (add_expectation/fallback) -> {str(e3)}")
                        st.write(f"Debug: Config attempted: {{'expectation_type': '{expectation_type}', 'kwargs': {kwargs}}}")
                        return False

        except Exception as e:
            st.error(f"Error adding expectation to suite: {str(e)}")
            st.write(f"Debug: Failed expectation config: {expectation_config}")
            return False
    
    def validate_data(self, data: pd.DataFrame, suite: ExpectationSuite) -> Dict:
        """Validate data against expectation suite using GE 0.18+ API"""
        try:
            if self.context is None:
                if not self.initialize_context():
                    return None
            
            # Normalize suite to ensure it contains GXExpectation objects, not raw dicts
            suite = self._normalize_suite(suite)
            
            # Debug: Check the suite before validation
            st.write(f"Debug: Validating suite '{suite.name}' with {len(suite.expectations)} expectations")
            st.write(f"Debug: Data shape: {data.shape}")
            
            # Use the new GE 0.18+ validation approach
            try:
                # Method 1: Try using the new GE 0.18+ validation API
                validation_result = self.context.run_validation_operator(
                    "action_list_operator",
                    assets_to_validate=[data],
                    expectation_suite=suite
                )
                st.write(f"Validation completed using new GE 0.18+ API")
                return validation_result.to_json_dict()
            except Exception as e1:
                st.write(f"Debug: New API failed: {str(e1)}")
                
                try:
                    # Method 2: Try using the legacy validation approach
                    from great_expectations.execution_engine.pandas_execution_engine import PandasExecutionEngine
                    from great_expectations.data_context.util import instantiate_class_from_config
                    
                    # Create a simple validation using the execution engine
                    execution_engine = PandasExecutionEngine()
                    batch_data = execution_engine.get_batch_data(data)
                    
                    # Validate using the suite directly
                    validation_result = suite.validate(batch_data)
                    st.write(f"Validation completed using execution engine approach")
                    return validation_result.to_json_dict()
                except Exception as e2:
                    st.write(f"Debug: Execution engine approach failed: {str(e2)}")
                    
                    try:
                        # Method 3: Try using the most basic validation approach
                        # Create a simple validation result manually
                        validation_result = {
                            "success": True,
                            "results": [],
                            "statistics": {
                                "evaluated_expectations": len(suite.expectations),
                                "successful_expectations": 0,
                                "unsuccessful_expectations": 0,
                                "success_percent": 0.0
                            }
                        }
                        
                        # Process each expectation manually
                        st.write(f"Debug: Processing {len(suite.expectations)} expectations manually")
                        for i, expectation in enumerate(suite.expectations):
                            try:
                                # Extract expectation information properly
                                exp_type = getattr(expectation, 'expectation_type', None)
                                exp_kwargs = getattr(expectation, 'kwargs', {})
                                
                                st.write(f"Debug: Expectation {i+1}: type={exp_type}, kwargs={exp_kwargs}")
                                
                                # Create expectation_config structure for proper display
                                exp_config = {
                                    'type': exp_type,
                                    'expectation_type': exp_type,
                                    'kwargs': exp_kwargs
                                }
                                
                                if exp_type == 'expect_column_values_to_not_be_null':
                                    column = exp_kwargs.get('column')
                                    if column in data.columns:
                                        null_count = data[column].isnull().sum()
                                        success = null_count == 0
                                        validation_result["results"].append({
                                            "success": success,
                                            "expectation_config": exp_config,
                                            "result": {
                                                "element_count": len(data),
                                                "unexpected_count": null_count,
                                                "unexpected_percent": (null_count / len(data) * 100) if len(data) > 0 else 0
                                            }
                                        })
                                        if success:
                                            validation_result["statistics"]["successful_expectations"] += 1
                                        else:
                                            validation_result["statistics"]["unsuccessful_expectations"] += 1
                                
                                elif exp_type == 'expect_column_values_to_be_unique':
                                    column = exp_kwargs.get('column')
                                    if column in data.columns:
                                        unique_count = data[column].nunique()
                                        total_count = len(data[column])
                                        success = unique_count == total_count
                                        unexpected_count = total_count - unique_count
                                        validation_result["results"].append({
                                            "success": success,
                                            "expectation_config": exp_config,
                                            "result": {
                                                "element_count": total_count,
                                                "unexpected_count": unexpected_count,
                                                "unexpected_percent": (unexpected_count / total_count * 100) if total_count > 0 else 0
                                            }
                                        })
                                        if success:
                                            validation_result["statistics"]["successful_expectations"] += 1
                                        else:
                                            validation_result["statistics"]["unsuccessful_expectations"] += 1
                                
                                elif exp_type == 'expect_column_values_to_be_between':
                                    column = exp_kwargs.get('column')
                                    min_value = exp_kwargs.get('min_value')
                                    max_value = exp_kwargs.get('max_value')
                                    if column in data.columns:
                                        if min_value is not None and max_value is not None:
                                            out_of_range = data[(data[column] < min_value) | (data[column] > max_value)]
                                            unexpected_count = len(out_of_range)
                                            success = unexpected_count == 0
                                            validation_result["results"].append({
                                                "success": success,
                                                "expectation_config": exp_config,
                                                "result": {
                                                    "element_count": len(data),
                                                    "unexpected_count": unexpected_count,
                                                    "unexpected_percent": (unexpected_count / len(data) * 100) if len(data) > 0 else 0
                                                }
                                            })
                                            if success:
                                                validation_result["statistics"]["successful_expectations"] += 1
                                            else:
                                                validation_result["statistics"]["unsuccessful_expectations"] += 1
                                
                                elif exp_type == 'expect_column_values_to_be_in_set':
                                    column = exp_kwargs.get('column')
                                    value_set = exp_kwargs.get('value_set', [])
                                    if column in data.columns and value_set:
                                        out_of_set = data[~data[column].isin(value_set)]
                                        unexpected_count = len(out_of_set)
                                        success = unexpected_count == 0
                                        validation_result["results"].append({
                                            "success": success,
                                            "expectation_config": exp_config,
                                            "result": {
                                                "element_count": len(data),
                                                "unexpected_count": unexpected_count,
                                                "unexpected_percent": (unexpected_count / len(data) * 100) if len(data) > 0 else 0
                                            }
                                        })
                                        if success:
                                            validation_result["statistics"]["successful_expectations"] += 1
                                        else:
                                            validation_result["statistics"]["unsuccessful_expectations"] += 1
                                
                                elif exp_type == 'expect_table_row_count_to_be_between':
                                    min_value = exp_kwargs.get('min_value')
                                    max_value = exp_kwargs.get('max_value')
                                    actual_count = len(data)
                                    
                                    # Check if the actual count is within the expected range
                                    success = (min_value is None or actual_count >= min_value) and (max_value is None or actual_count <= max_value)
                                    
                                    # For table-level expectations, there are no "unexpected" records
                                    # The entire table either passes or fails the expectation
                                    unexpected_count = 0 if success else 1
                                    
                                    validation_result["results"].append({
                                        "success": success,
                                        "expectation_config": exp_config,
                                        "result": {
                                            "element_count": actual_count,
                                            "unexpected_count": unexpected_count,
                                            "unexpected_percent": 0.0 if success else 100.0
                                        }
                                    })
                                    if success:
                                        validation_result["statistics"]["successful_expectations"] += 1
                                    else:
                                        validation_result["statistics"]["unsuccessful_expectations"] += 1
                                
                                elif exp_type == 'expect_table_columns_to_match_ordered_list':
                                    expected_columns = exp_kwargs.get('column_list', [])
                                    actual_columns = list(data.columns)
                                    
                                    # Check if the actual columns match the expected list exactly
                                    success = actual_columns == expected_columns
                                    
                                    # For table-level expectations, there are no "unexpected" records
                                    unexpected_count = 0 if success else 1
                                    
                                    validation_result["results"].append({
                                        "success": success,
                                        "expectation_config": exp_config,
                                        "result": {
                                            "element_count": len(actual_columns),
                                            "unexpected_count": unexpected_count,
                                            "unexpected_percent": 0.0 if success else 100.0
                                        }
                                    })
                                    if success:
                                        validation_result["statistics"]["successful_expectations"] += 1
                                    else:
                                        validation_result["statistics"]["unsuccessful_expectations"] += 1
                                
                                elif exp_type == 'expect_column_values_to_match_regex':
                                    column = exp_kwargs.get('column')
                                    regex_pattern = exp_kwargs.get('regex')
                                    if column in data.columns and regex_pattern:
                                        import re
                                        try:
                                            pattern = re.compile(regex_pattern)
                                            # Check which values don't match the regex
                                            non_matching = data[~data[column].astype(str).str.match(pattern, na=False)]
                                            unexpected_count = len(non_matching)
                                            success = unexpected_count == 0
                                            
                                            validation_result["results"].append({
                                                "success": success,
                                                "expectation_config": exp_config,
                                                "result": {
                                                    "element_count": len(data),
                                                    "unexpected_count": unexpected_count,
                                                    "unexpected_percent": (unexpected_count / len(data) * 100) if len(data) > 0 else 0
                                                }
                                            })
                                            if success:
                                                validation_result["statistics"]["successful_expectations"] += 1
                                            else:
                                                validation_result["statistics"]["unsuccessful_expectations"] += 1
                                        except Exception as regex_e:
                                            # If regex compilation fails, mark as failed
                                            validation_result["results"].append({
                                                "success": False,
                                                "expectation_config": exp_config,
                                                "exception_info": {"exception_message": f"Invalid regex pattern: {str(regex_e)}"}
                                            })
                                            validation_result["statistics"]["unsuccessful_expectations"] += 1
                                
                                elif exp_type == 'expect_column_value_lengths_to_be_between':
                                    column = exp_kwargs.get('column')
                                    min_value = exp_kwargs.get('min_value')
                                    max_value = exp_kwargs.get('max_value')
                                    if column in data.columns:
                                        # Convert to string and get lengths
                                        string_lengths = data[column].astype(str).str.len()
                                        out_of_range = string_lengths[(string_lengths < min_value) | (string_lengths > max_value)]
                                        unexpected_count = len(out_of_range)
                                        success = unexpected_count == 0
                                        
                                        validation_result["results"].append({
                                            "success": success,
                                            "expectation_config": exp_config,
                                            "result": {
                                                "element_count": len(data),
                                                "unexpected_count": unexpected_count,
                                                "unexpected_percent": (unexpected_count / len(data) * 100) if len(data) > 0 else 0
                                            }
                                        })
                                        if success:
                                            validation_result["statistics"]["successful_expectations"] += 1
                                        else:
                                            validation_result["statistics"]["unsuccessful_expectations"] += 1
                                
                                elif exp_type == 'expect_custom_sql_query_to_return_expected_result':
                                    # Handle custom SQL expectations
                                    try:
                                        custom_result = self.custom_sql_expectation.validate_expectation(data, exp_config)
                                        validation_result["results"].append(custom_result)
                                        
                                        if custom_result.get("success", False):
                                            validation_result["statistics"]["successful_expectations"] += 1
                                        else:
                                            validation_result["statistics"]["unsuccessful_expectations"] += 1
                                    except Exception as custom_e:
                                        st.write(f"Debug: Custom SQL expectation failed: {str(custom_e)}")
                                        validation_result["results"].append({
                                            "success": False,
                                            "expectation_config": exp_config,
                                            "exception_info": {"exception_message": f"Custom SQL validation failed: {str(custom_e)}"},
                                            "result": {
                                                "element_count": len(data),
                                                "unexpected_count": len(data),
                                                "unexpected_percent": 100.0
                                            }
                                        })
                                        validation_result["statistics"]["unsuccessful_expectations"] += 1
                                
                                else:
                                    # Generic handling for other expectation types
                                    validation_result["results"].append({
                                        "success": False,
                                        "expectation_config": exp_config,
                                        "exception_info": {"exception_message": f"Expectation type '{exp_type}' not yet implemented in manual validation"},
                                        "result": {
                                            "element_count": len(data),
                                            "unexpected_count": 0,
                                            "unexpected_percent": 0.0
                                        }
                                    })
                                    validation_result["statistics"]["unsuccessful_expectations"] += 1
                                
                            except Exception as exp_e:
                                st.write(f"Debug: Failed to process expectation {exp_type}: {str(exp_e)}")
                                # Create proper structure even for failed expectations
                                exp_config = {
                                    'type': exp_type,
                                    'expectation_type': exp_type,
                                    'kwargs': exp_kwargs
                                }
                                validation_result["results"].append({
                                    "success": False,
                                    "expectation_config": exp_config,
                                    "exception_info": {"exception_message": str(exp_e)}
                                })
                                validation_result["statistics"]["unsuccessful_expectations"] += 1
                        
                        # Calculate success percentage
                        total_expectations = validation_result["statistics"]["evaluated_expectations"]
                        if total_expectations > 0:
                            validation_result["statistics"]["success_percent"] = (
                                validation_result["statistics"]["successful_expectations"] / total_expectations * 100
                            )
                        
                        st.write(f"Validation completed using manual approach")
                        st.write(f"Debug: Final validation result structure:")
                        st.write(f"  - Results count: {len(validation_result['results'])}")
                        for i, result in enumerate(validation_result['results']):
                            exp_config = result.get('expectation_config', {})
                            exp_type = exp_config.get('type', exp_config.get('expectation_type', 'Unknown'))
                            column = exp_config.get('kwargs', {}).get('column', 'N/A')
                            st.write(f"    Result {i+1}: type={exp_type}, column={column}")
                        return validation_result
                        
                    except Exception as e3:
                        st.error("All validation methods failed")
                        st.write(f"Debug: All validation methods failed:")
                        st.write(f"  New API -> {str(e1)}")
                        st.write(f"  Execution Engine -> {str(e2)}")
                        st.write(f"  Manual -> {str(e3)}")
                        return None
            
        except Exception as e:
            st.error(f"Error validating data: {str(e)}")
            st.exception(e)
            return None

    def _normalize_suite(self, suite: ExpectationSuite) -> ExpectationSuite:
        """Ensure the suite contains valid GXExpectation objects.
        If any raw dicts are present, rebuild a new suite using the proper API.
        """
        try:
            # If everything looks good (no dicts), return as-is
            if hasattr(suite, 'expectations') and all(not isinstance(exp, dict) for exp in (suite.expectations or [])):
                return suite

            # Rebuild a new suite with the same name - handle different GE versions
            suite_name = getattr(suite, 'name', 'rebuilt_suite')
            try:
                # Try the new GE 0.18+ style first
                rebuilt_suite = ExpectationSuite()
                rebuilt_suite.name = suite_name
            except TypeError:
                # Fallback to older style if needed
                rebuilt_suite = ExpectationSuite(expectation_suite_name=suite_name)
            # Attempt to register with context if available
            try:
                if self.context is not None and hasattr(self.context, 'suites'):
                    self.context.suites.add(rebuilt_suite)
            except Exception:
                pass

            for exp in getattr(suite, 'expectations', []) or []:
                if isinstance(exp, dict):
                    cfg = exp
                else:
                    try:
                        cfg = exp.to_json_dict()
                    except Exception:
                        cfg = {
                            'expectation_type': getattr(exp, 'expectation_type', None),
                            'kwargs': getattr(exp, 'kwargs', {}) or {}
                        }
                if cfg and cfg.get('expectation_type'):
                    st.write(f"Debug: Adding expectation {cfg.get('expectation_type')} to normalized suite")
                    self.add_expectation_to_suite(rebuilt_suite, cfg)

            st.info("Normalized expectation suite to GE-native objects for validation")
            return rebuilt_suite
        except Exception:
            # On any failure, return original suite
            return suite
    
    def create_data_docs(self, validation_result: Dict) -> str:
        """Generate data docs HTML"""
        try:
            if self.context is None:
                return None
            
            # Build data docs
            self.context.build_data_docs()
            
            # Get the path to the built docs
            docs_sites = self.context.get_docs_sites_urls()
            if docs_sites:
                return docs_sites[0]['site_url']
            return None
        except Exception as e:
            st.error(f"Error creating data docs: {str(e)}")
            return None
    
    def export_suite_to_json(self, suite: ExpectationSuite) -> str:
        """Export expectation suite to JSON string"""
        try:
            return json.dumps(suite.to_json_dict(), indent=2)
        except Exception as e:
            st.error(f"Error exporting suite to JSON: {str(e)}")
            return None
    
    def import_suite_from_json(self, json_string: str) -> ExpectationSuite:
        """Import expectation suite from JSON string"""
        try:
            suite_dict = json.loads(json_string)
            suite_name = suite_dict.get('name', 'imported_suite')
            
            # Handle different GE versions
            try:
                # Try the new GE 0.18+ style first
                suite = ExpectationSuite()
                suite.name = suite_name
            except TypeError:
                # Fallback to older style if needed
                suite = ExpectationSuite(expectation_suite_name=suite_name)
            
            # Set other attributes manually
            if 'meta' in suite_dict:
                suite.meta = suite_dict['meta']
            if 'expectations' in suite_dict:
                suite.expectations = suite_dict['expectations']
            return suite
        except Exception as e:
            st.error(f"Error importing suite from JSON: {str(e)}")
            return None
    
    def get_available_expectations(self) -> List[str]:
        """Get list of available expectation types"""
        return [
            "expect_table_row_count_to_be_between",
            "expect_table_columns_to_match_ordered_list", 
            "expect_column_values_to_not_be_null",
            "expect_column_values_to_be_unique",
            "expect_column_values_to_be_of_type",
            "expect_column_values_to_be_in_set",
            "expect_column_values_to_be_between",
            "expect_column_value_lengths_to_be_between",
            "expect_column_values_to_match_regex",
            "expect_column_mean_to_be_between",
            "expect_column_median_to_be_between",
            "expect_column_stdev_to_be_between",
            "expect_column_sum_to_be_between",
            "expect_column_values_to_be_dateutil_parseable",
            "expect_column_values_to_match_strftime_format",
            "expect_custom_sql_query_to_return_expected_result"
        ]
    
    def get_expectation_description(self, expectation_type: str) -> str:
        """Get description for expectation type"""
        descriptions = {
            "expect_table_row_count_to_be_between": "Expect table to have row count within specified range",
            "expect_table_columns_to_match_ordered_list": "Expect table columns to match specified list",
            "expect_column_values_to_not_be_null": "Expect column values to not be null",
            "expect_column_values_to_be_unique": "Expect all column values to be unique",
            "expect_column_values_to_be_of_type": "Expect column values to be of specified data type",
            "expect_column_values_to_be_in_set": "Expect column values to be in specified set",
            "expect_column_values_to_be_between": "Expect column values to be within specified range",
            "expect_column_value_lengths_to_be_between": "Expect column value lengths to be within range",
            "expect_column_values_to_match_regex": "Expect column values to match regex pattern",
            "expect_column_mean_to_be_between": "Expect column mean to be within specified range",
            "expect_column_median_to_be_between": "Expect column median to be within specified range",
            "expect_column_stdev_to_be_between": "Expect column standard deviation to be within range",
            "expect_column_sum_to_be_between": "Expect column sum to be within specified range",
            "expect_column_values_to_be_dateutil_parseable": "Expect column values to be parseable as dates",
            "expect_column_values_to_match_strftime_format": "Expect column values to match date format",
            "expect_custom_sql_query_to_return_expected_result": "Custom SQL-based validation for complex business rules and multi-column checks"
        }
        return descriptions.get(expectation_type, "No description available")
    
    def get_column_types(self, data: pd.DataFrame) -> Dict[str, str]:
        """Get column names and their data types"""
        return {col: str(dtype) for col, dtype in data.dtypes.items()}
    
    def get_numeric_columns(self, data: pd.DataFrame) -> List[str]:
        """Get list of numeric columns"""
        return data.select_dtypes(include=['number']).columns.tolist()
    
    def get_text_columns(self, data: pd.DataFrame) -> List[str]:
        """Get list of text/object columns"""
        return data.select_dtypes(include=['object', 'string']).columns.tolist()
    
    def get_datetime_columns(self, data: pd.DataFrame) -> List[str]:
        """Get list of datetime columns"""
        return data.select_dtypes(include=['datetime']).columns.tolist()
    
    def sample_data(self, data: pd.DataFrame, sample_size: int = 1000) -> pd.DataFrame:
        """Sample data for faster processing"""
        if len(data) <= sample_size:
            return data
        return data.sample(n=sample_size, random_state=42)