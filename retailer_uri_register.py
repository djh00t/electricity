import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
# Uninstall the incompatible fitz library
# pip uninstall fitz
# pip uninstall pymupdf
# Reinstall the fitz library with the correct architecture
# pip install --no-cache-dir pymupdf
import fitz  # PyMuPDF
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def disassemble_pdf(pdf_filename):
    logger.info(f"Opening PDF file: {pdf_filename}")
    with fitz.open(pdf_filename) as pdf:
        logger.info(f"PDF file opened successfully: {pdf_filename}")
        retailer_data = []
        for page_number in range(pdf.page_count):
            logger.info(f"Processing page: {page_number + 1}/{pdf.page_count}")
            page = pdf[page_number]

            text = page.get_text("text")
            lines = text.split('\n')
            # Generic text extraction logic
            for line in lines:
                # Assuming each line contains a brand name followed by its URI
                # and they are separated by a known delimiter, e.g., a comma.
                parts = line.split(',')  # Replace comma with the actual delimiter
                if len(parts) == 2:
                    brand, uri = parts[0].strip(), parts[1].strip()
                    # Validate the extracted data
                    if uri.lower().startswith('http') and 'placeholder' not in uri.lower():
                        retailer_data.append({'brand': brand, 'uri': uri})
                    else:
                        logger.warning(f"Invalid data found on page {page_number + 1}: {line}")
                else:
                    logger.warning(f"Unexpected line format on page {page_number + 1}: {line}")
                    i += 2
    logger.info(f"Completed disassembling PDF: {pdf_filename}")
    return retailer_data


def download_first_pdf(url):
    # Send a GET request to the URL
    logger.info(f"Sending GET request to URL: {url}")
    response = requests.get(url, allow_redirects=True, stream=True)
    # Raise an exception if the request was unsuccessful
    response.raise_for_status()
    # Follow redirects and show the final URL
    # print(f"Final URL after redirects: {response.url}")

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the first PDF link within an h3 with class "card__title file__title"
    # and the href has attributes type="application/pdf" and class="stretched-link"
    pdf_link = soup.find('h3', class_='card__title file__title').find('a', href=True, type="application/pdf", class_="stretched-link")
    if pdf_link:
        # Construct the full URL for the PDF link
        pdf_url = urllib.parse.urljoin(response.url, pdf_link['href'])
        logger.info(f"Found PDF URL: {pdf_url}")
        # Get the PDF file name
        pdf_filename = 'retailer_uri_register.pdf'
        # Download the PDF
        logger.info(f"Downloading PDF: {pdf_filename}")
        pdf_response = requests.get(pdf_url)
        pdf_response.raise_for_status()
        # Save the PDF to a file
        with open(pdf_filename, 'wb') as f:
            f.write(pdf_response.content)
        # print(f"PDF downloaded: {pdf_filename}")
    else:
        logger.warning("No PDF link found on the page.")
        return  # Return early if no PDF link is found
        print("No PDF link found on the page.")

    # Disassemble the PDF to show its internal "code"
    logger.info(f"Disassembling PDF: {pdf_filename}")
    table_content = disassemble_pdf(pdf_filename)
    if table_content:
        # Print the list of dictionaries
        for entry in table_content:
            print(entry)
    else:
        logger.warning("No data extracted from the PDF.")
    print(table_content)

    # Turn table_content into comma separated list by taking every second line
    # and making it the second column of the previous line and saving it as
    # retailer_uri_list
    # Print the list of dictionaries
    #for entry in table_content:
    #    print(entry)
    

# URL of the AER retailer base URIs page
url = 'https://www.aer.gov.au/documents/consumer-data-right-list-energy-retailer-base-uris-june-2023'
# Download the first PDF found on the page
download_first_pdf(url)
