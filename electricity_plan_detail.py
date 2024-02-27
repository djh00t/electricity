import argparse, sys
import os
import json
import requests

def fetch_plan_details(base_url, headers, plan_id):
    response = requests.get(f"{base_url}cds-au/v1/energy/plans/{plan_id}", headers=headers)
    return response.json()
from utilities import load_provider_urls

def save_plan_details(brand, plan_id, plan_details):
    brand_directory = f"plans/{brand}"
    if not os.path.exists(brand_directory):
        os.makedirs(brand_directory)
    filename = f"{brand_directory}/{plan_id}.json"
    with open(filename, 'w') as file:
        json.dump(plan_details, file, indent=4)

def main():
    parser = argparse.ArgumentParser(description='Fetch and save plan details.')
    parser.add_argument('planId', type=str, help='The planId to fetch details for.')
    args = parser.parse_args()

    # Load provider URLs from the CSV file
    provider_urls = load_provider_urls('electricity_plan_urls.csv')

    # Extract brand and base URL for the given planId
    brand, base_url = next((brand, url) for brand, url in provider_urls.items() if args.planId in url)

    headers = {'x-v': '1'}
    plan_details = fetch_plan_details(base_url, headers, args.planId)
    save_plan_details(brand, args.planId, plan_details)

if __name__ == '__main__':
    main()
from utilities import load_provider_urls
