from future.utils import with_metaclass

from src.library.singleton import SingletonMetaClass


class Configuration(with_metaclass(SingletonMetaClass, object)):
    """
    Singleton that holds configuration parameters.
    Default values are stored in ConfigurationBuilder.
    """
    socks_host = ""
    socks_port = 0
    web_host = ""
    web_port = 0
    poll_interval = 0
    debug = False
    log_filename = ""  # Path to log file
    database = None  # Database instance
    database_name = ""  # Full path to the database, can be SQLite or PostgreSQL connection
    version_filename = ""  # File that contains version number
    version = ""  # Version information
    git_commit_id = ""  # Git commit ID
