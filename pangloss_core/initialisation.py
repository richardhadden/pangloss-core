import importlib.util
import os
import sys

import typer

from pangloss_core.database import initialise_database_driver
from pangloss_core.exceptions import PanglossInitialisationError


def import_project_file_of_name(folder_name: str, file_name: str):
    sys.path.append(os.getcwd())

    MODULE_PATH = os.path.join(folder_name, file_name)
    MODULE_NAME = folder_name
    spec = importlib.util.spec_from_file_location(MODULE_NAME, MODULE_PATH)

    if spec and spec.loader:
        try:
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)
            p = importlib.import_module(folder_name, package=file_name)
        except FileNotFoundError:
            return None
        return p


def get_project_settings(project_name: str):
    p = import_project_file_of_name(folder_name=project_name, file_name="settings.py")
    if not p:
        raise PanglossInitialisationError(f'Project "{project_name}" not found"')
    return getattr(p, "settings")


def get_app_clis(app_name: str) -> list[typer.Typer]:
    p = import_project_file_of_name(folder_name=app_name, file_name="cli.py")
    if p:
        clis = []
        for key, value in p.__dict__.items():
            if isinstance(value, typer.Typer):
                clis.append(value)
        return clis
    return []


def initialise_pangloss_application(settings):
    initialise_database_driver(settings)
