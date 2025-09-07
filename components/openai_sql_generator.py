import os
from typing import Optional, Dict, List
from openai import OpenAI
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class OpenAISQLGenerator:
    """OpenAI-powered SQL query generator for data validation"""
    
    def __init__(self):
        self.client = None
        self.model = "gpt-4o-mini"  # Default to a widely available model
        
    def _initialize_client(self) -> bool:
        """Initialize OpenAI client with API key from .env file or Streamlit secrets"""
        api_key = None
        
        # Try Streamlit secrets first (for cloud deployment)
        try:
            if hasattr(st, 'secrets'):
                api_key = st.secrets.get('OPENAI_API_KEY')
        except Exception:
            # If secrets not available or accessible, continue to environment variable
            pass
        
        # Fallback to environment variable (for local development)
        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            return False
        
        try:
            self.client = OpenAI(api_key=api_key)
            return True
        except Exception:
            return False
    
    def is_available(self) -> bool:
        """Check if OpenAI integration is available"""
        return self._initialize_client()
    
    def generate_sql_query(
        self, 
        description: str, 
        data_columns: List[str], 
        data_types: Dict[str, str],
        sample_data: Optional[pd.DataFrame] = None,
        selected_columns: Optional[List[str]] = None
    ) -> Optional[Dict[str, str]]:
        """Generate SQL query using OpenAI API"""
        if not self._initialize_client():
            return None
        
        # Build context about the data
        column_info = []
        for col in data_columns:
            dtype = data_types.get(col, "unknown")
            column_info.append(f"- {col} ({dtype})")
        
        # Add selected columns emphasis if provided
        focus_context = ""
        if selected_columns:
            focus_context = f"\n\nFOCUS COLUMNS (user selected these specific columns):\n"
            for col in selected_columns:
                dtype = data_types.get(col, "unknown")
                focus_context += f"- {col} ({dtype}) - PRIORITIZE THIS COLUMN\n"
        
        # Add sample data context if available
        sample_context = ""
        if sample_data is not None and not sample_data.empty:
            sample_context = "\n\nSample data (first 3 rows):\n"
            # Show selected columns first if available
            columns_to_show = selected_columns if selected_columns else list(sample_data.columns)[:5]
            for idx, row in sample_data.head(3).iterrows():
                values = [f"{col}={repr(row[col])}" for col in columns_to_show if col in sample_data.columns]
                sample_context += f"Row {idx}: {', '.join(values)}\n"
        
        prompt = f"""Generate a complete SQL validation rule based on this requirement:

{description}

Available columns:
{chr(10).join(column_info)}
{focus_context}
{sample_context}

Requirements:
1. Generate a SQL query that:
   - Uses {{table_name}} as the table name placeholder
   - Returns COUNT(*) as violation_count (count of rows that violate the rule)
   - Focuses on finding violations (rows that should NOT exist)
   - Uses True/False for boolean columns (not 1/0)
   - Handles NULL values appropriately
   - Uses clear, descriptive conditions
   - If user selected specific columns, focuses the query on those columns
   - Is efficient and readable

2. Generate a descriptive name for this validation rule (max 50 characters)

3. Generate a detailed description of what this validation checks (max 200 characters)

Return your response in this exact JSON format:
{{
    "sql_query": "SELECT COUNT(*) as violation_count FROM {{table_name}} WHERE ...",
    "name": "Descriptive Name for the Rule",
    "description": "Detailed description of what this validation checks"
}}"""
        
        try:
            # Use appropriate parameters based on model
            request_params = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a SQL expert specializing in data validation queries. Return ONLY a JSON object with keys 'sql_query', 'name', and 'description' as specified. Do not include markdown fences, code blocks, or explanatory prose."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 500
            }
            
            response = self.client.chat.completions.create(**request_params)
            
            response_content = response.choices[0].message.content.strip()
            
            # Clean up the response (remove markdown formatting if present)
            if response_content.startswith("```json"):
                response_content = response_content[7:]
            elif response_content.startswith("```"):
                response_content = response_content[3:]
            if response_content.endswith("```"):
                response_content = response_content[:-3]
            
            # Parse JSON response
            import json
            try:
                result = json.loads(response_content.strip())
                return {
                    "sql_query": result.get("sql_query", ""),
                    "name": result.get("name", "Custom SQL Validation"),
                    "description": result.get("description", "Custom SQL validation rule")
                }
            except json.JSONDecodeError:
                # Fallback: try to extract SQL query from text response
                lines = response_content.split('\n')
                sql_query = ""
                for line in lines:
                    if line.strip().upper().startswith('SELECT'):
                        sql_query = line.strip()
                        break
                
                if sql_query:
                    return {
                        "sql_query": sql_query,
                        "name": "Custom SQL Validation",
                        "description": description[:200] if description else "Custom SQL validation rule"
                    }
                else:
                    return None
            
        except Exception as e:
            # Show detailed error information
            error_msg = str(e)
            st.error(f"OpenAI API error: {error_msg}")
            
            # Add debugging information
            with st.expander("🔍 Debug Information", expanded=True):
                st.write("**Request Parameters:**")
                st.json(request_params)
                
                if "Error code: 400" in error_msg:
                    st.warning("**HTTP 400 Error**: Invalid request parameters")
                elif "Error code: 401" in error_msg:
                    st.warning("**HTTP 401 Error**: Invalid API key")
                elif "Error code: 429" in error_msg:
                    st.warning("**HTTP 429 Error**: Rate limit exceeded, try again later")
                elif "model" in error_msg.lower():
                    st.warning(f"**Model Error**: The model '{self.model}' might not be available or accessible with your API key")
                    st.info("Try switching to a different model like gpt-4o-mini or gpt-4o")
                
                st.write("**Full Error:**")
                st.code(error_msg)
            
            return None
    
    def render_openai_section(self, data: pd.DataFrame) -> Optional[str]:
        """Render OpenAI SQL generation interface"""
        if not self.is_available():
            # Show a simplified interface without AI - no alerts or warnings
            st.markdown("### 📝 Describe Your Validation Rule")
            description = st.text_area(
                "Describe what you want to validate:",
                height=100,
                placeholder="Example: Check for duplicate values in the email column\nOr: Find rows where the age field is missing or invalid",
                help="Describe your validation rule. You can then write the SQL query manually below."
            )
            
            if description:
                st.info("💡 Use the manual SQL editor below to write your query based on this description.")
            
            return None
        
        st.markdown("### 🤖 AI-Powered SQL Generation")
        
        # Field selection section
        st.markdown("#### 🎯 Select Fields for Your Query")
        
        # Multi-column layout for field selection
        col1, col2 = st.columns(2)
        
        with col1:
            selected_columns = st.multiselect(
                "Choose columns to focus on:",
                options=list(data.columns),
                help="Select the columns that your validation rule should check"
            )
        
        with col2:
            if selected_columns:
                st.markdown("**Selected Column Info:**")
                for col in selected_columns:
                    col_type = str(data[col].dtype)
                    sample_values = data[col].dropna().unique()[:3]
                    st.write(f"• **{col}** ({col_type})")
                    if len(sample_values) > 0:
                        st.write(f"  Sample: {', '.join(map(str, sample_values))}")
        
        # Description and model selection
        st.markdown("#### 📝 Describe Your Rule")
        col3, col4 = st.columns([2, 1])
        with col3:
            description = st.text_area(
                "Describe your validation rule:",
                height=120,
                placeholder="Example: prospect__list must be unique\nOr: Find rows where email addresses are missing or invalid format",
                help="Describe what data quality issue you want to detect. Be specific about the columns and conditions."
            )
        
        with col4:
            model_options = [
                "gpt-4o-mini",
                "gpt-4o",
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo",
                "gpt-5"
            ]
            
            # Check if we should use fallback model
            default_index = 0
            if 'fallback_model' in st.session_state:
                if st.session_state['fallback_model'] in model_options:
                    default_index = model_options.index(st.session_state['fallback_model'])
                    st.info(f"🔄 Switched to {st.session_state['fallback_model']} as fallback")
                    del st.session_state['fallback_model']  # Clear the fallback
            
            self.model = st.selectbox(
                "Model:",
                options=model_options,
                index=default_index,
                help="Choose the OpenAI model to use"
            )
            
            # Show model-specific info
            if self.model in ["gpt-4o", "gpt-4o-mini"]:
                st.info("✅ Reliable model choice")
            elif self.model == "gpt-3.5-turbo":
                st.info("💰 Cost-effective option")
            
        
        if description:
            # Validate description
            if len(description.strip()) < 10:
                st.warning("Please provide a more detailed description (at least 10 characters)")
                return None
            
            if st.button("🚀 Generate SQL Query", type="primary"):
                with st.spinner(f"Generating SQL query using {self.model}..."):
                    try:
                        # Use selected columns if provided, otherwise use all columns
                        focus_columns = selected_columns if selected_columns else list(data.columns)
                        
                        # Show what we're sending to the AI
                        with st.expander("📤 Request Details", expanded=False):
                            st.write(f"**Model:** {self.model}")
                            st.write(f"**Description:** {description}")
                            st.write(f"**Focus Columns:** {focus_columns}")
                            st.write(f"**Total Columns Available:** {len(data.columns)}")
                        
                        result = self.generate_sql_query(
                            description=description,
                            data_columns=focus_columns,
                            data_types={col: str(dtype) for col, dtype in data.dtypes.items()},
                            sample_data=data,
                            selected_columns=selected_columns
                        )
                        
                        if result:
                            st.success("SQL validation rule generated successfully!")
                            
                            # Display the generated components
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown("**Generated Name:**")
                                st.info(result['name'])
                            with col2:
                                st.markdown("**Generated Description:**")
                                st.info(result['description'])
                            
                            st.markdown("**Generated SQL Query:**")
                            st.code(result['sql_query'], language="sql")
                            
                            # Store in session state for use in manual builder
                            st.session_state['sql_query'] = result['sql_query']
                            st.session_state['generated_name'] = result['name']
                            st.session_state['generated_description'] = result['description']
                            
                            # Show a tip
                            st.info("💡 The query, name, and description have been generated. You can test it using the 🧪 Test Query button below.")
                            
                            return result['sql_query']
                        else:
                            st.error("Failed to generate SQL query")
                            
                            # Provide quick fixes
                            st.markdown("### 🔧 Quick Fixes:")
                            col_a, col_b = st.columns(2)
                            
                            with col_a:
                                if st.button("🔄 Try with gpt-4o-mini", type="secondary"):
                                    st.session_state['fallback_model'] = 'gpt-4o-mini'
                                    st.rerun()
                            
                            with col_b:
                                if st.button("📝 Use Manual Query", type="secondary"):
                                    # Generate a basic query based on the description
                                    if "null" in description.lower() and selected_columns:
                                        basic_query = f"""SELECT COUNT(*) as violation_count
FROM {{table_name}}
WHERE {selected_columns[0]} IS NULL"""
                                        st.session_state['sql_query'] = basic_query
                                        st.rerun()
                            
                            # Show a manual query suggestion
                            if "null" in description.lower() and selected_columns:
                                st.info(f"💡 **Quick Solution**: For '{selected_columns[0]} must not be null', try this query:")
                                suggested_query = f"""SELECT COUNT(*) as violation_count
FROM {{table_name}}
WHERE {selected_columns[0]} IS NULL"""
                                st.code(suggested_query, language="sql")
                    
                    except Exception as e:
                        st.error(f"Unexpected error during generation: {str(e)}")
        
        return None