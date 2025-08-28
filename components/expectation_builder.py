import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ge_helpers import GEHelpers
from config.app_config import AppConfig

class ExpectationBuilderComponent:
    """Component for building and managing expectations"""
    
    def __init__(self):
        self.ge_helpers = GEHelpers()
        self.config = AppConfig()
        
        # Initialize session state for expectations
        if 'expectation_configs' not in st.session_state:
            st.session_state.expectation_configs = []
        if 'current_suite_name' not in st.session_state:
            st.session_state.current_suite_name = "default_suite"
        
        # Auto-load default suite if no expectations are configured
        if (len(st.session_state.expectation_configs) == 0 and 
            'default_suite_loaded' not in st.session_state):
            self._load_default_suite()
    
    def render(self, data: pd.DataFrame):
        """Render the expectation builder interface"""
        st.markdown("### ⚙️ Configure Your Data Expectations")
        
        # Suite management
        self._render_suite_management()
        
        # Template selection
        self._render_template_selection(data)
        
        # Expectation builder
        self._render_expectation_builder(data)
        
        # Current expectations display
        self._render_current_expectations()
        
        # Navigation buttons
        self._render_navigation_buttons()
    
    def _render_suite_management(self):
        """Render suite management interface"""
        st.markdown("#### 📋 Expectation Suite")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            suite_name = st.text_input(
                "Suite Name:",
                value=st.session_state.current_suite_name,
                help="Enter a name for your expectation suite"
            )
            st.session_state.current_suite_name = suite_name
        
        with col2:
            if st.button("Clear All", type="secondary"):
                st.session_state.expectation_configs = []
                st.success("All expectations cleared!")
    
    def _render_template_selection(self, data: pd.DataFrame):
        """Render template selection interface"""
        st.markdown("#### 📑 Quick Start Templates")
        
        template_options = ["None"] + list(self.config.EXPECTATION_TEMPLATES.keys())
        selected_template = st.selectbox(
            "Choose a template to get started:",
            options=template_options,
            help="Templates provide pre-configured expectations for common scenarios"
        )
        
        if selected_template != "None":
            template_config = self.config.EXPECTATION_TEMPLATES[selected_template]
            st.info(f"**{selected_template}**: {template_config['description']}")
            
            if st.button(f"Apply {selected_template} Template"):
                self._apply_template(selected_template, data)
    
    def _apply_template(self, template_name: str, data: pd.DataFrame):
        """Apply a template to the current suite"""
        template_config = self.config.EXPECTATION_TEMPLATES[template_name]
        
        for expectation_type in template_config['expectations']:
            if expectation_type == "expect_table_row_count_to_be_between":
                config = {
                    'expectation_type': expectation_type,
                    'kwargs': {
                        'min_value': max(1, int(len(data) * 0.9)),
                        'max_value': int(len(data) * 1.1)
                    }
                }
                st.session_state.expectation_configs.append(config)
            
            elif expectation_type == "expect_table_columns_to_match_ordered_list":
                config = {
                    'expectation_type': expectation_type,
                    'kwargs': {
                        'column_list': list(data.columns)
                    }
                }
                st.session_state.expectation_configs.append(config)
            
            elif expectation_type == "expect_column_values_to_not_be_null":
                # Add for all columns with < 10% null values
                for col in data.columns:
                    null_pct = (data[col].isnull().sum() / len(data)) * 100
                    if null_pct < 10:  # Only for columns with low null percentage
                        config = {
                            'expectation_type': expectation_type,
                            'kwargs': {'column': col}
                        }
                        st.session_state.expectation_configs.append(config)
        
        st.success(f"Applied {template_name} template with {len(template_config['expectations'])} expectation types!")
    
    def _render_expectation_builder(self, data: pd.DataFrame):
        """Render the main expectation builder"""
        st.markdown("#### 🛠️ Build Custom Expectations")
        
        # Expectation type selection
        available_expectations = self.ge_helpers.get_available_expectations()
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            expectation_type = st.selectbox(
                "Expectation Type:",
                options=available_expectations,
                format_func=lambda x: x.replace('expect_', '').replace('_', ' ').title(),
                help="Choose the type of expectation to create"
            )
        
        with col2:
            description = self.ge_helpers.get_expectation_description(expectation_type)
            st.info(description)
        
        # Dynamic parameter builder based on expectation type
        expectation_config = self._build_expectation_config(expectation_type, data)
        
        # Add expectation button
        if st.button("Add Expectation", type="primary"):
            if expectation_config:
                st.session_state.expectation_configs.append(expectation_config)
                st.success("Expectation added successfully!")
            else:
                st.error("Please configure all required parameters!")
    
    def _build_expectation_config(self, expectation_type: str, data: pd.DataFrame) -> Optional[Dict]:
        """Build expectation configuration based on type"""
        config = {'expectation_type': expectation_type, 'kwargs': {}}
        
        if expectation_type == "expect_table_row_count_to_be_between":
            col1, col2 = st.columns(2)
            with col1:
                min_value = st.number_input("Minimum rows:", min_value=0, value=len(data))
            with col2:
                max_value = st.number_input("Maximum rows:", min_value=min_value, value=len(data))
            
            config['kwargs'] = {'min_value': min_value, 'max_value': max_value}
        
        elif expectation_type == "expect_table_columns_to_match_ordered_list":
            expected_columns = st.multiselect(
                "Expected columns (in order):",
                options=list(data.columns),
                default=list(data.columns)
            )
            config['kwargs'] = {'column_list': expected_columns}
        
        elif "column" in expectation_type:
            # Column-based expectations
            column = st.selectbox("Select Column:", options=list(data.columns))
            config['kwargs']['column'] = column
            
            if column:
                self._add_column_specific_params(expectation_type, config, data, column)
        
        return config if config['kwargs'] else None
    
    def _add_column_specific_params(self, expectation_type: str, config: Dict, 
                                   data: pd.DataFrame, column: str):
        """Add column-specific parameters to expectation config"""
        
        if expectation_type == "expect_column_values_to_not_be_null":
            # No additional parameters needed
            pass
        
        elif expectation_type == "expect_column_values_to_be_unique":
            # No additional parameters needed
            pass
        
        elif expectation_type == "expect_column_values_to_be_of_type":
            type_options = ["int", "float", "str", "bool", "datetime"]
            expected_type = st.selectbox("Expected Type:", options=type_options)
            config['kwargs']['type_'] = expected_type
        
        elif expectation_type == "expect_column_values_to_be_in_set":
            if pd.api.types.is_object_dtype(data[column]):
                unique_values = data[column].dropna().unique()
                if len(unique_values) <= 50:  # Only show for reasonable number of values
                    value_set = st.multiselect(
                        "Allowed values:",
                        options=list(unique_values),
                        default=list(unique_values)[:10]
                    )
                    config['kwargs']['value_set'] = value_set
                else:
                    manual_values = st.text_area(
                        "Enter allowed values (one per line):",
                        help="Enter each allowed value on a separate line"
                    )
                    if manual_values:
                        value_set = [v.strip() for v in manual_values.split('\n') if v.strip()]
                        config['kwargs']['value_set'] = value_set
        
        elif expectation_type == "expect_column_values_to_be_between":
            if pd.api.types.is_numeric_dtype(data[column]):
                col_min = float(data[column].min())
                col_max = float(data[column].max())
                
                col1, col2 = st.columns(2)
                with col1:
                    min_value = st.number_input(
                        "Minimum value:",
                        value=col_min,
                        help=f"Current column min: {col_min}"
                    )
                with col2:
                    max_value = st.number_input(
                        "Maximum value:",
                        value=col_max,
                        help=f"Current column max: {col_max}"
                    )
                
                config['kwargs'].update({
                    'min_value': min_value,
                    'max_value': max_value
                })
        
        elif expectation_type == "expect_column_value_lengths_to_be_between":
            if pd.api.types.is_object_dtype(data[column]):
                current_lengths = data[column].astype(str).str.len()
                current_min = int(current_lengths.min())
                current_max = int(current_lengths.max())
                
                col1, col2 = st.columns(2)
                with col1:
                    min_length = st.number_input(
                        "Minimum length:",
                        min_value=0,
                        value=current_min,
                        help=f"Current min length: {current_min}"
                    )
                with col2:
                    max_length = st.number_input(
                        "Maximum length:",
                        min_value=min_length,
                        value=current_max,
                        help=f"Current max length: {current_max}"
                    )
                
                config['kwargs'].update({
                    'min_value': min_length,
                    'max_value': max_length
                })
        
        elif expectation_type == "expect_column_values_to_match_regex":
            regex_pattern = st.text_input(
                "Regex Pattern:",
                help="Enter a regular expression pattern to match"
            )
            if regex_pattern:
                config['kwargs']['regex'] = regex_pattern
        
        elif expectation_type in ["expect_column_mean_to_be_between", 
                                 "expect_column_median_to_be_between", 
                                 "expect_column_stdev_to_be_between"]:
            if pd.api.types.is_numeric_dtype(data[column]):
                if expectation_type == "expect_column_mean_to_be_between":
                    current_value = float(data[column].mean())
                    metric_name = "mean"
                elif expectation_type == "expect_column_median_to_be_between":
                    current_value = float(data[column].median())
                    metric_name = "median"
                else:  # stdev
                    current_value = float(data[column].std())
                    metric_name = "standard deviation"
                
                col1, col2 = st.columns(2)
                with col1:
                    min_value = st.number_input(
                        f"Minimum {metric_name}:",
                        value=current_value * 0.9,
                        help=f"Current {metric_name}: {current_value:.2f}"
                    )
                with col2:
                    max_value = st.number_input(
                        f"Maximum {metric_name}:",
                        value=current_value * 1.1,
                        help=f"Current {metric_name}: {current_value:.2f}"
                    )
                
                config['kwargs'].update({
                    'min_value': min_value,
                    'max_value': max_value
                })
    
    def _render_current_expectations(self):
        """Render current expectations list"""
        st.markdown("#### 📋 Current Expectations")
        
        if not st.session_state.expectation_configs:
            st.info("No expectations configured yet. Add some expectations above!")
            return
        
        # Display expectations in a table format
        expectations_data = []
        for i, config in enumerate(st.session_state.expectation_configs):
            expectations_data.append({
                'ID': i + 1,
                'Type': config['expectation_type'].replace('expect_', '').replace('_', ' ').title(),
                'Column': config['kwargs'].get('column', 'N/A'),
                'Parameters': str(config['kwargs'])
            })
        
        expectations_df = pd.DataFrame(expectations_data)
        
        # Allow selection of expectations to remove
        with st.expander("📋 Manage Expectations", expanded=True):
            selected_expectations = st.multiselect(
                "Select expectations to remove:",
                options=range(len(st.session_state.expectation_configs)),
                format_func=lambda x: f"#{x+1}: {expectations_data[x]['Type']} - {expectations_data[x]['Column']}"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Remove Selected", type="secondary"):
                    # Remove in reverse order to maintain indices
                    for idx in sorted(selected_expectations, reverse=True):
                        st.session_state.expectation_configs.pop(idx)
                    st.success("Selected expectations removed!")
                    st.rerun()
            
            with col2:
                total_count = len(st.session_state.expectation_configs)
                st.metric("Total Expectations", total_count)
        
        # Display the table
        st.dataframe(expectations_df, use_container_width=True, hide_index=True)
    
    def _render_navigation_buttons(self):
        """Render navigation buttons"""
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("← Back to Profiling", type="secondary"):
                st.session_state.current_step = 'profile'
                st.rerun()
        
        with col2:
            # Export/Import expectations
            self._render_import_export()
        
        with col3:
            if len(st.session_state.expectation_configs) > 0:
                if st.button("Configure Suite →", type="primary"):
                    # Debug: Check what expectations are configured
                    st.write(f"🔍 Debug: Found {len(st.session_state.expectation_configs)} configured expectations")
                    st.write(f"🔍 Debug: Session state keys: {list(st.session_state.keys())}")
                    st.write(f"🔍 Debug: expectation_configs type: {type(st.session_state.expectation_configs)}")
                    
                    if st.session_state.expectation_configs:
                        for i, config in enumerate(st.session_state.expectation_configs):
                            st.write(f"  {i+1}. {config.get('expectation_type', 'Unknown')} - {config}")
                    else:
                        st.write("⚠️ No expectations found in session state!")
                        st.write("🔍 Debug: Checking if default suite was loaded...")
                        if hasattr(st.session_state, 'default_suite_loaded'):
                            st.write(f"Default suite loaded: {st.session_state.default_suite_loaded}")
                        else:
                            st.write("Default suite not loaded")
                    
                    # Create the expectation suite and store it
                    suite = self.ge_helpers.create_expectation_suite(
                        st.session_state.current_suite_name
                    )
                    
                    if suite:
                        # Add all configured expectations to the suite
                        st.write(f"🔍 Debug: Adding {len(st.session_state.expectation_configs)} expectations to suite...")
                        success_count = 0
                        for i, config in enumerate(st.session_state.expectation_configs):
                            if self.ge_helpers.add_expectation_to_suite(suite, config):
                                success_count += 1
                            else:
                                st.error(f"Failed to add expectation {i+1}")
                        
                        st.write(f"🔍 Debug: Successfully added {success_count}/{len(st.session_state.expectation_configs)} expectations")
                        st.write(f"🔍 Debug: Final suite has {len(suite.expectations)} expectations")
                        
                        # Persist suite and configs in session
                        st.session_state.expectation_suite = suite
                        try:
                            st.session_state.expectation_suite_json = self.ge_helpers.export_suite_to_json(suite)
                        except Exception:
                            st.session_state.expectation_suite_json = None
                        st.session_state.current_step = 'validate'
                        st.success("Expectation suite created! Ready for validation.")
                        st.rerun()
                    else:
                        st.error("Failed to create expectation suite!")
            else:
                st.warning("Add some expectations before proceeding!")
    
    def _render_import_export(self):
        """Render import/export functionality"""
        with st.popover("💾 Import/Export"):
            # Export
            st.markdown("**Export Expectations**")
            if st.session_state.expectation_configs:
                import json
                export_data = {
                    'suite_name': st.session_state.current_suite_name,
                    'expectations': st.session_state.expectation_configs
                }
                export_json = json.dumps(export_data, indent=2)
                
                st.download_button(
                    "Download JSON",
                    data=export_json,
                    file_name=f"{st.session_state.current_suite_name}.json",
                    mime="application/json"
                )
            else:
                st.info("No expectations to export")
            
            st.markdown("**Import Expectations**")
            uploaded_json = st.file_uploader(
                "Upload expectation suite:",
                type=['json'],
                help="Upload a previously exported expectation suite"
            )
            
            if uploaded_json is not None:
                try:
                    import json
                    import_data = json.loads(uploaded_json.read())
                    
                    st.session_state.current_suite_name = import_data.get(
                        'suite_name', 'imported_suite'
                    )
                    st.session_state.expectation_configs = import_data.get(
                        'expectations', []
                    )
                    
                    st.success("Expectations imported successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error importing expectations: {str(e)}")
    
    def _load_default_suite(self):
        """Load default expectation suite from file"""
        try:
            import json
            import os
            
            # Get the path to default_suite.json
            current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            default_suite_path = os.path.join(current_dir, 'default_suite.json')
            
            if os.path.exists(default_suite_path):
                with open(default_suite_path, 'r') as f:
                    import_data = json.load(f)
                
                st.session_state.current_suite_name = import_data.get('suite_name', 'default_suite')
                st.session_state.expectation_configs = import_data.get('expectations', [])
                st.session_state.default_suite_loaded = True
                
                st.success(f"✅ Loaded default suite with {len(st.session_state.expectation_configs)} expectations!")
            else:
                st.warning("Default suite file not found")
                st.session_state.default_suite_loaded = True  # Don't try again
                
        except Exception as e:
            st.error(f"Error loading default suite: {str(e)}")
            st.session_state.default_suite_loaded = True  # Don't try again