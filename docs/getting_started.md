# Getting Started with TavoAI SDK

The TavoAI SDK provides a simple, intuitive interface for evaluating content against regulatory guardrails defined in the TavoAI RPAC repository. This guide will help you set up and start using the SDK.

## Installation

### Prerequisites

1. Choose one of the following options:
   - **Option 1 (CLI)**: Install the Open Policy Agent (OPA) CLI: https://www.openpolicyagent.org/docs/latest/#1-download-opa
   - **Option 2 (Server)**: Deploy the TavoAI Policy Server

2. Clone the TavoAI RPAC repository for the policies:
   ```bash
   git clone https://github.com/tavoai/tavoai-rpac.git
   ```

### Install the SDK

```bash
pip install tavoai-sdk
```

For development:

```bash
pip install -e .[dev]
```

## Basic Usage

Here's how to use the SDK to evaluate content against regulatory guardrails:

```python
from tavoai.sdk import TavoAIClient, GuardrailType

# Initialize the client with CLI mode (default)
client = TavoAIClient(rpac_directory="/path/to/tavoai-rpac")

# Or initialize with Policy Server mode
# client = TavoAIClient(api_base_url="http://localhost:5000")

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

# Evaluate an output response
output_result = client.evaluate_output(
    content="While I cannot provide specific investment advice...",
    guardrail_type=GuardrailType.FINANCIAL_ADVICE
)

# Check if the output is allowed
if output_result.allowed:
    print("Output content is allowed!")
else:
    print("Output content is not allowed!")
    for reason in output_result.rejection_reasons:
        print(f"{reason.get('category')}: {reason.get('reason')}")
```

## Using the Decorator

For a more convenient approach, you can use the `TavoAIGuardrail` decorator:

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

## Next Steps

- Check out the [API Reference](./api_reference.md) for detailed information about the SDK's classes and methods
- Explore the [examples](../examples) directory for more usage examples
- Learn how to [customize policies](./custom_policies.md) to fit your specific needs 