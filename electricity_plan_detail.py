import argparse, sys
import os
from datetime import datetime, timezone
from utilities import load_provider_urls, ensure_brand_directory
import logging
import json
import requests
from datetime import datetime, timezone, timedelta

REFRESH_DAYS = 1  # Number of days after which the plan should be refreshed

def fetch_plan_details(base_url, headers, plan_id):
    response = requests.get(f"{base_url}cds-au/v1/energy/plans/{plan_id}", headers=headers)
    return response.json()

def setup_logging(debug):
    if debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.info(f"Plan details for plan ID '{plan_id}' were skipped as they are up to date.")
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from utilities import load_provider_urls

def save_plan_details(brand_name, plan_id, plan_details):
    brand_directory = ensure_brand_directory(brand_name)
    filename = f"{brand_directory}/{plan_id}.json"
    if should_refresh_plan(filename):
        last_downloaded = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        plan_details['meta'] = {'lastDownloaded': last_downloaded}
        with open(filename, 'w') as file:
            json.dump(plan_details, file, indent=4)
        logging.info(f"Plan details for plan ID '{plan_id}' were refreshed.")

def should_refresh_plan(filename):
    if not os.path.exists(filename):
        return True
    with open(filename, 'r') as file:
        plan_data = json.load(file)
    last_downloaded_str = plan_data.get('meta', {}).get('lastDownloaded')
    if last_downloaded_str:
        last_downloaded = datetime.strptime(last_downloaded_str, "%Y-%m-%dT%H:%M:%S.000Z").replace(tzinfo=timezone.utc)
        if datetime.now(timezone.utc) - last_downloaded > timedelta(days=REFRESH_DAYS):
            return True
    return False

def main():
    parser = argparse.ArgumentParser(description='Fetch and save plan details.')
    parser.add_argument('planId', type=str, help='The planId to fetch details for.')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    setup_logging(args.debug)

    # Search for the brand by looking through the JSON files in the plans directory
    # Search for the provider name by looking through the JSON files in the plans directory
    plans_directory = ensure_brand_directory('')
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
    if should_refresh_plan(f"{ensure_brand_directory(brand)}/{args.planId}.json"):
        save_plan_details(brand, args.planId, plan_details)
    save_plan_details(brand, args.planId, plan_details)

if __name__ == '__main__':
    main()
from utilities import load_provider_urls
