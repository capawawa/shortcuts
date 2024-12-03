import click
import sys
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import track

from config import CONFIG, logger
from shortcut_doc_maker import ShortcutDocMaker
from shortcut_analyzer import ShortcutAnalyzer
from doc_generator import DocGenerator

console = Console()

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Apple Shortcuts Documentation Generator

    This tool analyzes Apple Shortcuts files and generates comprehensive documentation.
    """
    pass

@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--recursive', '-r', is_flag=True, help='Process directories recursively')
@click.option('--format', '-f', type=click.Choice(['markdown', 'html', 'json']), default='markdown',
              help='Output format for documentation')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--analyze/--no-analyze', default=True, help='Perform analysis on the shortcuts')
@click.option('--visualize/--no-visualize', default=True, help='Generate visualizations')
def process(input_path: str, recursive: bool, format: str, output: Optional[str],
           analyze: bool, visualize: bool):
    """Process shortcuts and generate documentation."""
    try:
        # Initialize components
        doc_maker = ShortcutDocMaker()
        analyzer = ShortcutAnalyzer(doc_maker)
        generator = DocGenerator(doc_maker, analyzer)
        
        # Process input
        with console.status("[bold green]Processing shortcuts..."):
            results = doc_maker.process_input(input_path)
            
        # Show processing results
        _display_processing_results(results)
        
        # Perform analysis if requested
        if analyze:
            with console.status("[bold green]Analyzing shortcuts..."):
                analysis = analyzer.analyze_all()
            _display_analysis_results(analysis)
            
            if visualize:
                with console.status("[bold green]Generating visualizations..."):
                    analyzer.generate_visualizations()
                
        # Generate documentation
        with console.status(f"[bold green]Generating {format} documentation..."):
            output_file = generator.generate(format, output)
            
        console.print(f"\n[bold green]Documentation generated:[/] {output_file}")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        logger.exception("Error in processing")
        sys.exit(1)

@cli.command()
@click.option('--format', '-f', type=click.Choice(['json', 'yaml']), default='json',
              help='Export format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def export(format: str, output: Optional[str]):
    """Export raw data in specified format."""
    try:
        doc_maker = ShortcutDocMaker()
        analyzer = ShortcutAnalyzer(doc_maker)
        generator = DocGenerator(doc_maker, analyzer)
        
        output_file = generator.export_data(format)
        console.print(f"[bold green]Data exported:[/] {output_file}")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        logger.exception("Error in export")
        sys.exit(1)

@cli.command()
def stats():
    """Display database statistics."""
    try:
        doc_maker = ShortcutDocMaker()
        analyzer = ShortcutAnalyzer(doc_maker)
        
        table = Table(title="Shortcuts Database Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Actions", str(len(doc_maker.known_actions)))
        table.add_row("Total Parameters", str(sum(len(params) for params in doc_maker.parameter_types.values())))
        table.add_row("Menu Structures", str(len(doc_maker.menu_structures)))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        logger.exception("Error in stats")
        sys.exit(1)

def _display_processing_results(results: dict):
    """Display processing results in a formatted table."""
    table = Table(title="Processing Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Files Processed", str(len(results['processed_files'])))
    table.add_row("New Actions", str(len(results['new_actions'])))
    table.add_row("Errors", str(len(results['errors'])))
    
    console.print(table)
    
    if results['new_actions']:
        console.print("\n[bold]New Actions Found:[/]")
        for action in sorted(results['new_actions']):
            console.print(f"  • {action}")
            
    if results['errors']:
        console.print("\n[bold red]Errors:[/]")
        for error in results['errors']:
            console.print(f"  • {error}")

def _display_analysis_results(analysis: dict):
    """Display analysis results in a formatted table."""
    table = Table(title="Analysis Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Common Patterns", str(len(analysis['common_patterns'])))
    table.add_row("Central Actions", str(len(analysis['action_flows']['central_actions'])))
    table.add_row("Isolated Actions", str(len(analysis['action_flows']['isolated_actions'])))
    
    console.print(table)

if __name__ == '__main__':
    cli() 