import argparse
import csv
import logging
import os
import time
from datetime import datetime

import numpy as np

from src.price_node import PriceNode
from src.tor_session import TorSession

tor_session = TorSession()
price_nodes = [
    "44mgyoe2b6oqiytt.onion",
    "5bmpx76qllutpcyp.onion",
    "xc3nh4juf2hshy7e.onion",
    "62nvujg5iou3vu3i.onion",
    "ceaanhbvluug4we6.onion"]
monitored_markets = [
    "USD",
    "EUR",
    "CAD",
    "XMR"
]

MAX_MARKET_PRICE_DEVIATION = 2
MAX_TX_FEE_DEVIATION = 10


def fetch_price_data():
    price_data = []
    for node_address in price_nodes:
        price_node = PriceNode(node_address)
        if price_node.is_online(tor_session):
            node_version = price_node.get_version(tor_session)
            fees = price_node.get_fees(tor_session)
            all_market_prices = price_node.get_all_market_prices(tor_session)
        else:
            logging.warning("Offline node: {}".format(price_node))
            node_version = None
            fees = {}
            all_market_prices = {}
        data = {
            'nodeAddress': node_address,
            'nodeVersion': node_version,
            'btcTxFee': fees.get('btc', None)}
        for market in monitored_markets:
            data[market.lower() + "MarketPrice"] = all_market_prices.get(market.upper(), None)
        price_data.append(data)
    return price_data


def analyze_price_data(price_data):
    btc_tx_fees = [x['btcTxFee'].price for x in price_data]
    if len(set(btc_tx_fees)) > 1:
        min_fee = np.amin(btc_tx_fees)
        max_fee = np.amax(btc_tx_fees)
        deviation = ((float(max_fee) - min_fee) / min_fee) * 100
        if deviation > MAX_TX_FEE_DEVIATION:
            nodes_with_fees = [(x['nodeAddress'], x['btcTxFee']) for x in price_data]
            logging.warning("BTC transaction fee deviates between nodes by {:.2f}%; {}".format(deviation, nodes_with_fees))
    monitored_market_keys = [x.lower() + "MarketPrice" for x in monitored_markets]
    for market in monitored_market_keys:
        market_prices = [x[market].price for x in price_data]
        if len(set(market_prices)) > 1:
            min_price = np.amin(market_prices)
            max_price = np.amax(market_prices)
            deviation = ((float(max_price) - min_price) / min_price) * 100
            if deviation > MAX_MARKET_PRICE_DEVIATION:
                nodes_with_market_price = [(x['nodeAddress'], x[market]) for x in price_data]
                logging.warning("Market price deviates between nodes by {:.2f}% for {} market; {}".format(deviation, market, nodes_with_market_price))


def write_price_data_to_csv(filename, price_data):
    with open(filename, "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        monitored_market_keys = [x.lower() + "MarketPrice" for x in monitored_markets]
        writer.writerow(["nodeAddress", "nodeVersion", "btcTxFee"] + monitored_market_keys)
        for data in price_data:
            writer.writerow([data['nodeAddress'], data['nodeVersion'], data['btcTxFee']] + [data[x] for x in monitored_market_keys])


def write_fee_rates_to_csv(filename, price_data):
    for currency in ['btc']:
        fee_rate_filename = "{}_{}".format(currency.lower(), filename)
        if not os.path.isfile(fee_rate_filename):
            with open(fee_rate_filename, "w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                addresses = [x['nodeAddress'] for x in price_data]
                writer.writerow(["timestamp"] + addresses)
        with open(fee_rate_filename, "a", newline="") as csv_file:
            writer = csv.writer(csv_file)
            fee_rates = [datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') + " UTC"] + [str(x[currency.lower() + 'TxFee'].price) for x in price_data]
            writer.writerow(fee_rates)


def write_exchange_rates_to_csv(filename, price_data):
    for market in monitored_markets:
        market_filename = "{}_{}".format(market.lower(), filename)
        if not os.path.isfile(market_filename):
            with open(market_filename, "w", newline="") as csv_file:
                writer = csv.writer(csv_file)
                addresses = [x['nodeAddress'] for x in price_data]
                writer.writerow(["timestamp"] + addresses)
        with open(market_filename, "a", newline="") as csv_file:
            writer = csv.writer(csv_file)
            exchange_rates = [datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') + " UTC"] + [x[market.lower() + 'MarketPrice'].price for x in price_data]
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

    logging.basicConfig(level=logging_level, format='%(asctime)s | %(levelname)s | %(message)s')

    logging.info("Starting Bisq Monitor")

    while True:
        try:
            price_data = fetch_price_data()
            analyze_price_data(price_data)
            write_price_data_to_csv("current_price_data.csv", price_data)
            write_fee_rates_to_csv("historical_fee_rates.csv", price_data)
            write_exchange_rates_to_csv("historical_exchange_rates.csv", price_data)
            time.sleep(args.poll_interval)
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
