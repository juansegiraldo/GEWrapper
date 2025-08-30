#!/usr/bin/env python3
"""
Test script to verify how the app loads data and affects SQL queries
"""

import pandas as pd
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_processing import DataProcessor
from components.custom_sql_expectations import CustomSQLExpectation

def test_app_data_loading():
    """Test how the app loads data and affects SQL queries"""
    
    print("=== Testing App Data Loading vs Direct CSV Reading ===")
    
    # Test 1: Direct CSV reading (like our standalone test)
    print("\n1. Direct CSV reading:")
    data_direct = pd.read_csv('sample_data/test_data_with_issues.csv')
    print(f"   Data types: {dict(data_direct.dtypes)}")
    print(f"   Active column unique values: {data_direct['active'].unique()}")
    print(f"   Active column type: {type(data_direct['active'].iloc[0])}")
    
    # Test 2: App data loading (like the Streamlit app)
    print("\n2. App data loading:")
    # Simulate file upload
    with open('sample_data/test_data_with_issues.csv', 'rb') as f:
        # Create a mock uploaded file object
        class MockUploadedFile:
            def __init__(self, content):
                self.content = content
                self.name = 'test_data_with_issues.csv'
                self.size = len(content)
            
            def read(self):
                return self.content
        
        mock_file = MockUploadedFile(f.read())
    
    data_app = DataProcessor.load_file(mock_file)
    print(f"   Data types: {dict(data_app.dtypes)}")
    print(f"   Active column unique values: {data_app['active'].unique()}")
    print(f"   Active column type: {type(data_app['active'].iloc[0])}")
    
    # Test 3: SQL queries on both datasets
    print("\n3. SQL Query Results:")
    custom_sql = CustomSQLExpectation()
    
    sql_query = """
    SELECT COUNT(*) as violation_count 
    FROM {table_name} 
    WHERE department = 'Sales' AND active = 1 AND salary < 40000
    """
    
    print(f"   SQL Query: {sql_query.strip()}")
    
    # Test on direct CSV data
    result_direct = custom_sql.execute_sql_query(data_direct, sql_query)
    print(f"   Direct CSV result: {result_direct['violation_count'].iloc[0] if not result_direct.empty else 'No result'}")
    
    # Test on app-loaded data
    result_app = custom_sql.execute_sql_query(data_app, sql_query)
    print(f"   App-loaded result: {result_app['violation_count'].iloc[0] if not result_app.empty else 'No result'}")
    
    # Test 4: Try different SQL conditions for app-loaded data
    print("\n4. Testing different SQL conditions for app-loaded data:")
    
    # Test with active = True (boolean)
    sql_query_bool = """
    SELECT COUNT(*) as violation_count 
    FROM {table_name} 
    WHERE department = 'Sales' AND active = True AND salary < 40000
    """
    result_bool = custom_sql.execute_sql_query(data_app, sql_query_bool)
    print(f"   active = True: {result_bool['violation_count'].iloc[0] if not result_bool.empty else 'No result'}")
    
    # Test with active = 'true' (string)
    sql_query_string = """
    SELECT COUNT(*) as violation_count 
    FROM {table_name} 
    WHERE department = 'Sales' AND active = 'true' AND salary < 40000
    """
    result_string = custom_sql.execute_sql_query(data_app, sql_query_string)
    print(f"   active = 'true': {result_string['violation_count'].iloc[0] if not result_string.empty else 'No result'}")
    
    # Test with active = 1 (integer)
    sql_query_int = """
    SELECT COUNT(*) as violation_count 
    FROM {table_name} 
    WHERE department = 'Sales' AND active = 1 AND salary < 40000
    """
    result_int = custom_sql.execute_sql_query(data_app, sql_query_int)
    print(f"   active = 1: {result_int['violation_count'].iloc[0] if not result_int.empty else 'No result'}")

if __name__ == "__main__":
    test_app_data_loading()
