import os
from get_providers import download_and_extract_pdf_data

def load_provider_urls():
    url = 'https://www.aer.gov.au/documents/consumer-data-right-list-energy-retailer-base-uris-june-2023'
    provider_data = download_and_extract_pdf_data(url)
    return {provider['brand']: provider['uri'] for provider in provider_data}

def ensure_brand_directory(brand_name):
    base_directory = "brands"
    directory = f"{base_directory}/{brand_name.replace(' ', '_').lower()}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory
