# TavoAI SDK Examples

This directory contains examples demonstrating how to use the TavoAI SDK for implementing content guardrails in your applications.

## Available Examples

### 1. Client-based Approach (`client_example.py`)

The client-based approach demonstrates direct use of the TavoAI client for evaluating content:

- Direct API calls for evaluating inputs and outputs
- Handling validation rejections with custom handlers
- Suitable for applications where you need fine-grained control over the evaluation process

Run this example with:
```
python examples/client_example.py
```

### 2. Decorator-based Approach (`decorator_example.py`)

The decorator-based approach shows how to use the TavoAI decorator pattern for more elegant integration:

- Using decorators to automatically validate function inputs and outputs
- Reusing decorator instances with different policies
- Implementing custom rejection handlers within the decorator
- Perfect for wrapping around LLM response functions

Run this example with:
```
python examples/decorator_example.py
```

## Prerequisites

Before running the examples, make sure:

1. You have installed the TavoAI SDK
2. You have a policy server running (examples use a local server at http://localhost:5000)
3. For colored logs, install the optional dependency: `pip install colorlog`

## Best Practices

- The decorator pattern is generally preferred for simpler integration with existing functions
- The client approach offers more flexibility for complex evaluation flows
- Custom rejection handlers can modify content instead of just failing with an error
- Use consistent metadata and configuration across evaluations for coherent policy enforcement 