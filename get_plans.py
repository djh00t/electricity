"""
Script to fetch and save electricity plans from providers.

This script fetches electricity plans from a list of provider URLs and saves them to JSON files.
Each provider's plans are saved in a directory named after the provider within a 'brands' directory.

The script uses the 'x-v: 1' header for API requests and queries the API with specific parameters
to retrieve current plans of all types and fuel types, paginating through results as necessary.

Plans are saved to 'brands/{brand}/plans.json' and include a 'meta.lastDownloaded' field with the
current datetime in UTC. Directories are created as needed. Plans are only updated if they are
older than the interval specified by 'BRAND_REFRESH_INTERVAL' in 'config.py'.

Usage:
    python get_plans.py [--debug]

Options:
    --debug  Enable debug logging for more verbose output.

Example:
    python get_plans.py --debug
"""

from utilities import ensure_brand_directory, is_file_older_than
from config import BRAND_REFRESH_INTERVAL
from get_providers import download_and_extract_pdf_data
import logging
import os
import requests
import json
from datetime import datetime
import argparse
import subprocess
from pathlib import Path
from utilities import is_file_older_than
from config import REFRESH_DAYS

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
    """
    Fetches all plans for a given provider using their base URL.

    Args:
        base_url (str): The base URL of the provider's API endpoint.
        headers (dict): The headers to use for the API request.

    Returns:
        list: A list of plan dictionaries fetched from the provider.
    """
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
    """
    Saves a list of plans to a JSON file for a given provider.

    Args:
        provider_name (str): The name of the provider.
        plans (list): The list of plans to save.

    The function creates a directory for the provider if it does not exist,
    and either writes the plans to a file or deletes the existing file if no plans are fetched.
    """
    directory = ensure_brand_directory(provider_name)
    filename = f"{directory.replace(' ', '_')}/plans.json"
    if plans:  # If plans is not an empty list, write to file
        with open(filename, 'w') as file:
            file.write(json.dumps(plans, indent=4))
        logging.info(f"Saved {len(plans)} plans for provider '{provider_name}' to '{filename}'")
    elif os.path.exists(filename):  # If plans is empty and file exists, delete the file
        os.remove(filename)
        logging.info(f"Deleted existing file '{filename}' as no plans were fetched")


def update_plan_details(brand, plan_ids):
    for plan_id in plan_ids:
        plan_detail_file = Path(f"brands/{brand}/{plan_id}.json")
        if not is_file_older_than(plan_detail_file, REFRESH_DAYS * 24 * 60 * 60):
            logging.info(f"Skipping plan detail for '{plan_id}' as it is up-to-date.")
            continue
        logging.info(f"Updating plan detail for '{plan_id}'.")
        subprocess.run(['python', 'get_plan_detail.py', plan_id], check=True)

def main():
    """
    The main function that orchestrates the fetching and saving of electricity plans.

    It processes command-line arguments, sets up logging, and iterates over provider URLs
    to fetch and save plans. It uses the 'BRAND_REFRESH_INTERVAL' to determine whether
    to refresh the plans for a provider.
    """
    provider_data = download_and_extract_pdf_data()
    provider_urls = {provider['brand']: provider['uri'] for provider in provider_data}
    logging.info(f"Number of providers found: {len(provider_urls)}")
    headers = {'x-v': '1'}
    total_providers = 0
    total_plans = 0
    for brand, brand_url in provider_urls.items():
        plans_file_path = f"brands/{brand.replace(' ', '_').lower()}/plans.json"
        if not is_file_older_than(plans_file_path, BRAND_REFRESH_INTERVAL):
            logging.info(f"Skipping provider '{brand}' as plans.json is up-to-date.")
            continue
        logging.info(f"Processing provider: {brand}")
        plans = fetch_plans(brand_url, headers)
        if plans:
            save_plans_to_file(brand, plans)
            plan_ids = [plan['planId'] for plan in plans]
            update_plan_details(brand, plan_ids)
            total_providers += 1
            total_plans += len(plans)

if __name__ == '__main__':
    main()
