"""
Test script for OpenAI SQL Generator integration
Run this to test the OpenAI integration without the full Streamlit app
"""

import os
import pandas as pd
from dotenv import load_dotenv
from components.openai_sql_generator import OpenAISQLGenerator

# Load environment variables
load_dotenv()

def test_openai_integration():
    """Test the OpenAI SQL generator"""
    print("Testing OpenAI SQL Generator Integration...")
    
    # Check if API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("OPENAI_API_KEY not found")
        print("For local development:")
        print("1. Copy .env.example to .env")
        print("2. Add your API key to the .env file")
        print("3. Get your API key from: https://platform.openai.com/api-keys")
        return False
    
    # Create test data
    test_data = pd.DataFrame({
        'name': ['John Doe', 'Jane Smith', None, 'Bob Johnson'],
        'email': ['john@example.com', 'invalid-email', 'jane@test.com', None],
        'age': [25, 30, 35, -5],
        'active': [True, False, True, False]
    })
    
    print(f"Test data created with shape: {test_data.shape}")
    print(f"Columns: {list(test_data.columns)}")
    print(f"Data types: {dict(test_data.dtypes)}")
    
    # Initialize generator
    generator = OpenAISQLGenerator()
    
    # Test availability
    if not generator.is_available():
        print("OpenAI client not available")
        return False
    
    print("OpenAI client initialized successfully")
    
    # Test SQL generation
    description = "Find rows where email addresses are missing or have invalid format"
    print(f"\nGenerating SQL for: {description}")
    
    sql_query = generator.generate_sql_query(
        description=description,
        data_columns=list(test_data.columns),
        data_types={col: str(dtype) for col, dtype in test_data.dtypes.items()},
        sample_data=test_data
    )
    
    if sql_query:
        print("SQL query generated successfully!")
        print("\nGenerated SQL:")
        print("-" * 50)
        print(sql_query)
        print("-" * 50)
        return True
    else:
        print("Failed to generate SQL query")
        return False

if __name__ == "__main__":
    success = test_openai_integration()
    if success:
        print("\nOpenAI integration test passed!")
    else:
        print("\nOpenAI integration test failed!")