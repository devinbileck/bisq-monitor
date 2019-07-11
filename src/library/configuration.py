from future.utils import with_metaclass

from src.library.singleton import SingletonMetaClass


class Configuration(with_metaclass(SingletonMetaClass, object)):
    """
    Singleton that holds configuration parameters.
    Default values are stored in ConfigurationBuilder.
    """

    rest_network_port = 0  # REST API network port
    log_filename = ''  # Path to log file
    database = None  # Database instance
    database_path = ''  # Full path to the database, can be SQLite or PostgreSQL connection
    version_filename = ''  # File that contains version number
    version = ''  # Version information
    git_commit_id = ''  # Git commit ID

    @classmethod
    def summary(cls):
        return {
            'rest_network_port': cls.rest_network_port,
            'log_filename': cls.log_filename,
            'database': 'Database: %r' % cls.database,
            'database_path': cls.database_path
        }
