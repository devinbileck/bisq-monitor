import argparse
import logging
import os

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

    log.info("Starting Bisq Monitor")

    monitor = PriceNodeMonitor(tor_session, args.poll_interval)
    try:
        resource_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.path.pardir, "resources")
        log.debug("Resource path: {}".format(resource_path))
        if not os.path.isdir(resource_path):
            os.mkdir(resource_path)
        monitor.run(resource_path)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
