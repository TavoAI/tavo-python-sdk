# TavoAI SDK

A Python SDK for integrating with TavoAI's risk control as code (RCAC) guardrails.

[![PyPI version](https://img.shields.io/pypi/v/tavoai-sdk.svg)](https://pypi.org/project/tavoai-sdk/)
[![Python Versions](https://img.shields.io/pypi/pyversions/tavoai-sdk.svg)](https://pypi.org/project/tavoai-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 1. Introduction

The TavoAI SDK provides a simple, intuitive interface for evaluating content against regulatory guardrails defined in the TavoAI RCAC repository. This SDK allows you to validate both input queries and output responses to ensure AI risk controls are in place.

TavoAI's risk control as code (RCAC) guardrails help ensure AI systems comply with controls from industry-specific regulations across financial services, healthcare, insurance, and more. The SDK supports both synchronous validation of content through a client API and automatic validation through function decorators.

### Features

- **Easy Integration**: Simple API to validate content against risk controls
- **Input & Output Validation**: Validate both user queries and AI responses
- **Multiple Use Modes**: Support for both local OPA CLI evaluation and remote policy server
- **Decorator Support**: Simple decorator API to automatically validate function inputs and outputs
- **Custom Configuration**: Flexible metadata and configuration options

## Installation

```bash
pip install tavoai-sdk
```

## 2. Get Started with Local Dev Environment

### 2.1 Install tavo-cli Tool to Spin Up a Local Server

To use the TavoAI SDK, you'll need a running policy server. The easiest way to get started is with the tavo-cli tool.

For installation instructions, please visit the official tavo-cli GitHub repository:

```
https://github.com/TavoAI/tavo-cli#tavo-cli
```

The repository provides platform-specific installation instructions for macOS and Linux.

### 2.2 Local Dev Server Usage

See instructions for the local dev server here:

```
https://github.com/TavoAI/tavo-cli#usage
```

## 3. Quick Start

### 3.1 Client API

```python
from tavoai.sdk import TavoAIClient

# Initialize the client with the policy server URL
client = TavoAIClient(api_base_url="http://localhost:5000")

# Example metadata and configuration
metadata = {
    "jurisdiction": "US",
    "industry": "financial",
    "use_case": "investment_advice"
}

config = {
    "pii_detection_enabled": True,
    "misinformation_detection_enabled": True
}

# Evaluate an input query
input_result = client.evaluate_input(
    content="What stocks should I invest in for my retirement?",
    policy_name="financial_advice_input",
    metadata=metadata,
    config=config
)

# Check if the input is allowed
if input_result.allowed:
    print("Input content is allowed!")
else:
    print("Input content is not allowed!")
    for reason in input_result.rejection_reasons:
        print(f"{reason.get('category')}: {reason.get('reason')}")

# Evaluate an output response
output_result = client.evaluate_output(
    content="While I cannot provide specific investment advice...",
    policy_name="financial_advice_output",
    metadata=metadata,
    config=config
)
```

### 3.2 Decorator API

The decorator API provides a more convenient way to automatically validate function inputs and outputs:

```python
from tavoai.sdk import TavoAIClient, TavoAIGuardrail

# Initialize client
client = TavoAIClient(api_base_url="http://localhost:5000")

# Create a guardrail decorator with shared configuration
guardrail = TavoAIGuardrail(
    client=client,
    metadata={"jurisdiction": "US", "industry": "financial"}
)

# Apply decorator with specific policy names
@guardrail("financial_advice_input", "financial_advice_output")
def get_financial_advice(query: str) -> str:
    # This function would typically call an LLM API
    return "Thank you for your question about financial planning..."

# The decorator will validate both the input and output
response = get_financial_advice("How should I invest for retirement?")
```

## 4. Examples

The SDK includes several example scripts demonstrating different usage patterns:

- **Basic Usage**: Simple examples of using the client and decorator APIs
- **Client Example**: Detailed examples of using the client API for input and output validation
- **Decorator Example**: Detailed examples of using the decorator API for automatic validation

See the [examples directory](examples/) for full working examples.

### Controls Examples

See the [cli repo](https://github.com/TavoAI/tavo-cli/tree/master/opa/controls_examples) for some pre-populated controls in Rego code.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 