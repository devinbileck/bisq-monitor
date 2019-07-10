import json
import logging

from flask import jsonify
from flask_restful import Resource
from werkzeug.exceptions import HTTPException

from src.api.exceptions import ServerError
from src.api.exceptions import UnknownParameterError
from src.library import serializer

log = logging.getLogger(__name__)


class ApiEndpoint(Resource):
    """Base class for all API endpoints."""

    def get(self):
        """
        Handles a GET request and formats the response.
        @return (flask.Response): The response to the request.
        """
        try:
            try:
                # The dict needs to be serialized and deserialized to use custom_serializer in converting objects to string.
                # If this step is not done here, it will not be formatted properly by jsonify that wraps the HTTP response.
                response = json.loads(json.dumps(self.get_command(), default=serializer))
            except AttributeError as attr_error:
                log.error("UnknownParameterError {}".format(attr_error))
                raise UnknownParameterError({'error': str(attr_error)})
        except HTTPException as http_error:
            log.error(http_error)
            raise
        except Exception:
            raise
        try:
            return jsonify(response)
        except Exception as any_error:
            raise ServerError(u"%s\n%s" % (response, any_error))

    def get_command(self):
        """Abstract method that is wrapped by self.get() and contains the implementation details for the GET request."""
        raise NotImplementedError('self.get_command() needs to be implemented.')
