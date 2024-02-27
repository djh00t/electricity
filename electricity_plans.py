import csv
import os
import requests
import json
from datetime import datetime
import logging
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--debug', action='store_true', help='Enable debug logging')
args = parser.parse_args()

if args.debug:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
else:
    logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def load_provider_urls(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        reader.fieldnames = [name.strip() for name in reader.fieldnames]
        return {row['Brand Name']: row['Retailer Base URI'].strip() for row in reader}

def fetch_plans(base_url, headers):
    page = 1
    plans = []
    logging.info(f"Fetching plans for provider with base URL: {base_url}")
    while True:
        params = {
            'effective': 'CURRENT',
            'type': 'ALL',
            'page': str(page),
            'page-size': '100',
            'fuelType': 'ALL'
        }
        response = requests.get(f"{base_url}cds-au/v1/energy/plans", headers=headers, params=params)
        data = response.json()
        plans_data = data.get('data', {}).get('plans', [])
        if plans_data:
            plans.extend(plans_data)
            logging.info(f"Page {page}: Retrieved {len(plans_data)} plans")
        if page >= data['meta']['totalPages']:
            break
        page += 1
    logging.info(f"Total plans fetched: {len(plans)}")
    return plans

def save_plans_to_file(provider_name, plans):
    directory = "plans"
    if not os.path.exists(directory):
        os.makedirs(directory)
    date_str = datetime.now().strftime('%Y%m%d')
    filename = f"{directory}/{date_str}_{provider_name.replace(' ', '_')}.json"
    if plans:  # If plans is not an empty list, write to file
        with open(filename, 'w') as file:
            file.write(json.dumps(plans, indent=4))
        logging.info(f"Saved {len(plans)} plans for provider '{provider_name}' to '{filename}'")
    elif os.path.exists(filename):  # If plans is empty and file exists, delete the file
        os.remove(filename)
        logging.info(f"Deleted existing file '{filename}' as no plans were fetched")

def main():
    provider_urls = load_provider_urls('electricity_plan_urls.csv')
    headers = {'x-v': '1'}
    total_providers = 0
    total_plans = 0
    for brand, brand_url in provider_urls.items():
        logging.info(f"Processing provider: {brand}")
        plans = fetch_plans(brand_url, headers)
        save_plans_to_file(brand, plans)
        total_providers += 1
        total_plans += len(plans)
    logging.info(f"Finished processing. Total providers: {total_providers}, Total plans: {total_plans}")

if __name__ == '__main__':
    main()
