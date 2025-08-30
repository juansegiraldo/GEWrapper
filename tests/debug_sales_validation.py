#!/usr/bin/env python3
"""
Debug script for Sales salary validation rule
"""

import pandas as pd
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.custom_sql_expectations import CustomSQLExpectation

def debug_sales_validation():
    """Debug the Sales salary validation rule step by step"""
    
    # Load the test data
    data = pd.read_csv('sample_data/test_data_with_issues.csv')
    print(f"Loaded data with {len(data)} rows")
    print(f"Columns: {list(data.columns)}")
    
    # Show data types
    print(f"\nData types:")
    for col in data.columns:
        print(f"  {col}: {data[col].dtype}")
    
    # Show Sales employees with details
    sales_employees = data[data['department'] == 'Sales']
    print(f"\nSales employees ({len(sales_employees)}):")
    for _, row in sales_employees.iterrows():
        print(f"  - {row['name']}: active='{row['active']}' (type: {type(row['active'])}), salary={row['salary']} (type: {type(row['salary'])})")
    
    # Test different SQL queries
    custom_sql = CustomSQLExpectation()
    
    # Test 1: Original query with active = 1
    print(f"\n=== TEST 1: Original query with active = 1 ===")
    sql_query_1 = """
    SELECT COUNT(*) as violation_count 
    FROM {table_name} 
    WHERE department = 'Sales' AND active = 1 AND salary < 40000
    """
    
    try:
        result_1 = custom_sql.execute_sql_query(data, sql_query_1)
        print(f"Result 1: {result_1}")
        if not result_1.empty:
            print(f"Violation count 1: {result_1['violation_count'].iloc[0]}")
    except Exception as e:
        print(f"Error 1: {str(e)}")
    
    # Test 2: Query with active = 'true'
    print(f"\n=== TEST 2: Query with active = 'true' ===")
    sql_query_2 = """
    SELECT COUNT(*) as violation_count 
    FROM {table_name} 
    WHERE department = 'Sales' AND active = 'true' AND salary < 40000
    """
    
    try:
        result_2 = custom_sql.execute_sql_query(data, sql_query_2)
        print(f"Result 2: {result_2}")
        if not result_2.empty:
            print(f"Violation count 2: {result_2['violation_count'].iloc[0]}")
    except Exception as e:
        print(f"Error 2: {str(e)}")
    
    # Test 3: Query without active condition
    print(f"\n=== TEST 3: Query without active condition ===")
    sql_query_3 = """
    SELECT COUNT(*) as violation_count 
    FROM {table_name} 
    WHERE department = 'Sales' AND salary < 40000
    """
    
    try:
        result_3 = custom_sql.execute_sql_query(data, sql_query_3)
        print(f"Result 3: {result_3}")
        if not result_3.empty:
            print(f"Violation count 3: {result_3['violation_count'].iloc[0]}")
    except Exception as e:
        print(f"Error 3: {str(e)}")
    
    # Test 4: Query that counts ALL rows
    print(f"\n=== TEST 4: Query that counts ALL rows ===")
    sql_query_4 = """
    SELECT COUNT(*) as violation_count 
    FROM {table_name}
    """
    
    try:
        result_4 = custom_sql.execute_sql_query(data, sql_query_4)
        print(f"Result 4: {result_4}")
        if not result_4.empty:
            print(f"Total rows: {result_4['violation_count'].iloc[0]}")
    except Exception as e:
        print(f"Error 4: {str(e)}")
    
    # Test 5: Manual pandas filtering to verify expected results
    print(f"\n=== TEST 5: Manual pandas filtering ===")
    
    # Test with active = 1 (integer)
    manual_result_1 = data[
        (data['department'] == 'Sales') & 
        (data['active'] == 1) & 
        (data['salary'] < 40000)
    ]
    print(f"Manual filter with active=1: {len(manual_result_1)} rows")
    for _, row in manual_result_1.iterrows():
        print(f"  - {row['name']}: active={row['active']}, salary={row['salary']}")
    
    # Test with active = 'true' (string)
    manual_result_2 = data[
        (data['department'] == 'Sales') & 
        (data['active'] == 'true') & 
        (data['salary'] < 40000)
    ]
    print(f"Manual filter with active='true': {len(manual_result_2)} rows")
    for _, row in manual_result_2.iterrows():
        print(f"  - {row['name']}: active={row['active']}, salary={row['salary']}")
    
    # Test with active = True (boolean)
    manual_result_3 = data[
        (data['department'] == 'Sales') & 
        (data['active'] == True) & 
        (data['salary'] < 40000)
    ]
    print(f"Manual filter with active=True: {len(manual_result_3)} rows")
    for _, row in manual_result_3.iterrows():
        print(f"  - {row['name']}: active={row['active']}, salary={row['salary']}")

if __name__ == "__main__":
    debug_sales_validation()
