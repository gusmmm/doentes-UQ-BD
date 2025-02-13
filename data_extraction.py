from pathlib import Path
import json
import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.traceback import install
from rich import print as rprint
from settings import EXTRACTOR_MODELS

# Install rich traceback handler
install(show_locals=True)

# Add parent directory to Python path so we can import extractors
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from extractors.patient_extractor import PatientDataExtractor
from extractors.burn_extractor import BurnDataExtractor
from extractors.extraction_utils import extract_and_format_data

console = Console()

def main():
    try:
        # Test file path
        file_path = project_root / "data" / "md-final" / "2301.md"
        
        if not file_path.exists():
            console.print(f"[red]Error: File not found at {file_path}[/red]")
            return
            
        console.print(Panel(f"Processing file: {file_path.name}", 
                           title="Data Extraction Pipeline",
                           border_style="blue"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            # Extract and format data for MongoDB
            task = progress.add_task("Extracting data...", total=None)
            mongo_doc = extract_and_format_data(file_path, project_root)
            progress.remove_task(task)
            
        if mongo_doc:
            console.print("\n[green]Data Extraction Complete[/green]")
            console.print(Panel(
                "Models Used:\n" +
                f"- Patient Data: [cyan]{EXTRACTOR_MODELS['patient'].value}[/cyan]\n" +
                f"- Burn Data: [cyan]{EXTRACTOR_MODELS['burn'].value}[/cyan]\n" +
                f"- Medical History: [cyan]{EXTRACTOR_MODELS['medical_history'].value}[/cyan]",
                title="Extraction Details",
                border_style="green"
            ))
            
            # Print extracted data
            console.print("\n[yellow]Extracted MongoDB Document:[/yellow]")
            console.print("-" * 80)
            console.print(json.dumps(mongo_doc, indent=2, ensure_ascii=False))
            
            # Save to JSON
            output_file = project_root / "data" / "json" / f"{file_path.stem}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(mongo_doc, f, indent=2, ensure_ascii=False)
                
            console.print(f"\n[green]✓[/green] JSON output saved to: {output_file}")
        else:
            console.print("\n[red]Failed to extract data[/red]")
            
    except Exception as e:
        console.print(f"[red]Error in main extraction pipeline: {str(e)}[/red]")
        console.print_exception(show_locals=True)
        return None

if __name__ == "__main__":
    main()
