#!/usr/bin/env python3
"""
QA Results Analyzer

Simple script to analyze CSV results from the QA test runner.
Generates summary reports and identifies patterns in test failures.

Usage:
    python analyze_qa_results.py qa_test_results_TIMESTAMP.csv
"""

import pandas as pd
import sys
from pathlib import Path


def analyze_results(csv_file: str):
    """Analyze QA test results from CSV file"""
    
    if not Path(csv_file).exists():
        print(f"❌ File not found: {csv_file}")
        return
    
    # Load results
    df = pd.read_csv(csv_file)
    
    print("=" * 80)
    print("📊 QA TEST RESULTS ANALYSIS")
    print("=" * 80)
    print(f"📁 File: {csv_file}")
    print(f"📅 Timestamp: {df['timestamp'].iloc[0] if not df.empty else 'Unknown'}")
    print("-" * 80)
    
    # Overall summary
    total_tests = len(df)
    passed_tests = df['test_passed'].sum()
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"🔢 OVERALL RESULTS:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests} ✅")
    print(f"   Failed: {failed_tests} ❌") 
    print(f"   Success Rate: {success_rate:.1f}%")
    print()
    
    # Results by expectation category
    print("📋 RESULTS BY CATEGORY:")
    category_stats = df.groupby('expectation_category').agg({
        'test_passed': ['count', 'sum']
    }).round(1)
    
    category_stats.columns = ['total', 'passed']
    category_stats['failed'] = category_stats['total'] - category_stats['passed']
    category_stats['success_rate'] = (category_stats['passed'] / category_stats['total'] * 100).round(1)
    
    for category, stats in category_stats.iterrows():
        print(f"   {category.replace('_', ' ').title()}: {stats['success_rate']:.1f}% ({int(stats['passed'])}/{int(stats['total'])})")
    
    print()
    
    # Results by test scenario
    print("🎭 RESULTS BY TEST SCENARIO:")
    scenario_stats = df.groupby('test_scenario').agg({
        'test_passed': ['count', 'sum']
    }).round(1)
    
    scenario_stats.columns = ['total', 'passed']
    scenario_stats['success_rate'] = (scenario_stats['passed'] / scenario_stats['total'] * 100).round(1)
    
    for scenario, stats in scenario_stats.iterrows():
        print(f"   {scenario.replace('_', ' ').title()}: {stats['success_rate']:.1f}% ({int(stats['passed'])}/{int(stats['total'])})")
    
    print()
    
    # Performance analysis
    if 'execution_time_seconds' in df.columns:
        print("⏱️ PERFORMANCE ANALYSIS:")
        performance_stats = df['execution_time_seconds'].describe()
        print(f"   Average execution time: {performance_stats['mean']:.3f}s")
        print(f"   Fastest test: {performance_stats['min']:.3f}s")
        print(f"   Slowest test: {performance_stats['max']:.3f}s")
        
        # Slowest expectation types
        slow_expectations = df.groupby('expectation_type')['execution_time_seconds'].mean().sort_values(ascending=False).head(5)
        print(f"   Slowest expectation types:")
        for exp_type, avg_time in slow_expectations.items():
            short_name = exp_type.replace('expect_', '').replace('_', ' ').title()
            print(f"     {short_name}: {avg_time:.3f}s")
        print()
    
    # Failed tests analysis
    if failed_tests > 0:
        print("❌ FAILED TESTS ANALYSIS:")
        failed_df = df[df['test_passed'] == False]
        
        # Most common failure types
        failure_types = failed_df['expectation_type'].value_counts().head(5)
        print(f"   Most problematic expectation types:")
        for exp_type, count in failure_types.items():
            short_name = exp_type.replace('expect_', '').replace('_', ' ').title()
            print(f"     {short_name}: {count} failures")
        
        # Common error patterns
        if 'error_message' in failed_df.columns:
            errors_with_messages = failed_df[failed_df['error_message'].notna()]
            if not errors_with_messages.empty:
                print(f"   Sample error messages:")
                for i, (_, row) in enumerate(errors_with_messages.head(3).iterrows()):
                    exp_name = row['expectation_type'].replace('expect_', '').replace('_', ' ').title()
                    print(f"     {exp_name}: {row['error_message'][:100]}...")
        print()
    
    # Recommendations
    print("💡 RECOMMENDATIONS:")
    
    if success_rate >= 90:
        print("   ✅ Excellent! Your data quality expectations are working well.")
    elif success_rate >= 75:
        print("   ⚠️ Good, but some expectations need attention.")
    else:
        print("   🚨 Many expectations are failing. Review your test data and expectation configurations.")
    
    # Specific recommendations based on failures
    if failed_tests > 0:
        failed_categories = failed_df['expectation_category'].value_counts()
        worst_category = failed_categories.index[0]
        print(f"   🔍 Focus on improving {worst_category.replace('_', ' ')} expectations.")
        
        failed_scenarios = failed_df['test_scenario'].value_counts()
        if len(failed_scenarios) > 0:
            worst_scenario = failed_scenarios.index[0] 
            print(f"   📊 Pay attention to {worst_scenario.replace('_', ' ')} test scenarios.")
    
    print("=" * 80)


def find_latest_results():
    """Find the most recent QA results file"""
    results_files = list(Path('.').glob('qa_test_results_*.csv'))
    
    if not results_files:
        print("❌ No QA results files found.")
        print("   Run 'python tests/simple_qa_runner.py' first to generate results.")
        return None
    
    # Sort by filename (which contains timestamp)
    latest_file = sorted(results_files, reverse=True)[0]
    return str(latest_file)


def main():
    """Main analyzer entry point"""
    if len(sys.argv) > 1:
        csv_file = sys.argv[1]
    else:
        csv_file = find_latest_results()
        if csv_file:
            print(f"📁 Using latest results file: {csv_file}")
        else:
            return 1
    
    analyze_results(csv_file)
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)