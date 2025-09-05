#!/usr/bin/env python3
"""
Windows-Compatible Simple QA Test Runner

Runs basic QA tests and outputs to CSV without any Unicode issues.
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
from typing import Dict, List, Any
import random

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.ge_helpers import GEHelpers
from components.custom_sql_expectations import CustomSQLExpectation


class SimpleDataGenerator:
    """Generate test data without external dependencies"""
    
    def __init__(self):
        random.seed(42)
        np.random.seed(42)
    
    def generate_clean_data(self, rows=100):
        """Generate clean test data"""
        data = {
            'id': range(1, rows + 1),
            'name': [f'Person_{i}' for i in range(1, rows + 1)],
            'email': [f'user{i}@example.com' for i in range(1, rows + 1)],
            'age': np.random.randint(18, 80, rows),
            'salary': np.random.normal(50000, 15000, rows).round(2),
            'category': np.random.choice(['A', 'B', 'C', 'D'], rows),
        }
        return pd.DataFrame(data)
    
    def generate_data_with_nulls(self, rows=100):
        """Generate data with null values"""
        df = self.generate_clean_data(rows)
        
        # Add nulls to some records
        null_indices = np.random.choice(rows, size=int(rows * 0.1), replace=False)
        df.loc[null_indices, 'name'] = None
        
        return df
    
    def generate_data_with_duplicates(self, rows=100):
        """Generate data with duplicate IDs"""
        df = self.generate_clean_data(rows)
        
        # Add duplicate IDs
        duplicate_indices = np.random.choice(rows, size=int(rows * 0.05), replace=False)
        df.loc[duplicate_indices, 'id'] = 1  # Make them all ID 1
        
        return df


class SimpleQATester:
    """Simple QA tester"""
    
    def __init__(self):
        self.ge_helpers = GEHelpers()
        self.data_gen = SimpleDataGenerator()
        self.results = []
        
        # Common expectation types to test
        self.expectation_types = [
            "expect_column_values_to_not_be_null",
            "expect_column_values_to_be_unique",
            "expect_table_row_count_to_be_between",
            "expect_column_values_to_be_in_set",
            "expect_column_values_to_be_between"
        ]
    
    def run_tests(self):
        """Run all tests"""
        print("Running QA Tests...")
        print(f"Testing {len(self.expectation_types)} expectation types")
        print("-" * 50)
        
        for exp_type in self.expectation_types:
            print(f"\nTesting: {exp_type}")
            self.test_expectation_type(exp_type)
        
        return self.results
    
    def test_expectation_type(self, exp_type):
        """Test one expectation type with multiple scenarios"""
        
        scenarios = {
            'clean_data': self.data_gen.generate_clean_data(),
            'with_nulls': self.data_gen.generate_data_with_nulls(),
            'with_duplicates': self.data_gen.generate_data_with_duplicates()
        }
        
        for scenario_name, data in scenarios.items():
            try:
                print(f"  {scenario_name}...", end=" ")
                
                # Create expectation config
                config = self.create_expectation_config(exp_type, data)
                
                if config:
                    # Test the expectation (simplified simulation)
                    success = self.test_expectation(exp_type, scenario_name, data, config)
                    
                    self.results.append({
                        'expectation_type': exp_type,
                        'test_scenario': scenario_name,
                        'test_passed': success,
                        'data_rows': len(data),
                        'data_columns': len(data.columns)
                    })
                    
                    print("PASS" if success else "FAIL")
                else:
                    print("SKIP (no config)")
                    
            except Exception as e:
                print(f"ERROR: {str(e)}")
                self.results.append({
                    'expectation_type': exp_type,
                    'test_scenario': scenario_name,
                    'test_passed': False,
                    'data_rows': len(data) if 'data' in locals() else 0,
                    'data_columns': len(data.columns) if 'data' in locals() else 0,
                    'error_message': str(e)
                })
    
    def create_expectation_config(self, exp_type, data):
        """Create expectation configuration"""
        
        if exp_type == "expect_column_values_to_not_be_null":
            return {
                'expectation_type': exp_type,
                'kwargs': {'column': 'name'}
            }
        
        elif exp_type == "expect_column_values_to_be_unique":
            return {
                'expectation_type': exp_type,
                'kwargs': {'column': 'id'}
            }
        
        elif exp_type == "expect_table_row_count_to_be_between":
            return {
                'expectation_type': exp_type,
                'kwargs': {
                    'min_value': max(1, len(data) - 10),
                    'max_value': len(data) + 10
                }
            }
        
        elif exp_type == "expect_column_values_to_be_in_set":
            return {
                'expectation_type': exp_type,
                'kwargs': {
                    'column': 'category',
                    'value_set': ['A', 'B', 'C', 'D']
                }
            }
        
        elif exp_type == "expect_column_values_to_be_between":
            return {
                'expectation_type': exp_type,
                'kwargs': {
                    'column': 'age',
                    'min_value': 0,
                    'max_value': 120
                }
            }
        
        return None
    
    def test_expectation(self, exp_type, scenario, data, config):
        """Simple expectation testing logic"""
        
        try:
            kwargs = config.get('kwargs', {})
            
            if exp_type == "expect_column_values_to_not_be_null":
                column = kwargs.get('column')
                if column in data.columns:
                    null_count = data[column].isnull().sum()
                    # Clean data should pass, data with nulls should fail
                    if scenario == 'clean_data':
                        return null_count == 0
                    elif scenario == 'with_nulls':
                        return null_count == 0  # This should fail
                    else:
                        return null_count == 0
            
            elif exp_type == "expect_column_values_to_be_unique":
                column = kwargs.get('column')
                if column in data.columns:
                    unique_count = data[column].nunique()
                    total_count = len(data[column].dropna())
                    # Clean data should pass, data with duplicates should fail
                    if scenario == 'clean_data':
                        return unique_count == total_count
                    elif scenario == 'with_duplicates':
                        return unique_count == total_count  # This should fail
                    else:
                        return unique_count == total_count
            
            elif exp_type == "expect_table_row_count_to_be_between":
                row_count = len(data)
                min_val = kwargs.get('min_value', 0)
                max_val = kwargs.get('max_value', float('inf'))
                return min_val <= row_count <= max_val
            
            elif exp_type == "expect_column_values_to_be_in_set":
                column = kwargs.get('column')
                value_set = set(kwargs.get('value_set', []))
                if column in data.columns:
                    data_values = set(data[column].dropna())
                    return data_values.issubset(value_set)
            
            elif exp_type == "expect_column_values_to_be_between":
                column = kwargs.get('column')
                min_val = kwargs.get('min_value', float('-inf'))
                max_val = kwargs.get('max_value', float('inf'))
                if column in data.columns:
                    out_of_range = ((data[column] < min_val) | (data[column] > max_val)).sum()
                    return out_of_range == 0
            
            return True  # Default pass
            
        except Exception:
            return False
    
    def save_results_to_csv(self):
        """Save results to CSV"""
        if not self.results:
            print("No results to save")
            return
        
        df = pd.DataFrame(self.results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simple_qa_results_{timestamp}.csv"
        df.to_csv(filename, index=False)
        
        print(f"\nResults saved to: {filename}")
        
        # Print summary
        total_tests = len(df)
        passed_tests = df['test_passed'].sum()
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\nSUMMARY:")
        print(f"Total tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success rate: {success_rate:.1f}%")
        
        # Show failures
        failed_tests = df[df['test_passed'] == False]
        if not failed_tests.empty:
            print(f"\nFAILED TESTS:")
            for _, row in failed_tests.iterrows():
                print(f"  {row['expectation_type']} - {row['test_scenario']}")


def main():
    """Main function"""
    print("Simple QA Test Runner")
    print("=" * 30)
    
    tester = SimpleQATester()
    tester.run_tests()
    tester.save_results_to_csv()
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)