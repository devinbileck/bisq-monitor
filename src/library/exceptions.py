class ConfigurationError(Exception):
    """Raised when there are errors retrieving the configuration."""
    pass


class ParseException(Exception):
    """Raised when an error is encountered while parsing data."""
    pass
