__author__ = 'daniel'

class FrankError(Exception):
    """
    Should not happen :-)
    """
    pass

class ArgumentError(FrankError):
    """
    Raised when an invalid argument is passed
    """
    pass

class TimeoutError(FrankError):
    """
    Raised when query execution failed due to a timeout
    """
    pass

class ConnectionError(FrankError):
    """
    Raised when query execution failed due to a connection error
    """
    pass

class HttpError(FrankError):
    """
    Raised when an HTTP error occured while trying to execute a query
    """
    pass
