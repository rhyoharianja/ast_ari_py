class ARIError(Exception):
    """Base exception for ARI errors."""
    pass

class ResourceNotFound(ARIError):
    """Raised when a requested resource is not found (404)."""
    pass

class InvalidState(ARIError):
    """Raised when the resource is in an invalid state for the operation (409)."""
    pass
