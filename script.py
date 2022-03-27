import requests
import argparse
from datetime import datetime, timezone
import csv
from time import sleep

OPENSEA_APIKEY = "YOUR_API_KEY"

def get_events(start_date, end_date, cursor='', event_type='successful', **kwargs):
    url = "https://api.opensea.io/api/v1/events"
    query = {"only_opensea": "false", 
             "occurred_before": end_date,
             "occurred_after": start_date,
             "event_type": event_type,
             "cursor": cursor,
             **kwargs
             }

    headers = {
        "Accept": "application/json",
        "X-API-KEY": OPENSEA_APIKEY
    }
    response = requests.request("GET", url, headers=headers, params=query)

    return response.json()

def parse_event(event):
    record = {}
    asset = event.get('asset')
    if asset == None:
        return None # if there's no asset that means it's not a single NFT transaction so skip this item

    #collection
    record['collection_slug'] = asset['collection']['slug']
    record['collection_name'] = asset['collection']['name']
    record['collection_url'] = "https://opensea.io/collection/" + asset['collection']['slug']

    #asset
    record['asset_id'] = asset['id']
    record['asset_name'] = asset['name']
    record['asset_description'] = asset['description']
    record['asset_contract_date'] = asset['asset_contract']['created_date']
    record['asset_url'] = asset['permalink']
    record['asset_img_url'] = asset['image_url']

    #event
    record['event_id'] = event['id']
    record['event_time'] = event.get('created_date')
    record['event_auction_type'] = event.get('auction_type')
    record['event_contract_address'] = event.get('contract_address')
    record['event_quantity'] = event.get('quantity')
    record['event_payment_symbol'] =  None if event.get('payment_token') == None else event.get('payment_token').get('symbol')

    decimals = 18
    if event.get('payment_token') != None:
        decimals = event.get('payment_token').get('decimals')

    price_str = event['total_price']

    try: 
        if len(price_str) < decimals:
            price_str =  "0." + (decimals-len(price_str)) * "0" + price_str
            record['event_total_price'] = float(price_str)
        else:
            record['event_total_price'] = float(price_str[:-decimals] + "." + price_str[len(price_str)-decimals:])
    except:
        print(event)

    return record

def fetch_all_events(start_date, end_date, pause=1, **kwargs):
    result = list()
    next = ''
    fetch = True

    print(f"Fetching events between {start_date} and {end_date}")
    while fetch:
        response = get_events(int(start_date.timestamp()), int(end_date.timestamp()), cursor=next, **kwargs)

        for event in response['asset_events']:
            cleaned_event = parse_event(event)
            
            if cleaned_event != None:
                result.append(cleaned_event)

        if response['next'] is None:
            fetch = False
        else:
            next = response['next']

        sleep(pause)

    return result

def write_csv(data, filename):
    with open(filename, mode='w', encoding='utf-8', newline='\n') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames = data[0].keys())

        writer.writeheader()
        for event in data:
            writer.writerow(event)   

def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: {0!r}".format(s)
        raise argparse.ArgumentTypeError(msg)

def valid_datetime(arg_datetime_str):
    try:
        return datetime.strptime(arg_datetime_str, "%Y-%m-%d %H:%M")
    except ValueError:
        try:
            return datetime.strptime(arg_datetime_str, "%Y-%m-%d")
        except ValueError:
            msg = "Given Datetime ({0}) not valid! Expected format, 'YYYY-MM-DD' or 'YYYY-MM-DD HH:mm'!".format(arg_datetime_str)
            raise argparse.ArgumentTypeError(msg)   

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', "--startdate", help="The Start Date (YYYY-MM-DD or YYYY-MM-DD HH:mm)", required=True, type=valid_datetime)
    parser.add_argument('-e', "--enddate", help="The End Date (YYYY-MM-DD or YYYY-MM-DD HH:mm)", required=True, type=valid_datetime)
    parser.add_argument('-p', '--pause', help='Seconds to wait between http requests. Default: 1', required=False, default=1, type=float)
    parser.add_argument('-o', '--outfile', help='Output file path for saving nft sales record in csv format', required=False, default='./data.csv', type=str)
    args = parser.parse_args()
    res = fetch_all_events(args.startdate.replace(tzinfo=timezone.utc), args.enddate.replace(tzinfo=timezone.utc), args.pause)

    if len(res) != 0:
        write_csv(res, args.outfile)
    
    print("Done!")

if __name__ == "__main__":
    main()