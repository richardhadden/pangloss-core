from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from pangloss_core.api import setup_api_routes
from pangloss_core.settings import BaseSettings
from pangloss_core.model_setup.model_manager import ModelManager


def get_application(settings: BaseSettings):
    for installed_app in settings.INSTALLED_APPS:
        __import__(f"{installed_app}.models")

    ModelManager.initialise_models(depth=3)

    _app = FastAPI(
        title=settings.PROJECT_NAME,
        swagger_ui_parameters={"defaultModelExpandDepth": 1, "deepLinking": True},
    )
    _app = setup_api_routes(_app, settings)
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app