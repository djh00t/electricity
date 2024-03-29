import argparse, sys
import os
from datetime import datetime, timezone
from utilities import load_provider_urls, ensure_brand_directory
import logging
import json
import requests
from datetime import datetime, timezone, timedelta
from concurrent.futures import ProcessPoolExecutor

def check_plan_exists(filename):
    exists = os.path.isfile(filename)
    updated = False
    if exists:
        with open(filename, 'r') as file:
            plan_data = json.load(file)
        last_downloaded_str = plan_data.get('meta', {}).get('lastDownloaded')
        if last_downloaded_str:
            last_downloaded = datetime.strptime(last_downloaded_str, "%Y-%m-%dT%H:%M:%S.000Z").replace(tzinfo=timezone.utc)
            current_time = datetime.now(timezone.utc)
            time_difference = current_time - last_downloaded
            if time_difference > timedelta(days=REFRESH_DAYS):
                updated = True
    return exists, updated

def download_and_save_plan_details(plan_info):
    brand_name, plan_id, base_url, headers = plan_info
    plan_details = fetch_plan_details(base_url, headers, plan_id)
    save_plan_details(brand_name, plan_id, plan_details)

REFRESH_DAYS = 1  # Number of days after which the plan should be refreshed
DETAIL_THREADS = 10  # Number of parallel processes for checking plan details

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

def check_refresh_plan(filename):
    needs_refresh = False
    try:
        if not os.path.exists(filename):
            logging.info(f"Plan file '{filename}' does not exist. It will be downloaded.")
            needs_refresh = True
        else:
            with open(filename, 'r') as file:
                plan_data = json.load(file)
            last_downloaded_str = plan_data.get('meta', {}).get('lastDownloaded')
            if last_downloaded_str:
                last_downloaded = datetime.strptime(last_downloaded_str, "%Y-%m-%dT%H:%M:%S.000Z").replace(tzinfo=timezone.utc)
                current_time = datetime.now(timezone.utc)
                time_difference = current_time - last_downloaded
                days_difference = time_difference.days
                logging.info(f"Plan file '{filename}' exists. Current UTC time: {current_time.strftime('%Y-%m-%dT%H:%M:%S.000Z')}, Last downloaded: {last_downloaded_str}, Days difference: {days_difference}")
                if time_difference > timedelta(days=REFRESH_DAYS):
                    needs_refresh = True
    except Exception as e:
        logging.error(f"Error checking if plan '{filename}' needs refresh: {e}")
    return filename, needs_refresh

def should_refresh_plans(filenames):
    with ProcessPoolExecutor(max_workers=DETAIL_THREADS) as executor:
        results = executor.map(check_refresh_plan, filenames)
    return {filename: needs_refresh for filename, needs_refresh in results}

def save_plan_details(brand_name, plan_id, plan_details):
    brand_directory = ensure_brand_directory(brand_name)
    filename = f"{brand_directory}/{plan_id}.json"
    last_downloaded = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    plan_details['meta'] = {'lastDownloaded': last_downloaded}
    with open(filename, 'w') as file:
        json.dump(plan_details, file, indent=4)
    # logging.info(f"Plan details for plan ID '{plan_id}' were refreshed.")

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
    plan_filename = f"{ensure_brand_directory(brand)}/{args.planId}.json"
    if should_refresh_plan(plan_filename):
        plan_details = fetch_plan_details(base_url, headers, args.planId)
        save_plan_details(brand, args.planId, plan_details)
        logging.info(f"Plan details for plan ID '{args.planId}' were downloaded and saved.")
    else:
        logging.info(f"Plan details for plan ID '{args.planId}' were skipped as they are up to date.")
    # logging.info(f"Plan details for plan ID '{plan_id}' were refreshed.")

if __name__ == '__main__':
    main()