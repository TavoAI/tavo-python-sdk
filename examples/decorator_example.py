#!/usr/bin/env python
"""Example demonstrating the TavoAI SDK decorator-based approach."""

import logging
from tavoai.sdk import TavoAIClient, TavoAIGuardrail
from tavoai.sdk.exceptions import PolicyEvaluationError

# Configure logging with a consistent format
# Note: If colorlog is installed, logs will be color-coded by level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Prevent duplicate log messages
logging.getLogger("tavoai_sdk").propagate = False


def main():
    """Run decorator-based approach examples."""
    # Initialize the client with the policy server URL
    client = TavoAIClient(api_base_url="http://localhost:5000")
    
    # Example metadata and configuration
    metadata = {
        "jurisdiction": "US",
        "user": {
            "id": "user123",
            "type": "authenticated",
            "access_level": "standard"
        },
        "industry": "financial",
        "use_case": "investment_advice"
    }
    
    config = {
        "pii_detection_enabled": True,
        "pii_allowed_with_consent": False,
        "misinformation_detection_enabled": True,
        "bias_detection_enabled": True
    }
    
    # Basic decorator example
    print("\n=== Basic decorator example ===")
    
    # Create a decorator with shared configuration
    guardrail = TavoAIGuardrail(
        client=client,
        metadata=metadata,
        config=config
    )
    
    # Apply decorator with specific policy names
    @guardrail("financial_advice_input", "financial_advice_output")
    def get_financial_advice(query: str) -> str:
        """Generate financial advice response (would typically call an LLM API)."""
        return """
        Thank you for your question about financial planning.
        
        I want to be clear that I cannot provide personalized investment recommendations. 
        All investments carry risk, and past performance is not indicative of future results.
        
        Generally speaking, retirement planning often involves diversification, considering 
        your time horizon, and aligning investments with your risk tolerance. 
        
        Please consult with a qualified financial advisor who can review your specific 
        circumstances before making investment decisions.
        """
    
    # Apply the same decorator with different policies to another function
    @guardrail("medical_information_input", "medical_information_output")
    def get_health_advice(query: str) -> str:
        """Generate health advice response (would typically call an LLM API)."""
        return """
        Thank you for your health-related question.
        
        I want to clarify that I can provide general health information,
        but this should not replace professional medical advice. 
        
        Please consult with a qualified healthcare provider for personalized
        medical guidance based on your specific health situation.
        """
    
    try:
        response = get_financial_advice("How should I invest for retirement?")
        print(f"Financial advice response: {response[:50]}...")
        
        health_response = get_health_advice("What are some general health tips?")
        print(f"Health advice response: {health_response[:50]}...")
    except PolicyEvaluationError as e:
        print(f"Error: {e}")
    
    # Advanced example with custom rejection handlers
    print("\n=== Example with custom rejection handlers ===")
    
    def handle_input_rejection(query, result, context):
        """Custom handler for input validation failures."""
        print(f"Input handler: Rejected query: '{query}'")
        print(f"Rejection reasons: {len(result.rejection_reasons)}")
        
        # If it's a specific stock recommendation, generalize it
        if "stock" in query.lower() and "recommend" in query.lower():
            return "Can you provide general retirement planning advice?"
        
        # Return None to indicate we couldn't fix it, let the decorator raise the error
        return None
    
    def handle_output_rejection(query, response, result, context):
        """Custom handler for output validation failures."""
        print(f"Output handler: Response rejected for query: '{query}'")
        print(f"Rejection reasons: {len(result.rejection_reasons)}")
        
        # Add a disclaimer to try to make the response compliant
        disclaimer = """
        DISCLAIMER: This is general information only and not financial advice.
        Please consult with a qualified professional for specific advice.
        """
        
        return response + disclaimer
    
    # Create a decorator with shared configuration
    guardrail_with_handlers = TavoAIGuardrail(
        client=client,
        metadata=metadata,
        config=config
    )
    
    # Apply the decorator with handlers
    @guardrail_with_handlers(
        "financial_advice_input", 
        "financial_advice_output",
        on_input_rejection=handle_input_rejection,
        on_output_rejection=handle_output_rejection
    )
    def get_custom_financial_advice(query: str) -> str:
        """Generate financial advice that might need modification by handlers."""
        return """
        Based on historical performance, investing in index funds that track the overall
        market has been a reliable strategy for many retirement investors.
        """
    
    try:
        # Try with an input that might be rejected
        print("Trying a potentially problematic query...")
        response = get_custom_financial_advice("What stocks should I recommend to my clients?")
        print(f"Response with handler: {response[:50]}...")
        
        # Try with a response that might be rejected (the function's output)
        print("Trying with the function's potentially problematic response...")
        response = get_custom_financial_advice("How should I invest for retirement?")
        print(f"Modified response length: {len(response)}")
    except PolicyEvaluationError as e:
        print(f"Error even with handlers: {e}")


if __name__ == "__main__":
    main() 