from utilities import ensure_brand_directory
from get_providers import download_and_extract_pdf_data
import logging
import requests
import json
from datetime import datetime
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true', help='Enable debug logging')
args = parser.parse_args()

logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if args.debug:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Starting electricity plans script")

def fetch_plans(base_url, headers):
    page = 1
    plans = []
    logging.debug(f"Fetching plans for provider with base URL: {base_url}")
    while True:
        params = {
            'effective': 'CURRENT',
            'type': 'ALL',
            'page': str(page),
            'page-size': '1000',
            'fuelType': 'ALL'
        }
        response = requests.get(f"{base_url}cds-au/v1/energy/plans", headers=headers, params=params)
        if response.ok:
            data = response.json()
            if 'meta' in data and 'totalPages' in data['meta']:
                plans_data = data.get('data', {}).get('plans', [])
                if plans_data:
                    plans.extend(plans_data)
                    logging.debug(f"Page {page}: Retrieved {len(plans_data)} plans")
                if page >= data['meta']['totalPages']:
                    break
            else:
                logging.error(f"Missing 'meta' or 'totalPages' in response data for page {page}")
                break
        else:
            logging.error(f"Failed to fetch plans for page {page} with status code: {response.status_code}")
            break
        page += 1
    logging.debug(f"Total plans fetched: {len(plans)}")
    return plans

def save_plans_to_file(provider_name, plans):
    directory = ensure_brand_directory(provider_name)
    filename = f"{directory.replace(' ', '_')}/plans.json"
    if plans:  # If plans is not an empty list, write to file
        with open(filename, 'w') as file:
            file.write(json.dumps(plans, indent=4))
        logging.info(f"Saved {len(plans)} plans for provider '{provider_name}' to '{filename}'")
    elif os.path.exists(filename):  # If plans is empty and file exists, delete the file
        os.remove(filename)
        logging.info(f"Deleted existing file '{filename}' as no plans were fetched")
import os
from datetime import datetime, timedelta
import time

def fetch_plans(base_url, headers):
    ...

def save_plans_to_file(provider_name, plans):
    ...

def is_file_older_than(filepath, seconds):
    if not os.path.isfile(filepath):
        return True
    file_mod_time = os.path.getmtime(filepath)
    return (time.time() - file_mod_time) > seconds

def main():
    provider_data = download_and_extract_pdf_data()
    provider_urls = {provider['brand']: provider['uri'] for provider in provider_data}
    logging.info(f"Number of providers found: {len(provider_urls)}")
    headers = {'x-v': '1'}
    total_providers = 0
    total_plans = 0
    for brand, brand_url in provider_urls.items():
        logging.info(f"Processing provider: {brand}")
        plans_file_path = f"brands/{brand.replace(' ', '_').lower()}/plans.json"
        if not is_file_older_than(plans_file_path, BRAND_REFRESH_INTERVAL):
            logging.info(f"Skipping provider '{brand}' as plans.json is up-to-date.")
            continue
        plans = fetch_plans(brand_url, headers)
        if plans:
            save_plans_to_file(brand, plans)
            total_providers += 1
            total_plans += len(plans)

if __name__ == '__main__':
    main()
