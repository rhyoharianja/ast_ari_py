class ARIError(Exception):
    """Base exception for ARI errors."""
    pass

class ARIBadRequest(ARIError):
    """Raised when the request parameters are missing or invalid (400)."""
    pass

class ARIAuthError(ARIError):
    """Raised when authentication fails (401)."""
    pass

class ARIForbidden(ARIError):
    """Raised when the user is not authorized to access the resource (403)."""
    pass

class ResourceNotFound(ARIError):
    """Raised when a requested resource is not found (404)."""
    pass

class InvalidState(ARIError):
    """Raised when the resource is in an invalid state for the operation (409)."""
    pass

class ARIUnprocessableEntity(ARIError):
    """Raised when the request is valid but cannot be processed (422)."""
    pass

class ARIServerError(ARIError):
    """Raised when Asterisk encounters an internal error (5xx)."""
    pass
