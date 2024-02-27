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
    retailer_data = []
    with fitz.open(pdf_filename) as pdf:
        pages_text = []
        for page in pdf:
            pages_text.append(page.get_text("dict"))  # Append the dict output to the pages_text list
        for page_text in pages_text:  # Iterate over each page's text
            blocks = page_text["blocks"]
            start_processing = False
            for b in blocks:
                if "lines" in b:
                    for line in b["lines"]:
                        spans = line["spans"]
                        if len(spans) >= 2:
                            brand = spans[0]["text"].strip()
                            uri = spans[1]["text"].strip()
                            if "Retailer Base URI" in brand:
                                start_processing = True
                                continue
                            if start_processing:
                                if "Change log" in brand:
                                    return retailer_data
                                if brand and uri and "www.aer.gov.au/cdr" not in uri:
                                    retailer_data.append({'brand': brand, 'uri': uri})
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
