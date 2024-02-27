import argparse, sys
import os
import json
import requests
import re

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

    # Search for the provider name by looking through the JSON files in the plans directory
    plans_directory = 'plans'
    provider_name = None
    for filename in os.listdir(plans_directory):
        if re.match(r'\d{8}_.*\.json$', filename):
            with open(os.path.join(plans_directory, filename), 'r') as file:
                plans = json.load(file)
                for plan in plans:
                    if plan.get('planId') == args.planId:
                        provider_name = plan.get('brandName')
                        break
        if provider_name:
            break

    if not provider_name:
        sys.stderr.write(f"Error: The planId '{args.planId}' was not found in any plan files.\n")
        sys.exit(1)

    # Load provider URLs from the CSV file to get the base URL
    provider_urls = load_provider_urls('electricity_plan_urls.csv')
    base_url = provider_urls.get(provider_name)
    if not base_url:
        sys.stderr.write(f"Error: The provider name '{provider_name}' was not found in provider URLs.\n")
        sys.exit(1)

    headers = {'x-v': '1'}
    plan_details = fetch_plan_details(base_url, headers, args.planId)
    save_plan_details(provider_name, args.planId, plan_details)
    save_plan_details(brand, args.planId, plan_details)

if __name__ == '__main__':
    main()
from utilities import load_provider_urls
