import streamlit as st
import pandas as pd
import time
from typing import Dict, Any, Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.ge_helpers import GEHelpers
from config.app_config import AppConfig

class ValidationRunnerComponent:
    """Component for executing data validation"""
    
    def __init__(self):
        self.ge_helpers = GEHelpers()
        self.config = AppConfig()
    
    def render(self, data: pd.DataFrame, expectation_suite):
        """Render the validation execution interface"""
        st.markdown("### Run Data Validation")
        
        # Ensure we have a usable expectation suite; rebuild from configs if needed
        if expectation_suite is None or not hasattr(expectation_suite, 'expectations') or len(getattr(expectation_suite, 'expectations', []) or []) == 0:
            configs = st.session_state.get('expectation_configs', [])
            if configs:
                st.info("No expectations found in suite. Rebuilding from configured expectations…")
                rebuilt_suite = self.ge_helpers.create_expectation_suite(
                    st.session_state.get('current_suite_name', 'rebuilt_suite')
                )
                success_count = 0
                for cfg in configs:
                    if self.ge_helpers.add_expectation_to_suite(rebuilt_suite, cfg):
                        success_count += 1
                st.write(f"Debug: Rebuilt suite with {success_count}/{len(configs)} expectations")
                st.session_state.expectation_suite = rebuilt_suite
                expectation_suite = rebuilt_suite
            else:
                st.error("Expectation suite has no expectations! Please go back and add some expectations.")
                if st.button("← Back to Expectations", type="secondary", key="back_to_expectations_btn1"):
                    st.session_state.current_step = 'expectations'
                    st.rerun()
                return
        
        # Validation summary
        self._render_validation_summary(data, expectation_suite)
        
        # Execution options
        self._render_execution_options(data)
        
        # Run validation
        self._render_validation_execution(data, expectation_suite)
        
        # Navigation
        self._render_navigation_buttons()
    
    def _render_validation_summary(self, data: pd.DataFrame, expectation_suite):
        """Render validation summary information"""
        st.markdown("#### Validation Summary")
        
        # First row with main metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Dataset Rows", f"{len(data):,}")
        
        with col2:
            st.metric("Dataset Columns", len(data.columns))
        
        with col3:
            expectation_count = len(expectation_suite.expectations) if expectation_suite else 0
            st.metric("Expectations", expectation_count)
        
        # Second row with suite name in full width for better readability
        st.markdown("---")
        suite_name = expectation_suite.name if expectation_suite else "Unknown"
        st.markdown(f"**Suite Name:** `{suite_name}`")
        
        # Show expectation details
        if expectation_suite and hasattr(expectation_suite, 'expectations'):
            with st.expander("View Expectations to be Validated"):
                for i, expectation in enumerate(expectation_suite.expectations, 1):
                    # Support both GE ExpectationConfiguration objects and dicts
                    if isinstance(expectation, dict):
                        exp_type = expectation.get('expectation_type', 'Unknown')
                        kwargs = expectation.get('kwargs', {}) or {}
                    else:
                        exp_type = getattr(expectation, 'expectation_type', 'Unknown')
                        kwargs = getattr(expectation, 'kwargs', {}) or {}

                    column = kwargs.get('column', 'N/A')
                    
                    st.write(f"**{i}.** {exp_type.replace('expect_', '').replace('_', ' ').title()}")
                    if column != 'N/A':
                        st.write(f"   Column: `{column}`")
                    
                    # Show key parameters
                    key_params = {k: v for k, v in kwargs.items() 
                                if k not in ['column'] and not k.startswith('result_format')}
                    if key_params:
                        st.write(f"   Parameters: {key_params}")
                    
                    st.write("---")
    
    def _render_execution_options(self, data: pd.DataFrame):
        """Render validation execution options"""
        st.markdown("#### Execution Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Data sampling option
            use_sample = st.checkbox(
                "Use data sampling for faster execution",
                value=len(data) > self.config.DEFAULT_SAMPLE_SIZE,
                help=f"Recommended for datasets larger than {self.config.DEFAULT_SAMPLE_SIZE:,} rows"
            )
            
            if use_sample:
                sample_size = st.slider(
                    "Sample size:",
                    min_value=1000,
                    max_value=min(len(data), 50000),
                    value=min(len(data), self.config.DEFAULT_SAMPLE_SIZE),
                    step=1000
                )
                st.session_state.validation_sample_size = sample_size
                st.info(f"Will validate using {sample_size:,} randomly sampled rows")
            else:
                st.session_state.validation_sample_size = None
        
        with col2:
            # Validation mode
            validation_mode = st.radio(
                "Validation mode:",
                options=["All at Once", "Step by Step"],
                help="All at Once: Run all expectations together\nStep by Step: Run expectations one by one with progress tracking"
            )
            st.session_state.validation_mode = validation_mode
            
            # Result detail level
            detail_level = st.selectbox(
                "Result detail level:",
                options=["Summary Only", "Basic Details", "Full Details"],
                index=1,
                help="Choose how much detail to include in validation results"
            )
            st.session_state.result_detail_level = detail_level
    
    def _render_validation_execution(self, data: pd.DataFrame, expectation_suite):
        """Render validation execution interface"""
        st.markdown("#### Execute Validation")
        
        # Check if validation has already been run
        if 'validation_completed' in st.session_state and st.session_state.validation_completed:
            st.success("Validation completed! Check the Results tab to view detailed results.")
            
            # Show quick summary
            if st.session_state.validation_results:
                self._show_quick_results_summary()
            
            if st.button("Run Validation Again", type="secondary", key="run_validation_again_btn", use_container_width=True):
                st.session_state.validation_completed = False
                st.session_state.validation_results = None
                st.rerun()
        
        else:
            # Run validation button
            if st.button("🚀 Start Validation", type="primary", use_container_width=True):
                self._execute_validation(data, expectation_suite)
    
    def _execute_validation(self, data: pd.DataFrame, expectation_suite):
        """Execute the validation process"""
        try:
            # Prepare data
            validation_data = self._prepare_validation_data(data)
            
            # Initialize progress tracking
            total_expectations = len(expectation_suite.expectations) if hasattr(expectation_suite, 'expectations') else 0
            
            if st.session_state.validation_mode == "Step by Step":
                self._run_step_by_step_validation(validation_data, expectation_suite, total_expectations)
            else:
                self._run_batch_validation(validation_data, expectation_suite)
            
        except Exception as e:
            st.error(f"Validation failed: {str(e)}")
            st.exception(e)
    
    def _prepare_validation_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Prepare data for validation (sampling if requested)"""
        if st.session_state.get('validation_sample_size'):
            sample_size = st.session_state.validation_sample_size
            if len(data) > sample_size:
                with st.spinner(f"Sampling {sample_size:,} rows from {len(data):,} total rows..."):
                    sampled_data = data.sample(n=sample_size, random_state=42).reset_index(drop=True)
                st.info(f"Using sample of {len(sampled_data):,} rows for validation")
                return sampled_data
        
        return data
    
    def _run_batch_validation(self, data: pd.DataFrame, expectation_suite):
        """Run all expectations at once"""
        with st.spinner("Running validation..."):
            start_time = time.time()
            
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Initializing validation...")
            progress_bar.progress(0.1)
            
            # Debug: Check expectations before validation
            if hasattr(expectation_suite, 'expectations'):
                st.write(f"Debug: Suite has {len(expectation_suite.expectations)} expectations")
                for i, exp in enumerate(expectation_suite.expectations[:3]):  # Show first 3
                    if isinstance(exp, dict):
                        exp_type = exp.get('expectation_type', exp.get('type', 'Unknown'))
                        exp_kwargs = exp.get('kwargs', {})
                        column = exp_kwargs.get('column', 'N/A')
                        st.write(f"  {i+1}. {exp_type} (Column: {column})")
                    else:
                        exp_type = getattr(exp, 'expectation_type', 'Unknown')
                        exp_kwargs = getattr(exp, 'kwargs', {}) or {}
                        column = exp_kwargs.get('column', 'N/A')
                        st.write(f"  {i+1}. {exp_type} (Column: {column})")
            else:
                st.write("Debug: Suite has no expectations attribute")
            
            # Additional debug info
            st.write(f"Debug: Expectation suite type: {type(expectation_suite)}")
            st.write(f"Debug: Expectation suite name: {getattr(expectation_suite, 'name', 'Unknown')}")
            
            # Run validation
            status_text.text("Executing expectations...")
            progress_bar.progress(0.5)
            
            validation_result = self.ge_helpers.validate_data(data, expectation_suite)
            
            progress_bar.progress(0.9)
            status_text.text("Processing results...")
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            progress_bar.progress(1.0)
            status_text.text(f"Validation completed in {execution_time:.2f} seconds!")
            
            if validation_result:
                # Debug: Show validation result structure
                st.write("Debug: Validation result keys:", list(validation_result.keys()))
                if 'statistics' in validation_result:
                    st.write("Debug: Statistics:", validation_result['statistics'])
                
                st.session_state.validation_results = validation_result
                st.session_state.validation_completed = True
                st.session_state.validation_execution_time = execution_time
                
                # Show success message with summary
                self._show_validation_completion_message(validation_result, execution_time)
                
                time.sleep(1)  # Brief pause to show completion
                st.rerun()
            else:
                st.error("Validation failed to produce results!")
    
    def _run_step_by_step_validation(self, data: pd.DataFrame, expectation_suite, total_expectations: int):
        """Run expectations one by one with detailed progress"""
        st.markdown("#### Step-by-Step Validation Progress")
        
        # Create containers for dynamic updates
        progress_container = st.container()
        results_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Summary metrics containers
            metric_cols = st.columns(4)
            with metric_cols[0]:
                total_metric = st.empty()
            with metric_cols[1]:
                passed_metric = st.empty()
            with metric_cols[2]:
                failed_metric = st.empty()
            with metric_cols[3]:
                progress_metric = st.empty()
        
        # Initialize tracking
        passed_count = 0
        failed_count = 0
        results_list = []
        
        start_time = time.time()
        
        # Run each expectation individually
        for i, expectation in enumerate(expectation_suite.expectations):
            current_step = i + 1
            progress = current_step / total_expectations
            
            # Update progress display
            progress_bar.progress(progress)
            status_text.text(f"Running expectation {current_step} of {total_expectations}...")
            
            # Update metrics
            total_metric.metric("Total", f"{current_step}/{total_expectations}")
            passed_metric.metric("Passed", passed_count, delta=None)
            failed_metric.metric("Failed", failed_count, delta=None)
            progress_metric.metric("Progress", f"{progress*100:.1f}%")
            
            try:
                # Create a temporary suite with just this expectation
                temp_suite = self.ge_helpers.create_expectation_suite(f"temp_suite_{i}")
                # Convert to config dict robustly
                if isinstance(expectation, dict):
                    exp_config = expectation
                else:
                    try:
                        exp_config = expectation.to_json_dict()
                    except Exception:
                        exp_config = {
                            'expectation_type': getattr(expectation, 'expectation_type', ''),
                            'kwargs': getattr(expectation, 'kwargs', {}) or {}
                        }
                
                # Ensure the config has the proper structure
                if 'expectation_type' not in exp_config:
                    exp_config['expectation_type'] = exp_config.get('type', 'Unknown')
                
                self.ge_helpers.add_expectation_to_suite(temp_suite, exp_config)
                
                # Run validation for this expectation
                result = self.ge_helpers.validate_data(data, temp_suite)
                
                if result and result.get('results'):
                    expectation_result = result['results'][0]
                    
                    # Ensure the result has the proper expectation_config structure
                    if 'expectation_config' not in expectation_result:
                        expectation_result['expectation_config'] = exp_config
                    
                    results_list.append(expectation_result)
                    
                    if expectation_result.get('success', False):
                        passed_count += 1
                    else:
                        failed_count += 1
                    
                    # Show individual result
                    with results_container:
                        if isinstance(expectation, dict):
                            exp_type_label = expectation.get('expectation_type', expectation.get('type', 'Unknown'))
                            exp_column = expectation.get('kwargs', {}).get('column', 'N/A')
                        else:
                            exp_type_label = getattr(expectation, 'expectation_type', 'Unknown')
                            exp_column = getattr(expectation, 'kwargs', {}).get('column', 'N/A')
                        
                        display_label = f"{exp_type_label}"
                        if exp_column != 'N/A':
                            display_label += f" ({exp_column})"
                        
                        if expectation_result.get('success', False):
                            st.success(f"Step {current_step}: {display_label}")
                        else:
                            st.error(f"Step {current_step}: {display_label}")
                            st.write(f"   Details: {expectation_result.get('result', {}).get('details', 'No details available')}")
                
                # Small delay to make progress visible
                time.sleep(0.1)
                
            except Exception as e:
                failed_count += 1
                st.error(f"Step {current_step} failed: {str(e)}")
        
        # Complete validation
        end_time = time.time()
        execution_time = end_time - start_time
        
        progress_bar.progress(1.0)
        status_text.text(f"Validation completed in {execution_time:.2f} seconds!")
        
        # Update final metrics
        total_metric.metric("Total", total_expectations)
        passed_metric.metric("Passed", passed_count)
        failed_metric.metric("Failed", failed_count)
        progress_metric.metric("Progress", "100%")
        
        # Store results
        validation_result = {
            'results': results_list,
            'success': failed_count == 0,
            'statistics': {
                'evaluated_expectations': total_expectations,
                'successful_expectations': passed_count,
                'unsuccessful_expectations': failed_count,
                'success_percent': (passed_count / total_expectations * 100) if total_expectations > 0 else 0
            },
            'meta': {
                'execution_time': execution_time,
                'validation_mode': 'step_by_step'
            }
        }
        
        st.session_state.validation_results = validation_result
        st.session_state.validation_completed = True
        st.session_state.validation_execution_time = execution_time
        
        self._show_validation_completion_message(validation_result, execution_time)
    
    def _show_validation_completion_message(self, validation_result: Dict, execution_time: float):
        """Show validation completion message with summary"""
        success_rate = validation_result.get('statistics', {}).get('success_percent', 0)
        total_expectations = validation_result.get('statistics', {}).get('evaluated_expectations', 0) or 0
        passed = validation_result.get('statistics', {}).get('successful_expectations', 0) or 0
        failed = validation_result.get('statistics', {}).get('unsuccessful_expectations', 0) or 0
        
        # Handle None success_rate
        if success_rate is None:
            success_rate = 0 if total_expectations == 0 else (passed / total_expectations * 100)
        
        # Ensure success_rate is a number
        if not isinstance(success_rate, (int, float)):
            success_rate = 0
        
        if success_rate == 100:
            st.balloons()
            st.success(f"Perfect! All {total_expectations} expectations passed in {execution_time:.2f} seconds!")
        elif success_rate >= 80:
            st.success(f"Good! {passed}/{total_expectations} expectations passed ({success_rate:.1f}% success rate)")
        else:
            st.warning(f"{passed}/{total_expectations} expectations passed ({success_rate:.1f}% success rate)")
        
        if failed > 0:
            st.error(f"{failed} expectations failed. Check the detailed results for more information.")
    
    def _show_quick_results_summary(self):
        """Show a quick summary of validation results"""
        if not st.session_state.validation_results:
            return
        
        results = st.session_state.validation_results
        stats = results.get('statistics', {})
        
        st.markdown("#### Quick Results Summary")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total = stats.get('evaluated_expectations', 0)
            st.metric("Total Expectations", total)
        
        with col2:
            passed = stats.get('successful_expectations', 0)
            st.metric("Passed", passed, delta=None)
        
        with col3:
            failed = stats.get('unsuccessful_expectations', 0)
            st.metric("Failed", failed, delta=None)
        
        with col4:
            success_rate = stats.get('success_percent')
            if success_rate is not None and isinstance(success_rate, (int, float)):
                st.metric("Success Rate", f"{success_rate:.1f}%")
            else:
                # Calculate success rate if not provided or invalid
                total = stats.get('evaluated_expectations', 0) or 0
                passed = stats.get('successful_expectations', 0) or 0
                if total > 0:
                    success_rate = (passed / total) * 100
                    st.metric("Success Rate", f"{success_rate:.1f}%")
                else:
                    st.metric("Success Rate", "0.0%")
        
        with col5:
            # Calculate average data failure rate across all expectations
            if 'results' in results and results['results']:
                total_failure_rate = 0
                valid_expectations = 0
                
                for result in results['results']:
                    if 'result' in result and 'element_count' in result['result']:
                        element_count = result['result']['element_count']
                        unexpected_count = result['result'].get('unexpected_count', 0)
                        missing_count = result['result'].get('missing_count', 0)
                        
                        if element_count > 0:
                            failure_rate = (unexpected_count + missing_count) / element_count * 100
                            total_failure_rate += failure_rate
                            valid_expectations += 1
                
                if valid_expectations > 0:
                    avg_failure_rate = total_failure_rate / valid_expectations
                    st.metric("Avg Data Failure Rate", f"{avg_failure_rate:.1f}%")
                else:
                    st.metric("Avg Data Failure Rate", "N/A")
            else:
                st.metric("Avg Data Failure Rate", "N/A")
    
    def _render_navigation_buttons(self):
        """Render navigation buttons"""
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("← Back to Expectations", type="secondary", key="back_to_expectations_btn2"):
                st.session_state.current_step = 'expectations'
                st.rerun()
        
        with col2:
            if st.session_state.get('validation_completed', False):
                if st.button("View Results →", type="primary", key="view_results_btn"):
                    st.session_state.current_step = 'results'
                    st.rerun()
            else:
                st.info("Complete validation to proceed to results")