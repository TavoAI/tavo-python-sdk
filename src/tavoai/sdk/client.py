"""Client for interacting with TavoAI regulatory guardrails."""

import logging
from typing import Dict, Any, Optional, Callable

import requests

from tavoai.sdk.models import PolicyResult, ContentType
from tavoai.sdk.exceptions import (
    PolicyEvaluationError,
    PolicyNotFoundError,
    ServerConnectionError
)
from tavoai.sdk.utils import configure_logger


class TavoAIClient:
    """
    Client for interacting with TavoAI regulatory guardrails.
    
    This client interacts with a remote policy server to evaluate
    content against regulatory policies.
    """
    
    def __init__(
        self, 
        api_base_url: str = "http://localhost:5000",
        log_level: int = logging.INFO
    ):
        """
        Initialize the TavoAI client.
        
        Args:
            api_base_url: Base URL for the policy server API.
            log_level: Logging level.
        """
        self.api_base_url = api_base_url
        self.logger = configure_logger("tavoai_sdk", log_level)
    
    def _evaluate_policy(self, policy_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a policy against input data via REST API.
        
        Args:
            policy_name: Name of the policy to evaluate.
            input_data: Input data to evaluate against the policy.
            
        Returns:
            Policy evaluation result.
            
        Raises:
            PolicyNotFoundError: If the policy is not found
            ServerConnectionError: If connection to the server fails
            PolicyEvaluationError: If evaluation fails for other reasons
        """
        try:
            # Use the RESTful endpoint /policies/{policy_name}/evaluate
            response = requests.post(
                f"{self.api_base_url}/policies/{policy_name}/evaluate",
                json={"input": input_data},
                timeout=10
            )
            
            if response.status_code == 404:
                msg = f"Policy '{policy_name}' not found"
                self.logger.error(msg)
                raise PolicyNotFoundError(msg)
            elif response.status_code != 200:
                msg = f"Policy evaluation failed: {response.text}"
                self.logger.error(msg)
                raise PolicyEvaluationError(msg)
            
            return response.json()
            
        except requests.exceptions.ConnectionError:
            msg = f"Could not connect to server at {self.api_base_url}"
            self.logger.error(msg)
            raise ServerConnectionError(msg)
        except requests.exceptions.Timeout:
            msg = f"Connection to {self.api_base_url} timed out"
            self.logger.error(msg)
            raise ServerConnectionError(msg)
        except (PolicyNotFoundError, ServerConnectionError, PolicyEvaluationError):
            # Re-raise these specific exceptions
            raise
        except Exception as e:
            msg = f"Error evaluating policy: {str(e)}"
            self.logger.error(msg)
            raise PolicyEvaluationError(msg)
    
    def _evaluate_content(
        self,
        content: str,
        policy_name: str,
        content_type: ContentType,
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        on_rejection: Optional[Callable[[PolicyResult], Any]] = None
    ) -> PolicyResult:
        """
        Evaluate content against a specified policy.
        
        Args:
            content: Content to evaluate.
            policy_name: Name of the policy to evaluate against.
            content_type: Type of content (input or output).
            metadata: Optional metadata for policy evaluation.
            config: Optional configuration for policy evaluation.
            request_id: Optional request ID for tracking.
            on_rejection: Optional callback function called when content is not allowed.
            
        Returns:
            PolicyResult object containing the evaluation result,
            or the result of the on_rejection callback if provided and content is not allowed.
            
        Raises:
            Various exceptions from _evaluate_policy
        """
        self.logger.info(f"Evaluating {content_type.value} content against {policy_name} policy")
        
        # Construct the input data
        input_data = {
            "content_type": content_type.value,
            "content": content,
            "metadata": metadata or {},
            "config": config or {},
            "request_id": request_id or "req-" + str(hash(content))[:8]
        }
        
        try:
            # Evaluate the policy
            result = self._evaluate_policy(policy_name, input_data)
            
            # Parse the result
            allowed = result.get("allow", False)
            rejection_reasons = result.get("rejection_reasons", [])
            
            # Log the result
            self.logger.info(f"Policy evaluation result: {result}")
            
            # Create the PolicyResult
            policy_result = PolicyResult(allowed, rejection_reasons)
            
            # Call rejection handler if content is not allowed and a handler is provided
            if not allowed and on_rejection:
                return on_rejection(policy_result)
            
            return policy_result
        
        except Exception as e:
            self.logger.error(f"Policy evaluation failed: {str(e)}")
            # Re-raise the exception to be handled by the caller
            raise
    
    def evaluate_input(
        self,
        content: str,
        policy_name: str,
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        on_rejection: Optional[Callable[[PolicyResult], Any]] = None
    ) -> PolicyResult:
        """
        Evaluate input content against a policy.
        
        Args:
            content: Input content to evaluate.
            policy_name: Name of the policy to evaluate against.
            metadata: Optional metadata for policy evaluation.
            config: Optional configuration for policy evaluation.
            request_id: Optional request ID for tracking.
            on_rejection: Optional callback function called when content is not allowed.
            
        Returns:
            PolicyResult object containing the evaluation result,
            or the result of the on_rejection callback if provided and content is not allowed.
        """
        return self._evaluate_content(
            content, 
            policy_name, 
            ContentType.INPUT, 
            metadata, 
            config, 
            request_id, 
            on_rejection
        )
    
    def evaluate_output(
        self,
        content: str,
        policy_name: str,
        metadata: Optional[Dict[str, Any]] = None,
        config: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        on_rejection: Optional[Callable[[PolicyResult], Any]] = None
    ) -> PolicyResult:
        """
        Evaluate output content against a policy.
        
        Args:
            content: Output content to evaluate.
            policy_name: Name of the policy to evaluate against.
            metadata: Optional metadata for policy evaluation.
            config: Optional configuration for policy evaluation.
            request_id: Optional request ID for tracking.
            on_rejection: Optional callback function called when content is not allowed.
            
        Returns:
            PolicyResult object containing the evaluation result,
            or the result of the on_rejection callback if provided and content is not allowed.
        """
        return self._evaluate_content(
            content, 
            policy_name, 
            ContentType.OUTPUT, 
            metadata, 
            config, 
            request_id, 
            on_rejection
        ) 