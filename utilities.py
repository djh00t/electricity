"""Utility functions for the electricity plans project.

This module provides helper functions for file and directory management, as well as
loading provider URLs from a PDF file.
"""

import os
import time
from config import RETAILER_PDF_URL  # Import the URL for the retailer PDF from the configuration
from get_providers import download_and_extract_pdf_data

def load_provider_urls():
    provider_data = download_and_extract_pdf_data()
    return {provider['brand']: provider['uri'] for provider in provider_data}

def ensure_brand_directory(brand_name):  # Ensure that a directory exists for the given brand name
    base_directory = "brands"
    directory = f"{base_directory}/{brand_name.replace(' ', '_').lower()}"  # Create a sanitized directory name
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def is_file_older_than(filepath, seconds):
    if not os.path.isfile(filepath):
        return True  # If the file does not exist, consider it "older"
    file_mod_time = os.path.getmtime(filepath)
    return (time.time() - file_mod_time) > seconds
