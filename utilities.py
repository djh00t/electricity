import os
from get_providers import download_and_extract_pdf_data
from get_providers import download_and_extract_pdf_data

import time
import os

def load_provider_urls():
    return download_and_extract_pdf_data()

def ensure_brand_directory(brand_name):
    ...

def is_file_older_than(filepath, seconds):
    if not os.path.isfile(filepath):
        return True
    file_mod_time = os.path.getmtime(filepath)
    return (time.time() - file_mod_time) > seconds
    base_directory = "brands"
    directory = f"{base_directory}/{brand_name.replace(' ', '_').lower()}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory
