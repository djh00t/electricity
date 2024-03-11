"""
Configuration settings for the project.
"""
RETAILER_PDF_URL = 'https://www.aer.gov.au/documents/consumer-data-right-list-energy-retailer-base-uris-june-2023'

# How often plans.json should be updated (in seconds)
BRAND_REFRESH_INTERVAL = 60 * 60 * 24  # 24 hours

# Number of days after which the plan should be refreshed
REFRESH_DAYS = 1

# Number of parallel processes for checking plan details
DETAIL_THREADS = 10
