import csv
import os
import requests
from datetime import datetime

def load_provider_urls(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        next(reader, None)  # Skip the header row
        return {row['Brand Name']: row['Retailer Base URI'] for row in reader if row['Brand Name']}

def fetch_plans(base_url, headers):
    page = 1
    plans = []
    while True:
        params = {
            'effective': 'CURRENT',
            'type': 'ALL',
            'page': str(page),
            'page-size': '100',
            'fuelType': 'ALL'
        }
        response = requests.get(f"{base_url}cds-au/v1/energy/plans", headers=headers, params=params)
        data = response.json()
        plans.extend(data['data'])
        if page >= data['meta']['totalPages']:
            break
        page += 1
    return plans

def save_plans_to_file(provider_name, plans):
    directory = "plans"
    if not os.path.exists(directory):
        os.makedirs(directory)
    date_str = datetime.now().strftime('%Y%m%d')
    filename = f"{directory}/{date_str}_{provider_name.replace(' ', '_')}.json"
    with open(filename, 'w') as f:
        f.write(json.dumps(plans, indent=4))

def main():
    provider_urls = load_provider_urls('electricity_plan_urls.csv')
    headers = {'x-v': '1'}
    for provider_name, base_url in provider_urls.items():
        plans = fetch_plans(base_url, headers)
        save_plans_to_file(provider_name, plans)

if __name__ == '__main__':
    main()
