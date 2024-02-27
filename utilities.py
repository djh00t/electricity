import csv

def load_provider_urls(filename):
    with open(filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        reader.fieldnames = [name.strip() for name in reader.fieldnames]
        return {row['Brand Name']: row['Retailer Base URI'].strip() for row in reader}
