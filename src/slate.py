import shutil
from pathlib import Path
import typer
import subprocess
import sys
import os

try:
    import dotenv

    dotenv.load_dotenv()
except ImportError:
    typer.secho("[warn] python-dotenv not installed, skipping .env loading", fg=typer.colors.YELLOW)

app = typer.Typer(help="slate_runner_cli - API companion.")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Entry point for slate_runner_cli."""
    if ctx.invoked_subcommand is None:
        typer.secho("slate_runner_cli", fg=typer.colors.BLUE)
        typer.echo("\nuse 'slate --help' to see available commands.\n")
        raise typer.Exit()


@app.command()
def run():
    """Run the FastAPI app using .env configuration (or defaults)."""
    api_host = os.getenv("API_HOST", "127.0.0.1")
    api_port = os.getenv("API_PORT", "8049")
    service_name = os.getenv("SERVICE_NAME", "slate_runner_api")
    log_level = os.getenv("LOG_LEVEL", "INFO").lower()

    typer.secho(f"[info] {service_name} init...", fg=typer.colors.BLUE)

    subprocess.run(
        [
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", api_host,
            "--port", api_port,
            "--reload",
            "--log-level", log_level
        ],
        check=True, cwd="src"
    )


@app.command()
def install():
    """Install project dependencies from requirements.txt."""
    typer.secho("[info] installing dependencies...", fg=typer.colors.BLUE)
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)


@app.command()
def upgrade():
    """Upgrade all dependencies and update requirements.txt."""
    typer.secho("[info] upgrading dependencies...", fg=typer.colors.BLUE)
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"], check=True)
    freeze()


@app.command()
def clean():
    """Remove venv and Python caches."""
    typer.secho("[info] cleaning virtualenv and caches...", fg=typer.colors.BLUE)
    dirs_to_remove = [".venv", ".pytest_cache", ".mypy_cache", "htmlcov"]
    for d in dirs_to_remove:
        shutil.rmtree(d, ignore_errors=True)
    for cache in Path(".").rglob("__pycache__"):
        shutil.rmtree(cache, ignore_errors=True)
    typer.secho("[success] clean complete.", fg=typer.colors.GREEN)


@app.command()
def freeze():
    """Freeze current environment into requirements.txt (excluding local -e installs)."""
    typer.secho("[info] freezing dependencies...", fg=typer.colors.BLUE)
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        capture_output=True, text=True, check=True
    )
    filtered = "\n".join(
        line for line in result.stdout.splitlines()
        if not line.startswith("-e ")  # exclude editable install
    )
    with open("requirements.txt", "w") as f:
        f.write(filtered + "\n")


if __name__ == "__main__":
    app()
