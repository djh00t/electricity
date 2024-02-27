import argparse, os
from utilities import ensure_brand_directory, load_provider_urls
import logging
import json
import csv
import subprocess
from tabulate import tabulate
from electricity_plan_detail import fetch_plan_details, save_plan_details
from electricity_plan_detail import should_refresh_plan
import sys
import logging

def filter_plans_by_postcode(plans_data, postcode):
    return [plan for plan in plans_data if postcode in plan.get('geography', {}).get('includedPostcodes', [])]

def get_providers_from_plans(filtered_plans):
    return list(set(plan.get('brandName') for plan in filtered_plans))

def get_plan_names_from_plans(filtered_plans):
    return [{
        'brandName': plan.get('brandName'),
        'planId': plan.get('planId'),
        'displayName': plan.get('displayName'),
        'fuelType': plan.get('fuelType'),
        'distributors': plan.get('geography', {}).get('distributors', []),
        'customerType': plan.get('customerType')
    } for plan in filtered_plans]

def output_results_as_json(results):
    print(json.dumps(results, indent=4))

def output_results_as_csv(results, header):
    writer = csv.DictWriter(sys.stdout, fieldnames=header)
    writer.writeheader()
    for row in results:
        writer.writerow(row)

def output_results_as_text(results):
    print(tabulate(results, headers='keys', tablefmt='grid'))

def main():
    parser = argparse.ArgumentParser(description='Search for electricity plans by postcode.')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--postcode', required=True, type=str, help='Postcode to filter plans by.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--providers', action='store_true', help='Return a list of provider brand names.')
    group.add_argument('--plans', action='store_true', help='Return a list of plan display names.')
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('--json', action='store_true', help='Output results in JSON format.')
    output_group.add_argument('--csv', action='store_true', help='Output results in CSV format.')
    output_group.add_argument('--text', action='store_true', help='Output results in table format.')
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def load_plans_from_all_brands():
        plans_data = []
        for brand_directory in os.listdir('brands'):
            plans_file = ensure_brand_directory(brand_directory) + '/plans.json'
            if os.path.isfile(plans_file):
                with open(plans_file, 'r') as file:
                    plans_data.extend(json.load(file))
        return plans_data

    plans_data = load_plans_from_all_brands()    
    filtered_plans = filter_plans_by_postcode(plans_data, args.postcode)
    provider_urls = load_provider_urls('electricity_plan_urls.csv')
    headers = {'x-v': '1'}
    normalized_provider_urls = {name.lower().replace(' ', '_'): url for name, url in provider_urls.items()}


    # The rest of the main function code goes here, but it's not duplicated.
    args = parser.parse_args()
    filtered_plans = filter_plans_by_postcode(plans_data, args.postcode)
    normalized_provider_urls = {name.lower().replace(' ', '_'): url for name, url in provider_urls.items()}
    headers = {'x-v': '1'}

    if args.providers:
        providers = get_providers_from_plans(filtered_plans)
    elif args.plans:
        plan_names = get_plan_names_from_plans(filtered_plans)
        for plan in plan_names:
            brand_name = plan['brandName']
            plan_id = plan['planId']
            normalized_brand_name = brand_name.lower().replace(' ', '_')
            base_url = normalized_provider_urls.get(normalized_brand_name)
            if base_url:
                plan_filename = f"brands/{normalized_brand_name}/{plan_id}.json"
                if should_refresh_plan(plan_filename):
                    plan_details = fetch_plan_details(base_url, headers, plan_id)
                    save_plan_details(brand_name, plan_id, plan_details)
            else:
                logging.info(f"Plan details for plan ID '{plan_id}' were skipped as they are up to date.")
    else:
        logging.error(f"Base URL for provider '{brand_name}' not found. Looked up as '{normalized_brand_name}'.")

    # Output results after fetching and saving all plan details
    if args.providers:
        if args.json:
            output_results_as_json(providers)
        elif args.csv:
            output_results_as_csv(providers, ['Provider'])
        else:  # Default to text output
            output_results_as_text(providers)
    elif args.plans:
        if args.json:
            output_results_as_json(plan_names)
        elif args.csv:
            output_results_as_csv(plan_names, ['displayName', 'planId', 'fuelType', 'distributors', 'customerType'])
        elif args.text:
            output_results_as_text(plan_names)
        else:  # Default to text output
            output_results_as_text(plan_names)

if __name__ == '__main__':
    main()
    # Ensure this is the end of the main function and there are no duplicates.
