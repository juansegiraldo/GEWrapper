#!/usr/bin/env python3
"""
Test script to verify the correct Sales salary validation
"""

import pandas as pd
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.custom_sql_expectations import CustomSQLExpectation

def test_correct_validation():
    """Test the correct Sales salary validation"""
    
    # Load the test data
    data = pd.read_csv('sample_data/test_data_with_issues.csv')
    print(f"Loaded data with {len(data)} rows")
    
    # Create the custom SQL expectation
    custom_sql = CustomSQLExpectation()
    
    # CORRECT SQL query (using active = 1 for boolean True)
    sql_query = """
    SELECT COUNT(*) as violation_count 
    FROM {table_name} 
    WHERE department = 'Sales' AND active = 1 AND salary < 40000
    """
    
    print(f"\nTesting CORRECT SQL query:")
    print(sql_query)
    
    # Test the query execution
    try:
        result_df = custom_sql.execute_sql_query(data, sql_query)
        print(f"\nQuery execution result:")
        print(result_df)
        
        if not result_df.empty and 'violation_count' in result_df.columns:
            violation_count = result_df['violation_count'].iloc[0]
            print(f"Violation count: {violation_count}")
            
            if violation_count == 1:
                print("✅ SUCCESS: Found exactly 1 violation (Frank Miller)")
            else:
                print(f"❌ UNEXPECTED: Found {violation_count} violations instead of 1")
        else:
            print("Query returned no results or unexpected format")
            
    except Exception as e:
        print(f"❌ Error executing query: {str(e)}")
    
    # Create expectation config
    expectation_config = {
        'expectation_type': 'expect_custom_sql_query_to_return_expected_result',
        'kwargs': {
            'name': 'Sales Active Employee Salary Validation',
            'query': sql_query,
            'expected_result_type': 'empty',
            'description': 'Ensures that active Sales department employees have a salary equal to or greater than 40000',
            'tolerance': 0.0
        }
    }
    
    # Test the full validation
    print(f"\nTesting full validation:")
    try:
        validation_result = custom_sql.validate_expectation(data, expectation_config)
        print(f"Validation result: {validation_result}")
        
        if validation_result.get('success', False):
            print("✅ Validation PASSED - No violations found")
        else:
            print("❌ Validation FAILED - Violations found")
            unexpected_count = validation_result.get('result', {}).get('unexpected_count', 'N/A')
            print(f"Unexpected count: {unexpected_count}")
            
    except Exception as e:
        print(f"❌ Error in validation: {str(e)}")

if __name__ == "__main__":
    test_correct_validation()
