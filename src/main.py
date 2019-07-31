import argparse
import logging
import os

from src.library.configuration import Configuration
from src.library.configuration_builder import config_from_file
from src.library.database import Database
from src.library.tor_session import TorSession
from src.library.bisq.price_node import PriceNode
from src.model.price_node_model import PriceNodeModel
from src.price_node_monitor import PriceNodeMonitor
from src.web_app import WebApp


def main():
    parser = argparse.ArgumentParser(description="Monitor Bisq network")
    parser.add_argument("--config_file", default="config.json", help="the configuration file to load parameters from (default=config.json)")
    parser.add_argument("--socks_host", default="127.0.0.1", help="the socks5 host to connect to for TOR (default=127.0.0.1)")
    parser.add_argument("--socks_port", type=int, default=9050, help="the socks5 port (default=9050)")
    parser.add_argument("--web_host", default="127.0.0.1", help="the hostname to listen on for the web interface (default=127.0.0.1)")
    parser.add_argument("--web_port", type=int, default=5000, help="the port of the web interface (default=5000)")
    parser.add_argument("--poll_interval", type=int, default=120, help="the interval in seconds to poll Bisq network nodes for data (default=120)")
    parser.add_argument("--debug", action='store_true', default=False, help="log debug output")
    args = parser.parse_args()

    logging_level = logging.INFO
    if args.debug:
        logging_level = logging.DEBUG
    logging.basicConfig(level=logging_level, format='%(asctime)s | %(name)s | %(filename)s:%(lineno)d | %(levelname)s | %(message)s')
    log = logging.getLogger(__name__)

    if args.config_file and os.path.isfile(args.config_file):
        config_from_file(args.config_file)

    if not os.path.isdir(os.path.dirname(Configuration.log_filename)):
        Configuration.log_filename = os.path.join(os.path.dirname(__file__), Configuration.log_filename)

    Configuration.database = Database(Configuration.database_name)

    tor_session = TorSession()
    tor_session.socks_host = args.socks_host
    tor_session.socks_port = args.socks_port

    resource_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, "resources")
    if not os.path.isdir(resource_path):
        os.mkdir(resource_path)

    price_nodes = [
        PriceNode("44mgyoe2b6oqiytt.onion"),
        PriceNode("5bmpx76qllutpcyp.onion"),
        PriceNode("xc3nh4juf2hshy7e.onion"),
        PriceNode("62nvujg5iou3vu3i.onion"),
        PriceNode("ceaanhbvluug4we6.onion")
    ]
    monitored_markets = [
        "USD",
        "EUR",
        "CAD",
        "XMR"
    ]

    log.info("Starting price node monitor")
    log.info("Price nodes: {}".format(price_nodes))
    log.info("Monitored markets: {}".format(monitored_markets))
    price_node_monitor = PriceNodeMonitor(tor_session, price_nodes, monitored_markets, args.poll_interval, resource_path)
    price_node_monitor.start()

    log.info("Starting web application")
    web_app = WebApp(args.web_host, args.web_port)
    web_app.run()


if __name__ == "__main__":
    main()
