import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.data_upload import DataUploadComponent
from components.expectation_builder import ExpectationBuilderComponent
from components.validation_runner import ValidationRunnerComponent
from components.results_display import ResultsDisplayComponent
from utils.ge_helpers import GEHelpers
from utils.suite_helpers import generate_suite_name
from config.app_config import AppConfig

st.set_page_config(
    page_title="DataWash by Stratesys - Data Quality made simple",
    page_icon="🧹",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None
    if 'data_context' not in st.session_state:
        st.session_state.data_context = None
    if 'expectation_suite' not in st.session_state:
        st.session_state.expectation_suite = None
    if 'validation_results' not in st.session_state:
        st.session_state.validation_results = None
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 'upload'
    if 'current_suite_name' not in st.session_state:
        # Generate suite name based on uploaded file + timestamp
        suite_name = generate_suite_name()
        st.session_state.current_suite_name = suite_name
    elif (st.session_state.get('uploaded_filename') and 
          st.session_state.get('current_suite_name', '').startswith('unknown_dataset')):
        # Update suite name if we now have an uploaded filename
        suite_name = generate_suite_name()
        st.session_state.current_suite_name = suite_name
    if 'ge_helpers' not in st.session_state:
        st.session_state.ge_helpers = GEHelpers()

def main():
    """Main application function"""
    initialize_session_state()
    
    st.title("🧹 DataWash by Stratesys")
    st.markdown("### Data Quality made simple")
    st.markdown("---")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    st.sidebar.markdown("Follow these steps to validate your data:")
    
    steps = {
        'upload': '📁 Upload Data',
        'profile': '📊 Data Profiling', 
        'expectations': '⚙️ Configure Expectations',
        'validate': '✅ Run Validation',
        'results': '📋 View Results'
    }
    
    selected_step = st.sidebar.radio(
        "Choose a step:",
        list(steps.keys()),
        format_func=lambda x: steps[x],
        index=list(steps.keys()).index(st.session_state.current_step)
    )
    
    st.session_state.current_step = selected_step
    
    # Progress indicator
    step_index = list(steps.keys()).index(selected_step)
    progress = (step_index + 1) / len(steps)
    st.sidebar.progress(progress)
    st.sidebar.markdown(f"**Step {step_index + 1} of {len(steps)}**")
    
    # Copyright and attribution
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📝 About")
    st.sidebar.markdown("**Developed by**  \n*Juan Giraldo*")
    st.sidebar.markdown("**Product**  \n*DataWash by Stratesys*  \n*v 0.2*")
    st.sidebar.markdown("**© 2025 All Rights Reserved**  \n*Data Quality Made Simple*")
    
    # Main content area
    if selected_step == 'upload':
        render_upload_step()
    elif selected_step == 'profile':
        render_profile_step()
    elif selected_step == 'expectations':
        render_expectations_step()
    elif selected_step == 'validate':
        render_validation_step()
    elif selected_step == 'results':
        render_results_step()

def render_upload_step():
    """Render the data upload step"""
    st.header("📁 Upload Your Data")
    data_upload = DataUploadComponent()
    data_upload.render()

def render_profile_step():
    """Render the data profiling step"""
    st.header("📊 Data Profiling")
    
    if st.session_state.uploaded_data is None:
        st.warning("Please upload data first!")
        st.stop()
    
    data_upload = DataUploadComponent()
    data_upload.show_data_profile(st.session_state.uploaded_data)

def render_expectations_step():
    """Render the expectations configuration step"""
    st.header("⚙️ Configure Data Expectations")
    
    if st.session_state.uploaded_data is None:
        st.warning("Please upload data first!")
        st.stop()
    
    expectation_builder = ExpectationBuilderComponent()
    expectation_builder.render(st.session_state.uploaded_data)

def render_validation_step():
    """Render the validation execution step"""
    # Removed duplicate header - title is now handled in ValidationRunnerComponent
    
    if st.session_state.uploaded_data is None:
        st.warning("Please upload data first!")
        st.stop()
    
    if st.session_state.expectation_suite is None:
        st.warning("Please configure expectations first!")
        st.stop()
    
    validation_runner = ValidationRunnerComponent()
    validation_runner.render(
        st.session_state.uploaded_data,
        st.session_state.expectation_suite
    )

def render_results_step():
    """Render the results display step"""
    st.header("📋 Validation Results")
    
    if st.session_state.validation_results is None:
        st.warning("Please run validation first!")
        st.stop()
    
    results_display = ResultsDisplayComponent()
    results_display.render(st.session_state.validation_results)

if __name__ == "__main__":
    main()