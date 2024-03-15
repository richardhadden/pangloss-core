import asyncio
import atexit
import contextlib
import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rich import print

from pangloss_core.settings import BaseSettings

logger = logging.getLogger("uvicorn.info")
RunningBackgroundTasks = []


def get_application(settings: BaseSettings):
    DEVELOPMENT_MODE = "--reload" in sys.argv

    from pangloss_core.model_setup.model_manager import ModelManager
    from pangloss_core.api import setup_api_routes
    from pangloss_core.background_tasks import BackgroundTaskRegistry
    
    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        # Load the ML model
        for task in BackgroundTaskRegistry:
            if not DEVELOPMENT_MODE or task["run_in_dev"]:
            
                r = running_task = asyncio.create_task(task["function"]())
                print("TASK",r)
                RunningBackgroundTasks.append(running_task)
            else:
                logger.warning(f"Skipping background task '{task["name"]}' for development mode")
        yield
        print("[yellow bold]Closing background tasks...[/yellow bold]")
        for task in RunningBackgroundTasks:
            task.cancel()
        print("[green bold]Background tasks closed[/green bold]")

    for installed_app in settings.INSTALLED_APPS:
        __import__(f"{installed_app}.models")
        __import__(f"{installed_app}.background_tasks")
        __import__(installed_app)

    ModelManager.initialise_models(depth=3)

    _app = FastAPI(
        title=settings.PROJECT_NAME,
        swagger_ui_parameters={"defaultModelExpandDepth": 1, "deepLinking": True},
        lifespan=lifespan
    )
    _app = setup_api_routes(_app, settings)
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in ["*"]],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


