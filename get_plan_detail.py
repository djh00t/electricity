"""
Script to download and update individual electricity plan details.

This module provides functionality to download and update the details for each
electricity plan specified in the brands/{brand}/plans.json file. It saves the
updated plan details into individual JSON files named brands/{brand}/{planId}.json.
It also checks if the existing plan details are older than a specified number of
days (REFRESH_DAYS) before deciding to update them, to avoid unnecessary downloads.

Functions:
    check_plan_exists(filename): Check if a plan's details file exists and needs updating.
    fetch_plan_details(base_url, headers, plan_id): Fetch plan details from the API.
    setup_logging(debug): Configure the logging level.
    check_refresh_plan(filename): Determine if a plan's details need to be refreshed.
    should_refresh_plans(filenames): Check multiple plans to determine if they need refreshing.
    save_plan_details(brand_name, plan_id, plan_details): Save plan details to a JSON file.
    download_and_save_plan_details(plan_info): Download and save plan details given plan info.

This module is designed to be imported and used by `get_plans.py`.

import argparse, sys
import os
from config import REFRESH_DAYS, DETAIL_THREADS
from datetime import datetime, timezone, timedelta
from utilities import ensure_brand_directory
import logging
import json
import requests
from concurrent.futures import ProcessPoolExecutor
from utilities import load_provider_urls

def check_plan_exists(filename):
    """
    Check if a plan's details file exists and whether it needs to be updated.

    Args:
        filename (str): The path to the plan's JSON file.

    Returns:
        tuple: A tuple containing a boolean indicating if the file exists and
               a boolean indicating if the file is outdated and needs an update.
    """
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

def setup_logging(debug):
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

def check_refresh_plan(filename):
    """
    Determine if a plan's details file needs to be refreshed based on its last downloaded date.

    Args:
        filename (str): The path to the plan's JSON file.

    Returns:
        tuple: A tuple containing the filename and a boolean indicating if the file needs refreshing.
    """
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
    """
    Determine which plans need their details refreshed.

    Args:
        filenames (list): A list of filenames for plan details JSON files.

    Returns:
        dict: A dictionary mapping filenames to booleans indicating if they need refreshing.
    """
    with ProcessPoolExecutor(max_workers=config.DETAIL_THREADS) as executor:
        results = executor.map(check_refresh_plan, filenames)
    return {filename: needs_refresh for filename, needs_refresh in results}

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

    parser = argparse.ArgumentParser(description='Fetch and save plan details.')
    parser.add_argument('planId', type=str, help='The planId to fetch details for.')
    parser.add_argument('brand', type=str, help='The brand name to fetch details for.')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    args = parser.parse_args()
    setup_logging(args.debug)

    brand = args.brand
    if not brand:
        sys.stderr.write("Error: Brand name is required.\n")
        sys.exit(1)

    plan_id = args.planId
    if not plan_id:
        sys.stderr.write("Error: Plan ID is required.\n")
        sys.exit(1)

    # Load provider URLs
    provider_urls = load_provider_urls()
    base_url = provider_urls.get(brand)
    if not base_url:
        sys.stderr.write(f"Error: The brand '{brand}' was not found in provider URLs.\n")
        sys.exit(1)

    headers = {'x-v': '1'}
    plan_filename = f"{ensure_brand_directory(brand)}/{args.planId}.json"
    if check_refresh_plan(plan_filename)[1]:
        plan_details = fetch_plan_details(base_url, headers, args.planId)
        save_plan_details(brand, args.planId, plan_details)
        logging.info(f"Plan details for plan ID '{args.planId}' were downloaded and saved.")
    else:
        logging.info(f"Plan details for plan ID '{args.planId}' are up to date and were not refreshed.")
    # logging.info(f"Plan details for plan ID '{plan_id}' were refreshed.")

def download_and_save_plan_details(plan_info):
    """
    Download and save the details of a plan given its information.

    Args:
        plan_info (tuple): A tuple containing the brand name, plan ID, base URL, and headers.
    """
    brand_name, plan_id, base_url, headers = plan_info
    plan_details = fetch_plan_details(base_url, headers, plan_id)
    save_plan_details(brand_name, plan_id, plan_details)

if __name__ == '__main__':
    # Entry point for the script when run as a standalone program.
    main()
