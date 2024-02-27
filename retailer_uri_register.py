import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import fitz  # PyMuPDF

def extract_table_from_pdf(pdf_filename):
    # Open the PDF file
    with fitz.open(pdf_filename) as pdf:
        table_content = []  # List to store all rows of the table
        for page in pdf:  # Iterate over each page
            blocks = page.get_text("dict")["blocks"]  # Get the text blocks
            for b in blocks:  # Iterate over each block
                if "lines" in b:  # Check if the block contains lines
                    for line in b["lines"]:  # Iterate over each line
                        spans = line["spans"]  # Get the spans in the line
                        if len(spans) > 1:  # Check if there are multiple spans (likely a table row)
                            row = [s["text"].strip() for s in spans if s["text"].strip()]  # Extract text from each span
                            if row:  # If there is text, add it as a table row
                                table_content.append(row)
        return table_content  # Return the extracted table content

def disassemble_pdf(pdf_filename):
    with fitz.open(pdf_filename) as pdf:
        for page_number in range(len(pdf)):
            page = pdf[page_number]
            print(f"--- Page {page_number + 1} ---")
            print(page.get_text("rawdict"))

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
        # Extract the table from the downloaded PDF
        table_content = extract_table_from_pdf(pdf_filename)
        # Output the extracted table content
        print(table_content)
    else:
        print("No PDF link found on the page.")

    # Disassemble the PDF to show its internal "code"
    disassemble_pdf(pdf_filename)

# URL of the AER retailer base URIs page
url = 'https://www.aer.gov.au/documents/consumer-data-right-list-energy-retailer-base-uris-june-2023'
# Download the first PDF found on the page
download_first_pdf(url)
