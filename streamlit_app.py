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

# Accessible Button Styling (WCAG AA Compliant)
st.markdown("""
<style>
    /* Primary Action Buttons - Accessible Blue Gradient (4.5:1+ contrast) */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 16px !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 15px 0 rgba(37, 99, 235, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px 0 rgba(37, 99, 235, 0.4) !important;
    }
    
    /* Secondary Action Buttons - Light Blue (4.5:1+ contrast) */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 0.6rem 1.2rem !important;
        border-radius: 8px !important;
        box-shadow: 0 3px 12px 0 rgba(14, 165, 233, 0.25) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 16px 0 rgba(14, 165, 233, 0.35) !important;
    }
    
    /* Link Buttons - Accessible Teal with Dark Text (7:1+ contrast) */
    .stLinkButton > a {
        background: linear-gradient(135deg, #a7f3d0 0%, #6ee7b7 100%) !important;
        border: none !important;
        color: #065f46 !important;
        font-weight: bold !important;
        text-decoration: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 15px 0 rgba(110, 231, 183, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stLinkButton > a:hover {
        background: linear-gradient(135deg, #6ee7b7 0%, #34d399 100%) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px 0 rgba(110, 231, 183, 0.4) !important;
        color: #064e3b !important;
    }
    
    /* Enhance button icons */
    .stButton button, .stLinkButton a {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
    }
    
    /* Destructive Actions - Accessible Orange/Red (4.5:1+ contrast) */
    .stButton > button:has-text("Clear"), 
    .stButton > button:has-text("Remove"),
    .stButton > button:has-text("Cancel") {
        background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
        color: white !important;
    }
    
    .stButton > button:has-text("Clear"):hover,
    .stButton > button:has-text("Remove"):hover,
    .stButton > button:has-text("Cancel"):hover {
        background: linear-gradient(135deg, #ea580c 0%, #dc2626 100%) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Test/Validation Buttons - Accessible Green (4.5:1+ contrast) */
    .stButton > button:has-text("Test"),
    .stButton > button:has-text("Validate") {
        background: linear-gradient(135deg, #16a34a 0%, #15803d 100%) !important;
        color: white !important;
    }
    
    .stButton > button:has-text("Test"):hover,
    .stButton > button:has-text("Validate"):hover {
        background: linear-gradient(135deg, #15803d 0%, #166534 100%) !important;
        transform: translateY(-1px) !important;
    }
</style>
""", unsafe_allow_html=True)

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
    
    # Display DataWash logo
    st.image("docs/assets/Logo DataWash.png", width=800)
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
    st.sidebar.markdown("### About")
    st.sidebar.markdown("**Developed by**  \n*[Juan Giraldo](https://www.linkedin.com/in/juan-sebastian-giraldo/)*")
    st.sidebar.markdown("**Product**  \n*DataWash by [Stratesys](https://www.stratesys-ts.com/)*  \n*v 0.2*")
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
    st.header("Upload Your Data")
    data_upload = DataUploadComponent()
    data_upload.render()

def render_profile_step():
    """Render the data profiling step"""
    st.header("Data Profiling")
    
    if st.session_state.uploaded_data is None:
        st.warning("Please upload data first!")
        st.stop()
    
    data_upload = DataUploadComponent()
    data_upload.show_data_profile(st.session_state.uploaded_data)

def render_expectations_step():
    """Render the expectations configuration step"""
    st.header("Configure Data Expectations")
    
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
    st.header("Validation Results")
    
    if st.session_state.validation_results is None:
        st.warning("Please run validation first!")
        st.stop()
    
    results_display = ResultsDisplayComponent()
    results_display.render(st.session_state.validation_results)

if __name__ == "__main__":
    main()