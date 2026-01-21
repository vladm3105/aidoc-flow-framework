import json
import sys
from typing import Any, Dict
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich.panel import Panel

console = Console()

def inspect(label: str, data: Any) -> Any:
    """
    Pause execution and allow the user to inspect/modify data.
    
    Args:
        label: Description of what is being inspected.
        data: The data payload (dict, list, string, etc).
        
    Returns:
        The modified data (or original if unchanged).
    """
    # 1. Display Current State
    console.rule(f"[bold red]INSPECTOR PAUSE: {label}[/bold red]")
    
    formatted_json = json.dumps(data, indent=2, default=str)
    syntax = Syntax(formatted_json, "json", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Current Payload", expand=False))
    
    # 2. Ask for Action
    action = Prompt.ask(
        "Action", 
        choices=["continue", "edit", "abort"], 
        default="continue",
        show_choices=True
    )
    
    if action == "abort":
        console.print("[bold red]Aborting execution via Inspector.[/bold red]")
        sys.exit(1)
        
    elif action == "edit":
        # 3. Edit Mode
        console.print("[yellow]Enter new JSON payload (Press Ctrl+D to finish):[/yellow]")
        try:
            new_input = sys.stdin.read()
            # If empty (just Ctrl+D), maybe they meant no change? 
            # But usually that means "replace with this empty thing".
            # Let's assume they want to replace it.
            if not new_input.strip():
                 console.print("[dim]Empty input received. Keeping original.[/dim]")
                 return data
                 
            try:
                new_data = json.loads(new_input)
                console.print("[green]Payload updated![/green]")
                return new_data
            except json.JSONDecodeError as e:
                console.print(f"[bold red]Invalid JSON provided: {e}. Reverting to original.[/bold red]")
                return data
                
        except KeyboardInterrupt:
             console.print("\n[dim]Edit cancelled.[/dim]")
             return data

    return data

if __name__ == "__main__":
    # Test Run
    data = {"action": "buy", "symbol": "AAPL", "qty": 100}
    console.print("Running Inspector Checkpoint...")
    new_data = inspect("Trade Execution", data)
    console.print(f"Resulting Data: {new_data}")
