#!/usr/bin/env python3
"""
Debug Failed QA Tests

This script helps you investigate and fix failing QA tests by:
1. Showing detailed failure information
2. Re-creating the exact test scenario
3. Testing potential fixes
4. Generating corrected test data

Usage:
    python debug_failed_tests.py qa_test_results_TIMESTAMP.csv
"""

import pandas as pd
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tests.comprehensive_qa_framework import SyntheticDataGenerator, ComprehensiveQATester


class FailedTestDebugger:
    """Debug and fix failed QA tests"""
    
    def __init__(self):
        self.data_generator = SyntheticDataGenerator()
        self.tester = ComprehensiveQATester()
    
    def debug_failures(self, csv_file: str):
        """Debug all failed tests from CSV results"""
        
        if not Path(csv_file).exists():
            print(f"❌ File not found: {csv_file}")
            return
        
        # Load results and filter failures
        df = pd.read_csv(csv_file)
        failed_tests = df[df['test_passed'] == False]
        
        if failed_tests.empty:
            print("🎉 No failed tests found! All tests passed.")
            return
        
        print("DEBUGGING FAILED TESTS")
        print("=" * 60)
        print(f"Found {len(failed_tests)} failed tests")
        print("-" * 60)
        
        for idx, (_, test) in enumerate(failed_tests.iterrows(), 1):
            print(f"\n🚨 FAILURE #{idx}")
            self.debug_single_failure(test)
            print("-" * 60)
        
        # Provide overall recommendations
        self.provide_fix_recommendations(failed_tests)
    
    def debug_single_failure(self, test_row):
        """Debug a single failed test in detail"""
        
        expectation_type = test_row['expectation_type']
        test_scenario = test_row['test_scenario'] 
        error_message = test_row.get('error_message', 'No error message')
        expected = test_row['expected_outcome']
        actual = test_row['actual_outcome']
        
        print(f"📋 Expectation: {expectation_type}")
        print(f"🎭 Scenario: {test_scenario}")
        print(f"❌ Error: {error_message}")
        print(f"🎯 Expected: {expected}")
        print(f"📊 Actual: {actual}")
        
        # Re-create the test scenario to investigate
        print(f"\n🔬 RECREATING TEST SCENARIO...")
        try:
            # Generate the same test data
            data = self.recreate_test_data(test_scenario)
            print(f"📊 Test data: {data.shape[0]} rows, {data.shape[1]} columns")
            
            # Show data sample
            print("📋 Data sample:")
            print(data.head(3).to_string())
            
            # Show data quality issues
            self.analyze_data_issues(data, expectation_type)
            
            # Suggest fixes
            self.suggest_fixes(expectation_type, test_scenario, error_message, data)
            
        except Exception as e:
            print(f"⚠️ Could not recreate test scenario: {str(e)}")
    
    def recreate_test_data(self, test_scenario: str) -> pd.DataFrame:
        """Recreate the exact test data that caused the failure"""
        
        data_generators = {
            'clean_data_pass': self.data_generator.generate_clean_dataset,
            'with_nulls_fail': self.data_generator.generate_dataset_with_nulls, 
            'with_duplicates_fail': self.data_generator.generate_dataset_with_duplicates,
            'type_violations_fail': self.data_generator.generate_dataset_with_type_issues,
            'range_violations_fail': self.data_generator.generate_dataset_with_range_violations,
            'format_violations_fail': self.data_generator.generate_dataset_with_format_issues,
            'edge_cases': self.data_generator.generate_edge_case_dataset
        }
        
        generator = data_generators.get(test_scenario)
        if generator:
            if test_scenario == 'edge_cases':
                return generator()
            else:
                return generator(rows=100)  # Same as in tests
        else:
            # Default to clean data
            return self.data_generator.generate_clean_dataset(100)
    
    def analyze_data_issues(self, data: pd.DataFrame, expectation_type: str):
        """Analyze what might be wrong with the test data"""
        
        print(f"\n🔍 DATA QUALITY ANALYSIS:")
        
        # Check for nulls
        null_counts = data.isnull().sum()
        if null_counts.any():
            print(f"   🚫 Null values found:")
            for col, count in null_counts[null_counts > 0].items():
                print(f"      {col}: {count} nulls ({count/len(data)*100:.1f}%)")
        
        # Check for duplicates in ID column
        if 'id' in data.columns:
            duplicate_count = data['id'].duplicated().sum()
            if duplicate_count > 0:
                print(f"   🔄 Duplicate IDs: {duplicate_count}")
        
        # Check data types
        print(f"   📊 Data types:")
        for col, dtype in data.dtypes.items():
            print(f"      {col}: {dtype}")
        
        # Check for obvious issues
        numeric_cols = data.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            if col == 'age' and (data[col] < 0).any():
                negative_count = (data[col] < 0).sum()
                print(f"   ⚠️ Negative ages: {negative_count}")
            
            if col == 'age' and (data[col] > 120).any():
                old_count = (data[col] > 120).sum()
                print(f"   ⚠️ Ages over 120: {old_count}")
        
        # Check string columns
        if 'email' in data.columns:
            invalid_emails = ~data['email'].astype(str).str.contains('@', na=False)
            if invalid_emails.any():
                invalid_count = invalid_emails.sum()
                print(f"   📧 Invalid email formats: {invalid_count}")
    
    def suggest_fixes(self, expectation_type: str, test_scenario: str, error_message: str, data: pd.DataFrame):
        """Suggest specific fixes based on the failure"""
        
        print(f"\n💡 SUGGESTED FIXES:")
        
        # Generic suggestions based on expectation type
        if "null" in expectation_type and "with_nulls" in test_scenario:
            print(f"   ✅ This failure is EXPECTED - null expectation should fail with null data")
            print(f"   🔧 No fix needed - test is working correctly")
        
        elif "unique" in expectation_type and "duplicates" in test_scenario:
            print(f"   ✅ This failure is EXPECTED - uniqueness should fail with duplicates")
            print(f"   🔧 No fix needed - test is working correctly")
        
        elif "between" in expectation_type and "range_violations" in test_scenario:
            print(f"   ✅ This failure is EXPECTED - range checks should fail with violations")
            print(f"   🔧 No fix needed - test is working correctly")
        
        elif "regex" in expectation_type and "format_violations" in test_scenario:
            print(f"   ✅ This failure is EXPECTED - format checks should fail with bad formats")
            print(f"   🔧 No fix needed - test is working correctly")
        
        elif "clean_data_pass" in test_scenario:
            print(f"   🚨 This failure is UNEXPECTED - clean data should pass")
            print(f"   🔧 NEEDS INVESTIGATION:")
            
            if "Exception" in error_message or "Error" in error_message:
                print(f"      1. Check if expectation logic has bugs")
                print(f"      2. Verify test data generation is correct")
                print(f"      3. Check Great Expectations implementation")
            
            if "custom_sql" in expectation_type:
                print(f"      4. Verify SQL query syntax and logic")
                print(f"      5. Check if pandasql is installed: pip install pandasql")
        
        elif "edge_cases" in test_scenario:
            print(f"   ⚠️ Edge case failure - may be expected depending on expectation")
            print(f"   🔧 INVESTIGATE:")
            print(f"      1. Check if edge case handling is correct")
            print(f"      2. Verify expectation parameters are appropriate")
            print(f"      3. Consider if edge case should pass or fail")
        
        # Specific error-based suggestions
        if "pandasql" in error_message.lower():
            print(f"   🔧 IMMEDIATE FIX: Install pandasql")
            print(f"      pip install pandasql")
        
        if "column not found" in error_message.lower():
            print(f"   🔧 IMMEDIATE FIX: Check column names in test data generation")
        
        if "import" in error_message.lower():
            print(f"   🔧 IMMEDIATE FIX: Install missing dependencies")
    
    def provide_fix_recommendations(self, failed_tests: pd.DataFrame):
        """Provide overall recommendations for fixing failures"""
        
        print("\n🎯 OVERALL RECOMMENDATIONS")
        print("=" * 60)
        
        # Count failure types
        unexpected_failures = failed_tests[
            failed_tests['test_scenario'].str.contains('clean_data_pass|edge_cases')
        ]
        expected_failures = failed_tests[
            failed_tests['test_scenario'].str.contains('nulls|duplicates|violations|issues')
        ]
        
        print(f"📊 Failure breakdown:")
        print(f"   Expected failures: {len(expected_failures)} (these are good!)")
        print(f"   Unexpected failures: {len(unexpected_failures)} (these need fixing)")
        
        if len(unexpected_failures) == 0:
            print(f"\n🎉 GREAT NEWS! All failures are expected behavior.")
            print(f"   Your expectations are working correctly!")
        else:
            print(f"\n🔧 PRIORITY FIXES NEEDED:")
            
            # Group by expectation type
            problem_expectations = unexpected_failures.groupby('expectation_type').size().sort_values(ascending=False)
            
            for exp_type, count in problem_expectations.items():
                short_name = exp_type.replace('expect_', '').replace('_', ' ').title()
                print(f"   🚨 {short_name}: {count} unexpected failures")
        
        # Common fixes
        print(f"\n🛠️ COMMON FIXES:")
        print(f"   1. Check utils/ge_helpers.py - expectation implementation")
        print(f"   2. Verify components/custom_sql_expectations.py - SQL logic")
        print(f"   3. Install missing dependencies: pip install pandasql great-expectations")
        print(f"   4. Check test data generation in comprehensive_qa_framework.py")
        
        print(f"\n📋 NEXT STEPS:")
        print(f"   1. Fix unexpected failures first")
        print(f"   2. Re-run tests: python tests/simple_qa_runner.py")
        print(f"   3. Verify fixes: python debug_failed_tests.py [new_results.csv]")
    
    def create_test_fix_template(self, expectation_type: str):
        """Create a template for fixing a specific expectation"""
        
        template = f"""
# Fix template for {expectation_type}

## 1. Check expectation implementation in utils/ge_helpers.py
Look for the validation logic and ensure it handles edge cases properly.

## 2. Check test data generation
Verify that synthetic data matches what the expectation expects.

## 3. Test manually
```python
from tests.comprehensive_qa_framework import SyntheticDataGenerator
from utils.ge_helpers import GEHelpers

# Generate test data
gen = SyntheticDataGenerator()
data = gen.generate_clean_dataset(100)

# Test expectation manually
ge_helpers = GEHelpers()
config = {{
    'expectation_type': '{expectation_type}',
    'kwargs': {{
        # Add appropriate parameters here
    }}
}}

# Run validation
result = ge_helpers.validate_expectation(data, config)
print(result)
```

## 4. Common issues and fixes
- ImportError: Install missing packages
- Column not found: Check column names
- Type errors: Verify data type handling
- SQL errors: Check query syntax (for custom SQL expectations)
"""
        
        filename = f"fix_template_{expectation_type}.md"
        with open(filename, 'w') as f:
            f.write(template)
        
        print(f"📝 Fix template created: {filename}")


def main():
    """Main debugger entry point"""
    
    if len(sys.argv) < 2:
        # Find latest results file
        results_files = list(Path('.').glob('qa_test_results_*.csv'))
        if not results_files:
            print("❌ No QA results files found.")
            print("   Run 'python tests/simple_qa_runner.py' first.")
            return 1
        
        csv_file = str(sorted(results_files, reverse=True)[0])
        print(f"Using latest results: {csv_file}")
    else:
        csv_file = sys.argv[1]
    
    debugger = FailedTestDebugger()
    debugger.debug_failures(csv_file)
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)