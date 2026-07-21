"""
Global Exceptions.

Sprint:
    2.49 - Exception Handling
"""


class AlphaEdgeAIException(Exception):
    """
    Base exception for AlphaEdge AI.
    """

    pass


class ValidationException(AlphaEdgeAIException):
    """
    Raised when validation fails.
    """

    pass


class ConfigurationException(AlphaEdgeAIException):
    """
    Raised when configuration is invalid.
    """

    pass


class ResourceNotFoundException(AlphaEdgeAIException):
    """
    Raised when a resource cannot be found.
    """

    pass
