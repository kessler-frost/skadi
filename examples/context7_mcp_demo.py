"""Example demonstrating how to use Context7 MCP with Skadi.

This example shows how to use the real Context7 MCP integration to fetch
PennyLane documentation dynamically for circuit generation.

NOTE: This example requires running in an environment with Context7 MCP access
      (e.g., Claude Code CLI). It will not work in standard Python environments.
"""

from skadi.knowledge.context7_client import Context7Client


def demo_basic_usage():
    """Basic usage of Context7Client with caching."""
    print("\n=== Basic Context7 Client Usage ===\n")

    # Initialize the client
    client = Context7Client()
    print(f"Library ID: {client.library_id}")
    print(f"Cache size: {client.get_cache_stats()['size']}\n")

    # Example 1: Query for Hadamard gate documentation
    topic1 = "qml.Hadamard gate"
    print(
        f"Checking if MCP call needed for '{topic1}': {client.needs_mcp_call(topic1)}"
    )

    # In a Claude Code environment, you would now make the MCP call:
    # docs = mcp__context7__get-library-docs(
    #     context7CompatibleLibraryID="/pennylaneai/pennylane",
    #     topic="qml.Hadamard gate",
    #     tokens=2000
    # )
    #
    # Then cache the result:
    # client.cache_docs(topic1, docs)

    # For this demo, we'll simulate cached docs
    sample_docs = """
### Using Hadamard Gate in PennyLane

```python
import pennylane as qml

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def circuit():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.probs()
```

The Hadamard gate creates a superposition state.
"""
    client.cache_docs(topic1, sample_docs)
    print(f"Cached documentation for '{topic1}'")
    print(f"MCP call needed now: {client.needs_mcp_call(topic1)}\n")

    # Retrieve from cache
    cached = client.get_docs(topic1)
    print("Retrieved from cache:")
    print(cached[:100] + "...\n")


def demo_formatted_context():
    """Demo getting formatted context for prompts."""
    print("\n=== Formatted Context for Prompts ===\n")

    client = Context7Client()

    # Simulate cached documentation
    docs = """
### CNOT Gate Examples

```python
import pennylane as qml

dev = qml.device('default.qubit', wires=2)

@qml.qnode(dev)
def bell_state():
    qml.Hadamard(wires=0)
    qml.CNOT(wires=[0, 1])
    return qml.state()
```

The CNOT gate creates entanglement between qubits.
"""
    client.cache_docs("qml.CNOT gate", docs)

    # Get formatted context
    context = client.get_context("qml.CNOT gate")
    print("Formatted context:")
    print(context)
    print()


def demo_code_snippet_extraction():
    """Demo extracting code snippets from documentation."""
    print("\n=== Code Snippet Extraction ===\n")

    client = Context7Client()

    docs = """
Here's how to use rotation gates:

```python
import pennylane as qml

dev = qml.device('default.qubit', wires=1)

@qml.qnode(dev)
def circuit(theta):
    qml.RX(theta, wires=0)
    qml.RY(theta, wires=0)
    return qml.expval(qml.PauliZ(0))
```

And here's another example:

```python
# Simple rotation
qml.RZ(0.5, wires=0)
```
"""

    snippets = client.extract_code_snippets(docs)
    print(f"Found {len(snippets)} code snippets:\n")

    for i, snippet in enumerate(snippets, 1):
        print(f"Snippet {i}:")
        print(snippet)
        print()

    # Format for prompt
    formatted = client.format_for_prompt(docs, max_snippets=2)
    print("Formatted for LLM prompt:")
    print(formatted)


def demo_convenience_methods():
    """Demo convenience methods for common queries."""
    print("\n=== Convenience Methods ===\n")

    client = Context7Client()

    # These methods format the topic appropriately
    # In a real environment with MCP, you would then make the MCP call

    print("Operation docs topic:")
    operation_topic = "qml.Hadamard Hadamard gate operation"
    print(f"  {operation_topic}")
    print(f"  Needs MCP call: {client.needs_mcp_call(operation_topic)}\n")

    print("Decorator docs topic:")
    decorator_topic = "@qml.qnode qnode decorator"
    print(f"  {decorator_topic}")
    print(f"  Needs MCP call: {client.needs_mcp_call(decorator_topic)}\n")

    print("Device docs topic:")
    device_topic = "qml.device default.qubit device initialization"
    print(f"  {device_topic}")
    print(f"  Needs MCP call: {client.needs_mcp_call(device_topic)}\n")

    print("Template docs topic:")
    template_topic = "qml.AngleEmbedding AngleEmbedding template circuit"
    print(f"  {template_topic}")
    print(f"  Needs MCP call: {client.needs_mcp_call(template_topic)}\n")


def demo_cache_management():
    """Demo cache management features."""
    print("\n=== Cache Management ===\n")

    client = Context7Client()

    # Add multiple items to cache
    topics = ["qml.Hadamard", "qml.CNOT", "qml.RX", "qml.device"]
    for topic in topics:
        client.cache_docs(topic, f"Documentation for {topic}")

    # Check cache stats
    stats = client.get_cache_stats()
    print(f"Cache size: {stats['size']}/{stats['max_size']}")
    print(f"Cached topics: {len(stats['keys'])}\n")

    # Clear cache
    client.clear_cache()
    stats = client.get_cache_stats()
    print(f"After clearing - Cache size: {stats['size']}")


def demo_real_mcp_workflow():
    """
    Demo showing the real workflow with MCP calls.

    NOTE: This is pseudocode showing how it would work in Claude Code environment.
    """
    print("\n=== Real MCP Workflow (Pseudocode) ===\n")

    print(
        """
# Step 1: Initialize the client
from skadi.knowledge.context7_client import Context7Client

client = Context7Client()

# Step 2: Check if MCP call is needed
topic = "qml.Hadamard qml.CNOT gates"
if client.needs_mcp_call(topic):
    print(f"Need to fetch docs for: {topic}")

    # Step 3: Make MCP call (in Claude Code environment)
    # docs = mcp__context7__get-library-docs(
    #     context7CompatibleLibraryID="/pennylaneai/pennylane",
    #     topic=topic,
    #     tokens=2000
    # )

    # Step 4: Cache the result
    # client.cache_docs(topic, docs)

# Step 5: Use the cached documentation
context = client.get_context(topic)

# Step 6: Pass to circuit generator or LLM prompt
# This context can now be used to augment circuit generation
"""
    )


def main():
    """Run all demos."""
    print("=" * 60)
    print("Context7 MCP Integration Demo")
    print("=" * 60)

    try:
        demo_basic_usage()
        demo_formatted_context()
        demo_code_snippet_extraction()
        demo_convenience_methods()
        demo_cache_management()
        demo_real_mcp_workflow()

        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError running demo: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
