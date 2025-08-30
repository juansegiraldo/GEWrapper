import pandas as pd
import streamlit as st
from typing import Dict, List, Any, Optional, Union
import re
import sqlparse
from sqlparse import sql, tokens


class CustomSQLExpectation:
    """Framework for creating and managing custom SQL-based expectations"""
    
    def __init__(self):
        self.expectation_type = "expect_custom_sql_query_to_return_expected_result"
        self.query_templates = self._load_query_templates()
    
    def _load_query_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined SQL query templates for common validation patterns"""
        return {
            "cross_column_comparison": {
                "name": "Cross-Column Comparison",
                "description": "Compare values between two columns (e.g., start_date < end_date)",
                "template": """
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE NOT ({column1} {operator} {column2})
  AND {column1} IS NOT NULL 
  AND {column2} IS NOT NULL
""",
                "parameters": ["column1", "column2", "operator"],
                "expected_result": "empty",
                "category": "relationships"
            },
            "mathematical_relationship": {
                "name": "Mathematical Relationship",
                "description": "Validate mathematical relationships (e.g., total = price * quantity)",
                "template": """
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE ABS({result_column} - ({operand1} {operator} {operand2})) > {tolerance}
  AND {result_column} IS NOT NULL
  AND {operand1} IS NOT NULL
  AND {operand2} IS NOT NULL
""",
                "parameters": ["result_column", "operand1", "operator", "operand2", "tolerance"],
                "expected_result": "empty",
                "category": "calculations"
            },
            "referential_integrity": {
                "name": "Referential Integrity",
                "description": "Check if values in one column exist in another table/column",
                "template": """
SELECT COUNT(*) as violation_count
FROM {table_name} t1
LEFT JOIN {reference_table} t2 ON t1.{column} = t2.{reference_column}
WHERE t1.{column} IS NOT NULL
  AND t2.{reference_column} IS NULL
""",
                "parameters": ["column", "reference_table", "reference_column"],
                "expected_result": "empty",
                "category": "integrity"
            },
            "business_rule": {
                "name": "Custom Business Rule",
                "description": "Define custom business logic validation",
                "template": """
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE NOT ({custom_condition})
""",
                "parameters": ["custom_condition"],
                "expected_result": "empty",
                "category": "business"
            },
            "data_freshness": {
                "name": "Data Freshness Check",
                "description": "Ensure data was updated within a specified time period",
                "template": """
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE {date_column} < CURRENT_DATE - INTERVAL '{max_age_days}' DAY
""",
                "parameters": ["date_column", "max_age_days"],
                "expected_result": "empty",
                "category": "temporal"
            },
            "aggregation_check": {
                "name": "Aggregation Validation",
                "description": "Validate aggregated values (sum, count, average, etc.)",
                "template": """
SELECT 
  CASE 
    WHEN {aggregation}({column}) {operator} {expected_value} THEN 0
    ELSE 1
  END as violation_count
FROM {table_name}
""",
                "parameters": ["aggregation", "column", "operator", "expected_value"],
                "expected_result": "empty",
                "category": "aggregations"
            },
            "duplicate_detection": {
                "name": "Advanced Duplicate Detection",
                "description": "Find duplicates across multiple columns with conditions",
                "template": """
