#!/usr/bin/env python
"""Basic usage example for the TavoAI SDK."""

import logging
from tavoai.sdk import TavoAIClient, TavoAIGuardrail
from tavoai.sdk.exceptions import PolicyEvaluationError

# Configure logging only once with a consistent format
# Note: If colorlog is installed, logs will be color-coded by level
# pip install colorlog
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Prevent duplicate log messages by disabling propagation from the SDK logger
logging.getLogger("tavoai_sdk").propagate = False

def main():
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
    
    # Evaluate an input query
    input_result = client.evaluate_input(
        content="What stocks should I invest in for my retirement?",
        policy_name="financial_advice_input",
        metadata=metadata,
        config=config
    )
    
    if input_result.allowed:
        print("Input content is allowed!")
        
        # Evaluate an output response
        output_result = client.evaluate_output(
            content="""
            Thank you for your interest in retirement planning.
            
            I want to clarify that I cannot provide specific investment advice or stock recommendations. 
            Investment decisions should be based on your individual financial situation, goals, 
            risk tolerance, and time horizon.
            
            For retirement planning, it's generally advisable to:
            - Diversify your investments across different asset classes
            - Consider your time horizon and risk tolerance
            - Regularly review and adjust your portfolio
            - Consider consulting with a licensed financial advisor
            
            Past performance is not indicative of future results, and all investments involve risk 
            including the possible loss of principal.
            
            Would you like general information about different investment options for retirement planning instead?
            """,
            policy_name="financial_advice_output",
            metadata=metadata,
            config=config
        )
        
        if output_result.allowed:
            print("Output content is allowed!")
        else:
            print(f"Output content is not allowed: {output_result}")
    else:
        print(f"Input content is not allowed: {input_result}")
    
    # Example with rejection handler
    print("\n=== Example with custom rejection handler ===")
    
    def handle_input_rejection(result):
        print(f"Input was rejected with {len(result.rejection_reasons)} reason(s):")
        for reason in result.rejection_reasons:
            print(f"  - {reason.get('category', 'Unknown')}: {reason.get('reason', 'No reason provided')}")
        
        # Return a modified query that should pass the guardrail
        print("Returning a more general query instead...")
        return "What are some general considerations for retirement planning?"
    
    # Evaluate with a specific stock recommendation request that's likely to be rejected
    modified_query = client.evaluate_input(
        content="Tell me which specific stocks I should invest in right now for maximum returns",
        policy_name="financial_advice_input",
        metadata=metadata,
        config=config,
        on_rejection=handle_input_rejection
    )
    
    # If we have a string, it means the rejection handler was triggered and returned a modified query
    if isinstance(modified_query, str):
        print(f"Using modified query: {modified_query}")
        
        # Now evaluate the modified query
        result = client.evaluate_input(
            content=modified_query,
            policy_name="financial_advice_input"
        )
        
        if result.allowed:
            print("Modified query is allowed!")
        else:
            print("Modified query was still rejected")
    
    # Example with decorator
    print("\n=== Example with decorator ===")
    
    # Create a decorator with shared configuration
    guardrail = TavoAIGuardrail(
        client=client,
        metadata=metadata,
        config=config
    )
    
    # Apply decorator with specific policy names
    @guardrail("financial_advice_input", "financial_advice_output")
    def get_financial_advice(query: str) -> str:
        # This function would typically call an LLM API
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
        
    # Example with custom rejection handlers in decorator
    print("\n=== Example with custom rejection handlers in decorator ===")
    
    # Define custom rejection handlers for decorator
    def handle_decorator_input_rejection(query, result, context):
        print(f"Decorator input handler: Rejected query: '{query}'")
        print(f"Rejection reasons: {len(result.rejection_reasons)}")
        
        # If it's a specific stock recommendation, generalize it
        if "stock" in query.lower() and "recommend" in query.lower():
            return "Can you provide general retirement planning advice?"
        
        # Return None to indicate we couldn't fix it, let the decorator raise the error
        return None
    
    def handle_decorator_output_rejection(query, response, result, context):
        print(f"Decorator output handler: Response rejected for query: '{query}'")
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
        on_input_rejection=handle_decorator_input_rejection,
        on_output_rejection=handle_decorator_output_rejection
    )
    def get_custom_financial_advice(query: str) -> str:
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
    except ValueError as e:
        print(f"Error even with handlers: {e}")

if __name__ == "__main__":
    main() 