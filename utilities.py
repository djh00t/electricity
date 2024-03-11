import os
import time
from config import RETAILER_PDF_URL
from get_providers import download_and_extract_pdf_data

def load_provider_urls():
    provider_data = download_and_extract_pdf_data(RETAILER_PDF_URL)
    return {provider['brand']: provider['uri'] for provider in provider_data}

def ensure_brand_directory(brand_name):
    base_directory = "brands"
    directory = f"{base_directory}/{brand_name.replace(' ', '_').lower()}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def is_file_older_than(filepath, seconds):
    if not os.path.isfile(filepath):
        return True
    file_mod_time = os.path.getmtime(filepath)
    return (time.time() - file_mod_time) > seconds