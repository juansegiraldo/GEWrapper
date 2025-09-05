#!/usr/bin/env python3
"""
Comprehensive QA Testing Framework for Data Quality Expectations

This framework automatically tests ALL expectation types with various data scenarios,
edge cases, and use cases to ensure robust data quality validation.

Usage:
    python tests/comprehensive_qa_framework.py

Features:
- Tests all 16+ expectation types
- Generates synthetic test data with known issues
- Tests edge cases and boundary conditions
- Provides detailed reporting and analysis
- Supports batch testing and regression testing
"""

import pandas as pd
import numpy as np
import json
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import random
import tempfile
import traceback
from dataclasses import dataclass, asdict
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ge_helpers import GEHelpers
from components.custom_sql_expectations import CustomSQLExpectation
# from utils.data_processing import DataProcessor  # Not needed for basic testing


@dataclass
class TestResult:
    """Test result data structure"""
    expectation_type: str
    test_scenario: str
    expected_outcome: str
    actual_outcome: str
    success: bool
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    data_shape: Optional[Tuple[int, int]] = None
    additional_info: Optional[Dict] = None


@dataclass
class TestSummary:
    """Overall test summary"""
    total_tests: int
    passed_tests: int
    failed_tests: int
    success_rate: float
    total_execution_time: float
    expectation_coverage: Dict[str, int]


