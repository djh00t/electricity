import argparse
import os
import json

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
    return [plan.get('displayName') for plan in filtered_plans]

def main():
    parser = argparse.ArgumentParser(description='Search for electricity plans by postcode.')
    parser.add_argument('--postcode', required=True, type=str, help='Postcode to filter plans by.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--providers', action='store_true', help='Return a list of provider brand names.')
    group.add_argument('--plans', action='store_true', help='Return a list of plan display names.')
    args = parser.parse_args()

    plans_data = load_plans_from_directory('plans')
    filtered_plans = filter_plans_by_postcode(plans_data, args.postcode)

    if args.providers:
        providers = get_providers_from_plans(filtered_plans)
        print(providers)
    elif args.plans:
        plan_names = get_plan_names_from_plans(filtered_plans)
        print(plan_names)

if __name__ == '__main__':
    main()
