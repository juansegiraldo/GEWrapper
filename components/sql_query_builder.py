import streamlit as st
import pandas as pd
from typing import Dict, Any, List, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.custom_sql_expectations import CustomSQLExpectation, SQLQueryBuilder


class SQLQueryBuilderComponent:
    """Streamlit component for building custom SQL expectations with visual interface"""
    
    def __init__(self):
        self.custom_sql_expectation = CustomSQLExpectation()
        self.query_builder = SQLQueryBuilder()
    
    def render(self, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Render the SQL query builder interface"""
        st.markdown("#### 🔍 Custom SQL Query Builder")
        st.markdown("Create complex validations using SQL queries for multi-column business rules.")
        
        # Template selection
        template_config = self._render_template_selection()
        
        if template_config:
            # Build query from template
            query_config = self._render_template_builder(template_config, data)
        else:
            # Manual query builder
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
        st.markdown("##### 🔧 Configure Template Parameters")
        
        template_name = template_config["name"]
        template_sql = template_config["template"]
        parameters = template_config.get("parameters", [])
        
        # Show template preview
        with st.expander("📋 Template SQL Preview", expanded=False):
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
        """Render manual SQL builder with simplified 2-column layout"""
        st.markdown("##### Manual SQL Query")
        
        # Two-column layout: SQL input (wide) + Available Columns (narrow)
        # Use consistent 2:1 ratio across the Configure Expectations step
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Initialize session state for SQL query
            if 'sql_query' not in st.session_state:
                st.session_state['sql_query'] = ""
            
            # Manual SQL input - takes up more space
            sql_query = st.text_area(
                "SQL query:",
                value=st.session_state.get('sql_query', ''),
                height=200,
                help="Write your custom SQL query. Use {table_name} as placeholder for the data table.",
                placeholder="""
Example:
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE email IS NULL OR email NOT LIKE '%@%.%'

💡 Tip: Use True/False for boolean columns, not 1/0
💡 The app automatically converts active = 1 to active = True
"""
            )
            
            # Native link button to custom GPT for SQL help
            gpt_url = "https://chatgpt.com/g/g-68b1ee414c4081919498f880f3ee5993-datawash-custom-sql-generator"
            if hasattr(st, "link_button"):
                st.link_button("🚀 Open DataWash SQL Generator GPT", gpt_url, use_container_width=True)
            else:
                st.markdown(f"[🚀 Open DataWash SQL Generator GPT]({gpt_url})")
            
            # Update session state
            st.session_state['sql_query'] = sql_query
            
            if sql_query:
                # Validate SQL
                validation_result = self.custom_sql_expectation.validate_sql_query(sql_query)
                
                if not validation_result["is_valid"]:
                    for error in validation_result["errors"]:
                        st.error(f"❌ {error}")
                
                for warning in validation_result["warnings"]:
                    st.warning(f"⚠️ {warning}")
                
                for security_issue in validation_result["security_issues"]:
                    st.error(f"🔒 Security Issue: {security_issue}")
                
                if validation_result["is_valid"] and not validation_result["security_issues"]:
                    return self._render_query_configuration(data, sql_query, "empty", "Custom SQL Validation")
        
        with col2:
            # Available Columns (with filter)
            st.markdown("**Available Columns**")
            filter_text = st.text_input("Filter columns", key="available_cols_filter")
            columns_iter = data.columns
            if filter_text:
                lower_filter = filter_text.lower()
                columns_iter = [c for c in data.columns if lower_filter in c.lower()]
            for col in columns_iter:
                col_type = str(data[col].dtype)
                st.write(f"• `{col}` ({col_type})")

        # Collapsed helper area
        with st.expander("Help & Tools", expanded=False):
            tips_tab, patterns_tab, prompt_tab, examples_tab, data_tab, tools_tab = st.tabs([
                "Tips", "Patterns", "Prompt", "Examples", "Data", "Tools"
            ])

            with tips_tab:
                st.markdown("**General SQL Tips**")
                st.write("• Use `{table_name}` as table placeholder")
                st.write("• Return `violation_count` column")
                st.write("• Use WHERE NOT (condition) pattern")
                st.write("• Handle NULL values appropriately")
                st.write("• For boolean columns, prefer `column = True` or `column = False`")
                st.write("• The app will automatically fix `column = 1` to `column = True`")
                st.markdown("**Boolean Column Syntax**")
                st.info(
                    """
✅ Recommended: `active = True` / `active = False`, `status = 'active'` / `status = 'inactive'`

⚠️ Works but discouraged: `active = 1` / `active = 0`, `active = 'true'` / `active = 'false'`

❌ Won't work: `active = '1'` / `active = '0'`
                    """
                )

            with patterns_tab:
                st.markdown("**Common Validation Patterns**")
                st.markdown(
                    """
**Email Validation:**
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE email IS NULL OR email NOT LIKE '%@%.%'
```

**Date Range Validation:**
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE join_date < '2020-01-01' OR join_date > CURRENT_DATE
```

**Email Format Validation:**
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE email NOT LIKE '%@%.%' OR email IS NULL
```

**Age Range Validation:**
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE age < 18 OR age > 65
```

**Required Field Validation:**
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE name IS NULL OR TRIM(name) = ''
```

**Cross-Column Validation:**
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE start_date >= end_date AND start_date IS NOT NULL AND end_date IS NOT NULL
```
                    """
                )

            with prompt_tab:
                st.markdown("**LLM Prompt for SQL Generation**")
                st.code(
                    """
Generate a SQL query to validate data quality. Requirements:
- Use {table_name} as the table name placeholder
- Return COUNT(*) as violation_count
- Use True/False for boolean columns (not 1/0)
- Example: WHERE email IS NULL OR email NOT LIKE '%@%.%'
- Focus on finding violations (rows that should NOT exist)
- Use clear, descriptive conditions

Context: [Describe your validation rule here]
                    """,
                    language="text",
                )

            with examples_tab:
                st.markdown("**Quick Query Examples**")
                example_queries = {
                    "Check for NULL values": "SELECT COUNT(*) as violation_count FROM {table_name} WHERE name IS NULL",
                    "Salary range check": "SELECT COUNT(*) as violation_count FROM {table_name} WHERE salary < 30000 OR salary > 100000",
                    "Email format": "SELECT COUNT(*) as violation_count FROM {table_name} WHERE email NOT LIKE '%@%.%'",
                    "Invalid emails": "SELECT COUNT(*) as violation_count FROM {table_name} WHERE email IS NULL OR email NOT LIKE '%@%.%'",
                }
                cols = st.columns(2)
                for idx, (name, query) in enumerate(example_queries.items()):
                    with cols[idx % 2]:
                        if st.button(f"📋 {name}", key=f"example_{name}"):
                            st.session_state['sql_query'] = query
                            st.rerun()

            with data_tab:
                st.write(f"**Shape:** {data.shape[0]} rows × {data.shape[1]} columns")
                st.write(f"**Memory:** {data.memory_usage(deep=True).sum() / 1024:.1f} KB")
                with st.expander("Sample Data (first 5 rows)", expanded=False):
                    st.dataframe(data.head(), use_container_width=True)

            with tools_tab:
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    if st.button("🧹 Clear Query", key="clear_query"):
                        st.session_state['sql_query'] = ""
                        st.rerun()
                with col_b:
                    if st.button("📋 Copy Template", key="copy_template"):
                        template = """SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE [your_condition_here]"""
                        st.code(template, language="sql")
                with col_c:
                    if st.button("🔍 Validate Current Query", key="validate_query"):
                        if 'sql_query' in st.session_state and st.session_state['sql_query']:
                            validation_result = self.custom_sql_expectation.validate_sql_query(st.session_state['sql_query'])
                            if validation_result["is_valid"]:
                                st.success("✅ Query is valid!")
                            else:
                                st.error("❌ Query has issues")
                                for error in validation_result["errors"]:
                                    st.write(f"• {error}")

                # Test query action and debugging output
                if st.button("🧪 Test Query", key="test_query_btn"):
                    try:
                        fixed_sql_query = self._fix_boolean_conditions(st.session_state.get('sql_query', ''), data)
                        st.markdown("**🔍 Testing Query:**")
                        st.code(fixed_sql_query, language="sql")
                        st.write("**📊 Data Info:**")
                        st.write(f"Data shape: {data.shape}")
                        st.write(f"Data columns: {list(data.columns)}")
                        st.write(f"Data types: {dict(data.dtypes)}")
                        
                        # Show sample data for debugging
                        st.write("**📋 Sample Data (first 3 rows):**")
                        sample_data = data.head(3)
                        for idx, row in sample_data.iterrows():
                            display_values = [f"{col}={row[col]}" for col in row.index]
                            st.write(f"  Row {idx}: {', '.join(display_values)}")
                        
                        result = self.custom_sql_expectation.execute_sql_query(data, fixed_sql_query)
                        if not result.empty:
                            st.success("✅ Query executed successfully!")
                            st.dataframe(result.head(), use_container_width=True)
                            if 'violation_count' in result.columns:
                                violation_count = result['violation_count'].iloc[0]
                                st.info(f"Violation count: {violation_count}")
                                
                                # Add more debugging for the specific case
                                if violation_count == 0:
                                    st.warning("⚠️ Query returned 0 violations. This means no data quality issues were found.")
                                    st.info("ℹ️ Your data appears to be clean according to this validation rule.")
                        else:
                            st.warning("Query returned no results")
                    except Exception as e:
                        st.error(f"Query test failed: {str(e)}")
        
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
        """Render query configuration options"""
        st.markdown("##### ⚙️ Query Configuration")
        
        # Fix boolean conditions in the SQL query
        fixed_sql_query = self._fix_boolean_conditions(sql_query, data)
        
        # Keep a consistent 2:1 ratio for configuration as well
        col1, col2 = st.columns([2, 1])
        
        with col1:
            name = st.text_input(
                "Expectation Name:",
                value=default_name,
                help="Descriptive name for this validation rule"
            )
            
            description = st.text_area(
                "Description:",
                height=80,
                help="Detailed description of what this validation checks"
            )
        
        with col2:
            expected_result_options = [
                ("empty", "No violations (expect query to return 0 rows/violations)"),
                ("non_empty", "Violations exist (expect query to return rows)"),
                ("count_equals", "Exact count (specify expected number)"),
                ("count_between", "Count within range (specify min/max)")
            ]
            
            expected_result_type = st.selectbox(
                "Expected Result:",
                options=[opt[0] for opt in expected_result_options],
                format_func=lambda x: next(opt[1] for opt in expected_result_options if opt[0] == x),
                index=next(i for i, opt in enumerate(expected_result_options) if opt[0] == default_expected)
            )
            
            # Additional configuration based on expected result type
            expected_value = None
            tolerance = 0.0
            min_value = None
            max_value = None
            
            if expected_result_type == "count_equals":
                expected_value = st.number_input(
                    "Expected Count:",
                    min_value=0,
                    help="Exact number of violations/rows expected"
                )
                tolerance = st.number_input(
                    "Tolerance:",
                    min_value=0.0,
                    value=0.0,
                    help="Acceptable deviation from expected count"
                )
            elif expected_result_type == "count_between":
                col_min, col_max = st.columns(2)
                with col_min:
                    min_value = st.number_input("Min Count:", min_value=0, value=0)
                with col_max:
                    max_value = st.number_input("Max Count:", min_value=0, value=10)
        
        # Query preview
        with st.expander("📋 Final SQL Query Preview", expanded=False):
            st.code(fixed_sql_query, language="sql")
        
        # Test query option
        if st.button("🧪 Test Query", help="Test the query against current data"):
            try:
                # Show the query being tested
                st.markdown("**🔍 Testing Query:**")
                st.code(fixed_sql_query, language="sql")
                
                # Add debugging information
                st.write("**📊 Data Info:**")
                st.write(f"Data shape: {data.shape}")
                st.write(f"Data columns: {list(data.columns)}")
                st.write(f"Data types: {dict(data.dtypes)}")
                
                # Show sample data for debugging
                st.write("**📋 Sample Data (first 3 rows):**")
                sample_data = data.head(3)
                for idx, row in sample_data.iterrows():
                    display_values = [f"{col}={row[col]}" for col in row.index]
                    st.write(f"  Row {idx}: {', '.join(display_values)}")
                
                result = self.custom_sql_expectation.execute_sql_query(data, fixed_sql_query)
                if not result.empty:
                    st.success("✅ Query executed successfully!")
                    st.dataframe(result.head(), use_container_width=True)
                    
                    if 'violation_count' in result.columns:
                        violation_count = result['violation_count'].iloc[0]
                        st.info(f"Violation count: {violation_count}")
                        
                        # Add more debugging for the specific case
                        if violation_count == 0:
                            st.warning("⚠️ Query returned 0 violations. This means no data quality issues were found.")
                            st.info("ℹ️ Your data appears to be clean according to this validation rule.")
                else:
                    st.warning("Query returned no results")
            except Exception as e:
                st.error(f"Query test failed: {str(e)}")
        
        # Build final configuration
        if name and fixed_sql_query:
            config = self.custom_sql_expectation.build_expectation_config(
                name=name,
                sql_query=fixed_sql_query,
                expected_result_type=expected_result_type,
                expected_value=expected_value,
                description=description,
                tolerance=tolerance
            )
            
            # Add range values if needed
            if expected_result_type == "count_between":
                config['kwargs']['min_value'] = min_value
                config['kwargs']['max_value'] = max_value
            
            return config
        
        return None