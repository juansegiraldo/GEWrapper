import great_expectations as gx
from great_expectations.core import ExpectationSuite
from great_expectations.core.expectation_configuration import ExpectationConfiguration
import pandas as pd
import json
import tempfile
import os
from typing import Dict, List, Any, Optional
import streamlit as st

class GEHelpers:
    """Helper class for Great Expectations operations"""
    
    def __init__(self):
        self.context = None
        self.data_source = None
        
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
            
            # Create expectation suite directly
            suite = ExpectationSuite()
            suite.name = suite_name
            
            # Add the suite to context if it has suites attribute
            if hasattr(self.context, 'suites'):
                self.context.suites.add(suite)
            
            st.write(f"🔍 Debug: Created suite '{suite_name}' with {len(suite.expectations)} expectations")
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

            # Build an ExpectationConfiguration and add it via the public API (GE 1.5+)
            try:
                exp_config_obj = ExpectationConfiguration(
                    type=expectation_type,
                    kwargs=kwargs,
                )
                suite.add_expectation_configuration(exp_config_obj)
            except Exception as e1:
                # Fallback 1: build Expectation and add via add_expectation()
                try:
                    # Create a new ExpectationConfiguration for the fallback
                    fallback_config = ExpectationConfiguration(
                        type=expectation_type,
                        kwargs=kwargs,
                    )
                    built = suite._build_expectation(expectation_configuration=fallback_config)
                    suite.add_expectation(built)
                except Exception as e2:
                    # Fallback 2: let GE process the dict config
                    try:
                        processed = suite._process_expectation({'expectation_type': expectation_type, 'kwargs': kwargs})
                        suite.add_expectation(processed)
                    except Exception as e3:
                        st.error("Failed to add expectation using Great Expectations API")
                        st.write("🔍 Debug: add errors:")
                        st.write(f"  add_expectation_configuration -> {str(e1)}")
                        st.write(f"  add_expectation(built) -> {str(e2)}")
                        st.write(f"  add_expectation(processed) -> {str(e3)}")
                        st.write(f"🔍 Debug: Config attempted: {{'expectation_type': '{expectation_type}', 'kwargs': {kwargs}}}")
                        return False

            # Confirm addition
            current_count = len(suite.expectations) if hasattr(suite, 'expectations') and suite.expectations else 0
            st.write(f"🔍 Debug: Added '{expectation_type}'. Suite expectation count: {current_count}")
            return True
        except Exception as e:
            st.error(f"Error adding expectation to suite: {str(e)}")
            st.write(f"🔍 Debug: Failed expectation config: {expectation_config}")
            return False
    
    def validate_data(self, data: pd.DataFrame, suite: ExpectationSuite) -> Dict:
        """Validate data against expectation suite"""
        try:
            if self.context is None:
                if not self.initialize_context():
                    return None
            
            # Normalize suite to ensure it contains GXExpectation objects, not raw dicts
            suite = self._normalize_suite(suite)
            
            # Debug: Check the suite before validation
            st.write(f"🔍 Debug: Validating suite '{suite.name}' with {len(suite.expectations)} expectations")
            st.write(f"🔍 Debug: Data shape: {data.shape}")
            
            # Create data source and asset for validation
            try:
                data_source = self.context.data_sources.add_pandas(name="validation_data_source")
            except:
                # Data source might already exist, get it instead
                data_source = self.context.data_sources.get("validation_data_source")
            
            try:
                data_asset = data_source.add_dataframe_asset(name="validation_dataframe_asset")
            except:
                # Asset might already exist, get it instead  
                data_asset = data_source.get_asset("validation_dataframe_asset")
            
            try:
                batch_definition = data_asset.add_batch_definition_whole_dataframe("validation_batch")
            except:
                # Batch definition might already exist, get it instead
                batch_definition = data_asset.get_batch_definition("validation_batch")
            
            # Create batch parameters and validate
            batch_parameters = {"dataframe": data}
            batch = batch_definition.get_batch(batch_parameters=batch_parameters)
            
            # In GE 0.18+, batch.data is a PandasBatchData wrapper without __len__.
            # Use the known dataframe length instead of calling len() on the wrapper.
            st.write(f"🔍 Debug: Created batch for dataframe with {len(data)} rows")
            
            # Validate the batch against the suite
            validation_result = batch.validate(suite)
            
            st.write(f"🔍 Debug: Validation completed, result keys: {list(validation_result.to_json_dict().keys())}")
            
            return validation_result.to_json_dict()
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

            # Rebuild a new suite with the same name
            rebuilt_suite = ExpectationSuite()
            rebuilt_suite.name = getattr(suite, 'name', 'rebuilt_suite')
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
                    self.add_expectation_to_suite(rebuilt_suite, cfg)

            st.info("🔧 Normalized expectation suite to GE-native objects for validation")
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
            suite = ExpectationSuite()
            # Set attributes manually for GE 0.18+ compatibility
            if 'name' in suite_dict:
                suite.name = suite_dict['name']
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
            "expect_column_values_to_match_strftime_format"
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
            "expect_column_values_to_match_strftime_format": "Expect column values to match date format"
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