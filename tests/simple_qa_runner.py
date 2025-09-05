#!/usr/bin/env python3
"""
Simple QA Test Runner - CSV Output

Runs comprehensive tests for all data quality expectation types and outputs results to CSV.
Much simpler than a dashboard - just run it and get your results in a spreadsheet.

Usage:
    python tests/simple_qa_runner.py

Output:
    - qa_test_results.csv: Detailed test results
    - qa_summary.csv: Summary statistics

Features:
- Tests all 16+ expectation types automatically
- Multiple data scenarios (clean, nulls, duplicates, etc.)
- Edge case testing
- Performance metrics
- Easy to analyze in Excel/Google Sheets
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import random
import traceback

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from comprehensive_qa_framework import ComprehensiveQATester, SyntheticDataGenerator


class SimpleQARunner:
    """Simple QA runner that outputs CSV files"""
    
    def __init__(self):
        self.tester = ComprehensiveQATester()
        self.data_generator = SyntheticDataGenerator()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def run_all_tests(self):
        """Run all tests and save to CSV"""
        print("Starting Comprehensive QA Tests...")
        print(f"Testing {len(self.tester.expectation_types)} expectation types")
        print("-" * 60)
        
        try:
            # Run the comprehensive tests
            summary = self.tester.run_comprehensive_tests()
            
            # Save results to CSV
            self.save_results_to_csv()
            self.save_summary_to_csv(summary)
            
            print("\nAll tests completed!")
            print(f"Results saved to:")
            print(f"   - qa_test_results_{self.timestamp}.csv")
            print(f"   - qa_summary_{self.timestamp}.csv")
            
            return True
            
        except Exception as e:
            print(f"❌ Error running tests: {str(e)}")
            traceback.print_exc()
            return False
    
    def save_results_to_csv(self):
        """Save detailed test results to CSV"""
        results_data = []
        
        for result in self.tester.results:
            results_data.append({
                'timestamp': self.timestamp,
                'expectation_type': result.expectation_type,
                'expectation_category': self.get_expectation_category(result.expectation_type),
                'test_scenario': result.test_scenario,
                'expected_outcome': result.expected_outcome,
                'actual_outcome': result.actual_outcome,
                'test_passed': result.success,
                'execution_time_seconds': result.execution_time,
                'data_rows': result.data_shape[0] if result.data_shape else None,
                'data_columns': result.data_shape[1] if result.data_shape else None,
                'error_message': result.error_message,
                'has_error': result.error_message is not None
            })
        
        df = pd.DataFrame(results_data)
        filename = f"qa_test_results_{self.timestamp}.csv"
        df.to_csv(filename, index=False)
        
        print(f"Detailed results saved: {filename}")
        print(f"   {len(df)} test results")
    
    def save_summary_to_csv(self, summary):
        """Save test summary to CSV"""
        summary_data = []
        
        # Overall summary
        summary_data.append({
            'timestamp': self.timestamp,
            'metric_type': 'overall',
            'metric_name': 'total_tests',
            'value': summary.total_tests,
            'percentage': 100.0
        })
        
        summary_data.append({
            'timestamp': self.timestamp,
            'metric_type': 'overall',
            'metric_name': 'passed_tests',
            'value': summary.passed_tests,
            'percentage': (summary.passed_tests / summary.total_tests * 100) if summary.total_tests > 0 else 0
        })
        
        summary_data.append({
            'timestamp': self.timestamp,
            'metric_type': 'overall',
            'metric_name': 'failed_tests',
            'value': summary.failed_tests,
            'percentage': (summary.failed_tests / summary.total_tests * 100) if summary.total_tests > 0 else 0
        })
        
        summary_data.append({
            'timestamp': self.timestamp,
            'metric_type': 'overall',
            'metric_name': 'success_rate',
            'value': summary.success_rate,
            'percentage': summary.success_rate
        })
        
        summary_data.append({
            'timestamp': self.timestamp,
            'metric_type': 'overall',
            'metric_name': 'execution_time_seconds',
            'value': summary.total_execution_time,
            'percentage': None
        })
        
        # Per-expectation summary
        expectation_stats = self.calculate_expectation_stats()
        for exp_type, stats in expectation_stats.items():
            summary_data.append({
                'timestamp': self.timestamp,
                'metric_type': 'by_expectation',
                'metric_name': f"{exp_type}_total",
                'value': stats['total'],
                'percentage': None
            })
            
            summary_data.append({
                'timestamp': self.timestamp,
                'metric_type': 'by_expectation', 
                'metric_name': f"{exp_type}_passed",
                'value': stats['passed'],
                'percentage': (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            })
        
        # By category summary  
        category_stats = self.calculate_category_stats()
        for category, stats in category_stats.items():
            summary_data.append({
                'timestamp': self.timestamp,
                'metric_type': 'by_category',
                'metric_name': f"{category}_total",
                'value': stats['total'],
                'percentage': None
            })
            
            summary_data.append({
                'timestamp': self.timestamp,
                'metric_type': 'by_category',
                'metric_name': f"{category}_passed", 
                'value': stats['passed'],
                'percentage': (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
            })
        
        df = pd.DataFrame(summary_data)
        filename = f"qa_summary_{self.timestamp}.csv"
        df.to_csv(filename, index=False)
        
        print(f"Summary saved: {filename}")
    
    def get_expectation_category(self, expectation_type: str) -> str:
        """Categorize expectation types"""
        if 'table' in expectation_type:
            return 'table_level'
        elif any(stat in expectation_type for stat in ['mean', 'median', 'stdev', 'sum']):
            return 'statistical'  
        elif any(fmt in expectation_type for fmt in ['regex', 'format', 'dateutil', 'strftime']):
            return 'format_pattern'
        elif 'custom_sql' in expectation_type:
            return 'custom_sql'
        elif 'column' in expectation_type:
            return 'column_validation'
        else:
            return 'other'
    
    def calculate_expectation_stats(self) -> Dict[str, Dict]:
        """Calculate stats per expectation type"""
        stats = {}
        
        for result in self.tester.results:
            exp_type = result.expectation_type
            if exp_type not in stats:
                stats[exp_type] = {'total': 0, 'passed': 0}
            
            stats[exp_type]['total'] += 1
            if result.success:
                stats[exp_type]['passed'] += 1
        
        return stats
    
    def calculate_category_stats(self) -> Dict[str, Dict]:
        """Calculate stats per expectation category"""
        stats = {}
        
        for result in self.tester.results:
            category = self.get_expectation_category(result.expectation_type)
            if category not in stats:
                stats[category] = {'total': 0, 'passed': 0}
            
            stats[category]['total'] += 1
            if result.success:
                stats[category]['passed'] += 1
        
        return stats
    
    def run_quick_test(self, expectation_types: List[str] = None):
        """Run a quick test with specific expectation types"""
        if expectation_types:
            self.tester.expectation_types = expectation_types
            print(f"Running quick test for {len(expectation_types)} expectation types")
        
        return self.run_all_tests()
    
    def generate_test_data_samples(self):
        """Generate sample test datasets and save them"""
        print("Generating sample test datasets...")
        
        datasets = {
            'clean_data': self.data_generator.generate_clean_dataset(1000),
            'data_with_nulls': self.data_generator.generate_dataset_with_nulls(1000),
            'data_with_duplicates': self.data_generator.generate_dataset_with_duplicates(1000),
            'data_with_type_issues': self.data_generator.generate_dataset_with_type_issues(1000),
            'data_with_range_violations': self.data_generator.generate_dataset_with_range_violations(1000),
            'data_with_format_issues': self.data_generator.generate_dataset_with_format_issues(1000),
            'edge_case_data': self.data_generator.generate_edge_case_dataset()
        }
        
        for name, dataset in datasets.items():
            filename = f"sample_{name}_{self.timestamp}.csv"
            dataset.to_csv(filename, index=False)
            print(f"   {filename}: {len(dataset)} rows, {len(dataset.columns)} columns")
        
        print("Sample datasets generated!")


def main():
    """Main entry point"""
    runner = SimpleQARunner()
    
    print("=" * 60)
    print("Simple Data Quality QA Test Runner")
    print("=" * 60)
    
    # Ask user what they want to do
    print("\nOptions:")
    print("1. Run full comprehensive test suite (recommended)")
    print("2. Run quick test (subset of expectations)")
    print("3. Generate sample test datasets only")
    
    try:
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            success = runner.run_all_tests()
            return 0 if success else 1
            
        elif choice == "2":
            # Quick test with most common expectations
            quick_expectations = [
                "expect_column_values_to_not_be_null",
                "expect_column_values_to_be_unique", 
                "expect_column_values_to_be_between",
                "expect_table_row_count_to_be_between",
                "expect_column_values_to_be_in_set"
            ]
            success = runner.run_quick_test(quick_expectations)
            return 0 if success else 1
            
        elif choice == "3":
            runner.generate_test_data_samples()
            return 0
            
        else:
            print("Invalid option. Please select 1, 2, or 3.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\nTest execution cancelled by user")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)