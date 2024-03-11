import os
from get_providers import download_and_extract_pdf_data
from get_providers import download_and_extract_pdf_data

def load_provider_urls():
    return download_and_extract_pdf_data()

def ensure_brand_directory(brand_name):
    base_directory = "brands"
    directory = f"{base_directory}/{brand_name.replace(' ', '_').lower()}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory
