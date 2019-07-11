import json
import re
from enum import IntEnum

from .exceptions import ParseException


class StringFormat(IntEnum):
    alphabetic = 1,  # a-zA-Z, returns a string
    alphanumeric = 2,  # a-zA-Z0-9, returns a string
    boolean = 3,  # true or false (case insensitive), returns a boolean
    email = 4,  # email format, returns a string
    int = 5,  # 0-9, returns an integer
    json = 6,  # JSON/dict format that can be parsed by json module
    string_list = 7,  # Comma delimited list, returns a list of strings
    url = 8  # URL format, returns a string


def parse_string(string_input, expected_format):
    """
    Parses string and returns the processed output based on the expected format.
    @raise (ParseException) if parameters cannot be converted to expected format.
    @param (str) string_input: String to be parsed.
    @param (StringFormat) expected_format: Expected format of the input.
    @return (mixed): The processed output based on the expected format.
    """
    if expected_format == StringFormat.int:
        try:
            return int(string_input)
        except ValueError:
            raise ParseException("String is not an integer '%s'" % string_input)
    elif expected_format == StringFormat.alphabetic:
        if string_input.isalpha():
            return string_input
        raise ParseException("String contains non-alphabetic characters '%s'" % string_input)
    elif expected_format == StringFormat.alphanumeric:
        if string_input.isalnum():
            return string_input
        raise ParseException("String contains non-alphanumeric characters '%s'" % string_input)
    elif expected_format == StringFormat.url:
        reg = re.match('^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$', string_input)
        if reg is not None:
            return string_input
        raise ParseException("String is not a valid URL '%s'" % string_input)
    elif expected_format == StringFormat.email:
        reg = re.match(r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*"
                       r"@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$",
                       string_input)
        if reg is not None:
            return string_input
        raise ParseException("String is not a valid email address '%s'" % string_input)
    elif expected_format == StringFormat.string_list:
        reg = re.match(r"^(([0-9a-zA-Z]+\s*,?\s*)+)$", string_input)
        if reg is not None:
            return string_input.split(',')
        raise ParseException("String is not a valid string list '%s'" % string_input)
    elif expected_format == StringFormat.boolean:
        if isinstance(string_input, bool):
            return string_input
        elif isinstance(string_input, str):
            if string_input.lower() == 'true':
                return True
            elif string_input.lower() == 'false':
                return False
        raise ParseException("String '%s' is neither true nor false" % string_input)
    elif expected_format == StringFormat.json:
        if isinstance(string_input, dict):
            return string_input
        try:
            json_input = json.loads(string_input)
            if not isinstance(json_input, dict):
                raise ValueError("String is not in dictionary format '%s'" % string_input)
        except (TypeError, ValueError) as ex:
            ParseException("String '%s' cannot be parsed with the given type %s.\n%s" % (string_input, expected_format, ex))
        else:
            return json_input
    return ParseException("String '%s' cannot be parsed with the given type %s" % (string_input, expected_format))
