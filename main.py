import argparse
import csv
import logging
import os
import time
from datetime import datetime

from requests import HTTPError

from price_node import PriceNode
from tor_session import TorSession, IncorrectResponseData

price_nodes = [
    "44mgyoe2b6oqiytt.onion",
    "5bmpx76qllutpcyp.onion",
    "xc3nh4juf2hshy7e.onion",
    "62nvujg5iou3vu3i.onion",
    "ceaanhbvluug4we6.onion"]
tor_session = TorSession()


def fetch_price_data():
    price_data = []
    for node_address in price_nodes:
        price_node = PriceNode(node_address)
        node_version = price_node.get_version(tor_session)
        fees = price_node.get_fees(tor_session)
        market_prices = price_node.get_all_market_prices(tor_session)
        price_data.append({
            'nodeAddress': node_address,
            'nodeVersion': node_version,
            'btcTxFee': fees['btc'],
            'usdMarketPrice': market_prices['USD']})
    return price_data


def write_price_data_to_csv(filename, price_data):
    with open(filename, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["nodeAddress", "nodeVersion", "btcTxFee", "usdMarketPrice"])
        for data in price_data:
            writer.writerow([data['nodeAddress'], data['nodeVersion'], data['btcTxFee'], data['usdMarketPrice']])


def write_fee_rates_to_csv(filename, price_data):
    if not os.path.isfile(filename):
        with open(filename, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            addresses = [x['nodeAddress'] for x in price_data]
            writer.writerow(["timestamp"] + addresses)
    with open(filename, "a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        fee_rates = [datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') + " UTC"] + [str(x['btcTxFee']) for x in price_data]
        writer.writerow(fee_rates)


def write_exchange_rates_to_csv(filename, price_data):
    if not os.path.isfile(filename):
        with open(filename, "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            addresses = [x['nodeAddress'] for x in price_data]
            writer.writerow(["timestamp"] + addresses)
    with open(filename, "a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        exchange_rates = [datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') + " UTC"] + [str(x['usdMarketPrice']) for x in price_data]
        writer.writerow(exchange_rates)


def main():
    parser = argparse.ArgumentParser(description="Monitor Bisq nodes")
    parser.add_argument("--socks_host", default="127.0.0.1", help="the socks5 host to connect to (default=127.0.0.1)")
    parser.add_argument("--socks_port", type=int, default=9050, help="the socks5 port (default=9050)")
    parser.add_argument("--poll_interval", type=int, default=120, help="the interval in seconds to poll for data (default=120)")
    parser.add_argument("--debug", action='store_true', default=False, help="log debug output")
    args = parser.parse_args()

    tor_session.socks_host = args.socks_host
    tor_session.socks_port = args.socks_port

    logging_level = logging.INFO
    if args.debug:
        logging_level = logging.DEBUG

    logging.basicConfig(level=logging_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    while True:
        try:
            price_data = fetch_price_data()
            write_price_data_to_csv("current_price_data.csv", price_data)
            write_fee_rates_to_csv("historical_fee_rates.csv", price_data)
            write_exchange_rates_to_csv("historical_exchange_rates.csv", price_data)
            time.sleep(args.poll_interval)
        except HTTPError as e:
            logging.error(e)
        except IncorrectResponseData as e:
            logging.error(e)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
