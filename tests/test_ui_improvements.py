#!/usr/bin/env python3
"""
Test script to verify UI improvements in the expectation builder component
"""

import sys
import os
import pandas as pd

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.expectation_builder import ExpectationBuilderComponent

def test_expectation_builder_ui():
    """Test the improved expectation builder UI components"""
    
    # Create sample data
    data = pd.DataFrame({
        'name': ['John', 'Jane', 'Bob', None],
        'age': [25, 30, 35, 40],
        'email': ['john@example.com', 'jane@example.com', 'invalid-email', None],
        'salary': [50000, 60000, 70000, 80000],
        'active': [True, False, True, False]
    })
    
    print("Sample data created successfully")
    print(f"   Shape: {data.shape}")
    print(f"   Columns: {list(data.columns)}")
    
    # Test expectation builder component initialization
    try:
        builder = ExpectationBuilderComponent()
        print("ExpectationBuilderComponent initialized successfully")
    except Exception as e:
        print(f"Failed to initialize ExpectationBuilderComponent: {e}")
        return False
    
    # Test template application
    try:
        builder._apply_template("Basic Data Quality", data)
        print("Template application works correctly")
    except Exception as e:
        print(f"Template application failed: {e}")
        return False
    
    # Test expectation config building
    try:
        config = builder._build_expectation_config("expect_column_values_to_not_be_null", data)
        if config and config.get('expectation_type') == "expect_column_values_to_not_be_null":
            print("Expectation config building works correctly")
        else:
            print("Expectation config building failed")
            return False
    except Exception as e:
        print(f"Expectation config building failed: {e}")
        return False
    
    # Test import processing
    try:
        # Create a mock import file
        import json
        mock_import_data = {
            'suite_name': 'test_suite',
            'expectations': [
                {
                    'expectation_type': 'expect_column_values_to_not_be_null',
                    'kwargs': {'column': 'name'}
                }
            ]
        }
        
        # Simulate file upload object
        class MockUploadedFile:
            def __init__(self, data):
                self.data = json.dumps(data).encode()
                self.name = "test_suite.json"
            
            def seek(self, pos):
                pass
            
            def read(self):
                return self.data.decode()
        
        mock_file = MockUploadedFile(mock_import_data)
        builder._process_import(mock_file)
        print("Import processing works correctly")
    except Exception as e:
        print(f"Import processing failed: {e}")
        return False
    
    print("\nAll UI improvement tests passed!")
    return True

if __name__ == "__main__":
    success = test_expectation_builder_ui()
    sys.exit(0 if success else 1)
