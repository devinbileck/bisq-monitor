import argparse
import logging
import os

from src.library.configuration import Configuration, load_config_from_file
from src.library.tor_session import TorSession
from src.library.bisq.price_node import PriceNode
from src.price_node_monitor import PriceNodeMonitor
from src.web_app import WebApp


def main():
    parser = argparse.ArgumentParser(description="Monitor Bisq network")
    parser.add_argument("-c", "--config_file", default="config.yml", help="the configuration file to load parameters from (default=config.yml)")
    parser.add_argument("-d", "--debug", action="store_true", default=False, help="log debug output")
    args = parser.parse_args()

    logging_level = logging.INFO
    if args.debug:
        logging_level = logging.DEBUG
    logging.basicConfig(level=logging_level, format="%(asctime)s | %(name)s | %(filename)s:%(lineno)d | %(levelname)s | %(message)s")
    log = logging.getLogger(__name__)

    if args.config_file and os.path.isfile(args.config_file):
        load_config_from_file(args.config_file)

    tor_session = TorSession()
    tor_session.socks5_host = Configuration.socks5_host
    tor_session.socks5_port = Configuration.socks5_port

    resource_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, "resources")
    if not os.path.isdir(resource_path):
        os.mkdir(resource_path)

    price_nodes = []
    for price_node in Configuration.price_nodes:
        price_nodes.append(PriceNode(price_node["address"], price_node["operator"]))

    monitored_markets = []
    for monitored_market in Configuration.monitored_markets:
        monitored_markets.append(monitored_market)

    log.info("Starting price node monitor")
    log.info("Price nodes: {}".format(price_nodes))
    log.info("Monitored markets: {}".format(monitored_markets))
    price_node_monitor = PriceNodeMonitor(tor_session, price_nodes, monitored_markets, Configuration.poll_interval, resource_path)
    price_node_monitor.start()

    log.info("Starting web application")
    web_app = WebApp(Configuration.web_host, Configuration.web_port)
    web_app.run()


if __name__ == "__main__":
    main()
