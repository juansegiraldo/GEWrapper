#!/usr/bin/env python3
"""
Test script for data profiling download functionality
"""

import pandas as pd
import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.data_processing import DataProcessor

def test_download_functionality():
    """Test the data profiling download functionality"""
    
    # Create a sample dataset
    print("Creating sample dataset...")
    sample_data = {
        'id': range(1, 1001),
        'name': [f'User_{i}' for i in range(1, 1001)],
        'age': [20 + (i % 50) for i in range(1, 1001)],
        'email': [f'user{i}@example.com' for i in range(1, 1001)],
        'active': [True if i % 2 == 0 else False for i in range(1, 1001)],
        'score': [75.5 + (i % 25) for i in range(1, 1001)],
        'created_date': pd.date_range('2023-01-01', periods=1000, freq='D')
    }
    
    # Add some missing values
    for i in range(50, 60):
        sample_data['age'][i] = None
    for i in range(100, 110):
        sample_data['email'][i] = None
    
    df = pd.DataFrame(sample_data)
    
    # Generate profile
    print("Generating data profile...")
    processor = DataProcessor()
    profile = processor.get_data_profile(df)
    
    if not profile:
        print("Failed to generate profile!")
        return False
    
    print("Profile generated successfully!")
    
    # Test each download format
    formats = ['json', 'excel', 'html', 'csv']
    
    for format_type in formats:
        print(f"\nTesting {format_type.upper()} format...")
        try:
            content = processor.generate_downloadable_profile(df, profile, format_type)
            if content:
                print(f"{format_type.upper()} format generated successfully!")
                print(f"   Size: {len(content)} bytes")
                
                # Save to file for inspection
                # Map format types to proper file extensions
                file_extensions = {
                    'json': 'json',
                    'excel': 'xlsx',
                    'html': 'html',
                    'csv': 'csv'
                }
                file_extension = file_extensions.get(format_type, format_type)
                filename = f"test_profile.{file_extension}"
                with open(filename, 'wb') as f:
                    f.write(content)
                print(f"   Saved to: {filename}")
            else:
                print(f"Failed to generate {format_type.upper()} format!")
                return False
        except Exception as e:
            print(f"Error generating {format_type.upper()} format: {str(e)}")
    
    print("\nDownload functionality test completed!")
    return True

if __name__ == "__main__":
    test_download_functionality()
