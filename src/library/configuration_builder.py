import json
import os

import yaml
from git import Repo

from src.library.exceptions import ConfigurationError
from src.library.configuration import Configuration
from src.library.string_helpers import StringFormat, parse_string


def config_from_file(file_path):
    if not file_path:
        raise ConfigurationError('Configuration file is not set')
    if not os.path.isfile(file_path):
        raise ConfigurationError('Configuration file "%s" is not found' % file_path)
    data = {}
    with open(file_path, 'r') as file_stream:
        if file_path.endswith(('.yml', '.yaml')):
            data.update(yaml.load(file_stream))
        elif file_path.endswith('.json'):
            data.update(json.load(file_stream))
        else:
            raise ConfigurationError('Configuration file "%s" is not supported' % file_path)
        ConfigurationDictBuilder.set_settings(data)
        ConfigurationDictBuilder.initialize_configuration()


class ConfigurationBuilder(object):

    @classmethod
    def initialize_configuration(cls):
        cls._get_configuration()
        cls._get_version()
        cls._get_git_details()

    @classmethod
    def _get_configuration(cls):
        Configuration.rest_network_port = cls.get_settings('rest_network_port', 5000, StringFormat.int)
        Configuration.log_filename = cls.get_settings('log_filename', 'app.log')
        Configuration.version_filename = cls.get_settings('version_filename', 'version.txt')
        Configuration.database_path = 'sqlite:///{db}'.format(
            db=cls.get_settings('database_name', 'bisq-monitor.sqlite'))

    @classmethod
    def _get_version(cls):
        if os.path.isfile(Configuration.version_filename):
            with open(Configuration.version_filename, 'r') as file_stream:
                Configuration.version = file_stream.readline()
        else:
            Configuration.version = 'unknown'

    @classmethod
    def _get_git_details(cls):
        try:
            r = Repo(os.path.realpath(os.path.join(os.getcwd(), '..', '..')))
            Configuration.git_commit_id = str(r.head.commit.name_rev)
        except:
            Configuration.git_commit_id = 'unknown'

    @classmethod
    def get_settings(cls, key, default=None, expected_format=None):
        raise ConfigurationError('ConfigurationBuilder.get_settings is not defined. Use subclass.get_settings instead')


class ConfigurationDictBuilder(ConfigurationBuilder):
    _settings = {}

    @classmethod
    def get_settings(cls, key, default=None, expected_format=None):
        """
        Returns default value if the environment variable doesn't exist or if it is empty.
        Otherwise, returns the environment variable value.
        @param (str) key: Settings Key
        @param (object) default: Value to be set if environment variable is not set
        @param (StringFormat) expected_format: Expected format of the environment variable
        @return (object): Returns either the environment variable if it is not empty, otherwise, the default value
        """
        if not cls._settings:
            raise ConfigurationError('settings is not defined')

        if key.lower() not in cls._settings:
            return default

        value = cls._settings[key.lower()]

        if not value:
            return default

        if not expected_format:
            return value

        return parse_string(value, expected_format)

    @classmethod
    def set_settings(cls, settings_dict):
        cls._settings = dict((k.lower(), v) for k, v in list(settings_dict.items()))
