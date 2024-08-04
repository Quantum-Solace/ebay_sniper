import requests
import time
import datetime
import json
import logging
import threading
import re
from requests.auth import AuthBase

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

APP_ID = config['app_id']
CERT_ID = config['cert_id']
DEV_ID = config['dev_id']
REDIRECT_URI = config['redirect_uri']
USER_TOKEN = config['user_token']
MAX_RETRIES = config['max_retries']
RETRY_DELAY = config['retry_delay']

class EbayAuth(AuthBase):
    def __call__(self, r):
        r.headers['Authorization'] = f'Bearer {USER_TOKEN}'
        return r

def make_request(url, params=None, method='GET', payload=None):
    for attempt in range(MAX_RETRIES):
        try:
            if method == 'GET':
                response = requests.get(url, params=params, auth=EbayAuth())
            elif method == 'POST':
                response = requests.post(url, json=payload, auth=EbayAuth())
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Request failed: {e}. Retrying {attempt + 1}/{MAX_RETRIES}...")
            time.sleep(RETRY_DELAY)
    logging.error("Max retries reached. Exiting.")
    return None

def find_item(keyword, fallback_url=None):
    search_url = 'https://api.ebay.com/buy/browse/v1/item_summary/search'
    params = {
        'q': keyword,
        'limit': 1,
        'sort': '-price'
    }
    data = make_request(search_url, params=params)
    
    if data and data.get('itemSummaries'):
        return data['itemSummaries'][0]
    elif fallback_url:
        data = make_request(fallback_url)
        if data and data.get('itemSummaries'):
            return data['itemSummaries'][0]
    return None

def get_item_from_url(url):
    item_id = re.search(r'/itm/(\d+)', url)
    if item_id:
        item_id = item_id.group(1)
        item_url = f'https://api.ebay.com/buy/browse/v1/item/{item_id}'
        item = make_request(item_url)
        return item
    return None

def place_bid(item_id, bid_amount, currency):
    bid_url = f'https://api.ebay.com/buy/browse/v1/item/{item_id}/place_proxy_bid'
    payload = {
        'maxBidAmount': {
            'currency': currency,
            'value': bid_amount
        }
    }
    return make_request(bid_url, method='POST', payload=payload)

def snipe_auction(input_str, bid_amount, bid_time, currency, fallback_url=None):
    item = None
    if re.match(r'https?://', input_str):
        item = get_item_from_url(input_str)
    else:
        item = find_item(input_str, fallback_url)

    if not item:
        logging.info("Item not found.")
        return

    item_id = item['itemId']
    end_time = datetime.datetime.strptime(item['itemEndTime'], "%Y-%m-%dT%H:%M:%S.%fZ")
    bid_time = min(max(bid_time, 1), 3600)
    
    wait_time = (end_time - datetime.datetime.utcnow()).total_seconds() - bid_time
    if wait_time > 0:
        time.sleep(wait_time)
    
    try:
        result = place_bid(item_id, bid_amount, currency)
        if result:
            logging.info(f"Bid placed successfully: {result}")
        else:
            logging.error("Failed to place bid.")
    except Exception as e:
        logging.error(f"Failed to place bid: {str(e)}")

def main():
    input_str = input("Enter keyword to search for item or direct eBay link: ")
    bid_amount = float(input("Enter maximum bid amount: "))
    bid_time = int(input("Enter bid time in seconds (up to 3600): "))
    currency = input("Enter currency (e.g., USD, EUR, GBP): ").upper()
    fallback_url = input("Enter fallback URL (optional): ")
    
    # Create a thread for the sniping process
    snipe_thread = threading.Thread(target=snipe_auction, args=(input_str, bid_amount, bid_time, currency, fallback_url))
    snipe_thread.start()

if __name__ == "__main__":
    main()

