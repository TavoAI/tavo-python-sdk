# TavoAI SDK

A Python SDK for integrating with TavoAI's regulatory policy as code (RPAC) guardrails.

[![PyPI version](https://img.shields.io/pypi/v/tavoai-sdk.svg)](https://pypi.org/project/tavoai-sdk/)
[![Python Versions](https://img.shields.io/pypi/pyversions/tavoai-sdk.svg)](https://pypi.org/project/tavoai-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Introduction

The TavoAI SDK provides a simple, intuitive interface for evaluating content against regulatory guardrails defined in the TavoAI RPAC repository. This SDK allows you to validate both input queries and output responses to ensure compliance with industry-specific regulations and best practices.

## Features

- **Easy Integration**: Simple API to validate content against regulatory policies
- **Multiple Domains**: Support for financial, healthcare, insurance and more
- **Input & Output Validation**: Validate both user queries and AI responses
- **Multiple Use Modes**: Support for both local OPA CLI evaluation and remote policy server
- **Decorator Support**: Simple decorator API to automatically validate function inputs and outputs
- **Custom Configuration**: Flexible metadata and configuration options

## Installation

```bash
pip install tavoai-sdk
```

## Quick Start

```python
from tavoai.sdk import TavoAIClient, GuardrailType

# Initialize the client with the policy server URL
client = TavoAIClient(api_base_url="http://localhost:5000")

# Evaluate an input query
input_result = client.evaluate_input(
    content="What stocks should I invest in for my retirement?",
    guardrail_type=GuardrailType.FINANCIAL_ADVICE
)

# Check if the input is allowed
if input_result.allowed:
    print("Input content is allowed!")
else:
    print("Input content is not allowed!")
    for reason in input_result.rejection_reasons:
        print(f"{reason.get('category')}: {reason.get('reason')}")
```

## Documentation

- [Getting Started](docs/getting_started.md)
- [API Reference](docs/api_reference.md)
- [Examples](examples/)

## Available Guardrails

The SDK provides the following predefined guardrail types:

### Financial Services

- `FINANCIAL_ADVICE`: Guardrails for financial advice content
- `FINANCIAL_DATA_PROTECTION`: Protection of financial data and PII
- `INVESTMENT_RECOMMENDATIONS`: Investment-specific advice
- `RETIREMENT_ADVICE`: Retirement planning and superannuation advice

### Healthcare

- `MEDICAL_INFORMATION`: General medical information guardrails
- `PATIENT_DATA_PROTECTION`: Protection of patient data and PHI
- `MENTAL_HEALTH_SUPPORT`: Mental health-related guidance
- `MEDICATION_INFORMATION`: Information about medications

### Insurance

- `INSURANCE_CLAIMS_ADVICE`: Guidance on insurance claims
- `INSURANCE_POLICY_GUIDANCE`: Information about insurance policies
- `INSURANCE_RISK_ASSESSMENT`: Assessment of insurance risks

## Decorator API

```python
from tavoai.sdk import TavoAIClient, GuardrailType, TavoAIGuardrail

client = TavoAIClient(api_base_url="http://localhost:5000")

@TavoAIGuardrail(
    client=client,
    input_guardrail=GuardrailType.FINANCIAL_ADVICE,
    output_guardrail=GuardrailType.FINANCIAL_ADVICE
)
def get_financial_advice(query: str) -> str:
    # This function would typically call an LLM API
    return "Thank you for your question about financial planning..."

# The decorator will validate both the input and output
response = get_financial_advice("How should I invest for retirement?")
```

## Development

```bash
# Clone the repository
git clone https://github.com/tavoai/tavo-python-sdk.git
cd tavo-python-sdk

# Install in development mode
pip install -e .[dev]

# Run tests
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 