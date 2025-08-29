#!/usr/bin/env python3
"""
Test script to verify that the row count expectation validation fix works correctly.
This script tests the manual validation logic for the expect_table_row_count_to_be_between expectation.
"""

import pandas as pd
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.ge_helpers import GEHelpers

def test_row_count_expectation():
    """Test the row count expectation validation"""
    print("🧪 Testing row count expectation validation...")
    
    # Create test data with 20 rows
    test_data = pd.DataFrame({
        'id': range(1, 21),
        'name': [f'Person_{i}' for i in range(1, 21)],
        'age': [25 + i for i in range(20)],
        'email': [f'person{i}@example.com' for i in range(1, 21)]
    })
    
    print(f"📊 Test data shape: {test_data.shape}")
    
    # Create GE helpers instance
    ge_helpers = GEHelpers()
    
    # Create a test expectation suite
    from great_expectations.core import ExpectationSuite
    
    try:
        suite = ExpectationSuite()
        suite.name = "test_suite"
    except TypeError:
        suite = ExpectationSuite(expectation_suite_name="test_suite")
    
    # Add the row count expectation
    row_count_config = {
        'expectation_type': 'expect_table_row_count_to_be_between',
        'kwargs': {
            'min_value': 20,
            'max_value': 20
        }
    }
    
    success = ge_helpers.add_expectation_to_suite(suite, row_count_config)
    print(f"✅ Added expectation to suite: {success}")
    
    # Run validation
    print("🔍 Running validation...")
    validation_result = ge_helpers.validate_data(test_data, suite)
    
    if validation_result:
        print("📋 Validation Results:")
        print(f"  - Results count: {len(validation_result.get('results', []))}")
        
        for i, result in enumerate(validation_result.get('results', [])):
            exp_config = result.get('expectation_config', {})
            exp_type = exp_config.get('expectation_type', 'Unknown')
            success = result.get('success', False)
            result_data = result.get('result', {})
            
            print(f"  Result {i+1}:")
            print(f"    - Type: {exp_type}")
            print(f"    - Success: {success}")
            print(f"    - Element count: {result_data.get('element_count', 'N/A')}")
            print(f"    - Unexpected count: {result_data.get('unexpected_count', 'N/A')}")
            print(f"    - Unexpected percent: {result_data.get('unexpected_percent', 'N/A')}")
        
        # Check statistics
        stats = validation_result.get('statistics', {})
        print(f"📊 Statistics:")
        print(f"  - Total expectations: {stats.get('evaluated_expectations', 0)}")
        print(f"  - Successful: {stats.get('successful_expectations', 0)}")
        print(f"  - Unsuccessful: {stats.get('unsuccessful_expectations', 0)}")
        print(f"  - Success percent: {stats.get('success_percent', 0)}%")
        
        # Verify the fix worked
        if stats.get('successful_expectations', 0) == 1 and stats.get('unsuccessful_expectations', 0) == 0:
            print("✅ SUCCESS: Row count expectation validation is working correctly!")
            return True
        else:
            print("❌ FAILURE: Row count expectation validation is still inconsistent!")
            return False
    else:
        print("❌ FAILURE: Validation returned None!")
        return False

def test_multiple_expectations():
    """Test multiple expectations including the problematic ones"""
    print("\n🧪 Testing multiple expectations...")
    
    # Create test data
    test_data = pd.DataFrame({
        'id': range(1, 21),
        'name': [f'Person_{i}' for i in range(1, 21)],
        'age': [25 + i for i in range(20)],
        'email': [f'person{i}@example.com' for i in range(1, 21)]
    })
    
    # Create GE helpers instance
    ge_helpers = GEHelpers()
    
    # Create a test expectation suite
    from great_expectations.core import ExpectationSuite
    
    try:
        suite = ExpectationSuite()
        suite.name = "test_suite_multiple"
    except TypeError:
        suite = ExpectationSuite(expectation_suite_name="test_suite_multiple")
    
    # Add multiple expectations
    expectations = [
        {
            'expectation_type': 'expect_table_row_count_to_be_between',
            'kwargs': {'min_value': 20, 'max_value': 20}
        },
        {
            'expectation_type': 'expect_column_values_to_not_be_null',
            'kwargs': {'column': 'id'}
        },
        {
            'expectation_type': 'expect_column_values_to_be_unique',
            'kwargs': {'column': 'id'}
        },
        {
            'expectation_type': 'expect_column_values_to_match_regex',
            'kwargs': {'column': 'email', 'regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'}
        }
    ]
    
    for exp_config in expectations:
        success = ge_helpers.add_expectation_to_suite(suite, exp_config)
        print(f"✅ Added {exp_config['expectation_type']}: {success}")
    
    # Run validation
    print("🔍 Running validation with multiple expectations...")
    validation_result = ge_helpers.validate_data(test_data, suite)
    
    if validation_result:
        stats = validation_result.get('statistics', {})
        print(f"📊 Multiple expectations results:")
        print(f"  - Total: {stats.get('evaluated_expectations', 0)}")
        print(f"  - Successful: {stats.get('successful_expectations', 0)}")
        print(f"  - Unsuccessful: {stats.get('unsuccessful_expectations', 0)}")
        print(f"  - Success percent: {stats.get('success_percent', 0)}%")
        
        # All expectations should pass with this test data
        if stats.get('successful_expectations', 0) == 4 and stats.get('unsuccessful_expectations', 0) == 0:
            print("✅ SUCCESS: All expectations passed correctly!")
            return True
        else:
            print("❌ FAILURE: Some expectations failed unexpectedly!")
            return False
    else:
        print("❌ FAILURE: Validation returned None!")
        return False

if __name__ == "__main__":
    print("🚀 Starting validation fix tests...")
    
    test1_passed = test_row_count_expectation()
    test2_passed = test_multiple_expectations()
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED! The validation fix is working correctly.")
    else:
        print("\n💥 SOME TESTS FAILED! The validation fix needs more work.")
        sys.exit(1)
