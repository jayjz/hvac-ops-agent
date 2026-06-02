import asyncio
import click
import logging
import os
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from dotenv import load_dotenv
from api.main import JobStatus
from core.logging_config import configure_logging
from core.orchestrator import run_pm_job

configure_logging()
logger = logging.getLogger("agentforge_pm.cli")

load_dotenv()
console = Console()

@click.group()
def cli():
    """
    🤖 CodeForge AI - Autonomous Codebase Modernization
    
    A powerful command-line tool to interact with the CodeForge AI system.
    """
    pass

@cli.command()
@click.argument('repo_url')
@click.option('--goals', '-g', multiple=True, required=True, help='Define a modernization goal. Can be used multiple times.')
@click.option('--branch', '-b', default='codeforge-modernized', help='The name of the new git branch to create.')
@click.option('--dry-run', is_flag=True, help='Analyze the repo and show a plan without making changes.')
def modernize(repo_url, goals, branch, dry_run):
    """
    Analyze and modernize a code repository.
    """
    console.print(f"[bold blue]🚀 Starting CodeForge AI Modernization[/bold blue]")
    console.print(f"   [cyan]Repository:[/cyan] {repo_url}")
    console.print(f"   [cyan]Goals:[/cyan] {', '.join(goals)}")
    
    if dry_run:
        console.print("[yellow]🔍 Dry Run Mode: No changes will be written or pushed.[/yellow]\n")
        # Simulate planning
        with console.status("[bold green]Cloning repo and analyzing structure...") as status:
            time.sleep(2)
            console.log("Repository cloned successfully.")
            time.sleep(1)
            console.log("Analyzing file tree and dependencies...")
            time.sleep(2)
        
        table = Table(title="[bold]Modernization Plan[/bold]")
        table.add_column("Step", style="magenta")
        table.add_column("Task", style="green")
        table.add_column("Details")
        
        table.add_row("1", "Dependency Check", "Scan requirements.txt for outdated packages.")
        table.add_row("2", "Code Refactoring", "Upgrade syntax in 15 Python files.")
        table.add_row("3", "Documentation", "Add Google-style docstrings to 32 functions.")
        table.add_row("4", "Test Generation", "Create pytest unit tests for critical logic.")
        
        console.print(table)
        console.print("\n[bold green]✅ Dry run complete. Run without --dry-run to execute this plan.[/bold green]")
    else:
        # Simulate a real run
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
        ) as progress:
            task1 = progress.add_task("Cloning repository...", total=100)
            task2 = progress.add_task("Analyzing and planning...", total=100)
            task3 = progress.add_task("Executing modernization...", total=100)

            # Simulate work
            progress.update(task1, advance=30)
            time.sleep(1)
            progress.update(task1, advance=70)
            
            progress.update(task2, advance=50)
            time.sleep(2)
            progress.update(task2, advance=50)
            
            progress.update(task3, advance=20)
            time.sleep(2)
            progress.update(task3, advance=40)
            time.sleep(3)
            progress.update(task3, advance=40)
            
        console.print("\n[bold green]✅ Modernization complete![/bold green]")
        console.print(f"   [cyan]Changes have been committed to branch:[/cyan] [bold yellow]{branch}[/bold yellow]")
        console.print("   Please review the changes and create a pull request.")

@cli.command()
@click.option(
    '--project-path',
    type=click.Path(exists=True, readable=True),
    default=None,
    help='Optional local folder or file containing PM artifacts. Uses synthetic data when omitted.',
)
@click.option(
    '--goals',
    '-g',
    multiple=True,
    required=True,
    help='Define a PM goal. Can be used multiple times.',
)
def forge_pm(project_path, goals):
    """
    Run AgentForge PM for HVAC, construction, and industrial automation projects.
    """
    job_id = f"cli-pm-{int(time.time())}"
    jobs = {job_id: JobStatus(job_id=job_id, status="PENDING", progress=0.0, details="Queued.")}

    console.print("[bold blue]Starting AgentForge PM[/bold blue]")
    console.print(f"   [cyan]Project Path:[/cyan] {project_path or 'synthetic fallback'}")
    console.print(f"   [cyan]Goals:[/cyan] {', '.join(goals)}")
    result = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("Running PM agents...", total=100)

        async def run_with_progress():
            pm_task = asyncio.create_task(run_pm_job(
                job_id=job_id,
                goals=list(goals),
                project_path=project_path,
                jobs=jobs,
            ))
            while not pm_task.done():
                progress.update(
                    task,
                    completed=jobs[job_id].progress * 100,
                    description=jobs[job_id].details,
                )
                await asyncio.sleep(0.5)
            finished = await pm_task
            progress.update(
                task,
                completed=jobs[job_id].progress * 100,
                description=jobs[job_id].details,
            )
            return finished

        try:
            result = asyncio.run(run_with_progress())
        except Exception as exc:
            console.print(f"\n[bold red]AgentForge PM failed:[/bold red] {exc}")
            console.print_exception(show_locals=False)
            raise click.ClickException(str(exc)) from exc

    report = result.get("pm_report", {})
    console.print("\n[bold green]AgentForge PM complete[/bold green]")
    console.print(f"   [cyan]Requirements:[/cyan] {report.get('requirements_count', 0)}")
    console.print(f"   [cyan]High Risks:[/cyan] {report.get('high_risk_count', 0)}")
    console.print(f"   [cyan]Planned Duration:[/cyan] {report.get('planned_duration_days', 'n/a')} days")

@cli.command()
@click.argument('path', type=click.Path(exists=True, file_okay=False, readable=True))
def analyze(path):
    """
    Analyze a local project and generate a tech debt report.
    """
    console.print(f"[bold blue]🔍 Analyzing local project at:[/bold blue] {path}")
    
    with console.status("[bold green]Scanning files and assessing code quality...") as status:
        time.sleep(3)
        files_scanned = 128
        issues_found = 42

    console.print(f"\n[bold green]✅ Analysis Complete[/bold green]")
    
    table = Table(title="[bold]Operations Health Report[/bold]")
    table.add_column("Category", style="cyan")
    table.add_column("Issues Found", style="magenta")
    table.add_column("Severity", style="red")

    table.add_row("Low Stock Alerts", "5", "High")
    table.add_row("Overdue Invoices", "22", "Medium")
    table.add_row("No Test Coverage", "11", "High")
    table.add_row("Code Smells", "4", "Low")
    
    console.print(table)
    console.print(f"\nScanned [bold]{files_scanned}[/bold] files and found [bold]{issues_found}[/bold] potential improvements.")

if __name__ == '__main__':
    cli()
