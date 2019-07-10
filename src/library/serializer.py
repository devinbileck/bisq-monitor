# coding=utf-8
"""Defines a custom serializer."""

from datetime import datetime, date


def serializer(obj):
    """
    Custom serializer for objects not serializable by default by json module
    @param (object) obj: Object to be serialized
    @return (str|object): serialized form or the original data if it was not serialized
    """
    if isinstance(obj, (datetime, date)):
        return str(obj)
    elif isinstance(obj, int):
        return str(obj)
    else:
        return obj
