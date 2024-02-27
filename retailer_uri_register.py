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
        for page_number in range(len(pdf)):
            logger.info(f"Processing page: {page_number + 1}/{len(pdf)}")
            page = pdf[page_number]

            text = page.get_text("text")
            lines = text.split('\n')
            # Find the index of the line containing "Retailer Base URI"
            start_index = next((i for i, line in enumerate(lines) if "Retailer Base URI" in line), -1)
            # Find the index of the line containing "Change log"
            end_index = next((i for i, line in enumerate(lines) if "Change log" in line), None)
            # If the line is found, print the text from the next line onwards
            if start_index != -1:
                logger.info(f"Found 'Retailer Base URI' on page: {page_number + 1}")
                # If the "Change log" line is found, only take lines up to that line
                content_after_title = lines[start_index + 1:end_index]
                # Filter out lines containing "www.aer.gov.au/cdr" and lines that are just page numbers (standalone numbers)
                non_empty_lines = [line for line in content_after_title if "www.aer.gov.au/cdr" not in line and line.strip() and not line.strip().isdigit()]
                logger.info(f"Filtered non-empty lines on page: {page_number + 1}")
                # Handle broken multiline URIs and clean up URIs
                retailer_data = []
                for i in range(0, len(non_empty_lines), 2):
                    brand = non_empty_lines[i].strip()
                    uri = non_empty_lines[i + 1].strip() if i + 1 < len(non_empty_lines) else ''
                    # Concatenate broken lines for URI
                    while not uri.endswith('/') and i + 2 < len(non_empty_lines):
                        uri += non_empty_lines[i + 2].strip()
                        i += 1
                    if uri:  # Ensure URI is not empty
                        logger.info(f"Appending retailer data entry for brand: {brand}")
                        retailer_data.append({'brand': brand, 'uri': uri.replace('\n', '').replace(' ', '')})
                # Remove the first list entry if it matches the specified pattern
                if retailer_data and retailer_data[0] == {'brand': 'Brand Name ', 'uri': 'Retailer Base URI '}:
                    retailer_data.pop(0)
                logger.info(f"Completed processing page: {page_number + 1}")
                return retailer_data
    logger.info(f"Completed disassembling PDF: {pdf_filename}")
                if i + 1 < len(non_empty_lines):
                    uri = non_empty_lines[i + 1].strip()
                else:
                    break
                # Check if URI is broken over multiple lines
                while not uri.endswith('/') and i + 2 < len(non_empty_lines):
                    i += 1
                    uri += non_empty_lines[i + 1].strip()
                logger.info(f"Appending retailer data entry for brand: {brand}")
                retailer_data.append({'brand': brand, 'uri': uri.replace('\n', '').replace(' ', '')})
                i += 2
                # Remove the first list entry if it matches the specified pattern
                if retailer_data and retailer_data[0] == {'brand': 'Brand Name ', 'uri': 'Retailer Base URI '}:
                    retailer_data.pop(0)
                logger.info(f"Completed processing page: {page_number + 1}")
                return retailer_data
    logger.info(f"Completed disassembling PDF: {pdf_filename}")


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
        print("No PDF link found on the page.")

    # Disassemble the PDF to show its internal "code"
    logger.info(f"Disassembling PDF: {pdf_filename}")
    table_content = disassemble_pdf(pdf_filename)
    print(table_content)

    # Turn table_content into comma separated list by taking every second line
    # and making it the second column of the previous line and saving it as
    # retailer_uri_list
    # Print the list of dictionaries
    for entry in table_content:
        print(entry)
    

# URL of the AER retailer base URIs page
url = 'https://www.aer.gov.au/documents/consumer-data-right-list-energy-retailer-base-uris-june-2023'
# Download the first PDF found on the page
download_first_pdf(url)