SELECT COUNT(*) as violation_count
FROM (
  SELECT {columns}, COUNT(*) as duplicate_count
  FROM {table_name}
  WHERE {conditions}
  GROUP BY {columns}
  HAVING COUNT(*) > 1
) duplicates
""",
                "parameters": ["columns", "conditions"],
                "expected_result": "empty",
                "category": "duplicates"
            }
        }
    
    def get_template_categories(self) -> List[str]:
        """Get list of available template categories"""
        categories = set()
        for template in self.query_templates.values():
            categories.add(template["category"])
        return sorted(list(categories))
    
    def get_templates_by_category(self, category: str) -> Dict[str, Dict]:
        """Get templates filtered by category"""
        return {
            key: template for key, template in self.query_templates.items()
            if template["category"] == category
        }
    
    def validate_sql_query(self, query: str) -> Dict[str, Any]:
        """Validate SQL query syntax and security"""
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "security_issues": []
        }
        
        try:
            # Parse the SQL query
            parsed = sqlparse.parse(query)
            if not parsed:
                validation_result["is_valid"] = False
                validation_result["errors"].append("Invalid SQL syntax")
                return validation_result
            
            # Check for dangerous SQL operations
            dangerous_keywords = [
                'DROP', 'DELETE', 'UPDATE', 'INSERT', 'CREATE', 'ALTER', 
                'TRUNCATE', 'EXEC', 'EXECUTE', 'MERGE'
            ]
            
            query_upper = query.upper()
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    validation_result["security_issues"].append(
                        f"Potentially dangerous SQL keyword detected: {keyword}"
                    )
            
            # Check for required SELECT statement
            if not query_upper.strip().startswith('SELECT'):
                validation_result["warnings"].append(
                    "Query should start with SELECT for data validation"
                )
            
            # Check for table name placeholder
            if '{table_name}' not in query:
                validation_result["warnings"].append(
                    "Query should include {table_name} placeholder"
                )
                
        except Exception as e:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"SQL parsing error: {str(e)}")
        
        return validation_result
    
    def build_expectation_config(
        self, 
        name: str,
        sql_query: str, 
        expected_result_type: str = "empty",
        expected_value: Union[int, float, None] = None,
        description: str = "",
        tolerance: float = 0.0
    ) -> Dict[str, Any]:
        """Build expectation configuration for custom SQL query"""
        
        config = {
            'expectation_type': self.expectation_type,
            'kwargs': {
                'name': name,
                'query': sql_query,
                'expected_result_type': expected_result_type,
                'description': description,
                'tolerance': tolerance
            }
        }
        
        if expected_value is not None:
            config['kwargs']['expected_value'] = expected_value
            
        return config
    
    def execute_sql_query(
        self, 
        data: pd.DataFrame, 
        sql_query: str, 
        table_name: str = "data_table"
    ) -> pd.DataFrame:
        """Execute SQL query against pandas DataFrame using pandasql"""
        try:
            import pandasql as ps
            
            # Replace table name placeholder
            formatted_query = sql_query.replace('{table_name}', table_name)
            
            # Create a local environment with the data
            local_env = {table_name: data}
            
            # Execute the query
            result = ps.sqldf(formatted_query, local_env)
            return result
            
        except ImportError:
            st.error("pandasql library is required for custom SQL expectations. Please install it with: pip install pandasql")
            return pd.DataFrame()
        except Exception as e:
            st.error(f"Error executing SQL query: {str(e)}")
            return pd.DataFrame()
    
    def _build_failing_rows_query(self, original_query: str) -> Optional[str]:
        """Convert a violation count query to a query that returns the actual failing rows.

        Note: We intentionally avoid window functions like ROW_NUMBER() for maximum SQLite/pandasql
        compatibility. The caller can still map rows back to the original data by value matching.
        """
        try:
            # Parse the original query to extract the WHERE condition
            query_upper = original_query.upper().strip()
            
            # Look for the WHERE clause
            if "WHERE NOT (" in query_upper:
                # Extract the condition inside WHERE NOT (...)
                where_start = query_upper.find("WHERE NOT (")
                where_clause = original_query[where_start + len("WHERE NOT ("):]
                
                # Find the matching closing parenthesis
                paren_count = 1
                condition_end = 0
                for i, char in enumerate(where_clause):
                    if char == '(':
                        paren_count += 1
                    elif char == ')':
                        paren_count -= 1
                        if paren_count == 0:
                            condition_end = i
                            break
                
                if condition_end > 0:
                    # Extract the condition (remove the NOT part)
                    condition = where_clause[:condition_end]
                    # Build a query to return the actual failing rows (no window function)
                    failing_rows_query = (
                        "SELECT *\nFROM {table_name}\nWHERE NOT (" + condition + ")"
                    )
                    return failing_rows_query.strip()
            
            elif "WHERE " in query_upper:
                # For other WHERE patterns, try to extract the condition
                where_start = query_upper.find("WHERE ")
                where_clause = original_query[where_start + 6:].strip()
                
                # For COUNT(*) queries that find violations, the WHERE clause directly identifies the violating rows
                # So we can use the same WHERE clause to get the actual failing rows
                failing_rows_query = (
                    "SELECT *\nFROM {table_name}\nWHERE " + where_clause
                )
                return failing_rows_query.strip()
                
        except Exception as e:
            # Log the error for debugging
            print(f"Error building failing rows query: {str(e)}")
            pass
        
        return None
    
    def validate_expectation(
        self, 
        data: pd.DataFrame, 
        expectation_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate data against custom SQL expectation"""
        
        kwargs = expectation_config.get('kwargs', {})
        query = kwargs.get('query', '')
        expected_result_type = kwargs.get('expected_result_type', 'empty')
        expected_value = kwargs.get('expected_value')
        tolerance = kwargs.get('tolerance', 0.0)
        name = kwargs.get('name', 'Custom SQL Expectation')
        
        try:
            # Execute the main query to get violation count
            result_df = self.execute_sql_query(data, query)

            # Derive failing rows directly from the WHERE clause whenever possible
            failing_rows_df = pd.DataFrame()
            try:
                failing_rows_query = self._build_failing_rows_query(query)
                if failing_rows_query:
                    failing_rows_df = self.execute_sql_query(data, failing_rows_query)
            except Exception:
                # Fall back to empty failing rows if we can't derive them
                failing_rows_df = pd.DataFrame()
            
            if result_df.empty:
                return {
                    "success": False,
                    "expectation_config": expectation_config,
                    "result": {
                        "element_count": len(data),
                        "unexpected_count": 1,
                        "unexpected_percent": 100.0,
                        "partial_unexpected_list": [],
                        "unexpected_index_list": []
                    },
                    "exception_info": {"exception_message": "Query returned no results"}
                }
            
            # Evaluate result based on expected type
            success = False
            violation_count = 0
            
            if expected_result_type == "empty":
                # Expect no violations (result should be empty or have zero violation_count)
                if 'violation_count' in result_df.columns:
                    violation_count = int(result_df['violation_count'].iloc[0])
                    success = violation_count == 0
                else:
                    success = len(result_df) == 0
                    violation_count = len(result_df)
                    
            elif expected_result_type == "non_empty":
                # Expect violations to exist
                success = len(result_df) > 0
                violation_count = 0 if success else 1
                
            elif expected_result_type == "count_equals":
                # Expect specific count
                if 'violation_count' in result_df.columns:
                    actual_count = int(result_df['violation_count'].iloc[0])
                else:
                    actual_count = len(result_df)
                
                if expected_value is not None:
                    success = abs(actual_count - expected_value) <= tolerance
                    violation_count = abs(actual_count - expected_value) if not success else 0
                else:
                    success = False
                    violation_count = 1
                    
            elif expected_result_type == "count_between":
                # Expect count within range
                if 'violation_count' in result_df.columns:
                    actual_count = int(result_df['violation_count'].iloc[0])
                else:
                    actual_count = len(result_df)
                
                min_val = kwargs.get('min_value', 0)
                max_val = kwargs.get('max_value', float('inf'))
                success = min_val <= actual_count <= max_val
                violation_count = 0 if success else abs(actual_count - min_val) if actual_count < min_val else abs(actual_count - max_val)
            
            # Calculate percentage
            total_elements = len(data)
            unexpected_percent = (violation_count / total_elements * 100) if total_elements > 0 else 0
            
            # Prepare failing rows data for detailed results
            partial_unexpected_list = []
            unexpected_index_list = []
            
            if not failing_rows_df.empty and violation_count > 0:
                display_failing_rows = failing_rows_df
                unexpected_index_list = []
                
                # Convert failing rows to list of dictionaries for partial_unexpected_list
                partial_unexpected_list = display_failing_rows.head(100).to_dict('records')  # Limit to first 100 for performance
            
            result = {
                "element_count": total_elements,
                "unexpected_count": violation_count,
                "unexpected_percent": unexpected_percent,
                "partial_unexpected_list": partial_unexpected_list,
                "unexpected_index_list": unexpected_index_list[:100],  # Limit to first 100 indices
                "query_result": result_df.to_dict('records')[:10]  # First 10 rows for debugging
            }
            
            # Add full failing rows data for download if available
            if not failing_rows_df.empty:
                result["unexpected_rows_data"] = failing_rows_df.to_dict('records')
            
            return {
                "success": success,
                "expectation_config": expectation_config,
                "result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "expectation_config": expectation_config,
                "result": {
                    "element_count": len(data),
                    "unexpected_count": len(data),
                    "unexpected_percent": 100.0,
                    "partial_unexpected_list": [],
                    "unexpected_index_list": []
                },
                "exception_info": {"exception_message": f"Custom SQL validation failed: {str(e)}"}
            }


