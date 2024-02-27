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

def disassemble_pdf(pdf_filename):
    with fitz.open(pdf_filename) as pdf:
        for page_number in range(len(pdf)):
            page = pdf[page_number]
            # print(f"--- Page {page_number + 1} ---")
            text = page.get_text("text")
            lines = text.split('\n')
            # Find the index of the line containing "Retailer Base URI"
            start_index = next((i for i, line in enumerate(lines) if "Retailer Base URI" in line), None)
            # Find the index of the line containing "Change log"
            end_index = next((i for i, line in enumerate(lines) if "Change log" in line), None)
            # If the line is found, print the text from the next line onwards
            if start_index is not None:
            if start_index != -1:
                # If the "Change log" line is found, only take lines up to that line
                content_after_title = lines[start_index + 2:end_index]  # Start from the line after "Retailer Base URI"
                # Filter out lines containing "www.aer.gov.au/cdr" and lines that are just page numbers (standalone numbers)
                non_empty_lines = [line for line in content_after_title if "www.aer.gov.au/cdr" not in line and line.strip() and not line.strip().isdigit()]
                # Convert the non_empty_lines into a list of dictionaries
                retailer_data = []
                for i in range(0, len(non_empty_lines), 2):
                    retailer_data.append({'brand': non_empty_lines[i], 'uri': non_empty_lines[i + 1]})
                return retailer_data
            else:
                # If the "Change log" line is found, only take lines up to that line
                if end_index is not None:
                    lines = lines[:end_index]
                # Filter out lines containing "www.aer.gov.au/cdr" and lines that are just page numbers (standalone numbers)
                non_empty_lines = [line for line in lines if "www.aer.gov.au/cdr" not in line and line.strip() and not line.strip().isdigit()]
                # Convert the non_empty_lines into a list of dictionaries
                retailer_data = []
                for i in range(0, len(non_empty_lines), 2):
                    retailer_data.append({'brand': non_empty_lines[i], 'uri': non_empty_lines[i + 1]})
                return retailer_data

def download_first_pdf(url):
    # Send a GET request to the URL
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
        # Get the PDF file name
        pdf_filename = 'retailer_uri_register.pdf'
        # Download the PDF
        pdf_response = requests.get(pdf_url)
        pdf_response.raise_for_status()
        # Save the PDF to a file
        with open(pdf_filename, 'wb') as f:
            f.write(pdf_response.content)
        # print(f"PDF downloaded: {pdf_filename}")
    else:
        print("No PDF link found on the page.")

    # Disassemble the PDF to show its internal "code"
    table_content = disassemble_pdf(pdf_filename)
    print(table_content)

    # Turn table_content into comma separated list by taking every second line
    # and making it the second column of the previous line and saving it as
    # retailer_uri_list
    retailer_uri_list = []
    for i in range(0, len(table_content), 2):
        retailer_uri_list.append(f"{table_content[i]},{table_content[i + 1]}")
    

# URL of the AER retailer base URIs page
url = 'https://www.aer.gov.au/documents/consumer-data-right-list-energy-retailer-base-uris-june-2023'
# Download the first PDF found on the page
download_first_pdf(url)
