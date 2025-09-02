import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ge_helpers import GEHelpers
from utils.suite_helpers import generate_suite_name
from utils.smart_template_engine import SmartTemplateEngine
from config.app_config import AppConfig
from components.sql_query_builder import SQLQueryBuilderComponent

class ExpectationBuilderComponent:
    """Component for building and managing expectations"""
    
    def __init__(self):
        self.ge_helpers = GEHelpers()
        self.config = AppConfig()
        self.sql_query_builder = SQLQueryBuilderComponent()
        self.smart_engine = SmartTemplateEngine()
        
        # Initialize session state for expectations
        if 'expectation_configs' not in st.session_state:
            st.session_state.expectation_configs = []
        
        # (No SQL popup flag needed when using st.dialog)
        
        # Generate suite name only if not already set or if we have a new uploaded file
        if ('current_suite_name' not in st.session_state or 
            (st.session_state.get('uploaded_filename') and 
             st.session_state.get('current_suite_name', '').startswith('unknown_dataset'))):
            self._generate_suite_name()
    
    def _generate_suite_name(self):
        """Generate suite name based on uploaded file + timestamp"""
        suite_name = generate_suite_name()
        st.session_state.current_suite_name = suite_name
    
    def render(self, data: pd.DataFrame):
        """Render the expectation builder interface"""
        # Global layout/style tweaks so widgets consistently fill their columns
        self._inject_layout_css()
        
        # Suite management
        self._render_suite_management()
        
        # Quick actions row (import button and templates)
        self._render_quick_actions(data)
        
        # Main expectation builder
        self._render_expectation_builder(data)
        
        # Current expectations display (collapsible)
        self._render_current_expectations()
        
        # Navigation buttons
        self._render_navigation_buttons()
        
    
    def _render_suite_management(self):
        """Render suite management interface"""
        st.markdown("#### Expectation Suite")
        
        # Show current dataset info
        uploaded_filename = st.session_state.get('uploaded_filename', 'No dataset uploaded')
        if uploaded_filename != 'No dataset uploaded':
            st.info(f"**Dataset:** {uploaded_filename}")

        # Use consistent 2:1 ratio across all sections
        col1, col2 = st.columns([2, 1])

        with col1:
            suite_name = st.text_input(
                "Suite Name:",
                value=st.session_state.current_suite_name,
                help="Enter a name for your expectation suite"
            )
            st.session_state.current_suite_name = suite_name

        with col2:
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("🔄 Regenerate Name", type="secondary", help="Generate new suite name with current timestamp"):
                    new_suite_name = generate_suite_name()
                    st.session_state.current_suite_name = new_suite_name
                    st.success(f"Generated new suite name: {new_suite_name}")
                    st.rerun()
            with btn_col2:
                if st.button("🗑️ Clear All", type="secondary"):
                    st.session_state.expectation_configs = []
                    # Clear any processing flags
                    if 'import_processing' in st.session_state:
                        del st.session_state.import_processing
                    if 'last_imported_file' in st.session_state:
                        del st.session_state.last_imported_file
                    st.success("All expectations cleared!")
    
    def _render_quick_actions(self, data: pd.DataFrame):
        """Render quick actions row with import button and templates"""
        st.markdown("#### Quick Actions")
        
        # Use consistent 2:1 ratio to align with other sections
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Quick Import Button
            if st.button("📥 Import Expectations", type="secondary", help="Import a previously exported expectation suite"):
                st.session_state.show_import_popup = True
        
        with col2:
            # Quick Start Templates (collapsible)
            with st.expander("Quick Start Templates", expanded=False):
                template_options = ["None"] + list(self.config.EXPECTATION_TEMPLATES.keys())
                selected_template = st.selectbox(
                    "Choose a template to get started:",
                    options=template_options,
                    help="Templates provide pre-configured expectations for common scenarios"
                )
                
                if selected_template != "None":
                    template_config = self.config.EXPECTATION_TEMPLATES[selected_template]
                    st.info(f"**{selected_template}**: {template_config['description']}")
                    
                    if st.button(f"🎯 Apply {selected_template} Template", key=f"apply_template_{selected_template}", type="primary"):
                        self._apply_template(selected_template, data)
        
        # Import popup
        if st.session_state.get('show_import_popup', False):
            self._render_import_popup()
    
    def _render_import_popup(self):
        """Render import popup interface"""
        with st.container():
            st.markdown("---")
            st.markdown("### Import Expectations")
            
            uploaded_json = st.file_uploader(
                "Upload expectation suite:",
                type=['json'],
                help="Upload a previously exported expectation suite",
                key="import_uploader"
            )
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                if st.button("❌ Cancel", type="secondary"):
                    st.session_state.show_import_popup = False
                    st.rerun()
            
            with col2:
                if st.button("✅ Import", type="primary", disabled=uploaded_json is None):
                    if uploaded_json:
                        self._process_import(uploaded_json)
                        st.session_state.show_import_popup = False
                        st.rerun()
    
    def _process_import(self, uploaded_json):
        """Process imported expectation suite"""
        # Check if we're already processing an import to prevent loops
        if 'import_processing' in st.session_state and st.session_state.import_processing:
            st.info("Processing import...")
            return
        
        try:
            # Set processing flag to prevent loops
            st.session_state.import_processing = True
            
            import json
            # Reset file pointer to beginning
            uploaded_json.seek(0)
            import_data = json.loads(uploaded_json.read())
            
            # Validate the imported data structure
            if 'expectations' not in import_data:
                st.error("Invalid file format: 'expectations' key not found")
                return
            
            if not isinstance(import_data['expectations'], list):
                st.error("Invalid file format: 'expectations' must be a list")
                return
            
            # Validate each expectation has required fields
            valid_expectations = []
            for i, exp in enumerate(import_data['expectations']):
                if not isinstance(exp, dict):
                    st.warning(f"Expectation {i+1} is not a valid dictionary, skipping...")
                    continue
                
                if 'expectation_type' not in exp:
                    st.warning(f"Expectation {i+1} missing 'expectation_type', skipping...")
                    continue
                
                if 'kwargs' not in exp:
                    st.warning(f"Expectation {i+1} missing 'kwargs', skipping...")
                    continue
                
                valid_expectations.append(exp)
            
            if not valid_expectations:
                st.error("No valid expectations found in the file!")
                return
            
            # Update session state
            st.session_state.current_suite_name = import_data.get(
                'suite_name', 'imported_suite'
            )
            st.session_state.expectation_configs = valid_expectations
            
            # Clear any existing suite to force recreation
            if 'expectation_suite' in st.session_state:
                del st.session_state.expectation_suite
            
            # Mark this file as imported to prevent re-processing
            st.session_state.last_imported_file = uploaded_json.name
            
            st.success(f"Successfully imported {len(valid_expectations)} expectations!")
            if len(valid_expectations) < len(import_data['expectations']):
                st.warning(f"{len(import_data['expectations']) - len(valid_expectations)} expectations were skipped due to invalid format.")
            
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON file: {str(e)}")
        except Exception as e:
            st.error(f"Error importing expectations: {str(e)}")
            st.error("Please ensure the file is a valid expectation suite JSON file.")
        finally:
            # Always clear the processing flag
            st.session_state.import_processing = False
    
    
    def _apply_template(self, template_name: str, data: pd.DataFrame):
        """Apply a smart template to the current suite"""
        try:
            # Use SmartTemplateEngine to generate intelligent expectations
            smart_expectations = self.smart_engine.analyze_data_for_template(data, template_name)
            
            if not smart_expectations:
                # Fallback to basic template logic if smart engine returns nothing
                st.warning(f"Smart template '{template_name}' didn't generate expectations. Using basic fallback.")
                self._apply_basic_template_fallback(template_name, data)
                return
            
            # Add the generated expectations to session state
            added_count = 0
            for expectation in smart_expectations:
                if self._is_valid_expectation_config(expectation):
                    st.session_state.expectation_configs.append(expectation)
                    added_count += 1
                else:
                    st.warning(f"Skipped invalid expectation: {expectation.get('expectation_type', 'unknown')}")
            
            if added_count > 0:
                st.success(f"Applied {template_name} with {added_count} intelligent expectations based on your data!")
            else:
                st.error(f"No valid expectations were generated from {template_name} template.")
                
        except Exception as e:
            st.error(f"Error applying smart template: {str(e)}")
            # Fallback to basic template
            self._apply_basic_template_fallback(template_name, data)
    
    def _apply_basic_template_fallback(self, template_name: str, data: pd.DataFrame):
        """Fallback to basic template logic if smart template fails"""
        template_config = self.config.EXPECTATION_TEMPLATES[template_name]
        added_count = 0
        
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
                added_count += 1
            
            elif expectation_type == "expect_table_columns_to_match_ordered_list":
                config = {
                    'expectation_type': expectation_type,
                    'kwargs': {
                        'column_list': list(data.columns)
                    }
                }
                st.session_state.expectation_configs.append(config)
                added_count += 1
            
            elif expectation_type == "expect_column_values_to_not_be_null":
                for col in data.columns:
                    null_pct = (data[col].isnull().sum() / len(data)) * 100
                    if null_pct < 10:
                        config = {
                            'expectation_type': expectation_type,
                            'kwargs': {'column': col}
                        }
                        st.session_state.expectation_configs.append(config)
                        added_count += 1
        
        st.success(f"Applied {template_name} fallback template with {added_count} expectations!")
    
    def _is_valid_expectation_config(self, config: Dict[str, Any]) -> bool:
        """Validate an expectation configuration"""
        if not isinstance(config, dict):
            return False
        
        if 'expectation_type' not in config:
            return False
        
        if 'kwargs' not in config or not isinstance(config['kwargs'], dict):
            return False
        
        return True
    
    def _render_expectation_builder(self, data: pd.DataFrame):
        """Render the main expectation builder"""
        st.markdown("#### Build Custom Expectations")
        
        # Expectation type selection
        available_expectations = self.ge_helpers.get_available_expectations()
        
        # Consistent two-column ratio across sections
        col1, col2 = st.columns([2, 1])
        
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
        if st.button("✨ Add Expectation", type="primary", key="add_expectation_btn"):
            if expectation_config:
                st.session_state.expectation_configs.append(expectation_config)
                st.success("Expectation added successfully!")
            else:
                st.error("Please configure all required parameters!")

    def _inject_layout_css(self):
        """Inject lightweight CSS to normalize widget widths in columns."""
        st.markdown(
            """
            <style>
            /* Ensure core input widgets fill their column width */
            div[data-testid="stSelectbox"] > div { width: 100%; }
            div[data-testid="stTextInput"] > div > div { width: 100%; }
            div[data-testid="stNumberInput"] > div { width: 100%; }
            div[data-testid="stFileUploader"] { width: 100%; }
            div[data-testid="stFileUploaderDropzone"] { min-height: 110px; }
            /* Make info boxes use full width of their column */
            div[role="alert"] { width: 100%; }
            </style>
            """,
            unsafe_allow_html=True,
        )
    
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
        
        elif expectation_type == "expect_custom_sql_query_to_return_expected_result":
            # Custom SQL expectation - decorator-based dialog
            st.markdown("**Custom SQL-based validation allows you to create complex business rules and multi-column checks.**")

            @st.dialog("Custom SQL Query Builder", width="large", dismissible=True, on_dismiss="ignore")
            def open_sql_builder_dialog():
                custom_config = self.sql_query_builder.render(data)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("❌ Cancel", type="secondary"):
                        # Close dialog by rerunning without calling the dialog again
                        st.rerun()
                with col2:
                    if st.button("✅ Add SQL Expectation", type="primary", disabled=custom_config is None):
                        if custom_config:
                            st.session_state.expectation_configs.append(custom_config)
                            st.success("SQL expectation added successfully!")
                            st.rerun()

            if st.button("🔍 Open SQL Query Builder", type="secondary"):
                open_sql_builder_dialog()

            return None
        
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
        """Render current expectations list with better organization"""
        st.markdown("#### Current Expectations")
        
        if not st.session_state.expectation_configs:
            st.info("No expectations configured yet. Add some expectations above!")
            return
        
        # Summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Expectations", len(st.session_state.expectation_configs))
        with col2:
            column_expectations = sum(1 for config in st.session_state.expectation_configs 
                                    if 'column' in config.get('kwargs', {}))
            st.metric("Column Expectations", column_expectations)
        with col3:
            table_expectations = len(st.session_state.expectation_configs) - column_expectations
            st.metric("Table Expectations", table_expectations)
        
        # Expectations management in collapsible section
        with st.expander("Manage Expectations", expanded=False):
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
            selected_expectations = st.multiselect(
                "Select expectations to remove:",
                options=range(len(st.session_state.expectation_configs)),
                format_func=lambda x: f"#{x+1}: {expectations_data[x]['Type']} - {expectations_data[x]['Column']}"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Remove Selected", type="secondary", key="remove_selected_btn"):
                    # Remove in reverse order to maintain indices
                    for idx in sorted(selected_expectations, reverse=True):
                        st.session_state.expectation_configs.pop(idx)
                    st.success("Selected expectations removed!")
                    st.rerun()
                
                if st.button("🗑️ Clear All", type="secondary", key="clear_all_btn"):
                    st.session_state.expectation_configs = []
                    st.success("All expectations cleared!")
                    st.rerun()
            
            with col2:
                # Export button
                if st.button("📤 Export Suite", type="secondary"):
                    self._export_expectations()
            
            # Display the table
            st.dataframe(expectations_df, use_container_width=True, hide_index=True)
    
    def _export_expectations(self):
        """Export expectations to JSON"""
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
                mime="application/json",
                key="export_expectations_btn"
            )
    
    def _render_navigation_buttons(self):
        """Render navigation buttons"""
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⬅️ Back to Profiling", type="secondary", key="back_to_profiling_btn"):
                st.session_state.current_step = 'profile'
                st.rerun()
        
        with col2:
            # Export expectations
            self._render_export()
        
        with col3:
            if len(st.session_state.expectation_configs) > 0:
                if st.button("⚙️ Configure Suite →", type="primary", key="configure_suite_btn"):
                    # Create the expectation suite and store it
                    suite = self.ge_helpers.create_expectation_suite(
                        st.session_state.current_suite_name
                    )
                    
                    if suite:
                        # Add all configured expectations to the suite
                        success_count = 0
                        for i, config in enumerate(st.session_state.expectation_configs):
                            if self.ge_helpers.add_expectation_to_suite(suite, config):
                                success_count += 1
                            else:
                                st.error(f"Failed to add expectation {i+1}")
                        
                        if success_count > 0:
                            # Persist suite and configs in session
                            st.session_state.expectation_suite = suite
                            try:
                                st.session_state.expectation_suite_json = self.ge_helpers.export_suite_to_json(suite)
                            except Exception:
                                st.session_state.expectation_suite_json = None
                            st.session_state.current_step = 'validate'
                            st.success(f"Expectation suite created with {success_count} expectations! Ready for validation.")
                            st.rerun()
                        else:
                            st.error("Failed to add any expectations to the suite!")
                    else:
                        st.error("Failed to create expectation suite!")
            else:
                st.warning("Add some expectations before proceeding!")
    
    def _render_export(self):
        """Render export functionality"""
        with st.popover("💾 Export"):
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
                    mime="application/json",
                    key="export_expectations_btn"
                )
            else:
                st.info("No expectations to export")
            

    
    def _render_sql_dialog(self, data: pd.DataFrame):
        """Render the SQL Query Builder dialog."""
        # Create a modal-like popup using container and styling
        with st.container():
            # Add some visual separation
            st.markdown("---")
            
            # Create a styled container that looks like a modal
            with st.container():
                st.markdown("### Custom SQL Query Builder")
                st.info("Use this tool to build complex SQL queries for data validation.")
                
                # Render the SQLQueryBuilderComponent within the dialog
                custom_config = self.sql_query_builder.render(data)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("❌ Cancel", type="secondary", key="cancel_sql_dialog_btn"):
                        st.session_state.show_sql_popup = False
                        st.rerun()
                
                with col2:
                    if st.button("✅ Add SQL Expectation", type="primary", key="add_sql_expectation_btn", disabled=custom_config is None):
                        if custom_config:
                            st.session_state.expectation_configs.append(custom_config)
                            st.success("SQL expectation added successfully!")
                            st.session_state.show_sql_popup = False
                            st.rerun()
                        else:
                            st.error("Please configure a valid SQL query first.")
            
            # Add visual separation at the end
            st.markdown("---")
    
    