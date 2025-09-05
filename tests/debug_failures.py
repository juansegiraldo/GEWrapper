#!/usr/bin/env python3
"""
Simple Failed Test Debugger (Windows Compatible)

Shows you exactly which tests failed and why, without fancy Unicode characters.
"""

import pandas as pd
import sys
import os
from pathlib import Path

def debug_failures(csv_file):
    """Debug failed tests from CSV results"""
    
    if not Path(csv_file).exists():
        print(f"ERROR: File not found: {csv_file}")
        return
    
    # Load results
    df = pd.read_csv(csv_file)
    failed_tests = df[df['test_passed'] == False]
    
    if failed_tests.empty:
        print("GOOD NEWS: No failed tests found! All tests passed.")
        return
    
    print("FAILED TESTS ANALYSIS")
    print("=" * 60)
    print(f"Found {len(failed_tests)} failed tests out of {len(df)} total")
    print()
    
    # Show each failure
    for idx, (_, test) in enumerate(failed_tests.iterrows(), 1):
        print(f"FAILURE #{idx}:")
        print(f"  Expectation: {test['expectation_type']}")
        print(f"  Scenario: {test['test_scenario']}")
        print(f"  Expected: {test['expected_outcome']}")
        print(f"  Actual: {test['actual_outcome']}")
        
        if pd.notna(test.get('error_message')):
            print(f"  Error: {test['error_message']}")
        
        # Simple diagnosis
        scenario = test['test_scenario']
        exp_type = test['expectation_type']
        
        if 'clean_data_pass' in scenario:
            print("  DIAGNOSIS: This is UNEXPECTED - clean data should pass")
            print("  ACTION NEEDED: Check expectation implementation")
        elif any(x in scenario for x in ['nulls', 'duplicates', 'violations', 'issues', 'format']):
            print("  DIAGNOSIS: This is EXPECTED - bad data should fail")
            print("  ACTION: None - test working correctly")
        elif 'edge_cases' in scenario:
            print("  DIAGNOSIS: Edge case failure - may be expected")
            print("  ACTION: Review if this should pass or fail")
        
        print("-" * 40)
    
    # Summary recommendations
    unexpected_failures = failed_tests[
        failed_tests['test_scenario'].str.contains('clean_data_pass')
    ]
    
    print("\nSUMMARY:")
    print(f"Expected failures: {len(failed_tests) - len(unexpected_failures)}")
    print(f"Unexpected failures: {len(unexpected_failures)} <- THESE NEED FIXING")
    
    if len(unexpected_failures) > 0:
        print(f"\nPROBLEM EXPECTATIONS:")
        problem_expectations = unexpected_failures['expectation_type'].value_counts()
        for exp_type, count in problem_expectations.items():
            print(f"  {exp_type}: {count} failures")
        
        print(f"\nNEXT STEPS:")
        print(f"1. Check utils/ge_helpers.py for implementation bugs")
        print(f"2. Install missing dependencies: pip install pandasql")
        print(f"3. Check components/custom_sql_expectations.py")
        print(f"4. Re-run tests after fixes")
    else:
        print(f"\nALL GOOD: All failures are expected behavior!")


def find_latest_results():
    """Find most recent results file"""
    results_files = list(Path('.').glob('qa_test_results_*.csv'))
    if not results_files:
        return None
    return str(sorted(results_files, reverse=True)[0])


def main():
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = find_latest_results()
        if not csv_file:
            print("ERROR: No QA results files found.")
            print("Run 'python tests/simple_qa_runner.py' first.")
            return 1
        print(f"Using latest results: {csv_file}")
    
    debug_failures(csv_file)
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)