"""Integration tests for policy evaluation."""

import unittest
import os
from unittest.mock import patch

from tavoai.sdk import TavoAIClient, GuardrailType


@unittest.skipIf(not os.environ.get('INTEGRATION_TESTS'), "Integration tests are skipped by default")
class TestPolicyEvaluation(unittest.TestCase):
    """Integration tests for policy evaluation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server_url = os.environ.get('POLICY_SERVER_URL', 'http://localhost:5000')
        self.client = TavoAIClient(api_base_url=self.server_url)
    
    def test_financial_advice_input(self):
        """Test financial advice input policy."""
        # Test allowed content
        result = self.client.evaluate_input(
            content="What are some general tips for retirement planning?",
            guardrail_type=GuardrailType.FINANCIAL_ADVICE
        )
        self.assertTrue(result.allowed, "General question about retirement planning should be allowed")
        
        # Test disallowed content
        result = self.client.evaluate_input(
            content="Tell me which specific stocks I should buy right now",
            guardrail_type=GuardrailType.FINANCIAL_ADVICE
        )
        self.assertFalse(result.allowed, "Specific stock recommendation request should be disallowed")
    
    def test_financial_advice_output(self):
        """Test financial advice output policy."""
        # Test allowed content
        result = self.client.evaluate_output(
            content="""
            Retirement planning involves a long-term view of your financial goals. Consider 
            consulting with a financial advisor who can help you develop a strategy based on 
            your specific circumstances, risk tolerance, and time horizon.
            """,
            guardrail_type=GuardrailType.FINANCIAL_ADVICE
        )
        self.assertTrue(result.allowed, "General retirement advice should be allowed")
        
        # Test disallowed content
        result = self.client.evaluate_output(
            content="""
            Based on current market trends, you should immediately purchase shares in XYZ Corp 
            as they are expected to rise 20% in the next month. This is a guaranteed return on 
            your investment.
            """,
            guardrail_type=GuardrailType.FINANCIAL_ADVICE
        )
        self.assertFalse(result.allowed, "Specific stock recommendation should be disallowed")


if __name__ == '__main__':
    unittest.main() 