from werkzeug.exceptions import BadRequest, ExpectationFailed, InternalServerError


class CannotProcessError(ExpectationFailed):
    """Raised when the server encountered a request it cannot fulfill due to an error."""
    pass


class ServerError(InternalServerError):
    """Raised when there's an unexpected error in the server."""
    pass


class UnknownParameterError(BadRequest):
    """Raised when there are inconsistencies in request parameters."""
    pass
