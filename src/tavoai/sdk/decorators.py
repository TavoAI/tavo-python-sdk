"""Decorators for the TavoAI SDK."""

from functools import wraps
from typing import Dict, Any, Callable, Optional, Union, TypeVar

from tavoai.sdk.client import TavoAIClient
from tavoai.sdk.exceptions import PolicyEvaluationError
from tavoai.sdk.models import PolicyResult

# Type for the decorated function's result
T = TypeVar('T')

# Type for rejection handlers
InputRejectionHandler = Callable[[str, PolicyResult, Dict[str, Any]], Union[str, None]]
OutputRejectionHandler = Callable[[str, T, PolicyResult, Dict[str, Any]], Union[T, None]]


class TavoAIGuardrail:
    """
    Decorator for applying TavoAI guardrails to functions.
    
    This decorator evaluates both input and output content against specified
    guardrails and raises exceptions if the content doesn't meet the requirements.
    """
    
    def __init__(
        self,
        client: TavoAIClient,
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the decorator.
        
        Args:
            client: The TavoAI client to use for policy evaluation.
            metadata: Metadata for policy evaluation.
            config: Configuration for policy evaluation.
        """
        self.client = client
        self.metadata = metadata or {}
        self.config = config or {}
    
    def __call__(
        self, 
        input_policy: str, 
        output_policy: Optional[str] = None,
        on_input_rejection: Optional[InputRejectionHandler] = None,
        on_output_rejection: Optional[OutputRejectionHandler] = None
    ):
        """
        Apply the decorator with specified policies and optional rejection handlers.
        
        Args:
            input_policy: Policy name for input validation.
            output_policy: Policy name for output validation (defaults to input_policy).
            on_input_rejection: Optional handler for input validation failures.
              Function receives (query, result, context) and can return modified query or None to raise default error.
            on_output_rejection: Optional handler for output validation failures.
              Function receives (query, response, result, context) and can return modified response or None to raise default error.
            
        Returns:
            Decorator function that will wrap the target function.
        """
        effective_output_policy = output_policy or input_policy
        
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(query: str, *args, **kwargs) -> T:
                # Generate a request ID to link input and output evaluations
                request_id = f"req-{hash(query)}"[:16]
                
                # Context dict for rejection handlers
                context = {
                    "metadata": self.metadata,
                    "config": self.config,
                    "request_id": request_id,
                    "args": args,
                    "kwargs": kwargs
                }
                
                # Evaluate the input query
                input_result = self.client.evaluate_input(
                    content=query,
                    policy_name=input_policy,
                    metadata=self.metadata,
                    config=self.config,
                    request_id=request_id
                )
                
                # If input validation fails, handle the rejection
                if not input_result.allowed:
                    if on_input_rejection:
                        # Call the custom handler
                        modified_query = on_input_rejection(query, input_result, context)
                        if modified_query is not None:
                            # Use the modified query instead
                            query = modified_query
                        else:
                            # Handler returned None, raise the default error
                            raise PolicyEvaluationError(f"Input validation failed: {input_result}")
                    else:
                        # No custom handler, raise the default error
                        raise PolicyEvaluationError(f"Input validation failed: {input_result}")
                
                # Call the function with the input (possibly modified)
                response = func(query, *args, **kwargs)
                
                # Evaluate the output response
                output_result = self.client.evaluate_output(
                    content=response,
                    policy_name=effective_output_policy,
                    metadata=self.metadata,
                    config=self.config,
                    request_id=request_id
                )
                
                # If output validation fails, handle the rejection
                if not output_result.allowed:
                    if on_output_rejection:
                        # Call the custom handler
                        modified_response = on_output_rejection(query, response, output_result, context)
                        if modified_response is not None:
                            # Use the modified response instead
                            return modified_response
                        else:
                            # Handler returned None, raise the default error
                            raise PolicyEvaluationError(f"Output validation failed: {output_result}")
                    else:
                        # No custom handler, raise the default error
                        raise PolicyEvaluationError(f"Output validation failed: {output_result}")
                
                # Return the validated response
                return response
            
            return wrapper
        
        return decorator 