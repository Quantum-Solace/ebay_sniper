# eBay Sniper

A Python script to place automatic bids on eBay auctions using the eBay API.

## Features

- Bid on eBay items using keywords or direct eBay links.
- Customize bid time, bid amount, and currency.
- Supports fallback URLs if the keyword search fails.
- Optimized for speed and accuracy.

## Requirements

- Python 3.6 or higher
- `requests` library

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/ebay_sniper.git
    cd ebay_sniper
    ```

2. **Create a virtual environment:**

    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment:**

    - On Windows:

        ```bash
        venv\Scripts\activate
        ```

    - On macOS/Linux:

        ```bash
        source venv/bin/activate
        ```

4. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Create `config.json`:**

    Create a `config.json` file with the following content:

    ```json
    {
        "app_id": "YOUR_APP_ID",
        "cert_id": "YOUR_CERT_ID",
        "dev_id": "YOUR_DEV_ID",
        "redirect_uri": "YOUR_REDIRECT_URI",
        "user_token": "YOUR_USER_TOKEN",
        "max_retries": 3,
        "retry_delay": 2
    }
    ```

    Replace the placeholders with your actual eBay API credentials.

## Usage

Run the script:

```bash
python ebay_sniper.py
