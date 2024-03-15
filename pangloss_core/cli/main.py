import importlib.util
import subprocess
import typing
import os
import sys

from cookiecutter.exceptions import OutputDirExistsException
from cookiecutter.main import cookiecutter
from rich import print
from rich.panel import Panel
from rich.syntax import Syntax


import typer

from pangloss_core.exceptions import PanglossCLIError

cli = typer.Typer(
    add_completion=False,
    help="Pangloss CLI",
    name="Pangloss CLI",
)

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "templates")


@cli.command(help="Create new project")
def createapp(app_name: typing.Annotated[str, typer.Argument()]):
    context = {"folder_name": app_name}
    try:
        cookiecutter(
            os.path.join(TEMPLATES_DIR, "app"),
            extra_context=context,
            no_input=True,
        )
    except OutputDirExistsException:
        print(
            "\n",
            Panel(
                f"[bold red]App creation failed:[/bold red] Folder [bold blue]{context["folder_name"]}[/bold blue] already exists.",
                title="Creating Pangloss app",
                subtitle="😡",
                subtitle_align="right",
            ),
            "\n",
        )
    else:
        my_code = f"""
class Settings(BaseSettings):
    PROJECT_NAME: str = "MyApp"
    
    ...

    INSTALLED_APPS: list[str] = ["pangloss_core", "{context["folder_name"]}"] # <-- Add 
"""

        print(
            "\n",
            Panel(
                (
                    f"[bold green]App successfully created:[/bold green] Pangloss app [bold blue]{context["folder_name"]}[/bold blue] created successfully!"
                    f'\n\nGo to your project [blue]settings.py[/blue] and add [blue]"{context["folder_name"]}"[/blue] to [blue]Settings.INSTALLED_APPS[/blue]:'
                    f"\n\nThen go to [blue]{context["folder_name"]}/models.py[/blue] to add some models"
                ),
                title="Creating Pangloss project",
                subtitle="🍹",
                subtitle_align="right",
            ),
            "\n",
        )


@cli.command(help="Create new project")
def createproject(project_name: typing.Annotated[str, typer.Argument()]):
    context = {"folder_name": project_name}
    try:
        cookiecutter(
            os.path.join(TEMPLATES_DIR, "project"),
            extra_context=context,
            no_input=True,
        )
    except OutputDirExistsException:
        print(
            "\n",
            Panel(
                f"[bold red]Project creation failed:[/bold red] Folder [bold blue]{context["folder_name"]}[/bold blue] already exists.",
                title="Creating Pangloss project",
                subtitle="😡",
                subtitle_align="right",
            ),
            "\n",
        )
    else:
        print(
            "\n",
            Panel(
                (
                    f"[bold green]Project successfully created:[/bold green] Pangloss project [bold blue]{context["folder_name"]}[/bold blue] created successfully!"
                    f"\n\nGo to [blue]{context["folder_name"]}/settings.py[/blue] to configure the database"
                    f"\n\nThen run [deep_pink4]pangloss run {context["folder_name"]}[/deep_pink4] to run the development server"
                ),
                title="Creating Pangloss project",
                subtitle="🍹",
                subtitle_align="right",
            ),
            "\n",
        )


@cli.command(help="Does Nothing")
def startapp(name: str):
    print("[green]Hello world![/green]")


@cli.command(help="Starts development server")
def run(project_name: typing.Annotated[str, typer.Argument()]):
    
    sys.path.append(os.getcwd())

    MODULE_PATH = os.path.join(os.getcwd(), project_name, "settings.py")
    MODULE_NAME = project_name
    spec = importlib.util.spec_from_file_location(MODULE_NAME, MODULE_PATH)

    if spec and spec.loader:
        try:
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            p = importlib.import_module(project_name, package="SETTINGS")
        except FileNotFoundError:
            raise PanglossCLIError(
                f'Project "{project_name}" not found in current directory: "{os.getcwd()}"'
            )
    reload_watch_list = ["--reload-dir", os.path.join(os.getcwd(), project_name)]
    for installed_app in p.settings.INSTALLED_APPS:
        m = __import__(installed_app)

        reload_watch_list.append("--reload-dir")
        reload_watch_list.append(m.__path__[0])

    panel = Panel(
        (
            f"Autoreloading on!\n\n   Watching project: [bold green]{project_name}[/bold green]\n   "
            f"Watching installed apps: {", ".join(f"[bold blue]{a}[/bold blue]" for a in p.settings.INSTALLED_APPS)}"
        ),
        title="📜 Starting Pangloss development server!",
        subtitle="(tally ho!)",
        subtitle_align="right",
    )
    print("\n\n", panel, "\n\n")
    sc_command = ["uvicorn", f"{project_name}.main:app", "--reload", *reload_watch_list]
    subprocess.call(sc_command)
