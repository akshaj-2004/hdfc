# HDFC Life Policy Scraper

This Python script automates the process of scraping policy documents from the HDFC Life website. It downloads the first 5 policy PDFs and extracts metadata into a CSV file.

## Features
- **Navigation**: Accesses the HDFC Life policy documents page.
- **Extraction**: Scrapes Policy Name, UIN, and Policy Type.
- **Downloading**: Downloads policy PDFs to a local folder `HDFC_Policy_Documents`.
- **Data Saving**: Saves extracted metadata to `policy_data.csv`.
- **Error Handling**: Handles network errors and missing files gracefully.

## Prerequisites
- Python 3.x
- Internet connection

## Installation

1. Clone the repository or download the script.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script using Python:

```bash
python3 hdfc_policy_scraper.py
```

## Output

- **PDFs**: Downloaded to `HDFC_Policy_Documents/` directory.
- **Data**: Saved in `policy_data.csv`.

## Assumptions
- The script targets the "Savings & Investment (live)" section or similar as it appears first.
- The UIN is extracted from the policy name or URL if available matching the pattern `[0-9]{3}[A-Z][0-9]{3}[A-Z][0-9]{2}`.
- The script stops after processing 5 policies as per requirements.
