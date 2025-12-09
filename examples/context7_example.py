"""Example: Using Context7Tools to query PennyLane documentation."""

from skadi.engine import Context7Tools

# Initialize the toolkit (uses CONTEXT7_API_KEY from environment if set)
toolkit = Context7Tools()

# Search for documentation on specific topics
topics = [
    "CNOT gate",
    "qml.Hadamard",
    "quantum state measurement",
]

for topic in topics:
    print(f"\n{'=' * 80}")
    print(f"Searching for: {topic}")
    print("=" * 80)

    result = toolkit.search_pennylane_docs(topic)
    print(result)
