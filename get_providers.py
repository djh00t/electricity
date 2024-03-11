"""
This script is used to download and extract retailer information from a specified PDF file.
The PDF is expected to contain retailer names and their corresponding base URIs.

The script performs the following steps:
1. Download the PDF from a given URL.
2. Extract retailer data from the PDF.
3. Print the extracted data to the console.

Usage:
    Simply run the script, and it will perform the download and extraction automatically.
    The URL from which the PDF is downloaded is hardcoded in the script.

Example:
    python get_providers.py
"""
import io
import requests
from bs4 import BeautifulSoup
import urllib.parse
import fitz  # PyMuPDF
import logging
from config import RETAILER_PDF_URL
from config import RETAILER_PDF_URL

# Configure logging
logger = logging.getLogger(__name__)

def extract_pdf_data(pdf_path):
    """
    Extracts retailer data from a PDF file.

    Args:
        pdf_path (str): The file path to the PDF from which to extract data.
        pdf_stream (stream): A byte stream of the PDF from which to extract data.

    Returns:
        list of dict: A list of dictionaries containing retailer 'brand' and 'uri'.
    """
    logger.debug(f"Opening PDF stream")
    logger.debug(f"Opening PDF file: {pdf_path}")
    retailer_data = []
    with fitz.open(stream=pdf_path, filetype="pdf") as pdf:  # pdf_path is now correctly passed as an argument
        for page_num in range(pdf.page_count):
            page = pdf.load_page(page_num)
            text = page.get_text("text")
            lines = text.split('\n')
            i = 0
            while i < len(lines) - 1:
                if "Change log" in lines[i]:  # Stop processing if "Change log" is found
                    break
                    break  # Stop processing if "Change log" is found
                brand, uri = lines[i].strip(), lines[i + 1].strip()
                if uri.lower().startswith('http') and 'placeholder' not in uri.lower():
                    retailer_data.append({'brand': brand, 'uri': uri})
                    i += 2  # Skip the next line as it's already processed
                else:
                    i += 1  # Move to the next line
            logger.debug(f"Processed page: {page_num + 1}/{pdf.page_count}")
    logger.debug("Completed PDF data extraction")  # Extraction complete
    return retailer_data

def download_and_extract_pdf_data():
    """
    Downloads the first PDF found at the given URL and extracts data from it to memory.

    Args:
        url (str): The URL to fetch the PDF from.

    Returns:
        list of dict: A list of dictionaries containing retailer 'brand' and 'uri'.
    """
    logger.info(f"Fetching URL: {url}")
    response = requests.get(RETAILER_PDF_URL)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    pdf_link_tag = soup.find('h3', class_='card__title file__title').find('a', href=True, type="application/pdf", class_="stretched-link")

    
    if not pdf_link_tag:
        logger.warning("No PDF link found on the page.")
        return []

    pdf_url = urllib.parse.urljoin(response.url, pdf_link_tag['href'])
    logger.info(f"Downloading PDF from: {pdf_url}")
    
    logger.info(f"Downloading PDF from: {pdf_url}")

    pdf_response = requests.get(pdf_url)
    pdf_response.raise_for_status()  # Ensure we have a successful response

    # Here we pass the PDF content directly as a stream
    return extract_pdf_data(io.BytesIO(pdf_response.content))  # Correctly passing the stream to the extract_pdf_data function

# Perform the download and data extraction.
retailer_data = download_and_extract_pdf_data()
# Optionally, you can now use retailer_data as needed, for example:
# print(retailer_data)
