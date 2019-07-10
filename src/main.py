import argparse
import logging
import os

from src.flask_app import FlaskApp, FlaskApp
from src.price_node_monitor import PriceNodeMonitor
from src.tor_session import TorSession


def main():
    parser = argparse.ArgumentParser(description="Monitor Bisq nodes")
    parser.add_argument("--socks_host", default="127.0.0.1", help="the socks5 host to connect to (default=127.0.0.1)")
    parser.add_argument("--socks_port", type=int, default=9050, help="the socks5 port (default=9050)")
    parser.add_argument("--poll_interval", type=int, default=120, help="the interval in seconds to poll for data (default=120)")
    parser.add_argument("--debug", action='store_true', default=False, help="log debug output")
    args = parser.parse_args()

    tor_session = TorSession()
    tor_session.socks_host = args.socks_host
    tor_session.socks_port = args.socks_port

    logging_level = logging.INFO
    if args.debug:
        logging_level = logging.DEBUG
    logging.basicConfig(level=logging_level, format='%(asctime)s | %(name)s | %(levelname)s | %(message)s')
    log = logging.getLogger(__name__)

    resource_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, "resources")
    if not os.path.isdir(resource_path):
        os.mkdir(resource_path)

    price_nodes = [
        "44mgyoe2b6oqiytt.onion",
        "5bmpx76qllutpcyp.onion",
        "xc3nh4juf2hshy7e.onion",
        "62nvujg5iou3vu3i.onion",
        "ceaanhbvluug4we6.onion"
    ]
    monitored_markets = [
        "USD",
        "EUR",
        "CAD",
        "XMR"
    ]

    log.info("Starting Bisq Monitor")
    log.info("Price nodes: {}".format(price_nodes))
    log.info("Monitored markets: {}".format(monitored_markets))
    log.info("Resource path: {}".format(resource_path))
    monitor = PriceNodeMonitor(tor_session, price_nodes, monitored_markets, args.poll_interval, resource_path)
    monitor.start()

    log.info("Starting flask")
    flask_app = FlaskApp("FlaskApp")
    flask_app.run()


if __name__ == "__main__":
    main()
