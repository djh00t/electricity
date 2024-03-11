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

import concurrent.futures
from utilities import ensure_brand_directory, is_file_older_than
#from get_plan_detail import download_and_save_plan_details, setup_logging as setup_detail_logging
from config import REFRESH_DAYS
from utilities import load_provider_urls, download_and_extract_pdf_data
import logging
import os
import requests
import json
from datetime import datetime, timezone, timedelta
from datetime import datetime
import argparse
import subprocess
from pathlib import Path
from utilities import is_file_older_than, load_provider_urls, ensure_brand_directory
from concurrent.futures import ThreadPoolExecutor
from config import DETAIL_THREADS
from config import REFRESH_DAYS


parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true", help="Enable debug logging")
args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

if args.debug:
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
    )
else:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

logging.info("Starting electricity plans script")


def setup_detail_logging(debug):
    """
    Configure the logging level based on the debug flag.

    Args:
        debug (bool): If True, set logging to debug level, otherwise to info level.
    """
    if debug:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        # Note: The logging statement for skipping up-to-date plan details has been moved to the appropriate function.


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
            "effective": "CURRENT",
            "type": "ALL",
            "page": str(page),
            "page-size": "1000",
            "fuelType": "ALL",
        }
        response = requests.get(
            f"{base_url}cds-au/v1/energy/plans", headers=headers, params=params
        )
        if response.ok:
            data = response.json()
            if "meta" in data and "totalPages" in data["meta"]:
                plans_data = data.get("data", {}).get("plans", [])
                if plans_data:
                    plans.extend(plans_data)
                    logging.debug(f"Page {page}: Retrieved {len(plans_data)} plans")
                if page >= data["meta"]["totalPages"]:
                    break
            else:
                logging.error(
                    f"Missing 'meta' or 'totalPages' in response data for page {page}"
                )
                break
        else:
            logging.error(
                f"Failed to fetch plans for page {page} with status code: {response.status_code}"
            )
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
        with open(filename, "w") as file:
            file.write(json.dumps(plans, indent=4))
        logging.info(
            f"Saved {len(plans)} plans for provider '{provider_name}' to '{filename}'"
        )
    elif os.path.exists(filename):  # If plans is empty and file exists, delete the file
        os.remove(filename)
        logging.info(f"Deleted existing file '{filename}' as no plans were fetched")


def fetch_plan_details(base_url, headers, plan_id):
    """
    Fetch the details of a specific plan from the API.

    Args:
        base_url (str): The base URL for the provider's API.
        headers (dict): The headers to use for the API request.
        plan_id (str): The unique identifier for the plan.

    Returns:
        dict: The JSON response containing the plan details.
    """
    response = requests.get(f"{base_url}cds-au/v1/energy/plans/{plan_id}", headers=headers)
    return response.json()

def save_plan_details(brand_name, plan_id, plan_details):
    """
    Save the details of a plan to a JSON file.

    Args:
        brand_name (str): The name of the brand associated with the plan.
        plan_id (str): The unique identifier for the plan.
        plan_details (dict): The plan details to save.
    """
    brand_directory = ensure_brand_directory(brand_name)
    filename = f"{brand_directory}/{plan_id}.json"
    last_downloaded = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    plan_details['meta'] = {'lastDownloaded': last_downloaded}
    with open(filename, 'w') as file:
        json.dump(plan_details, file, indent=4)
    logging.info(f"Plan details for plan ID '{plan_id}' were saved.")

def update_plan_details(brand, plan_ids, base_url, headers):
    """
    Update the plan details for the given brand and plan IDs.

    Args:
        brand (str): The brand name.
        plan_ids (list): A list of plan IDs.
        base_url (str): The base URL for downloading plan details.
        headers (dict): The headers to be used for the HTTP request.

    Returns:
        None
    """
def update_plan_details(brand, plan_ids, base_url, headers):
    def download_and_save(plan_id):
        brand_sanitized = brand.replace(' ', '_').lower()
        # plan_detail_file variable is now correctly defined inside the loop
        if os.path.isfile(plan_detail_file):  # Check if the plan detail file exists
            logging.info(f"Plan detail file exists: {plan_detail_file}")
            with open(plan_detail_file, 'r') as file:
                plan_data = json.load(file)
            last_downloaded_str = plan_data.get('meta', {}).get('lastDownloaded')
            if last_downloaded_str:
                last_downloaded = datetime.strptime(last_downloaded_str, "%Y-%m-%dT%H:%M:%S.000Z").replace(tzinfo=timezone.utc)
                current_time = datetime.now(timezone.utc)
                if (current_time - last_downloaded) < timedelta(days=REFRESH_DAYS):
                    logging.info(f"Skipping plan detail for '{plan_id}' as it is up-to-date.")
                    return
                else:
                    logging.info(f"Downloading plan detail for '{plan_id}'.")
            else:
                logging.info(f"Downloading plan detail for '{plan_id}' due to missing 'lastDownloaded'.")
        else:
            logging.info(f"Plan detail file does not exist: {plan_detail_file}")
            logging.info(f"Downloading plan detail for '{plan_id}' as file does not exist.")
        plan_details = fetch_plan_details(base_url, headers, plan_id)
        save_plan_details(brand, plan_id, plan_details)

    with ThreadPoolExecutor(max_workers=DETAIL_THREADS) as executor:
        futures = [executor.submit(download_and_save, plan_id) for plan_id in plan_ids]
        for future in concurrent.futures.as_completed(futures):
            future.result()  # This will raise any exceptions caught by the worker threads
            # Removed incorrect code block that was outside the loop


def setup_logging(debug):
    """
    Sets up the logging configuration.
    If debug is True, set the logging level to DEBUG, otherwise set it to INFO.
    """
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s")


def main():
    """
    The main function that orchestrates the fetching and saving of electricity plans.

    It processes command-line arguments, sets up logging, and iterates over provider URLs
    to fetch and save plans. It uses the 'BRAND_REFRESH_INTERVAL' to determine whether
    to refresh the plans for a provider.
    """
    parser = argparse.ArgumentParser(description="Fetch and save electricity plans.")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    setup_logging(args.debug)
    # Set up logging for the detail module as well
    setup_detail_logging(args.debug)

    provider_urls = load_provider_urls()
    logging.info(f"Number of providers found: {len(provider_urls)}")
    headers = {"x-v": "1"}
    total_providers = 0
    total_plans = 0
    for brand, brand_url in provider_urls.items():
        brand_sanitized = brand.replace(' ', '_').lower()
        plans_file_path = f"brands/{brand_sanitized}/plans.json"
        if is_file_older_than(plans_file_path, REFRESH_DAYS * 24 * 60 * 60):
            logging.info(f"Processing provider: {brand}")
            plans = fetch_plans(brand_url, headers)
            if plans:
                save_plans_to_file(brand, plans)
                total_providers += 1
                total_plans += len(plans)
        # Check if individual plan details are up-to-date
        if os.path.exists(plans_file_path):
            with open(plans_file_path, 'r') as file:
                plans = json.load(file)
            plan_ids = [plan["planId"] for plan in plans]
            update_plan_details(brand, plan_ids, brand_url, headers)
        logging.info(f"Processing provider: {brand}")
        plans = fetch_plans(brand_url, headers)
        if plans:
            save_plans_to_file(brand, plans)
            plan_ids = [plan["planId"] for plan in plans]
            update_plan_details(brand, plan_ids, brand_url, headers)
            total_providers += 1
            total_plans += len(plans)


if __name__ == "__main__":
    main()
