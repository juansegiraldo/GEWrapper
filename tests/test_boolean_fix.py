#!/usr/bin/env python3
"""
Test script to verify the boolean condition fix
"""

import pandas as pd
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.sql_query_builder import SQLQueryBuilderComponent
from utils.data_processing import DataProcessor

def test_boolean_fix():
    """Test the boolean condition fix"""
    
    print("=== Testing Boolean Condition Fix ===")
    
    # Load data using the app's DataProcessor
    with open('sample_data/test_data_with_issues.csv', 'rb') as f:
        class MockUploadedFile:
            def __init__(self, content):
                self.content = content
                self.name = 'test_data_with_issues.csv'
                self.size = len(content)
            
            def read(self):
                return self.content
        
        mock_file = MockUploadedFile(f.read())
    
    data = DataProcessor.load_file(mock_file)
    print(f"Data shape: {data.shape}")
    print(f"Data types: {dict(data.dtypes)}")
    
    # Create SQL query builder
    sql_builder = SQLQueryBuilderComponent()
    
    # Test different SQL queries
    test_queries = [
        # Original query with active = 1
        """
        SELECT COUNT(*) as violation_count
        FROM {table_name}
        WHERE department = 'Sales' AND active = 1 AND salary < 40000
        """,
        
        # Query with active = True
        """
        SELECT COUNT(*) as violation_count
        FROM {table_name}
        WHERE department = 'Sales' AND active = True AND salary < 40000
        """,
        
        # Query with active = 'true'
        """
        SELECT COUNT(*) as violation_count
        FROM {table_name}
        WHERE department = 'Sales' AND active = 'true' AND salary < 40000
        """
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}:")
        print(f"Original query: {query.strip()}")
        
        # Apply the fix
        fixed_query = sql_builder._fix_boolean_conditions(query, data)
        print(f"Fixed query: {fixed_query.strip()}")
        
        # Test the query execution
        from components.custom_sql_expectations import CustomSQLExpectation
        custom_sql = CustomSQLExpectation()
        
        try:
            result = custom_sql.execute_sql_query(data, fixed_query)
            if not result.empty and 'violation_count' in result.columns:
                violation_count = result['violation_count'].iloc[0]
                print(f"Result: {violation_count} violations")
            else:
                print(f"Result: No violation_count column found")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_boolean_fix()
