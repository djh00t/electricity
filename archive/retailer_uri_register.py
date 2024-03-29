import requests
from bs4 import BeautifulSoup
import urllib.parse
import fitz  # PyMuPDF
import logging

# Configure logging
logger = logging.getLogger(__name__)

def extract_pdf_data(pdf_path):
    """Extracts retailer data from a PDF file."""
def extract_pdf_data(pdf_path):
    """
    Extracts retailer data from a PDF file.

    Args:
        pdf_path (str): The file path to the PDF from which to extract data.

    Returns:
        list of dict: A list of dictionaries containing retailer 'brand' and 'uri'.
    """
    logger.debug(f"Opening PDF file: {pdf_path}")
    retailer_data = []
    with fitz.open(pdf_path) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf.load_page(page_num)
            text = page.get_text("text")
            lines = text.split('\n')
            i = 0
            while i < len(lines) - 1:
                if "Change log" in lines[i]:
                    break  # Stop processing if "Change log" is found
                brand, uri = lines[i].strip(), lines[i + 1].strip()
                if uri.lower().startswith('http') and 'placeholder' not in uri.lower():
                    retailer_data.append({'brand': brand, 'uri': uri})
                    i += 2  # Skip the next line as it's already processed
                else:
                    i += 1  # Move to the next line
            logger.debug(f"Processed page: {page_num + 1}/{pdf.page_count}")
    logger.debug("Completed PDF data extraction")
    return retailer_data

def download_and_extract_pdf_data(url):
    """Downloads the first PDF found at the URL and extracts data from it."""
def download_and_extract_pdf_data(url):
    """
    Downloads the first PDF found at the given URL and extracts data from it.

    Args:
        url (str): The URL to fetch the PDF from.

    Returns:
        None
    """
    logger.info(f"Fetching URL: {url}")
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    pdf_link_tag = soup.find('h3', class_='card__title file__title').find('a', href=True, type="application/pdf", class_="stretched-link")
    
    if not pdf_link_tag:
        logger.warning("No PDF link found on the page.")
        return

    pdf_url = urllib.parse.urljoin(response.url, pdf_link_tag['href'])
    pdf_filename = 'retailer_uri_register.pdf'
    logger.info(f"Downloading PDF from: {pdf_url}")
    
    pdf_response = requests.get(pdf_url)
    pdf_response.raise_for_status()
    with open(pdf_filename, 'wb') as file:
        file.write(pdf_response.content)

    retailer_data = extract_pdf_data(pdf_filename)
    print(retailer_data)

url = 'https://www.aer.gov.au/documents/consumer-data-right-list-energy-retailer-base-uris-june-2023'
    print(retailer_data)

# The URL from which to download and extract PDF data.
url = 'https://www.aer.gov.au/documents/consumer-data-right-list-energy-retailer-base-uris-june-2023'
# Perform the download and data extraction.
download_and_extract_pdf_data(url)
