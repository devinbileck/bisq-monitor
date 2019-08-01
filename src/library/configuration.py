import json
import os

import yaml
from future.utils import with_metaclass
from git import Repo

from src.library.database import Database
from src.library.exceptions import ConfigurationError
from src.library.singleton import SingletonMetaClass
from src.library.string_helpers import StringFormat, parse_string


class Configuration(with_metaclass(SingletonMetaClass, object)):
    socks5_host = "127.0.0.1"
    socks5_port = 9050
    web_host = "127.0.0.1"
    web_port = 5000
    poll_interval = 120
    price_nodes = []
    monitored_markets = []
    database = None
    version = ""
    git_commit_id = ""


def load_config_from_file(file_path):
    if not os.path.isfile(file_path):
        raise ConfigurationError("Configuration file not found: {}".format(file_path))
    config = {}
    with open(file_path, "r") as file_stream:
        if file_path.endswith((".yml", ".yaml")):
            config.update(yaml.load(file_stream))
        elif file_path.endswith(".json"):
            config.update(json.load(file_stream))
        else:
            raise ConfigurationError("Configuration file not supported: {}".format(file_path))
        ConfigurationBuilder.initialize_configuration(config)


class ConfigurationBuilder(object):
    _config = {}

    @classmethod
    def initialize_configuration(cls, config_dict):
        cls._set_config(config_dict)
        cls._get_configuration()
        cls._get_version()
        cls._get_git_details()

    @classmethod
    def _set_config(cls, config_dict):
        cls._config = dict((k.lower(), v) for k, v in list(config_dict.items()))

    @classmethod
    def _get_configuration(cls):
        Configuration.socks5_host = cls._get_settings("socks5_host", Configuration.socks5_host, StringFormat.ip_address)
        Configuration.socks5_port = cls._get_settings("socks5_port", Configuration.socks5_port, StringFormat.int)
        Configuration.web_host = cls._get_settings("web_host", Configuration.web_host, StringFormat.ip_address)
        Configuration.web_port = cls._get_settings("web_port", Configuration.web_port, StringFormat.int)
        Configuration.poll_interval = cls._get_settings("poll_interval", Configuration.poll_interval, StringFormat.int)
        Configuration.price_nodes = cls._get_settings("price_nodes", Configuration.price_nodes)
        Configuration.monitored_markets = cls._get_settings("monitored_markets", Configuration.monitored_markets)
        Configuration.database = Database("db.sqlite")

    @classmethod
    def _get_version(cls):
        if not os.path.isfile("version.txt"):
            return
        with open("version.txt", "r") as file_stream:
            Configuration.version = file_stream.readline()

    @classmethod
    def _get_git_details(cls):
        try:
            r = Repo(os.path.realpath(os.path.join(os.getcwd(), "..", "..")))
            Configuration.git_commit_id = str(r.head.commit.name_rev)
        except:
            pass

    @classmethod
    def _get_settings(cls, key, default=None, expected_format=None):
        if key.lower() not in cls._config:
            return default

        value = cls._config[key.lower()]

        if not value:
            return default

        if not expected_format:
            return value

        return parse_string(value, expected_format)
