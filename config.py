"""
Configuration settings for the project.
"""
RETAILER_PDF_URL = 'https://www.aer.gov.au/documents/consumer-data-right-list-energy-retailer-base-uris-june-2023'

# How often plans.json should be updated (in seconds)

# Number of days after which the plan should be refreshed
REFRESH_DAYS = 7

# Number of parallel processes for checking plan details
DETAIL_THREADS = 10
