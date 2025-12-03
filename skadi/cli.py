"""Command-line interface for Skadi quantum circuit generation."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.syntax import Syntax
from rich.table import Table

from skadi.backends.executor import CircuitExecutor
from skadi.backends.recommender import BackendRecommender, Recommendation
from skadi.backends.registry import BackendRegistry
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
        Intent string: "create", "modify", "optimize"
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
    command: str = typer.Argument(
        ..., help="Natural language description or 'show'/'clear'"
    ),
    with_code: bool = typer.Option(False, "--with-code", help="Display generated code"),
) -> None:
    """Generate and manipulate quantum circuits using natural language."""
    # Handle special commands using match/case
    match command.lower().strip():
        case "show":
            circuit = load_circuit()
            if circuit is None:
                console.print("[yellow]No circuit found.[/yellow] Create one first.")
                raise typer.Exit(1)
            visualize_circuit(circuit, "Current Circuit")
            if with_code:
                display_code(circuit.code)
            return

        case "clear":
            if not CIRCUIT_FILE.exists():
                console.print("[yellow]No circuit file found.[/yellow]")
                raise typer.Exit(0)
            CIRCUIT_FILE.unlink()
            console.print(f"[green]✓[/green] Removed {CIRCUIT_FILE}")
            return

    # Check API key
    if not settings.skadi_api_key:
        console.print("[red]Error:[/red] SKADI_API_KEY not set")
        console.print("Please set it in your .env file or environment")
        raise typer.Exit(1)

    # Detect intent
    intent = detect_intent(command)

    # Handle "create" intent
    if intent == "create":
        console.print(f"[bold]Generating circuit:[/bold] {command}")

        generator = CircuitGenerator()
        circuit = generator.generate_circuit(command)

        visualize_circuit(circuit, "Generated Circuit")
        if with_code:
            display_code(circuit.code, "Generated Code")

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

        if with_code:
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
        if with_code:
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
        if with_code:
            display_code(modified.code, "Modified Code")

        save_circuit(modified)
        raise typer.Exit(0)


def _display_backend_menu(recommendations: list[Recommendation]) -> None:
    """Display backend selection menu with Rich."""
    table = Table(title="Available Backends")
    table.add_column("Backend", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Score", style="green")
    table.add_column("Notes", style="yellow")

    for i, rec in enumerate(recommendations):
        info = rec.backend_status.info
        notes = ", ".join(rec.reasons[:2])
        if rec.warnings:
            notes += f" [dim]({rec.warnings[0]})[/dim]"

        # Mark recommended backend
        name = info.name
        if i == 0:
            name = f"{name} [green](recommended)[/green]"

        table.add_row(
            name,
            info.backend_type.value,
            f"{rec.score:.0f}",
            notes,
        )

    console.print(table)


def _display_results(result: any) -> None:
    """Display execution results."""
    import numpy as np

    console.print()
    console.print(Panel.fit("[bold green]Execution Results[/bold green]"))

    if not hasattr(result, "__iter__") or isinstance(result, str):
        console.print(f"[cyan]Result:[/cyan] {result}")
        console.print()
        return

    result_array = np.array(result)

    # 2D array: density matrix
    if result_array.ndim == 2:
        console.print("[cyan]Density Matrix (diagonal populations):[/cyan]")
        num_bits = int(np.log2(result_array.shape[0]))
        for i in range(result_array.shape[0]):
            population = np.real(result_array[i, i])
            if population > 1e-10:
                console.print(
                    f"  |{i:0{num_bits}b}⟩⟨{i:0{num_bits}b}|: {population:.4f}"
                )
        console.print()
        return

    # 1D complex array: state vector
    if result_array.dtype in [np.complex64, np.complex128]:
        console.print("[cyan]State Vector:[/cyan]")
        num_bits = int(np.log2(len(result_array)))
        for i, amp in enumerate(result_array):
            if np.abs(amp) > 1e-10:
                console.print(f"  |{i:0{num_bits}b}⟩: {amp:.4f}")
        console.print()
        return

    # 1D real array: probabilities or measurement results
    if result_array.ndim == 1 and np.issubdtype(result_array.dtype, np.floating):
        console.print("[cyan]Probabilities:[/cyan]")
        num_bits = int(np.log2(len(result_array)))
        for i, prob in enumerate(result_array):
            if prob > 1e-10:
                console.print(f"  |{i:0{num_bits}b}⟩: {prob:.4f}")
        console.print()
        return

    # Fallback for other array types
    console.print(f"[cyan]Result:[/cyan] {result}")
    console.print()


@app.command()
def run(
    shots: Optional[int] = typer.Option(None, "--shots", "-s", help="Number of shots"),
    backend: Optional[str] = typer.Option(None, "--backend", "-b", help="Backend name"),
    auto: bool = typer.Option(False, "--auto", "-a", help="Auto-select best backend"),
    cloud: bool = typer.Option(False, "--cloud", help="Allow cloud backends"),
) -> None:
    """Execute the current circuit on a quantum backend.

    Shows available backends with recommendations and lets user choose.

    Examples:
        skadi run                    # Show backend menu, user picks
        skadi run --auto             # Auto-select recommended backend
        skadi run --backend default.qubit --shots 1000
        skadi run --cloud            # Include cloud backends in options
    """
    circuit = load_circuit()
    if circuit is None:
        console.print(
            "[red]No circuit found.[/red] Create one first with 'skadi create'"
        )
        raise typer.Exit(1)

    registry = BackendRegistry()
    recommender = BackendRecommender(registry)
    executor = CircuitExecutor(registry)

    # Get recommendations
    recommendations = recommender.recommend(circuit, allow_cloud=cloud)

    if not recommendations:
        console.print("[red]No available backends found.[/red]")
        raise typer.Exit(1)

    # Determine which backend to use
    if backend:
        selected_backend = backend
    elif auto:
        selected_backend = recommendations[0].backend_status.info.name
        console.print(
            f"[dim]Auto-selected backend:[/dim] [cyan]{selected_backend}[/cyan]"
        )
    else:
        # Display backend options and prompt user
        _display_backend_menu(recommendations)
        console.print()
        selected_backend = Prompt.ask(
            "Select backend",
            choices=[r.backend_status.info.name for r in recommendations],
            default=recommendations[0].backend_status.info.name,
        )

    # Validate backend exists
    if not registry.get(selected_backend):
        available = [s.info.name for s in registry.list_available()]
        console.print(f"[red]Backend '{selected_backend}' not available.[/red]")
        console.print(f"Available: {', '.join(available)}")
        raise typer.Exit(1)

    # Execute
    console.print()
    console.print(f"[bold]Executing on {selected_backend}...[/bold]")

    result = executor.execute(circuit, selected_backend, shots=shots)

    # Display results
    _display_results(result)


@app.command()
def backends(
    all_backends: bool = typer.Option(False, "--all", "-a", help="Show all backends"),
) -> None:
    """List available execution backends.

    Examples:
        skadi backends        # List available backends
        skadi backends --all  # List all backends (including unavailable)
    """
    registry = BackendRegistry()

    if all_backends:
        statuses = registry.list_all()
    else:
        statuses = registry.list_available()

    table = Table(title="Quantum Backends")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="magenta")
    table.add_column("Available", style="green")
    table.add_column("Description")
    table.add_column("Max Qubits")

    for status in statuses:
        info = status.info
        if status.available:
            available = "[green]Yes[/green]"
        else:
            available = f"[red]No[/red] - {status.availability_reason}"
        max_q = str(info.max_wires) if info.max_wires else "unlimited"

        table.add_row(
            info.name,
            info.backend_type.value,
            available,
            info.description,
            max_q,
        )

    console.print(table)


def cli() -> None:
    """Entry point for the console script."""
    app()


if __name__ == "__main__":
    cli()
