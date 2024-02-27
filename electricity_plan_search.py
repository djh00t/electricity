import argparse
import os
import json
import csv
from tabulate import tabulate

def load_plans_from_directory(directory):
    plans_data = []
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            with open(os.path.join(directory, filename), 'r') as file:
                plans_data.extend(json.load(file))
    return plans_data

def filter_plans_by_postcode(plans_data, postcode):
    return [plan for plan in plans_data if postcode in plan.get('geography', {}).get('includedPostcodes', [])]

def get_providers_from_plans(filtered_plans):
    return list(set(plan.get('brandName') for plan in filtered_plans))

def get_plan_names_from_plans(filtered_plans):
    return [{
        'displayName': plan.get('displayName'),
        'planId': plan.get('planId'),
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

def output_results_as_text(results, header):
    print(tabulate(results, headers=header, tablefmt='grid'))

def main():
    parser = argparse.ArgumentParser(description='Search for electricity plans by postcode.')
    parser.add_argument('--postcode', required=True, type=str, help='Postcode to filter plans by.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--providers', action='store_true', help='Return a list of provider brand names.')
    group.add_argument('--plans', action='store_true', help='Return a list of plan display names.')
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument('--json', action='store_true', help='Output results in JSON format.')
    output_group.add_argument('--csv', action='store_true', help='Output results in CSV format.')
    output_group.add_argument('--text', action='store_true', help='Output results in table format.')
    args = parser.parse_args()

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
        else:  # Default to text output
            output_results_as_text(plan_names, ['Display Name', 'Plan ID', 'Fuel Type', 'Distributors', 'Customer Type'])

if __name__ == '__main__':
    main()