class SQLQueryBuilder:
    """Helper class for building SQL queries with UI components"""
    
    @staticmethod
    def render_column_selector(
        data: pd.DataFrame, 
        label: str, 
        key: str, 
        multi: bool = False,
        help_text: str = None
    ) -> Union[str, List[str]]:
        """Render column selector for SQL query building"""
        columns = list(data.columns)
        
        if multi:
            return st.multiselect(
                label, 
                options=columns, 
                key=key,
                help=help_text
            )
        else:
            return st.selectbox(
                label, 
                options=[""] + columns, 
                key=key,
                help=help_text
            )
    
    @staticmethod
    def render_operator_selector(label: str, key: str, operators: List[str]) -> str:
        """Render operator selector"""
        return st.selectbox(label, options=operators, key=key)
    
    @staticmethod
    def render_value_input(
        label: str, 
        key: str, 
        input_type: str = "text",
        help_text: str = None
    ) -> Any:
        """Render value input based on type"""
        if input_type == "number":
            return st.number_input(label, key=key, help=help_text)
        elif input_type == "date":
            return st.date_input(label, key=key, help=help_text)
        else:
            return st.text_input(label, key=key, help=help_text)
    
    @staticmethod
    def build_query_from_template(template: str, parameters: Dict[str, Any]) -> str:
        """Build SQL query from template and parameters"""
        query = template
        for param, value in parameters.items():
            placeholder = f"{{{param}}}"
            query = query.replace(placeholder, str(value))
        return query