"""Custom exceptions for the TavoAI SDK."""


class TavoAIError(Exception):
    """Base exception for all TavoAI SDK errors."""
    pass


class PolicyEvaluationError(TavoAIError):
    """Exception raised when a policy evaluation fails."""
    pass


class PolicyNotFoundError(TavoAIError):
    """Exception raised when a policy is not found."""
    pass


class ServerConnectionError(TavoAIError):
    """Exception raised when a connection to the policy server fails."""
    pass 