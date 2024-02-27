from utilities import load_provider_urls
import os
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
            'page-size': '100',
            'fuelType': 'ALL'
        }
        response = requests.get(f"{base_url}cds-au/v1/energy/plans", headers=headers, params=params)
        data = response.json()  # Assuming response is always JSON and successful
        plans_data = data.get('data', {}).get('plans', [])
        if plans_data:
            plans.extend(plans_data)
            logging.info(f"Page {page}: Retrieved {len(plans_data)} plans")
        if page >= data['meta']['totalPages']:
            break
        page += 1
    logging.debug(f"Total plans fetched: {len(plans)}")
    return plans

def save_plans_to_file(provider_name, plans):
    base_directory = "brands"
    directory = f"{base_directory}/{provider_name}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = f"{directory}/plans.json"
    if plans:  # If plans is not an empty list, write to file
        with open(filename, 'w') as file:
            file.write(json.dumps(plans, indent=4))
        logging.info(f"Saved {len(plans)} plans for provider '{provider_name}' to '{filename}'")
    elif os.path.exists(filename):  # If plans is empty and file exists, delete the file
        os.remove(filename)
        logging.info(f"Deleted existing file '{filename}' as no plans were fetched")

def main():
    base_directory = "brands"
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)
    provider_urls = load_provider_urls('electricity_plan_urls.csv')
    headers = {'x-v': '1'}
    total_providers = 0
    total_plans = 0
    for brand, brand_url in provider_urls.items():
        logging.info(f"Processing provider: {brand}")
        plans = fetch_plans(brand_url, headers)
        if plans:
            save_plans_to_file(brand, plans)
            total_providers += 1
            total_plans += len(plans)

if __name__ == '__main__':
    main()
