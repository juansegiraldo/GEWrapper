"""
Simple test for OpenAI SQL Generator without Streamlit dependencies
"""

import os
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

def test_openai_direct():
    """Test OpenAI API directly"""
    print("Testing OpenAI API directly...")
    
    # Check if API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("OPENAI_API_KEY not found in environment variables")
        print("Set your API key in the .env file")
        return False
    
    print(f"API key found (first 10 chars): {api_key[:10]}...")
    
    try:
        # Initialize client
        client = OpenAI(api_key=api_key)
        print("OpenAI client initialized")
        
        # Test a simple request with proper parameters
        description = "prospect__list must be unique"
        columns = ["prospect__list", "name", "email", "status"]
        
        prompt = f"""Generate a SQL query for data validation based on this requirement:

{description}

Available columns:
- prospect__list (object)
- name (object)  
- email (object)
- status (object)

Requirements for the SQL query:
- Use {{table_name}} as the table name placeholder
- Return COUNT(*) as violation_count (count of rows that violate the rule)
- Focus on finding violations (rows that should NOT exist)
- Use True/False for boolean columns (not 1/0)
- Handle NULL values appropriately
- Use clear, descriptive conditions
- Return only the SQL query, no explanation

Example format:
SELECT COUNT(*) as violation_count
FROM {{table_name}}
WHERE [condition that identifies violations]
"""

        # Use appropriate parameters for widely available model
        model = "gpt-4o-mini"  # Use a model that definitely exists
        request_params = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a SQL expert specializing in data validation queries. Generate only the SQL query without any explanation or formatting."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }
        
        print(f"Making request to {model}...")
        response = client.chat.completions.create(**request_params)
        
        sql_query = response.choices[0].message.content.strip()
        
        # Clean up the response
        if sql_query.startswith("```sql"):
            sql_query = sql_query[6:]
        if sql_query.startswith("```"):
            sql_query = sql_query[3:]
        if sql_query.endswith("```"):
            sql_query = sql_query[:-3]
        
        sql_query = sql_query.strip()
        
        print("SQL query generated successfully!")
        print("\nGenerated SQL:")
        print("-" * 50)
        print(sql_query)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_openai_direct()
    if success:
        print("\nOpenAI integration test passed!")
    else:
        print("\nOpenAI integration test failed!")