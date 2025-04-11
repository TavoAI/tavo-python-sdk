#!/usr/bin/env python
"""Example demonstrating the TavoAI SDK client-based approach."""

import logging
from tavoai.sdk import TavoAIClient

# Configure logging with a consistent format
# Note: If colorlog is installed, logs will be color-coded by level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# Prevent duplicate log messages
logging.getLogger("tavoai_sdk").propagate = False


def main():
    """Run client-based approach examples."""
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
    
    # Basic direct evaluation example
    print("\n=== Basic client evaluation example ===")
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
    
    # Example with custom rejection handler
    print("\n=== Example with custom rejection handler ===")
    
    def handle_input_rejection(result):
        """Custom handler for rejected input."""
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


if __name__ == "__main__":
    main() 