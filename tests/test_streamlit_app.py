#!/usr/bin/env python3
"""
Test script to simulate Streamlit app environment and test SQL query execution
"""

import pandas as pd
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_processing import DataProcessor
from components.custom_sql_expectations import CustomSQLExpectation

def test_streamlit_app_simulation():
    """Simulate the Streamlit app environment and test SQL query execution"""
    
    print("=== Testing Streamlit App Simulation ===")
    
    # Simulate file upload like in the app
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
    
    # Load data using the app's DataProcessor
    print("\n1. Loading data with app's DataProcessor:")
    data = DataProcessor.load_file(mock_file)
    print(f"   Data shape: {data.shape}")
    print(f"   Data types: {dict(data.dtypes)}")
    print(f"   Active column unique values: {data['active'].unique()}")
    
    # Show Sales employees
    sales_employees = data[data['department'] == 'Sales']
    print(f"\n2. Sales employees:")
    for _, row in sales_employees.iterrows():
        print(f"   - {row['name']}: active={row['active']}, salary={row['salary']}")
    
    # Test the exact SQL query from the image
    print(f"\n3. Testing the exact SQL query from the image:")
    sql_query = """
    SELECT COUNT(*) as violation_count
    FROM {table_name}
    WHERE department = 'Sales' AND active = 1 AND salary < 40000
    """
    print(f"   SQL Query: {sql_query.strip()}")
    
    # Execute using the app's CustomSQLExpectation
    custom_sql = CustomSQLExpectation()
    try:
        result = custom_sql.execute_sql_query(data, sql_query)
        print(f"   Result DataFrame: {result}")
        if not result.empty and 'violation_count' in result.columns:
            violation_count = result['violation_count'].iloc[0]
            print(f"   Violation count: {violation_count}")
        else:
            print(f"   No violation_count column found")
    except Exception as e:
        print(f"   Error: {str(e)}")
    
    # Test with different active conditions
    print(f"\n4. Testing different active conditions:")
    
    conditions = [
        ("active = 1", "active = 1"),
        ("active = True", "active = True"),
        ("active = 'true'", "active = 'true'"),
        ("active = 0", "active = 0"),
        ("active = False", "active = False"),
        ("active = 'false'", "active = 'false'")
    ]
    
    for condition_name, condition in conditions:
        test_query = f"""
        SELECT COUNT(*) as violation_count
        FROM {{table_name}}
        WHERE department = 'Sales' AND {condition} AND salary < 40000
        """
        try:
            result = custom_sql.execute_sql_query(data, test_query)
            if not result.empty and 'violation_count' in result.columns:
                violation_count = result['violation_count'].iloc[0]
                print(f"   {condition_name}: {violation_count}")
            else:
                print(f"   {condition_name}: No result")
        except Exception as e:
            print(f"   {condition_name}: Error - {str(e)}")
    
    # Test manual pandas filtering for comparison
    print(f"\n5. Manual pandas filtering for comparison:")
    
    # Test with active = 1 (integer)
    manual_result_1 = data[
        (data['department'] == 'Sales') & 
        (data['active'] == 1) & 
        (data['salary'] < 40000)
    ]
    print(f"   Manual filter with active=1: {len(manual_result_1)} rows")
    
    # Test with active = True (boolean)
    manual_result_2 = data[
        (data['department'] == 'Sales') & 
        (data['active'] == True) & 
        (data['salary'] < 40000)
    ]
    print(f"   Manual filter with active=True: {len(manual_result_2)} rows")
    
    # Test with active = 'true' (string)
    manual_result_3 = data[
        (data['department'] == 'Sales') & 
        (data['active'] == 'true') & 
        (data['salary'] < 40000)
    ]
    print(f"   Manual filter with active='true': {len(manual_result_3)} rows")

if __name__ == "__main__":
    test_streamlit_app_simulation()
