"""Live example using real Context7 MCP calls.

This example demonstrates using Context7 MCP integration in Claude Code environment
to fetch real PennyLane documentation and use it for circuit generation.

NOTE: This requires running in Claude Code environment with MCP access.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skadi.knowledge.context7_client import Context7Client


def example_with_real_mcp():
    """
    Example showing how to use Context7 with real MCP calls.

    In this Claude Code environment, we can make actual MCP calls to fetch
    PennyLane documentation dynamically.
    """
    print("=== Context7 Live MCP Example ===\n")

    # Initialize client
    client = Context7Client()
    print(f"Library ID: {client.library_id}")
    print(f"Initial cache size: {client.get_cache_stats()['size']}\n")

    # Define topics we want documentation for
    topics = [
        "qml.Hadamard qml.CNOT gates",
        "qml.RX qml.RY qml.RZ rotation gates",
        "qml.device qml.qnode quantum node",
    ]

    print("Topics to fetch:\n")
    for i, topic in enumerate(topics, 1):
        print(f"{i}. {topic}")
    print()

    # For each topic, check if we need to fetch docs
    for topic in topics:
        print(f"\n--- Topic: {topic} ---")

        if client.needs_mcp_call(topic):
            print("  Status: Not cached, MCP call needed")
            print(
                f"  To fetch: Use mcp__context7__get-library-docs with topic='{topic}'"
            )

            # In Claude Code, you would make the actual MCP call here:
            # docs = mcp__context7__get-library-docs(
            #     context7CompatibleLibraryID="/pennylaneai/pennylane",
            #     topic=topic,
            #     tokens=2000
            # )
            # client.cache_docs(topic, docs)
            # print("  Status: Fetched and cached!")

        else:
            print("  Status: Already cached")
            cached_docs = client.get_docs(topic)
            print(f"  Cached docs size: {len(cached_docs)} characters")

    print(f"\n\nFinal cache size: {client.get_cache_stats()['size']}")


def example_usage_pattern():
    """
    Show the typical usage pattern for Context7 in a real application.
    """
    print("\n\n=== Typical Usage Pattern ===\n")

    print(
        """
1. User requests circuit generation:
   "Create a Bell state circuit with Hadamard and CNOT gates"

2. CircuitGenerator calls KnowledgeAugmenter:
   - Extracts key terms: "Hadamard", "CNOT"
   - Queries Context7Client

3. Context7Client checks cache:
   - If cached: Return immediately
   - If not cached: Signal need for MCP call

4. In Claude Code environment:
   - Make MCP call to fetch docs
   - Cache the results
   - Use in prompt augmentation

5. CircuitGenerator uses augmented prompt:
   - Combines user query + Context7 docs
   - Sends to LLM for code generation
   - Returns PennyLane circuit code
"""
    )


def show_mcp_call_template():
    """Show the exact MCP call format needed."""
    print("\n\n=== MCP Call Template ===\n")

    print(
        """
In Claude Code environment, use this format:

```python
from skadi.knowledge.context7_client import Context7Client

# Initialize
client = Context7Client()
topic = "qml.Hadamard qml.CNOT gates"

# Check if we need to fetch
if client.needs_mcp_call(topic):
    # Make MCP call (in Claude Code)
    docs = mcp__context7__get_library_docs(
        context7CompatibleLibraryID="/pennylaneai/pennylane",
        topic=topic,
        tokens=2000
    )

    # Cache the result
    client.cache_docs(topic, docs)

    print(f"Fetched {len(docs)} characters of documentation")
    print(f"Extracted {len(client.extract_code_snippets(docs))} code snippets")

# Now use the cached docs
context = client.get_context(topic)
print(context)
```

The MCP call returns markdown-formatted documentation with:
- Function signatures
- Parameter descriptions
- Code examples
- Usage patterns
- Related operations
"""
    )


def main():
    """Run all examples."""
    print("=" * 70)
    print("Context7 MCP Live Integration Example")
    print("Running in Claude Code Environment")
    print("=" * 70)
    print()

    try:
        example_with_real_mcp()
        example_usage_pattern()
        show_mcp_call_template()

        print("\n" + "=" * 70)
        print("Example completed!")
        print("=" * 70)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
