import argparse
import os
import logging
import json
import csv
from tabulate import tabulate

def load_plans_from_directory(directory):
    plans_data = []
    for brand_directory in os.listdir(directory):
        brand_path = os.path.join(directory, brand_directory)
        if os.path.isdir(brand_path):
            plans_file = os.path.join(brand_path, 'plans.json')
            if os.path.exists(plans_file):
                with open(plans_file, 'r') as file:
                    plans_data.extend(json.load(file))
    return plans_data

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

    plans_data = load_plans_from_directory('plans')
    filtered_plans = filter_plans_by_postcode(plans_data, args.postcode)

    if args.providers:
        providers = get_providers_from_plans(filtered_plans)
        if args.json:
            output_results_as_json(providers)
        elif args.csv:
            output_results_as_csv(providers, ['Provider'])
        else:  # Default to text output
            output_results_as_text(providers, ['Provider'])
    elif args.plans:
        plan_names = get_plan_names_from_plans(filtered_plans)
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
