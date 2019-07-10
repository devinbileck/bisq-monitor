import logging
from urllib.parse import unquote

from flask_restful import reqparse

from src.api.api_endpoint import ApiEndpoint
from src.library.plot import create_plot

log = logging.getLogger(__name__)


class Chart(ApiEndpoint):

    def get_command(self):
        """
        Implements the GET request.
        @raise (UnknownParameterError): When an unexpected parameter is encountered.
        @raise (CannotProcessError): When the server failed to process the request.
        @return (dict): Dictionary containing the fulfillment status of the request.
        """
        parser = reqparse.RequestParser()
        parser.add_argument('selected', type=str, required=True, help="Define selected chart. Parameter must be a string. {error_msg}")
        args = parser.parse_args()

        selected = unquote(args.selected)

        graph_json = create_plot(selected)
        return graph_json
