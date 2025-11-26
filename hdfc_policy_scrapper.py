import os
import requests
from bs4 import BeautifulSoup
import csv
import time
import re

# Constants
BASE_URL = "https://www.hdfclife.com"
POLICY_DOCS_URL = "https://www.hdfclife.com/policy-documents"
DOWNLOAD_DIR = "HDFC_Policy_Documents"
DATA_FILE = "policy_data.csv"
MAX_POLICIES = 5

def setup_directories():
    """Creates the download directory if it doesn't exist."""
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
        print(f"Created directory: {DOWNLOAD_DIR}")
    else:
        print(f"Directory already exists: {DOWNLOAD_DIR}")

def get_policy_documents():
    """Fetches and parses the policy documents page."""
    try:
        response = requests.get(POLICY_DOCS_URL)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return None

def extract_policy_data(soup):
    """Extracts policy data from the parsed HTML."""
    policies = []
    
    # Based on browser exploration:
    # Policies are likely in lists under sections.
    # We need to find the lists. The structure observed was <ul> with <li> containing <a> tags.
    # Let's look for all 'docName' class elements as a starting point, as observed.
    
    doc_links = soup.find_all('a', class_='docName')
    
    count = 0
    for link in doc_links:
        if count >= MAX_POLICIES:
            break
            
        policy_name = link.get_text(strip=True)
        pdf_url = link.get('href')
        
        if not pdf_url:
            continue
            
        # Handle relative URLs
        if not pdf_url.startswith('http'):
            pdf_url = BASE_URL + pdf_url
            
        # Extract UIN (Attempt to find it in text or URL)
        # Pattern for UIN is often like 101N146V08
        uin_match = re.search(r'[0-9]{3}[A-Z][0-9]{3}[A-Z][0-9]{2}', policy_name)
        if not uin_match:
             uin_match = re.search(r'[0-9]{3}[A-Z][0-9]{3}[A-Z][0-9]{2}', pdf_url)
        
        uin = uin_match.group(0) if uin_match else "N/A"
        
        # Determine Policy Type
        # We need to find the parent section.
        # The <ul> is likely inside a container that has a header.
        # Let's traverse up to find a header.
        policy_type = "Unknown"
        # Try to find the section header (e.g., h2, h3, or a specific class)
        # This part is tricky without exact DOM structure. 
        # I'll try to find the nearest previous header element.
        
        curr = link
        while curr:
            curr = curr.find_previous(['h2', 'h3', 'h4', 'div'])
            if curr and curr.name in ['h2', 'h3', 'h4']:
                policy_type = curr.get_text(strip=True)
                break
            if curr and curr.name == 'div' and 'accordion-title' in curr.get('class', []):
                 policy_type = curr.get_text(strip=True)
                 break
            # Safety break to avoid infinite loops or going too far up
            if not curr or curr.name == 'body':
                break

        policies.append({
            'Policy Name': policy_name,
            'UIN': uin,
            'Policy Type': policy_type,
            'PDF URL': pdf_url
        })
        count += 1
        
    return policies

def download_pdf(url, filename):
    """Downloads a PDF file from a URL."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        filepath = os.path.join(DOWNLOAD_DIR, filename)
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Downloaded: {filename}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {url}: {e}")
        return False

def save_data_to_csv(data):
    """Saves extracted data to a CSV file."""
    if not data:
        print("No data to save.")
        return

    fieldnames = ['Policy Name', 'UIN', 'Policy Type']
    
    try:
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow({k: row[k] for k in fieldnames})
        print(f"Data saved to {DATA_FILE}")
    except IOError as e:
        print(f"Error saving CSV: {e}")

def main():
    print("Starting HDFC Life Policy Scraper...")
    setup_directories()
    
    soup = get_policy_documents()
    if not soup:
        print("Failed to retrieve policy documents page. Exiting.")
        return

    print("Page retrieved. Extracting data...")
    policies = extract_policy_data(soup)
    
    if not policies:
        print("No policies found.")
        return

    print(f"Found {len(policies)} policies. Processing...")
    
    for policy in policies:
        # Create a safe filename
        safe_name = "".join([c for c in policy['Policy Name'] if c.isalnum() or c in (' ', '-', '_')]).strip()
        safe_name = safe_name[:50] # Limit length
        filename = f"{safe_name}.pdf"
        
        print(f"Downloading {filename}...")
        download_pdf(policy['PDF URL'], filename)
        
    save_data_to_csv(policies)
    print("Scraping completed successfully.")

if __name__ == "__main__":
    main()
