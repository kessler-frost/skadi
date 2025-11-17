"""Command-line interface for Skadi quantum circuit generation."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from skadi.config import settings
from skadi.core.circuit_generator import CircuitGenerator
from skadi.core.circuit_manipulator import CircuitManipulator
from skadi.core.circuit_representation import CircuitRepresentation

app = typer.Typer(
    help="Skadi - Generate and manipulate quantum circuits using natural language"
)
console = Console()

CIRCUIT_FILE = Path("circuit.py")


def detect_intent(command: str) -> str:
    """Detect user intent from command text.

    Args:
        command: Natural language command string

    Returns:
        Intent string: "create", "modify", "optimize", "show"
    """
    command_lower = command.lower()

    if any(keyword in command_lower for keyword in ["create", "new", "generate"]):
        return "create"

    if any(
        keyword in command_lower
        for keyword in ["modify", "update", "change", "add", "remove"]
    ):
        return "modify"

    if "optimize" in command_lower:
        return "optimize"

    if any(keyword in command_lower for keyword in ["show", "display", "visualize"]):
        return "show"

    # Default: create if no circuit exists, otherwise modify
    return "create" if not CIRCUIT_FILE.exists() else "modify"


def save_circuit(circuit: CircuitRepresentation) -> None:
    """Save circuit code to circuit.py file.

    Args:
        circuit: CircuitRepresentation to save
    """
    CIRCUIT_FILE.write_text(circuit.code)
    console.print(f"[green]✓[/green] Circuit saved to {CIRCUIT_FILE}")


def load_circuit() -> Optional[CircuitRepresentation]:
    """Load circuit from circuit.py file.

    Returns:
        CircuitRepresentation if file exists, None otherwise
    """
    if not CIRCUIT_FILE.exists():
        return None

    code = CIRCUIT_FILE.read_text()

    # Execute code to get qnode
    import pennylane as qml

    namespace = {"qml": qml, "pennylane": qml}
    exec(code, namespace)
    qnode = namespace.get("circuit")

    return CircuitRepresentation(
        qnode=qnode,
        code=code,
        description="Loaded from circuit.py",
    )


def visualize_circuit(circuit: CircuitRepresentation, title: str = "Circuit") -> None:
    """Display circuit visualization and specs.

    Args:
        circuit: CircuitRepresentation to visualize
        title: Panel title
    """
    # Get visualization
    visualization = circuit.get_visualization()

    # Get resource summary
    resources = circuit.get_resource_summary()

    # Format stats
    stats = (
        f"[cyan]Operations:[/cyan] {resources['num_operations']}  "
        f"[cyan]Depth:[/cyan] {resources['depth']}  "
        f"[cyan]Qubits:[/cyan] {resources['num_wires']}  "
        f"[cyan]Params:[/cyan] {resources['num_trainable_params']}"
    )

    # Display visualization panel
    console.print()
    console.print(
        Panel(
            visualization,
            title=f"[bold blue]{title}[/bold blue]",
            subtitle=stats,
            border_style="blue",
        )
    )
    console.print()


def display_code(code: str, title: str = "Generated Code") -> None:
    """Display syntax-highlighted Python code.

    Args:
        code: Python code string
        title: Panel title
    """
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    console.print()
    console.print(
        Panel(syntax, title=f"[bold green]{title}[/bold green]", border_style="green")
    )
    console.print()


@app.command()
def main(
    command: str,
    no_code: bool = typer.Option(False, "--no-code", help="Don't display code output"),
) -> None:
    """Process natural language commands to generate or manipulate quantum circuits.

    Args:
        command: Natural language description of desired circuit or operation
        no_code: If True, suppress code display

    Examples:
        skadi "Create a Bell state circuit"
        skadi "Modify the circuit to add a phase gate" --no-code
        skadi "Optimize the current circuit"
        skadi "Show the current circuit"
        skadi clear  (to remove circuit.py)
    """
    # Handle "clear" as a special command
    if command.lower().strip() == "clear":
        if not CIRCUIT_FILE.exists():
            console.print("[yellow]No circuit file found.[/yellow]")
            raise typer.Exit(0)

        CIRCUIT_FILE.unlink()
        console.print(f"[green]✓[/green] Removed {CIRCUIT_FILE}")
        raise typer.Exit(0)

    # Check API key
    if not settings.skadi_api_key:
        console.print("[red]Error:[/red] SKADI_API_KEY not set")
        console.print("Please set it in your .env file or environment")
        raise typer.Exit(1)

    # Detect intent
    intent = detect_intent(command)

    # Handle "show" intent
    if intent == "show":
        circuit = load_circuit()
        if circuit is None:
            console.print("[yellow]No circuit found.[/yellow] Create one first.")
            raise typer.Exit(1)

        visualize_circuit(circuit, "Current Circuit")
        if not no_code:
            display_code(circuit.code)
        raise typer.Exit(0)

    # Handle "create" intent
    if intent == "create":
        console.print(f"[bold]Generating circuit:[/bold] {command}")

        generator = CircuitGenerator()
        circuit = generator.generate_circuit(command)

        if not no_code:
            display_code(circuit.code, "Generated Code")
        visualize_circuit(circuit, "Generated Circuit")

        save_circuit(circuit)
        raise typer.Exit(0)

    # Handle "modify" and "optimize" intents (require existing circuit)
    circuit = load_circuit()
    if circuit is None:
        console.print(
            "[yellow]No circuit found.[/yellow] Creating a new one instead..."
        )

        generator = CircuitGenerator()
        circuit = generator.generate_circuit(command)

        if not no_code:
            display_code(circuit.code, "Generated Code")
        visualize_circuit(circuit, "Generated Circuit")

        save_circuit(circuit)
        raise typer.Exit(0)

    manipulator = CircuitManipulator()

    # Handle "optimize" intent
    if intent == "optimize":
        console.print(f"[bold]Optimizing circuit:[/bold] {command}")

        # Show original
        console.print("[dim]Original:[/dim]")
        visualize_circuit(circuit, "Original Circuit")

        # Optimize
        optimized = manipulator.optimize(circuit, level="aggressive", num_passes=2)

        # Show optimized
        visualize_circuit(optimized, "Optimized Circuit")
        if not no_code:
            display_code(optimized.code, "Optimized Code")

        # Show improvement
        if optimized.transform_history:
            improvement = optimized.transform_history[-1].get("improvement", {})
            if improvement:
                console.print("[bold green]Optimization Results:[/bold green]")
                console.print(
                    f"  Operations reduced: {improvement.get('operations_reduced', 0)}"
                )
                console.print(f"  Depth reduced: {improvement.get('depth_reduced', 0)}")
                console.print()

        save_circuit(optimized)
        raise typer.Exit(0)

    # Handle "modify" intent
    if intent == "modify":
        console.print(f"[bold]Modifying circuit:[/bold] {command}")

        # Show original
        console.print("[dim]Original:[/dim]")
        visualize_circuit(circuit, "Original Circuit")

        # Modify
        modified = manipulator.rewrite(circuit, command)

        # Show modified
        visualize_circuit(modified, "Modified Circuit")
        if not no_code:
            display_code(modified.code, "Modified Code")

        save_circuit(modified)
        raise typer.Exit(0)


def cli() -> None:
    """Entry point for the console script."""
    app()


if __name__ == "__main__":
    cli()
