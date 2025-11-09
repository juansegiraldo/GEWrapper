import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.custom_sql_expectations import CustomSQLExpectation, SQLQueryBuilder
from components.openai_sql_generator import OpenAISQLGenerator


class SQLQueryBuilderComponent:
    """Streamlit component for building custom SQL expectations with visual interface"""
    
    def __init__(self):
        self.custom_sql_expectation = CustomSQLExpectation()
        self.query_builder = SQLQueryBuilder()
        self.openai_generator = OpenAISQLGenerator()
    
    def render(self, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Render the simplified SQL query builder interface"""
        # No title needed - dialog already has one
        query_config = self._render_manual_query_builder(data)

        return query_config
    
    def _render_template_selection(self) -> Optional[Dict[str, Any]]:
        """Render template selection interface inside a collapsible expander"""
        with st.expander("Use a Template (optional)", expanded=False):
            # Get template categories with detailed descriptions
            categories = self.custom_sql_expectation.get_template_categories()
            
            # Create detailed tooltips for each category
            category_descriptions = {
                "aggregations": "Templates for counting, summing, and aggregating data across columns",
                "business": "Business logic validations like salary ranges, department rules, and compliance checks",
                "calculations": "Mathematical validations and computed field checks",
                "duplicates": "Finding duplicate records and uniqueness validations",
                "integrity": "Data integrity checks like foreign key relationships and referential integrity",
                "relationships": "Cross-table and cross-column relationship validations",
                "temporal": "Date and time-based validations, range checks, and chronological order"
            }
            
            # Create comprehensive help text with all categories
            help_text = (
                "Choose a category of pre-built query templates. Each category contains specialized templates for different types of data validation scenarios.\n\n**Available Categories:**\n"
            )
            for category in categories:
                category_templates = self.custom_sql_expectation.get_templates_by_category(category)
                help_text += (
                    f"• **{category.title()}** ({len(category_templates)} templates): "
                    f"{category_descriptions.get(category.lower(), 'General templates')}\n"
                )
            
            selected_category = st.selectbox(
                "Template Category:",
                options=["None"] + categories,
                help=help_text,
                format_func=lambda x: (
                    f"{x.title()} - {category_descriptions.get(x.lower(), 'General templates')}"
                    if x != "None" else "None - Build custom query manually"
                )
            )
            
            if selected_category != "None":
                templates = self.custom_sql_expectation.get_templates_by_category(selected_category)
                template_names = list(templates.keys())
                
                selected_template = st.selectbox(
                    "Template:",
                    options=[""] + template_names,
                    format_func=lambda x: templates[x]["name"] if x else "Select template...",
                    help=f"Choose a specific {selected_category.lower()} template to use as a starting point"
                )
                
                if selected_template:
                    template_config = templates[selected_template]
                    st.info(f"**{template_config['name']}**: {template_config['description']}")
                    return template_config
        
        return None
    
    def _render_template_builder(self, template_config: Dict[str, Any], data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Render template-based query builder"""
        st.markdown("##### Configure Template Parameters")
        
        template_name = template_config["name"]
        template_sql = template_config["template"]
        parameters = template_config.get("parameters", [])
        
        # Show template preview
        with st.expander("Template SQL Preview", expanded=False):
            st.code(template_sql, language="sql")
        
        # Parameter configuration
        param_values = {}
        
        # Dynamic parameter inputs based on template
        if template_name == "Cross-Column Comparison":
            col1, col2, col3 = st.columns(3)
            with col1:
                param_values["column1"] = self.query_builder.render_column_selector(
                    data, "First Column:", "template_col1", help_text="Select the first column to compare"
                )
            with col2:
                param_values["column2"] = self.query_builder.render_column_selector(
                    data, "Second Column:", "template_col2", help_text="Select the second column to compare"
                )
            with col3:
                operators = ["<", "<=", ">", ">=", "=", "!="]
                param_values["operator"] = self.query_builder.render_operator_selector(
                    "Operator:", "template_operator", operators
                )
        
        elif template_name == "Mathematical Relationship":
            col1, col2 = st.columns(2)
            with col1:
                param_values["result_column"] = self.query_builder.render_column_selector(
                    data, "Result Column:", "template_result_col", 
                    help_text="Column that should contain the calculated result"
                )
                param_values["operand1"] = self.query_builder.render_column_selector(
                    data, "First Operand:", "template_operand1", 
                    help_text="First column in the calculation"
                )
                param_values["operand2"] = self.query_builder.render_column_selector(
                    data, "Second Operand:", "template_operand2", 
                    help_text="Second column in the calculation"
                )
            with col2:
                operators = ["+", "-", "*", "/"]
                param_values["operator"] = self.query_builder.render_operator_selector(
                    "Mathematical Operator:", "template_math_op", operators
                )
                param_values["tolerance"] = st.number_input(
                    "Tolerance:", 
                    min_value=0.0, 
                    value=0.01, 
                    step=0.01,
                    help="Acceptable difference between expected and actual values"
                )
        
        elif template_name == "Referential Integrity":
            col1, col2 = st.columns(2)
            with col1:
                param_values["column"] = self.query_builder.render_column_selector(
                    data, "Foreign Key Column:", "template_fk_col", 
                    help_text="Column containing foreign key values"
                )
                param_values["reference_table"] = st.text_input(
                    "Reference Table:", 
                    help="Name of the table containing the primary keys"
                )
            with col2:
                param_values["reference_column"] = st.text_input(
                    "Reference Column:", 
                    help="Column in the reference table containing primary keys"
                )
        
        elif template_name == "Custom Business Rule":
            param_values["custom_condition"] = st.text_area(
                "Business Rule Condition:",
                height=100,
                help="Enter the SQL WHERE clause condition that defines your business rule",
                placeholder="Example: start_date <= end_date AND status IN ('active', 'pending')"
            )
        
        elif template_name == "Data Freshness Check":
            col1, col2 = st.columns(2)
            with col1:
                param_values["date_column"] = self.query_builder.render_column_selector(
                    data, "Date Column:", "template_date_col", 
                    help_text="Column containing date/timestamp values"
                )
            with col2:
                param_values["max_age_days"] = st.number_input(
                    "Maximum Age (days):", 
                    min_value=1, 
                    value=7,
                    help="Maximum number of days old the data can be"
                )
        
        elif template_name == "Aggregation Validation":
            col1, col2 = st.columns(2)
            with col1:
                aggregations = ["SUM", "COUNT", "AVG", "MIN", "MAX"]
                param_values["aggregation"] = st.selectbox("Aggregation Function:", aggregations)
                param_values["column"] = self.query_builder.render_column_selector(
                    data, "Column:", "template_agg_col", 
                    help_text="Column to aggregate"
                )
            with col2:
                operators = ["=", "!=", "<", "<=", ">", ">="]
                param_values["operator"] = self.query_builder.render_operator_selector(
                    "Comparison Operator:", "template_agg_op", operators
                )
                param_values["expected_value"] = st.number_input(
                    "Expected Value:", 
                    help="Expected result of the aggregation"
                )
        
        elif template_name == "Advanced Duplicate Detection":
            param_values["columns"] = ", ".join(self.query_builder.render_column_selector(
                data, "Columns to Check for Duplicates:", "template_dup_cols", 
                multi=True, help_text="Select columns that should be unique together"
            ))
            param_values["conditions"] = st.text_input(
                "Additional Conditions (optional):",
                help="Extra WHERE clause conditions",
                placeholder="Example: status = 'active'"
            )
            if not param_values["conditions"]:
                param_values["conditions"] = "1=1"  # Default condition
        
        # Build final query
        if all(param_values.get(param) for param in parameters if param != "conditions"):
            param_values["table_name"] = "{table_name}"  # Keep placeholder for runtime replacement
            
            final_query = self.query_builder.build_query_from_template(template_sql, param_values)
            
            # Validation configuration
            return self._render_query_configuration(
                data,
                final_query, 
                template_config.get("expected_result", "empty"),
                f"{template_name} Validation"
            )
        else:
            st.warning("Please fill in all required parameters to build the query.")
            return None
    
    def _render_manual_query_builder(self, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Render simplified SQL builder with only AI section"""

        # OpenAI generator section - this has columns, text for LLM, model, and Create SQL button
        generated_query = self.openai_generator.render_openai_section(data)

        # Test Query button - simplified
        st.markdown("---")
        if st.button("🧪 Test SQL", key="test_query_btn", type="secondary", use_container_width=True):
            current_query = st.session_state.get('sql_query', '')
            if not current_query:
                st.warning("No SQL query found. Please generate a query first.")
            else:
                try:
                    fixed_sql_query = self._fix_boolean_conditions(current_query, data)
                    result = self.custom_sql_expectation.execute_sql_query(data, fixed_sql_query)
                    if not result.empty and 'violation_count' in result.columns:
                        violation_count = result['violation_count'].iloc[0]
                        if violation_count == 0:
                            st.success(f"✅ Query valid - {violation_count} violations found")
                        else:
                            st.warning(f"⚠️ Query executed - {violation_count} violations found")
                    else:
                        st.info("Query executed successfully")
                except Exception as e:
                    st.error(f"Test failed: {str(e)}")

        # Show inline configuration if there's a valid query
        current_query = st.session_state.get('sql_query', '')
        if current_query:
            validation_result = self.custom_sql_expectation.validate_sql_query(current_query)
            if validation_result["is_valid"] and not validation_result["security_issues"]:
                return self._render_query_configuration(data, current_query, "empty", "Custom SQL Validation")

        return None

    def _fix_boolean_conditions(self, sql_query: str, data: pd.DataFrame) -> str:
        """Fix SQL query to handle boolean columns correctly with pandasql"""
        # Check if the query contains boolean column comparisons
        for col in data.columns:
            if data[col].dtype == bool:
                # Replace common boolean patterns
                sql_query = sql_query.replace(f"{col} = 1", f"{col} = True")
                sql_query = sql_query.replace(f"{col} = 0", f"{col} = False")
                sql_query = sql_query.replace(f"{col} = '1'", f"{col} = True")
                sql_query = sql_query.replace(f"{col} = '0'", f"{col} = False")
        
        return sql_query

    def _render_query_configuration(
        self,
        data: pd.DataFrame,
        sql_query: str,
        default_expected: str,
        default_name: str
    ) -> Optional[Dict[str, Any]]:
        """Render simplified query configuration options"""
        # Fix boolean conditions in the SQL query
        fixed_sql_query = self._fix_boolean_conditions(sql_query, data)

        # Use generated name and description if available
        default_name_value = st.session_state.get('generated_name', default_name)
        default_description_value = st.session_state.get('generated_description', '')

        st.markdown("---")
        name = st.text_input(
            "Name:",
            value=default_name_value,
            help="Descriptive name for this validation rule"
        )

        description = st.text_area(
            "Description:",
            value=default_description_value,
            height=60,
            help="Optional description"
        )

        # Build final configuration
        if name and fixed_sql_query:
            config = self.custom_sql_expectation.build_expectation_config(
                name=name,
                sql_query=fixed_sql_query,
                expected_result_type=default_expected,
                expected_value=None,
                description=description,
                tolerance=0.0
            )

            return config

        return None