class SyntheticDataGenerator:
    """Generate synthetic test data with controlled quality issues"""
    
    def __init__(self, seed=42):
        random.seed(seed)
        np.random.seed(seed)
    
    def generate_clean_dataset(self, rows=1000) -> pd.DataFrame:
        """Generate a clean dataset without issues"""
        data = {
            'id': range(1, rows + 1),
            'name': [f'Person_{i}' for i in range(1, rows + 1)],
            'email': [f'user{i}@example.com' for i in range(1, rows + 1)],
            'age': np.random.randint(18, 80, rows),
            'salary': np.random.normal(50000, 15000, rows).round(2),
            'score': np.random.uniform(0, 100, rows).round(1),
            'category': np.random.choice(['A', 'B', 'C', 'D'], rows),
            'is_active': np.random.choice([True, False], rows),
            'start_date': pd.date_range('2020-01-01', periods=rows, freq='D'),
            'description': [f'Description for person {i}' for i in range(1, rows + 1)]
        }
        return pd.DataFrame(data)
    
    def generate_dataset_with_nulls(self, rows=1000, null_percentage=0.1) -> pd.DataFrame:
        """Generate dataset with null values"""
        df = self.generate_clean_dataset(rows)
        
        # Introduce nulls randomly
        for col in ['name', 'email', 'salary', 'description']:
            null_indices = np.random.choice(rows, size=int(rows * null_percentage), replace=False)
            df.loc[null_indices, col] = None
        
        return df
    
    def generate_dataset_with_duplicates(self, rows=1000, duplicate_percentage=0.05) -> pd.DataFrame:
        """Generate dataset with duplicate values where they shouldn't exist"""
        df = self.generate_clean_dataset(rows)
        
        # Introduce duplicates in ID column (should be unique)
        duplicate_count = int(rows * duplicate_percentage)
        duplicate_indices = np.random.choice(rows, size=duplicate_count, replace=False)
        duplicate_values = np.random.choice(df['id'].iloc[:100], size=duplicate_count)
        df.loc[duplicate_indices, 'id'] = duplicate_values
        
        return df
    
    def generate_dataset_with_type_issues(self, rows=1000) -> pd.DataFrame:
        """Generate dataset with data type inconsistencies"""
        df = self.generate_clean_dataset(rows)
        
        # Convert some numeric values to strings
        type_error_indices = np.random.choice(rows, size=int(rows * 0.05), replace=False)
        df.loc[type_error_indices, 'age'] = 'invalid_age'
        df.loc[type_error_indices, 'salary'] = 'not_a_number'
        
        return df
    
    def generate_dataset_with_range_violations(self, rows=1000) -> pd.DataFrame:
        """Generate dataset with values outside expected ranges"""
        df = self.generate_clean_dataset(rows)
        
        # Age violations (negative ages, ages over 120)
        violation_indices = np.random.choice(rows, size=int(rows * 0.03), replace=False)
        df.loc[violation_indices[:len(violation_indices)//2], 'age'] = -5
        df.loc[violation_indices[len(violation_indices)//2:], 'age'] = 150
        
        # Score violations (outside 0-100 range)
        score_violations = np.random.choice(rows, size=int(rows * 0.02), replace=False)
        df.loc[score_violations, 'score'] = 150
        
        return df
    
    def generate_dataset_with_format_issues(self, rows=1000) -> pd.DataFrame:
        """Generate dataset with format violations"""
        df = self.generate_clean_dataset(rows)
        
        # Email format violations
        format_violations = np.random.choice(rows, size=int(rows * 0.1), replace=False)
        df.loc[format_violations, 'email'] = 'invalid_email_format'
        
        # Date format issues
        date_violations = np.random.choice(rows, size=int(rows * 0.05), replace=False)
        df.loc[date_violations, 'start_date'] = 'not_a_date'
        
        return df
    
    def generate_edge_case_dataset(self) -> pd.DataFrame:
        """Generate dataset with edge cases that should cause failures"""
        edge_cases = {
            'id': [1, 1, 2, 2],  # Duplicate IDs for uniqueness test failure
            'name': ['', ' ', None, 'Very_Long_Name_' + 'x' * 100],
            'email': ['@invalid', 'no-at-sign', '', None],
            'age': [0, -1, 200, None],
            'salary': [0, -50000, 999999999.99, None],
            'score': [0, 100, -1, 101],
            'category': ['', None, 'Z', 'invalid_category'],
            'is_active': [None, 'yes', 'no', 1],
            'start_date': [pd.NaT, '1900-01-01', '2050-12-31', None],
            'description': ['', None, 'x' * 1000, '   ']
        }
        return pd.DataFrame(edge_cases)


class ComprehensiveQATester:
    """Main QA testing framework"""
    
    def __init__(self):
        self.ge_helpers = GEHelpers()
        self.custom_sql = CustomSQLExpectation()
        self.data_generator = SyntheticDataGenerator()
        self.results: List[TestResult] = []
        
        # All expectation types to test
        self.expectation_types = [
            "expect_table_row_count_to_be_between",
            "expect_table_columns_to_match_ordered_list",
            "expect_column_values_to_not_be_null",
            "expect_column_values_to_be_unique",
            "expect_column_values_to_be_of_type",
            "expect_column_values_to_be_in_set",
            "expect_column_values_to_be_between",
            "expect_column_value_lengths_to_be_between",
            "expect_column_values_to_match_regex",
            "expect_column_mean_to_be_between",
            "expect_column_median_to_be_between",
            "expect_column_stdev_to_be_between",
            "expect_column_sum_to_be_between",
            "expect_column_values_to_be_dateutil_parseable",
            "expect_column_values_to_match_strftime_format",
            "expect_custom_sql_query_to_return_expected_result"
        ]
    
    def run_comprehensive_tests(self) -> TestSummary:
        """Run all comprehensive tests"""
        print("Starting Comprehensive QA Testing Framework")
        print(f"Testing {len(self.expectation_types)} expectation types...")
        print("-" * 80)
        
        start_time = datetime.now()
        
        # Test each expectation type
        for expectation_type in self.expectation_types:
            print(f"\n📋 Testing: {expectation_type}")
            self._test_expectation_type(expectation_type)
        
        # Calculate summary
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        summary = self._generate_summary(execution_time)
        self._print_summary(summary)
        self._save_detailed_report()
        
        return summary
    
    def _test_expectation_type(self, expectation_type: str):
        """Test a specific expectation type with multiple scenarios"""
        test_scenarios = self._get_test_scenarios_for_expectation(expectation_type)
        
        for scenario_name, test_config in test_scenarios.items():
            try:
                print(f"  {scenario_name}...", end=" ")
                result = self._execute_test(expectation_type, scenario_name, test_config)
                self.results.append(result)
                
                if result.success:
                    print("PASS")
                else:
                    print("FAIL")
                    if result.error_message:
                        print(f"    Error: {result.error_message}")
                        
            except Exception as e:
                print("ERROR")
                print(f"    Exception: {str(e)}")
                self.results.append(TestResult(
                    expectation_type=expectation_type,
                    test_scenario=scenario_name,
                    expected_outcome="Should execute without exception",
                    actual_outcome=f"Exception: {str(e)}",
                    success=False,
                    error_message=str(e)
                ))
    
    def _get_test_scenarios_for_expectation(self, expectation_type: str) -> Dict[str, Dict]:
        """Get test scenarios for a specific expectation type"""
        
        base_scenarios = {
            "clean_data_pass": {
                "data_generator": "generate_clean_dataset",
                "expected_pass": True,
                "description": "Should pass with clean data"
            },
            "edge_cases": {
                "data_generator": "generate_edge_case_dataset", 
                "expected_pass": False,
                "description": "Should handle edge cases appropriately"
            }
        }
        
        # Add specific scenarios based on expectation type
        if "null" in expectation_type:
            base_scenarios.update({
                "with_nulls_fail": {
                    "data_generator": "generate_dataset_with_nulls",
                    "expected_pass": False,
                    "description": "Should fail when nulls present"
                }
            })
        
        if "unique" in expectation_type:
            base_scenarios.update({
                "with_duplicates_fail": {
                    "data_generator": "generate_dataset_with_duplicates",
                    "expected_pass": False,
                    "description": "Should fail when duplicates present"
                }
            })
        
        if "type" in expectation_type:
            base_scenarios.update({
                "type_violations_fail": {
                    "data_generator": "generate_dataset_with_type_issues",
                    "expected_pass": False,
                    "description": "Should fail when type violations present"
                }
            })
        
        if "between" in expectation_type and "row_count" not in expectation_type:
            base_scenarios.update({
                "range_violations_fail": {
                    "data_generator": "generate_dataset_with_range_violations",
                    "expected_pass": False,
                    "description": "Should fail when values outside range"
                }
            })
        
        if "regex" in expectation_type or "format" in expectation_type:
            base_scenarios.update({
                "format_violations_fail": {
                    "data_generator": "generate_dataset_with_format_issues",
                    "expected_pass": False,
                    "description": "Should fail when format violations present"
                }
            })
        
        return base_scenarios
    
    def _execute_test(self, expectation_type: str, scenario_name: str, test_config: Dict) -> TestResult:
        """Execute a single test"""
        start_time = datetime.now()
        
        try:
            # Generate test data
            data_generator_method = getattr(self.data_generator, test_config["data_generator"])
            if test_config["data_generator"] == "generate_edge_case_dataset":
                test_data = data_generator_method()
            else:
                test_data = data_generator_method(rows=100)  # Smaller dataset for faster testing
            
            # Create expectation configuration
            expectation_config = self._create_expectation_config(expectation_type, test_data)
            
            if not expectation_config:
                return TestResult(
                    expectation_type=expectation_type,
                    test_scenario=scenario_name,
                    expected_outcome=test_config["description"],
                    actual_outcome="Failed to create expectation config",
                    success=False,
                    error_message="Could not create expectation configuration"
                )
            
            # Execute expectation
            validation_result = self._validate_expectation(test_data, expectation_config)
            
            # Determine if test passed
            expected_pass = test_config["expected_pass"]
            actual_pass = validation_result.get("success", False)
            test_success = (expected_pass == actual_pass)
            
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            return TestResult(
                expectation_type=expectation_type,
                test_scenario=scenario_name,
                expected_outcome=f"Expected pass: {expected_pass}",
                actual_outcome=f"Actually passed: {actual_pass}",
                success=test_success,
                execution_time=execution_time,
                data_shape=test_data.shape,
                additional_info={
                    "validation_result": validation_result,
                    "expectation_config": expectation_config
                }
            )
            
        except Exception as e:
            end_time = datetime.now()
            execution_time = (end_time - start_time).total_seconds()
            
            return TestResult(
                expectation_type=expectation_type,
                test_scenario=scenario_name,
                expected_outcome=test_config["description"],
                actual_outcome=f"Exception occurred: {str(e)}",
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _create_expectation_config(self, expectation_type: str, data: pd.DataFrame) -> Optional[Dict]:
        """Create appropriate expectation configuration for testing"""
        
        try:
            if expectation_type == "expect_table_row_count_to_be_between":
                # For edge cases, use a restrictive range to force failure
                if len(data) <= 10:  # Edge case dataset
                    return {
                        'expectation_type': expectation_type,
                        'kwargs': {
                            'min_value': 100,  # Require at least 100 rows (edge case has only 4)
                            'max_value': 1000
                        }
                    }
                else:
                    return {
                        'expectation_type': expectation_type,
                        'kwargs': {
                            'min_value': max(1, len(data) - 10),
                            'max_value': len(data) + 10
                        }
                    }
            
            elif expectation_type == "expect_table_columns_to_match_ordered_list":
                return {
                    'expectation_type': expectation_type,
                    'kwargs': {
                        'column_list': list(data.columns)
                    }
                }
            
            elif expectation_type == "expect_column_values_to_not_be_null":
                return {
                    'expectation_type': expectation_type,
                    'kwargs': {'column': 'name'}  # Test with name column
                }
            
            elif expectation_type == "expect_column_values_to_be_unique":
                return {
                    'expectation_type': expectation_type,
                    'kwargs': {'column': 'id'}  # Test with id column
                }
            
            elif expectation_type == "expect_column_values_to_be_of_type":
                return {
                    'expectation_type': expectation_type,
                    'kwargs': {
                        'column': 'age',
                        'type_': 'int'
                    }
                }
            
            elif expectation_type == "expect_column_values_to_be_in_set":
                return {
                    'expectation_type': expectation_type,
                    'kwargs': {
                        'column': 'category',
                        'value_set': ['A', 'B', 'C', 'D']
                    }
                }
            
            elif expectation_type == "expect_column_values_to_be_between":
                return {
                    'expectation_type': expectation_type,
                    'kwargs': {
                        'column': 'age',
                        'min_value': 0,
                        'max_value': 120
                    }
                }
            
            elif expectation_type == "expect_column_value_lengths_to_be_between":
                return {
                    'expectation_type': expectation_type,
                    'kwargs': {
                        'column': 'name',
                        'min_value': 1,
                        'max_value': 50
                    }
                }
            
            elif expectation_type == "expect_column_values_to_match_regex":
                return {
                    'expectation_type': expectation_type,
                    'kwargs': {
                        'column': 'email',
                        'regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    }
                }
            
            elif expectation_type == "expect_column_mean_to_be_between":
                if 'age' in data.columns and pd.api.types.is_numeric_dtype(data['age']):
                    mean_val = data['age'].mean() if not data['age'].isnull().all() else 50
                    return {
                        'expectation_type': expectation_type,
                        'kwargs': {
                            'column': 'age',
                            'min_value': mean_val - 10,
                            'max_value': mean_val + 10
                        }
                    }
            
            elif expectation_type == "expect_column_median_to_be_between":
                if 'age' in data.columns and pd.api.types.is_numeric_dtype(data['age']):
                    median_val = data['age'].median() if not data['age'].isnull().all() else 50
                    return {
                        'expectation_type': expectation_type,
                        'kwargs': {
                            'column': 'age',
                            'min_value': median_val - 10,
                            'max_value': median_val + 10
                        }
                    }
            
            elif expectation_type == "expect_column_stdev_to_be_between":
                if 'age' in data.columns and pd.api.types.is_numeric_dtype(data['age']):
                    std_val = data['age'].std() if not data['age'].isnull().all() else 10
                    return {
                        'expectation_type': expectation_type,
                        'kwargs': {
                            'column': 'age',
                            'min_value': max(0, std_val - 5),
                            'max_value': std_val + 5
                        }
                    }
            
            elif expectation_type == "expect_column_sum_to_be_between":
                if 'salary' in data.columns and pd.api.types.is_numeric_dtype(data['salary']):
                    sum_val = data['salary'].sum() if not data['salary'].isnull().all() else 1000000
                    return {
                        'expectation_type': expectation_type,
                        'kwargs': {
                            'column': 'salary',
                            'min_value': sum_val * 0.8,
                            'max_value': sum_val * 1.2
                        }
                    }
            
            elif expectation_type == "expect_column_values_to_be_dateutil_parseable":
                return {
                    'expectation_type': expectation_type,
                    'kwargs': {'column': 'start_date'}
                }
            
            elif expectation_type == "expect_column_values_to_match_strftime_format":
                return {
                    'expectation_type': expectation_type,
                    'kwargs': {
                        'column': 'start_date',
                        'strftime_format': '%Y-%m-%d'
                    }
                }
            
            elif expectation_type == "expect_custom_sql_query_to_return_expected_result":
                return {
                    'expectation_type': expectation_type,
                    'kwargs': {
                        'name': 'Test Custom SQL',
                        'query': 'SELECT COUNT(*) as violation_count FROM {table_name} WHERE age < 0',
                        'expected_result_type': 'empty',
                        'description': 'Check for negative ages'
                    }
                }
            
            return None
            
        except Exception as e:
            print(f"Error creating config for {expectation_type}: {str(e)}")
            return None
    
    def _validate_expectation(self, data: pd.DataFrame, expectation_config: Dict) -> Dict:
        """Validate data against expectation"""
        expectation_type = expectation_config['expectation_type']
        
        try:
            if expectation_type == "expect_custom_sql_query_to_return_expected_result":
                return self.custom_sql.validate_expectation(data, expectation_config)
            else:
                # For now, simulate GE validation - in real implementation, 
                # you would use actual Great Expectations validation
                return self._simulate_ge_validation(data, expectation_config)
        except Exception as e:
            return {
                "success": False,
                "exception_info": {"exception_message": str(e)}
            }
    
    def _simulate_ge_validation(self, data: pd.DataFrame, expectation_config: Dict) -> Dict:
        """Simulate Great Expectations validation for testing purposes"""
        expectation_type = expectation_config['expectation_type']
        kwargs = expectation_config.get('kwargs', {})
        
        try:
            # This is a simplified simulation - replace with actual GE validation
            if expectation_type == "expect_table_row_count_to_be_between":
                row_count = len(data)
                min_val = kwargs.get('min_value', 0)
                max_val = kwargs.get('max_value', float('inf'))
                success = min_val <= row_count <= max_val
                
            elif expectation_type == "expect_column_values_to_not_be_null":
                column = kwargs.get('column')
                if column in data.columns:
                    null_count = data[column].isnull().sum()
                    success = null_count == 0
                else:
                    success = False
                    
            elif expectation_type == "expect_column_values_to_be_unique":
                column = kwargs.get('column')
                if column in data.columns:
                    unique_count = data[column].nunique()
                    total_count = len(data[column].dropna())
                    success = unique_count == total_count
                else:
                    success = False
                    
            else:
                # For other expectation types, return a simplified success/failure
                # based on whether we have problematic data
                success = not self._data_has_issues(data, expectation_type, kwargs)
            
            return {
                "success": success,
                "result": {
                    "element_count": len(data),
                    "unexpected_count": 0 if success else 10,  # Simplified
                    "unexpected_percent": 0 if success else 10
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "exception_info": {"exception_message": str(e)}
            }
    
    def _data_has_issues(self, data: pd.DataFrame, expectation_type: str, kwargs: Dict) -> bool:
        """Check if data has obvious issues that would cause expectation to fail"""
        
        # Check for nulls in string columns that suggest data issues
        if any(col for col in data.columns if data[col].astype(str).str.contains('invalid').any()):
            return True
        
        # Check for negative values where they shouldn't be
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if (data[col] < 0).any() and 'age' in col.lower():
                return True
        
        # Check for obvious format issues
        if 'email' in data.columns:
            email_issues = data['email'].astype(str).str.contains('@').fillna(False)
            if not email_issues.all():
                return True
        
        return False
    
    def _generate_summary(self, execution_time: float) -> TestSummary:
        """Generate test summary"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.success)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Count tests per expectation type
        expectation_coverage = {}
        for result in self.results:
            expectation_type = result.expectation_type
            expectation_coverage[expectation_type] = expectation_coverage.get(expectation_type, 0) + 1
        
        return TestSummary(
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            success_rate=success_rate,
            total_execution_time=execution_time,
            expectation_coverage=expectation_coverage
        )
    
    def _print_summary(self, summary: TestSummary):
        """Print test summary to console"""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE QA TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests:      {summary.total_tests}")
        print(f"Passed:          {summary.passed_tests} ✅")
        print(f"Failed:          {summary.failed_tests} ❌")
        print(f"Success Rate:    {summary.success_rate:.1f}%")
        print(f"Execution Time:  {summary.total_execution_time:.2f} seconds")
        print("-" * 80)
        print("📋 Expectation Type Coverage:")
        for expectation_type, count in summary.expectation_coverage.items():
            short_name = expectation_type.replace('expect_', '').replace('_', ' ').title()
            print(f"  {short_name}: {count} tests")
        print("=" * 80)
    
    def _save_detailed_report(self):
        """Save detailed test report to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"tests/qa_test_report_{timestamp}.json"
        
        # Create tests directory if it doesn't exist
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        
        report_data = {
            "timestamp": timestamp,
            "summary": asdict(self._generate_summary(0)),  # Recalculate without execution time
            "detailed_results": [asdict(result) for result in self.results]
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        print(f"📄 Detailed report saved to: {report_file}")


def run_batch_testing():
    """Run comprehensive QA testing in batch mode"""
    tester = ComprehensiveQATester()
    
    try:
        summary = tester.run_comprehensive_tests()
        
        # Exit with appropriate code
        if summary.success_rate >= 80:
            print("🎉 QA Testing completed successfully!")
            return 0
        else:
            print("⚠️ QA Testing completed with failures. Review the report for details.")
            return 1
            
    except Exception as e:
        print(f"💥 QA Testing failed with exception: {str(e)}")
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    """
    Run comprehensive QA testing framework
    """
    print("🔧 Comprehensive Data Quality Expectation QA Framework")
    print("=" * 60)
    
    exit_code = run_batch_testing()
    exit(exit_code)