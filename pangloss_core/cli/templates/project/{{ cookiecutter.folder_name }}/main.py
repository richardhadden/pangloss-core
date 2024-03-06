from pangloss_core.application import get_application

from {{ cookiecutter.folder_name }}.settings import settings

app = get_application(settings=settings)


@app.get("/")
def index():
    return {"Hello": "World"}
