import requests
from bs4 import BeautifulSoup
import urllib.parse
import os

def download_first_pdf(url):
    # Send a GET request to the URL
    response = requests.get(url, allow_redirects=True)
    # Raise an exception if the request was unsuccessful
    response.raise_for_status()

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    # Find the first PDF link on the page
    pdf_link = soup.find('a', href=True, text=lambda x: x and x.endswith('.pdf'))
    if pdf_link:
        # Construct the full URL for the PDF link
        pdf_url = urllib.parse.urljoin(response.url, pdf_link['href'])
        # Get the PDF file name
        pdf_filename = os.path.basename(pdf_url)
        # Download the PDF
        pdf_response = requests.get(pdf_url)
        pdf_response.raise_for_status()
        # Save the PDF to a file
        with open(pdf_filename, 'wb') as f:
            f.write(pdf_response.content)
        print(f"PDF downloaded: {pdf_filename}")
    else:
        print("No PDF link found on the page.")

# URL of the AER retailer base URIs page
url = 'https://www.aer.gov.au/documents/consumer-data-right-list-energy-retailer-base-uris-june-2023'
# Download the first PDF found on the page
download_first_pdf(url)
