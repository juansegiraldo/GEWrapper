class AppConfig:
    """Application configuration constants"""
    
    # File upload settings
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    SUPPORTED_FILE_TYPES = ['csv', 'json', 'parquet', 'xlsx', 'xls']
    
    # Data display settings
    PREVIEW_ROWS = 20
    MAX_COLUMNS_DISPLAY = 50
    
    # Validation settings
    DEFAULT_SAMPLE_SIZE = 10000
    MAX_EXPECTATIONS_PER_SUITE = 100
    
    # UI settings
    SIDEBAR_WIDTH = 300
    CHART_HEIGHT = 400
    
    # Great Expectations settings
    GE_DATA_CONTEXT_ROOT_DIR = "./ge_data_context"
    DEFAULT_DATASOURCE_NAME = "streamlit_datasource"
    DEFAULT_DATA_CONNECTOR_NAME = "default_data_connector"
    DEFAULT_DATA_ASSET_NAME = "uploaded_data"
    
    # Export settings
    EXPORT_FORMATS = ['HTML', 'PDF', 'JSON']
    
    # Expectation templates
    EXPECTATION_TEMPLATES = {
        "Basic Data Quality": {
            "description": "Essential checks for data completeness and consistency",
            "expectations": [
                "expect_table_row_count_to_be_between",
                "expect_table_columns_to_match_ordered_list",
                "expect_column_values_to_not_be_null"
            ]
        },
        "Numeric Data Validation": {
            "description": "Validation for numeric columns",
            "expectations": [
                "expect_column_values_to_be_between",
                "expect_column_mean_to_be_between",
                "expect_column_values_to_be_of_type"
            ]
        },
        "Text Data Validation": {
            "description": "Validation for text and categorical columns",
            "expectations": [
                "expect_column_values_to_match_regex",
                "expect_column_values_to_be_in_set",
                "expect_column_value_lengths_to_be_between"
            ]
        },
        "Date and Time Validation": {
            "description": "Validation for datetime columns",
            "expectations": [
                "expect_column_values_to_be_dateutil_parseable",
                "expect_column_values_to_be_between"
            ]
        }
    }
    
    # Color scheme
    COLORS = {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e', 
        'success': '#2ca02c',
        'warning': '#d62728',
        'info': '#17becf',
        'light': '#f8f9fa',
        'dark': '#343a40'
    }
    
    # Chart configurations
    CHART_CONFIG = {
        'displayModeBar': False,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d']
    }