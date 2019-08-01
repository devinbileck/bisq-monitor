import csv
import logging
import os
import threading
import time
from datetime import datetime

import numpy

from src.library.bisq.price_node import PriceNode
from src.library.configuration import Configuration
from src.model.price_node_model import PriceNodeModel

log = logging.getLogger(__name__)


class PriceNodeMonitor(threading.Thread):
    """Monitors the Bisq network price nodes."""

    MAX_MARKET_PRICE_DEVIATION_PERCENTAGE = 2
    MAX_TX_FEE_DEVIATION_PERCENTAGE = 10

    def __init__(self, tor_session, price_nodes, monitored_markets, poll_interval, resource_path):
        super(PriceNodeMonitor, self).__init__(name="PriceNodeMonitor")
        self.__tor_session = tor_session
        self.__price_nodes = price_nodes
        self.__monitored_markets = monitored_markets
        self.__poll_interval = poll_interval
        self.__resource_path = resource_path
        self.__historical_fee_rates = []
        self.__historical_market_prices = []
        self.is_running = False
        for price_node in price_nodes:
            Configuration.database.session.add(PriceNodeModel(price_node.address, price_node.operator))
        Configuration.database.session.commit()

    @property
    def tor_session(self):
        return self.__tor_session

    @property
    def price_nodes(self):
        return self.__price_nodes

    @property
    def monitored_markets(self):
        return self.__monitored_markets

    @property
    def poll_interval(self):
        return self.__poll_interval

    @property
    def resource_path(self):
        return self.__resource_path

    def run(self):
        self.is_running = True
        while self.is_running:
            try:
                price_data = self.fetch_price_data()
                self.analyze_price_data(price_data)
                self.write_price_data_to_csv(self.resource_path, "current_price_data.csv", price_data)
                self.write_fee_rates_to_csv(self.resource_path, "historical_fee_rates.csv", price_data)
                self.write_exchange_rates_to_csv(self.resource_path, "historical_exchange_rates.csv", price_data)
            except Exception as e:
                log.error(e)
            time.sleep(self.poll_interval)

    def stop(self):
        self.is_running = False

    def fetch_price_data(self):
        price_data = []
        for price_node in self.price_nodes:
            if price_node.is_online(self.tor_session):
                node_version = price_node.get_version(self.tor_session)
                fees = price_node.get_current_fees(self.tor_session)
                all_market_prices = price_node.get_current_market_prices(self.tor_session)
            else:
                log.warning("Offline node: {}".format(price_node))
                node_version = None
                fees = {}
                all_market_prices = {}
            data = {
                'nodeAddress': price_node.address,
                'nodeVersion': node_version,
                'btcTxFee': fees.get('btc', None)}
            for market in self.monitored_markets:
                data[market.lower() + "MarketPrice"] = all_market_prices.get(market.upper(), None)
            price_data.append(data)
        return price_data

    def analyze_price_data(self, price_data):
        btc_tx_fees = [x['btcTxFee'].price if 'btcTxFee' in x and x['btcTxFee'] else -1 for x in price_data]
        if len(set(btc_tx_fees)) > 1:
            min_fee = numpy.amin(btc_tx_fees)
            max_fee = numpy.amax(btc_tx_fees)
            deviation = ((float(max_fee) - min_fee) / min_fee) * 100
            if deviation > self.MAX_TX_FEE_DEVIATION_PERCENTAGE:
                nodes_with_fees = [(x['nodeAddress'], x.get('btcTxFee', None)) for x in price_data]
                log.warning("BTC transaction fee deviates between nodes by more than {}% ({:.2f}%); {}".format(self.MAX_TX_FEE_DEVIATION_PERCENTAGE, deviation,
                                                                                                               nodes_with_fees))
        monitored_market_keys = [x.lower() + "MarketPrice" for x in self.monitored_markets]
        for market in monitored_market_keys:
            market_prices = [x[market].price if market in x and x[market] else -1 for x in price_data]
            if len(set(market_prices)) > 1:
                min_price = numpy.amin(market_prices)
                max_price = numpy.amax(market_prices)
                deviation = ((float(max_price) - min_price) / min_price) * 100
                if deviation > self.MAX_MARKET_PRICE_DEVIATION_PERCENTAGE:
                    nodes_with_market_price = [(x['nodeAddress'], x.get(market, None)) for x in price_data]
                    log.warning(
                        "Market price deviates between nodes by more than {}% ({:.2f}%) for {}; {}".format(self.MAX_MARKET_PRICE_DEVIATION_PERCENTAGE,
                                                                                                           deviation, market,
                                                                                                           nodes_with_market_price))

    def write_price_data_to_csv(self, resource_path, filename, price_data):
        with open(os.path.join(resource_path, filename), "w", newline="") as csv_file:
            writer = csv.writer(csv_file)
            monitored_market_keys = [x.lower() + "MarketPrice" for x in self.monitored_markets]
            writer.writerow(["nodeAddress", "nodeVersion", "btcTxFee"] + monitored_market_keys)
            for data in price_data:
                writer.writerow([data['nodeAddress'], data['nodeVersion'], data['btcTxFee']] + [data[x] for x in monitored_market_keys])

    def write_fee_rates_to_csv(self, resource_path, filename, price_data):
        for currency in ['btc']:
            fee_rate_filename = os.path.join(resource_path, "{}_{}".format(currency.lower(), filename))
            if not os.path.isfile(fee_rate_filename):
                with open(fee_rate_filename, "w", newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    addresses = [x['nodeAddress'] for x in price_data]
                    writer.writerow(["timestamp"] + addresses)
            with open(fee_rate_filename, "a", newline="") as csv_file:
                writer = csv.writer(csv_file)
                fee_rates = [datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') + " UTC"] + [str(x[currency.lower() + 'TxFee'].price)
                                                                                          if currency.lower() + 'TxFee' in x
                                                                                             and x[currency.lower() + 'TxFee']
                                                                                          else -1
                                                                                          for x in price_data]
                writer.writerow(fee_rates)

    def write_exchange_rates_to_csv(self, resource_path, filename, price_data):
        for market in self.monitored_markets:
            market_filename = os.path.join(resource_path, "{}_{}".format(market.lower(), filename))
            if not os.path.isfile(market_filename):
                with open(market_filename, "w", newline="") as csv_file:
                    writer = csv.writer(csv_file)
                    addresses = [x['nodeAddress'] for x in price_data]
                    writer.writerow(["timestamp"] + addresses)
            with open(market_filename, "a", newline="") as csv_file:
                writer = csv.writer(csv_file)
                exchange_rates = [datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') + " UTC"] + [x[market.lower() + 'MarketPrice'].price
                                                                                               if market.lower() + 'MarketPrice' in x
                                                                                                  and x[market.lower() + 'MarketPrice']
                                                                                               else -1
                                                                                               for x in price_data]
                writer.writerow(exchange_rates)
