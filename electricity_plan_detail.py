import argparse, sys
from utilities import load_provider_urls, ensure_brand_directory
import logging
import json
import requests
import re

def fetch_plan_details(base_url, headers, plan_id):
    response = requests.get(f"{base_url}cds-au/v1/energy/plans/{plan_id}", headers=headers)
    return response.json()

def setup_logging(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from utilities import load_provider_urls

def save_plan_details(brand, plan_id, plan_details):
    brand_directory = ensure_brand_directory(brand)
    filename = f"{brand_directory}/{plan_id}.json"
    with open(filename, 'w') as file:
        json.dump(plan_details, file, indent=4)

def main():
    parser = argparse.ArgumentParser(description='Fetch and save plan details.')
    parser.add_argument('planId', type=str, help='The planId to fetch details for.')
    args = parser.parse_args()
    setup_logging(args.debug)

    # Search for the brand by looking through the JSON files in the plans directory
    # Search for the provider name by looking through the JSON files in the plans directory
    plans_directory = 'plans'
    brand = None
    for brand_directory in os.listdir(plans_directory):
        brand_path = os.path.join(plans_directory, brand_directory)
        if os.path.isdir(brand_path):
            plans_file = os.path.join(brand_path, 'plans.json')
            if os.path.exists(plans_file):
                with open(plans_file, 'r') as file:
                    plans = json.load(file)
                    for plan in plans:
                        if plan.get('planId') == args.planId:
                            brand = plan.get('brandName')
                            break
        if brand:
            break

    if not brand:
        sys.stderr.write(f"Error: The planId '{args.planId}' was not found in any plan files.\n")
        sys.exit(1)

    # Load provider URLs from the CSV file to get the base URL
    provider_urls = load_provider_urls('electricity_plan_urls.csv')
    base_url = provider_urls.get(brand)
    if not base_url:
        sys.stderr.write(f"Error: The brand '{brand}' was not found in provider URLs.\n")
        sys.exit(1)

    headers = {'x-v': '1'}
    plan_details = fetch_plan_details(base_url, headers, args.planId)
    save_plan_details(brand, args.planId, plan_details)
    save_plan_details(brand, args.planId, plan_details)

if __name__ == '__main__':
    main()
from utilities import load_provider_urls
