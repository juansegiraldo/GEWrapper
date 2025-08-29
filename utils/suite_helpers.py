import streamlit as st
from datetime import datetime
import re

def generate_suite_name():
    """Generate suite name based on uploaded file + timestamp"""
    # Get uploaded filename from session state
    uploaded_filename = st.session_state.get('uploaded_filename', 'unknown_dataset')
    
    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create suite name: filename_timestamp
    suite_name = f"{uploaded_filename}_{timestamp}"
    
    # Clean the suite name (remove special characters that might cause issues)
    suite_name = re.sub(r'[^a-zA-Z0-9_-]', '_', suite_name)
    
    # Ensure the suite name is not too long (Great Expectations has limits)
    if len(suite_name) > 100:
        suite_name = suite_name[:100]
    
    return suite_name

def get_clean_filename(uploaded_filename):
    """Clean uploaded filename for use in suite name"""
    # Remove file extension for cleaner suite name
    base_filename = uploaded_filename.rsplit('.', 1)[0] if '.' in uploaded_filename else uploaded_filename
    return base_filename
