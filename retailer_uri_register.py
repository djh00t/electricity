import requests
from bs4 import BeautifulSoup
import urllib.parse
import os
import fitz  # PyMuPDF

def extract_table_from_pdf(pdf_filename):
    # Open the PDF file
    pdf_document = fitz.open(pdf_filename)
    table_content = []
    # Iterate over each page in the PDF
    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        # Extract all text that is formatted as a table
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    row_data = [span["text"].strip() for span in line["spans"]]
                    table_content.append(row_data)
        # Check if we've reached the "Change log" section and stop if we have
        text = page.get_text("text")
        if "Change log" in text:
            break
    pdf_document.close()
    return table_content

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

# URL of the AER retailer base URIs page
url = 'https://www.aer.gov.au/documents/consumer-data-right-list-energy-retailer-base-uris-june-2023'
# Download the first PDF found on the page
download_first_pdf(url)
