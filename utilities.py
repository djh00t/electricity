import os
import csv

def load_provider_urls(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        reader.fieldnames = [name.strip() for name in reader.fieldnames]
        return {row['Brand Name']: row['Retailer Base URI'].strip() for row in reader}

def ensure_brand_directory(brand_name):
    base_directory = "brands"
    directory = f"{base_directory}/{brand_name.replace(' ', '_')}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory
