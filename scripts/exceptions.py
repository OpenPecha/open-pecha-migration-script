
class OldPechaBackendError(RuntimeError):
    """
    Raised when the old pecha-backend persons API request fails.
    """
    pass

class NewPechaBackendError(RuntimeError):
    """
    Raised when the new pecha-backend persons API request fails.
    """
    pass

class DatabaseError(RuntimeError):
    """
    Raised when a database operation fails.
    """
    pass