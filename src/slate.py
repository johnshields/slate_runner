import typer
import subprocess
import sys
import os
import shlex

try:
    import dotenv

    dotenv.load_dotenv()
except ImportError:
    typer.echo("[warn] python-dotenv not installed, skipping .env loading")

app = typer.Typer(help="Slate Runner CLI - manage your project easily")


@app.command()
def run():
    """Run the FastAPI app using .env configuration (or defaults)."""
    api_host = os.getenv("API_HOST", "127.0.0.1")
    api_port = os.getenv("API_PORT", "8049")
    typer.echo(f"[info] Starting app on {api_host}:{api_port} ...")
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "main:app",
         "--host", api_host, "--port", api_port, "--reload"],
        check=True, cwd="src"
    )


@app.command()
def install():
    """Install project dependencies from requirements.txt."""
    typer.echo("[info] Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)


@app.command()
def upgrade():
    """Upgrade all dependencies and update requirements.txt."""
    typer.echo("[info] Upgrading dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"], check=True)
    freeze()


@app.command()
def clean():
    """Remove venv and Python caches (cross-platform)."""
    typer.echo("[info] Cleaning virtualenv and caches...")
    if os.name == "nt":  # Windows
        subprocess.run(["powershell", "-Command",
                        "Remove-Item -Recurse -Force .venv, **\\__pycache__, .pytest_cache, .mypy_cache, .coverage, htmlcov"],
                       check=False)
    else:  # Linux/Mac
        subprocess.run("rm -rf .venv **/__pycache__ .pytest_cache .mypy_cache .coverage htmlcov",
                       shell=True, check=False)


@app.command()
def freeze():
    """Freeze current environment into requirements.txt, excluding editable installs."""
    typer.echo("[info] Freezing dependencies (excluding editable packages)...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze", "--exclude-editable"],
        capture_output=True,
        text=True,
        check=True
    )

    filtered_lines = [line for line in result.stdout.splitlines() if not line.startswith("-e ")]
    with open("requirements.txt", "w") as f:
        f.write("\n".join(filtered_lines) + "\n")

    typer.echo("[success] requirements.txt updated.")


if __name__ == "__main__":
    app()
