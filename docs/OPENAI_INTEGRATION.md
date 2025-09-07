# OpenAI SQL Generator Integration

The custom SQL generator now supports OpenAI API integration for automatic SQL query generation.

## Setup

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup environment file:**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=your-api-key-here
   ```
   
3. **Get your OpenAI API key:**
   - Go to https://platform.openai.com/api-keys
   - Create a new API key
   - Add it to your `.env` file

### Streamlit Cloud Deployment

When deploying to Streamlit Cloud, you'll need to configure secrets:

1. **In your Streamlit Cloud dashboard:**
   - Go to your app settings
   - Navigate to the "Secrets" section
   - Add the following:
   ```toml
   OPENAI_API_KEY = "your-api-key-here"
   ```

2. **The app automatically detects the environment:**
   - Uses Streamlit secrets in cloud deployment
   - Uses `.env` file for local development
   - No code changes needed!

## Features

- **AI-Powered SQL Generation**: Describe your validation rule in plain English, and the AI will generate the corresponding SQL query
- **Multiple Model Support**: Choose from gpt-3.5-turbo, gpt-4, gpt-4-turbo, or gpt-4o-mini
- **Context-Aware**: Uses your data structure (columns, types, sample data) to generate more accurate queries
- **Fallback Support**: Still includes the original ChatGPT link as a fallback option

## Usage

1. Open the SQL Query Builder in the application
2. You'll see a new "🤖 AI-Powered SQL Generation" section at the top
3. Describe your validation rule in the text area
4. Select your preferred OpenAI model
5. Click "🚀 Generate SQL Query"
6. The generated query will appear in the manual SQL editor below

## Example

**Input Description:**
```
Find rows where email addresses are missing or have invalid format
```

**Generated SQL:**
```sql
SELECT COUNT(*) as violation_count
FROM {table_name}
WHERE email IS NULL OR email NOT LIKE '%@%.%'
```

## Models

- **gpt-5**: Most advanced model (default)
- **gpt-4o**: Latest GPT-4 model
- **gpt-4o-mini**: Optimized for speed and cost-effectiveness
- **gpt-4-turbo**: Balanced speed and accuracy
- **gpt-4**: More accurate for complex validation rules
- **gpt-3.5-turbo**: Fast and cost-effective for simple queries

## Error Handling

- If no API key is set, the integration gracefully falls back to manual entry
- API errors are displayed clearly to the user
- Generated queries are automatically cleaned of markdown formatting

## Testing

Run the test script to verify your setup:

```bash
python test_openai_integration.py
```

This will test the integration and show whether your API key is working correctly.